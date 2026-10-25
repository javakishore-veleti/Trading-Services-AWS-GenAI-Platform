from abc import ABC, abstractmethod


class AuthService(ABC):
    @abstractmethod
    def login(self, username: str, password: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def session(self, token: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def register_users(self, token: str, users: list[dict]) -> dict:
        raise NotImplementedError
