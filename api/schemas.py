from pydantic import BaseModel

class Job(BaseModel):
    rating: float
    company_name: str
    job_title: str
    salary: str
    salaries_reported: int
    location: str
    employment_status: str
    job_roles: str