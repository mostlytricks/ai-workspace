# fixture-app

> **gravity: v1.1** · _golden-scenario fixture — a minimal, deliberately clean `.gravity/` project used to test the `/new-domain` command. Not a real project._

A tiny stand-in project that exists only so `/new-domain` has something to run against. It has exactly **one** subject domain — `model` — fully wired into all four registry indexes. A correct `/new-domain` run adds a second domain wired the same way; `check.py` proves it.

> **Docs live in `.gravity/`.** This `CLAUDE.md` (identity + router) and `CONTEXT.md` (*now*) stay at the root and auto-load; everything else is organized by subject domain under `.gravity/`.

---

## Doc Map (`.gravity/`)

Docs are grouped by **subject domain**, not by doc-type. Recognized only when present.

```
.gravity/
  MISSION.html              # why — north star + the system in N domains
  IMPLEMENTATION_PLAN.md    # what/next — roadmap + per-domain status spine
  model/                    # the data model — Prisma schema + entities
```

`MISSION.html` owns *why*, `IMPLEMENTATION_PLAN.md` the roadmap + per-domain status, `CONTEXT.md` *now*.

## What to read before a change (router)

| If you're changing… | Read first | Human reference |
|---|---|---|
| The data model / entities | `.gravity/model/PLAN.md` | — |

## Adding a domain (start here for a new feature)

A **domain** earns a `.gravity/<domain>/` folder only when it has its own *principle* + a multi-step arc. Mint with `/new-domain fixture-app <domain>`, which wires all four indexes (this Doc Map + router table, the MISSION why-row, the PLAN status spine) so it's never orphaned. Start minimal — usually just a `PLAN.md` on day one.

## Git

- Remote: *none* (fixture)
- Default branch: `main`
