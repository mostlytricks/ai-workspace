# fixture-shop

> **gravity: v2.2** · _golden-scenario fixture — a minimal `.gravity/` project with one deliberate bug, used to test `/patch-slice`. Not a real project._

A tiny discount engine that exists only so `/patch-slice` (and `patch_slice.py`'s selftest) have something real to patch: a green gate over a live bug, a slice PLAN stating the repro as a currently-false scenario, and gitignored state for the snap/rollback walls.

> **Docs live in `.gravity/`.** This `CLAUDE.md` (identity + router) and `CONTEXT.md` (*now*) stay at the root and auto-load; everything else is organized by subject domain under `.gravity/`.

---

## Run / Test

```bash
python gate.py            # the gate: unit suite, true exit code
python probe_state.py     # exercises state/data.txt (rollback proof 4)
```

## Doc Map (`.gravity/`)

Docs are grouped by **subject domain**, not by doc-type. Recognized only when present.

```
.gravity/
  MISSION.html              # why — north star + the system in N domains
  IMPLEMENTATION_PLAN.md    # what/next — roadmap + per-domain status spine
  demo/                     # the discount engine — app.py + its suite + state ledger
```

`MISSION.html` owns *why*, `IMPLEMENTATION_PLAN.md` the roadmap + per-domain status, `CONTEXT.md` *now*.

## What to read before a change (router)

| If you're changing… | Read first | Human reference |
|---|---|---|
| The discount engine / its suite | `.gravity/demo/SPEC.md` | — |

## Git

- Remote: *none* (fixture; the scenario replay runs `git init` in a scratch copy)
- Default branch: `main`
