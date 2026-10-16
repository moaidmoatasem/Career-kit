from __future__ import annotations

import json
from datetime import date
from pathlib import Path


class Budget:
    """Per-source daily call counter persisted to disk so limits survive restarts."""

    def __init__(self, path: Path, today: date | None = None):
        self.path = path
        self.today = (today or date.today()).isoformat()
        self.data: dict[str, dict[str, int]] = {}
        if path.is_file():
            self.data = json.loads(path.read_text(encoding="utf-8"))

    def used(self, source: str) -> int:
        return self.data.get(source, {}).get(self.today, 0)

    def allow(self, source: str, per_day: int) -> bool:
        return self.used(source) < per_day

    def record(self, source: str) -> None:
        self.data[source] = {self.today: self.used(source) + 1}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
