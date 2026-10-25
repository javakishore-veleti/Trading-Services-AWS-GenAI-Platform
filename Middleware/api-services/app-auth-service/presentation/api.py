from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from services.impl.authsvc import AuthError
from services.object_factory import ServiceObjectFactory


class LoginBody(BaseModel):
    username: str
    password: str


class UserBody(BaseModel):
    username: str
    password: str
    role: str = "trader"
    trader_id: str = ""
    display_name: str = ""


class UsersBody(BaseModel):
    users: list[UserBody] = Field(default_factory=list)


class AuthApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/session", self.session, methods=["GET"])
        self.router.add_api_route("/users/bulk", self.register_users, methods=["POST"])

    def login(self, body: LoginBody) -> dict:
        try:
            return ServiceObjectFactory.auth_service().login(body.username, body.password)
        except AuthError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc

    def session(self, authorization: str = Header(default="")) -> dict:
        try:
            return ServiceObjectFactory.auth_service().session(_token(authorization))
        except AuthError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc

    def register_users(self, body: UsersBody, authorization: str = Header(default="")) -> dict:
        try:
            return ServiceObjectFactory.auth_service().register_users(
                _token(authorization),
                [user.model_dump() for user in body.users],
            )
        except AuthError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc


def _token(authorization: str) -> str:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Sign in again.")
    return authorization[len(prefix):]
