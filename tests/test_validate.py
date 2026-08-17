from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.validate_service import ValidateService

service = ValidateService()

result = service.validate()

print(result.success)
print(result.return_code)
print(result.stdout)
print(result.stderr)