import json
import os
import urllib.error
import urllib.request

from fastapi import HTTPException


def require_admin(authorization: str) -> dict:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Sign in again.")
    base = os.environ.get("AUTH_BASE_URL", "http://127.0.0.1:8501").rstrip("/")
    request = urllib.request.Request(f"{base}/session", headers={"Authorization": authorization})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            session = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode() or "Sign in again."
        raise HTTPException(status_code=exc.code, detail=_detail(detail)) from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail=f"Auth service is down: {exc.reason}") from exc
    if session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="An administrator session is required.")
    return session


def _detail(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    detail = parsed.get("detail", raw)
    return detail if isinstance(detail, str) else raw
