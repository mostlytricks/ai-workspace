# fixture-app

> **gravity: v1.2** · _golden-scenario fixture — a minimal, deliberately clean `.gravity/` project used to test the `/new-spec` command. Not a real project._

A tiny stand-in project that exists only so `/new-spec` has something to run against. It has exactly **one** subject domain — `model` — fully wired into all four registry indexes, **with real code and a real gate but no `SPEC.md` yet**. A correct `/new-spec` run authors `.gravity/model/SPEC.md` with *honest* enforcement tags (the Gate and every `[lint]`/`[test:]` tag verifiable against `package.json` + `tests/`); `check.py` proves it.

> **Docs live in `.gravity/`.** This `CLAUDE.md` (identity + router) and `CONTEXT.md` (*now*) stay at the root and auto-load; everything else is organized by subject domain under `.gravity/`.

---

## Stack

- Node 20, plain ESM JavaScript (`.mjs`), no dependencies.

## Test

- **`npm run lint:model`** (`scripts/check-model.mjs`) — validates every `data/*.json` record against `src/model.mjs`; exits non-zero on a violation. This is the model domain's real gate.
- **`npm test`** (`node --test tests/`) — the named behavioral tests (`model-required-fields`, `model-status-vocabulary`).

## Doc Map (`.gravity/`)

Docs are grouped by **subject domain**, not by doc-type. Recognized only when present.

```
.gravity/
  MISSION.html              # why — north star + the system in N domains
  IMPLEMENTATION_PLAN.md    # what/next — roadmap + per-domain status spine
  model/                    # the data model — record shape + validation
```

`MISSION.html` owns *why*, `IMPLEMENTATION_PLAN.md` the roadmap + per-domain status, `CONTEXT.md` *now*.

## What to read before a change (router)

| If you're changing… | Read first | Human reference |
|---|---|---|
| The data model / record validation | `.gravity/model/PLAN.md` | — |

## Entry Points

- `src/model.mjs` — `validateRecord` + the `REQUIRED_FIELDS`/`STATUS_VALUES` vocabulary (the real shape a SPEC copies).
- `scripts/check-model.mjs` — the gate; validates `data/*.json`.
- `tests/model.test.mjs` — `node:test` behavioral tests.

## Git

- Remote: *none* (fixture)
- Default branch: `main`
