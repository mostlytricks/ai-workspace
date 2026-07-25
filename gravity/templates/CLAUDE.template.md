# <project name>

One-sentence description of what this project is and who it serves.

> **alias:** `<short-name>` — optional per-project short name; gravity tooling (`.claude/scripts/resolve_project.py`) resolves it so you can type it instead of the full folder name. Delete this line to fall back to the derived acronym (e.g. `architecture-memory-os` → `amos`).

---

## Docs in this project

<!-- A fresh agent opening here gets only the auto-loaded CLAUDE.md + CONTEXT.md; this map
     tells it what the *other* files are and which one wins on conflict. Delete the lines that
     don't apply — two-doc projects keep only CONTEXT.md + CLAUDE.md.
     Precedence: CONTEXT (now) > CLAUDE (how) > PLAN (next) > MISSION (why). -->

- **CONTEXT.md** — start here: current state + the single next step. *Now.*
- **CLAUDE.md** (this file) — stable identity: stack, run/test, entry points, gotchas. *How.*
- **IMPLEMENTATION_PLAN.md** — phases & locked decisions. *What's next* (may lag; CONTEXT wins on "now"). *(four-doc pipeline only)*
- **MISSION.html** — why it exists, principles, non-goals. *Why* (browser-read). *(four-doc pipeline only)*
- **ARCHITECTURE.html** — component boundaries, seams, data contracts (only if present; else "how it's built" stays in *Entry Points* below). *(optional fifth doc)*
- **`.gravity/<domain>/SPEC.md`** — compact, agent-loadable rule sheet for one domain; links up to its ARCHITECTURE facet; enforcement-tagged where possible (only if present). *The sheet you hand an agent for a change.* *(`.gravity/` projects; copy `SPEC.template.md`. The flat root `SPEC.<domain>.md` is the legacy pre-`.gravity` form.)*
- **`.gravity/<domain>/ARCHITECTURE.html`** — browser-read human deep-dive on one domain (only if present). *Full rationale a human engineer reads.* *(optional; §6 audience split)*
- **DESIGN.md** — running-app visual design system: type, token contract, motion, anti-patterns (only if present). *App style — distinct from any doc theme.* *(UI projects; copy `DESIGN.template.md`)*
- **RUNBOOK.md** — operations: where it runs, deploy steps, health checks, rollback (only if present). *The 2am doc.* *(deploying projects; copy `RUNBOOK.template.md`; `.gravity/` projects keep it at `.gravity/RUNBOOK.md`)*
- **`docs/walkthroughs/*.md`** — dated, append-only proof-of-work records for shipped slices (only if present). *(optional; CONTEXT.md "Completed" links here rather than restating)*

## Stack

- **Language / runtime:** e.g. Python 3.12, Node 20, JDK 21
- **Framework:** e.g. FastAPI, Next.js 14, Spring Boot 3
- **Key dependencies:** the 2-3 libraries that shape the architecture (DB driver, ORM, UI lib).
- **Datastore:** e.g. Postgres 16 (local Docker), Redis (optional).

## Run

```bash
# install
<command>

# start dev server / app
<command>
```

Default ports / URLs: e.g. `http://localhost:8000` (API), `http://localhost:5173` (UI).

## Test

```bash
<command>
```

Coverage expectations or "no tests yet" — be honest.

## Conventions

- Branch naming: e.g. `feat/<short-name>`, `fix/<short-name>`.
- Commit style: e.g. Conventional Commits, or "imperative one-liner, no body."
- Formatter / linter: e.g. `ruff`, `prettier`, run on save.
- Anything non-obvious about file layout, naming, or where to put new code.

<!-- OPTIONAL — Document Authoring. Keep this section ONLY if the project uses the audience split
     (a domain SPEC.md + ARCHITECTURE.html — workspace CLAUDE.md §6). It's the router: it tells an
     agent which compact SPEC to read before which kind of change, and which human deep-dive sits behind it.
     For projects on .gravity/ prefer the full router block from GRAVITY.template.md instead (Doc Map +
     read-first table). Delete the whole section for projects without SPEC files. -->
## Document Authoring

- Rules for `<domain>` live in `.gravity/<domain>/SPEC.md`; the full human-readable model is `.gravity/<domain>/ARCHITECTURE.html`. Read the SPEC before changing `<the thing this domain governs — parser, schema, ranking, auth boundary…>`.
- `<second domain>` rules live in `.gravity/<other-domain>/SPEC.md`.
- These rules are enforced by `<lint command, e.g. npm run lint:docs>` (see **Test**) — run it after authoring or convention changes. Drop this line if there's no linter yet.

## Constraints & Gotchas

- Environmental quirks: e.g. requires WSL, needs Docker running, specific Node version.
- Known sharp edges: e.g. "auth middleware is being rewritten, don't add new routes to the old one."
- External dependencies: API keys needed, services that must be running, rate limits to respect.

## Entry Points

- Main file(s) where new work usually starts.
- Where the route/controller layer lives.
- Where shared types/schemas live.

<!-- This is the lightweight architecture map and the default home for "how it's built".
     If the project grows an ARCHITECTURE.html (workspace CLAUDE.md §6), that file becomes the
     canonical "how it's built" — keep this section a pointer to it rather than duplicating boundaries. -->
- The architectural seam, if any: state the *mechanics* here (which file/type is the boundary) and link the *principle* to `MISSION.html` — don't restate it. One concern, one home.

## Git

- Remote: `<url>`
- Default branch: `main` / `master` / other

---

<!--
This file is stable identity — it changes rarely. For in-flight session state
(what was just done, what's broken, what's next), use CONTEXT.md.
-->
