from __future__ import annotations

from dataclasses import asdict, dataclass

ERROR = "error"
WARNING = "warning"
INFO = "info"


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    where: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
