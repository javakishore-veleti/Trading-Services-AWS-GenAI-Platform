import sys
from pathlib import Path

import uvicorn

SERVICE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(SERVICE_DIR.parent))

from presentation.object_factory import PresentationObjectFactory
from service import ProcessHost


class MasterDataApp:
    def run(self) -> None:
        api = PresentationObjectFactory.api()
        mcp_layer = PresentationObjectFactory.mcp()
        app = ProcessHost("traders-master-data-mcp", mcp_layer.server, api.router).build()
        uvicorn.run(app, host="127.0.0.1", port=8105)


if __name__ == "__main__":
    MasterDataApp().run()
