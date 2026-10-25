"""Run the supplied tests and preserve their output, exit code, and hashes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

label = sys.argv[1]
command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
started_at = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
Path(f"evidence/{label}.log").write_bytes(result.stdout)
metadata = {
    "command": command,
    "working_directory": str(Path.cwd()),
    "started_at_utc": started_at,
    "exit_code": result.returncode,
    "test_sha256": {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(Path("tests").glob("*.py"))
    },
}
Path(f"evidence/{label}.json").write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
Path(f"evidence/{label}.exitcode.txt").write_text(str(result.returncode) + "\n", encoding="utf-8")
sys.stdout.buffer.write(result.stdout)
sys.stdout.flush()
print(f"Saved exit code: {result.returncode}")
raise SystemExit(result.returncode)
