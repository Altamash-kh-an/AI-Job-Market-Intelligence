from fastapi import FastAPI
from api.routers.jobs import router

from api.ai import router as ai_router
app = FastAPI()
app.include_router(ai_router)

app.include_router(router)

@app.get("/")
def home():
    return {
        "project": "AI Job Market Intelligence Platform",
        "status": "Running"
    }