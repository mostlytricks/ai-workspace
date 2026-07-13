# AI Workspace — Agent Operating Manual

Root contract for any coding agent working inside `ai-workspace/`. **Rules and invariants only** — step-by-step workflows for humans live in `docs/HANDBOOK.md`.

Always open the agent at this root, never one level deeper. When a project subdirectory has its own `CLAUDE.md` or `CONTEXT.md`, that local file wins on conflict.

---

## 1. Workspace Map

Gravity eats its own dogfood: the root holds only the auto-loader + shim + live indexes; the **stencils** live in `templates/` and the **read-docs** in `docs/` (so the root doesn't bury what matters — the same "few files at root" rule §6 gives projects).

```text
ai-workspace/
├── CLAUDE.md                       # This file — the operating manual. Auto-loads; the one router.
├── AGENTS.md                       # Codex-compatible shim; points to CLAUDE.md as canonical.
├── README.md                       # Human entry point.
├── PROJECTS.md                     # Live index of all projects across tiers. LOCAL-ONLY (git-ignored — carries private project info).
├── PROJECTS.sample.md              # Sanitized template for PROJECTS.md — the tracked skeleton copy (`cp PROJECTS.sample.md PROJECTS.md` on a fresh workspace).
├── VERSION                         # Gravity system version (SemVer) — paired with a git tag vX.Y.Z (§2).
├── CHANGELOG.md                    # How gravity's own rules/templates/commands evolved (major = a rule projects depend on breaks).
├── .gitignore                      # Deny-all/whitelist: tracks only the portable skeleton (§2).
│
├── docs/                           # Human/browser READ-DOCS (rarely change):
│   ├── INTRO.html                  #   Browser-read introduction to gravity. Start here.
│   ├── OVERVIEW.md / OVERVIEW.ko.md #  Dev-professional system overview + coverage map (EN · KR).
│   ├── HANDBOOK.md                 #   Human-facing guide: workflows, slash commands, glossary.
│   ├── MISSION.html                #   The workspace's own north star — the durable why behind these rules.
│   └── DESIGN.docs.md              #   Shared theme for browser-read project HTML docs (distinct from DESIGN.md — §6).
│
├── templates/                      # Per-project / per-domain STENCILS (copied, never auto-loaded):
│   ├── CLAUDE.template.md          #   Per-project stable-identity stencil.
│   ├── AGENTS.template.md          #   Per-project Codex-compatible shim; points to CLAUDE.md.
│   ├── CONTEXT.template.md         #   Per-project session-handoff stencil.
│   ├── MISSION.template.html       #   Per-project "why" stencil (optional four-doc pipeline, §6).
│   ├── IMPLEMENTATION_PLAN.template.md  # Per-project "what/next" stencil (optional four-doc pipeline, §6). Two shapes: phase roadmap (arc projects) or slice queue (growing projects); optional Tracks section = the cross-domain direction axis.
│   ├── PLAN.template.md            #   Per-domain / per-slice "what/next" stencil — Goal + given/when/then Scenario + Slice + Verification; seeded by /new-domain and /interview (§6).
│   ├── ARCHITECTURE.template.html  #   Per-project "how it's built" stencil (optional fifth doc, §6). Also seeds ARCHITECTURE.<facet>.html deep-dives.
│   ├── SPEC.template.md            #   Per-domain agent-loadable spec stencil — generative (Minimal Shape + Generate loop) and limiting (enforcement-tagged Rules); paired with an ARCHITECTURE facet (optional; §6). Carries a first-class INTEGRATION VARIANT (Boundary Map + Change Order) for the cross-service `integration` domain (§5).
│   ├── DB-EVIDENCE.template.md     #   Brownfield DB evidence pack: checklist + manifest (metadata CSVs a DBA exports offline) → .gravity/integration/structural/db/MANIFEST.md; consumed by /excavate (§5).
│   ├── GRAVITY.template.md         #   Root-CLAUDE.md router block (Doc Map + read-first table + domain gate) for projects adopting .gravity/ (optional; §6).
│   ├── GRAVITY-PROTOCOL.template.md #  Project-embedded protocol card → copied to .gravity/GRAVITY.md when .gravity/ is created, so the repo is self-describing off-workspace (§6).
│   ├── WALKTHROUGH.template.md     #   Per-change "what got done + proof" stencil (optional, append-only; §6).
│   ├── INTAKE.template.md          #   Per-batch bug/issue intake sheet — verbatim reports + required-facts checklist → docs/intake/<date>.md; seeded by /intake, routes out to slice PLANs (§6).
│   ├── GIVEN-MANIFEST.template.md  #   Provenance sheet for the given layer — received domain knowledge under .gravity/given/, routed from .gravity/inbox/ by /given (§6).
│   ├── DESIGN.template.md          #   Per-project running-app UI design-system stencil (optional; §6).
│   └── RUNBOOK.template.md         #   Per-project operations stencil — deploy · envs · health · rollback (optional; §6, the "2am test").
│
├── .claude/commands/               # Workspace-level slash commands.
├── .claude/scripts/                # Helper scripts (link_project.py, new_project.py, retire_project.py).
│
├── repos/                          # CANONICAL storage. Real project files live here.
├── active/                         # Junctions → repos/. Being worked; touched <30 days.
├── stable/                         # Junctions → repos/. Shipped & in use; no active arc. Staleness-exempt; CONTEXT.md names the reactivation trigger.
├── dormant/                        # Junctions → repos/. Paused; CONTEXT.md must name a resume blocker.
└── archive/                        # Junctions → repos/. Done. Read-only.
```

**Routing** (the lifecycle reads: *being worked · works · paused · over*):
- New project or idea → `/init-project <name>` — `repos/<name>/`, junction into `active/<name>`. If the idea dies within days, `/retire <name>` and delete; scaffolding is one command, so there is no cheaper "incubator" stage (that tier was retired in v2.0).
- Shipped and in use, nothing in flight → `/ship <name>` — junction moves to `stable/`; CONTEXT.md's Next Step becomes the **reactivation trigger** ("back to active when X"). Staleness rules don't apply in `stable/` — silence is success, not neglect.
- Reactivate → `mv stable/<name> active/`. Refresh CONTEXT.md with the new arc.
- Pause an active project → `mv active/<name> dormant/`. Update CONTEXT.md's Next Step with the resume blocker (something *blocks* it — that's what distinguishes dormant from stable).
- Resume → `mv dormant/<name> active/`. Refresh CONTEXT.md.
- Done or dead → `/retire <name>` — assess, then **archive** (keep, read-only) or **delete** (permanent). No further edits once archived.

