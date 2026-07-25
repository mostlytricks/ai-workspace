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

## The portable walls (`lib/`)

- `scan_project.py` — the one scanner for a project's gravity docs (domains, spine, SPEC census,
  scenarios, queue, tracks, walkthroughs, context, preflight packets). Facts only, stdlib only;
  every instrument and checker reads through it so the docs are parsed exactly one way.
- `run_gate.py` — runs a domain SPEC's extracted gate inside the project and propagates its exit
  code (exit 2 = an honest "no gate to run" refusal, never a pass).

Both run off-workspace with a project path (workspace alias resolution is manager-side sugar).
