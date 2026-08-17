from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.mend_service import MendService


def test_mend_service_creation():

    service = MendService()

    assert service is not None