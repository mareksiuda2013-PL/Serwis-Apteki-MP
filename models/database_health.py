from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class HealthCheck:
    name: str
    status: str = "UNKNOWN"
    value: str = ""
    message: str = ""


@dataclass(slots=True)
class DatabaseHealth:
    status: str = "UNKNOWN"
    summary: str = ""
    checks: list[HealthCheck] = field(
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