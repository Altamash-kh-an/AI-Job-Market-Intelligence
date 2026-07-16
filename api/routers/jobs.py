from fastapi import APIRouter
from api.database import get_connection
from api.schemas import Job

router = APIRouter()


@router.get("/jobs")
def get_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM pan_india_jobs
            LIMIT 1000
        """)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        jobs = [dict(zip(columns, row)) for row in rows]

        return jobs

    finally:
        cursor.close()
        conn.close()

@router.get("/jobs/search")
def search_jobs(location: str):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM pan_india_jobs WHERE location = %s LIMIT 10",
            (location,)
        )

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        jobs = []

        for row in rows:
            jobs.append(dict(zip(columns, row)))

        return jobs

    finally:
        cursor.close()
        conn.close()


@router.get("/jobs/{job_id}")
def get_job(job_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM pan_india_jobs WHERE job_id = %s",
            (job_id,)
        )

        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        if not row:
            return {"message": "Job not found"}

        return dict(zip(columns, row))

    finally:
        cursor.close()
        conn.close()


@router.post("/jobs")
def add_job(job: Job):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO pan_india_jobs
            (rating, company_name, job_title, salary,
            salaries_reported, location,
            employment_status, job_roles)

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                job.rating,
                job.company_name,
                job.job_title,
                job.salary,
                job.salaries_reported,
                job.location,
                job.employment_status,
                job.job_roles
            )
        )

        conn.commit()

        return {"message": "Job Added Successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


@router.put("/jobs/{job_id}")
def update_job(job_id: int, job: Job):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE pan_india_jobs

            SET
            rating=%s,
            company_name=%s,
            job_title=%s,
            salary=%s,
            salaries_reported=%s,
            location=%s,
            employment_status=%s,
            job_roles=%s

            WHERE job_id=%s
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
                job_id
            )
        )

        conn.commit()

        return {"message": "Job Updated Successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM pan_india_jobs WHERE job_id = %s",
            (job_id,)
        )

        conn.commit()

        return {"message": "Job Deleted Successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()