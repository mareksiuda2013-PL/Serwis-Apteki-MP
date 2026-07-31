from dataclasses import dataclass, field


@dataclass
class OperationResult:
    success: bool
    message: str
    data: dict = field(default_factory=dict)