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
├── PROJECTS.md                     # Live index of all projects across tiers.
├── VERSION                         # Gravity system version (SemVer) — paired with a git tag vX.Y.Z (§2).
├── CHANGELOG.md                    # How gravity's own rules/templates/commands evolved (major = a rule projects depend on breaks).
├── .gitignore                      # Deny-all/whitelist: tracks only the portable skeleton (§2).
│
├── docs/                           # Human/browser READ-DOCS (rarely change):
│   ├── HANDBOOK.md                 #   Human-facing guide: workflows, slash commands, glossary.
│   ├── MISSION.html                #   The workspace's own north star — the durable why behind these rules.
│   └── DESIGN.docs.md              #   Shared theme for browser-read project HTML docs (distinct from DESIGN.md — §6).
│
├── templates/                      # Per-project / per-domain STENCILS (copied, never auto-loaded):
│   ├── CLAUDE.template.md          #   Per-project stable-identity stencil.
│   ├── AGENTS.template.md          #   Per-project Codex-compatible shim; points to CLAUDE.md.
│   ├── CONTEXT.template.md         #   Per-project session-handoff stencil.
│   ├── MISSION.template.html       #   Per-project "why" stencil (optional four-doc pipeline, §6).
│   ├── IMPLEMENTATION_PLAN.template.md  # Per-project "what/next" stencil (optional four-doc pipeline, §6). Two shapes: phase roadmap (arc projects) or slice queue (growing projects).
│   ├── PLAN.template.md            #   Per-domain / per-slice "what/next" stencil — Goal + given/when/then Scenario + Slice + Verification; seeded by /new-domain and /interview (§6).
│   ├── ARCHITECTURE.template.html  #   Per-project "how it's built" stencil (optional fifth doc, §6). Also seeds ARCHITECTURE.<facet>.html deep-dives.
│   ├── SPEC.template.md            #   Per-domain agent-loadable spec stencil — generative (Minimal Shape + Generate loop) and limiting (enforcement-tagged Rules); paired with an ARCHITECTURE facet (optional; §6). Carries a first-class INTEGRATION VARIANT (Boundary Map + Change Order) for the cross-service `integration` domain (§5).
│   ├── GRAVITY.template.md         #   Root-CLAUDE.md router block (Doc Map + read-first table + domain gate) for projects adopting .gravity/ (optional; §6).
│   ├── WALKTHROUGH.template.md     #   Per-change "what got done + proof" stencil (optional, append-only; §6).
│   └── DESIGN.template.md          #   Per-project running-app UI design-system stencil (optional; §6).
│
├── .claude/commands/               # Workspace-level slash commands.
├── .claude/scripts/                # Helper scripts (link_project.py, new_project.py, retire_project.py).
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
- Done or dead → `/retire <name>` — assess, then **archive** (keep, read-only) or **delete** (permanent). No further edits once archived.

After any transition, update `PROJECTS.md`.

Never create files at the workspace root other than the meta files listed above.

---

## 2. Git Boundaries

- **The root repo tracks only the gravity *skeleton*, never the projects.** `ai-workspace/` is a git repo (remote `mostlytricks/ai-workspace`), but its `.gitignore` is **deny-all-then-whitelist**: it commits only the meta files (`AGENTS.md`, `CLAUDE.md`, the `*.template.*` stencils, `.claude/` commands+scripts, the root docs, `VERSION`, `CHANGELOG.md`) and denies every tier folder. The whitelist **is** the portable skeleton — what gets replicated into another local runtime. So: never add `repos/`, `active/`, `dormant/`, `archive/`, or `incubator/` to this repo (the `*` rule already blocks them) — that would make it the forbidden *umbrella repo* of your projects.
- **Each project is its own independent repo** under `repos/<project>/`, with its own remote. Project version control never mixes with the skeleton repo above.
- **Gravity itself is versioned** (SemVer): the system version lives in the root `VERSION` file + a git tag `vX.Y.Z`, with changes recorded in the root `CHANGELOG.md` (see it for the major/minor/patch rule — *major = a rule projects depend on breaks*). A project records the gravity version it adopted via the `> gravity: vX.Y` line in its root `CLAUDE.md` router (seeded from `GRAVITY.template.md`), so stale adoptions are detectable.
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

