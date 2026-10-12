from fastapi import FastAPI
from api.routers.jobs import router
from api.ai import router as ai_router
from api.schemas import HealthResponse, HomeResponse

app = FastAPI()
app.include_router(ai_router)
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/", response_model=HomeResponse)
def home() -> HomeResponse:
    return HomeResponse(
        project="AI Job Market Intelligence Platform",
        status="Running",
    )