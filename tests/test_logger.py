from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import Logger


logger = Logger()

logger.log(
    "TEST",
    True,
    "Logger działa poprawnie",
)

print("Logger OK")
