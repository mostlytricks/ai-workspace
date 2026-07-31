# Kepler — the AI-workspace handbook

Human-facing guide for working in `ai-workspace/` — **Kepler** is the workspace manager (tiers, junctions, index, dashboard); **gravity** is the doc protocol projects adopt (`gravity/`). The agent's operating rules live in `CLAUDE.md` (loaded into every agent session); this file is for **you** — open it when you need a walkthrough, a slash-command lookup, or to clarify terminology.

---

## Quick start — "I want to..."

| I want to... | Use |
|---|---|
| Create a brand-new project | `/init-project <name>` ([Workflow 1](#workflow-1--create-a-brand-new-project) is the manual fallback) |
| Bring in a project that already lives elsewhere on disk | [Workflow 2](#workflow-2--bring-in-an-existing-project-from-elsewhere) |
| Ship a finished project to `stable/` | `/ship <name>` ([Workflow 3](#workflow-3--ship-a-project-active--stable) is the manual fallback) |
| Move a project between tiers | `mv <tier>/<name> <other-tier>/` (instant — see [storage model](#storage-model)) |
| See status across all projects | `/triage` |
| Re-orient on one project — what's it for, what should I ask? | `/mission <name>` |
| Give a long-lived project a "why" doc and a phase roadmap | [Adopt the full doc pipeline](#adopt-the-full-doc-pipeline) |
| Move a doc-heavy project's docs into a `.gravity/` directory | `/adopt-gravity <name>` ([Adopt the `.gravity/` doc system](#adopt-the-gravity-doc-system)) |
| Add a new domain to a `.gravity/` project | `/new-domain <name> <domain>` |
| Land on an existing legacy system (f/e + b/e's + DB) | `/excavate <name>` ([Adopt gravity on an existing (brownfield) system](#adopt-gravity-on-an-existing-brownfield-system)) |
| Bring a project up to the current gravity version | `/sync-gravity <name>` ([Upgrade a project to a newer gravity](#upgrade-a-project-to-a-newer-gravity)) |
| Triage a batch of user bug reports into the docs | `/intake <name>` ([Manage a user bug/issue batch](#manage-a-user-bugissue-batch-intake--patch)) |
| Feed domain knowledge / production-data docs to a project | drop in `.gravity/_inbox/`, then `/given <name>` |
| Set the workspace up on a new machine, or repair broken junctions | `python .claude/scripts/bootstrap.py` ([Set up on a new machine](#set-up-on-a-new-machine)) |
| Update a sibling Kepler workspace on another drive | `/deploy-kepler <path>` ([Propagate Kepler](#propagate-kepler-to-a-sibling-workspace)) |
| Know what exists right now | Read `PROJECTS.md` |

---

## Slash commands

Run from the `ai-workspace/` root in Claude Code. One line each — **the full procedure lives in `.claude/commands/<name>.md`** (the one home; read that file to know exactly what a command does). None of them commit or push for you.

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a new project end-to-end: `repos/` folder, junction, templates, `git init`, index row. |
| `/ship <name>` | active → stable when a release shipped: evidence check, Next Step → reactivation trigger, junction + index move. |
| `/triage` | Weekly survey: stale/stencil/bloat flags + the mechanical checkers → one-page drift report. Read-only. |
| `/mission <name>` | Re-orient on one project: what it's for, where it stands, what to ask next. Read-only. |
| `/interview <name> [<feature>]` | `/mission` in reverse — interviews *you* to fill the docs, strawman-first; with `<feature>`, the feature-intake ritual (domain gate + `given/when/then` scenario). |
| `/adopt-gravity <name>` | Retrofit `.gravity/`: relocate docs by domain, seed router + protocol card + lib, wire the four indexes. Confirms before touching disk. |
| `/sync-gravity <name>` | Upgrade to current gravity: re-copy card + lib, bump stamps; judgment deltas reported as a checklist, never auto-migrated. |
| `/new-domain <name> <domain>` | Mint one domain: is-it-a-domain gate, folder + starter PLAN, all four indexes wired. |
| `/new-spec <name> <domain>` | Author a domain SPEC: Minimal Shape + Rules tagged only from evidence; runs the gate to prove it. |
| `/intake <name>` | Triage a bug-report batch into a dated verbatim sheet → root causes → slice PLANs + queue rows. Reported claims only; no repro, no slice. |
| `/given <name>` | Route `.gravity/_inbox/` into the given layer: one routing table, provenance manifests, inbox ends empty. |
| `/patch-slice <name> [slug]` | Land one slice under the patch-loop walls: anchor → bare-gated verify (N=3) → proven rollback. Merge/push stays yours. |
| `/cut-release [name]` | One release Change Order (no arg = gravity itself): confirmed bump from `[Unreleased]`, green gate required, stops before push. |
| `/retire <name>` | End of life: read-only risk card, then **archive** (reversible) or **delete** (permanent). |
| `/dashboard` · `/open-dashboard` | Status across tiers: terminal report · regenerate + open the HTML dashboard in the browser. |
| `/excavate <name>` | Brownfield survey from code evidence → cited Boundary Map + structural dumps; unknowns stay `OPEN:`, never touches the DB. |
| `/observatory <name> [theme]` | One project, one page: seven tabs (Overview+drift+tracks · Queue · Seams · Spec Health · Graduation · Timeline · Orbit 3D) rendered into `<project>/.gravity/_observatory/` — generated, git-ignored, and self-renderable off-workspace (`python .gravity/_lib/generate_observatory.py`). |
| `/preflight <name> <domain>` | The agent-side twin: a domain's pre-change packet — ordered read-first list, runnable gate, honest warnings. Pointer-first. |
| `/open-mission [name]` · `/open-architecture [name] [facet]` | Open the authored HTML docs in the browser; locate + launch, never regenerate. |

---

## The four-doc pipeline (optional)

Every project carries two files: `CLAUDE.md` (stable identity) and `CONTEXT.md` (rolling now). A project with a real arc — multi-phase, long-lived, the kind you keep losing the thread on — can add two more, so that **four docs change at four different rates**:

| Doc | Answers | Changes | Why this format |
|---|---|---|---|
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML — a stable thing you *read* in a browser; theme generated by `gravity/lib/doc_theme.py` |
| `CLAUDE.md` | **How** — identity, stack, constraints | on refactors | Markdown — auto-loads into the agent |
| `IMPLEMENTATION_PLAN.md` | **What/next** — phases, locked decisions, the gate | per phase | Markdown — the agent edits it, so clean diffs win |
| `CONTEXT.md` | **Now** — state + the one next step | per session | Markdown — auto-loads into the agent |

It's **opt-in**. Most projects don't need it; the overhead only pays off when the mission keeps slipping out of view. `/mission` reads these four to re-orient you; `/triage` flags when they contradict each other. The binding rule is **one concern, one home** — each concern has one canonical owner-doc, others link rather than restate (the ownership table is workspace `CLAUDE.md` §6). When "how it's built" outgrows CLAUDE.md's Entry Points, the optional fifth doc `ARCHITECTURE.html` takes it (see the glossary entry for the map/trace split).

---

## Storage model

```
ai-workspace/
├── repos/                  ← real files (.git, .venv, node_modules) live here
│   ├── my-api/
│   ├── agent-ui/
│   └── ...
│
├── active/
│   └── my-api    ─→ junction → repos/my-api
├── stable/
│   └── shipped-s ─→ junction → repos/shipped-s
├── dormant/
│   └── old-x     ─→ junction → repos/old-x
└── archive/
    └── done-y    ─→ junction → repos/done-y
```

Tier folders are **views**, not storage. A project's tier = which junction folder it appears in. Moving between tiers (`mv active/x dormant/`) renames a ~1KB pointer — instant, never touches `node_modules` or `.venv`.

The lifecycle reads: **active** = being worked · **stable** = works (shipped, in use, staleness-exempt) · **dormant** = paused on a blocker · **archive** = over. (The old real-folder `incubator/` tier was retired in v2.0 — `/init-project` made scaffolding cheap enough that experiments start in `active/` and dead ones get `/retire`d.)

---

## Decision: where should a project's real files live?

```
Is the project already at a real path I can't (or don't want to) change?
├── No  → repos/<name>/        ← default. Workflow 1 or 3.
└── Yes → keep external path   ← Workflow 2b (junction in place)
```

Keep the external path when:
- IDE workspace files reference it (`.code-workspace`, JetBrains `.idea/`)
- CI runners or build scripts hardcode the path
- The project lives on a different drive

Otherwise prefer `repos/`. Same-drive `mv` is metadata-only and instant, so bringing in an existing same-drive project (Workflow 2a) is cheap.

---

## Workflow 1 — Create a brand-new project

**Easy way:** `/init-project <name>` from the workspace root. Done.

**Manual way:**

1. Pick a `<name>` (kebab-case, no spaces).
2. Create the real folder under `repos/`.
3. Junction it into `active/`.
4. Copy both templates into the project.
5. `cd` into it and `git init`.
6. Add a row to `PROJECTS.md` under `## active/`.

**PowerShell:**
```powershell
$name = "<name>"
New-Item -ItemType Directory -Path "repos\$name" | Out-Null
New-Item -ItemType Junction   -Path "active\$name" -Target "repos\$name" | Out-Null
Copy-Item templates\CLAUDE.template.md  "repos\$name\CLAUDE.md"
Copy-Item templates\CONTEXT.template.md "repos\$name\CONTEXT.md"
Set-Location "active\$name"
git init
```

**Bash (Git Bash on Windows):**
```bash
name="<name>"
mkdir -p "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
cp gravity/templates/CLAUDE.template.md  "repos/$name/CLAUDE.md"
cp gravity/templates/CONTEXT.template.md "repos/$name/CONTEXT.md"
cd "active/$name"
git init
```

After scaffolding: edit `CLAUDE.md` (stack, run/test commands, conventions), `CONTEXT.md` (initial Next Step), and `PROJECTS.md`.

---

## Workflow 2 — Bring in an existing project from elsewhere

The project already exists at some path on disk. Two sub-flows — pick using the [decision tree above](#decision-where-should-a-projects-real-files-live).

### 2a — Move into `repos/`, then junction

1. Purge build artifacts at the source (`node_modules`, `.venv`, `target`, `build`).
2. `mv` the project folder into `repos/<name>/`.
3. Junction it into `active/<name>`.
4. Add `CLAUDE.md` and `CONTEXT.md` if missing — **don't overwrite** existing files.
5. Reinstall dependencies inside the project.
6. Add a row to `PROJECTS.md`.

**PowerShell:**
```powershell
$src  = "C:\path\to\old-thing"
$name = "old-thing"
Remove-Item -Recurse -Force "$src\node_modules","$src\.venv","$src\target","$src\build" -ErrorAction SilentlyContinue
Move-Item   $src "repos\$name"
New-Item    -ItemType Junction -Path "active\$name" -Target "repos\$name" | Out-Null
if (-not (Test-Path "repos\$name\CLAUDE.md"))  { Copy-Item templates\CLAUDE.template.md  "repos\$name\CLAUDE.md" }
if (-not (Test-Path "repos\$name\CONTEXT.md")) { Copy-Item templates\CONTEXT.template.md "repos\$name\CONTEXT.md" }
Set-Location "active\$name"
# reinstall deps, then edit ../../PROJECTS.md
```

**Bash:**
```bash
src="C:/path/to/old-thing"
name="old-thing"
rm -rf "$src/node_modules" "$src/.venv" "$src/target" "$src/build"
mv "$src" "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
[ -f "repos/$name/CLAUDE.md" ]  || cp gravity/templates/CLAUDE.template.md  "repos/$name/CLAUDE.md"
[ -f "repos/$name/CONTEXT.md" ] || cp gravity/templates/CONTEXT.template.md "repos/$name/CONTEXT.md"
cd "active/$name"
# reinstall deps, then edit ../../PROJECTS.md
```

### 2b — Junction in place (leave the project where it lives)

1. Junction the external path directly into `active/<name>` (skip `repos/`).
2. Add `CLAUDE.md` and `CONTEXT.md` at the external path if missing.
3. Add a `PROJECTS.md` row; mark the row as **external** so future-you remembers where the real files are.

**PowerShell:**
```powershell
$src  = "C:\path\to\old-thing"
$name = "old-thing"
New-Item -ItemType Junction -Path "active\$name" -Target $src | Out-Null
if (-not (Test-Path "$src\CLAUDE.md"))  { Copy-Item templates\CLAUDE.template.md  "$src\CLAUDE.md" }
if (-not (Test-Path "$src\CONTEXT.md")) { Copy-Item templates\CONTEXT.template.md "$src\CONTEXT.md" }
```

**Bash:**
```bash
src="C:/path/to/old-thing"
name="old-thing"
python .claude/scripts/link_project.py "active/$name" "$src"   # junction (Win) / symlink (POSIX)
[ -f "$src/CLAUDE.md" ]  || cp gravity/templates/CLAUDE.template.md  "$src/CLAUDE.md"
[ -f "$src/CONTEXT.md" ] || cp gravity/templates/CONTEXT.template.md "$src/CONTEXT.md"
```

---

## Workflow 3 — Ship a project (active → stable)

For a project that **shipped well**: it's in real use, a release is cut, and there's no in-flight next step. Stable is the "it works, stop nagging me" tier — staleness rules don't apply there, because silence is success.

**Easy way:** `/ship <name>` from the workspace root. It verifies release evidence (git tag or CHANGELOG version), rewrites the CONTEXT.md Next Step into a reactivation trigger, moves the junction, and updates `PROJECTS.md`. Done.

**Manual way:**

1. Check the entry gate honestly: is a release cut (tag/CHANGELOG) or is the thing demonstrably in use? Is there really nothing in flight? (Something *blocking* progress → that's `dormant/`, not `stable/`.)
2. Rewrite `CONTEXT.md`'s Next Step into the **reactivation trigger** — one line: *"Reactivate when X"*.
3. `mv active/<name> stable/` (instant; it's a junction).
4. Move the project's row to the `## stable/` section of `PROJECTS.md` and rewrite its focus column into the steady state + trigger.

**Bash:**
```bash
name="<name>"
mv "active/$name" "stable/$name"
# then edit stable/$name/CONTEXT.md (Next Step → reactivation trigger) and PROJECTS.md
```

**Reactivate (stable → active):** when the trigger fires, `mv stable/<name> active/`, refresh `CONTEXT.md` with the new arc's Next Step, and move the `PROJECTS.md` row back. No command needed — reactivation always comes with fresh intent that only you can write.

---

## Manage a user bug/issue batch (intake → patch)

Bugs are **not a domain** — never mint `.gravity/bugs/` or a standing BUGS.md. A batch flows through two commands:

1. **`/intake <name>`** — reports land verbatim in a dated sheet (`docs/intake/<date>.md`), each item carries six facts (gaps elicited or `OPEN:` — **no repro, no slice**), root causes dedupe into one slice PLAN each + queue rows.
2. **`/patch-slice <name> <slug>`** — one slice at a time, `now` first. The batch closes when every intake row's `→` line points somewhere: a PLAN, a rejection with a reason, or an `OPEN` naming what's awaited.

The compounding effect is the point: every fixed bug leaves the regression test that graduates its scenario into the SPEC's Behavioral Contract, so bug season *hardens* the SPEC instead of just draining time. Meta-signal: a domain that eats most bugs batch after batch is under-fenced (tag census mostly `[review]`) — schedule a `/new-spec` pass, not more patches.

---

## Adopt the full doc pipeline

When a project has grown a real arc and you keep re-deriving "what was this for again?", give it the two extra docs (see [the four-doc pipeline](#the-four-doc-pipeline-optional)). Worth it when the project is multi-phase, long-lived, and `active/`; skip for one-shots and anything stable, dormant, or archived.

1. Copy the two templates into the project (don't overwrite if they somehow exist):

   **Bash:**
   ```bash
   name="<name>"
   [ -f "repos/$name/MISSION.html" ]             || cp gravity/templates/MISSION.template.html             "repos/$name/MISSION.html"
   [ -f "repos/$name/IMPLEMENTATION_PLAN.md" ]   || cp gravity/templates/IMPLEMENTATION_PLAN.template.md   "repos/$name/IMPLEMENTATION_PLAN.md"
   ```

   **PowerShell:**
   ```powershell
   $name = "<name>"
   if (-not (Test-Path "repos\$name\MISSION.html"))           { Copy-Item templates\MISSION.template.html           "repos\$name\MISSION.html" }
   if (-not (Test-Path "repos\$name\IMPLEMENTATION_PLAN.md")) { Copy-Item templates\IMPLEMENTATION_PLAN.template.md "repos\$name\IMPLEMENTATION_PLAN.md" }
   ```

2. **Fill `MISSION.html` first** (the why) — open it in a browser as you go. The `.lede` line matters most: `/dashboard` and `/mission` read it verbatim. Nail the **Current Non-Goals** section — that's what keeps an agent on-mission and what `/triage` checks recent work against.
3. **Then `IMPLEMENTATION_PLAN.md`** (the what/next) — list the phases done/next/todo, the locked decisions, and the gate (the exact commands a phase must pass). Move the multi-phase arc *out* of `CONTEXT.md` and into here; leave `CONTEXT.md` holding only *now*.
4. Run `/mission <name>` to sanity-check it reads well and produces useful questions.
5. The `MISSION.html` styling comes preloaded from the theme; if you hand-roll other HTML docs, generate the block with `python gravity/lib/doc_theme.py` (guide: `gravity/DESIGN.docs.md`).

> Or just ask the agent: *"adopt the full doc pipeline for `<name>`"* — it'll copy the templates and help you fill them.

---

## Adopt the `.gravity/` doc system

Once a project grows several architecture/spec/plan docs across multiple domains, the root gets crowded and the two auto-loaders get buried. The `.gravity/` system relocates every heavy doc into a `.gravity/` directory **organized by subject domain**, leaving only `CLAUDE.md` + `CONTEXT.md` + `README.md` at the root; the root harness files carry only gravity's 4-line fenced pointer block, and the map lives at `.gravity/ROUTER.md`. Opt-in, recognized only when present; CLIs/scripts/libraries never need it. `knowledge-viewer` is the worked example. **The protocol itself — doc kinds, navigation, SPEC anatomy, the never-do list — is the card** (`.gravity/GRAVITY.md`, seeded at adoption): that's the file to read, project-side or here (`gravity/GRAVITY-PROTOCOL.md`).

- **Retrofit an existing project** — `/adopt-gravity <name>`: proposes a before→after move table (*you confirm the boundaries*), `git mv`s docs into domain folders, seeds router + card + lib, wires the four indexes.
- **Add a domain later** — `/new-domain <name> <domain>`: runs the *is-it-a-domain?* gate first (most features are a `PLAN.*.md` slice, not a folder), then wires all four indexes.
- **Add an integration layer** — the normal domain flow with the reserved name `integration`, for contracts *between* services/domains. Keep small facts in `CONTRACT.md`; promote when agents repeatedly cross boundaries.

> Or just ask the agent: *"move `<name>` onto the `.gravity/` doc system"* / *"add a `<domain>` domain to `<name>`"*.

---

## Adopt gravity on an existing (brownfield) system

Everything above assumes you're *authoring* a project. Landing on a **mature system you didn't write** — one frontend, several backends, a database, MyBatis `mapper.xml` or JPA in the middle — inverts the flow: **archaeology before authorship**. Same gravity containers, opposite fill order. The one structural difference: the **`integration` domain comes first, not last** — on brownfield, the seams are exactly what you don't know and what will hurt you.

The intake order:

1. **Two-doc minimum, day one (~30 min).** Root `CLAUDE.md` = what you learn getting it running: the services table, ports, run commands, where each part lives. `CONTEXT.md` = why you're here + the single next step. Nothing else yet.
2. **`.gravity/integration/SPEC.md` seeded early, filled as you dig.** Use `SPEC.template.md`'s integration variant. The **Boundary Map** gets one row per seam you *confirm* (web → api, api → api, api → DB via mapper/JPA) — **every row cites the file it came from; a seam you can't trace is an `OPEN:` line, never a guess.** The **Change Order** records the edit sequence you reverse-engineer (typically DB → mapper/entity → DTO → controller → client → component) — mark it *draft* until you've shipped through it once.
3. **Join the tiers on three keys**: **table name** (DB ↔ mapper/entity), **path + method** (frontend call ↔ controller), **base URL / queue name** (backend ↔ backend). What doesn't join is a *finding* — a dead endpoint, an unreached table, an external consumer — and belongs in the report, not the map.
4. **Structural dumps are regenerable.** Extracted inventories (endpoint→service→mapper→table chains, component→endpoint calls) live in `.gravity/integration/structural/` with a "never hand-edit, re-extract" header — the same discipline as generated code.
5. **Domains are discovered, not invented.** Mint `.gravity/<domain>/` folders from the system's real modules (one per service, or `web`/`api`/`data`), via `/new-domain` and its gate. Legacy modules enter the status spine as **✓ stable** — it's shipped, working software; a domain flips ◑ only when your work lands on it.
6. **Verified semantics only with citations.** Glossary entries for cryptic columns and coded values, business rules — each fact names the endpoint/table/column it came from.

**`/excavate <name>` automates steps 1–4**: it scans the code (never the DB), presents the inventory for confirmation, then writes the two-doc minimum, the cited Boundary Map, and the structural dumps — leaving the un-traceable honestly `OPEN:`.

### The DB evidence pack — when the code doesn't carry the queries

Some systems defeat code archaeology on the DB side: dynamic/string-built SQL, logic in stored procedures, a shared database touched by repos you can't see. The missing evidence comes from the database's own **metadata**, collected **offline** as flat files by a read-only account — the agent never needs DB access, and **no row data is exported** (structure, comments, constraints, grants, activity stats only — no PII).

**`gravity/templates/DB-EVIDENCE.template.md`** is both the shopping list you hand a DBA (exact Oracle queries per item, `information_schema` equivalents noted) and the pack's **manifest**. Everything lands in one place:

```
<project>/.gravity/integration/structural/db/
  MANIFEST.md          # the checklist — each item `present (<date>)` or `OPEN:`
  ddl/*.sql            # P1 — CREATE TABLE scripts you scraped yourself (no DBA needed)
  tables-columns.csv   # P1 — inventory + comments (the semantics)
  constraints.csv      # P1 — PK/FK/UK: the entity graph
  db-source.sql        # P2 — procedures/views/triggers (queries living in the DB)
  grants.csv           # P2 — which account/service can touch which tables
  rowcounts.csv        # P2 — live vs dead tables
  activity.csv         # P3 — actually-executed SQL (DBA-assisted)
  docs/                # human artifacts (ERD, table-definition sheets) — claims to verify
```

**Can't get a DBA? Scrap the DDL yourself** — `CREATE TABLE` scripts from SQL Developer / DBeaver (*export DDL*) or the repo's migrations are a full graph source (`ddl/*.sql`); the tool states the caveat (scripts can drift from the deployed schema, coverage = what you scraped) and, when the dictionary CSVs later arrive, reports script-vs-database disagreements as drift instead of merging them. And to kill the recurring worry: **no row data, ever** — the CSVs are the database's own catalog of your tables (the data dictionary), not table contents.

**Partial is fine by design** — collect P1 today and start; every absent item is an `OPEN:` row in the MANIFEST, never a blocker. The moment anything lands, **run the instrument**: `python .gravity/_lib/scan_db.py` (it travels with the lib) parses the pack, builds the FK graph, proposes candidate *vertical business domains* (naming prefix vs grant signature vs FK community — winner picked by modularity, scores printed), and names the **candidate seams**: FK edges that leave their cluster, cross-schema flagged. Its two laws: an absent file reports `unknown`, never `0`, and every confidence names the signals it used. `/excavate` runs it and carries the candidates into the domain proposal; when no pack exists at all, it seeds the empty MANIFEST so you leave with the shopping list. Don't have the pack yet? Drop whatever the DBA sends into `.gravity/_inbox/` — `/given` routes pack-shaped files here and flips the MANIFEST rows.

**What the manifest buys** (worth saying to whoever asks why it exists): it stops the analysis from claiming coverage it doesn't have. "Clustered from `constraints.csv`" can be audited against whether that row says `present`; without the manifest, "we analyzed the DB" sounds equally confident whether it saw six files or one.

### Many services, many repos — the hub project

When one system is spread across **many service repositories**, the cross-service gravity (the integration domain, the Boundary Map, the DB evidence pack) has no single repo to live in. The answer reuses the workspace's own root pattern: a **hub project** — a docs-only repo that tracks the system-level gravity while the service clones live *inside it, git-denied* (the same deny-all/whitelist trick `ai-workspace/.gitignore` uses on `repos/`):

```
repos/<system>/                # THE workspace project = the hub (its own git repo)
  CLAUDE.md · CONTEXT.md · README.md    # router: the services table names each repo + where it lives
  .gitignore                   # deny services/ — the hub commits docs + evidence ONLY
  .gravity/
    GRAVITY.md                 # protocol card
    integration/
      SPEC.md                  # Boundary Map + Change Order across ALL services
      structural/              # code-scan dumps + db/ evidence pack (above)
  services/                    # NOT tracked by the hub — each a full independent clone
    <service-a>/               #   own .git, own remote
    <service-b>/
```

Why this shape: `/excavate` gets one scan surface (`services/*/`) and the Boundary-Map citations use stable relative paths (`services/order-api/src/…`) that survive any machine; the hub repo stays a legal gravity project (it commits only what it owns — docs and evidence — so it is **not** the forbidden umbrella repo: service code is never committed, never submoduled). Each service repo keeps its own two-doc minimum (and optionally its own `.gravity/`) independently; the hub's `CLAUDE.md` services table is the router between them. One-or-two-service projects don't need this — a single repo with `.gravity/integration/` stays the simpler correct shape.

---

## Upgrade a project to a newer gravity

Gravity itself is versioned (`VERSION` + `CHANGELOG.md` + git tag), and each adopted project pins the version it was built on in **three stamps**: the `> gravity: vX.Y` stamp in its fenced router block (root `CLAUDE.md`/`AGENTS.md`), and — for `.gravity/` projects — the `gravity protocol · vX.Y` stamp in the embedded card (`.gravity/GRAVITY.md`) plus the plain version in `.gravity/_lib/VERSION` (`LIB_STALE` when it trails the distribution). When gravity cuts a new release, projects don't upgrade themselves; they drift, visibly: `/triage` flags stale cards (📡), and the `PROJECTS.md` **Gravity adoption** table shows who's on what.

**Run `/sync-gravity <name>`** to bring one project current. It does the two layers differently on purpose:

- **Mechanical (applied for you):** re-copies the protocol card fresh from the template (it's a verbatim copy by contract — never hand-merged), re-installs `.gravity/_lib/` (`install_lib.py` — same verbatim contract, so upgrading means re-copying, never patching), bumps both stamps to the current `VERSION`, verifies with `check.py consistency`, and reconciles the adoption-table row. For a pre-v4 project it first offers `python .claude/scripts/migrate_gravity_v4.py <name>` (dry-run by default) — the one convention change with a dedicated migrator, because a directory rename carries no judgment; run before anything else touches the tree, it subsumes the whole mechanical layer.
- **Judgment (reported, never auto-applied):** it reads every `CHANGELOG.md` section between the project's old stamp and now, and hands you a checklist of convention changes the project might violate — quoted from the changelog, one line each. Restructuring to satisfy a new convention is its own task; a sync never does it as a side effect.

A minor-only delta usually means an empty checklist — re-copy, bump, done. It never commits (except the v4 migrator, which commits its own rename by design); the diff is your review checkpoint. (Manual fallback: **first**, on a pre-v4 project, `python .claude/scripts/migrate_gravity_v4.py <name>` from a clean worktree — running `install_lib.py` before it deletes the old `lib/` and strands the other machinery dirs half-migrated; then `cp gravity/GRAVITY-PROTOCOL.md <project>/.gravity/GRAVITY.md`, fill the stamp from `VERSION`, `python .claude/scripts/install_lib.py <name>`, edit the router's stamp line, run `/triage`.)

---

## Set up on a new machine

The root repo tracks only the **skeleton** — the meta files, `gravity/`, and `.claude/` tooling. Every tier folder is denied and `PROJECTS.md` is git-ignored (it names private work), which is exactly the "no umbrella repo" boundary. The consequence: a fresh clone has the rules and the instruments but no `repos/`, no tiers, no index, and no junctions.

```bash
git clone https://github.com/mostlytricks/ai-workspace.git
cd ai-workspace
python .claude/scripts/bootstrap.py          # --dry-run to preview
```

That creates `repos/` + the four tier folders and seeds `PROJECTS.md` from `PROJECTS.sample.md`. Then clone your projects into `repos/`, add their rows to `PROJECTS.md`, and **run it again** — it links each one into the tier its row names (junction on Windows, relative symlink on POSIX, both through `link_project.py`).

The same command is the fix for **broken links** on an established machine: it removes and re-makes any junction that dangles, and reports what it verified. It's safe to re-run any time; on a healthy workspace it reports "all present / 0 made".

Three things it deliberately refuses:

- **It never guesses a tier.** A folder in `repos/` with no `PROJECTS.md` row is listed under *"NOT filed"*, not filed somewhere plausible — an index that contains a guess is an index you can't trust.
- **It never clones.** Remotes live in each project's own `.git/config`; a manifest of them would name private repos, so exporting one has to be a deliberate act.
- **It never edits an existing `PROJECTS.md`.** The index is the source of truth for tiers, so bootstrap reads it and only seeds it when there is none.

## Propagate Kepler to a sibling workspace

For **several Kepler workspaces on one machine** (per-purpose, on different drives) that were created as plain copies rather than clones: `/deploy-kepler <target-path>` (script: `.claude/scripts/deploy_kepler.py`). It updates a sibling's *skeleton* from this workspace's HEAD — never its projects, never its private state.

```bash
python .claude/scripts/deploy_kepler.py D:/work-workspace              # dry-run report
python .claude/scripts/deploy_kepler.py D:/work-workspace --apply     # do it
```

How it stays safe, mechanically:

- **The manifest is `git ls-files`** — the `.gitignore` whitelist made executable. `.claude/settings.json`, `PROJECTS.md`, `repos/`, and the tiers are outside it **by construction**; there is no exclusion list to forget.
- **Kepler's version is the skeleton commit** (hash + date — the manager has no SemVer by design, §2). A `.kepler-deployed` stamp in the target records what was last shipped, so the report can tell a **safe update** (target untouched since last deploy) from a **local modification** (the sibling's owner edited it — kept unless `--force`) and an **orphan** (source stopped shipping it — kept unless `--prune`).
- **Dry-run is the default**; it refuses a dirty source (deploys must be reproducible from a commit) and a target that overlaps this tree. On a **first deploy** there is no stamp, so every difference honestly reads *local-modified* — eyeball the list once, then `--force`.

Gravity is deliberately not this command's job: after a deploy, run `/sync-gravity` per project **in that workspace**, and its `bootstrap.py` only if tiers/junctions there are broken.

---

## Glossary

- **Junction** — Windows directory pointer (`mklink /J`). Same-volume only; no admin or Developer Mode. Used throughout the tier folders. **Always create one via `.claude/scripts/link_project.py <link> <target>`** or PowerShell `New-Item -ItemType Junction` — never the Git-Bash `cmd //c "mklink …"` form, whose MSYS quoting silently eats the `$name` variable.
- **Symbolic link (symlink)** — `mklink /D` on Windows; `ln -s` on POSIX. On Windows requires admin or Developer Mode. Crosses volumes; has full POSIX semantics under WSL. Use only when junctions aren't enough.
- **Tier** — one of `active/`, `stable/`, `dormant/`, `archive/`. A project's tier = which tier folder its junction lives in. The lifecycle reads *being worked · works · paused · over*.
- **Reactivation trigger** — the one-line Next Step a `stable/` project's CONTEXT.md must carry: *"Reactivate when X."* The mirror of dormant's resume blocker — but nothing is blocked; the project simply works and is waiting for a reason to change.
- **View vs storage** — `repos/` is **storage** (real files). Tier folders are **views** (junctions). Moving a project between views doesn't touch storage.
- **Repo vs project** — used interchangeably here. Each project under `repos/` is its own independent git repository with its own remote.
- **Root** — the `ai-workspace/` directory itself. Its repo versions only the **skeleton** (deny-all/whitelist `.gitignore`); tier folders, projects, and `PROJECTS.md` are never tracked here — that would be the forbidden umbrella repo.
- **Workspace-level `CLAUDE.md`** — the agent operating manual at the workspace root. Auto-loaded every agent session. Contains rules and invariants only.
- **Project-level `CLAUDE.md`** — per-project stable identity file (`repos/<name>/CLAUDE.md`). Stack, run commands, conventions. Auto-loaded when an agent opens at that project.
- **`CONTEXT.md`** — per-project mutable handoff file: Completed / Current State / Next Step, updated every session. A **rolling snapshot of now, not a log**; git history is the changelog, so pruning loses nothing.
- **`MISSION.html`** — optional per-project "why" doc: north star, principles, non-goals. The slowest-changing of the four docs; browser-read. Part of the [four-doc pipeline](#the-four-doc-pipeline-optional).
- **`IMPLEMENTATION_PLAN.md`** — optional "what/next" doc: phase roadmap or slice queue, locked decisions, the gate, optional **Tracks** (the direction axis). The multi-phase arc lives here; `CONTEXT.md` holds only *now*.
- **Work layers (slice · phase · spine · track)** — the **slice** is the only unit of work; phases/queue (time), the status spine (domain), and tracks (direction) are *indexes over slices* and hold no work themselves. Full statement in `IMPLEMENTATION_PLAN.template.md`.
- **Chore** — maintenance work with no principle of its own; **never a domain**. Done now → no doc; deferred → one dated `○` queue row (the **comet clock** — `SLICE_STALE` flags it past 30 days); recurring → graduate to a wall. Full ruling in the protocol card.
- **Four-doc pipeline** — the optional `MISSION.html` + `CLAUDE.md` + `IMPLEMENTATION_PLAN.md` + `CONTEXT.md` set, ordered by rate of change (rarely → per-session). Opt-in for ambitious `active/` projects.
- **`ARCHITECTURE.html`** — optional *fifth* doc, split by question: the system page is the **map** (Domain × Layer grid + flows), a domain page is the **trace** (one row expanded down the layers). `data-path` anchors checked by `check.py arch`. Recognized when present, never mandated.
- **`.gravity/`** — optional per-project directory holding the heavy docs (everything but root `CLAUDE.md` + `CONTEXT.md` + `README.md`), grouped by subject domain; the directory **is** the domain registry. Adopt with `/adopt-gravity`, extend with `/new-domain`; `knowledge-viewer` is the worked example. The protocol's full statement is the card.
- **Protocol card (`.gravity/GRAVITY.md`)** — the canonical project-side protocol, copied verbatim from `gravity/GRAVITY-PROTOCOL.md` and version-stamped; never hand-edited (upgrade = re-copy). Makes each repo self-describing off-workspace. `/triage` flags a missing or stale card (📡).
- **Domain (`.gravity/`)** — a durable subject area with its own principle and non-goal, earning a `.gravity/<domain>/` folder; most features are just a `PLAN.*.md` slice. Two axes, capability first — the gate lives in `.gravity/ROUTER.md`. Vs DDD: a gravity domain is a documentation facet, looser than a bounded context.
- **Machinery sigil (`_`)** — a leading underscore on a `.gravity/` folder marks gravity's own machinery, never a subject domain: `_lib/` (installed instruments), `_observatory/` (generated page), `_inbox/` (drop zone), `_given/` (received knowledge, root and per-domain). Replaces v3's prose list; machinery sorts apart from the alphabetized domains and can't collide with one. A pre-v4 project reports `MACHINERY_UNMIGRATED`; `python .claude/scripts/migrate_gravity_v4.py <name>` fixes it.
- **`SPEC.md` — the change contract** — the per-domain agent-loadable contract: Minimal Shape + enforcement-tagged Rules (anatomy in the card). Vs industry "spec-driven development": **spec-governed change, not spec-generated scaffolding**.
- **Integration domain** — optional `.gravity/integration/` for contracts *between* services/domains (Boundary Map + Change Order). Promote from `CONTRACT.md` when agents repeatedly cross boundaries; never for a service's internals.
- **Doc ownership** — each concern has one canonical owner doc; other docs *link*, never restate. `/triage` flags collisions. The ownership table is workspace `CLAUDE.md` §6; the protocol side is the card.
- **`gravity/DESIGN.docs.md`** — the guide to the browser-read HTML-doc theme, which `gravity/lib/doc_theme.py` generates and `.claude/scripts/apply_doc_theme.py` applies (distinct from a project's app-design `DESIGN.md`).
- **`RUNBOOK.md`** — optional operations doc for projects that deploy: the *"would you need this at 2am?"* test. Secrets stay pointers, never values.
- **Patch-loop** — the 7-step safe-patching ritual behind `/patch-slice` (`docs/PLAN.patch-loop.md`; walls in `.claude/scripts/patch_slice.py`). Bug intake is its front door: a bug enters as a currently-false `given/when/then`, and the fix leaves the regression test that graduates it.
- **`PROJECTS.md`** — workspace-level project index at the root. Source of truth for which tier each project lives in.
- **`HANDBOOK.md`** — this file. Human-facing guide. Not auto-loaded into agent context.
- **Stale** — for `active/` projects, untouched >14 days. `/triage` flags these. Very stale (>30 days) should probably move to `dormant/`.
- **Orphan** — a folder under `repos/` with no junction in any tier. `/triage` flags these too.
- **Stencil** — a `CONTEXT.md` copied from the template but never filled in (still has `YYYY-MM-DD` / `<project name>` placeholders). Listed as active but holds no real state. `/triage` flags these as top priority.
- **Bloated** — a `CONTEXT.md` that has outgrown its snapshot role (>~6 Completed bullets or >~80 lines). Needs pruning, not clearing — git history keeps the old versions. `/triage` flags these.

---

## See also

- `docs/INTRO.html` — the browser-read **introduction to gravity**. The onboarding read; this handbook is the working reference.
- `CLAUDE.md` — the agent operating manual (Kepler rules and invariants).
- `gravity/GRAVITY-PROTOCOL.md` — **the protocol card**: the canonical project-side doctrine, copied to `.gravity/GRAVITY.md` at adoption.
- `gravity/README.md` — the catalog of every stencil and lib instrument, one line each.
- `.claude/commands/` — the slash-command definitions: the one home for what each command actually does.
- `.claude/scenarios/README.md` — finding meanings and severity bars for every `check.py` checker.
- `PROJECTS.md` — the current project index.
