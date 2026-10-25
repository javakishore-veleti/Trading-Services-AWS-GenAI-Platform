import hashlib

from dao.interfaces import AuthDao


def digest(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class AuthDaoImpl(AuthDao):
    def __init__(self) -> None:
        self._users: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}
        self.save_user({
            "username": "admin",
            "password_digest": digest("local-admin"),
            "role": "admin",
            "trader_id": "",
            "display_name": "Administrator",
        })

    def find_user(self, username: str) -> dict | None:
        return self._users.get(username)

    def save_user(self, user: dict) -> None:
        self._users[user["username"]] = user

    def save_session(self, token: str, session: dict) -> None:
        self._sessions[token] = session

    def find_session(self, token: str) -> dict | None:
        return self._sessions.get(token)