**For step-by-step procedures** (new project, bring in existing, promote from incubator, including PowerShell + Bash code), see **`docs/HANDBOOK.md`**. For the common new-project case, use `/init-project <name>`.

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
- **Brownfield inversion:** on an *existing mature system you didn't author* (legacy: a frontend + several backends + a database), the `integration` domain comes **first**, not last — the seams are exactly what you don't know, and greenfield's docs-then-code order flips to **archaeology before authorship**. Intake order: two-doc minimum → `.gravity/integration/SPEC.md` (Boundary Map filled from code evidence, every row citing its source file, unknowns as `OPEN:`) → domains minted from *discovered* modules (entering the status spine as ✓ stable — it's shipped software). `/excavate <project>` automates the survey; the human procedure is HANDBOOK "Adopt gravity on an existing (brownfield) system".

---

## 6. Per-Project Files — `CLAUDE.md` & `CONTEXT.md`

Each project in `repos/` (i.e. anything surfaced via `active/` or `dormant/`) has two files at its root:

- **`<project>/CLAUDE.md` — stable identity.** What the project is, stack, run/test commands, conventions, gotchas. Rarely changes. Auto-loads when an agent opens at that subdir (works through the junction). Copy from `CLAUDE.template.md`.
- **`<project>/AGENTS.md` — Codex-compatible shim.** Optional tiny pointer to `CLAUDE.md`; copy from `AGENTS.template.md` when a project should be discoverable by agents that look for `AGENTS.md`. Never duplicate rules here.
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
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely | HTML (browser-read; copy `MISSION.template.html`, theme in `DESIGN.docs.md`) |
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
| One facet's deep "how it's built" (human reference) | **`.gravity/<domain>/ARCHITECTURE.html`** — when one ARCHITECTURE page serves several domains | "is this the full rationale a *human* engineer reads for one domain?" |
| One domain's spec — what to build + the walls (agent contract) | **`.gravity/<domain>/SPEC.md`** — the compact agent-loadable sheet: a Minimal Shape to build *from* + enforcement-tagged Rules that *fence* it, links up to its facet | "is this the short spec you'd hand an *agent* to make a change safely?" |
| Contracts between domains/services | **`.gravity/integration/SPEC.md`** when present; otherwise `CONTRACT.md` / root `CLAUDE.md` | "could changing one part silently break another runtime, schema, generated client, auth flow, queue, or webhook?" |
| The set of domains itself (existence · routing · why · status) | **`.gravity/` directory** + root `CLAUDE.md` (routing) + `MISSION.html` (why) + `IMPLEMENTATION_PLAN.md` (status) — **no registry file** | "which of the four rates does this domain-level fact change at?" |
| App visual design · type · token contract · motion | **`<project>/DESIGN.md`** (copy `DESIGN.template.md`) — for UI projects | "would changing this alter the app's look or erase its personality?" |
| Browser-read HTML-doc look (MISSION.html / ARCHITECTURE.html) | **DESIGN.docs.md** | "is this about how a *doc page* renders, not the app?" |

**`DESIGN.md` vs `DESIGN.docs.md` — don't conflate.** `DESIGN.md` owns the *running app's* visual identity (the thing users operate); `DESIGN.docs.md` owns the look of *browser-read project docs*. A project may have both — keep app design in `DESIGN.md` and the doc theme separate (a per-project doc-theme file may be named `DESIGN.docs.md`, as in agent-view-desktop). `DESIGN.md` is **recognized only when present** and **never mandated** — copy `DESIGN.template.md` only for projects with a UI worth protecting; skip it for libraries, CLIs, and scripts. (Heads-up: one project, `antigravity--pptx-template-manager`, uses `DESIGN.md` for a *JSON schema contract*, not UI — a legacy exception predating this rule, not the convention.)

The overlap to watch is the **architectural seam**. MISSION owns the one-sentence *principle* ("everything reduces to one Session shape" / "the JSON deck-spec is the interface"); CLAUDE.md (or ARCHITECTURE.html) owns the *mechanics* (which files, the gotcha) and points back — *"preserve the seam (MISSION §04)"* — instead of re-describing it. Same for non-goals vs constraints: a strategic "we don't do X" lives in MISSION; the operational "doing X breaks the build" lives in CLAUDE.md.

