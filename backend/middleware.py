"""Small ASGI middleware: bounded bodies, request IDs, and privacy-safe logs."""
import json
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

from starlette.responses import JSONResponse

logger = logging.getLogger("careerlens.requests")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.propagate = False


class RequestProtection:
    def __init__(self, app):
        self.app = app
        self.attempts = defaultdict(deque)
        self.lock = Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = uuid.uuid4().hex
        started = time.perf_counter()
        status = 500

        async def protected_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).extend([
                    (b"x-request-id", request_id.encode()),
                    (b"x-content-type-options", b"nosniff"),
                    (b"cache-control", b"no-store"),
                ])
            await send(message)

        async def reject(code, detail):
            await JSONResponse({"detail": detail}, status_code=code)(scope, receive, protected_send)

        try:
            # IP-based local abuse protection, independent of success or failure.
            # Proxy trust must be configured at the server; never trust arbitrary X-Forwarded-For.
            auth_path = scope["path"]
            prefix = os.getenv("API_PREFIX", "").rstrip("/")
            if prefix and auth_path.startswith(prefix + "/"):
                auth_path = auth_path[len(prefix):]
            if (scope["method"] == "POST" and auth_path in ("/auth/login", "/auth/register")) or (
                scope["method"] == "DELETE" and auth_path == "/auth/me"
            ):
                key = (scope.get("client") or ("unknown",))[0]
                now = time.monotonic()
                with self.lock:
                    # Expire idle clients to bound the map, not only each client's deque.
                    for old in list(self.attempts):
                        if not self.attempts[old] or self.attempts[old][-1] <= now - 60:
                            del self.attempts[old]
                    history = self.attempts[key]
                    while history and history[0] <= now - 60:
                        history.popleft()
                    limited = len(history) >= int(os.getenv("AUTH_REQUESTS_PER_MINUTE", "20"))
                    if not limited:
                        history.append(now)
                if limited:
                    return await reject(429, "Too many authentication attempts. Try again in a minute.")
            maximum = 6 * 1024 * 1024
            headers = dict(scope.get("headers", []))
            try:
                length = int(headers.get(b"content-length", b"0"))
            except ValueError:
                return await reject(400, "Invalid Content-Length.")
            if length < 0:
                return await reject(400, "Invalid Content-Length.")
            if length > maximum:
                return await reject(413, "The total request must be at most 6 MB.")
            # Read at most the limit even when Content-Length is absent or inaccurate.
            messages, size = [], 0
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                size += len(message.get("body", b""))
                if size > maximum:
                    return await reject(413, "The total request must be at most 6 MB.")
                messages.append(message)
                if not message.get("more_body", False):
                    break
            index = 0

            async def replay():
                nonlocal index
                if index < len(messages):
                    item = messages[index]
                    index += 1
                    return item
                return await receive()

            await self.app(scope, replay, protected_send)
        finally:
            # Never log tokens, query strings, document contents, email addresses, or provider responses.
            logger.info(json.dumps({"request_id": request_id, "method": scope["method"],
                                   "path": scope["path"], "status": status,
                                   "duration_ms": round((time.perf_counter() - started) * 1000)}))
