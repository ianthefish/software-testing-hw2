"""Run a command and preserve its real output, exit status, and source hashes."""

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    output = Path(args.output)
    if output.exists() or output.with_suffix(".json").exists():
        parser.error("Evidence already exists; choose a new filename.")
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [Path("calculator.py"), *sorted(Path("tests").glob("*.py"))]
    hashes = {p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}
    timestamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding="utf-8", errors="replace")
    metadata = {"timestamp": timestamp, "cwd": str(Path.cwd()), "command": command,
                "returncode": result.returncode, "sha256": hashes}
    content = f"TIME={timestamp}\nCWD={Path.cwd()}\nCOMMAND={subprocess.list2cmdline(command)}\n\n"
    content += result.stdout + f"\nTEST_EXIT_CODE={result.returncode}\n"
    output.write_text(content, encoding="utf-8")
    output.with_suffix(".json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(content, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
