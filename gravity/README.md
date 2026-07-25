# gravity/ — the protocol distribution

Everything a project **adopts** lives in this directory; everything that *manages* projects
(tiers, junctions, `PROJECTS.md`, the dashboard) stays outside it with the workspace manager.
The split rule: if a cloned project repo could need it, it belongs here; if only this machine's
portfolio needs it, it doesn't.

```
gravity/
├── VERSION               # the protocol's SemVer — the version projects stamp (`> gravity: vX.Y`)
├── CHANGELOG.md          # how the protocol's rules/templates/commands evolved (major = a rule projects depend on breaks)
├── GRAVITY-PROTOCOL.md   # the protocol card → copied VERBATIM to <project>/.gravity/GRAVITY.md at adoption
├── templates/            # the per-project / per-domain stencils (catalog below)
└── lib/                  # the portable walls: scan_project.py · run_gate.py
```

**Versioned apart from the manager.** Manager-only changes (tier rules, dashboard, workspace
commands) never bump `VERSION`; a bump means something a *project* depends on changed, so
`PROTOCOL_STALE` warnings stay honest. Cut releases with `/cut-release` (no argument).

## The stencil catalog (`templates/`)

Copied, never auto-loaded. Each stencil also self-describes in its header comment.

| Stencil | What it seeds |
|---|---|
| `CLAUDE.template.md` | Per-project stable-identity file (stack, run/test, conventions, gotchas). |
| `AGENTS.template.md` | Codex-compatible shim; points to CLAUDE.md as canonical. |
| `CONTEXT.template.md` | Session-handoff snapshot: Completed / Current State / Next Step. |
| `MISSION.template.html` | The "why" doc — north star, principles, non-goals (four-doc pipeline, CLAUDE.md §6). |
| `IMPLEMENTATION_PLAN.template.md` | The "what/next" doc. Two shapes: phase roadmap (arc projects) or slice queue (growing projects); optional **Tracks** section = the direction axis. Header carries the **work-layer law**. |
| `PLAN.template.md` | Per-domain / per-slice intent — Goal + given/when/then Scenario + Slice + Verification; seeded by `/new-domain` and `/interview`. |
| `ARCHITECTURE.template.html` | "How it's built" overview (optional fifth doc); also seeds per-domain deep-dives. |
| `SPEC.template.md` | The per-domain **change contract** — generative (Minimal Shape + Generate loop) and limiting (enforcement-tagged Rules). Carries the first-class INTEGRATION VARIANT (Boundary Map + Change Order) for the cross-service `integration` domain. |
| `GRAVITY.template.md` | The **thin fenced router block** — the only thing gravity writes into root harness files (CLAUDE.md, AGENTS.md, …); machine-managed between `<!-- gravity:router -->` fences. |
| `ROUTER.template.md` | The full in-`.gravity/` router → `.gravity/ROUTER.md`: Doc Map + read-first table + the is-it-a-domain gate. |
| `WALKTHROUGH.template.md` | Per-change "what got done + proof" record (append-only, dated). |
| `INTAKE.template.md` | Per-batch bug/issue intake sheet — verbatim reports + required-facts checklist → `docs/intake/<date>.md`; seeded by `/intake`. |
| `GIVEN-MANIFEST.template.md` | Provenance sheet for the given layer — received domain knowledge routed from `.gravity/inbox/` by `/given`. |
| `DB-EVIDENCE.template.md` | Brownfield DB evidence pack: checklist + manifest of metadata CSVs a DBA exports offline; consumed by `/excavate`. |
| `DESIGN.template.md` | Running-app UI design-system contract (UI projects only). |
| `RUNBOOK.template.md` | Operations doc — deploy · envs · health · rollback (the "2am test"; deploying projects only). |

## The portable instruments (`lib/`)

Everything here is **stdlib-only and path-relative by rule**, because it doesn't stay here:
`python .claude/scripts/install_lib.py <project>` copies this whole directory into
`<project>/.gravity/lib/` with a `VERSION` stamp. The protocol card makes a repo
self-*describing*; the lib makes it self-*rendering* — a clone that has never seen this
workspace can scan, check and render itself.

- `scan_project.py` — the one scanner for a project's gravity docs (domains, spine, SPEC census,
  scenarios, queue, tracks, walkthroughs, context, preflight packets). Facts only, stdlib only;
  every instrument and checker reads through it so the docs are parsed exactly one way.
- `check_project.py` — the project-scoped structural checks (`consistency`, `spec`, `intake`,
  `given`) plus a CLI. The workspace-scoped half (tiers, `PROJECTS.md`, the golden-scenario
  harness) stays in `.claude/scenarios/check.py`, which re-exports this one.
- `generate_observatory.py` — the seven-tab page, written to `<project>/.gravity/observatory/`.
  `generate_cosmos.py` (Orbit 3D + the five-palette `THEMES` family) and `generate_boundary.py`
  (the seam graph) are its renderer modules; each keeps a debug CLI.
- `project_arg.py` — which project (path first, workspace alias only as sugar) and where output
  goes (the self-ignoring `observatory/` folder).
- `run_gate.py` — runs a domain SPEC's extracted gate inside the project and propagates its exit
  code (exit 2 = an honest "no gate to run" refusal, never a pass).

Every one of them takes a project **path**; the workspace's alias resolution
(`.claude/scripts/resolve_project.py`) is manager-side sugar reached only when present. Installed
in a project, they need no argument at all — the lib's own location names its project.

**Never hand-edit an installed copy.** It's verbatim, like the card: fix it here and re-install
(`/sync-gravity`). `check_project` WARNs `LIB_MISSING` / `LIB_STALE` when a project has no lib or
an older one than the distribution.
