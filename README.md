# AI Workspace Management

A personal operating system for running many AI/coding projects from one root —
without the usual mess of stray `.venv`s, accidental umbrella repos, and "wait,
what was I doing here?" context loss.

This repository tracks **only the management layer** (the operating manual, the
handbook, the project index, and the slash commands). The projects themselves
live in their own independent git repos and are never committed here.

---

## 🎯 Currently focused on

| Project | Stack | Status |
|---|---|---|
| **multi-system-maintenance-agent-system** | Claude Code subagents + git + JSONL | Build complete (Phases 0–6). Next: attach a real service + wire a read-only DB MCP |
| ↳ *ADK variant* (`...-google-adk`) | Google ADK (Sequential/Parallel/Loop agents) | Build plan drafted — assembling the typed toolset (read-only first) |
| local-llmstxt-server | Node/TS (Fastify + Vite/React) | Deciding on a docs-split refactor |
| meta-project-manager | Markdown orchestration convention | Onboarding its first managed project |

> Full live index, including incubator/dormant/archive, in [`PROJECTS.md`](./PROJECTS.md).

---

## How it works

Projects move through **tiers** by lifecycle. Real files live once in `repos/`;
the tier folders are just Windows directory junctions pointing at them, so moving
a project between tiers is an instant metadata-only `mv` — it never copies
`node_modules` or `.venv`.

```text
ai-workspace/
├── repos/         # CANONICAL storage — real project files live here
├── incubator/     # ephemeral experiments (real folders)
├── active/    →   # junctions → repos/  · touched < 30 days
├── dormant/   →   # junctions → repos/  · paused; resume blocker named
└── archive/   →   # junctions → repos/  · done, read-only
```

**Routing rule of thumb:**
- Unsure if it has a future → `incubator/`
- Real project → `repos/<name>/`, junctioned into `active/`
- Pausing → `mv active/<name> dormant/` (and name the resume blocker)
- Done/dead → `mv */<name> archive/`

### Two files per project
- **`CLAUDE.md`** — stable identity: what it is, stack, run/test commands, gotchas.
- **`CONTEXT.md`** — a rolling *snapshot of now*: Completed / Current State / Next Step.
  Not a log — git history is the changelog.

### Git boundaries
- Root is local-only as a *workspace*; this repo publishes the **management docs only**.
- Each project in `repos/<name>/` is its own repo with its own remote.

---

## Tooling (slash commands)

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a new project: `repos/<name>/`, junction into `active/`, copy templates, `git init`, add a `PROJECTS.md` row |
| `/promote <name>` | Graduate an incubator project to `active/` |
| `/triage` | Survey `active/` + `dormant/`, flag stale / bloated / drifted `CONTEXT.md` files |
| `/dashboard` | One-screen status across all tiers |

---

## Repo layout

```text
CLAUDE.md            # Agent operating manual (rules & invariants)
HANDBOOK.md          # Human guide: workflows, command cheatsheet, glossary
PROJECTS.md          # Live index of every project + current focus
CLAUDE.template.md   # Per-project stable-identity stencil
CONTEXT.template.md  # Per-project session-handoff stencil
.claude/commands/    # Workspace slash commands
```
