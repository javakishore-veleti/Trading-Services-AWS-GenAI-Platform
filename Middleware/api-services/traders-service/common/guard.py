import json
import os
import urllib.error
import urllib.request

from fastapi import HTTPException


def require_admin(authorization: str) -> dict:
    return _session(authorization, "admin")


def require_trader(authorization: str) -> dict:
    return _session(authorization, "trader")


def _session(authorization: str, role: str) -> dict:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Sign in again.")
    base = os.environ.get("AUTH_BASE_URL", "http://127.0.0.1:8501").rstrip("/")
    request = urllib.request.Request(
        f"{base}/session",
        headers={"Authorization": authorization},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            session = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode() or "Sign in again."
        raise HTTPException(status_code=exc.code, detail=_detail(detail)) from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail=f"Auth service is down: {exc.reason}") from exc
    if session.get("role") != role:
        raise HTTPException(status_code=403, detail=f"A {role} session is required.")
    return session


def register_traders(authorization: str, traders: list[dict]) -> None:
    password = os.environ.get("TRADER_PASSWORD", "local-trader")
    base = os.environ.get("AUTH_BASE_URL", "http://127.0.0.1:8501").rstrip("/")
    body = json.dumps({
        "users": [
            {
                "username": trader["username"],
                "password": password,
                "role": "trader",
                "trader_id": trader["trader_id"],
                "display_name": trader["display_name"],
            }
            for trader in traders
        ]
    }).encode()
    request = urllib.request.Request(
        f"{base}/users/bulk",
        data=body,
        headers={"Authorization": authorization, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode() or "Could not register trader logins."
        raise HTTPException(status_code=exc.code, detail=_detail(detail)) from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail=f"Auth service is down: {exc.reason}") from exc


def _detail(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    detail = parsed.get("detail", raw)
    return detail if isinstance(detail, str) else raw
