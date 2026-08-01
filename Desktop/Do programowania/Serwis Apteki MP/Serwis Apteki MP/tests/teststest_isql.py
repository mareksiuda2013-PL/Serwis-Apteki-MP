from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.firebird.client import FirebirdClient

client = FirebirdClient(
    r"C:\Program Files\Firebird\Firebird_3_0\bin\isql.exe"
)

ok, output = client.execute(
    database=r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
    user="SYSDBA",
    password="masterkey",
    sql="""
SELECT CURRENT_USER
FROM RDB$DATABASE;
""",
)

print("OK:", ok)
print(output)