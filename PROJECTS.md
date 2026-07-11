# Projects Index

Source of truth for what exists in this workspace and which tier each project lives in. Update this whenever a project moves between `active/`, `dormant/`, or `archive/`, or when its focus/blocker changes meaningfully. Real project files live in `repos/<name>/`; tier folders hold directory junctions pointing into `repos/`.

**Format per row:** `name | stack | last-touched (YYYY-MM-DD) | current focus or resume blocker`

---

## active/

_Touched within ~30 days. Each has CLAUDE.md + CONTEXT.md. The "focus" column should be the same as the project's CONTEXT.md → Next Step, in one line._

- antigravity--pptx-template-manager          | Python (google-adk + python-pptx)   | 2026-06-07 | just activated; make the initial commit (13 untracked files, .gitignore already correct) after a `test_generation.py` smoke run
- knowledge-viewer                            | Node/TS workspaces (server+client)  | 2026-07-01 | local markdown/HTML knowledge viewer (wikilink graph + backlinks + ⌘K + AI chat); on the full doc pipeline, real telos = PKM → collect reports → surface **issues & risks** (graph = risk surface). **Strategy reordered to search-first:** Phase 2.5 (hybrid retrieval) now lands before Phase 2 (importance/status encoding) so ~1000 docs are findable before the reports→findings→triage arc. Phase 2.5 half-built + uncommitted: `server/src/search/{corpus,lexical,semantic}.ts` written (BM25 + OpenAI-compatible embeddings) but the merge layer + wiring are missing. Not coupled to AMOS (deliberate). Next: add `hybrid.ts`, wire `/api/search` + the chat tool + ⌘K, gate, commit
- local-llmstxt-server _(alias `nova`)_       | Node/TS (Fastify + Vite/React)      | 2026-07-06 | intranet `llms.txt` control plane. Phases 1-8 + Track R + Track M (M6 clean `/docs/` URLs, M7 reader+review UI) done; M3 external-mirror pilot validated in sandbox (`code.claude.com` 163/163). Phase 8 Search re-built (API `/api/search` + `docs-import search`; API/CLI only, not yet in UI). Next: run M3 on the real intranet host + offline acceptance test, then M4 (first internal pptx/excel manual).
- agent-view-desktop                          | Electron 33 + Vite + React 18 + TS  | 2026-06-27 | `.gravity` adopted v1.0; root `CLAUDE.md` is now the router and heavy docs live under `.gravity/`. Existing Phase 12/13 runtime-adapter + version-matrix work remains uncommitted. Next: run `npm run typecheck` + `npm run build`, then the Gate 0 live smoke test before committing or starting Phase 14.
- api-server-managing-agent                  | Knowledge base + Claude Code skill (targets Spring Boot + Oracle) | 2026-06-04 | full doc set written (MISSION/CLAUDE/PLAN/CONTEXT) — method-first, read-only, two-layer knowledge seam. Next: Phase 1 — knowledge model + templates + a sample Spring Boot + Oracle schema (resolve sample-source + store-format open Qs first)
- architecture-memory-os                      | TS/Node MCP core (SQLite-indexed Markdown graph) | 2026-07-04 | AMOS — institutional architecture-memory layer; docs on `.gravity/` (root `CLAUDE.md` is the router). **Phases 1–7 built & green (typecheck + 54/54 vitest, 2026-07-01)** incl. MCP server (8 tools), directed `impact`, and the PMO change/risk governance report; 13-node seed corpus. 3 early pre-`.gravity` commits on `master`; the whole current slice (`.gravity/` move + Phase 6/7 + new tests) is uncommitted, no remote. Next: commit the slice + add a remote, then scope the sizing aid vs multi-format ingest
- my-personal-accountant | tbd | 2026-06-20 | scaffolded, fill in CLAUDE.md
- lecture-note | self-contained HTML lecture decks | 2026-06-28 | initialized: portable 16:9 slide-deck project with embedded CSS/JS template (`templates/lecture.template.html`), `lectures/` target folder, README, and project docs. Next: choose the general design theme, then tune template tokens before first real lecture
- capability-compass                           | tbd (Python + embeddings, prototype) | 2026-06-28 | **engineer capability-intelligence**: map each engineer as a capability vector (skills/projects/HR/git signals) so leaders answer "who do we need for the next big bet?" (frontier model, OLTP→AI transition) from evidence. First surface = a visual vector-space capability map. Next: decide the vector-space spine (seeded taxonomy vs LLM-embedded skills), then seed 5-10 fake engineers + render the first map
- astra                                        | Python (FastAPI + uvicorn) skill registry | 2026-07-05 | private Agent-Skill registry/server (immutable versions, publish/curate/yank, version-history view). Ships orbit's skills to the GitHub-less work machine. Remote live at `github.com/mostlytricks/astra`, tag `v0.1.0`; `[Unreleased]` holds a minor's worth of work → **cut v0.2.0** when ready. Next: adoption analytics (download counts) — needs a write-path counter on the read-only registry
- orbit                                        | Python (stdlib) Claude Code skills   | 2026-07-06 | home-machine file-intelligence workbench: 7 skills (filing chain `file-scout`→`file-triage`→`file-find`→`area-architect`→`orbit-dashboard` + `locate` waypoint nav + `process-architect`), all walled by mechanical fixture gates. Designs skills that astra ships to work. `main` at `v0.4.1`. Next: review+merge **PR #2** (`file-find` + locate seam) → cut **v0.5.0**
- pulsar                                       | Python (stdlib) Claude Code skills   | 2026-07-05 | work-machine HR/ops assistant (astra-shaped from birth; design instance carries no real data). Day-one slice done: hours-ledger ingest + 52h overtime-check calculator + fixture gate (green). Next: user picks slice 2 — `notice-digest` or `welfare-guide` (needs source-system description, an `/interview pulsar <feature>` shape)
- forge-world _(alias `forge`)_                | JS (Vite 8 + three r185)             | 2026-07-11 | game-feel **semiconductor stack-up simulator** (educational: slate = process layer, etch/deposit). PR #1 merged; **Phases 1–6 ✓** on restarted branch `claude/3d-block-stacking-viz-rc0kxb`: process re-theme, pattern editor (custom types + stack@2 JSON), soft ordering audit, ⚗ recipe presets, and the `add-layer-type` agent skill with Damascene Cu as worked example (remote `mostlytricks/forge-world`; junction/tier wiring pending on the local machine). **v0.1.0 cut 2026-07-11** (commit `c0c0f9c`; tag local-only — remote proxy 403s tag pushes, re-tag after merge). Next: merge the PR + push the tag, then pick next arc — teaching mode · Electron wrapper · grid decision
- agent-terraform                              | Claude Code skills + FastMCP (Python) | 2026-07-06 | spec-driven pipeline turning internal backend APIs into agent serving layers (per-service MCP servers + Agent Skills). PRs #1–#3 merged; `.gravity/` v1.4 with 3 domains (spec · readiness · onboarding). No real service onboarded yet (internal services unreachable remotely). Next: Phase 1 pilot on the work machine — pick a small Python service, then `onboard <name>`

