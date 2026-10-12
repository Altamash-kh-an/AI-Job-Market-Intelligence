import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from google.genai.errors import APIError
from pydantic import ValidationError

from api import ai
from api.schemas import AIQueryPlan, AIQuestion


def make_plan(**overrides):
    values = {
        "columns": ["job_id", "company_name"],
        "filters": [],
        "order_by": None,
        "direction": "asc",
        "limit": 10,
        "aggregate": None,
        "aggregate_column": None,
        "group_by": None,
    }
    values.update(overrides)
    return AIQueryPlan.model_validate(values)


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.readonly = False
        self.query = None
        self.parameters = None
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def close(self):
        self.closed = True

    def set_session(self, *, readonly):
        self.readonly = readonly

    def cursor(self):
        return FakeCursor(self)


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, parameters):
        self.connection.query = query
        self.connection.parameters = parameters

    def fetchall(self):
        return self.connection.rows


class AIQueryPlanTests(unittest.TestCase):
    def test_valid_plan_builds_allowlisted_query(self):
        plan = make_plan(
            aggregate="count",
            group_by="location",
            order_by="aggregate_value",
        )

        query, parameters = ai._build_read_query(plan)

        self.assertIn("COUNT(*) AS aggregate_value", query)
        self.assertIn("GROUP BY location", query)
        self.assertIn("LIMIT %s", query)
        self.assertEqual(parameters, (10,))

    def test_json_validation_rejects_malformed_and_extra_fields(self):
        with self.assertRaises(ValidationError):
            AIQueryPlan.model_validate_json("{")
        with self.assertRaises(ValidationError):
            AIQueryPlan.model_validate_json('{"limit": 10, "unexpected": true}')

    def test_schema_rejects_unsupported_columns_and_operators(self):
        for filter_data in (
            {"column": "password", "operator": "eq", "value": "x"},
            {"column": "location", "operator": "drop", "value": "x"},
            {
                "column": "location",
                "operator": "eq",
                "value": "x",
                "unexpected": True,
            },
        ):
            with self.subTest(filter_data=filter_data):
                with self.assertRaises(ValidationError):
                    make_plan(filters=[filter_data])

    def test_filter_values_are_parameterized(self):
        attack_like_value = "Bengaluru' OR 1=1 --"
        plan = make_plan(
            filters=[
                {
                    "column": "location",
                    "operator": "contains",
                    "value": attack_like_value,
                }
            ]
        )

        query, parameters = ai._build_read_query(plan)

        self.assertIn("location ILIKE %s", query)
        self.assertNotIn(attack_like_value, query)
        self.assertEqual(parameters, (f"%{attack_like_value}%", 10))

    def test_invalid_numeric_filter_is_rejected(self):
        plan = make_plan(
            filters=[{"column": "rating", "operator": "gt", "value": "high"}]
        )

        with self.assertRaises(ValueError):
            ai._build_read_query(plan)

    def test_salary_expression_only_casts_plain_signed_decimals(self):
        pattern = ai.SALARY_NUMERIC_PATTERN
        for value in ("400000", "400000.25", "-400000", "+400000.25"):
            with self.subTest(value=value):
                self.assertIsNotNone(re.fullmatch(pattern, value))
        for value in ("₹1,00,000", "400000-800000", "1e6", " 400000"):
            with self.subTest(value=value):
                self.assertIsNone(re.fullmatch(pattern, value))

        plan = make_plan(
            filters=[{"column": "salary", "operator": "gte", "value": 400000}]
        )
        query, parameters = ai._build_read_query(plan)
        self.assertIn(f"CASE WHEN salary ~ '{pattern}'", query)
        self.assertIn("THEN salary::numeric END >= %s", query)
        self.assertEqual(parameters, (400000, 10))

    def test_query_limit_is_strict_and_bounded(self):
        plan = make_plan(limit=100)
        query, parameters = ai._build_read_query(plan)
        self.assertIn("LIMIT %s", query)
        self.assertEqual(parameters[-1], 100)

        for limit in (101, "10", 10.0, True):
            with self.subTest(limit=limit):
                with self.assertRaises(ValidationError):
                    make_plan(limit=limit)

    def test_unused_aggregate_and_invalid_grouping_are_rejected(self):
        with self.assertRaises(ValidationError):
            make_plan(aggregate="median")
        with self.assertRaises(ValueError):
            ai._build_read_query(make_plan(aggregate_column="rating"))
        with self.assertRaises(ValueError):
            ai._build_read_query(make_plan(group_by="location"))
        with self.assertRaises(ValueError):
            ai._build_read_query(
                make_plan(
                    aggregate="count",
                    group_by="location",
                    order_by="company_name",
                )
            )


