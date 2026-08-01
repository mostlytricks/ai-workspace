# CONTEXT — fixture-app

Last touched: 2026-07-02

## Completed
- Fixture seeded with one fully-wired domain (`model`) carrying real code + a real gate but **no SPEC.md**, for the `/new-spec` golden-scenario.

## Current State
- One domain (`model`) exists and is wired into all four registry indexes. `npm run lint:model` and `npm test` are green; `.gravity/model/` has only a `PLAN.md`.

## Next Step
- (For the scenario) run `/new-spec fixture-app model` against a copy of this fixture, then `check.py scenario`.

<!-- This is a test fixture, not a real project. Keep it minimal and clean. -->
