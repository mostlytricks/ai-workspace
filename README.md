# ai-workspace — Kepler + gravity

A personal operating system for running many AI/coding projects from one root.
It is **two named products** in one repo:

- **Kepler** — the *workspace manager*: tiers, junctions, the project index, the
  dashboard. The laws of motion for the project fleet. This machine only,
  deliberately unversioned (git history is its changelog).
- **gravity** — the *doc protocol* a project adopts: how a codebase describes
  itself so agents (and humans) can change it safely across sessions. Portable —
  it lives whole in [`gravity/`](./gravity/README.md), with its own SemVer.

This repo tracks **only the skeleton** (manual, handbook, protocol distribution,
slash commands). The projects themselves are independent git repos and are never
committed here.

> New here? Open [`docs/INTRO.html`](./docs/INTRO.html) in a browser for the
> guided introduction, or [`docs/OVERVIEW.md`](./docs/OVERVIEW.md) for the
> dev-professional system map.

---

## Kepler — the workspace manager

Projects move through **tiers** by lifecycle. Real files live once in `repos/`;
the tier folders hold directory junctions pointing at them, so moving a project
between tiers is an instant metadata-only `mv` — it never copies `node_modules`
or `.venv`.

```text
ai-workspace/
├── repos/         # CANONICAL storage — real project files live here
├── active/    →   # junctions → repos/  · being worked; touched < 30 days
├── stable/    →   # junctions → repos/  · shipped & in use; reactivation trigger named
├── dormant/   →   # junctions → repos/  · paused; resume blocker named
└── archive/   →   # junctions → repos/  · done, read-only
```

The lifecycle reads *being worked · works · paused · over*: `/init-project`
scaffolds into `active/`, `/ship` moves shipped work to `stable/`, a plain `mv`
pauses to `dormant/` (naming the blocker), `/retire` archives or deletes.
`PROJECTS.md` (local-only, git-ignored) is the live index; `/dashboard` renders
it, `/triage` flags drift weekly.

Each project keeps two root files regardless of anything else: **`CLAUDE.md`**
(stable identity — stack, run/test, gotchas; auto-loads) and **`CONTEXT.md`**
(a rolling snapshot of *now* — Completed / Current State / Next Step, updated
every session; git history is the changelog, so it stays small).

---

## gravity — the protocol projects adopt

Kepler answers "where do projects live"; gravity answers **"how does one project
stay understandable while agents change it."** Its core move is splitting a
project's knowledge by **rate of change**, giving each concern exactly one home:

| Doc | Question | Changes |
|---|---|---|
| `MISSION.html` | **Why** — north star, principles, non-goals | rarely |
| `ARCHITECTURE.html` | **How it's built** — components, seams, data flow | on redesigns |
| `SPEC.md` | **The rules** — what's true of every valid unit, forever | when a wall changes |
| `PLAN.*.md` | **What/next** — the intent of one change | per slice |
| `CONTEXT.md` | **Now** — state + the single next step | per session |

Everything except the two root auto-loaders lives in a **`.gravity/` directory**,
grouped **by domain, not by doc-type**:

```text
<project>/
  CLAUDE.md · CONTEXT.md · README.md      # root: identity (+ a 4-line fenced router block), now, user guide
  .gravity/
    GRAVITY.md                            # the protocol card — a verbatim, version-stamped copy
    ROUTER.md                             # Doc Map + what-to-read-before-changing-what
    MISSION.html · ARCHITECTURE.html · IMPLEMENTATION_PLAN.md · DESIGN.md   # cross-cutting
    <domain>/  ARCHITECTURE.html · SPEC.md · PLAN.*.md   # one folder per subject
```

**A domain** is a subject that earns its own gravity: its own principle and
non-goal (a MISSION row), rules worth a SPEC, a multi-step arc. The directory
*is* the registry — there is no registry file; a domain exists by having a
folder, and is wired into four indexes (ROUTER Doc Map, ROUTER read-first table,
MISSION row, PLAN status spine) so it's never orphaned. `/new-domain` runs the
is-it-a-domain gate before minting one.

