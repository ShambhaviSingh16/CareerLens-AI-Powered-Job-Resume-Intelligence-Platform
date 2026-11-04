import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware

from auth.routes import router as auth_router
from database import check_database_connection
from matching.routes import router as analysis_router
from middleware import RequestProtection
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI(
    title="CareerLens API",
    description="AI-powered resume and job match intelligence platform",
    version="0.1.0",
)

app.add_middleware(RequestProtection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_prefix = os.getenv("API_PREFIX", "")
app.include_router(auth_router, prefix=api_prefix)
app.include_router(analysis_router, prefix=api_prefix)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check():
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Database is not ready.") from exc

    return {
        "status": "ok",
        "database": "connected",
    }


class SPAFiles(StaticFiles):
    async def get_response(self, path, scope):
        path = path.replace("\\", "/").lstrip("/")
        # Never turn a missing API route or asset into a successful HTML response.
        if path.split("/", 1)[0] in {"api", "auth", "analyses", "health"}:
            raise StarletteHTTPException(404)
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404 or Path(path).suffix:
                raise
            return await super().get_response("index.html", scope)


frontend_build = Path(os.getenv("FRONTEND_BUILD_DIR", "frontend_dist"))
if frontend_build.is_dir():
    app.mount("/", SPAFiles(directory=frontend_build, html=True), name="frontend")
