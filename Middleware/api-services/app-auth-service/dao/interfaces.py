from abc import ABC, abstractmethod


class AuthDao(ABC):
    @abstractmethod
    def find_user(self, username: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def save_user(self, user: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_session(self, token: str, session: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_session(self, token: str) -> dict | None:
        raise NotImplementedError
