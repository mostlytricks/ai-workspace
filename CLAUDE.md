# AI Workspace — Agent Operating Manual

Root contract for any coding agent working inside `ai-workspace/`. **Rules and invariants only** — step-by-step workflows for humans live in `HANDBOOK.md`.

Always open the agent at this root, never one level deeper. When a project subdirectory has its own `CLAUDE.md` or `CONTEXT.md`, that local file wins on conflict.

---

## 1. Workspace Map

```text
ai-workspace/
├── CLAUDE.md                       # This file. Rules for agents.
├── MISSION.html                    # The workspace's own north star — the durable why behind these rules.
├── HANDBOOK.md                     # Human-facing guide: workflows, slash commands, glossary.
├── PROJECTS.md                     # Index of all projects across tiers.
├── CLAUDE.template.md              # Per-project stable-identity stencil.
├── CONTEXT.template.md             # Per-project session-handoff stencil.
├── MISSION.template.html           # Per-project "why" stencil (optional four-doc pipeline, §6).
├── IMPLEMENTATION_PLAN.template.md # Per-project "what/next" stencil (optional four-doc pipeline, §6).
├── ARCHITECTURE.template.html      # Per-project "how it's built" stencil (optional fifth doc, §6).
├── DOC_THEME.md                    # Shared theme for browser-read project HTML docs.
├── .gitignore                      # Defense-in-depth against accidental git init at root.
├── .claude/commands/               # Workspace-level slash commands.
├── .claude/scripts/                # Helper scripts (link_project.py, new_project.py).
│
├── repos/                          # CANONICAL storage. Real project files live here.
├── incubator/                      # Ephemeral real folders. No junctions.
├── active/                         # Junctions → repos/. Touched <30 days.
├── dormant/                        # Junctions → repos/. Paused; CONTEXT.md must name a resume blocker.
└── archive/                        # Junctions → repos/. Done. Read-only.
```

**Routing:**
- New idea, unclear future → `incubator/<name>/` (real folder).
- New real project OR promoted from incubator → `repos/<name>/`, junction into `active/<name>`.
- Pause an active project → `mv active/<name> dormant/`. Update CONTEXT.md's Next Step with the resume blocker.
- Resume → `mv dormant/<name> active/`. Refresh CONTEXT.md.
- Done or dead → `mv */<name> archive/`. No further edits.

After any transition, update `PROJECTS.md`.

Never create files at the workspace root other than the meta files listed above.

---

## 2. Git Boundaries

- Root is local-only. Never `git init` at `ai-workspace/`. Never push the workspace as an umbrella repo.
- Version control lives in `repos/<project>/`. Each project is an independent repo with its own remote.
- Junctions are transparent to `git` — commands run from inside a tier junction operate on the real `.git` in `repos/<project>/`.

---

## 3. Project Storage Invariants

