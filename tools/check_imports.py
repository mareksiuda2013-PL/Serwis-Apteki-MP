from __future__ import annotations

import sys
from pathlib import Path
from importlib import import_module

# Dodaj katalog główny projektu do PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODULES = [
    "main",
    "core.module_manager",
    "gui.main_window",
    "modules.dashboard.page",
    "modules.firebird.page",
    "modules.firebird.controller",
    "services.firebird.firebird_service",
    "services.firebird.discovery.installation_service",
    "services.firebird.service_service",
    "services.firebird.database_service",
]

failed = False

print(f"Project root: {PROJECT_ROOT}\n")

for module in MODULES:

    try:
        import_module(module)
        print(f"[ OK ] {module}")

    except Exception as e:

        failed = True

        print(f"[ERR ] {module}")
        print(f"       {type(e).__name__}: {e}")

if failed:
    raise SystemExit(1)

print("\n✅ Wszystkie importy poprawne.")