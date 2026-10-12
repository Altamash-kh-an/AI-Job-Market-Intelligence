import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from api.routers import jobs


class FakeCursor:
    description = [(column,) for column in jobs.JOB_COLUMNS]

    def __init__(self):
        self.query = None
        self.parameters = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters

    def fetchall(self):
        return [
            (
                1,
                4.0,
                "Example",
                "Python Engineer",
                "100000",
                1,
                "Delhi",
                "Full Time",
                "Engineering",
            )
        ]


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def close(self):
        pass

    def cursor(self):
        return self.cursor_instance


class JobEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pagination_and_filters_are_parameterized(self):
        connection = FakeConnection()
        with patch.object(jobs, "get_connection", return_value=connection):
            response = self.client.get(
                "/jobs",
                params={
                    "page": 2,
                    "page_size": 2,
                    "location": "Delhi",
                    "job_title": "Python' OR 1=1 --",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["job_id"], 1)
        self.assertIn("location = %s", connection.cursor_instance.query)
        self.assertIn("job_title ILIKE %s", connection.cursor_instance.query)
        self.assertEqual(
            connection.cursor_instance.parameters,
            ["Delhi", "%Python' OR 1=1 --%", 2, 2],
        )

    def test_page_size_is_bounded(self):
        response = self.client.get("/jobs", params={"page_size": 101})
        self.assertEqual(response.status_code, 422)

    def test_all_write_endpoints_fail_closed_without_token(self):
        payload = {
            "rating": 4,
            "company_name": "Example",
            "job_title": "Engineer",
            "salary": "100000",
            "salaries_reported": 1,
            "location": "Delhi",
            "employment_status": "Full Time",
            "job_roles": "Engineering",
        }
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(jobs, "get_connection") as connect,
        ):
            responses = (
                self.client.post("/jobs", json=payload),
                self.client.put("/jobs/1", json=payload),
                self.client.delete("/jobs/1"),
            )

        self.assertEqual(
            [response.status_code for response in responses], [503, 503, 503]
        )
        connect.assert_not_called()

    def test_invalid_write_token_is_rejected(self):
        with (
            patch.dict(os.environ, {"API_WRITE_TOKEN": "test-token"}, clear=True),
            patch.object(jobs, "get_connection") as connect,
        ):
            response = self.client.delete(
                "/jobs/1",
                headers={"Authorization": "Bearer wrong-token"},
            )

        self.assertEqual(response.status_code, 401)
        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
