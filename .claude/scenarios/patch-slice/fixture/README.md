# fixture-shop

A minimal `.gravity/` project used only as the **golden input** for the `/patch-slice` golden-scenario (`.claude/scenarios/patch-slice/`). Not a real project — do not promote, junction, or build it.

It ships one deliberate bug under a green gate (the clamp in `app.py` is untested), a slice PLAN whose Scenario is the **currently-false repro** (the bug-intake worked example), and a gitignored-at-replay stateful ledger (`state/data.txt`) so the snap/rollback walls have real state to protect. The scenario copies this fixture, `git init`s the copy, runs the patch-loop ritual against it, and `check.py selftest` drives the same tree through both fork branches mechanically.
