from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.client import FirebirdClient
from services.firebird.discovery.installation_service import InstallationService


def test_fetch_one():
    installation = InstallationService().first_installation()

    client = FirebirdClient(installation)

    result = client.fetch_one(
        "SELECT CURRENT_USER FROM RDB$DATABASE;"
    )

    assert result is not None


def test_fetch_all():
    installation = InstallationService().first_installation()

    client = FirebirdClient(installation)

    result = client.fetch_all(
        "SELECT FIRST 5 RDB$RELATION_NAME FROM RDB$RELATIONS;"
    )

    assert result is not None