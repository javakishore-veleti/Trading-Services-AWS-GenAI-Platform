import hmac
import secrets

from dao.impl.store import digest
from dao.interfaces import AuthDao
from services.interfaces import AuthService


class AuthError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class AuthServiceImpl(AuthService):
    def __init__(self, dao: AuthDao) -> None:
        self._dao = dao

    def login(self, username: str, password: str) -> dict:
        user = self._dao.find_user(username.strip())
        if user is None or not hmac.compare_digest(user["password_digest"], digest(password)):
            raise AuthError(401, "The username or password is wrong.")
        token = secrets.token_urlsafe(32)
        session = self._public(user)
        self._dao.save_session(token, session)
        return {"token": token, **session}

    def session(self, token: str) -> dict:
        found = self._dao.find_session(token.strip())
        if found is None:
            raise AuthError(401, "Sign in again.")
        return found

    def register_users(self, token: str, users: list[dict]) -> dict:
        actor = self.session(token)
        if actor["role"] != "admin":
            raise AuthError(403, "An administrator session is required.")
        for user in users:
            self._dao.save_user({
                "username": user["username"],
                "password_digest": digest(user["password"]),
                "role": user.get("role", "trader"),
                "trader_id": user.get("trader_id", ""),
                "display_name": user.get("display_name", user["username"]),
            })
        return {"registered": len(users)}

    def _public(self, user: dict) -> dict:
        return {
            "username": user["username"],
            "role": user["role"],
            "trader_id": user["trader_id"],
            "display_name": user["display_name"],
        }