class AIIntegrationBoundaryTests(unittest.TestCase):
    def test_empty_and_malformed_gemini_plan_responses_fail(self):
        for text in (None, "  ", "not-json"):
            client = SimpleNamespace(
                models=SimpleNamespace(
                    generate_content=lambda **_: SimpleNamespace(text=text)
                )
            )
            with self.subTest(text=text):
                with self.assertRaises((ValueError, ValidationError)):
                    ai._generate_query_plan("question", client)

    def test_missing_gemini_configuration_returns_service_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as caught:
                ai._get_gemini_client()

        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("key", caught.exception.detail.lower())

    def test_provider_failure_returns_sanitized_gateway_error(self):
        provider_error = APIError(503, {"message": "private provider detail"})
        with patch.object(ai, "_get_gemini_client", side_effect=provider_error):
            with self.assertRaises(HTTPException) as caught:
                ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(caught.exception.status_code, 502)
        self.assertNotIn("private provider detail", caught.exception.detail)

    def test_invalid_plan_returns_gateway_error_without_database_access(self):
        with self.assertRaises(ValidationError) as validation_error:
            AIQueryPlan.model_validate_json('{"limit": 10, "unexpected": true}')
        connection_factory = patch.object(ai, "get_connection")

        with (
            patch.object(ai, "_get_gemini_client", return_value=object()),
            patch.object(
                ai,
                "_generate_query_plan",
                side_effect=validation_error.exception,
            ),
            connection_factory as get_connection,
        ):
            with self.assertRaises(HTTPException) as caught:
                ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(caught.exception.status_code, 502)
        get_connection.assert_not_called()

    def test_transport_failure_returns_sanitized_gateway_error(self):
        transport_error = httpx.ConnectError("private transport detail")
        with patch.object(ai, "_get_gemini_client", side_effect=transport_error):
            with self.assertRaises(HTTPException) as caught:
                ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(caught.exception.status_code, 502)
        self.assertNotIn("private transport detail", caught.exception.detail)

    def test_answer_generation_failure_does_not_leak_provider_details(self):
        connection = FakeConnection(rows=[(4,)])
        provider_error = APIError(503, {"message": "private provider detail"})
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=lambda **_: (_ for _ in ()).throw(provider_error)
            )
        )

        with (
            patch.object(ai, "_get_gemini_client", return_value=client),
            patch.object(ai, "_generate_query_plan", return_value=make_plan()),
            patch.object(ai, "get_connection", return_value=connection),
        ):
            with self.assertRaises(HTTPException) as caught:
                ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(caught.exception.status_code, 502)
        self.assertNotIn("private provider detail", caught.exception.detail)
        self.assertTrue(connection.readonly)
        self.assertTrue(connection.closed)

    def test_success_keeps_answer_contract_and_executes_read_only(self):
        connection = FakeConnection(rows=[(4,)])
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=lambda **_: SimpleNamespace(text="  Four jobs.  ")
            )
        )

        with (
            patch.object(ai, "_get_gemini_client", return_value=client),
            patch.object(ai, "_generate_query_plan", return_value=make_plan()),
            patch.object(ai, "get_connection", return_value=connection),
        ):
            answer = ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(answer.answer, "Four jobs.")
        self.assertIn("sql", answer.model_dump())
        self.assertTrue(connection.readonly)
        self.assertTrue(connection.closed)
        self.assertEqual(connection.parameters, (10,))

    def test_empty_answer_returns_gateway_error(self):
        connection = FakeConnection(rows=[(4,)])
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=lambda **_: SimpleNamespace(text=" \n ")
            )
        )

        with (
            patch.object(ai, "_get_gemini_client", return_value=client),
            patch.object(ai, "_generate_query_plan", return_value=make_plan()),
            patch.object(ai, "get_connection", return_value=connection),
        ):
            with self.assertRaises(HTTPException) as caught:
                ai.chat(AIQuestion(question="show jobs"))

        self.assertEqual(caught.exception.status_code, 502)
        self.assertEqual(caught.exception.detail, "AI returned an empty answer.")


if __name__ == "__main__":
    unittest.main()
