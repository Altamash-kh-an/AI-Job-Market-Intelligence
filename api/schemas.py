from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


class JobCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: float = Field(ge=0, le=5)
    company_name: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    salary: str = Field(min_length=1, max_length=100)
    salaries_reported: int = Field(ge=0, le=2_147_483_647)
    location: str = Field(min_length=1, max_length=100)
    employment_status: str = Field(min_length=1, max_length=100)
    job_roles: str = Field(min_length=1, max_length=100)


class JobRead(BaseModel):
    job_id: int
    rating: float | None
    company_name: str | None
    job_title: str | None
    salary: str | None
    salaries_reported: int | None
    location: str | None
    employment_status: str | None
    job_roles: str | None


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: Literal["ok"]


class HomeResponse(BaseModel):
    project: str
    status: Literal["Running"]


class AIQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2000)


class AIAnswer(BaseModel):
    sql: str
    answer: str


class AIQueryFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column: Literal[
        "job_id",
        "rating",
        "company_name",
        "job_title",
        "salary",
        "salaries_reported",
        "location",
        "employment_status",
        "job_roles",
    ]
    operator: Literal["eq", "contains", "gt", "gte", "lt", "lte"]
    value: StrictStr | StrictInt | StrictFloat


class AIQueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    columns: list[
        Literal[
            "job_id",
            "rating",
            "company_name",
            "job_title",
            "salary",
            "salaries_reported",
            "location",
            "employment_status",
            "job_roles",
        ]
    ] = Field(
        default=[
            "job_id",
            "rating",
            "company_name",
            "job_title",
            "salary",
            "salaries_reported",
            "location",
            "employment_status",
            "job_roles",
        ],
        min_length=1,
        max_length=9,
    )
    filters: list[AIQueryFilter] = Field(default_factory=list, max_length=8)
    order_by: Literal[
        "job_id",
        "rating",
        "company_name",
        "job_title",
        "salary",
        "salaries_reported",
        "location",
        "employment_status",
        "job_roles",
        "aggregate_value",
    ] | None = None
    direction: Literal["asc", "desc"] = "asc"
    limit: StrictInt = Field(default=10, ge=1, le=100)
    aggregate: Literal["count", "avg", "min", "max", "sum"] | None = None
    aggregate_column: Literal[
        "job_id",
        "rating",
        "company_name",
        "job_title",
        "salary",
        "salaries_reported",
        "location",
        "employment_status",
        "job_roles",
    ] | None = None
    group_by: Literal[
        "job_id",
        "rating",
        "company_name",
        "job_title",
        "salary",
        "salaries_reported",
        "location",
        "employment_status",
        "job_roles",
    ] | None = None