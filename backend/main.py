from fastapi import FastAPI

from auth.routes import router as auth_router
from database import check_database_connection


app = FastAPI(
    title="CareerLens API",
    description="AI-powered resume and job match intelligence platform",
    version="0.1.0",
)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check():
    check_database_connection()

    return {
        "status": "ok",
        "database": "connected",
    }