from pathlib import Path
import sys
import traceback

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:

    from services.firebird.discovery.installation_service import InstallationService

    print("Import OK")

    service = InstallationService()

    fb = service.first_installation()

    print("Wynik:")
    print(fb)

    if fb:
        print("Install :", fb.install_path)
        print("ISQL    :", fb.isql)
        print("GBAK    :", fb.gbak)
        print("GFIX    :", fb.gfix)
        print("FBCLIENT:", fb.fbclient)
        print("CONF    :", fb.firebird_conf)

except Exception:
    traceback.print_exc()