**A SPEC is a change contract**, two halves at once: *generative* — a Minimal
Shape + a Generate loop an agent instantiates a correct unit from — and
*limiting* — Rules where **every rule carries an enforcement tag**
(`[lint]` / `[type]` / `[test:name]` / `[review]` / `[—]`) naming the wall that
catches a violation, so the contract never lies about which rules are real walls
versus reviewer judgment. Behavioral domains add given/when/then invariants,
each bound to a named test. Cross-service contracts get their own
**`integration` domain** (Boundary Map + Change Order).

**The work-layer law:** the **slice** is the only unit of work. Phases/queue
(time), the status spine (domain), and **tracks** (direction — named
cross-domain intents, ≤3 active) are *indexes over slices*, never separate work.
Intent matures along one boundary: a scenario enters as given/when/then in a
slice PLAN and graduates into the SPEC's Behavioral Contract only once a named
test asserts it — and a bug is just a currently-false scenario entering the same
door.

**Adoption never collides with the project.** gravity owns nothing in a
project's root files except a machine-managed 4-line fenced
`<!-- gravity:router -->` block; the full map lives in `.gravity/ROUTER.md`. The
protocol card (`.gravity/GRAVITY.md`) makes the repo self-describing when cloned
without this workspace, and its `gravity: vX.Y` stamp against
[`gravity/VERSION`](./gravity/VERSION) makes stale adoptions detectable.

Full distribution — the protocol card, all stencils, and the portable
scanners — is cataloged in [`gravity/README.md`](./gravity/README.md).

---

## Tooling (slash commands)

⊙ marks protocol-side commands (they work on a project's gravity docs);
unmarked ones are Kepler-side.

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a new project: repo folder, junction, stencils, `git init`, index row |
| `/ship` · `/retire` · `/triage` · `/dashboard` | Lifecycle moves + the weekly drift survey + one-screen status |
| ⊙ `/adopt-gravity <name>` | Retrofit `.gravity/` into an existing project; `/sync-gravity` upgrades a stale adoption |
| ⊙ `/excavate <name>` | Brownfield survey → cited Boundary Map; unknowns stay `OPEN:`, seams are never guessed |
| ⊙ `/new-domain` · `/new-spec` · `/interview` | Mint a domain (gate + 4 indexes) · author a tagged SPEC from evidence · elicit what's only in your head |
| ⊙ `/intake` · `/given` | The two evidence doors: bug-report batches · received domain knowledge, both routed with provenance |
| ⊙ `/preflight <name> <domain>` | The pre-change packet: read-first order, coupled SPECs, the runnable gate, honest warnings |
| ⊙ `/patch-slice` · `/cut-release` | Land one slice under the patch-loop walls · cut one release (stops before push) |
| ⊙ `/observatory <name>` | One project, one page — Overview+drift+tracks · Queue · Seams · Spec Health · Graduation · Timeline · Orbit 3D. A wrong page means doc drift |
| ⊙ `/mission <name>` | Re-orient: what it's for, where it stands, what to ask next |

> The full cheat sheet, workflows, and glossary live in
> [`docs/HANDBOOK.md`](./docs/HANDBOOK.md). The agent-facing rules and
> invariants live in [`CLAUDE.md`](./CLAUDE.md) — the one operating manual.

---

## Repo layout

```text
CLAUDE.md             # Kepler's operating manual (rules & invariants) — auto-loads for agents
AGENTS.md             # Codex-compatible shim → points to CLAUDE.md
PROJECTS.sample.md    # tracked skeleton of the local-only project index (cp → PROJECTS.md)
docs/                 # human/browser read-docs: INTRO.html · OVERVIEW.md · HANDBOOK.md · MISSION.html · DESIGN.docs.md
gravity/              # THE PROTOCOL DISTRIBUTION: VERSION · CHANGELOG.md · GRAVITY-PROTOCOL.md · templates/ · lib/
.claude/commands/     # the slash commands (procedures live here, loaded on invocation)
.claude/scenarios/    # the mechanical walls: check.py consistency/spec/workspace/intake/given + fixtures
```

The `.gitignore` is deny-all-then-whitelist: the tracked files above **are** the
portable skeleton; every tier folder is denied, so this repo can never become an
umbrella repo of the projects it manages.
