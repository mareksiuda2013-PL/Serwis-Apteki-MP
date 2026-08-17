from dataclasses import dataclass
from pathlib import Path


@dataclass
class FirebirdInstallation:
    version: str
    install_path: Path
    bin_path: Path
    service_name: str
    fbclient_path: Path
    firebird_exe: Path