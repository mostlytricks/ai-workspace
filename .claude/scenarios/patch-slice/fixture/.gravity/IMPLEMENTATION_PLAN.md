# fixture-shop — Implementation plan & resume sheet

> One-line working scenario: a minimal buggy project that exists only to test `/patch-slice`.
> Branch `main` · last updated 2026-07-12.

## Status right now

Fixture with one wired domain (`demo`), a green gate, and one deliberate untested bug.

```
roadmap:  1 (next)
goal:     stay a clean, minimal patch-target for the /patch-slice golden-scenario
```

## Domain status spine

`○ planned · ◑ building · ✓ shipped`

| Domain | Status | Owns |
|---|---|---|
| `demo` | ◑ | the discount engine — `app.py`, its suite, the `state/` ledger |

## Phase roadmap

### Phase 1 — Fix the clamp bug · next
Land `.gravity/demo/PLAN.fix.md` via the patch-loop ritual. (Fixture placeholder — the scenario replays this forever.)

## Locked decisions

- This is a test fixture — the bug is load-bearing; never fix it *in the fixture itself*.

## The gate

`python gate.py` — the unit suite, true exit code.