## incubator/

_Experimental. Real folders OR junctions into `repos/` if intended to graduate. No CLAUDE.md/CONTEXT.md overhead. Promote with `/promote <name>` when validated._

- ai-workspace-config         | PowerShell (bootstrap.ps1)        | 2026-05-24 | the **portable workspace shell** — clone on a new PC → `bootstrap.ps1` reads PROJECTS.md, clones each project into `repos/`, recreates tier junctions. This is the mission's "later shape" seed. Next: decide if portability is on the roadmap; if so, /promote it and exercise the bootstrap on a clean checkout

## dormant/

_Paused but alive. The "resume blocker" must be concrete — what specifically needs to be true before you'd pick this back up. If you can't name a blocker, this project belongs in archive/._

- multi-system-maintenance-agent-system      | Claude Code subagents + git + JSONL | paused 2026-07-06 | resume blocker: no real target service + read-only DB (ideally a replica) to attach. Build is complete and standalone (Phases 0-6); nothing to do without a live service to point `.mcp.json` + `db-inspector` at
- antigravity-based-project-plan-methodology | Node/TS CLI (commander, tsx)        | paused 2026-06-03 | resume blocker: no current use for the methodology CLI. Resume when running the lifecycle on a real project (→ cover the untested Task-Lock Safeguard) or publishing it (→ wire dist/ for npx). Feature-complete + clean otherwise
- _example_         | _Node/Express_        | _paused 2026-02-10_ | _resume blocker: target API v2 not yet released_

