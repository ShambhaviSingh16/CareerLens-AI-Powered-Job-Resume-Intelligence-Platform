import os
from io import BytesIO

import pytest
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set before importing application modules. Never use the developer's database or API key.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-only-secret-never-use-in-production"
os.environ["GROQ_API_KEY"] = "test-only-no-real-network"
os.environ["ANALYSES_PER_DAY"] = "5"
os.environ["GLOBAL_ANALYSES_PER_DAY"] = "20"

from database import get_db
from main import app
from models import Base

RESUME_TEXT = "Projects\nBuilt Python APIs with FastAPI and SQLite for a library.\nSkills\nPython, SQL\nEducation\nComputer Science\ncandidate@example.com"
JOB_TEXT = "Build Python APIs with FastAPI. Write automated tests. Collaborate with the team on reliable backend services."


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    yield factory
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def db_override():
        with session_factory() as session:
            yield session
    app.dependency_overrides[get_db] = db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth(client):
    def register(email="candidate@example.com"):
        credentials = {"email": email, "password": "test-password-123"}
        assert client.post("/auth/register", json=credentials).status_code == 201
        token = client.post("/auth/login", json=credentials).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return register


@pytest.fixture
def resume_bytes():
    document = Document()
    for line in RESUME_TEXT.splitlines():
        document.add_paragraph(line)
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


@pytest.fixture
def model_output():
    return {
        "summary": "The candidate demonstrates Python APIs but does not evidence automated testing.",
        "skills": [
            {"skill": "Python APIs", "required": True, "status": "strong",
             "requirement_quote": "Build Python APIs with FastAPI.",
             "evidence": "Built Python APIs with FastAPI and SQLite for a library.",
             "explanation": "The library project directly demonstrates Python API development."},
            {"skill": "Automated tests", "required": True, "status": "missing",
             "requirement_quote": "Write automated tests.", "evidence": None,
             "explanation": "No automated tests are mentioned in the resume."},
        ], "suggestions": [],
    }


@pytest.fixture(autouse=True)
def block_real_provider(monkeypatch):
    import matching.service as service

    def forbidden(*args, **kwargs):
        raise AssertionError("Tests must mock the AI provider; no real API calls permitted")
    monkeypatch.setattr(service, "provider_client", forbidden)
