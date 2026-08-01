<!--
ROUTER.template.md — the project router, living INSIDE .gravity/ (gravity v3).
Copy to <project>/.gravity/ROUTER.md and fill every <…>. /adopt-gravity seeds it;
/new-domain and /new-spec wire new rows into it.

Why here and not the root CLAUDE.md: root harness files (CLAUDE.md, AGENTS.md, …)
are shared real estate gravity doesn't own — they carry only the 4-line fenced
pointer (GRAVITY.template.md). This file is the full map, one hop away, with zero
collision risk. Keep it a ROUTER, not a second architecture doc: it points at
where things live, it does not restate them. One concern, one home.
-->

# Router — where the docs live & what to read before a change

> Read `.gravity/GRAVITY.md` (the protocol card) first if you're new to `.gravity/` docs —
> it explains the doc kinds, their rates of change, and the navigation discipline.
> **Human, not an agent?** Open `.gravity/GRAVITY.html` instead — same protocol, written to be read
> in a browser, with diagrams and a phrasebook of what to ask an agent for.

## Doc Map (`.gravity/`)

Docs are grouped by **subject domain**, not by doc-type. A domain folder holds whichever of three kinds it needs — `ARCHITECTURE.html` (human deep-dive), `SPEC.md` (change contract), `PLAN.*.md` (what/next) — named by *kind* because the folder already names the subject. **Recognized only when present.**

```
.gravity/
  GRAVITY.md                # the protocol card — how to work these docs (versioned copy, never hand-edit)
  GRAVITY.html              # the same protocol for a HUMAN — browser-read guide + phrasebook (verbatim copy, travels with the card; + GRAVITY.ko.html 한국어판)
  ROUTER.md                 # this file — the map + read-first table
  MISSION.html              # why — north star (browser-read)
  ARCHITECTURE.html         # how — system overview (browser-read)
  IMPLEMENTATION_PLAN.md    # what/next — roadmap spine + per-domain status (+ optional Tracks)
  DESIGN.md                 # visual-token contract (UI projects only)
  _inbox/                   # THE DROP ZONE — put received files here; /given routes them out (README = the door sign; contents never committed)
  _lib/                     # the installed gravity instruments (machine-managed — never hand-edit; `_` = machinery, never a domain)
  _observatory/             # generated instrument output — git-ignored, never authored (regenerate, don't fix)
  _given/ + MANIFEST.md     # cross-cutting received knowledge (per-domain variant below)
  _roadmap/                 # the plan sheet (ROADMAP.md) + dated URD analyses (/urd) + the stakeholder engagement book (report-<slug>.html, /report); authored & committed, never a domain
  <domain>/   ARCHITECTURE.html · SPEC.md · PLAN.*.md   # one folder per subject; add lines as domains appear
  <domain>/_given/ + MANIFEST.md                         # received knowledge routed here by /given (provenance rows)
  integration/ SPEC.md · ARCHITECTURE.html · PLAN.*.md   # optional: cross-service/domain contracts only
  integration/structural/db/ + MANIFEST.md               # the DB evidence pack (DBA-exported metadata CSVs); read by .gravity/_lib/scan_db.py
```

**Handing in a file?** Drop it in `.gravity/_inbox/` and run `/given` — its README explains the door. DB metadata goes to `integration/structural/db/` (directly or via the inbox); its `MANIFEST.md` is the shopping list *and* the coverage record. An agreed requirements document (URD) enters the same way — run `/urd` to route it and write the plan sheet.

