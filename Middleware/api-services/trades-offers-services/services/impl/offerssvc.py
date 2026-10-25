from dao.interfaces import OffersDao
from services.interfaces import OffersService


class OffersError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class OffersServiceImpl(OffersService):
    def __init__(self, dao: OffersDao) -> None:
        self._dao = dao

    def quote(self, base: str, term: str, direction: str) -> dict:
        found = self._dao.quote(base, term, direction or "sell_base")
        if found is None:
            raise OffersError(404, f"No quote is published for {base}/{term}.")
        return found
