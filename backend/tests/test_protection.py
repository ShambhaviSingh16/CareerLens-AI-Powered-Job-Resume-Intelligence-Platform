import pytest
from middleware import RequestProtection
from starlette.responses import JSONResponse


def test_body_size_and_response_headers(client):
    response = client.post("/auth/login", content=b"x", headers={"Content-Length": str(7 * 1024 * 1024)})
    assert response.status_code == 413
    assert response.headers["x-content-type-options"] == "nosniff"
    assert len(response.headers["x-request-id"]) == 32


def test_auth_rate_limit(client, monkeypatch):
    monkeypatch.setenv("AUTH_REQUESTS_PER_MINUTE", "1")
    body = {"email": "nobody@example.com", "password": "wrong-password"}
    assert client.post("/auth/login", json=body).status_code == 401
    assert client.post("/auth/login", json=body).status_code == 429


def test_account_deletion_requires_password_and_revokes_access(client, auth):
    headers = auth()
    assert client.request("DELETE", "/auth/me", headers=headers, json={"password": "wrong-password"}).status_code == 403
    assert client.request("DELETE", "/auth/me", headers=headers, json={"password": "test-password-123"}).status_code == 204
    assert client.get("/auth/me", headers=headers).status_code == 401


@pytest.mark.anyio
async def test_chunked_request_without_content_length_is_bounded():
    called = False
    async def app(*args):
        nonlocal called
        called = True
    scope = {"type": "http", "method": "POST", "path": "/analyses", "headers": [], "client": ("test", 1)}
    messages = iter([{"type": "http.request", "body": b"x" * (4 * 1024 * 1024), "more_body": True},
                     {"type": "http.request", "body": b"x" * (3 * 1024 * 1024), "more_body": False}])
    sent = []
    async def receive():
        return next(messages)
    async def send(message):
        sent.append(message)
    await RequestProtection(app)(scope, receive, send)
    assert sent[0]["status"] == 413
    assert not called


@pytest.mark.anyio
async def test_production_api_prefix_does_not_bypass_auth_throttle(monkeypatch):
    monkeypatch.setenv("API_PREFIX", "/api")
    monkeypatch.setenv("AUTH_REQUESTS_PER_MINUTE", "1")
    async def app(scope, receive, send):
        await JSONResponse({"ok": True})(scope, receive, send)
    protected = RequestProtection(app)
    statuses = []
    for _ in range(2):
        scope = {"type": "http", "method": "POST", "path": "/api/auth/login", "headers": [], "client": ("test", 1)}
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        async def send(message):
            if message["type"] == "http.response.start":
                statuses.append(message["status"])
        await protected(scope, receive, send)
    assert statuses == [200, 429]
