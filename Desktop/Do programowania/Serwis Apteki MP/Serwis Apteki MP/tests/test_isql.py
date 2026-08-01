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

ok, output = client.execute(
    database=cfg.database,
    user=cfg.user,
    password=cfg.password,
    sql="""
SELECT CURRENT_USER
FROM RDB$DATABASE;
""",
)

print(ok)
print(output)