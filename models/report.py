from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReportItem:
    section: str
    name: str
    status: str = "INFO"
    value: str = ""
    message: str = ""


@dataclass(slots=True)
class DatabaseReport:
    database: str = ""
    status: str = "UNKNOWN"
    summary: str = ""

    items: list[ReportItem] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )

    @property
    def is_ok(self) -> bool:
        return self.status == "OK"

    @property
    def has_warning(self) -> bool:
        return self.status == "WARNING"

    @property
    def has_error(self) -> bool:
        return self.status == "ERROR"