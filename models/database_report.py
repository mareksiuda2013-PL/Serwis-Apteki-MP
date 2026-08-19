from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from models import DatabaseStatistics
from services.firebird.diagnostics_service import DiagnosticResult


@dataclass(slots=True)
class ReportOperation:
    name: str
    status: str
    message: str = ""


@dataclass(slots=True)
class DatabaseReport:
    database: str = ""
    generated_at: str = ""

    statistics: DatabaseStatistics | None = None
    diagnostic: DiagnosticResult | None = None

    recommendations: list[str] = field(
        default_factory=list
    )

    operations: list[ReportOperation] = field(
        default_factory=list
    )

    summary: str = ""

    def __post_init__(self) -> None:

        if not self.generated_at:

            self.generated_at = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )