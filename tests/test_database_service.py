from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.database_service import DatabaseService

db = DatabaseService()

print("Version :", db.version())
print("ODS     :", db.ods())
print("Dialect :", db.sql_dialect())
print("Page    :", db.page_size())
print("Tables  :", db.tables())