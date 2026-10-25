# Q7 tests-only implementation evidence

Only the supplied tests in this directory were used to determine the implementation. No supplied test was edited, and no commit or push was performed.

## Implementation

`calculator.py` defines `Calculator.add`, `subtract`, `multiply`, and `divide`. The first three use Python arithmetic operators. Division uses true division, which returns a float for the integer inputs in the supplied tests. A zero divisor explicitly raises `ValueError`.

## Validation

Command, run from this directory with the required Python executable:

```powershell
& 'C:\Users\ianyu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest discover -s tests -v
```

- Before implementation: test discovery could not import the missing `calculator` module. The runner reported one failed test-module load, `FAILED (errors=1)`, and exit code 1.
- After implementation: all 5 supplied test methods passed; exit code 0.
- SHA-256 hashes recorded before and after match for both supplied Python test files.

The supplied tests cover one addition example; six subtraction examples; six multiplication examples; six division examples (including float result type); and one division-by-zero case. They include positive and negative integers and zero where explicitly listed by the tests.

This validates the supplied tests only. Other inputs, additional behaviors, and hidden tests were not evaluated.

## Evidence files

- `before.log` and `after.log`: actual combined standard output and standard error, saved as emitted by Python.
- `before.exitcode.txt` and `after.exitcode.txt`: actual process exit codes.
- `before.json` and `after.json`: command, working directory, UTC start time, exit code, and supplied-test SHA-256 hashes.
- `run_tests.py`: reusable runner used to collect the evidence.
