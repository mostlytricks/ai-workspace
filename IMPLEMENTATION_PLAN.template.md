<!--
  IMPLEMENTATION_PLAN.template.md — the "what/next" doc (one of the four clocks; see workspace CLAUDE.md §6).
  Copy to repos/<project>/IMPLEMENTATION_PLAN.md and fill it in. Markdown (not HTML) on purpose:
  this is the doc that changes every phase and that the agent edits, so clean diffs matter more than polish.
  It is the resume sheet — open it in a fresh session to pick up exactly where things stand.
  Boundary vs CONTEXT.md: PLAN holds the multi-phase ARC (decisions, gate, what's left);
  CONTEXT.md holds only NOW (this session's state + the single next step). Don't duplicate.

  GRANULARITY NOTE: the multi-phase roadmap below is the project-level arc. The *next* phase is
  expanded into a "phase spec" (Goal → Review gate → Proposed Changes → Verification) — a
  spec-first, human-gated, deep-linked slice. done/todo phases stay one-liners; you only write the
  full spec for the phase you're about to build, then collapse it to a one-liner once it ships
  (its detail survives in git history + the phase's WALKTHROUGH.md).
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
4. Read the **next** phase's spec, confirm its **User review required** block, then build it.
5. When it passes the gate: write the phase's `WALKTHROUGH.md`, collapse the spec to a one-liner, update `CONTEXT.md`.

## Phase roadmap

Each phase = a shippable slice that passes the gate. Tag each `done` / `next` / `todo`.
`done`/`todo` phases are one-liners; the `next` phase carries the full spec (the four blocks below).

### Phase 1 — <name> · done
What it delivered, in 1-2 lines. → `WALKTHROUGH` (if one was written).

### Phase 2 — <name> · done
What it delivered.

### Phase 3 — <name> · next

The slice in flight. This is the spec the agent executes — written and reviewed *before* code.

**Goal.** What this phase delivers and why, in 2-3 lines. The end state a reviewer can check against.

**User review required.** ⚠ The decisions a human must confirm *before* the agent starts building.
This is the gate — approval is an explicit artifact here, not a buried chat reply. Leave `[ ]` until confirmed.
- [ ] **<decision / assumption>** — <the choice and its blast radius; what changes if you say no.>
- [ ] **<scope boundary>** — <what this phase will and won't touch.>

**Proposed changes.** Every change tagged `[NEW]` / `[MODIFY]` / `[DELETE]`, grouped by layer,
each pointing at the exact file (and line range where it helps). Be concrete enough to execute —
name the functions/signatures, not just the file.
> Reference style: in Claude Code, `path:line` is clickable (e.g. `server/db.ts:42`); a markdown
> link `[server/db.ts](server/db.ts)` works too. Use line anchors when pointing at an existing symbol.

- **[NEW]** `path/to/new_file.ts` — <what it is + the key exports it adds.>
- **[MODIFY]** `server/db.ts:42` — add `migrateFoo(): void`; called once at boot from `index.ts`.
- **[MODIFY]** `ui/api.ts` — add typed `fetchFoo()` helper; must stay in sync with the new route.
- **[DELETE]** `path/old.ts` — superseded by the [NEW] above.

**Verification.** The runnable check that proves this phase works — numbered, reproducible.
Mirrors the project gate but is scoped to *this* slice; the result becomes the phase's walkthrough.
1. <set up input / fixture>
2. <run command> — expect <observable result>.
3. <check output / endpoint / UI state> against the Goal.

### Phase 4 — <name> · todo
Sketch only — expand into the full spec above when it becomes "next".

## Locked decisions

Decisions that are settled — don't relitigate without a reason. This is what stops an agent
from re-opening closed questions every session. (A `User review required` item graduates to here
once confirmed.)

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
