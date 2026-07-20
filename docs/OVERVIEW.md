# Gravity — System Overview & Coverage

> The developer-professional view of the whole system, in one read.
> Current as of **gravity v2.5.1 + unreleased** (2026-07). Korean edition: `OVERVIEW.ko.md`.
> Deep dives: `CLAUDE.md` (the agent contract) · `HANDBOOK.md` (workflows) · `.claude/scenarios/README.md` (checker reference).

---

## 1. What gravity is

Gravity is a **methodology plus a mechanical toolchain** for running many software projects with AI coding agents — across sessions, machines, and heterogeneous models (Claude, Codex, whatever comes next). It attacks exactly one failure mode:

> **Knowledge loss between sessions.** Agents have no memory; humans forget; chats evaporate. Anything that must survive — intent, rules, state, provenance, proof — must live in files with a designated owner, or it is gone.

Everything in the system derives from that: the docs are the persistence layer, the commands are rituals that keep the docs honest, and the checkers are mechanical walls that catch lying docs. Gravity is deliberately **not** a project-management suite — see §10.

## 2. Design principles

1. **One concern, one home.** Every fact has exactly one owning document; everyone else links to it. Restating is how two copies drift into two different "truths."
2. **Docs change at different rates.** *Why* (rarely) · *how* (on refactors) · *what/next* (per slice) · *now* (per session). A doc that mixes rates rots at the speed of its fastest content.
3. **Facts by script, judgment by agent.** Deterministic scripts scan/verify/build; agents interpret and decide. The boundary is never blurred.
4. **Mechanical walls over prose promises.** "Did the agent do it right, or just say it did?" Every claim an agent can make — indexes wired, spec enforced, rollback proven, sheet routed — has a checker that can call it a lie.
5. **Evidence over invention.** Unknowns are written as visible `OPEN: awaiting …`, never plausibly filled. No repro → no fix. No deck/code evidence → no schema.
6. **Ceremony is opt-in.** Two docs are mandatory; everything else is *recognized when present, never mandated*. Rituals that don't pay for themselves are drift, not discipline.
7. **Recipes shrink, walls grow.** As models improve, step-by-step procedure text should get shorter while the checker codebase gets larger. (Trajectory since v2.1 confirms: prose → scripts.)

## 3. The workspace layer

```
ai-workspace/            # skeleton repo (deny-all .gitignore; whitelist IS the portable skeleton)
├── CLAUDE.md            # agent operating manual — auto-loads; word-budget walled (MANUAL_BLOAT)
├── docs/                # human read-docs (this file, HANDBOOK, INTRO, MISSION, intake sheets)
├── templates/           # 16 stencils — copied into projects, never auto-loaded
├── .claude/commands/    # 20 slash commands (lazy: loaded only on invocation)
├── .claude/scenarios/   # the verification harness (check.py + golden fixtures)
├── repos/               # canonical project storage — each its own independent git repo
└── active/ stable/ dormant/ archive/   # tier folders: junctions only, never real files
```

**Lifecycle** reads *being worked · works · paused · over*: `/init-project` → `active/`; `/ship` → `stable/` (Next Step becomes a *reactivation trigger*; staleness-exempt — silence is success); pause → `dormant/` (must name a *resume blocker*); `/retire` → archive or delete. Tier moves are junction `mv`s — instant, and transparent to git. `PROJECTS.md` is the live index, **local-only** (it names private projects; the skeleton ships a sanitized sample).

## 4. The per-project doc layer

**Two-doc minimum (mandatory):**

| Doc | Question | Cadence |
|---|---|---|
| `CLAUDE.md` | *how* — identity, stack, run/test, conventions, the Doc-Map router | on refactors |
| `CONTEXT.md` | *now* — Completed (1–2 sessions) · Current State · one Next Step | every session; pruned (~80 lines) |

**Four-doc pipeline (for projects with a real arc):** add `MISSION.html` (*why* — north star, principles, non-goals; what `/triage` checks drift against) and `IMPLEMENTATION_PLAN.md` (*what/next* — domain status spine, slice queue with exactly one slice in `now`, locked decisions, the gate).

