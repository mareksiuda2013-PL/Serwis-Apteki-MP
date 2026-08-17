from pathlib import Path
import sys
import traceback

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:

    from services.firebird.statistics_service import StatisticsService

    print("Import OK")

    service = StatisticsService()

    print("Service OK")

    result = service.header()

    print("Success :", result.success)
    print("Code    :", result.return_code)

    print("\n===== STDOUT =====\n")
    print(result.stdout)

    print("\n===== STDERR =====\n")
    print(result.stderr)

except Exception:
    traceback.print_exc()