from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from auth.security import JWT_SECRET


def test_register_login_and_me(client, auth):
    headers = auth()
    assert client.get("/auth/me", headers=headers).json()["email"] == "candidate@example.com"
    assert client.post("/auth/register", json={"email": "candidate@example.com", "password": "test-password-123"}).status_code == 409
    assert client.post("/auth/login", json={"email": "candidate@example.com", "password": "wrong-password"}).status_code == 401


def test_short_password_returns_validation(client):
    response = client.post("/auth/register", json={"email": "candidate@example.com", "password": "123456"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "password"


@pytest.mark.parametrize("payload", [
    {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
    {"sub": "1"}, {"sub": "not-an-id", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
    {"sub": "9999", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
])
def test_invalid_tokens_rejected(client, payload):
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    assert client.get("/analyses", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_anonymous_access_rejected(client):
    assert client.get("/analyses").status_code == 401
    assert client.get("/auth/me").status_code == 401
