"""Exercise an actual running stack. Makes no provider calls unless explicitly requested."""
import argparse
import json
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--api-prefix", default="/api")
    parser.add_argument("--live-analysis", action="store_true", help="Explicitly send one synthetic PDF to the configured Free-plan provider")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    def request(path, method="GET", data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        payload = json.dumps(data).encode() if data is not None else None
        with urlopen(Request(base + path, data=payload, headers=headers, method=method), timeout=10) as response:
            raw = response.read()
            return json.loads(raw) if raw and "application/json" in response.headers.get("Content-Type", "") else raw

    for _ in range(60):
        try:
            request("/health/database")
            break
        except (OSError, HTTPError):
            time.sleep(2)
    else:
        raise SystemExit("Stack did not become ready.")
    assert b"<html" in request("/").lower()
    assert b"<html" in request("/sample").lower()
    credentials = {"email": f"smoke-{uuid.uuid4().hex}@example.com", "password": uuid.uuid4().hex}
    token = None
    try:
        request(args.api_prefix + "/auth/register", "POST", credentials)
        token = request(args.api_prefix + "/auth/login", "POST", credentials)["access_token"]
        assert request(args.api_prefix + "/auth/me", token=token)["email"] == credentials["email"]
        assert request(args.api_prefix + "/analyses", token=token) == []
        if args.live_analysis:
            # Optional dependency is already present in the backend environment.
            import pymupdf
            with pymupdf.open() as document:
                page = document.new_page()
                page.insert_text((50, 50), "Projects\nBuilt Python APIs with FastAPI and PostgreSQL for a library.\nWrote automated tests with pytest.\nSkills\nPython, SQL\nEducation\nComputer Science\nfictional@example.com")
                pdf = document.tobytes()
            boundary = uuid.uuid4().hex
            fields = {"job_title": "Synthetic backend role", "job_description": "Python API development is required. PostgreSQL database experience is required. Automated testing is required. Docker experience is preferred."}
            parts = []
            for name, value in fields.items():
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="resume"; filename="synthetic.pdf"\r\nContent-Type: application/pdf\r\n\r\n'.encode() + pdf + b"\r\n")
            parts.append(f"--{boundary}--\r\n".encode())
            headers = {"Authorization": "Bearer " + token, "Content-Type": "multipart/form-data; boundary=" + boundary}
            with urlopen(Request(base + args.api_prefix + "/analyses", data=b"".join(parts), headers=headers), timeout=90) as response:
                analysis = json.loads(response.read())
            assert analysis["result"]["skills"]
            assert request(args.api_prefix + f'/analyses/{analysis["id"]}', token=token)["id"] == analysis["id"]
            request(args.api_prefix + f'/analyses/{analysis["id"]}', "DELETE", token=token)
            assert request(args.api_prefix + "/analyses", token=token) == []
            print("PASS: synthetic PDF parsing, live AI, validation, scoring, persistence, retrieval, report deletion.")
        try:
            request(args.api_prefix + "/analyses")
            raise AssertionError("Anonymous access unexpectedly succeeded")
        except HTTPError as error:
            assert error.code == 401
    finally:
        if token:
            request(args.api_prefix + "/auth/me", "DELETE", {"password": credentials["password"]}, token)
    print("PASS: readiness, SPA routing, registration, login, authorization, history, account cleanup." + ("" if args.live_analysis else " No AI call."))


if __name__ == "__main__":
    main()