A project's real files live in **one of two places**:
- **`repos/<name>/`** — default for new projects. Tier folders hold junctions pointing here.
- **An external path** (e.g. `D:\code\old-thing\`) — when something hardcodes the existing path (IDE workspace files, CI, different drive). Junction directly from the tier folder; skip `repos/`.

**Invariants:**
- Tier folders (`active/`, `dormant/`, `archive/`) hold **directory junctions** (`mklink /J`) only — never real project files. `incubator/` is the exception: real folders.
- Use junctions, not symbolic links. Junctions need no admin or Developer Mode on Windows. Use `mklink /D` only when crossing drives or needing full POSIX semantics under WSL.
- **Create links only via `python .claude/scripts/link_project.py <link> <target>`** (junction on Windows, symlink on Linux/WSL) or PowerShell `New-Item -ItemType Junction`. **Never** the Git-Bash form `cmd //c "mklink /J active\\$name …"` — MSYS quoting silently drops the `$name` variable and creates a bogus `active$name` link. The helper is argv-driven, so no shell can corrupt the paths; `/init-project` and `/promote` both use it.
- Tier transitions = `mv <tier>/<name> <other-tier>/`. Same-drive `mv` is metadata-only and instant; never touches `node_modules` or `.venv`.
- Never use File Explorer drag-drop to move folders containing `node_modules` or `.venv` — it sometimes performs file-by-file copies and thrashes the disk. Use `mv` (bash) or `Move-Item` (PowerShell).

**For step-by-step procedures** (new project, bring in existing, promote from incubator, including PowerShell + Bash code), see **HANDBOOK.md**. For the common new-project case, use `/init-project <name>`.

---

## 4. Python `.venv` Isolation

- No root venv. Never create or activate `.venv` at `ai-workspace/` or `repos/`. Shared venvs cause silent version collisions.
- One venv per project, inside its own `repos/<name>/` folder.
- `cd` into the specific project folder (junction or real path — both work) before running `pip install` or `python -m venv`. The interpreter context must match the closest `.venv` to the file being edited.
- A venv created via the junction path hardcodes the underlying real path. Fine in place — but if the real folder ever moves out of `repos/`, recreate the venv.

---

## 5. Multi-Service Contract Pattern

When a project contains multiple services that talk to each other, treat them as one integrated unit.

- Before editing across services, locate the contract file in the project root (`GLOBAL_RULES.md`, `CONTRACT.md`, or the project `CLAUDE.md`). It documents port assignments, base URLs, auth flow, shared schema locations. If none exists and you're changing a cross-service interface, create one first.
- Data-mutation loop: update backend entity/DTO/schema first → run schema export if one exists → update frontend types and API client → verify the contract file still matches.

---

## 6. Per-Project Files — `CLAUDE.md` & `CONTEXT.md`

Each project in `repos/` (i.e. anything surfaced via `active/` or `dormant/`) has two files at its root:

- **`<project>/CLAUDE.md` — stable identity.** What the project is, stack, run/test commands, conventions, gotchas. Rarely changes. Auto-loads when an agent opens at that subdir (works through the junction). Copy from `CLAUDE.template.md`.
- **`<project>/CONTEXT.md` — mutable handoff state.** Completed / Current State / Next Step. Updated every session. A **rolling snapshot of *now***, not a log — see *Keeping CONTEXT.md small* below. Copy from `CONTEXT.template.md`.

Templates are stencils, not config — nothing loads them automatically.

**Skip both** for `incubator/` one-shots (overhead exceeds value) and `archive/` (no further edits; leave existing CONTEXT.md as the final state record).

**Session ritual** for `active/` and `dormant/` projects:
- **At start** (entering a project subdir): read `<project>/CONTEXT.md` first. If missing and the project qualifies, copy the template.
- **At end** (before stopping): update Completed / Current State / Next Step, bump `Last touched`. For dormant projects, Next Step must name the resume blocker.
- A stale `CONTEXT.md` is worse than none. If you didn't update it, say so in the file rather than leaving outdated claims.

A qualifying session that ends without updating `CONTEXT.md` is incomplete.

**Keeping CONTEXT.md small — it's a snapshot, not a log.**

CONTEXT.md answers "where is this *now* and what's next" — nothing more. The durable record of *what happened over time* lives elsewhere and must not be duplicated here:

- **git history is the changelog.** `git log -p CONTEXT.md` recovers every past version of this file verbatim. Pruning CONTEXT.md is therefore **non-destructive** — old state isn't lost, it's in git. For the agent-pipeline projects, `CHANGELOG.md` / `registry.jsonl` are the durable record too.

Refresh rules (apply on every update):
- **Completed** — last 1–2 sessions only. Drop older bullets; they're in `git log`. It's a window, not an archive.
- **Current State** — overwrite to describe present reality. Don't append deltas on top of stale claims.
- **Next Step** — exactly one item, replaced each time.
- **Prune trigger:** if Completed exceeds ~6 bullets or the file exceeds ~80 lines, trim before you finish. `/triage` flags files that cross these thresholds.
- **Never clear to zero.** A project moving to `archive/` freezes its CONTEXT.md as the final-state record (per *Skip both* above).

**Optional: the full four-doc pipeline (ambitious `active/` projects only).**

The two mandatory files cover identity and now. A project with a real arc — multi-phase, long-lived, easy to lose the thread on — may add two more, giving **four docs that change at four different rates**:

| Doc | Question | Changes | Format |
|---|---|---|---|
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML (browser-read; copy `MISSION.template.html`, theme in `DOC_THEME.md`) |
| `CLAUDE.md` | **How** — identity, stack, constraints | on refactors | Markdown (auto-loads) |
| `IMPLEMENTATION_PLAN.md` | **What/next** — phases, locked decisions, the gate | per phase | Markdown (agent edits it; copy `IMPLEMENTATION_PLAN.template.md`) |
| `CONTEXT.md` | **Now** — state + single next step | per session | Markdown (auto-loads) |

This is **opt-in**, not mandated — most projects (and all `incubator/`/`dormant/` ones) stay on the two-doc rule; the overhead only pays off when you keep losing the mission across sessions or projects. `MISSION.html` is HTML because it's a stable thing you *read*; `IMPLEMENTATION_PLAN.md` is Markdown because it changes every phase and the agent edits it. Boundary to keep: PLAN holds the multi-phase arc, CONTEXT holds only *now* — don't duplicate. `/mission <project>` re-orients off these four; `/triage` flags drift between them. See HANDBOOK "Adopt the full doc pipeline" for the how.

**Doc ownership — one concern, one home (reference, don't restate).**

These docs answer *different* questions, so they shouldn't *collide* — but the same fact written in two of them eventually drifts into two *different* facts. The rule: every concern has exactly **one canonical owner**; any other doc that needs it **links to the owner rather than restating it**.

| Concern | Owner | The test |
|---|---|---|
| Why it exists · principles · strategic non-goals | **MISSION.html** | "would breaking this betray the mission?" |
| Identity · stack · run/test · entry points · gotchas · secrets | **CLAUDE.md** | "would breaking this fail a build or leak a secret?" |
| Phases · locked decisions · the gate | **IMPLEMENTATION_PLAN.md** | "is this about *what's next*?" |
| Current state · the single next step | **CONTEXT.md** | "is this only true *right now*?" |
| How it's built · seams · data contracts | **CLAUDE.md** Entry Points — or **ARCHITECTURE.html** when it outgrows a file map | "would a new contributor need this to navigate the code?" |

The overlap to watch is the **architectural seam**. MISSION owns the one-sentence *principle* ("everything reduces to one Session shape" / "the JSON deck-spec is the interface"); CLAUDE.md (or ARCHITECTURE.html) owns the *mechanics* (which files, the gotcha) and points back — *"preserve the seam (MISSION §04)"* — instead of re-describing it. Same for non-goals vs constraints: a strategic "we don't do X" lives in MISSION; the operational "doing X breaks the build" lives in CLAUDE.md.

**Optional fifth doc — `ARCHITECTURE.html` (how it's built).** Most projects describe their architecture adequately in CLAUDE.md's *Entry Points* (a file map) plus the one-line seam in MISSION — leave it there. A project whose "how it's built" genuinely outgrows a file map — multiple services, non-obvious data flow, several contributors — may add a browser-read `ARCHITECTURE.html` (copy `ARCHITECTURE.template.html`, theme in `DOC_THEME.md`) as the canonical home for component boundaries, the seam's mechanics, data contracts, and build/deploy shape. It is **recognized only when present** (like MISSION.html — `/mission` reads it, `/triage` checks it) and **never mandated**; don't add it where a file map already serves. For cross-service contracts specifically, §5's `CONTRACT.md`/`GLOBAL_RULES.md` is this same idea living at the service boundary.

---

## 7. Cross-Project Tooling

- **`PROJECTS.md`** is the index. One line per project: name, stack, last-touched, focus or resume blocker. Update on any tier transition or significant status change.
- **`/init-project <name>`** scaffolds a brand-new project end-to-end (Workflow 1 in HANDBOOK): creates `repos/<name>/`, junctions into `active/`, copies both templates, runs `git init`, adds a `PROJECTS.md` row. Use instead of running §3-referenced commands by hand.
- **`/promote <name>`** graduates an incubator project to active (Workflow 3 in HANDBOOK): `mv incubator/<name> repos/<name>`, junctions into `active/`, runs `git init` only if missing, copies templates only if missing (never overwrites), adds a `PROJECTS.md` row.
- **`/triage`** scans `active/` + `dormant/` (following junctions into `repos/`), reads each `CONTEXT.md`, and flags stale entries, **unfilled stencils**, **bloated files needing a prune** (per §6 thresholds), index drift, and **doc-pipeline drift** (MISSION non-goals vs recent work, plan-phase vs CONTEXT contradictions, ambitious projects missing a mission doc, and **doc collisions** — the same fact restated across MISSION and CLAUDE.md, per the §6 ownership rule), and orphans — producing a one-page report. Read-only by default. Use weekly.
- **`/mission <project>`** re-orients on a single project: reads its four docs — plus `ARCHITECTURE.html` if present (per the optional pipeline in §6) — and prints what it's for, where it stands, and the sharp questions worth asking the agent next. Read-only. Use when you've lost the thread on *why* a project exists or *what to ask* to push it forward.
- **`HANDBOOK.md`** is the human-facing guide — workflows, slash command cheat sheet, glossary. Not auto-loaded; agents may read it when explicitly asked.
