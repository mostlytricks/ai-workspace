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
| Know what exists right now | Read `PROJECTS.md` |

---

## Slash commands

Run from the `ai-workspace/` root in Claude Code.

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a brand-new project end-to-end: creates `repos/<name>/`, junctions it into `active/`, copies both templates, runs `git init`, adds a row to `PROJECTS.md`. |
| `/promote <name>` | Graduate `incubator/<name>` into a real project: moves it into `repos/<name>/`, junctions into `active/`, runs `git init` if missing, copies missing templates (preserves existing), adds a row to `PROJECTS.md`. |
| `/triage` | Survey `active/` + `dormant/`, read each `CONTEXT.md`, flag stale projects (>14 days), unfilled stencils, bloated files needing a prune, index drift, and doc-pipeline drift — produce a one-page status report. Read-only by default. |
| `/mission <name>` | Re-orient on one project: read its four docs and print what it's for, where it stands, and the sharp questions worth asking the agent next. Read-only. Run it when you've lost the thread. |
| `/dashboard` | One-screen status across all four tiers; active projects on the full pipeline also show their mission + current phase. Regenerates the visual HTML dashboard. |

---

## The four-doc pipeline (optional)

Every project carries two files: `CLAUDE.md` (stable identity) and `CONTEXT.md` (rolling now). A project with a real arc — multi-phase, long-lived, the kind you keep losing the thread on — can add two more, so that **four docs change at four different rates**:

| Doc | Answers | Changes | Why this format |
|---|---|---|---|
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML — a stable thing you *read* in a browser; styled via `DOC_THEME.md` |
| `CLAUDE.md` | **How** — identity, stack, constraints | on refactors | Markdown — auto-loads into the agent |
| `IMPLEMENTATION_PLAN.md` | **What/next** — phases, locked decisions, the gate | per phase | Markdown — the agent edits it, so clean diffs win |
| `CONTEXT.md` | **Now** — state + the one next step | per session | Markdown — auto-loads into the agent |

It's **opt-in**. Most projects don't need it; the overhead only pays off when the mission keeps slipping out of view. `/mission` reads these four to re-orient you; `/triage` flags when they contradict each other.

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
Copy-Item CLAUDE.template.md  "repos\$name\CLAUDE.md"
Copy-Item CONTEXT.template.md "repos\$name\CONTEXT.md"
Set-Location "active\$name"
git init
```

**Bash (Git Bash on Windows):**
```bash
name="<name>"
mkdir -p "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
cp CLAUDE.template.md  "repos/$name/CLAUDE.md"
cp CONTEXT.template.md "repos/$name/CONTEXT.md"
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
if (-not (Test-Path "repos\$name\CLAUDE.md"))  { Copy-Item CLAUDE.template.md  "repos\$name\CLAUDE.md" }
if (-not (Test-Path "repos\$name\CONTEXT.md")) { Copy-Item CONTEXT.template.md "repos\$name\CONTEXT.md" }
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
[ -f "repos/$name/CLAUDE.md" ]  || cp CLAUDE.template.md  "repos/$name/CLAUDE.md"
[ -f "repos/$name/CONTEXT.md" ] || cp CONTEXT.template.md "repos/$name/CONTEXT.md"
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
if (-not (Test-Path "$src\CLAUDE.md"))  { Copy-Item CLAUDE.template.md  "$src\CLAUDE.md" }
if (-not (Test-Path "$src\CONTEXT.md")) { Copy-Item CONTEXT.template.md "$src\CONTEXT.md" }
```

**Bash:**
```bash
src="C:/path/to/old-thing"
name="old-thing"
python .claude/scripts/link_project.py "active/$name" "$src"   # junction (Win) / symlink (POSIX)
[ -f "$src/CLAUDE.md" ]  || cp CLAUDE.template.md  "$src/CLAUDE.md"
[ -f "$src/CONTEXT.md" ] || cp CONTEXT.template.md "$src/CONTEXT.md"
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
if (-not (Test-Path "CLAUDE.md"))  { Copy-Item ..\..\CLAUDE.template.md  CLAUDE.md }
if (-not (Test-Path "CONTEXT.md")) { Copy-Item ..\..\CONTEXT.template.md CONTEXT.md }
```

**Bash:**
```bash
name="<name>"
mv "incubator/$name" "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
cd "active/$name"
[ -d ".git" ]       || git init
[ -f "CLAUDE.md" ]  || cp ../../CLAUDE.template.md  CLAUDE.md
[ -f "CONTEXT.md" ] || cp ../../CONTEXT.template.md CONTEXT.md
```

---

## Adopt the full doc pipeline

When a project has grown a real arc and you keep re-deriving "what was this for again?", give it the two extra docs (see [the four-doc pipeline](#the-four-doc-pipeline-optional)). Worth it when the project is multi-phase, long-lived, and `active/`; skip for one-shots, incubator experiments, and anything dormant or archived.

1. Copy the two templates into the project (don't overwrite if they somehow exist):

   **Bash:**
   ```bash
   name="<name>"
   [ -f "repos/$name/MISSION.html" ]             || cp MISSION.template.html             "repos/$name/MISSION.html"
   [ -f "repos/$name/IMPLEMENTATION_PLAN.md" ]   || cp IMPLEMENTATION_PLAN.template.md   "repos/$name/IMPLEMENTATION_PLAN.md"
   ```

   **PowerShell:**
   ```powershell
   $name = "<name>"
   if (-not (Test-Path "repos\$name\MISSION.html"))           { Copy-Item MISSION.template.html           "repos\$name\MISSION.html" }
   if (-not (Test-Path "repos\$name\IMPLEMENTATION_PLAN.md")) { Copy-Item IMPLEMENTATION_PLAN.template.md "repos\$name\IMPLEMENTATION_PLAN.md" }
   ```

2. **Fill `MISSION.html` first** (the why) — open it in a browser as you go. The `.lede` line matters most: `/dashboard` and `/mission` read it verbatim. Nail the **Current Non-Goals** section — that's what keeps an agent on-mission and what `/triage` checks recent work against.
3. **Then `IMPLEMENTATION_PLAN.md`** (the what/next) — list the phases done/next/todo, the locked decisions, and the gate (the exact commands a phase must pass). Move the multi-phase arc *out* of `CONTEXT.md` and into here; leave `CONTEXT.md` holding only *now*.
4. Run `/mission <name>` to sanity-check it reads well and produces useful questions.
5. The `MISSION.html` styling comes preloaded from the theme; if you hand-roll other HTML docs, match `DOC_THEME.md`.

> Or just ask the agent: *"adopt the full doc pipeline for `<name>`"* — it'll copy the templates and help you fill them.

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
- **`DOC_THEME.md`** — the shared warm-terminal theme for browser-read project HTML docs (`MISSION.html` and any hand-rolled architecture/design page). Stylesheet + skeleton to copy.
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
- `.claude/commands/` — slash command definitions (read these to understand exactly what `/init-project`, `/triage`, and `/mission` do).
- `MISSION.template.html` · `IMPLEMENTATION_PLAN.template.md` · `DOC_THEME.md` — the optional four-doc pipeline stencils + the HTML doc theme.
