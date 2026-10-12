import ipaddress
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    db_host = os.getenv("DB_HOST")
    db_password = os.getenv("DB_PASSWORD")
    sslmode = os.getenv("DB_SSLMODE", "require")

    required_variables = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PORT")
    missing_variables = [
        name for name in required_variables if not os.getenv(name)
    ]
    if missing_variables:
        raise RuntimeError(
            "Missing required database configuration: "
            + ", ".join(missing_variables)
        )

    try:
        is_loopback = (
            db_host == "localhost"
            or ipaddress.ip_address(db_host).is_loopback
        )
    except ValueError:
        is_loopback = False

    if not db_password and not (is_loopback and sslmode == "disable"):
        raise RuntimeError(
            "DB_PASSWORD is required unless connecting to a local loopback "
            "database with DB_SSLMODE=disable."
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        sslmode=sslmode,
    )