from contextlib import closing
import logging
from typing import Annotated

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from api.database import get_connection
from api.security import require_write_token
from api.schemas import ErrorResponse, JobCreate, JobRead, MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)

JOB_COLUMNS = (
    "job_id",
    "rating",
    "company_name",
    "job_title",
    "salary",
    "salaries_reported",
    "location",
    "employment_status",
    "job_roles",
)


def _fetch_jobs(
    *,
    location: str | None = None,
    company_name: str | None = None,
    job_title: str | None = None,
    employment_status: str | None = None,
    job_role: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    filters = (
        ("location", location, False),
        ("company_name", company_name, False),
        ("job_title", job_title, True),
        ("employment_status", employment_status, False),
        ("job_roles", job_role, False),
    )
    conditions = []
    parameters = []

    for column, value, partial in filters:
        if value is not None:
            conditions.append(f"{column} ILIKE %s" if partial else f"{column} = %s")
            parameters.append(f"%{value}%" if partial else value)

    query = f"SELECT {', '.join(JOB_COLUMNS)} FROM pan_india_jobs"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY job_id LIMIT %s OFFSET %s"
    parameters.extend((limit, offset))

    with closing(get_connection()) as conn:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(query, parameters)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _database_unavailable() -> HTTPException:
    logger.error("Database operation failed.")
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Database operation failed.",
    )


@router.get(
    "/jobs",
    response_model=list[JobRead],
    responses={503: {"model": ErrorResponse}},
)
def get_jobs(
    location: Annotated[str | None, Query(max_length=100)] = None,
    company_name: Annotated[str | None, Query(max_length=255)] = None,
    job_title: Annotated[str | None, Query(max_length=255)] = None,
    employment_status: Annotated[str | None, Query(max_length=100)] = None,
    job_role: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1, le=1_000_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[dict]:
    try:
        return _fetch_jobs(
            location=location,
            company_name=company_name,
            job_title=job_title,
            employment_status=employment_status,
            job_role=job_role,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc


@router.get(
    "/jobs/search",
    response_model=list[JobRead],
    responses={503: {"model": ErrorResponse}},
)
def search_jobs(
    location: Annotated[str | None, Query(max_length=100)] = None,
    company_name: Annotated[str | None, Query(max_length=255)] = None,
    job_title: Annotated[str | None, Query(max_length=255)] = None,
    employment_status: Annotated[str | None, Query(max_length=100)] = None,
    job_role: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[dict]:
    try:
        return _fetch_jobs(
            location=location,
            company_name=company_name,
            job_title=job_title,
            employment_status=employment_status,
            job_role=job_role,
            limit=limit,
        )
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc


@router.get(
    "/jobs/{job_id}",
    response_model=JobRead,
    responses={
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def get_job(job_id: Annotated[int, Path(gt=0, le=2_147_483_647)]) -> dict:
    try:
        with closing(get_connection()) as conn:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"SELECT {', '.join(JOB_COLUMNS)} "
                        "FROM pan_india_jobs WHERE job_id = %s",
                        (job_id,),
                    )
                    row = cursor.fetchone()
                    if row is None:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Job not found.",
                        )
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc


@router.post(
    "/jobs",
    response_model=MessageResponse,
    dependencies=[Depends(require_write_token)],
    responses={
        401: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def add_job(job: JobCreate) -> MessageResponse:
    try:
        with closing(get_connection()) as conn:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO pan_india_jobs
                        (rating, company_name, job_title, salary,
                         salaries_reported, location, employment_status, job_roles)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            job.rating,
                            job.company_name,
                            job.job_title,
                            job.salary,
                            job.salaries_reported,
                            job.location,
                            job.employment_status,
                            job.job_roles,
                        ),
                    )
        return MessageResponse(message="Job Added Successfully")
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc


@router.put(
    "/jobs/{job_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_write_token)],
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def update_job(
    job_id: Annotated[int, Path(gt=0, le=2_147_483_647)], job: JobCreate
) -> MessageResponse:
    try:
        with closing(get_connection()) as conn:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE pan_india_jobs
                        SET rating = %s, company_name = %s, job_title = %s,
                            salary = %s, salaries_reported = %s, location = %s,
                            employment_status = %s, job_roles = %s
                        WHERE job_id = %s
                        """,
                        (
                            job.rating,
                            job.company_name,
                            job.job_title,
                            job.salary,
                            job.salaries_reported,
                            job.location,
                            job.employment_status,
                            job.job_roles,
                            job_id,
                        ),
                    )
                    if cursor.rowcount == 0:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Job not found.",
                        )
        return MessageResponse(message="Job Updated Successfully")
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc


@router.delete(
    "/jobs/{job_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_write_token)],
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def delete_job(
    job_id: Annotated[int, Path(gt=0, le=2_147_483_647)]
) -> MessageResponse:
    try:
        with closing(get_connection()) as conn:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM pan_india_jobs WHERE job_id = %s",
                        (job_id,),
                    )
                    if cursor.rowcount == 0:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Job not found.",
                        )
        return MessageResponse(message="Job Deleted Successfully")
    except (psycopg2.Error, RuntimeError) as exc:
        raise _database_unavailable() from exc
