# demo — PLAN.fix

Status: ○ planned

## Goal

Fix the clamp bug: `apply_discount(100, 150)` returns `-50` — a negative price — because `pct` is never clamped. The fix is done only when the regression test exists and is green.

## Scenario

<!-- BUG INTAKE (the worked example): this scenario is CURRENTLY FALSE — it is the repro,
     stated as the behavior the system does not yet exhibit. The slice is complete only
     when a named test asserts it; then it graduates into the demo SPEC's Behavioral
     Contract as [test:test_clamp_over_100]. A bug you can't state this way isn't
     understood well enough to patch. -->

- given price 100, when a 150% discount applies → 0 (clamped — never a negative price)

## Slice

- **[MODIFY]** `app.py` — clamp `pct` to `[0, 100]` inside `apply_discount`.
- **[NEW]** `tests/test_app.py::test_clamp_over_100` — the scenario above, asserted by name.

## Verification

1. `python gate.py` — green, including the new `test_clamp_over_100`.
2. Behavioral drive (the real entry point, not just the suite): `python -c "from app import apply_discount; print(apply_discount(100, 150))"` → `0.0`.
