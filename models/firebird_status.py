from dataclasses import dataclass
from pathlib import Path


@dataclass
class FirebirdStatus:
    running: bool
    version: str
    service_name: str
    install_path: Path | None
    database_connected: bool = False
    message: str = ""