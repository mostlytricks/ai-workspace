# Changelog — gravity (the ai-workspace system)

Notable changes to **gravity itself** — the rules in `CLAUDE.md`, the `*.template.*`
stencils, and the `.claude/` commands/scripts. This versions the **methodology**, not
the projects it manages (each project carries its own `CHANGELOG.md`).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); gravity adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), read for a *convention system*:

- **major** — a rule projects depend on **breaks**: a renamed/moved convention, a changed
  doc-ownership boundary, a restructure an existing project would now violate. (Example:
  flat `SPEC.<domain>.md` → `.gravity/<domain>/SPEC.md` was a breaking restructure.)
- **minor** — a new template, command, optional doc, or additive rule. Existing projects stay valid.
- **patch** — clarifications, tighter wording, typo/format fixes; no behavioral change to the rules.

The version lives in the **git tag** (`vX.Y.Z`) and the `VERSION` file — never in prose.
A project records the gravity version it was built on via the `> gravity: vX.Y` line in its
root-`CLAUDE.md` router (seeded from `GRAVITY.template.md`), so drift is detectable.

## [Unreleased]

_Nothing yet._

## [1.2.0] - 2026-07-02

### Added
- **Golden-scenario harness for gravity's own commands** (`.claude/scenarios/`) — gravity now tests the commands that *claim* to wire things up. A scenario is a triple: `(command, golden-input fixture, deterministic structural assertions)`. The agent step (running the command) stays manual; the assertion is a script. First scenario: **`/new-domain`** — copies a clean one-domain fixture, the agent adds a second domain, and the checker proves it's wired into all four registry indexes with nothing orphaned (catches the half-wired/orphaned-domain bug).
- **`check.py` — structural-invariant checker** (`.claude/scenarios/check.py`) — `check_gravity_consistency(project_dir)` reads the four registry owners (Doc Map, router table, MISSION "system in N domains" row, `IMPLEMENTATION_PLAN.md` status spine) and reports `UNDERWIRED` domains and `ORPHAN_ROUTE` rows via heuristic slug-match. CLI: `consistency` (one project), `scenario` (assert a golden-scenario's postconditions), `selftest` (proves the checker against a good + deliberately-broken fixture).
- **`/triage` runs `check.py`** — the `.gravity/` registry-drift flag is now mechanical instead of by-hand: triage shells out to `check.py consistency` per `.gravity/` project, so triage and the `/new-domain` scenario share one checker and agree by construction.
- **Project aliases — `resolve_project.py`** (`.claude/scripts/`) — a short token resolves to a canonical project with **no central registry** (PROJECTS.md stays the workspace index, not an alias table). The alias is a per-project identity fact, so a project **declares its own** via a `> alias: <slug>` line in its root `CLAUDE.md` (seeded from `CLAUDE.template.md`, next to the `> gravity:` stamp) — authoritative and owned per project. Resolution order: exact name → **declared alias** → unique acronym as a convenience (`amos` = architecture-memory-os, short ≤2-char tail segments like `os` kept whole) → unique substring (`compass`), refusing to guess when ambiguous. So a project gets a free derived alias immediately and can *claim* an intentional one. `check.py --project <alias>` resolves them; other project-taking commands can adopt the same helper. First declared alias: **`amos`** (architecture-memory-os).

## [1.1.0] - 2026-06-27

### Added
- **Dashboard gravity-adoption chips** — `generate_dashboard.py` reads each project's adoption layers **live from disk** (the `> gravity: vX.Y` stamp, `.gravity/` vs flat, a `CHANGELOG`, the `AGENTS.md` shim) and renders them as chips on every project card, with a legend. `PROJECTS.md` carries a matching at-a-glance **Gravity adoption** snapshot matrix.

## [1.0.0] - 2026-06-27

First versioned baseline of gravity — the system as it stands after the `.gravity/`
restructure and in active use across `repos/`. Captured retroactively; full pre-1.0
evolution is in `git log`.

### Added
- **Workspace operating manual** (`CLAUDE.md`) — tier model (`repos/` canonical + `active/`/`dormant/`/`archive/` junctions, `incubator/` real), git boundaries, `.venv` isolation, the multi-service contract pattern, and the per-project doc model.
- **Doc model** — two mandatory auto-loaders (`CLAUDE.md` identity / `CONTEXT.md` now), the opt-in four-doc pipeline (+`MISSION.html` why / `IMPLEMENTATION_PLAN.md` what-next), optional `ARCHITECTURE.html`, `DESIGN.md`, and `WALKTHROUGH.md`. One concern, one owner.
- **`.gravity/` directory** — domain-faceted docs; the directory is the registry (no registry file); per-domain `SPEC.md` (agent contract, enforcement-tagged) + `ARCHITECTURE.html` (human deep-dive). `knowledge-viewer` is the worked example.
- **Integration as a first-class SPEC shape** — `SPEC.template.md` flexes into a boundary contract (Boundary Map + Change Order) for the cross-service `integration` domain.
- **Stencils** — `CLAUDE` / `CONTEXT` / `AGENTS` / `MISSION` / `IMPLEMENTATION_PLAN` / `ARCHITECTURE` / `SPEC` / `WALKTHROUGH` / `DESIGN` / `GRAVITY` templates, all under **`templates/`**.
- **Self-applied root layout** — gravity follows its own "few files at root" rule: the root keeps only the auto-loader (`CLAUDE.md`), the Codex shim (`AGENTS.md`), `README.md`, and the live indexes (`PROJECTS.md` / `VERSION` / `CHANGELOG.md`); stencils live in **`templates/`** and human/browser read-docs (`HANDBOOK.md`, `MISSION.html`, shared `DESIGN.docs.md`) in **`docs/`**. The `.gitignore` whitelists both directories wholesale.
- **Commands** — `/init-project`, `/promote`, `/retire`, `/adopt-gravity`, `/new-domain`, `/new-spec`, `/cut-release`, `/triage`, `/mission`, `/dashboard`, `/open-dashboard`, `/open-mission`, `/open-architecture`; helper scripts (`link_project`, `new_project`, `retire_project`).
- **Self-versioning** — this `CHANGELOG.md`, the `VERSION` file, and the `> gravity: vX.Y` project stamp; the root git repo tracks only the portable skeleton via the deny-all/whitelist `.gitignore`.
- **Codex interop** — `AGENTS.md` (workspace) + `AGENTS.template.md` (per-project), pure pointers to the canonical `CLAUDE.md` (no rule duplication). Rolled out: `/init-project` + `/promote` + `/adopt-gravity` seed the shim, all current `active/` projects backfilled, `/triage` flags any project missing it.

[Unreleased]: https://github.com/mostlytricks/ai-workspace/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/mostlytricks/ai-workspace/releases/tag/v1.2.0
[1.1.0]: https://github.com/mostlytricks/ai-workspace/releases/tag/v1.1.0
[1.0.0]: https://github.com/mostlytricks/ai-workspace/releases/tag/v1.0.0
