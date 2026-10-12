import unittest
from unittest.mock import Mock

import requests

from dashboard.api_client import (
    APIConfigurationError,
    api_endpoint_url,
    fetch_all_jobs,
    normalize_api_url,
)


class APIURLTests(unittest.TestCase):
    def test_missing_and_empty_urls_have_actionable_errors(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                with self.assertRaisesRegex(APIConfigurationError, "API_URL"):
                    normalize_api_url(value)

    def test_normalizes_whitespace_and_trailing_slashes(self):
        self.assertEqual(
            normalize_api_url("  http://127.0.0.1:8000///  "),
            "http://127.0.0.1:8000",
        )

    def test_accepts_local_and_deployed_http_urls(self):
        self.assertEqual(
            api_endpoint_url("http://127.0.0.1:8000", "/jobs"),
            "http://127.0.0.1:8000/jobs",
        )
        self.assertEqual(
            api_endpoint_url("https://api.example.com/service/", "jobs"),
            "https://api.example.com/service/jobs",
        )

    def test_rejects_invalid_or_credential_bearing_urls(self):
        for value in (
            "api.example.com",
            "ftp://api.example.com",
            "http://api.example.com:invalid",
            "https://api.example.com?",
            "https://api.example.com#",
            "http://user:password@api.example.com",
            "https://api.example.com?token=secret",
            "https://api.example.com/path with space",
        ):
            with self.subTest(value=value):
                with self.assertRaises(APIConfigurationError):
                    normalize_api_url(value)

    def test_endpoint_must_be_relative(self):
        with self.assertRaises(ValueError):
            api_endpoint_url("http://127.0.0.1:8000", "https://other.example")


class JobsPaginationTests(unittest.TestCase):
    @staticmethod
    def job(job_id):
        return {
            "job_id": job_id,
            "rating": 4.0,
            "company_name": "Example",
            "job_title": "Engineer",
            "salary": "100000",
            "salaries_reported": 1,
            "location": "Delhi",
            "employment_status": "Full Time",
            "job_roles": "Engineering",
        }

    @staticmethod
    def response(rows):
        response = Mock()
        response.status_code = 200
        response.json.return_value = rows
        return response

    def test_fetches_pages_until_short_page(self):
        responses = [
            self.response([self.job(1), self.job(2)]),
            self.response([self.job(3)]),
        ]
        request_get = Mock(side_effect=responses)

        rows = fetch_all_jobs(
            "http://127.0.0.1:8000/",
            request_get=request_get,
            page_size=2,
            sleep=Mock(),
        )

        self.assertEqual([row["job_id"] for row in rows], [1, 2, 3])
        self.assertEqual(request_get.call_count, 2)
        self.assertEqual(
            request_get.call_args_list[0].args[0],
            "http://127.0.0.1:8000/jobs",
        )
        self.assertEqual(
            request_get.call_args_list[1].kwargs["params"],
            {"page": 2, "page_size": 2},
        )

    def test_rejects_malformed_responses_and_duplicate_ids(self):
        for malformed in (
            {"jobs": []},
            [{"job_id": True}],
            [{"job_id": 1}, {"job_id": 1}],
            [{"job_id": 1}],
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(RuntimeError):
                    fetch_all_jobs(
                        "http://127.0.0.1:8000",
                        request_get=Mock(return_value=self.response(malformed)),
                        sleep=Mock(),
                    )

    def test_retries_connection_failures_without_exposing_url_details(self):
        request_get = Mock(
            side_effect=requests.ConnectionError(
                "private detail including https://user:secret@example.com"
            )
        )

        with self.assertRaisesRegex(RuntimeError, "could not connect") as caught:
            fetch_all_jobs(
                "http://127.0.0.1:8000",
                request_get=request_get,
                sleep=Mock(),
            )

        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(request_get.call_count, 3)


if __name__ == "__main__":
    unittest.main()