`SPEC.md` is the spec you hand an agent for a change — a Minimal Shape to build *from* + enforcement-tagged Rules that *fence* it (`[lint]`/`[type]`/`[test:name]`/`[review]`/`[—]`); `ARCHITECTURE.html` is the human reference behind it (load it rarely — it's styled HTML). `MISSION.html` owns *why*, `IMPLEMENTATION_PLAN.md` the roadmap spine + per-domain status, root `CONTEXT.md` *now*.

## What to read before a change (router)

Before touching a domain, load its `SPEC.md` — the compact change contract. The paired `ARCHITECTURE.html` is the human reference behind it (read only when you need the full rationale). A "—" means that kind doesn't exist for the domain yet.

| If you're changing… | Read first | Human reference |
|---|---|---|
| <what an agent might change in this domain> | `.gravity/<domain>/SPEC.md` | `.gravity/<domain>/ARCHITECTURE.html` |
| Cross-service API/auth/env/typegen/queue/webhook/data-flow contract | `.gravity/integration/SPEC.md`, then affected domain SPECs | `.gravity/integration/ARCHITECTURE.html` |
| <…> | `.gravity/<domain>/SPEC.md` | — |

## Adding a domain (start here for a new feature)

A **domain** is a durable subject area an agent will repeatedly navigate and change — not every feature is one. Mint a `.gravity/<domain>/` folder only when the feature has its own *gravity*; otherwise it's a slice under an existing domain. Domains have two legitimate axes, and **capability comes first**: vertical (business/capability) domains — the units of purpose a user scenario names — are the default diagnosis; horizontal (structural) domains (`data`, `security`, `ops`, …) earn folders only where a runtime owns real rules worth fencing. One-folder-per-service is the degenerate case — "it's a separate repo/deployable" is not a principle, and that topology already lives in `integration`'s Boundary Map. (`/new-domain <project> <domain>` does steps 2–3 for you.) The optional `integration` domain is reserved for contracts between services/domains: API/client type flow, auth/session behavior, ports/base URLs, shared env, queues/events, webhooks, database access boundaries, and required change order.

**1. Gate — is it a domain?** It earns a folder when it has its own *principle* and you can say yes to most of:
- rules an agent must respect to change it safely → wants a `SPEC.md`
- a "how it's built" a human needs beyond a file map → wants an `ARCHITECTURE.html`
- a multi-step arc, not a single PR → wants a `PLAN.*.md`
- a one-line *why* + non-goal that should win arguments → wants a MISSION row
- for `integration`: a cross-boundary contract that repeatedly affects more than one domain/service → wants an integration `SPEC.md`; otherwise keep it in `CONTRACT.md`

If not: it's a **`PLAN.*.md` under an existing domain** (or an `ops/` folder for cross-cutting), not a new domain. If it spans domains, it's work *in* them — a **Track** row in `IMPLEMENTATION_PLAN.md` plus one slice per touched domain, never a new folder.

**2. Start minimal — one doc, the one it needs now.** Docs are recognized only when present, so don't scaffold all four. A feature starts as intent, so almost always:
- create `.gravity/<domain>/PLAN.md` (the what/next) — usually the only file on day one;
- add `SPEC.md` the moment an agent will *change* it and there are rules to not break;
- add `ARCHITECTURE.html` when "how it's built" outgrows the file map and a human needs the rationale;
- add the **MISSION row** once it's confirmed a durable domain (the why + guard).

**3. Wire the indexes (the cost of faceting is discoverability).** Adding a folder means updating, so it's never orphaned:
- this file's **Doc Map** → add the folder line;
- this file's **router table** → add the change→read-first row (once it has a `SPEC.md`);
- `.gravity/MISSION.html` → add the why/principle/non-goal row (once it's a real domain);
- `.gravity/IMPLEMENTATION_PLAN.md` **status spine** → add the `○/◑/✓` row;
- new `ARCHITECTURE.html` lede → back-pointer to its MISSION row.

**4. Lifecycle.** idea → `PLAN.md` (`○`) → building earns `SPEC`/`ARCH` (`◑`) → shipped (`✓`). Retiring a domain = fold its `PLAN` into a neighbor or archive it, then remove its rows from the four indexes above.

**Naming:** folder = the subject (kebab-case; never a leading `_` — that sigil marks gravity machinery, not a domain); files inside named by *kind* (`ARCHITECTURE.html` / `SPEC.md` / `PLAN.md`), with a slug suffix only when a kind repeats (`PLAN.improvement.md`).
