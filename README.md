# ai-workspace — Kepler + gravity

A personal operating system for running many AI/coding projects from one root.
It is **two named products** in one repo:

- **Kepler** — the *workspace manager*: tiers, junctions, the project index, the
  dashboard, the weekly drift survey. The laws of motion for the project fleet.
  This machine only, deliberately unversioned (git history is its changelog).
- **gravity** — the *doc protocol* a project adopts: how a codebase describes
  itself so agents (and humans) can change it safely across sessions. Portable —
  it lives whole in [`gravity/`](./gravity/README.md), with its own SemVer
  ([`VERSION`](./gravity/VERSION) + tags + [releases](../../releases)).

**How far gravity reaches** is the part a file listing won't show you: it covers
the path from *a sentence somebody said in a user meeting* to *a verified line in
the report handed back to them*. Three evidence doors let outside reality in
(bug reports — the past · handed-in knowledge · agreed requirements — the
future), everything downstream keeps a citation to where it entered, work is cut
into slices only at the moment it starts, and an outward report may say
"verified" only when it can name the proof.

This repo tracks **only the skeleton** (manual, guides, protocol distribution,
slash commands). The projects themselves are independent git repos and are never
committed here — the deny-all `.gitignore` makes an umbrella repo impossible by
construction.

> **New here?** Two browser-read guides split the story (clone first — GitHub
> renders HTML files as source, so open them locally in a browser):
>
> - [`docs/INTRO.html`](./docs/INTRO.html) — **the Kepler guide**: storage &
>   junctions, the four-tier lifecycle, the session ritual, a phrasebook of
>   workspace commands, what is checked mechanically.
> - [`gravity/GRAVITY-GUIDE.html`](./gravity/GRAVITY-GUIDE.html) — **the gravity
>   guide**: the doc protocol for a human engineer, with diagrams and a
>   phrasebook of what to ask an agent. This page *travels* — every adopted
>   project carries it as `.gravity/GRAVITY.html`
>   (한국어판: [`GRAVITY-GUIDE.ko.html`](./gravity/GRAVITY-GUIDE.ko.html)).
>
> For the dev-professional system map, read
> [`docs/OVERVIEW.md`](./docs/OVERVIEW.md) ·
> [한국어](./docs/OVERVIEW.ko.md). For workflows and the full command cheat
> sheet, [`docs/HANDBOOK.md`](./docs/HANDBOOK.md).

---

## Kepler — the workspace manager

Real files live once, in `repos/`; the tier folders hold **directory junctions**
(views), so a project's lifecycle tier is metadata — moving between tiers is an
instant `mv` that never copies `node_modules` or `.venv`, and git sees straight
through the junction to each project's own independent `.git`.

```text
ai-workspace/
├── repos/         # CANONICAL storage — real project files live here, exactly once
├── active/    →   # junctions → repos/  · being worked
├── stable/    →   # junctions → repos/  · shipped & in use; reactivation trigger named
├── dormant/   →   # junctions → repos/  · paused; resume blocker named
└── archive/   →   # junctions → repos/  · over, read-only
```

The lifecycle reads *being worked · works · paused · over*: `/init-project`
scaffolds into `active/`, `/ship` moves shipped work to `stable/` (where
staleness rules stop applying — silence is success), a plain `mv` pauses to
`dormant/` naming the blocker, `/retire` archives or deletes. `PROJECTS.md`
(local-only, git-ignored) is the live index; `/dashboard` renders the fleet,
`/triage` surveys drift weekly, and `check.py workspace` proves the junctions,
tiers, and index still agree.

Every project keeps two root files regardless of anything else: **`CLAUDE.md`**
(stable identity — auto-loads for agents) and **`CONTEXT.md`** (a rolling
snapshot of *now*, updated every session). The ritual: read `CONTEXT.md` first,
update it before you stop. That update is what makes the next resume free.

Full treatment — figures, the phrasebook, the honest "what Kepler does not do" —
in [`docs/INTRO.html`](./docs/INTRO.html).

---

## gravity — the protocol projects adopt

Kepler answers "where do projects live"; gravity answers **"how does one project
stay understandable while agents change it."** Its core move: split the
project's knowledge by **rate of change** and give every fact exactly one home —
mission (*why*, rarely changes) · `CLAUDE.md` (*how*, on refactors) · plan
(*what next*, per phase) · `CONTEXT.md` (*now*, per session). Everything beyond
the two root auto-loaders lives in a **`.gravity/`** directory, grouped **by
subject domain, not doc-type**:

