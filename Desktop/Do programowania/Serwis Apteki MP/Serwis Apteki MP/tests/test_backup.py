from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.backup_service import BackupService

backup = BackupService()

ok, log = backup.backup(
    r"C:\KSBAZA\KS-APW\WAPTEKA_TEST.fbk"
)

print(ok)
print(log)