**`.gravity/` (for projects that outgrow a flat root):** everything except the two auto-loaders moves under the dot, grouped **by subject domain, not doc-type**. Each domain folder holds whichever of the kinds it needs:

| Kind | Role |
|---|---|
| `SPEC.md` | the **agent contract**: a generative *Minimal Shape* + *Rules* where **every rule carries an enforcement tag** (`[lint]`/`[type]`/`[test:name]`/`[review]`/`[—]`) naming the wall that catches violations — the contract never lies about which rules are real walls vs judgment. Behavioral domains add a `given/when/then` **Behavioral Contract**, each line bound to a named test. |
| `ARCHITECTURE.html` | the human deep-dive (rationale), when it outgrows a file map |
| `PLAN.*.md` | one slice's intent: Goal · Scenario (`given/when/then`) · Slice · Verification. **Bugs enter here as *currently-false* scenarios** (the repro), and their fix must leave the regression test that graduates the scenario into the SPEC. |
| `given/` + `MANIFEST.md` | received domain knowledge (§5) |

**There is no domain registry file** — the directory *is* the registry, split across four rate-of-change owners: existence (the folders) · routing (root CLAUDE.md Doc Map + read-first table) · why (MISSION row) · status (PLAN spine). `check.py consistency` fails any domain missing from any owner. **The protocol card** (`.gravity/GRAVITY.md`, verbatim template copy, version-stamped) makes each repo self-describing when opened without the workspace.

**Optional, recognized-when-present:** `DESIGN.md` (app visual contract) · `RUNBOOK.md` (ops — the "2am test") · `docs/walkthroughs/` (dated, append-only *after*-records: what shipped + proof) · `AGENTS.md` (Codex shim).

## 5. The evidence layer — two doors in

Both doors hold **received** material (never decided truth) and **route out** rather than accumulate:

| | Intake (reported claims) | Given (handed-in knowledge) |
|---|---|---|
| Input | user/QA bug & issue reports | data dictionaries, business rules, vendor docs, org context |
| Landing | `docs/intake/<date>.md`, one dated sheet per batch, reports **verbatim** | `.gravity/inbox/` — git-ignored drop zone (nothing commits before triage decides privacy) |
| Ritual | `/intake`: six required facts per item (elicited or `OPEN:`), triage trio (real? → domain → bug/feature/doc-drift), dedupe to **root causes** | `/given`: one confirmed routing table → `.gravity/<domain>/given/` with provenance rows (source · received · version · **fidelity** · privacy) |
| Hard rule | **no repro, no slice**; bugs are never a domain | **quarry, not contract** — cite, never restate; disputes resolve against `raw/`, not renderings |
| Wall | `check.py intake` | `check.py given` |

The **maintenance loop** runs door-to-door: report → intake sheet → bug-intake slice PLAN (currently-false scenario) → `/patch-slice` (mechanical walls: anchor, snapshot, bare-gated verify with N=3 → forced four-proof rollback) → regression test graduates the scenario into the SPEC. Bug fixes are the fastest source of honest contract lines.

## 6. The command surface (20)

Commands are **lazy** — loaded only on invocation; the auto-load cost is CLAUDE.md alone (word-budget walled). Destructive commands (`/retire`, `/cut-release`, `/ship`) are `disable-model-invocation` — human-invoked only; self-selectable commands carry **trigger fences** ("when NOT to reach for this").

| Group | Commands |
|---|---|
| Lifecycle | `/init-project` · `/ship` · `/retire` |
| Doc system | `/adopt-gravity` · `/sync-gravity` · `/new-domain` · `/new-spec` · `/excavate` (brownfield: archaeology before authorship — cited Boundary Map, unknowns stay `OPEN:`) |
| Evidence & elicitation | `/interview` (head → docs, strawman-first) · `/intake` (reports) · `/given` (knowledge) · `/mission` (re-orient, read-only) |
| Maintenance | `/patch-slice` (script-walled patch loop) |
| Release | `/cut-release` (Change Order: confirmed bump from `[Unreleased]` evidence, green gate required, stops before push) |
| Survey & views | `/triage` (weekly drift report; mechanical scan) · `/dashboard` / `/open-dashboard` · `/observatory` (one project, one page — overview · domains · seams · spec health · 3D, scanned live from the docs) · `/open-mission` / `/open-architecture` |

