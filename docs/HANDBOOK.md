# AI Workspace — Handbook

Human-facing guide for working in `ai-workspace/`. The agent's operating rules live in `CLAUDE.md` (loaded into every agent session); this file is for **you** — open it when you need a walkthrough, a slash-command lookup, or to clarify terminology.

---

## Quick start — "I want to..."

| I want to... | Use |
|---|---|
| Create a brand-new project | `/init-project <name>` ([Workflow 1](#workflow-1--create-a-brand-new-project) is the manual fallback) |
| Bring in a project that already lives elsewhere on disk | [Workflow 2](#workflow-2--bring-in-an-existing-project-from-elsewhere) |
| Graduate an experiment from `incubator/` to `active/` | `/promote <name>` ([Workflow 3](#workflow-3--promote-from-incubator) is the manual fallback) |
| Move a project between tiers | `mv <tier>/<name> <other-tier>/` (instant — see [storage model](#storage-model)) |
| See status across all projects | `/triage` |
| Re-orient on one project — what's it for, what should I ask? | `/mission <name>` |
| Give a long-lived project a "why" doc and a phase roadmap | [Adopt the full doc pipeline](#adopt-the-full-doc-pipeline) |
| Move a doc-heavy project's docs into a `.gravity/` directory | `/adopt-gravity <name>` ([Adopt the `.gravity/` doc system](#adopt-the-gravity-doc-system)) |
| Add a new domain to a `.gravity/` project | `/new-domain <name> <domain>` |
| Know what exists right now | Read `PROJECTS.md` |

---

## Slash commands

Run from the `ai-workspace/` root in Claude Code.

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a brand-new project end-to-end: creates `repos/<name>/`, junctions it into `active/`, copies both templates, runs `git init`, adds a row to `PROJECTS.md`. |
| `/promote <name>` | Graduate `incubator/<name>` into a real project: moves it into `repos/<name>/`, junctions into `active/`, runs `git init` if missing, copies missing templates (preserves existing), adds a row to `PROJECTS.md`. |
| `/triage` | Survey `active/` + `dormant/`, read each `CONTEXT.md`, flag stale projects (>14 days), unfilled stencils, bloated files needing a prune, index drift, and doc-pipeline drift (incl. doc collisions — a fact restated across MISSION + CLAUDE.md). For `.gravity/` projects it runs `.claude/scenarios/check.py` to mechanically catch orphaned domains (a folder not wired into all four registry indexes). Produces a one-page status report. Read-only by default. |
| `/mission <name>` | Re-orient on one project: read its four docs (plus `ARCHITECTURE.html` and the `.gravity/` Doc Map if present) and print what it's for, where it stands, and the sharp questions worth asking the agent next. Read-only. Run it when you've lost the thread. |
| `/adopt-gravity <name>` | Retrofit the `.gravity/` doc system into a doc-heavy project: relocate the heavy docs out of the root into per-domain `.gravity/` folders (`git mv`), seed the root-`CLAUDE.md` router, wire the four registry owners. Proposes the move table and confirms before touching disk; doesn't commit. |
| `/new-domain <name> <domain>` | Mint one domain inside a project's `.gravity/`: run the *is-it-a-domain?* gate, create `.gravity/<domain>/PLAN.md`, and wire all four indexes (Doc Map, router table, MISSION row, status spine) so it's never orphaned. |
| `/new-spec <name> <domain>` | Author (or retrofit) one domain's `SPEC.md` from `SPEC.template.md` — the generative Minimal Shape + enforcement-tagged Rules. Finds the real gate, tags each rule only from evidence, wires the Doc-Map + router rows, runs the gate to prove it. |
| `/cut-release [name]` | Cut a versioned release with one Change Order. **No arg → bumps gravity itself** (`VERSION` + tag on the workspace skeleton repo); **`<name>` → bumps that project** (its manifest + tag). Resolves the version (stops on tag-vs-file drift), proposes + confirms the major/minor/patch bump from the changelog's `[Unreleased]`, runs the gate (won't tag red code), rewrites the changelog, bumps, commits, tags — **stops before push**. |
| `/retire <name>` | End a project's lifecycle: print a read-only risk card (remote? commits? uncommitted? referenced elsewhere?), then on your choice **archive** (junction → `archive/`, reversible) or **delete** (detach every junction, remove the real folder, permanent). Reconciles `PROJECTS.md` + regenerates the dashboard. |
| `/dashboard` | One-screen status across all four tiers; active projects on the full pipeline also show their mission + current phase. Regenerates the visual HTML dashboard. |
| `/open-dashboard` | The one-tap visual shortcut: regenerate the HTML dashboard from `PROJECTS.md` and **open it in the browser** — no terminal report. Use when you just want to *see* the dashboard. |
| `/open-mission [project]` | Open a project's `MISSION.html` in the browser (root or `.gravity/`); no arg opens the workspace's own. Authored doc — just locates + launches, never regenerates. |
| `/open-architecture [project] [facet]` | Open a project's `ARCHITECTURE.html` in the browser — the system overview, or a named facet (`.gravity/<facet>/ARCHITECTURE.html`). Locates + launches; never regenerates. No arg → explains gravity's own architecture lives in `CLAUDE.md §1`. |

---

## The four-doc pipeline (optional)

Every project carries two files: `CLAUDE.md` (stable identity) and `CONTEXT.md` (rolling now). A project with a real arc — multi-phase, long-lived, the kind you keep losing the thread on — can add two more, so that **four docs change at four different rates**:

| Doc | Answers | Changes | Why this format |
|---|---|---|---|
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML — a stable thing you *read* in a browser; styled via `DESIGN.docs.md` |
| `CLAUDE.md` | **How** — identity, stack, constraints | on refactors | Markdown — auto-loads into the agent |
| `IMPLEMENTATION_PLAN.md` | **What/next** — phases, locked decisions, the gate | per phase | Markdown — the agent edits it, so clean diffs win |
| `CONTEXT.md` | **Now** — state + the one next step | per session | Markdown — auto-loads into the agent |

It's **opt-in**. Most projects don't need it; the overhead only pays off when the mission keeps slipping out of view. `/mission` reads these four to re-orient you; `/triage` flags when they contradict each other.

**One concern, one home.** These docs answer different questions, so they shouldn't collide — but a fact written in two of them drifts into two different facts. Each concern has one canonical owner; another doc that needs it *links* rather than restates. Why → `MISSION.html`; how-to-behave/stack/secrets → `CLAUDE.md`; what's-next → `IMPLEMENTATION_PLAN.md`; now → `CONTEXT.md`. The classic overlap is the architectural seam: MISSION owns the one-line *principle*, CLAUDE.md owns the *mechanics* and points back. `/triage` flags collisions (the same fact restated across docs).

**Optional fifth doc — `ARCHITECTURE.html`.** When "how it's built" outgrows CLAUDE.md's Entry Points (multiple services, non-obvious data flow, several contributors), add a browser-read `ARCHITECTURE.html` (copy `ARCHITECTURE.template.html`, theme via `DESIGN.docs.md`) as the canonical home for component boundaries, the seam's mechanics, and data contracts. Recognized when present (`/mission` reads it, `/triage` checks it), never mandated — a file map in CLAUDE.md is enough for most projects.

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
├── dormant/
│   └── old-x     ─→ junction → repos/old-x
├── archive/
│   └── done-y    ─→ junction → repos/done-y
└── incubator/
    └── prototype-z         ← real folder (no junction; ephemeral)
```

Tier folders are **views**, not storage. A project's tier = which junction folder it appears in. Moving between tiers (`mv active/x dormant/`) renames a ~1KB pointer — instant, never touches `node_modules` or `.venv`.

`incubator/` is the exception: real folders, not junctions. Graduation to `active/` means `mv`-ing into `repos/` first (see [Workflow 3](#workflow-3--promote-from-incubator)).

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
cp templates/CLAUDE.template.md  "repos/$name/CLAUDE.md"
cp templates/CONTEXT.template.md "repos/$name/CONTEXT.md"
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
[ -f "repos/$name/CLAUDE.md" ]  || cp templates/CLAUDE.template.md  "repos/$name/CLAUDE.md"
[ -f "repos/$name/CONTEXT.md" ] || cp templates/CONTEXT.template.md "repos/$name/CONTEXT.md"
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
[ -f "$src/CLAUDE.md" ]  || cp templates/CLAUDE.template.md  "$src/CLAUDE.md"
[ -f "$src/CONTEXT.md" ] || cp templates/CONTEXT.template.md "$src/CONTEXT.md"
```

---

## Workflow 3 — Promote from `incubator/`

**Easy way:** `/promote <name>` from the workspace root. Done.

**Manual way:** when an experiment proves itself worth keeping.

1. Move the incubator folder into `repos/<name>/`.
2. Junction it into `active/<name>`.
3. `git init` if it isn't already a git repo.
4. Copy missing templates (incubator projects typically lack them).
5. Fill in `CLAUDE.md` (stable identity) and `CONTEXT.md` (current state + Next Step).
6. Add a row to `PROJECTS.md`.

**PowerShell:**
```powershell
$name = "<name>"
Move-Item "incubator\$name" "repos\$name"
New-Item -ItemType Junction -Path "active\$name" -Target "repos\$name" | Out-Null
Set-Location "active\$name"
if (-not (Test-Path ".git"))       { git init }
if (-not (Test-Path "CLAUDE.md"))  { Copy-Item ..\..\templates\CLAUDE.template.md  CLAUDE.md }
if (-not (Test-Path "CONTEXT.md")) { Copy-Item ..\..\templates\CONTEXT.template.md CONTEXT.md }
```

**Bash:**
```bash
name="<name>"
mv "incubator/$name" "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
cd "active/$name"
[ -d ".git" ]       || git init
[ -f "CLAUDE.md" ]  || cp ../../templates/CLAUDE.template.md  CLAUDE.md
[ -f "CONTEXT.md" ] || cp ../../templates/CONTEXT.template.md CONTEXT.md
```

---

## Adopt the full doc pipeline

When a project has grown a real arc and you keep re-deriving "what was this for again?", give it the two extra docs (see [the four-doc pipeline](#the-four-doc-pipeline-optional)). Worth it when the project is multi-phase, long-lived, and `active/`; skip for one-shots, incubator experiments, and anything dormant or archived.

1. Copy the two templates into the project (don't overwrite if they somehow exist):

   **Bash:**
   ```bash
   name="<name>"
   [ -f "repos/$name/MISSION.html" ]             || cp templates/MISSION.template.html             "repos/$name/MISSION.html"
   [ -f "repos/$name/IMPLEMENTATION_PLAN.md" ]   || cp templates/IMPLEMENTATION_PLAN.template.md   "repos/$name/IMPLEMENTATION_PLAN.md"
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
5. The `MISSION.html` styling comes preloaded from the theme; if you hand-roll other HTML docs, match `DESIGN.docs.md`.

> Or just ask the agent: *"adopt the full doc pipeline for `<name>`"* — it'll copy the templates and help you fill them.

---

## Adopt the `.gravity/` doc system

The four-doc pipeline above keeps the docs at the project root. Once a project grows **several** architecture/spec/plan docs across **multiple domains**, the root gets crowded and the two files that auto-load (`CLAUDE.md`, `CONTEXT.md`) get buried. The `.gravity/` system (workspace `CLAUDE.md` §6) fixes that: it relocates every heavy doc into a `.gravity/` directory **organized by subject domain**, leaving only `CLAUDE.md` + `CONTEXT.md` + `README.md` at the root. The root `CLAUDE.md` becomes the **router** — a Doc Map plus a "what to read before which change" table. `knowledge-viewer` is the worked example.

It's **opt-in and recognized only when present** — for projects that outgrew the flat root. CLIs, scripts, and libraries never need it; the two-doc minimum stays correct for them.

**Retrofit an existing project** — run `/adopt-gravity <name>`. The agent inventories the root, proposes a before→after move table (grouping docs by domain — *you confirm the boundaries*), `git mv`s them into `.gravity/<domain>/` folders, fixes cross-references, seeds the root-`CLAUDE.md` router from `GRAVITY.template.md`, and wires the four registry owners (directory · CLAUDE.md routing · MISSION why-rows · IMPLEMENTATION_PLAN status). It stops to confirm before moving anything and doesn't commit.

**Add a domain later** — run `/new-domain <name> <domain>`. It runs the *is-it-a-domain?* gate first (most features are a `PLAN.*.md` slice under an existing domain, not a new folder), then creates `.gravity/<domain>/PLAN.md` and **wires all four indexes** so the domain is never orphaned. The full gate + lifecycle lives in the project's root `CLAUDE.md` "Adding a domain" section (seeded from `GRAVITY.template.md`).

**Add an integration layer** — use the normal domain flow with the reserved name `integration` when a project has cross-boundary rules that repeatedly affect more than one service/domain: API/client type generation, auth/session flow, ports/base URLs, shared env, queues/events, webhooks, database access boundaries, or required change order. Keep small facts in `CONTRACT.md`; promote to `.gravity/integration/SPEC.md` when agents need a durable, enforcement-tagged contract before coding across boundaries. This is service-aware gravity, not a separate project topology.

> Or just ask the agent: *"move `<name>` onto the `.gravity/` doc system"* / *"add a `<domain>` domain to `<name>`"*.

---

## Glossary

- **Junction** — Windows directory pointer (`mklink /J`, or PowerShell `New-Item -ItemType Junction`). Same-volume only. No admin or Developer Mode required. We use junctions, not symbolic links, throughout the tier folders. **Always create one via `.claude/scripts/link_project.py <link> <target>`** (junction on Windows, symlink on Linux/WSL) or PowerShell `New-Item -ItemType Junction`. Never use the Git-Bash form `cmd //c "mklink /J active\\$name …"` — MSYS quoting eats the `$name` variable and creates a bogus `active$name` link. The helper drives `mklink` through Python argv, so no shell can corrupt the paths.
- **Symbolic link (symlink)** — `mklink /D` on Windows; `ln -s` on POSIX. On Windows requires admin or Developer Mode. Crosses volumes; has full POSIX semantics under WSL. Use only when junctions aren't enough.
- **Tier** — one of `active/`, `dormant/`, `archive/`. A project's tier = which tier folder its junction lives in.
- **View vs storage** — `repos/` is **storage** (real files). Tier folders are **views** (junctions). Moving a project between views doesn't touch storage.
- **Repo vs project** — used interchangeably here. Each project under `repos/` is its own independent git repository with its own remote.
- **Root** — the `ai-workspace/` directory itself. Never `git init` here; it's a local-only management layer.
- **Workspace-level `CLAUDE.md`** — the agent operating manual at the workspace root. Auto-loaded every agent session. Contains rules and invariants only.
- **Project-level `CLAUDE.md`** — per-project stable identity file (`repos/<name>/CLAUDE.md`). Stack, run commands, conventions. Auto-loaded when an agent opens at that project.
- **`CONTEXT.md`** — per-project mutable handoff file. Completed / Current State / Next Step. Updated every session. A **rolling snapshot of now, not a log** — keep it small (Completed = last 1–2 sessions; prune when >~6 Completed bullets or >~80 lines). git history is the changelog, so pruning loses nothing. See workspace `CLAUDE.md` §6.
- **`MISSION.html`** — optional per-project "why" doc: north star, principles, non-goals. The slowest-changing of the four docs; read in a browser. Copy from `MISSION.template.html`. Part of the [four-doc pipeline](#the-four-doc-pipeline-optional).
- **`IMPLEMENTATION_PLAN.md`** — optional per-project "what/next" doc: phase roadmap, locked decisions, the verification gate, open questions. Changes per phase; the agent edits it. Copy from `IMPLEMENTATION_PLAN.template.md`. The multi-phase arc lives here; `CONTEXT.md` holds only *now*.
- **Four-doc pipeline** — the optional `MISSION.html` + `CLAUDE.md` + `IMPLEMENTATION_PLAN.md` + `CONTEXT.md` set, ordered by how often each changes (rarely → per-session). Opt-in for ambitious `active/` projects. See workspace `CLAUDE.md` §6.
- **`ARCHITECTURE.html`** — optional per-project *fifth* doc: the canonical "how it's built" (component boundaries, the seam's mechanics, data contracts, build/deploy shape). Add only when "how it's built" outgrows CLAUDE.md's Entry Points. Browser-read; copy from `ARCHITECTURE.template.html`, styled via `DESIGN.docs.md`. Recognized when present, never mandated. See workspace `CLAUDE.md` §6.
- **`.gravity/`** — optional per-project directory that holds the heavy docs (everything but the root `CLAUDE.md` + `CONTEXT.md` + `README.md`), organized **by subject domain** rather than doc-type. Top level carries the cross-cutting `MISSION.html` / `ARCHITECTURE.html` / `IMPLEMENTATION_PLAN.md` / `DESIGN.md`; each `<domain>/` folder carries whichever of `ARCHITECTURE.html` (human *how*) · `SPEC.md` (agent *rules*) · `PLAN.*.md` (*what/next*) it needs. The directory **is** the domain registry — no registry file. Adopt with `/adopt-gravity`, extend with `/new-domain`. Recognized when present, never mandated (for projects that outgrew the flat root). `knowledge-viewer` is the worked example. See workspace `CLAUDE.md` §6.
- **Domain (`.gravity/`)** — a durable subject area an agent repeatedly navigates and changes, with its own *principle* and non-goal — earns a `.gravity/<domain>/` folder. Not every feature is a domain; a one-off is a `PLAN.*.md` slice under an existing domain. The *is-it-a-domain?* gate lives in the project's root `CLAUDE.md` (seeded from `GRAVITY.template.md`).
- **Integration domain** — optional `.gravity/integration/` folder for contracts between services/domains: API/client type flow, auth/session, ports/base URLs, shared env, queues/events, webhooks, database access boundaries, and required change order. Use it when `CONTRACT.md` is too small/flat for repeated agent work; do not use it for internal backend, frontend, or schema rules.
- **Doc ownership** — the rule that each concern has one canonical owner doc; other docs *link* to it rather than restate it (why → MISSION, how → CLAUDE.md, what/next → PLAN, now → CONTEXT, how-it's-built → CLAUDE.md/ARCHITECTURE.html). Prevents the same fact drifting into two different facts. `/triage` flags **doc collisions** — a fact restated across docs. See workspace `CLAUDE.md` §6.
- **`DESIGN.docs.md`** — the shared warm-terminal theme for browser-read project HTML docs (`MISSION.html` and any hand-rolled architecture/design page). Stylesheet + skeleton to copy.
- **`PROJECTS.md`** — workspace-level project index at the root. Source of truth for which tier each project lives in.
- **`HANDBOOK.md`** — this file. Human-facing guide. Not auto-loaded into agent context.
- **Stale** — for `active/` projects, untouched >14 days. `/triage` flags these. Very stale (>30 days) should probably move to `dormant/`.
- **Orphan** — a folder under `repos/` with no junction in any tier. `/triage` flags these too.
- **Stencil** — a `CONTEXT.md` copied from the template but never filled in (still has `YYYY-MM-DD` / `<project name>` placeholders). Listed as active but holds no real state. `/triage` flags these as top priority.
- **Bloated** — a `CONTEXT.md` that has outgrown its snapshot role (>~6 Completed bullets or >~80 lines). Needs pruning, not clearing — git history keeps the old versions. `/triage` flags these.

---

## See also

- `CLAUDE.md` — agent operating manual (rules and invariants).
- `PROJECTS.md` — current project index.
- `.claude/commands/` — slash command definitions (read these to understand exactly what `/init-project`, `/triage`, `/mission`, `/adopt-gravity`, and `/new-domain` do).
- `.claude/scenarios/` — gravity's **golden-scenario harness**: tests its own commands. `check.py` is the structural-invariant checker (`selftest` to prove it, `consistency` to check any `.gravity/` project, `scenario` to replay one); each `<command>/` folder holds a golden fixture + `expect.json` + a `SCENARIO.md` replay recipe. `/triage` calls the same checker. See `.claude/scenarios/README.md`.
- `MISSION.template.html` · `IMPLEMENTATION_PLAN.template.md` · `ARCHITECTURE.template.html` · `SPEC.template.md` · `DESIGN.docs.md` — the optional pipeline stencils (four-doc + optional fifth + agent spec) and the HTML doc theme.
- `GRAVITY.template.md` — the root-`CLAUDE.md` router block (Doc Map + read-first table + domain gate) for projects adopting the `.gravity/` doc system.