**Optional fifth doc — `ARCHITECTURE.html` (how it's built).** Most projects describe their architecture adequately in CLAUDE.md's *Entry Points* (a file map) plus the one-line seam in MISSION — leave it there. A project whose "how it's built" genuinely outgrows a file map — multiple services, non-obvious data flow, several contributors — may add a browser-read `ARCHITECTURE.html` (copy `ARCHITECTURE.template.html`, theme in `DESIGN.docs.md`) as the canonical home for component boundaries, the seam's mechanics, data contracts, and build/deploy shape. It is **recognized only when present** (like MISSION.html — `/mission` reads it, `/triage` checks it) and **never mandated**; don't add it where a file map already serves. For cross-service contracts specifically, §5's `CONTRACT.md`/`GLOBAL_RULES.md` is this same idea living at the service boundary.

**Optional: the `.gravity/` directory — where the heavy docs live (faceted projects).** Faceting (a deep-dive + an agent rule-sheet per domain) works, but the files pile up at the project root and bury the two that matter most. The fix is a **`.gravity/` directory** that holds *everything except* the two auto-loaders — `CLAUDE.md` and `CONTEXT.md` — plus `README.md` (the user guide). The leading dot is deliberate: a `CLAUDE.md` *inside* `.gravity/` would not auto-load, so the **root `CLAUDE.md` stays the one and only router**.

Inside, docs are grouped **by subject domain, not by doc-type**. The top level holds the cross-cutting four — `MISSION.html` (why), `ARCHITECTURE.html` (system overview), `IMPLEMENTATION_PLAN.md` (the roadmap spine), `DESIGN.md` (visual contract). Each `<domain>/` folder holds whichever of three kinds it needs — `ARCHITECTURE.html` (human *how*), `SPEC.md` (agent *rules*), `PLAN.*.md` (*what/next*) — **named by kind, because the folder already names the subject** (`doc/SPEC.md`, not `SPEC.doc.md`). Add a slug suffix only when a kind repeats (`PLAN.improvement.md`). The old flat form (`ARCHITECTURE.doc.html`, `SPEC.topic.md` at the project root) is the pre-`.gravity/` style — the directory supersedes it.

```
<project>/
  CLAUDE.md · CONTEXT.md · README.md          # stay at root — the router, now, and the user guide
  .gravity/
    MISSION.html · ARCHITECTURE.html · IMPLEMENTATION_PLAN.md · DESIGN.md   # cross-cutting
    <domain>/   ARCHITECTURE.html · SPEC.md · PLAN.*.md        # one folder per subject
```

**The directory *is* the domain registry — there is no registry file** (one would only duplicate the folder list, or collide with MISSION/PLAN/CLAUDE). The "set of domains" instead lives split across **four rate-of-change owners**: *existence* → the directory itself; *routing* → root `CLAUDE.md` (its **Doc Map** + a **change → read-first** table); *why / the principle* → `MISSION.html` (one row per domain — "the system in N domains"); *status / the arc* → `IMPLEMENTATION_PLAN.md` (a per-domain `✓/◑/○` spine). The per-domain **why stays singular** in MISSION — never fragment it into per-folder `WHY.md` files; each domain `ARCHITECTURE.html` points *back* to its MISSION row instead of re-deriving its purpose.

Same ownership rule as everywhere (one concern, one home): the **facet `ARCHITECTURE.html` owns the full human rationale**; the paired **`SPEC.md` is the spec an agent loads** and links *up* to its ARCHITECTURE rather than restating it; add a `SPEC.md` **only for domains an agent actually changes** (read-only domains stay HTML-only). A SPEC is **two halves at once**: *generative* — a **Minimal Shape** + a 3-step **Generate loop** an agent instantiates a correct unit *from*; and *limiting* — a **Rules** checklist where **every rule carries an enforcement tag** (`[lint]` / `[type]` / `[test:name]` / `[review]` / `[—]`) naming the wall that catches a violation, so generation is bounded and the contract never lies about which rules are real walls vs reviewer judgment. Behavioral domains (endpoints, parsers, retrieval) add a **Behavioral Contract** of `given/when/then` invariants, each bound to its test. Keep the rate-of-change boundary so SPEC doesn't swallow PLAN: **SPEC holds what's true of every valid unit forever; PLAN holds the intent of this change; WALKTHROUGH holds its proof.** Behavior matures along that boundary: a feature's use scenario enters as `given/when/then` in its PLAN's **Scenario** block (elicited by `/interview <project> <feature>`), and is promoted into the SPEC's Behavioral Contract only once a named test asserts it — intent graduates to contract by earning a wall, never by rewording. Enforce specs with a linter where the rules are checkable (`knowledge-viewer`'s `npm run lint:docs` is the reference implementation — its `doc/SPEC.md` is the worked example of the tagged form).

