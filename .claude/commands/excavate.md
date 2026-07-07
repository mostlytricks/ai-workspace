---
description: Survey an existing (brownfield) system and author its integration contract from code evidence — Boundary Map, structural dumps, domain proposal. Never guesses a seam; unknowns stay OPEN.
argument-hint: <project-or-alias>
---

You are running `/excavate` from `ai-workspace/` against project **`$ARGUMENTS`** — an **existing system you didn't author** (typically: one frontend + several backends + a database; Spring/JPA/MyBatis or similar). Greenfield gravity authors docs then code; brownfield inverts it: **archaeology before authorship**. This command is the archaeology — the brownfield twin of `/new-spec`: where `/new-spec` reads code to author one domain's contract, `/excavate` reads a whole codebase to author the **integration contract** and propose the domain map.

The honesty discipline is the same one everywhere in gravity, pointed at a legacy codebase: **every Boundary-Map row cites the file it came from; a seam you can't trace is written `OPEN:`, never guessed.** An uncited seam is this command's version of a fabricated wall.

## Step 0 — Locate & inventory (read before writing anything)

1. **Resolve the project** via `.claude/scripts/resolve_project.py` (tier junctions and external-path junctions both work). Not found → list candidates and stop.
2. **Check what docs exist**: root `CLAUDE.md` / `CONTEXT.md` / any `CONTRACT.md` / `GLOBAL_RULES.md` / `.gravity/`. Existing content is evidence — read it, never overwrite it. Also check for a **DB evidence pack** at `.gravity/integration/structural/db/` (see `templates/DB-EVIDENCE.template.md`) — its MANIFEST says what's `present` vs `OPEN:`.
3. **Detect the shape — monorepo or hub.** If the project is a **hub** (a docs-only repo whose `services/` folder holds independent service clones, each with its own `.git` — HANDBOOK "Many services, many repos"), the scan surface is `services/*/`; Boundary-Map citations use the `services/<name>/…` relative paths so they stay stable across machines. Never `git mv`/commit inside the service clones — the hub repo owns only the docs and evidence.
4. **Inventory the runnable parts**: build manifests (`pom.xml`, `build.gradle`, `package.json`, `Dockerfile`, `docker-compose.*`) → one row per runnable service (name, stack, likely port). This table is the skeleton everything else hangs on.

## Step 1 — Scan for seams (the evidence pass)

Collect four inventories, **each entry with its source file**:

| Inventory | What to scan | Evidence |
|---|---|---|
| **Endpoints** | `@RequestMapping`/`@Get..Mapping` (Spring), router/controller files (Node/Nest) | path + method → controller file |
| **DB access** | MyBatis `mapper.xml` (namespace + statement ids, `resultMap` → columns, table names in SQL) · JPA `@Entity`/`@Table`/`@Column` · repositories · raw SQL | table ↔ mapper-id / entity → the service methods that call them |
| **Frontend calls** | fetch/axios/api-client modules, generated clients | path + method → the components that import them |
| **Service ↔ service** | `RestTemplate`/`WebClient`/Feign base URLs, queue producers/consumers, webhook registrations, env vars carrying URLs/ports | from-service → to-service + transport |
| **DB evidence pack** *(when present)* | `structural/db/` CSVs: FK graph (`constraints.csv`), comments (`tables-columns.csv`), grants, source-in-DB, activity | table clusters + access boundaries → each row cites the CSV file |

