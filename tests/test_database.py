import os
import unittest
from unittest.mock import patch

from api import database


class DatabaseConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.required = {
            "DB_NAME": "jobs",
            "DB_USER": "app_user",
            "DB_PORT": "5432",
        }

    def test_loopback_without_password_requires_explicit_disabled_ssl(self):
        for host in ("localhost", "127.0.0.1", "::1"):
            with self.subTest(host=host):
                config = {
                    **self.required,
                    "DB_HOST": host,
                    "DB_SSLMODE": "disable",
                }
                with (
                    patch.dict(os.environ, config, clear=True),
                    patch.object(database.psycopg2, "connect") as connect,
                ):
                    database.get_connection()

                self.assertIsNone(connect.call_args.kwargs["password"])
                self.assertEqual(connect.call_args.kwargs["sslmode"], "disable")

    def test_remote_host_without_password_is_rejected(self):
        config = {
            **self.required,
            "DB_HOST": "db.example.com",
        }
        with (
            patch.dict(os.environ, config, clear=True),
            patch.object(database.psycopg2, "connect") as connect,
        ):
            with self.assertRaisesRegex(RuntimeError, "DB_PASSWORD is required"):
                database.get_connection()

        connect.assert_not_called()

    def test_loopback_without_password_and_ssl_is_rejected(self):
        config = {
            **self.required,
            "DB_HOST": "127.0.0.1",
        }
        with (
            patch.dict(os.environ, config, clear=True),
            patch.object(database.psycopg2, "connect") as connect,
        ):
            with self.assertRaisesRegex(RuntimeError, "DB_PASSWORD is required"):
                database.get_connection()

        connect.assert_not_called()

    def test_remote_connection_requires_password_and_defaults_to_ssl(self):
        config = {
            **self.required,
            "DB_HOST": "db.example.com",
            "DB_PASSWORD": "unit-test-placeholder",
        }
        with (
            patch.dict(os.environ, config, clear=True),
            patch.object(database.psycopg2, "connect") as connect,
        ):
            database.get_connection()

        self.assertEqual(connect.call_args.kwargs["sslmode"], "require")


if __name__ == "__main__":
    unittest.main()
