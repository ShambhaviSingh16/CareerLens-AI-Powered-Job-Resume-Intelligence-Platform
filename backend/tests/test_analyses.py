from sqlalchemy import func, select

from matching.service import AnalysisError
from models import Analysis, AnalysisAttempt, Job, Resume
from conftest import JOB_TEXT


def upload(client, headers, content):
    return client.post("/analyses", headers=headers,
                       data={"job_title": "Backend developer", "job_description": JOB_TEXT},
                       files={"resume": ("resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})


def test_save_history_ownership_and_delete(client, auth, resume_bytes, monkeypatch, model_output, session_factory):
    headers, other = auth(), auth("other@example.com")
    monkeypatch.setattr("matching.routes.analyze_resume", lambda *args: {**model_output, "match_score": 50})
    response = upload(client, headers, resume_bytes)
    assert response.status_code == 201, response.text
    analysis_id = response.json()["id"]
    assert client.get("/analyses", headers=headers).json()[0]["match_score"] == 50
    assert client.get("/analyses", headers=other).json() == []
    assert client.get(f"/analyses/{analysis_id}", headers=other).status_code == 404
    assert client.delete(f"/analyses/{analysis_id}", headers=other).status_code == 404
    assert client.get(f"/analyses/{analysis_id}", headers=headers).status_code == 200
    assert client.delete(f"/analyses/{analysis_id}", headers=headers).status_code == 204
    with session_factory() as db:
        for model in (Analysis, Resume, Job):
            assert db.scalar(select(func.count()).select_from(model)) == 0
        assert db.scalar(select(func.count()).select_from(AnalysisAttempt)) == 1


def test_provider_failure_does_not_save_documents(client, auth, resume_bytes, monkeypatch, session_factory):
    def fail(*args):
        raise AnalysisError("Provider unavailable", 503)
    monkeypatch.setattr("matching.routes.analyze_resume", fail)
    assert upload(client, auth(), resume_bytes).status_code == 503
    with session_factory() as db:
        for model in (Analysis, Resume, Job):
            assert db.scalar(select(func.count()).select_from(model)) == 0


def test_attempt_limit_survives_failure(client, auth, resume_bytes, monkeypatch):
    monkeypatch.setenv("ANALYSES_PER_DAY", "1")
    def fail(*args):
        raise AnalysisError("Provider unavailable", 503)
    monkeypatch.setattr("matching.routes.analyze_resume", fail)
    headers = auth()
    assert upload(client, headers, resume_bytes).status_code == 503
    assert upload(client, headers, resume_bytes).status_code == 429


def test_invalid_file_never_calls_provider(client, auth, monkeypatch):
    def unexpected(*args):
        raise AssertionError("Provider called for invalid file")
    monkeypatch.setattr("matching.routes.analyze_resume", unexpected)
    assert upload(client, auth(), b"invalid docx").status_code == 422


def test_global_limit_applies_across_users(client, auth, resume_bytes, monkeypatch, model_output):
    monkeypatch.setenv("GLOBAL_ANALYSES_PER_DAY", "1")
    monkeypatch.setattr("matching.routes.analyze_resume", lambda *args: {**model_output, "match_score": 50})
    first, second = auth(), auth("second@example.com")
    assert upload(client, first, resume_bytes).status_code == 201
    assert upload(client, second, resume_bytes).status_code == 429
    assert client.request("DELETE", "/auth/me", headers=first, json={"password": "test-password-123"}).status_code == 204
    assert upload(client, second, resume_bytes).status_code == 429


def test_missing_key_is_actionable(client, auth, resume_bytes, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = upload(client, auth(), resume_bytes)
    assert response.status_code == 503
    assert "sample" in response.json()["detail"]