After any transition, update `PROJECTS.md`.

Never create files at the workspace root other than the meta files listed above.

---

## 2. Git Boundaries

- **The root repo tracks only the gravity *skeleton*, never the projects.** `ai-workspace/` is a git repo (remote `mostlytricks/ai-workspace`), but its `.gitignore` is **deny-all-then-whitelist**: it commits only the meta files (`AGENTS.md`, `CLAUDE.md`, the `*.template.*` stencils, `.claude/` commands+scripts, the root docs, `VERSION`, `CHANGELOG.md`) and denies every tier folder. The whitelist **is** the portable skeleton — what gets replicated into another local runtime. So: never add `repos/`, `active/`, `stable/`, `dormant/`, or `archive/` to this repo (the `*` rule already blocks them) — that would make it the forbidden *umbrella repo* of your projects.
- **Each project is its own independent repo** under `repos/<project>/`, with its own remote. Project version control never mixes with the skeleton repo above.
- **Gravity itself is versioned** (SemVer): the system version lives in the root `VERSION` file + a git tag `vX.Y.Z`, with changes recorded in the root `CHANGELOG.md` (see it for the major/minor/patch rule — *major = a rule projects depend on breaks*). A project records the gravity version it adopted via the `> gravity: vX.Y` line in its root `CLAUDE.md` router (seeded from `GRAVITY.template.md`), so stale adoptions are detectable.
- Junctions are transparent to `git` — commands run from inside a tier junction operate on the real `.git` in `repos/<project>/`.

---

## 3. Project Storage Invariants

