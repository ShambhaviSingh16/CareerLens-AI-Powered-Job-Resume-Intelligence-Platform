import json

import httpx
import pytest
from pydantic import ValidationError

from matching.schemas import ModelAnalysis
from matching.service import AnalysisError, analyze_resume, calculate_score, validate_evidence
from conftest import JOB_TEXT, RESUME_TEXT


def mock_provider(monkeypatch, payload, status=200):
    import matching.service as service

    def respond(request):
        assert str(request.url) == "https://api.groq.com/openai/v1/chat/completions"
        assert json.loads(request.content)["response_format"] == {"type": "json_object"}
        return httpx.Response(status, json=payload)
    monkeypatch.setattr(service, "provider_client", lambda: httpx.Client(transport=httpx.MockTransport(respond)))


def test_provider_result_validated_and_scored(monkeypatch, model_output):
    mock_provider(monkeypatch, {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(model_output)}}]})
    result = analyze_resume(RESUME_TEXT, JOB_TEXT)
    assert result["match_score"] == 50
    assert all(check["found"] for check in result["document_checks"])


def test_weighted_rubric(model_output):
    model_output["skills"][1].update(status="partial", required=False, evidence="Skills")
    assert calculate_score(ModelAnalysis.model_validate(model_output)) == 83


def test_whitespace_quotation_rejected(model_output):
    model_output["skills"][0]["requirement_quote"] = "   "
    with pytest.raises(ValidationError):
        ModelAnalysis.model_validate(model_output)


@pytest.mark.parametrize("change", ["resume", "job", "duplicate", "rewrite", "missing"])
def test_invented_evidence_rejected(model_output, change):
    if change == "resume":
        model_output["skills"][0]["evidence"] = "Invented Kubernetes deployment"
    elif change == "job":
        model_output["skills"][0]["requirement_quote"] = "Invented requirement"
    elif change == "duplicate":
        model_output["skills"].append(model_output["skills"][0].copy())
    elif change == "rewrite":
        model_output["suggestions"] = [{"original": "Invented accomplishment", "rewrite": "Some rewrite", "reason": "Some reason"}]
    else:
        model_output["skills"][1]["evidence"] = "Skills"
    with pytest.raises(AnalysisError):
        validate_evidence(ModelAnalysis.model_validate(model_output), RESUME_TEXT, JOB_TEXT)


@pytest.mark.parametrize("payload,status,expected", [
    ({}, 429, 429), ({}, 401, 503), ({}, 500, 502),
    ({"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]}, 200, 502),
    ({"choices": [{"finish_reason": "stop", "message": {"content": "not json"}}]}, 200, 502),
])
def test_provider_failures(monkeypatch, payload, status, expected):
    mock_provider(monkeypatch, payload, status)
    with pytest.raises(AnalysisError) as exc:
        analyze_resume(RESUME_TEXT, JOB_TEXT)
    assert exc.value.status_code == expected


def test_provider_timeout(monkeypatch):
    import matching.service as service

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout("timeout")
    monkeypatch.setattr(service, "provider_client", timeout)
    with pytest.raises(AnalysisError) as exc:
        analyze_resume(RESUME_TEXT, JOB_TEXT)
    assert exc.value.status_code == 504
