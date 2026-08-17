from pathlib import Path
import sys
import traceback

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from services.firebird.restore_service import RestoreService

    print("Import OK")

    restore = RestoreService()

    print("Service OK")

    ok, log = restore.restore(
        r"C:\KSBAZA\KS-APW\WAPTEKA_TEST.fbk",
        r"C:\KSBAZA\KS-APW\RESTORE_TEST.FDB",
    )

    print(ok)
    print(log)

except Exception:
    traceback.print_exc()