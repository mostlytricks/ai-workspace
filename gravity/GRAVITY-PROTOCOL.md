<!--
gravity/GRAVITY-PROTOCOL.md — the embedded protocol card. Copied to
`.gravity/GRAVITY.md` whenever a project's `.gravity/` is created
(/adopt-gravity, /excavate). It makes the project repo SELF-DESCRIBING:
each project is its own independent git repo, so an agent that clones or
opens it *without* the ai-workspace never sees the workspace manual — this
card carries the project-side protocol with the repo.

At copy time, fill ONLY the version stamp below (major.minor from the
workspace `gravity/VERSION` file). Never edit anything else per project — the
card is a verbatim copy; on a gravity upgrade, refresh it by re-copying.
`check.py consistency` (and `/triage`) flags a missing or stale card.

Scope note: this card is the PROJECT-SIDE subset of gravity only. Workspace
rules (tiers, junctions, repos/ storage, PROJECTS.md) stay in the workspace
CLAUDE.md and are never embedded here.
-->

> **gravity protocol · v<X.Y>** — copied from the workspace `gravity/GRAVITY-PROTOCOL.md`; never hand-edit. On a gravity upgrade, re-copy from the workspace (`/triage` flags a stale card).

# The gravity protocol (project-side)

This project organizes its documentation with **gravity**. Two files auto-load from the project root — `CLAUDE.md` (identity, *how*) and `CONTEXT.md` (*now*) — and everything else lives under `.gravity/`, grouped **by subject domain**, not by doc-type. Gravity owns only the **fenced `<!-- gravity:router -->` block** in the root harness files (`CLAUDE.md`, `AGENTS.md`, …) — everything else there is the project's. The full map is **`.gravity/ROUTER.md`**: navigate from its **Doc Map**, never guess paths. *(Pre-v3 projects carry the Doc Map in root `CLAUDE.md` instead — same sections, older home.)*

## The doc kinds and their rates of change

| Doc | Question it answers | Changes |
|---|---|---|
| `.gravity/MISSION.html` | **why** — north star, principles, non-goals | rarely |
| root `CLAUDE.md` | **how** — identity, stack, run/test, conventions (+ gravity's fenced pointer block) | on refactors |
| `.gravity/ROUTER.md` | **routing** — the Doc Map + what to read before changing what + the is-it-a-domain gate | when domains change |
| `.gravity/<domain>/given/` + `MANIFEST.md` | **received** — knowledge handed in from outside (quarry, never contract; disputes resolve against `raw/`) | when material arrives via `.gravity/inbox/` |
| `.gravity/ARCHITECTURE.html` | **how it's built** — system overview | on structural change |
| `.gravity/IMPLEMENTATION_PLAN.md` | **what/next** — roadmap spine + per-domain `✓/◑/○` status (+ optional **Tracks**, the direction axis) | per phase/slice |
| root `CONTEXT.md` | **now** — current state + the single next step | every session |
| `.gravity/<domain>/SPEC.md` | the **change contract** for this domain (agent-loadable) | when rules change |
| `.gravity/<domain>/ARCHITECTURE.html` | the domain's human deep-dive / full rationale | on structural change |
| `.gravity/<domain>/PLAN.*.md` | the **intent of one change** — goal, scenario, slice, verification | per slice |

Three disciplines bind them:
- **One concern, one home.** Every fact has exactly one owner-doc; any other doc *links* to the owner instead of restating it. A fact written twice eventually drifts into two different facts.
- **Touch the doc that matches the change's rate.** *now* → `CONTEXT.md` · *what/next* → the domain's `PLAN.*.md` · *rules* → `SPEC.md` · *how-it's-built* → `ARCHITECTURE.html` · *why* → `MISSION.html`. Never write *now* into MISSION or *why* into CONTEXT.
- **One unit of work — the slice** (the smallest shippable change that passes the gate; its intent lives in a domain `PLAN.*.md`). Phases/queue (time), the status spine (domain), and Tracks (direction) are *indexes over slices* and hold no work themselves — a phase is just a slice with an ordinal.

## How to work here (the navigation discipline)

1. **Session start:** read root `CONTEXT.md`. **Session end:** update its Completed / Current State / Next Step (Completed = last 1–2 sessions only; exactly one Next Step; git history is the changelog, so prune freely).
2. **Before changing a domain:** load `.gravity/<domain>/SPEC.md` — the compact contract. Open the paired `ARCHITECTURE.html` only when you need the full rationale.
3. **Before changing a boundary** (API shape, generated/client types, auth/session behavior, ports/base URLs, shared env, queues/events, webhooks, cross-service data access): load `.gravity/integration/SPEC.md` **first** (or `CONTRACT.md` on smaller projects), then every affected domain SPEC — and follow its **Change Order**.
4. **Adding a feature:** run the *is-it-a-domain?* gate in `.gravity/ROUTER.md` ("Adding a domain"). The default verdict is a **`PLAN.<slug>.md` slice under an existing domain**. Mint a new `.gravity/<domain>/` folder only when the feature has its own gravity — and then **wire all four indexes** so it's never orphaned: the `ROUTER.md` Doc Map, the `ROUTER.md` router table (once it has a SPEC), the `MISSION.html` domain row, and the `IMPLEMENTATION_PLAN.md` status spine.

## Reading (and honoring) a SPEC.md

A SPEC is a **change contract** — a shape to build *from* plus fenced rules — not a generation blueprint: it governs changes to a system rather than scaffolding one from scratch. It is two halves at once:
- **Generative** — a **Minimal Shape** plus a short **Generate loop**: the template you instantiate a correct unit *from*.
- **Limiting** — a **Rules** checklist where **every rule carries an enforcement tag** naming the wall that catches a violation: `[lint]` / `[type]` / `[test:name]` are real, named checks; `[review]` / `[—]` mean human judgment only, no wall. A **Gate:** line names the command that must pass before the change ships.

Behavioral domains add a **Behavioral Contract** of `given/when/then` invariants, each bound to a named test. Behavior matures by graduation: a scenario enters as `given/when/then` intent in a PLAN, and is promoted into the SPEC's Behavioral Contract **only once a named test asserts it** — intent earns a wall, it is never reworded into one.

**Honesty rule:** never tag a rule with a wall you haven't verified exists. When unsure, under-claim to `[review]`. Run the Gate before declaring a change done; report the result faithfully.

## What never to do

- Don't create doc files at the project root — the root holds only `CLAUDE.md`, `CONTEXT.md`, `README.md` (plus code/config).
- Don't put a `CLAUDE.md` inside `.gravity/` — it would not auto-load; root files carry only gravity's fenced pointer.
- Don't edit inside the fenced `<!-- gravity:router -->` block by hand — it's machine-managed; and don't write gravity content outside it into a harness file.
- Don't restate a fact another doc owns — link to it.
- Don't invent docs to fill the layout — docs are recognized only when present; a domain with just a `PLAN.md` is fine.
- Don't leave an unknown plausibly filled — write it as a visible `OPEN:` line.
- Don't hand-edit this card — it's a versioned copy; re-copy from the workspace to upgrade.
