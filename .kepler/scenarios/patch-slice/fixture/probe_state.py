"""Proof 4 for rollback (F7): the restored state must actually FUNCTION,
not just diff clean. Reads the seed ledger and validates its shape."""
import sys
from pathlib import Path

try:
    text = Path("state/data.txt").read_text(encoding="utf-8")
    key, _, value = text.strip().partition("=")
    ok = key == "seed" and value.isdigit()
except (OSError, UnicodeDecodeError):
    ok = False
print("state probe: " + ("OK" if ok else "CORRUPT"))
sys.exit(0 if ok else 1)
