<!--
GRAVITY.template.md — the router block for a project that adopts the `.gravity/` doc
system (workspace CLAUDE.md §6). Paste these three sections into the project's ROOT
`CLAUDE.md` (which stays at the root and auto-loads — it is the only router). Delete
this comment and fill every <…>. `/adopt-gravity` seeds this for you.

Keep it a ROUTER, not a second architecture doc: it points at where things live, it
does not restate them. One concern, one home.
-->

> **gravity: v1.0** · _the version of the workspace gravity system this project adopted (root `VERSION` / `CHANGELOG.md`). Bump when you re-sync to a newer skeleton; `/triage` flags drift._

> **Docs live in `.gravity/`.** This `CLAUDE.md` (identity, *how*) and `CONTEXT.md` (*now*) stay at the project root and auto-load; `README.md` is the user guide. Everything else — the *why*, *what/next*, and *how it's built* — is organized **by subject domain** under `.gravity/`. See the **Doc Map** below. One concern, one home — link, don't restate.

## Doc Map (`.gravity/`)

Docs are grouped by **subject domain**, not by doc-type. A domain folder holds whichever of three kinds it needs — `ARCHITECTURE.html` (human deep-dive), `SPEC.md` (agent contract), `PLAN.*.md` (what/next) — named by *kind* because the folder already names the subject. **Recognized only when present.**

```
.gravity/
  MISSION.html              # why — north star (browser-read)
  ARCHITECTURE.html         # how — system overview (browser-read)
  IMPLEMENTATION_PLAN.md    # what/next — roadmap spine + per-domain status
  DESIGN.md                 # visual-token contract (UI projects only)
  <domain>/   ARCHITECTURE.html · SPEC.md · PLAN.*.md   # one folder per subject; add lines as domains appear
  integration/ SPEC.md · ARCHITECTURE.html · PLAN.*.md   # optional: cross-service/domain contracts only
```

`SPEC.md` is the spec you hand an agent for a change — a Minimal Shape to build *from* + enforcement-tagged Rules that *fence* it (`[lint]`/`[type]`/`[test:name]`/`[review]`/`[—]`); `ARCHITECTURE.html` is the human reference behind it (load it rarely — it's styled HTML). `MISSION.html` owns *why*, `IMPLEMENTATION_PLAN.md` the roadmap spine + per-domain status, `CONTEXT.md` *now*.

## What to read before a change (router)

Before touching a domain, load its `SPEC.md` — the compact agent contract. The paired `ARCHITECTURE.html` is the human reference behind it (read only when you need the full rationale). A "—" means that kind doesn't exist for the domain yet.

| If you're changing… | Read first | Human reference |
|---|---|---|
| <what an agent might change in this domain> | `.gravity/<domain>/SPEC.md` | `.gravity/<domain>/ARCHITECTURE.html` |
| Cross-service API/auth/env/typegen/queue/webhook/data-flow contract | `.gravity/integration/SPEC.md`, then affected domain SPECs | `.gravity/integration/ARCHITECTURE.html` |
| <…> | `.gravity/<domain>/SPEC.md` | — |

## Adding a domain (start here for a new feature)

A **domain** is a durable subject area an agent will repeatedly navigate and change — not every feature is one. Mint a `.gravity/<domain>/` folder only when the feature has its own *gravity*; otherwise it's a slice under an existing domain. (`/new-domain <project> <domain>` does steps 2–3 for you.) The optional `integration` domain is reserved for contracts between services/domains: API/client type flow, auth/session behavior, ports/base URLs, shared env, queues/events, webhooks, database access boundaries, and required change order.

**1. Gate — is it a domain?** It earns a folder when it has its own *principle* and you can say yes to most of:
- rules an agent must respect to change it safely → wants a `SPEC.md`
- a "how it's built" a human needs beyond a file map → wants an `ARCHITECTURE.html`
- a multi-step arc, not a single PR → wants a `PLAN.*.md`
- a one-line *why* + non-goal that should win arguments → wants a MISSION row
- for `integration`: a cross-boundary contract that repeatedly affects more than one domain/service → wants an integration `SPEC.md`; otherwise keep it in `CONTRACT.md`

If not: it's a **`PLAN.*.md` under an existing domain** (or an `ops/` folder for cross-cutting), not a new domain. If it spans domains, it's work *in* them — don't mint a new one.

**2. Start minimal — one doc, the one it needs now.** Docs are recognized only when present, so don't scaffold all four. A feature starts as intent, so almost always:
- create `.gravity/<domain>/PLAN.md` (the what/next) — usually the only file on day one;
- add `SPEC.md` the moment an agent will *change* it and there are rules to not break;
- add `ARCHITECTURE.html` when "how it's built" outgrows the file map and a human needs the rationale;
- add the **MISSION row** once it's confirmed a durable domain (the why + guard).

**3. Wire the indexes (the cost of faceting is discoverability).** Adding a folder means updating, so it's never orphaned:
- `CLAUDE.md` **Doc Map** → add the folder line;
- `CLAUDE.md` **router table** → add the change→read-first row (once it has a `SPEC.md`);
- `.gravity/MISSION.html` → add the why/principle/non-goal row (once it's a real domain);
- `.gravity/IMPLEMENTATION_PLAN.md` **status spine** → add the `○/◑/✓` row;
- new `ARCHITECTURE.html` lede → back-pointer to its MISSION row.

**4. Lifecycle.** idea → `PLAN.md` (`○`) → building earns `SPEC`/`ARCH` (`◑`) → shipped (`✓`). Retiring a domain = fold its `PLAN` into a neighbor or archive it, then remove its rows from the four indexes above.

**Naming:** folder = the subject (kebab-case); files inside named by *kind* (`ARCHITECTURE.html` / `SPEC.md` / `PLAN.md`), with a slug suffix only when a kind repeats (`PLAN.improvement.md`).