```text
<project>/
  CLAUDE.md · CONTEXT.md · README.md      # root: identity (+ a 4-line fenced router block), now, user guide
  .gravity/
    GRAVITY.md · GRAVITY.html             # the protocol, twice: the card (agent, version-stamped) + the guide (human; + .ko)
    ROUTER.md                             # THE MAP: what to read before changing what
    MISSION.html · ARCHITECTURE.html · IMPLEMENTATION_PLAN.md · DESIGN.md   # cross-cutting
    _inbox/ · _lib/ · _observatory/ · _given/ · _roadmap/  # machinery: a leading `_` is never a domain
    <domain>/  ARCHITECTURE.html · SPEC.md · PLAN.*.md   # one folder per subject
```

The doctrine itself lives in two files that ship with every adoption, so this
README deliberately doesn't restate it:

- **The card** — [`gravity/GRAVITY-PROTOCOL.md`](./gravity/GRAVITY-PROTOCOL.md)
  → `.gravity/GRAVITY.md`: the canonical project-side protocol, written for the
  agent. Domain gates, SPEC anatomy (enforcement-tagged walls), the graduation
  rule, the evidence doors, the never-do list — all of it, version-stamped so a
  stale adoption is detectable (`/triage` flags it, `/sync-gravity` heals it).
- **The guide** — [`gravity/GRAVITY-GUIDE.html`](./gravity/GRAVITY-GUIDE.html)
  → `.gravity/GRAVITY.html`: the same protocol written for the engineer who just
  opened the repo, with figures and a phrasebook. Unstamped; the family always
  moves together.

Adoption never collides with the project: gravity owns nothing in a project's
root files except a machine-managed 4-line fenced block, and the instruments in
`.gravity/_lib/` are stdlib-only Python — a bare clone renders and checks
*itself* with no workspace in sight. The full distribution (card, guides, 21
stencils, the portable instruments) is cataloged in
[`gravity/README.md`](./gravity/README.md).

---

## Tooling (slash commands)

⊙ marks protocol-side commands (they work on a project's gravity docs);
unmarked ones are Kepler-side.

| Command | What it does |
|---|---|
| `/init-project <name>` | Scaffold a new project: repo folder, junction, stencils, `git init`, index row |
| `/ship` · `/retire` · `/triage` · `/dashboard` | Lifecycle moves + the weekly drift survey + one-screen status |
| `/deploy-kepler <path>` | Propagate the skeleton to a sibling workspace — manifest = `git ls-files`, dry-run first |
| ⊙ `/adopt-gravity <name>` | Retrofit `.gravity/` into an existing project; `/sync-gravity` upgrades a stale adoption |
| ⊙ `/excavate <name>` | Brownfield survey → cited Boundary Map; unknowns stay `OPEN:`, seams are never guessed |
| ⊙ `/new-domain` · `/new-spec` · `/interview` | Mint a domain (gate + 4 indexes) · author a tagged SPEC from evidence · elicit what's only in your head |
| ⊙ `/intake` · `/given` · `/urd` | The three evidence doors: bug batches (the past) · received domain knowledge · agreed user requirements (the future) — all routed with provenance; `/urd` writes the plan sheet with basis-tagged estimates |
| ⊙ `/report <name>` | The outward artifact: the engagement book — one calm-UI HTML; Proposal tab + one report tab per cycle, "verified" only with named proof |
| ⊙ `/preflight <name> <domain>` | The pre-change packet: read-first order, coupled SPECs, the runnable gate, honest warnings |
| ⊙ `/patch-slice` · `/cut-release` | Land one slice under the patch-loop walls · cut one release (stops before push) |
| ⊙ `/observatory <name>` | One project, one page — Overview+drift · Queue · Seams · Spec Health · Graduation · Timeline · Orbit 3D. A wrong page means doc drift |
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
docs/                 # human/browser read-docs: INTRO.html (the Kepler guide) · OVERVIEW.md/.ko.md · HANDBOOK.md · MISSION.html
gravity/              # THE PROTOCOL DISTRIBUTION: VERSION · CHANGELOG.md · the card (agent) · the guides (human, EN+KO) · templates/ · lib/
.claude/commands/     # the slash commands (procedures live here, loaded on invocation)
.claude/scenarios/    # the mechanical walls: check.py consistency/spec/arch/given/intake/theme/workspace + fixtures
```

Fresh machine? Clone, `cp PROJECTS.sample.md PROJECTS.md`, then
`python .claude/scripts/bootstrap.py --dry-run` — the index rebuilds the tier
structure and repairs dangling junctions; it never guesses a tier and never
clones a project.
