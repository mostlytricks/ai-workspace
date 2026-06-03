# Projects Index

Source of truth for what exists in this workspace and which tier each project lives in. Update this whenever a project moves between `active/`, `dormant/`, or `archive/`, or when its focus/blocker changes meaningfully. Real project files live in `repos/<name>/`; tier folders hold directory junctions pointing into `repos/`.

**Format per row:** `name | stack | last-touched (YYYY-MM-DD) | current focus or resume blocker`

---

## active/

_Touched within ~30 days. Each has CLAUDE.md + CONTEXT.md. The "focus" column should be the same as the project's CONTEXT.md → Next Step, in one line._

- antigravity-based-project-plan-methodology | Node/TS CLI (commander, tsx)        | 2026-05-24 | add unit tests for the Task-Lock Safeguard in src/commands/task.ts; then commit untracked CONTEXT.md
- antigravity--pptx-template-manager          | Python (google-adk + python-pptx)   | 2026-06-03 | just activated; make the initial commit (13 untracked files, .gitignore already correct) after a `test_generation.py` smoke run
- claude-interactive-panel-20260516           | Node/TS workspaces (server+client)  | 2026-05-21 | verify + commit in-flight server/src/sections.ts related-topics change (+ fill CLAUDE.md, commit CONTEXT.md)
- local-llmstxt-server                        | Node/TS (Fastify + Vite/React)      | 2026-05-30 | review `modifycation-plan--docs-split.md` and decide execute / defer / close
- meta-project-manager                        | Markdown convention (orchestration) | 2026-05-26 | onboard first managed project; revise templates from real use
- multi-system-maintenance-agent-system       | Claude Code subagents + git + JSONL | 2026-05-31 | Phases 0-6 done (build complete, standalone). Next: attach a real service + wire read-only DB MCP
- agent-view-desktop                          | Electron 33 + Vite + React 18 + TS  | 2026-06-03 | multi-Claude orchestrator: Phase 6→10 arc pushed to origin (github.com/mostlytricks/agent-view-desktop, feat/orchestration @ 51e7a17) — session mgr + tool policy, ~/.flux plugin, transcript viewer, flux tools + shared memory, supervisor spawn/await workers, Overview dashboard + handoff, memory persistence + theme system. Phase 11 (Tier 3 resume = "Take control ▶" fork-resumes an external transcript live) built on top, UNCOMMITTED. Next: live smoke test, then commit. See IMPLEMENTATION_PLAN.md

## incubator/

_Experimental. Real folders OR junctions into `repos/` if intended to graduate. No CLAUDE.md/CONTEXT.md overhead. Promote with `/promote <name>` when validated._

- ai-workspace-config         | unknown                           | 2026-05-24 | unknown — clarify intent or archive
- coding-agent                | Python (claude-agent-sdk)         | 2026-05-30 | first run on a real task in repos/local-llmstxt-server; tune system prompt
- pipeline-demo               | Claude Code subagents + git + JSONL | 2026-05-31 | demo/target service for multi-system-maintenance-agent-system; build read-only loop (Phase 1)
- project-analysis-agent      | Python (claude-agent-sdk)         | 2026-05-30 | first run on repos/local-llmstxt-server to bootstrap its CLAUDE.md
- review-agent                | Python (claude-agent-sdk)         | 2026-05-30 | first run on a small diff; calibrate severity thresholds

## dormant/

_Paused but alive. The "resume blocker" must be concrete — what specifically needs to be true before you'd pick this back up. If you can't name a blocker, this project belongs in archive/._

- _example_         | _Node/Express_        | _paused 2026-02-10_ | _resume blocker: target API v2 not yet released_

## archive/

_Done, abandoned, or superseded. Read-only. Listed here only so you don't accidentally recreate something that already exists._

- agent-view        | _empty scaffold_      | archived 2026-05-30   | never had content; name is free to reuse but flagging so we don't recreate accidentally

---

## Not surfaced in a tier (intentional)

_Folders that live in `repos/` but have no workspace-tier junction because they're owned by another project here. Listed so triage doesn't keep flagging them as orphans._

- pims-api, pims-web | owned by `meta-project-manager` (junctioned into `projects/personal-intelligence-manage-system/services/`)

---

<!--
Maintenance notes:
- The /triage slash command (run from workspace root) can auto-summarize active/ and dormant/ by reading each subdir's CONTEXT.md. Use it weekly and reconcile any drift here.
- If a row hasn't been touched in 30+ days under active/, either update its CONTEXT.md or demote to dormant/.
- If a dormant row's resume blocker has resolved, promote back to active/ and refresh CONTEXT.md.
-->
