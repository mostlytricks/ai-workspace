<!--
  IMPLEMENTATION_PLAN.template.md — the "what/next" doc (one of the four clocks; see workspace CLAUDE.md §6).
  Copy to repos/<project>/IMPLEMENTATION_PLAN.md and fill it in. Markdown (not HTML) on purpose:
  this is the doc that changes every phase and that the agent edits, so clean diffs matter more than polish.
  It is the resume sheet — open it in a fresh session to pick up exactly where things stand.
  Boundary vs CONTEXT.md: PLAN holds the multi-phase ARC (decisions, gate, what's left);
  CONTEXT.md holds only NOW (this session's state + the single next step). Don't duplicate.
-->

# <project> — Implementation plan & resume sheet

> One-line working scenario: what this plan is driving toward.
> Branch `<branch>` · last updated YYYY-MM-DD.

## Status right now

Where things stand in one short paragraph: which phases are done, which is next, what's
committed vs in the working tree. Mirror the headline into the roadmap tags below.

```
roadmap:  1 ✓ → 2 ✓ → 3 (next) → 4 → 5
goal:     <the end state these phases add up to>
```

## How to resume in a fresh session

1. Open the repo at its project dir (junction or real path both work).
2. Read this file + `CONTEXT.md` (current state) + `MISSION.html` (why, if anything feels unmoored).
3. Confirm the branch; run the gate (below) to verify green.
4. Say *"continue with Phase N"* — build it, then update this file's status and `CONTEXT.md`.

## Phase roadmap

Each phase = a shippable slice that passes the gate. Tag each `done` / `next` / `todo`.

### Phase 1 — <name> · done
What it delivered, in 1-2 lines.

### Phase 2 — <name> · done
What it delivered.

### Phase 3 — <name> · next
The slice in flight or up next. Be concrete about the deliverable and where it lives.

### Phase 4 — <name> · todo
Sketch only — detail it when it becomes "next".

## Locked decisions

Decisions that are settled — don't relitigate without a reason. This is what stops an agent
from re-opening closed questions every session.

- **<decision>** — <the choice, and the one-line why.>
- **<decision>** — <…>

## Open questions

The sharp, still-unresolved questions worth raising. `/mission` surfaces these when you ask
"what should I ask the agent to improve this project."

- <question the next session should resolve, with enough context to act on it.>
- <…>

## The gate

The exact commands every phase must pass before it counts as done.

```bash
<lint / typecheck command>
<test command>
<build command>
```

Last green: <date / short note on what passed>.

## What's built so far

Optional running map of the key files and which phase added them — handy on big projects,
delete if the repo is small enough that `CLAUDE.md` Entry Points already covers it.

| File | Phase | What it does |
|---|---|---|
| `<path>` | 1 | <role> |
