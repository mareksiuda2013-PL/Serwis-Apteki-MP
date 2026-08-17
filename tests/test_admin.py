from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.system.admin_service import AdminService


print("Administrator:", AdminService.is_admin())
print("Status:", AdminService.status())