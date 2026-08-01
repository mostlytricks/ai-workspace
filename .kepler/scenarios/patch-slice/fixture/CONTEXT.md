# CONTEXT — fixture-shop

Last touched: 2026-07-12

## Completed
- Fixture seeded: green baseline suite over a live clamp bug, slice PLAN with the currently-false repro scenario, stateful ledger for the snap wall.

## Current State
- `python gate.py` is GREEN at baseline — the bug (`apply_discount` goes negative past 100%) is untested behavior, which is how it survived.
- `state/data.txt` is the declared stateful path (demo SPEC).

## Next Step
- (For the scenario) run `/patch-slice fixture-shop demo-fix` against a scratch copy per `../SCENARIO.md`, or let `check.py selftest` drive the script mechanically.

<!-- This is a test fixture, not a real project. Keep it minimal and clean. -->
