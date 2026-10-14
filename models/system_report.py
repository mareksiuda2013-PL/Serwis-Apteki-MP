from __future__ import annotations

from dataclasses import dataclass, field


STATUS_OK = "OK"
STATUS_WARNING = "WARNING"
STATUS_ERROR = "ERROR"


@dataclass(slots=True)
class ReportItem:
    name: str
    status: str = STATUS_OK
    message: str = ""


@dataclass(slots=True)
class SystemReport:
    items: list[ReportItem] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(item.status == STATUS_ERROR for item in self.items):
            return STATUS_ERROR

        if any(item.status == STATUS_WARNING for item in self.items):
            return STATUS_WARNING

        return STATUS_OK

    @property
    def has_errors(self) -> bool:
        return self.status == STATUS_ERROR

    @property
    def has_warnings(self) -> bool:
        return self.status == STATUS_WARNING

    def add(
        self,
        name: str,
        status: str = STATUS_OK,
        message: str = "",
    ) -> ReportItem:
        item = ReportItem(
            name=name,
            status=status,
            message=message,
        )

        self.items.append(item)

        return item