**Optional integration domain — service-aware gravity, not a new topology.** If a project has multiple runnable parts, generated clients, shared persistence, queues, webhooks, or auth/session behavior crossing boundaries, it may add `.gravity/integration/` like any other domain. The integration SPEC owns the boundary contract and change order; the service/domain SPECs still own their internals. Example: in a React + Spring Boot + Oracle project, `web/SPEC.md` owns React client conventions, `api/SPEC.md` owns controller/DTO rules, `data/SPEC.md` owns migrations/schema, and `integration/SPEC.md` owns the HTTP/API envelope, generated types, auth/session flow, local ports/base URLs, and the rule that React never connects to Oracle directly. Before cross-boundary edits, load `.gravity/integration/SPEC.md` first, then the affected domain SPECs.

**How an agent uses it** (the discipline that keeps faceting from sprawling):
- **Navigate** from the root `CLAUDE.md` Doc Map — never guess paths.
- **Before changing a domain**, load that domain's `.gravity/<domain>/SPEC.md` (the contract); open `ARCHITECTURE.html` only when you need the rationale.
- **Before changing a boundary**, load `.gravity/integration/SPEC.md` when present (or `CONTRACT.md` for smaller projects), then load every affected domain SPEC. Boundary changes include API shape, generated types, auth/session behavior, ports/base URLs, shared env, queues/events, webhooks, or data access rules between services.
- **Touch the doc that matches the change's rate:** *now* → `CONTEXT.md`; *what/next* → the domain's `PLAN.*.md`; *rules* → `SPEC.md`; *how-it's-built* → `ARCHITECTURE.html`; *why* → `MISSION.html`. Don't write *now* into MISSION or *why* into CONTEXT.
- **Adding a feature?** Run the gate first — *is it a domain?* (its own principle + non-goal, rules worth a SPEC, a multi-step arc) or just a `PLAN.*.md` slice under an existing domain. Mint a folder only when it earns its own gravity, and **wire all four indexes** (Doc Map, router table, MISSION row, PLAN spine) so it's never orphaned.

**Recognized only when present and never mandated** — `.gravity/` is for projects that outgrew the flat root; the two-doc minimum (`CLAUDE.md` + `CONTEXT.md`) is unchanged, and CLIs/scripts/libraries never need it. **`knowledge-viewer` is the worked example.** Adopt it in an existing project with **`/adopt-gravity <project>`**; mint a new domain (folder + all four indexes wired) with **`/new-domain <project> <domain>`**. See HANDBOOK "Adopt the `.gravity/` doc system."

**Optional per-change artifact — `WALKTHROUGH.md` (what got done + proof).** The five docs above are all *live* (they describe the present and get overwritten). A walkthrough is the opposite: a **dated, append-only record** of one shipped slice — the narrative of what changed *paired with the evidence it works* (gate output, and screenshots for UI). It's the human-reviewable trust artifact (modeled on Antigravity's walkthrough), the thing someone reads to trust a change without re-deriving it. Lives at `repos/<project>/docs/walkthroughs/<YYYY-MM-DD>-<domain>-<slug>.md`, one per slice; copy from `WALKTHROUGH.template.md`. **Indexed by time, tagged by domain — not foldered by it.** The live `.gravity/<domain>/` docs are faceted by *subject* because you read them *before* a change; a walkthrough is frozen history you read *after*, so it stays in the one flat dated log (the timeline) and names its domain(s) in the slug + a `Domain(s):` header for per-domain retrieval (`glob *-<domain>-*`). A cross-cutting slice lists every domain it touched rather than being forced into a single domain folder. **Opt-in and non-destructive:** write it when a phase or reviewable feature ships, freeze it, and have the matching `CONTEXT.md` "Completed" bullet *link* to it rather than restate it (one concern, one home). Skip for trivial fixes — don't grow ceremony that doesn't pay (MISSION §06). It closes the loop opened by `IMPLEMENTATION_PLAN.md`'s per-phase **Verification** block.

---

## 7. Cross-Project Tooling

