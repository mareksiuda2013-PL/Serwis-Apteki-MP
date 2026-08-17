from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.sweep_service import SweepService

service = SweepService()

result = service.sweep()

print(result.success)
print(result.return_code)
print(result.stdout)
print(result.stderr)