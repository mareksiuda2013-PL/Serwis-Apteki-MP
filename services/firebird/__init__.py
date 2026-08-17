from .config_service import ConfigService
from .firebird_service import FirebirdService
from .service_service import ServiceService
from .version_service import VersionService

__all__ = [
    "ConfigService",
    "FirebirdService",
    "ServiceService",
    "VersionService",
]

def __init__(self):

    super().__init__()

    if self.installation.gbak is None:
        raise RuntimeError("Brak gbak.exe")

    self.gbak = self.installation.gbak