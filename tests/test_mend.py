from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.mend_service import MendService

service = MendService()

result = service.mend()

print(result.success)
print(result.return_code)
print(result.stdout)
print(result.stderr)