## archive/

_Done, abandoned, or superseded. Read-only. Listed here only so you don't accidentally recreate something that already exists._

- agent-view        | _empty scaffold_      | archived 2026-05-30   | never had content; name is free to reuse but flagging so we don't recreate accidentally
- multi-system-maintenance-agent-system-google-adk | Python (Google ADK) | archived 2026-06-06 | superseded early ADK variant of multi-system-maintenance-agent-system (just a build plan + Run.py). Kept for reference only; its odd remote (→ ai-workspace.git) is moot now that it's read-only

---

## Gravity adoption

_Where each project sits on the gravity conventions (current system version: root `VERSION`). The **dashboard renders this live from disk** (chips on every card, always accurate); this table is the at-a-glance markdown view — a snapshot reconciled like the tier rows above (run `/triage` if it drifts). **stamp** = the `> gravity: vX.Y` line in `CLAUDE.md` · **docs** = `.gravity/` faceted vs `flat` two-doc · **card** = the `.gravity/GRAVITY.md` protocol-card stamp (`.gravity` projects only; `—` = missing → 📡 in `/triage`; `n/a` for flat projects) · **rel** = a `CHANGELOG.md` (release light-layer) · **codex** = the `AGENTS.md` shim._

| Project | stamp | docs | card | rel | codex |
|---|---|---|---|---|---|
| knowledge-viewer | `v1.0` | `.gravity` | — | ✓ | ✓ |
| architecture-memory-os | `v1.0` | `.gravity` | — | — | ✓ |
| local-llmstxt-server | `v1.0` | `.gravity` | — | ✓ | ✓ |
| lecture-note | — | flat | n/a | — | ✓ |
| capability-compass | `v1.1` | `.gravity` | — | — | ✓ |
| multi-system-maintenance-agent-system | — | flat | n/a | ✓ | ✓ |
| agent-view-desktop | `v1.0` | `.gravity` | — | — | ✓ |
| api-server-managing-agent | — | flat | n/a | — | ✓ |
| antigravity--pptx-template-manager | — | flat | n/a | — | ✓ |
| my-personal-accountant | — | flat | n/a | — | ✓ |
| astra | `v1.4` | flat | n/a | ✓ | ✓ |
| orbit | `v1.4` | `.gravity` | — | — | ✓ |
| pulsar | `v1.4` | flat | n/a | — | ✓ |
| agent-terraform | `v1.4` | `.gravity` | — | — | ✓ |
| forge-world | — | flat | n/a | ✓ | ✓ |
| antigravity-based-project-plan-methodology _(dormant)_ | — | flat | n/a | — | — |

Next adoption moves: decide per **flat** project whether it earns `.gravity` or stays a clean two-doc project with a light stamp; add release light-layer only where a project is ready to cut versions.

---

<!--
Maintenance notes:
- The /triage slash command (run from workspace root) can auto-summarize active/ and dormant/ by reading each subdir's CONTEXT.md. Use it weekly and reconcile any drift here.
- If a row hasn't been touched in 30+ days under active/, either update its CONTEXT.md or demote to dormant/.
- If a dormant row's resume blocker has resolved, promote back to active/ and refresh CONTEXT.md.
-->
