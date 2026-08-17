from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from services.firebird.client import FirebirdClient
from services.firebird.installation_service import InstallationService

cfg = Config()

installation = InstallationService().first_installation()

client = FirebirdClient(installation)

print(client.fetch_one(
    cfg.database,
    cfg.user,
    cfg.password,
    "SELECT CURRENT_USER FROM RDB$DATABASE;"
))

print()

print(client.fetch_all(
    cfg.database,
    cfg.user,
    cfg.password,
    "SELECT FIRST 5 RDB$RELATION_NAME FROM RDB$RELATIONS;"
))