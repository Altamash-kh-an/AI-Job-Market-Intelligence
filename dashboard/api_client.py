import time
from collections.abc import Callable
from urllib.parse import urlsplit

import requests

JOB_RESPONSE_FIELDS = frozenset(
    {
        "job_id",
        "rating",
        "company_name",
        "job_title",
        "salary",
        "salaries_reported",
        "location",
        "employment_status",
        "job_roles",
    }
)


class APIConfigurationError(ValueError):
    pass


def normalize_api_url(value: str | None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise APIConfigurationError(
            "API_URL is required. Set it to the FastAPI base URL "
            "(for local development: http://127.0.0.1:8000)."
        )

    candidate = value.strip()
    if any(character.isspace() for character in candidate):
        raise APIConfigurationError(
            "API_URL must be an absolute HTTP(S) URL without whitespace."
        )

    try:
        parsed = urlsplit(candidate)
        parsed.port
    except ValueError as exc:
        raise APIConfigurationError(
            "API_URL must be a valid absolute HTTP(S) base URL."
        ) from exc

    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or "?" in candidate
        or "#" in candidate
    ):
        raise APIConfigurationError(
            "API_URL must be an absolute HTTP(S) base URL without credentials, "
            "a query, or a fragment."
        )

    return candidate.rstrip("/")


def api_endpoint_url(api_url: str | None, endpoint: str) -> str:
    if not endpoint or endpoint.startswith("//") or "://" in endpoint:
        raise ValueError("API endpoint must be a relative path.")
    return f"{normalize_api_url(api_url)}/{endpoint.lstrip('/')}"


def fetch_all_jobs(
    api_url: str | None,
    *,
    request_get: Callable[..., requests.Response] = requests.get,
    sleep: Callable[[float], None] = time.sleep,
    page_size: int = 100,
    max_pages: int = 1_000_000,
) -> list[dict]:
    jobs = []
    seen_job_ids = set()
    endpoint = api_endpoint_url(api_url, "jobs")

    for page in range(1, max_pages + 1):
        for attempt in range(3):
            try:
                response = request_get(
                    endpoint,
                    params={"page": page, "page_size": page_size},
                    timeout=30,
                )
            except requests.RequestException as exc:
                if attempt == 2:
                    if isinstance(exc, requests.Timeout):
                        reason = "timed out"
                    elif isinstance(exc, requests.ConnectionError):
                        reason = "could not connect"
                    else:
                        reason = "request failed"
                    raise RuntimeError(
                        f"Jobs API request {reason} on page {page} "
                        "after 3 attempts."
                    ) from exc
                sleep(2)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 2:
                    raise RuntimeError(
                        f"Jobs API returned HTTP {response.status_code} "
                        f"on page {page} after 3 attempts."
                    )
                sleep(2)
                continue

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise RuntimeError(
                    f"Jobs API returned HTTP {response.status_code} "
                    f"on page {page}."
                ) from exc

            try:
                page_jobs = response.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"Jobs API returned invalid JSON on page {page}."
                ) from exc

            if not isinstance(page_jobs, list) or any(
                not isinstance(job, dict)
                or                 not isinstance(job.get("job_id"), int)
                or isinstance(job.get("job_id"), bool)
                or not JOB_RESPONSE_FIELDS.issubset(job)
                for job in page_jobs
            ):
                raise RuntimeError(
                    f"Jobs API returned an unexpected response on page {page}."
                )
            if len(page_jobs) > page_size:
                raise RuntimeError(
                    f"Jobs API returned more than {page_size} jobs on page {page}."
                )

            page_ids = [job["job_id"] for job in page_jobs]
            if len(page_ids) != len(set(page_ids)) or any(
                job_id in seen_job_ids for job_id in page_ids
            ):
                raise RuntimeError(
                    f"Jobs API returned duplicate job IDs on page {page}; "
                    "the dataset may be incomplete."
                )

            jobs.extend(page_jobs)
            seen_job_ids.update(page_ids)
            break
        else:
            raise RuntimeError(f"Unable to retrieve jobs page {page}.")

        if len(page_jobs) < page_size:
            return jobs

    raise RuntimeError(
        f"Jobs API exceeded the supported {max_pages}-page limit; "
        "the dataset may be incomplete."
    )
