from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.process_runner import ProcessRunner

runner = ProcessRunner()

result = runner.run(
    ["cmd", "/c", "echo", "TEST OK"]
)

print(result.success)
print(result.stdout)
print(result.stderr)
print(result.return_code)