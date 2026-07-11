# demo — SPEC

> Agent-loadable rule sheet for the `demo` domain (the discount engine). Golden-scenario fixture — deliberately tiny. Human rationale: the MISSION row; there is no ARCHITECTURE facet.

**Gate:** `python gate.py` — runs the unit suite; exits with its true status.

**Stateful paths:** `state/data.txt`

<!-- The seed ledger: gitignored at replay time, snapshotted by `patch_slice.py snap`
     before any patch. The line above is machine-read (comma-separated paths ONLY —
     prose on it would be parsed as more paths). -->

<!-- Legend: [lint] the linter fails on a violation · [test:name] a named test asserts it · [review] human judgment only. -->

## Minimal Shape

A pure function in `app.py` plus its named test in `tests/test_app.py`. Generate loop: state the behavior as given/when/then in the slice PLAN → write the named test → make it pass.

## Rules

- `[test:test_basic]` a discount reduces the price proportionally
- `[review]` engine functions stay pure — `state/` is read only by tools (`probe_state.py`), never by `app.py`

## Behavioral Contract

- `[test:test_basic]` given price 100, when a 20% discount applies → 80
- `[test:test_zero_pct]` given price 100, when a 0% discount applies → 100

<!-- The clamp scenario (never negative) lives in PLAN.fix.md as a currently-false
     scenario. It graduates here as [test:test_clamp_over_100] only when the patch
     lands that named test — intent becomes contract by earning a wall. -->
