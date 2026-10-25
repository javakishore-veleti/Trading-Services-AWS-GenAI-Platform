import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

SERVICE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVICE_DIR))

from presentation.object_factory import PresentationObjectFactory


class CustomerApp:
    def __init__(self) -> None:
        self._name = "customer-service"
        self._port = 8503

    def build(self) -> FastAPI:
        app = FastAPI(title=self._name)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://127.0.0.1:4200", "http://127.0.0.1:4201"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_api_route("/health", self.health, methods=["GET"])
        app.include_router(PresentationObjectFactory.api().router)
        return app

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": self._name}

    def run(self) -> None:
        uvicorn.run(self.build(), host="127.0.0.1", port=self._port)


if __name__ == "__main__":
    CustomerApp().run()