Scan **code, never connect to the database**: live data-dictionary extraction needs credentials — the offline **DB evidence pack** is the sanctioned substitute (metadata CSVs a DBA exports; `DB-EVIDENCE.template.md` is the shopping list). Consume only what its MANIFEST marks `present`; everything else stays an `OPEN:` follow-up. When the code carries no readable queries (dynamic SQL, stored procedures, repos you can't see), the pack is where the DB half of the seams comes from — FK connectivity + name prefixes + shared grants/activity cluster the tables into candidate **vertical (business) domains**, with the CSV as the citation.

## Step 2 — Join on the three keys

Stitch the inventories into seams:

- **table name** — DB ↔ mapper/entity (which services own/touch which tables)
- **path + method** — frontend call ↔ backend endpoint
- **base URL / queue name** — backend ↔ backend

Whatever joins cleanly becomes a Boundary-Map row. Whatever doesn't becomes a **finding** (Step 4) — never force a join.

## Step 3 — Present, confirm, then write

Show the user the service inventory, the proposed Boundary Map, and the file list you intend to create. **Wait for confirmation** — this is someone's working system. Then write:

1. **Two-doc minimum if missing**: root `CLAUDE.md` (services table, ports, run commands — only what Step 0/1 evidenced) + `CONTEXT.md` (why gravity landed here; Next Step). Copy from `templates/`; fill only evidenced fields, leave the rest as the stencil's `<FILL>`.
2. **The protocol card** — creating `.gravity/` for the first time means embedding the project-side protocol so the repo is self-describing off-workspace: `cp templates/GRAVITY-PROTOCOL.template.md <project>/.gravity/GRAVITY.md`, delete the template's top comment block, and fill its `v<X.Y>` stamp with major.minor from the workspace root `VERSION` file (never invent a version; the card is a verbatim copy, never tailored).
3. **`.gravity/integration/SPEC.md`** from `SPEC.template.md`'s **integration variant**:
   - **Boundary Map** — one row per confirmed seam, each citing its source file.
   - **Ports / base URLs** table from the manifests.
   - **Change Order** — drafted from the discovered dependency direction (typically DB → mapper/entity → DTO → controller → client → component), explicitly marked *draft — confirm against how this team actually ships*.
   - Rules tagged honestly: almost everything starts `[review]` — there is no lint wall yet; **never** tag `[test:x]` unless the test exists.
4. **`.gravity/integration/structural/`** — the regenerable dumps: `endpoints.md`, `db-map.md`, `frontend-calls.md`, `service-links.md`. Header on each: *auto-extracted by /excavate on <date> — regenerable, never hand-edit; re-run /excavate after structural change.*
5. **`structural/db/MANIFEST.md`** — if no DB evidence pack exists, seed the manifest from `templates/DB-EVIDENCE.template.md` (all rows `OPEN:`) so the user leaves with the exact shopping list to hand a DBA instead of a bare `OPEN:` line. If a pack exists, update its status rows to match what you actually consumed.

## Step 4 — Findings & OPEN items (the honest remainder)

List explicitly, in the SPEC and the report:

- **Unmatched frontend calls** — dead endpoint, external consumer, or a service you haven't found?
- **Unreached tables** — dead schema, or written by a system outside this repo?
- **Untraceable dynamic SQL** (MyBatis `<if>`/`<choose>`, string-built queries) — name the file, mark `OPEN:`.
- **DB data-dictionary pass** — `OPEN:` until the DB evidence pack (or its missing items) is collected; point at `structural/db/MANIFEST.md`.

## Step 5 — Propose domains, report, stop

- **Propose** candidate `.gravity/<domain>/` folders from the discovered modules (one per service, or `web`/`api`/`data` for a modulith), each with its evidence. With a DB evidence pack present, also propose **vertical (business) domain candidates** from the table clusters (FK connectivity · name prefixes · shared grants/activity), each citing its CSVs — gated later by `/interview <project> <feature>` like any candidate. **Don't mint them** — the *is-it-a-domain* gate and `/new-domain` stay the user's move. Note: legacy modules enter the status spine as **✓ stable** (it's shipped, working software); a domain flips ◑ only when work lands on it.
- Report: service inventory, seam count (mapped vs OPEN), findings, and the suggested next step (usually: confirm the Change Order, then `/new-domain` the module you're about to change). **Do not commit.**

## What NOT to do

- **Never write a seam without a source citation** — an uncited Boundary-Map row poisons the contract from day one.
- **Never fill an unknown plausibly** — `OPEN:` is the honest state; the map's value is that every row is real.
- **Don't mint domain folders** — propose only; the gate is the user's.
- **Don't touch application code or the database** — excavation writes docs only, reads code only.
- **Don't overwrite existing docs** — an existing `CONTRACT.md`/`CLAUDE.md` is evidence to fold in (and link), not to replace.
- **Don't skip the Step-3 confirmation**, and **don't commit**.