## 7. Verification harness & coverage

`check.py` (~1,200 lines) + `scan_workspace.py` + `patch_slice.py` are the walls. One checker, many callers — the same functions run on golden fixtures (scenarios) and live repos (`/triage`).

| Subcommand | Guards | Key findings |
|---|---|---|
| `consistency` | the four-owner domain registry never lies | `UNDERWIRED` (FAIL) · `PROTOCOL_STALE` |
| `spec` | enforcement tags stay true over time | `GATE_DEAD` · `TAG_DEAD` · `SPEC_UNFILLED` (FAIL) + per-domain tag census (walls vs `[review]`) |
| `workspace` | tier/index/adoption drift; the manual's own size | `MULTI_TIER` (FAIL) · `MANUAL_BLOAT` |
| `intake` | sheet honesty | `INTAKE_UNROUTED` (FAIL on a lying ✓ sheet) · `INTAKE_DEAD_ROUTE` |
| `given` | inbox routed, provenance present, manifests truthful | `GIVEN_GHOST_ROW` (FAIL) · `INBOX_UNROUTED` |
| `scenario` | a command's structural postconditions on a golden fixture | per `expect.json` |
| `selftest` | **the testers themselves**: every fixture clean, every checker catches its seeded drifts, and `patch_slice.py` driven end-to-end through green *and* red (forced rollback restoring git-ignored state byte-identical) | `SELFTEST PASSED/FAILED` |

**Coverage map (honest):** golden scenarios exist for `/new-domain`, `/new-spec`, `/excavate`, `/ship`, `/patch-slice`; in-code selftest halves cover `spec`, `workspace`, `intake`, `given`, and the patch-loop script. **Not yet scenario-covered:** `/init-project`, `/adopt-gravity`, `/sync-gravity`, `/cut-release`, `/interview`, `/retire`, the view commands. The agent's *judgment* steps are untestable by design — only structural postconditions are asserted. There is **no CI**: all walls run on demand (see §10); selftest is the run-after-editing-the-harness gate.

## 8. Versioning & upgrades

Gravity is SemVer'd **as a convention system**: major = a rule projects depend on breaks · minor = new template/command/additive rule · patch = wording. Version lives in `VERSION` + the git tag, never prose. Each project records its adopted version (`> gravity: vX.Y` router stamp + the protocol card's stamp); `/sync-gravity` upgrades mechanically (card re-copy + stamp) and reports judgment deltas as a quoted checklist, **never auto-migrating**. `/cut-release` is the same Change Order for gravity itself and for projects.

## 9. The feedback loop (a worked week)

Field report → `docs/intake/` sheet (verbatim, six facts) → fix → **regression wall** → often a new rule. Real examples, July 2026: a coding agent over-triggered `/intake` on a code-analysis task → trigger fence + the fences-on-birth rule (v2.5.1); selftest was red on Linux (`__pycache__` dirt) → fixed + recorded as intake item I1; the manual outgrew its context budget → §7 compressed to a pointer table + `MANUAL_BLOAT` wall — which then correctly fired on the *next* feature's first draft. The system governs its own growth.

## 10. Scope fence — what gravity is not

- **Not sprints/boards/estimates/metrics, and not CI** — gravity covers a lifecycle phase only where *knowledge loss between sessions* is the failure mode. Pipelines and process management are other tools' jobs.
- **Not an umbrella repo** — the workspace tracks only its skeleton; every project is its own repo with its own remote.
- **Not a capability crutch** — the walls target failure modes frontier models still have (session amnesia, momentum errors, convincing-but-wrong claims, ceremony temptation); the recipes are the part expected to shrink.
- **Not mandatory ceremony** — a CLI script lives happily on two docs forever.

---

*Cross-references: templates inventory — workspace `CLAUDE.md` §1 · rituals and rules — §6 · finding tables — `.claude/scenarios/README.md` · glossary and workflows — `HANDBOOK.md`.*