- **`PROJECTS.md`** is the index. One line per project: name, stack, last-touched, focus or resume blocker. Update on any tier transition or significant status change.
- **`/init-project <name>`** scaffolds a brand-new project end-to-end (Workflow 1 in HANDBOOK): creates `repos/<name>/`, junctions into `active/`, copies both templates, runs `git init`, adds a `PROJECTS.md` row. Use instead of running §3-referenced commands by hand.
- **`/promote <name>`** graduates an incubator project to active (Workflow 3 in HANDBOOK): `mv incubator/<name> repos/<name>`, junctions into `active/`, runs `git init` only if missing, copies templates only if missing (never overwrites), adds a `PROJECTS.md` row.
- **`/retire <name>`** ends the lifecycle (the destructive twin of `/init-project`): prints a read-only **risk card** (remote? commits? uncommitted? referenced by another project?), then on your choice either **archives** (junction → `archive/`, real files kept, reversible) or **deletes** (every junction detached + real folder removed, permanent). Backed by `retire_project.py`, which detaches junctions with `rmdir`/`unlink` — never `rm -rf` through a junction — then reconciles `PROJECTS.md` and regenerates the dashboard.
- **`/adopt-gravity <project>`** retrofits the `.gravity/` doc system (§6) into an existing project: creates `.gravity/`, relocates the heavy docs out of the project root (everything but `CLAUDE.md`/`CONTEXT.md`/`README.md`) with `git mv`, organizes them by domain folder, and seeds the root `CLAUDE.md` router block from `GRAVITY.template.md`. For projects that outgrew the flat root.
- **`/excavate <project>`** surveys a **brownfield** system (§5 brownfield inversion) and authors its integration contract **from code evidence** — the archaeology twin of `/new-spec`: scans four seam inventories (endpoints · MyBatis/JPA↔tables · frontend calls · service↔service links), joins them on the three keys (table name · path+method · base URL/queue), and writes the two-doc minimum (if missing) + `.gravity/integration/SPEC.md` (Boundary Map with a **source citation per row**, ports table, draft Change Order, `[review]`-tagged rules) + regenerable `structural/` dumps. Unjoinable evidence becomes **findings** (dead endpoints, unreached tables, untraceable dynamic SQL) and `OPEN:` lines — never a guessed seam. Proposes domain folders but doesn't mint them; confirms before writing; reads code never the DB; doesn't commit.
- **`/new-domain <project> <domain>`** mints one domain inside an existing `.gravity/`: creates `.gravity/<domain>/` with a starter `PLAN.md`, then **wires all four indexes** so it's never orphaned (Doc Map + read-first table in `CLAUDE.md`, the why/principle row in `MISSION.html`, the status row in `IMPLEMENTATION_PLAN.md`). Runs the *is-it-a-domain?* gate first.
- **`/cut-release [project]`** cuts a versioned release with one **Change Order**, context-aware: **no arg → bumps gravity itself** (`VERSION` + tag on the `ai-workspace` skeleton repo, §2); **`<project>` → bumps that project** (its manifest + tag on its repo). It resolves the current version from the version source *and* the latest git tag (stops on drift), proposes the major/minor/patch bump **from the changelog's `[Unreleased]` evidence and confirms it**, runs the project's real gate (refusing to tag red code), then renames `[Unreleased]` → `[X.Y.Z] - <date>` (date from the system), bumps the version source, commits, and tags — **stopping before push** (the push stays the user's checkpoint). Built so a weaker agent can't invent a version, hardcode a date, or tag a failing gate.
- **`/new-spec <project> <domain>`** authors (or retrofits) one domain's `SPEC.md` from `SPEC.template.md` — the generative **Minimal Shape** + enforcement-tagged **Rules**. Its substance is a **verification procedure that keeps every tag honest**: find the real gate in `package.json` (never invent one), read the code for the true shape, and tag each rule **only from evidence** (`[lint]` only if the linter checks it, `[test:x]` only if the test exists) — **under-claim to `[review]` when unsure**. Then wires the Doc-Map + router-table rows and runs the gate to prove it. Built so a *weaker* agent can't fabricate enforcement; `knowledge-viewer`'s `doc/SPEC.md` (lint pole) and `search/SPEC.md` (review pole) are the worked examples.
- **`/triage`** scans `active/` + `dormant/` (following junctions into `repos/`), reads each `CONTEXT.md`, and flags stale entries, **unfilled stencils**, **bloated files needing a prune** (per §6 thresholds), index drift, and **doc-pipeline drift** (MISSION non-goals vs recent work, plan-phase vs CONTEXT contradictions, ambitious projects missing a mission doc, **doc collisions** — the same fact restated across MISSION and CLAUDE.md, per the §6 ownership rule — and, for `.gravity/` projects, **index drift** between the domain folders and the four registry owners: a folder with no Doc-Map / MISSION-row / PLAN-status entry, or a row pointing at a folder that's gone — checked **mechanically** by shelling out to `.claude/scenarios/check.py consistency` rather than eyeballing the indexes — and **SPEC honesty rot** via `check.py spec`: a Gate naming a dead npm script/path, a `[test:<name>]` pointing at nothing, or template leftovers), and orphans — producing a one-page report. Read-only by default. Use weekly.
- **`.claude/scenarios/`** is gravity's **golden-scenario harness** — it tests gravity's own commands. A scenario is `(command, golden-input fixture, deterministic structural assertions)`: the agent step (running the command) stays manual; the assertion is `check.py`. Its core, `check_gravity_consistency()`, is shared with `/triage` (one checker, two callers — scenarios on fixtures, triage on live repos). `check.py selftest` proves the checkers and validates every scenario fixture; the `/new-domain`, `/new-spec`, and `/excavate` scenarios are the worked examples. This is the *acceptance* half of gravity testing ("did our improvement work as intended?"); the *conformance* half ("does a feature follow its domain SPEC?") begins with **`check.py spec`** — the **spec-honesty checker**, which verifies every `.gravity/<domain>/SPEC.md`'s Gate + enforcement tags against the repo's reality (npm scripts, paths, test files) so a tag can't silently keep claiming a wall that no longer exists, and prints a per-domain tag census (walls vs `[review]` judgment).
- **`/cosmos <project> [3d|both] [theme]`** renders one `.gravity/` project as a **star system** — the conceptual complement to `/dashboard`'s table. MISSION is the star; each domain a planet (size = doc mass, orbit distance = spine status, **orbit speed = activity**: PLAN count · mass · recency); a **ring** marks a SPEC (an unringed planet is an unfenced domain at a glance), a moon marks ARCHITECTURE.html, gold satellites are `PLAN.*.md` slices in transit. Every fact is scanned live from the four registry owners (folder list, spine, MISSION rows) — no hand-kept data, so a wrong-looking sky means wrong indexes (`/triage`). Backed by `.claude/dashboard/generate_cosmos.py` (alias-resolving; self-contained no-dependency HTML — SVG/CSS in 2D, hand-rolled canvas perspective in 3D; themeable via `--theme`, output gitignored under `.claude/dashboard/cosmos/`).
- **`/mission <project>`** re-orients on a single project: reads its four docs — plus `ARCHITECTURE.html` if present, and the `.gravity/` Doc Map + per-domain status spine for faceted projects (§6) — and prints what it's for, where it stands, and the sharp questions worth asking the agent next. Read-only. Use when you've lost the thread on *why* a project exists or *what to ask* to push it forward.
- **`/interview <project>`** is `/mission` in reverse — structured elicitation that gets what exists only in the **user's head** into the docs (the content-seeding twin of the structural commands: `/init-project` seeds stencils, `/new-spec` reads code, but a new or stuck project's *why/walls/shape/gate/next* has no source but the user). Gap-scans first (never asks what the docs answer), then asks the five themes **strawman-first** (a guess to correct beats a blank question), follows up only on contradictions, routes each answer to its one owner-doc, and writes unresolved items as visible **`OPEN:`** lines — never plausibly filled. Ambition-gated (small tools get two docs, no ceremony) and ends with a read-back confirmation. Doesn't commit. With a **`<feature>`** arg it becomes the **growing-project intake ritual**: runs `/new-domain`'s *is-it-a-domain* gate (default verdict: *slice*), elicits the **use scenario** as `given/when/then`, and writes either a wired new domain or a `PLAN.<slug>.md` slice (from `PLAN.template.md`) plus its spine/queue row — the scenario later graduates into the domain SPEC's Behavioral Contract once a test asserts it.
- **`docs/HANDBOOK.md`** is the human-facing guide — workflows, slash command cheat sheet, glossary. Not auto-loaded; agents may read it when explicitly asked.
