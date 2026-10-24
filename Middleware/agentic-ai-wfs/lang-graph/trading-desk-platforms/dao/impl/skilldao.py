from pathlib import Path

from dao.interfaces import SkillDao


class FileSkillDao(SkillDao):
    """Reads one skill file. It does not open the other desk skills."""

    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parents[6]

    def load(self, name: str) -> str | None:
        path = self._root / "Middleware" / "skills" / name / "skills" / name / "SKILL.md"
        if not path.is_file():
            return None
        return path.read_text()