A project's real files live in **one of two places**:
- **`repos/<name>/`** — default for new projects. Tier folders hold junctions pointing here.
- **An external path** (e.g. `D:\code\old-thing\`) — when something hardcodes the existing path (IDE workspace files, CI, different drive). Junction directly from the tier folder; skip `repos/`.

**Invariants:**
- Tier folders (`active/`, `stable/`, `dormant/`, `archive/`) hold **directory junctions** (`mklink /J`) only — never real project files. No exceptions (the real-folder `incubator/` tier was retired in v2.0).
- Use junctions, not symbolic links. Junctions need no admin or Developer Mode on Windows. Use `mklink /D` only when crossing drives or needing full POSIX semantics under WSL.
- **Create links only via `python .claude/scripts/link_project.py <link> <target>`** (junction on Windows, symlink on Linux/WSL) or PowerShell `New-Item -ItemType Junction`. **Never** the Git-Bash form `cmd //c "mklink /J active\\$name …"` — MSYS quoting silently drops the `$name` variable and creates a bogus `active$name` link. The helper is argv-driven, so no shell can corrupt the paths; `/init-project` uses it.
- Tier transitions = `mv <tier>/<name> <other-tier>/`. Same-drive `mv` is metadata-only and instant; never touches `node_modules` or `.venv`.
- Never use File Explorer drag-drop to move folders containing `node_modules` or `.venv` — it sometimes performs file-by-file copies and thrashes the disk. Use `mv` (bash) or `Move-Item` (PowerShell).

**For step-by-step procedures** (new project, bring in existing, ship to stable, including PowerShell + Bash code), see **`docs/HANDBOOK.md`**. For the common new-project case, use `/init-project <name>`.

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
- For projects on `.gravity/`, cross-service behavior may earn a normal domain named **`integration`**: `.gravity/integration/SPEC.md` owns the contracts *between* services/domains (API/client types, auth/session flow, ports/base URLs, queues/events, webhooks, shared env, database access boundaries, and the required change order). This is not a new project type; it is just the existing domain model applied to system boundaries. `SPEC.template.md` carries a first-class **integration variant** for authoring it — Minimal Shape becomes a **Boundary Map** (one row per seam + a local ports/base-URL table) and Generate becomes a **Change Order** (the strict cross-boundary edit sequence). `/new-spec <project> integration` uses it.
- Keep small integration facts in `CONTRACT.md` when a full domain would be ceremony. Promote them to `.gravity/integration/SPEC.md` only when agents repeatedly change cross-boundary behavior, when rules need enforcement tags/tests, or when the change order is easy to break.
- **Brownfield inversion:** on an *existing mature system you didn't author* (legacy: a frontend + several backends + a database), the `integration` domain comes **first**, not last — the seams are exactly what you don't know, and greenfield's docs-then-code order flips to **archaeology before authorship**. Intake order: two-doc minimum → `.gravity/integration/SPEC.md` (Boundary Map filled from code evidence, every row citing its source file, unknowns as `OPEN:`) → domains minted from *discovered* modules (entering the status spine as ✓ stable — it's shipped software). `/excavate <project>` automates the survey; the human procedure is HANDBOOK "Adopt gravity on an existing (brownfield) system". Two brownfield escalations, both HANDBOOK-documented: when the code carries no readable queries (dynamic SQL, stored procedures, invisible repos), the offline **DB evidence pack** (`DB-EVIDENCE.template.md` → `.gravity/integration/structural/db/`; metadata CSVs only, never row data, partial always allowed) supplies the DB half of the seams and the table clusters that seed *vertical business-domain* candidates; when the system spans **many service repos**, a docs-only **hub project** holds the cross-service gravity with the service clones git-denied under `services/` (the workspace's own deny-all pattern — the hub commits docs + evidence only, so it is never the forbidden umbrella repo).

---

## 6. Per-Project Files — `CLAUDE.md` & `CONTEXT.md`

Each project in `repos/` (i.e. anything surfaced via `active/`, `stable/`, or `dormant/`) has two files at its root:

- **`<project>/CLAUDE.md` — stable identity.** What the project is, stack, run/test commands, conventions, gotchas. Rarely changes. Auto-loads when an agent opens at that subdir (works through the junction). Copy from `CLAUDE.template.md`.
- **`<project>/AGENTS.md` — Codex-compatible shim.** Optional tiny pointer to `CLAUDE.md`; copy from `AGENTS.template.md` when a project should be discoverable by agents that look for `AGENTS.md`. Never duplicate rules here.
- **`<project>/CONTEXT.md` — mutable handoff state.** Completed / Current State / Next Step. Updated every session. A **rolling snapshot of *now***, not a log — see *Keeping CONTEXT.md small* below. Copy from `CONTEXT.template.md`.

Templates are stencils, not config — nothing loads them automatically.

**Skip both** for `archive/` (no further edits; leave existing CONTEXT.md as the final state record).

**Session ritual** for `active/`, `stable/`, and `dormant/` projects:
- **At start** (entering a project subdir): read `<project>/CONTEXT.md` first. If missing and the project qualifies, copy the template.
- **At end** (before stopping): update Completed / Current State / Next Step, bump `Last touched`. For dormant projects, Next Step must name the resume blocker; for stable projects, the reactivation trigger.
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
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML (browser-read; copy `MISSION.template.html`, theme in `DESIGN.docs.md`) |
| `CLAUDE.md` | **How** — identity, stack, constraints | on refactors | Markdown (auto-loads) |
| `IMPLEMENTATION_PLAN.md` | **What/next** — phases, locked decisions, the gate | per phase | Markdown (agent edits it; copy `IMPLEMENTATION_PLAN.template.md`) |
| `CONTEXT.md` | **Now** — state + single next step | per session | Markdown (auto-loads) |

This is **opt-in**, not mandated — most projects (and all `dormant/` ones) stay on the two-doc rule; the overhead only pays off when you keep losing the mission across sessions or projects. `MISSION.html` is HTML because it's a stable thing you *read*; `IMPLEMENTATION_PLAN.md` is Markdown because it changes every phase and the agent edits it. Boundary to keep: PLAN holds the multi-phase arc, CONTEXT holds only *now* — don't duplicate. `/mission <project>` re-orients off these four; `/triage` flags drift between them. See HANDBOOK "Adopt the full doc pipeline" for the how.

**Doc ownership — one concern, one home (reference, don't restate).**

These docs answer *different* questions, so they shouldn't *collide* — but the same fact written in two of them eventually drifts into two *different* facts. The rule: every concern has exactly **one canonical owner**; any other doc that needs it **links to the owner rather than restating it**.

| Concern | Owner | The test |
|---|---|---|
| Why it exists · principles · strategic non-goals | **MISSION.html** | "would breaking this betray the mission?" |
| Identity · stack · run/test · entry points · gotchas · secrets | **CLAUDE.md** | "would breaking this fail a build or leak a secret?" |
| Phases · locked decisions · the gate | **IMPLEMENTATION_PLAN.md** | "is this about *what's next*?" |
| Current state · the single next step | **CONTEXT.md** | "is this only true *right now*?" |
| How it's built · seams · data contracts | **CLAUDE.md** Entry Points — or **ARCHITECTURE.html** when it outgrows a file map | "would a new contributor need this to navigate the code?" |
| One facet's deep "how it's built" (human reference) | **`.gravity/<domain>/ARCHITECTURE.html`** — when one ARCHITECTURE page serves several domains | "is this the full rationale a *human* engineer reads for one domain?" |
| One domain's spec — what to build + the walls (agent contract) | **`.gravity/<domain>/SPEC.md`** — the compact agent-loadable sheet: a Minimal Shape to build *from* + enforcement-tagged Rules that *fence* it, links up to its facet | "is this the short spec you'd hand an *agent* to make a change safely?" |
| Contracts between domains/services | **`.gravity/integration/SPEC.md`** when present; otherwise `CONTRACT.md` / root `CLAUDE.md` | "could changing one part silently break another runtime, schema, generated client, auth flow, queue, or webhook?" |
| The set of domains itself (existence · routing · why · status) | **`.gravity/` directory** + root `CLAUDE.md` (routing) + `MISSION.html` (why) + `IMPLEMENTATION_PLAN.md` (status) — **no registry file** | "which of the four rates does this domain-level fact change at?" |
| App visual design · type · token contract · motion | **`<project>/DESIGN.md`** (copy `DESIGN.template.md`) — for UI projects | "would changing this alter the app's look or erase its personality?" |
| How it deploys · where it runs · how it recovers | **`<project>/RUNBOOK.md`** (copy `RUNBOOK.template.md`; `.gravity/` projects put it at `.gravity/RUNBOOK.md`, routed from the Doc Map) — for projects that deploy | "would you need this at 2am when it's down?" |
| Browser-read HTML-doc look (MISSION.html / ARCHITECTURE.html) | **DESIGN.docs.md** | "is this about how a *doc page* renders, not the app?" |

**`DESIGN.md` vs `DESIGN.docs.md` — don't conflate.** `DESIGN.md` owns the *running app's* visual identity (the thing users operate); `DESIGN.docs.md` owns the look of *browser-read project docs*. A project may have both — keep app design in `DESIGN.md` and the doc theme separate (a per-project doc-theme file may be named `DESIGN.docs.md`, as in agent-view-desktop). `DESIGN.md` is **recognized only when present** and **never mandated** — copy `DESIGN.template.md` only for projects with a UI worth protecting; skip it for libraries, CLIs, and scripts. (Heads-up: one project, `antigravity--pptx-template-manager`, uses `DESIGN.md` for a *JSON schema contract*, not UI — a legacy exception predating this rule, not the convention.)

**Optional ops doc — `RUNBOOK.md` (how it deploys, runs, recovers).** Gravity's lifecycle used to end at the tag (`/cut-release` stops before push); everything after — environments, deploy steps, config/secret *pointers*, health checks, rollback — lived in the operator's head, the exact knowledge-loss failure gravity exists to prevent. A project that actually deploys somewhere may add `RUNBOOK.md` (copy `RUNBOOK.template.md`; flat projects at the root, `.gravity/` projects at `.gravity/RUNBOOK.md` routed from the Doc Map). **Recognized only when present and never mandated** — the DESIGN.md rule applied to ops: skip it for local tools, libraries, and scripts. Ownership test: *"would you need this at 2am when it's down?"* Every step must be runnable as written in the target environment (a GitHub-less workplace runbook can't lean on `gh`). Secrets stay pointers — names and vault locations, never values. In-flight incidents belong in CONTEXT.md; a runbook changes at deploy-shape rate, like CLAUDE.md.

The overlap to watch is the **architectural seam**. MISSION owns the one-sentence *principle* ("everything reduces to one Session shape" / "the JSON deck-spec is the interface"); CLAUDE.md (or ARCHITECTURE.html) owns the *mechanics* (which files, the gotcha) and points back — *"preserve the seam (MISSION §04)"* — instead of re-describing it. Same for non-goals vs constraints: a strategic "we don't do X" lives in MISSION; the operational "doing X breaks the build" lives in CLAUDE.md.

**Optional fifth doc — `ARCHITECTURE.html` (how it's built).** Most projects describe their architecture adequately in CLAUDE.md's *Entry Points* (a file map) plus the one-line seam in MISSION — leave it there. A project whose "how it's built" genuinely outgrows a file map — multiple services, non-obvious data flow, several contributors — may add a browser-read `ARCHITECTURE.html` (copy `ARCHITECTURE.template.html`, theme in `DESIGN.docs.md`) as the canonical home for component boundaries, the seam's mechanics, data contracts, and build/deploy shape. It is **recognized only when present** (like MISSION.html — `/mission` reads it, `/triage` checks it) and **never mandated**; don't add it where a file map already serves. For cross-service contracts specifically, §5's `CONTRACT.md`/`GLOBAL_RULES.md` is this same idea living at the service boundary.

**Optional: the `.gravity/` directory — where the heavy docs live (faceted projects).** Faceting (a deep-dive + an agent rule-sheet per domain) works, but the files pile up at the project root and bury the two that matter most. The fix is a **`.gravity/` directory** that holds *everything except* the two auto-loaders — `CLAUDE.md` and `CONTEXT.md` — plus `README.md` (the user guide). The leading dot is deliberate: a `CLAUDE.md` *inside* `.gravity/` would not auto-load, so the **root `CLAUDE.md` stays the one and only router**.

Inside, docs are grouped **by subject domain, not by doc-type**. The top level holds the cross-cutting four — `MISSION.html` (why), `ARCHITECTURE.html` (system overview), `IMPLEMENTATION_PLAN.md` (the roadmap spine), `DESIGN.md` (visual contract). Each `<domain>/` folder holds whichever of three kinds it needs — `ARCHITECTURE.html` (human *how*), `SPEC.md` (agent *rules*), `PLAN.*.md` (*what/next*) — **named by kind, because the folder already names the subject** (`doc/SPEC.md`, not `SPEC.doc.md`). Add a slug suffix only when a kind repeats (`PLAN.improvement.md`). The old flat form (`ARCHITECTURE.doc.html`, `SPEC.topic.md` at the project root) is the pre-`.gravity/` style — the directory supersedes it.

```
<project>/
  CLAUDE.md · CONTEXT.md · README.md          # stay at root — the router, now, and the user guide
  .gravity/
    GRAVITY.md                                  # the embedded protocol card (versioned copy — see below)
    MISSION.html · ARCHITECTURE.html · IMPLEMENTATION_PLAN.md · DESIGN.md   # cross-cutting
    <domain>/   ARCHITECTURE.html · SPEC.md · PLAN.*.md        # one folder per subject
```

**The repo is self-describing — the protocol card (`.gravity/GRAVITY.md`).** Each project is its own independent repo (§2), so an agent that opens or clones a project *without* this workspace never sees this manual — it would find `.gravity/` full of SPECs and PLANs with no explanation of what they are. The fix: whenever `.gravity/` is created (`/adopt-gravity`, `/excavate`), copy `templates/GRAVITY-PROTOCOL.template.md` → `.gravity/GRAVITY.md` — the compact **project-side** protocol (doc kinds + rates, navigation discipline, SPEC anatomy, the never-do list), stamped `gravity protocol · vX.Y` from the root `VERSION`. The card embeds only what a project-opened agent needs; **workspace rules (tiers, junctions, `PROJECTS.md`) are never embedded** — one concern, one home, applied to gravity itself. It is a **verbatim copy, never hand-edited per project**; upgrading gravity means re-copying it. The router block (from `GRAVITY.template.md`) points at it, and `check.py consistency` (hence `/triage`) WARNs `PROTOCOL_MISSING` / `PROTOCOL_STALE` when the card is absent, unstamped, or older than the workspace `VERSION`.

**The directory *is* the domain registry — there is no registry file** (one would only duplicate the folder list, or collide with MISSION/PLAN/CLAUDE). The "set of domains" instead lives split across **four rate-of-change owners**: *existence* → the directory itself; *routing* → root `CLAUDE.md` (its **Doc Map** + a **change → read-first** table); *why / the principle* → `MISSION.html` (one row per domain — "the system in N domains"); *status / the arc* → `IMPLEMENTATION_PLAN.md` (a per-domain `✓/◑/○` spine, optionally crossed by **Tracks** — named cross-domain directions, each pointing up to its MISSION principle and down to the domain PLAN slices carrying it, holding no slices itself, ≤3 active; a track retires when its residue is enforcement-tagged SPEC rules). The per-domain **why stays singular** in MISSION — never fragment it into per-folder `WHY.md` files; each domain `ARCHITECTURE.html` points *back* to its MISSION row instead of re-deriving its purpose.

Same ownership rule as everywhere (one concern, one home): the **facet `ARCHITECTURE.html` owns the full human rationale**; the paired **`SPEC.md` is the spec an agent loads** and links *up* to its ARCHITECTURE rather than restating it; add a `SPEC.md` **only for domains an agent actually changes** (read-only domains stay HTML-only). A SPEC is **two halves at once**: *generative* — a **Minimal Shape** + a 3-step **Generate loop** an agent instantiates a correct unit *from*; and *limiting* — a **Rules** checklist where **every rule carries an enforcement tag** (`[lint]` / `[type]` / `[test:name]` / `[review]` / `[—]`) naming the wall that catches a violation, so generation is bounded and the contract never lies about which rules are real walls vs reviewer judgment. Behavioral domains (endpoints, parsers, retrieval) add a **Behavioral Contract** of `given/when/then` invariants, each bound to its test. Keep the rate-of-change boundary so SPEC doesn't swallow PLAN: **SPEC holds what's true of every valid unit forever; PLAN holds the intent of this change; WALKTHROUGH holds its proof.** Behavior matures along that boundary: a feature's use scenario enters as `given/when/then` in its PLAN's **Scenario** block (elicited by `/interview <project> <feature>`), and is promoted into the SPEC's Behavioral Contract only once a named test asserts it — intent graduates to contract by earning a wall, never by rewording. **Bugs enter the same door, inverted:** a bug is a *currently-false* scenario — the repro, stated in the slice PLAN as the behavior the system doesn't yet exhibit (`/patch-slice` requires this before any edit) — and its fix must leave the named regression test that graduates it; bug fixes are the fastest source of honest Behavioral Contract lines. Enforce specs with a linter where the rules are checkable (`knowledge-viewer`'s `npm run lint:docs` is the reference implementation — its `doc/SPEC.md` is the worked example of the tagged form).

**Optional integration domain — service-aware gravity, not a new topology.** If a project has multiple runnable parts, generated clients, shared persistence, queues, webhooks, or auth/session behavior crossing boundaries, it may add `.gravity/integration/` like any other domain. The integration SPEC owns the boundary contract and change order; the service/domain SPECs still own their internals. Example: in a React + Spring Boot + Oracle project, `web/SPEC.md` owns React client conventions, `api/SPEC.md` owns controller/DTO rules, `data/SPEC.md` owns migrations/schema, and `integration/SPEC.md` owns the HTTP/API envelope, generated types, auth/session flow, local ports/base URLs, and the rule that React never connects to Oracle directly. Before cross-boundary edits, load `.gravity/integration/SPEC.md` first, then the affected domain SPECs.

**How an agent uses it** (the discipline that keeps faceting from sprawling):
- **Navigate** from the root `CLAUDE.md` Doc Map — never guess paths.
- **Before changing a domain**, load that domain's `.gravity/<domain>/SPEC.md` (the contract); open `ARCHITECTURE.html` only when you need the rationale.
- **Before changing a boundary**, load `.gravity/integration/SPEC.md` when present (or `CONTRACT.md` for smaller projects), then load every affected domain SPEC. Boundary changes include API shape, generated types, auth/session behavior, ports/base URLs, shared env, queues/events, webhooks, or data access rules between services.
- **Touch the doc that matches the change's rate:** *now* → `CONTEXT.md`; *what/next* → the domain's `PLAN.*.md`; *rules* → `SPEC.md`; *how-it's-built* → `ARCHITECTURE.html`; *why* → `MISSION.html`. Don't write *now* into MISSION or *why* into CONTEXT.
- **Adding a feature?** Run the gate first — *is it a domain?* (its own principle + non-goal, rules worth a SPEC, a multi-step arc) or just a `PLAN.*.md` slice under an existing domain. Mint a folder only when it earns its own gravity, and **wire all four indexes** (Doc Map, router table, MISSION row, PLAN spine) so it's never orphaned.

**Recognized only when present and never mandated** — `.gravity/` is for projects that outgrew the flat root; the two-doc minimum (`CLAUDE.md` + `CONTEXT.md`) is unchanged, and CLIs/scripts/libraries never need it. **`knowledge-viewer` is the worked example.** Adopt it in an existing project with **`/adopt-gravity <project>`**; mint a new domain (folder + all four indexes wired) with **`/new-domain <project> <domain>`**. See HANDBOOK "Adopt the `.gravity/` doc system."

**Optional per-change artifact — `WALKTHROUGH.md` (what got done + proof).** The five docs above are all *live* (they describe the present and get overwritten). A walkthrough is the opposite: a **dated, append-only record** of one shipped slice — the narrative of what changed *paired with the evidence it works* (gate output, and screenshots for UI). It's the human-reviewable trust artifact (modeled on Antigravity's walkthrough), the thing someone reads to trust a change without re-deriving it. Lives at `repos/<project>/docs/walkthroughs/<YYYY-MM-DD>-<domain>-<slug>.md`, one per slice; copy from `WALKTHROUGH.template.md`. **Indexed by time, tagged by domain — not foldered by it.** The live `.gravity/<domain>/` docs are faceted by *subject* because you read them *before* a change; a walkthrough is frozen history you read *after*, so it stays in the one flat dated log (the timeline) and names its domain(s) in the slug + a `Domain(s):` header for per-domain retrieval (`glob *-<domain>-*`). A cross-cutting slice lists every domain it touched rather than being forced into a single domain folder. **Opt-in and non-destructive:** write it when a phase or reviewable feature ships, freeze it, and have the matching `CONTEXT.md` "Completed" bullet *link* to it rather than restate it (one concern, one home). Skip for trivial fixes — don't grow ceremony that doesn't pay (MISSION §06). It closes the loop opened by `IMPLEMENTATION_PLAN.md`'s per-phase **Verification** block.

**Evidence in, two doors — intake sheets and the given layer.** Both hold *received* material, never decided truth, and both route out rather than accumulate. **Bug reports** → one dated verbatim sheet per batch (`docs/intake/<date>.md` from `INTAKE.template.md`; `/intake` runs the ritual): six facts per item (gaps elicited or `OPEN: awaiting …`, never plausibly filled), each root cause routes to a bug-intake slice PLAN + queue row; **bugs are never a domain** — no `.gravity/bugs/`, no standing registry. **Domain knowledge** (data dictionaries, business rules, vendor docs) → drop in the git-ignored `.gravity/inbox/` (nothing commits before triage decides privacy); `/given` routes each file to `.gravity/<domain>/given/` (cross-cutting → `.gravity/given/`) with a provenance row: source · received · version · **fidelity** (`verbatim`/`reformatted`/`distilled`; disputes resolve against `given/raw/`, never a rendering) · privacy (private raws stay local; rows are committed pointers). **Quarry, not contract:** cite given docs, never restate; recurring facts graduate to owner-docs with `source: given/<file>` citations. Walls: `check.py intake` + `check.py given`. Private material stays on git-ignored paths.

---

## 7. Cross-Project Tooling

- **`PROJECTS.md`** is the index: one row per project — name, stack, last-touched, tier-appropriate one-liner (focus · reactivation trigger · resume blocker). Update on any tier transition or significant status change. **Local-only (git-ignored)** — it names private projects; the skeleton ships only the sanitized `PROJECTS.sample.md` (copy it on a fresh workspace).
- **`.claude/scenarios/`** is gravity's golden-scenario harness — the mechanical walls: `check.py consistency` (domain↔index drift in one project), `spec` (SPEC Gate/tag honesty vs repo reality), `workspace` (tier/index drift from `scan_workspace.py` facts — one scanner, many callers), `intake` (sheet honesty), `given` (inbox routed, manifested, no ghosts), `scenario`/`selftest` (the harness proving itself on fixtures). Finding meanings and severity bars live in `.claude/scenarios/README.md` — read that, not this bullet, to interpret a finding.
- **Everything else is a command.** The procedure lives in `.claude/commands/<name>.md` (the one home — loaded on invocation, never resident); human workflows and the full cheat sheet in `docs/HANDBOOK.md`. One line each:

| Command | What · when |
|---|---|
| `/init-project <name>` | Scaffold a new project end-to-end: repo folder, junction, stencils, `git init`, index row. |
| `/ship <name>` | active → stable when a release shipped: evidence card, Next Step → reactivation trigger, junction + index move. |
| `/retire <name>` | End of life: read-only risk card, then **archive** (reversible) or **delete** (permanent). |
| `/adopt-gravity <name>` | Retrofit `.gravity/` into a doc-heavy project: relocate docs by domain, seed router + protocol card. |
| `/sync-gravity <name>` | Upgrade to the current gravity: re-copy the card, bump the stamp; judgment deltas **reported, never auto-migrated**. |
| `/excavate <name>` | Brownfield survey → cited integration Boundary Map; unknowns stay `OPEN:`, seams are never guessed. |
| `/new-domain <name> <domain>` | Mint one domain: is-it-a-domain gate, folder + starter PLAN, all four indexes wired. |
| `/new-spec <name> <domain>` | Author a domain SPEC: Minimal Shape + Rules tagged **only from evidence**; under-claim to `[review]`. |
| `/interview <name> [<feature>]` | Elicit what exists only in the user's head into the owner-docs, strawman-first; with `<feature>`, the feature-intake ritual (is-it-a-domain gate + given/when/then scenario). |
| `/intake <name>` | Triage a bug-report batch: dated verbatim sheet, six facts per item (**no repro, no slice**), root causes → slice PLANs + queue rows. |
| `/given <name>` | Route `.gravity/inbox/` into the given layer: one routing table (domain · fidelity · privacy), provenance manifests, inbox ends empty. |
| `/patch-slice <name> [slug]` | Land one slice under the patch-loop walls: anchor → bare-gated verify → bounded fixes → proven rollback. Never merges or pushes. |
| `/cut-release [name]` | One release Change Order (no arg = gravity itself): confirmed bump from `[Unreleased]` evidence, green gate required, **stops before push**. |
| `/triage` | Weekly survey: mechanical scan + checkers → one-page drift report. Read-only. |
| `/dashboard` · `/open-dashboard` | Status across tiers: terminal report · browser one-tap. |
| `/cosmos <name> [3d\|both] [theme]` | One `.gravity/` project rendered as a star system, scanned live from the four indexes — a wrong sky means index drift. |
| `/mission <name>` | Re-orient on one project: what it's for, where it stands, what to ask next. Read-only. |
| `/open-mission [name]` · `/open-architecture [name] [facet]` | Open the authored HTML docs in the browser; locate + launch, never regenerate. |

- **`docs/HANDBOOK.md`** is the human-facing guide — workflows, the command cheat sheet, glossary. Not auto-loaded; agents read it when explicitly asked.
