"""Verify saved provenance; run from a checkout with the original Git tags.

Optional --q7-repo points to the independent Q7 checkout (or its bundle clone).
Optional --original-root checks byte identity with the user's source attachments.
This checks evidence consistency, not independent human authorship.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent.parent


def git(*args, cwd=ROOT):
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={cwd.as_posix()}", *args], cwd=cwd
    )


def normalized(data):
    return data.replace(b"\r\n", b"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q7-repo", type=Path)
    parser.add_argument("--original-root", type=Path)
    args = parser.parse_args()
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    pairs = [("9dba640", "089ba50"), ("5c11076", "54535ba"),
             ("1cb2c97", "614df7f"), ("b631553", "32132ee")]
    for number, (red, green) in enumerate(pairs, 1):
        red_parent = git("rev-parse", f"{red}^").decode().strip()
        check(f"Q1 cycle {number}: tests precede implementation",
              git("rev-parse", f"{green}^").strip() == git("rev-parse", red).strip()
              and not git("diff", red_parent, red, "--", "calculator.py")
              and not git("diff", red, green, "--", "tests")
              and bool(git("diff", red, green, "--", "calculator.py")),
              {"red": red, "green": green})

    for path in sorted((ROOT / "evidence/q1").glob("*.json")):
        expected = 1 if "-red" in path.stem else 0
        data = json.loads(path.read_text(encoding="utf-8"))
        check(path.relative_to(ROOT).as_posix(), data["returncode"] == expected,
              {"expected_exit": expected, "actual_exit": data["returncode"]})

    test, implementation = "563359b", "b1b377f"
    check("Q6 separate test and implementation commits",
          git("rev-parse", f"{implementation}^").strip() == git("rev-parse", test).strip()
          and git("diff", "--name-only", test, implementation).decode().splitlines() == ["calculator.py"],
          {"test": test, "implementation": implementation})
    check("Q6 approved test unchanged",
          git("show", f"{test}:tests/test_q6.py") == normalized((ROOT / "tests/test_q6.py").read_bytes()),
          "Compared the approved commit blob with the final test file (LF-normalized).")
    before = git("show", f"{test}:calculator.py").decode()
    check("Q6 no implementation in test commit", "def modulo" not in before and "def power" not in before,
          "Both method definitions absent before the implementation commit.")
    approval = "我已審查並同意；授權你代為提交此測試，再實作"
    log = json.loads((ROOT / "ai-usage/main-session.json").read_text(encoding="utf-8"))
    check("Q6 actual review preserved",
          approval in (ROOT / "evidence/q6/review.txt").read_text(encoding="utf-8")
          and any(approval in m["text"] and m["role"] == "user" for m in log["messages"]),
          "Review text is present in both the record and the user-message export.")
    for phase, expected in [("red", 1), ("green", 0)]:
        data = json.loads((ROOT / f"evidence/q6/01-contract-{phase}.json").read_text(encoding="utf-8"))
        check(f"Q6 {phase}", data["returncode"] == expected, {"exit": data["returncode"]})

    check("Q2 identical faults", not git("diff", "q2-broken-first", "q2-broken-again", "--", "calculator.py", "tests", ".github"),
          "Compared calculator, tests, and workflow at the two fault tags.")
    check("Q2 blind repair changes calculator only",
          git("diff", "--name-only", "q2-broken-again", "q2-agent-result", "--", "calculator.py", "tests", ".github").decode().splitlines() == ["calculator.py"],
          "Evidence files are outside the product/test/workflow comparison.")
    expected_ci = ["success", "failure", "success", "failure", "success"]
    ci_paths = sorted((ROOT / "evidence/q2").glob("*-ci.json"))
    actual_ci = [json.loads(p.read_text(encoding="utf-8"))[0]["conclusion"] for p in ci_paths]
    check("Q2 five completed cloud results", actual_ci == expected_ci, actual_ci)

    original_test = git("show", "q1-complete:tests/test_calculator.py")
    check("Q7 received original Q1 test unchanged",
          original_test == normalized((ROOT / "experiments/q7/tests/test_calculator.py").read_bytes()),
          "Compared the Q1 tag with the preserved Q7 test.")
    if args.q7_repo:
        q7 = args.q7_repo.resolve()
        check("Q7 initial input contains only tests",
              sorted(git("ls-tree", "-r", "--name-only", "q7-tests-only", cwd=q7).decode().splitlines())
              == ["tests/__init__.py", "tests/test_calculator.py"],
              "Checked the independent project's initial tree.")
        first = git("show", "q7-first-implementation:calculator.py", cwd=q7)
        check("Q7 first generated calculator preserved",
              first == normalized((ROOT / "experiments/q7/calculator.py").read_bytes())
              and not git("diff", "q7-first-implementation", "q7-complete", "--", "calculator.py", cwd=q7),
              {"first_commit": git("rev-parse", "q7-first-implementation", cwd=q7).decode().strip()})

    if args.original_root:
        for name in ["Calc.py", "CalcTest.py", "CalcTDD (AI agent).pdf"]:
            src = (args.original_root / name).read_bytes()
            dst = (ROOT / "original" / name).read_bytes()
            check(f"Unchanged original: {name}", src == dst,
                  {"sha256": hashlib.sha256(src).hexdigest()})

    coverage = json.loads((ROOT / "evidence/q3/coverage.json").read_text(encoding="utf-8"))["totals"]
    check("Coverage evidence", coverage["num_statements"] == coverage["covered_lines"] == 15
          and coverage["num_branches"] == coverage["covered_branches"] == 2
          and coverage["excluded_lines"] == 0, coverage)
    check("Verified functionality unchanged during reporting",
          not git("diff", "q3-code-complete", "--", "calculator.py", "tests", "experiments/q7/calculator.py", "experiments/q7/tests", ".coveragerc", ".github/workflows/ci.yml", "requirements-dev.txt"),
          "Compared the working files with the successful coverage CI commit.")
    protected = []
    for path in (ROOT / "ai-usage").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".txt"}:
            if "gAAAA" in path.read_text(encoding="utf-8"):
                protected.append(path.relative_to(ROOT).as_posix())
    check("No protected ciphertext substituted for AI prompts", not protected, protected)
    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Evidence consistency only; does not establish independent human authorship.",
              "all_passed": all(c["passed"] for c in checks), "checks": checks}
    (ROOT / "evidence/submission-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in checks:
        print(f"{'PASS' if c['passed'] else 'FAIL'} {c['name']}")
    raise SystemExit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
