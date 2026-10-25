import json
import os
from pathlib import Path


def dataset_path(*parts: str) -> Path:
    configured = os.environ.get("DATASETS_DIR", "").strip()
    root = Path(configured) if configured else Path(__file__).resolve().parents[4] / "CICD" / "Local" / "DataSets"
    return root.joinpath(*parts)


def read_json(path: Path) -> list:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
