from datetime import datetime, timedelta, timezone
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import func, select

from evaluation import run
from main import SPAFiles
from matching.service import AnalysisError
from models import Analysis, Resume
from test_analyses import upload


def test_account_deletion_removes_inputs_and_preserves_other_users(client, auth, resume_bytes, monkeypatch, model_output, session_factory):
    first, other = auth(), auth("other@example.com")
    monkeypatch.setattr("matching.routes.analyze_resume", lambda *args: {**model_output, "match_score": 50})
    assert upload(client, first, resume_bytes).status_code == 201
    assert upload(client, other, resume_bytes).status_code == 201
    assert client.request("DELETE", "/auth/me", headers=first, json={"password": "test-password-123"}).status_code == 204
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Analysis)) == 1
        assert db.scalar(select(func.count()).select_from(Resume)) == 1
    assert len(client.get("/analyses", headers=other).json()) == 1


def test_retention_is_preview_first_and_deletes_only_stale_inputs(client, auth, resume_bytes, monkeypatch, model_output, session_factory):
    import maintenance
    headers = auth()
    monkeypatch.setattr("matching.routes.analyze_resume", lambda *args: {**model_output, "match_score": 50})
    old = upload(client, headers, resume_bytes).json()["id"]
    upload(client, headers, resume_bytes)
    with session_factory() as db:
        db.get(Analysis, old).created_at = datetime.now(timezone.utc) - timedelta(days=40)
        db.commit()
    monkeypatch.setattr(maintenance, "SessionLocal", session_factory)
    monkeypatch.setattr("sys.argv", ["maintenance"])
    maintenance.main()
    assert len(client.get("/analyses", headers=headers).json()) == 2
    monkeypatch.setattr("sys.argv", ["maintenance", "--apply"])
    maintenance.main()
    assert len(client.get("/analyses", headers=headers).json()) == 1
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Resume)) == 1


def test_spa_fallback_does_not_hide_missing_api_or_assets(tmp_path):
    (tmp_path / "index.html").write_text("<html>Example app</html>")
    app = FastAPI()
    app.mount("/", SPAFiles(directory=tmp_path, html=True))
    with TestClient(app) as client:
        assert client.get("/sample").text == "<html>Example app</html>"
        assert client.get("/api/unknown").status_code == 404
        assert client.get("/missing.js").status_code == 404


def test_eval_baseline_and_replay_cli(tmp_path, monkeypatch):
    baseline, replay = tmp_path / "baseline.json", tmp_path / "replay.json"
    monkeypatch.setattr("sys.argv", ["evaluation", "--output", str(baseline)])
    assert run.main() == 0
    monkeypatch.setattr("sys.argv", ["evaluation", "--mode", "replay", "--predictions", str(baseline), "--output", str(replay)])
    assert run.main() == 0
    assert json.loads(baseline.read_text())["metrics"] == json.loads(replay.read_text())["metrics"]


def test_live_evaluation_requires_explicit_confirmation(monkeypatch):
    monkeypatch.setattr("sys.argv", ["evaluation", "--mode", "live"])
    with pytest.raises(SystemExit) as exc:
        run.main()
    assert exc.value.code == 2


def test_live_evaluation_stops_on_rate_limit(tmp_path, monkeypatch):
    calls = []
    def limited(*args):
        calls.append(1)
        raise AnalysisError("Rate limited", 429)
    monkeypatch.setattr(run, "analyze_resume", limited)
    output = tmp_path / "limited.json"
    monkeypatch.setattr("sys.argv", ["evaluation", "--mode", "live", "--confirm-free-plan", "--max-cases", "2", "--output", str(output)])
    assert run.main() == 1
    assert len(calls) == 1
    assert json.loads(output.read_text())["metrics"]["rejected_cases"] == 2
