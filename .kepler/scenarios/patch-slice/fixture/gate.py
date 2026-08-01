"""fixture-shop's real gate: run the unit suite, exit with its true status.

This is the command the demo SPEC's Gate line names (`python gate.py`).
It must be run BARE - never piped - so the exit code is the suite's own (F4).
"""
import subprocess
import sys

sys.exit(subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]
).returncode)
