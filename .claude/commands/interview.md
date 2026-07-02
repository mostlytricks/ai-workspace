---
description: Structured elicitation — extract a project's mission, walls, shape, gate, and next step from the user's head into the gravity docs. Evidence-first, strawman-style; unanswered questions stay OPEN, never plausibly filled.
argument-hint: <project-name>
---

You are running `/interview` from `ai-workspace/` to get what exists only in the **user's head** into project **`<project>`**'s docs. Parse `$ARGUMENTS` as `<project>`; if missing, ask.

This is the content-seeding twin of the structural commands: `/init-project` seeds *stencils*, `/new-spec` extracts truth from *code* — but a new or stuck project's mission, constraints, and non-goals have no source except the user. The honesty discipline is the same as `/new-spec`, pointed at a human instead of a codebase: **never invent intent; an unanswered question is written as `OPEN`, not filled plausibly.** A fabricated intent is this command's version of a fabricated wall.

Two modes, one core:
- **Seed** — a blank/partial project (empty stencils, "fill in CLAUDE.md"): interview for everything the gap scan can't answer.
- **Re-interview** — a stuck project (docs exist but name open questions, "User review required" blocks, or CONTEXT says "resolve X first"): ask **only** the OPEN items and any contradictions. Never re-ask what the docs already answer.

## Step 0 — Gap scan (read before asking a single question)

1. **Locate the project** under `active/`, `dormant/`, `incubator/`, or `repos/`. If not found, list close matches and stop.
2. **Read everything that exists**: `CLAUDE.md`, `CONTEXT.md`, `MISSION.html` / `IMPLEMENTATION_PLAN.md` (root or `.gravity/`), any brief/README, the `PROJECTS.md` row, and skim the code layout if there is one.
3. **Build the gap list** against the owner-doc table (workspace CLAUDE.md §6): for each concern — *why/non-goals* (MISSION), *identity/constraints* (CLAUDE.md), *locked decisions/phases/gate* (PLAN), *next step* (CONTEXT) — mark it **answered** (cite where), **OPEN** (named as open in a doc), or **missing**.
4. If the gap list is empty, say so and stop — there is nothing to interview for; suggest `/mission` instead.

**Hard rule: never ask what the docs already answer.** Asking known things proves you didn't read and burns the user's patience budget for the questions that matter.

## Step 1–5 — The five themes (ask in this order, skip answered ones)

Ask **one theme at a time**. For each, lead with a **strawman**: draft your best guess *from the evidence you read* and ask the user to confirm or correct it — a correction carries more signal than a cold answer. Where there is zero evidence, fall back to the open question. Label every guess as a guess.

| # | Theme | The question (strawman form) | Answer lands in |
|---|---|---|---|
| 1 | **Telos** | "From what I read, if this works, ⟨guess⟩ — right? And what would *betray* it?" (the betrayal answer is the non-goals table) | MISSION why + non-goals |
| 2 | **Walls** | "These look fixed: ⟨stack/env/data guesses⟩. Which are locked, which still open?" | CLAUDE.md constraints · PLAN Locked Decisions · PLAN open questions |
| 3 | **Shape** | "The smallest slice that proves this is worth continuing looks like ⟨guess⟩?" Plus the seam: "does everything reduce to one principle like ⟨guess⟩?" No seam yet → honest `OPEN`; Phase 1 becomes *find the seam* | CLAUDE.md identity · PLAN Phase 1 |
| 4 | **Gate** | "When Phase 1 is done, what proves it — a command, a demo, a number? My guess: ⟨guess⟩." "I'll eyeball it" is a valid answer — write `[review]` | PLAN per-phase Verification (future SPEC Gates) |
| 5 | **Now** | "So the single next step is ⟨guess⟩?" | CONTEXT.md Next Step |

**Follow-ups fire only on contradiction** — an answer that conflicts with the code, the docs, or an earlier answer. Name the conflict plainly and ask which side wins. Otherwise move on: five themes, roughly five questions; going deeper needs the user's go-ahead.

Prefer the structured question tool (options = your strawman + alternatives) so the user picks or corrects fast; free text is always available to them.

## Step 6 — Write, read back, stop

1. **Ambition gate first** (anti-ceremony, MISSION §06): a small tool gets a well-filled `CLAUDE.md` + `CONTEXT.md` and **no** MISSION/PLAN ceremony. Only a project with a real arc gets the four-doc pipeline — and only `.gravity/` if it already has (or clearly earns) it. This command must not become a machine for minting doc pipelines nobody needs.
2. **Route every answer to its one owner-doc** (one concern, one home — link, don't restate). Update, don't overwrite: preserve existing good content the way `/new-spec` retrofits do.
3. **Provenance where it matters**: what the user *said* is written plainly; what you *inferred* and they confirmed needs no mark; anything unresolved is written **`OPEN: <question>`** in the PLAN (or CONTEXT if that's the blocker) — visibly, so `/triage` and the next agent see it.
4. **Read back a half-page summary** — "here's what I heard: … — correct me" — and apply corrections before finishing.
5. Refresh `CONTEXT.md` (Completed bullet: "interviewed — docs updated"; Next Step from theme 5). **Do not commit** — that's the user's call.

## What NOT to do

- **Do not fill an unanswered question with a plausible answer.** `OPEN` is honest; fabricated intent poisons every doc downstream.
- **Do not ask what the docs already answer** — the gap scan exists so the user only spends attention where they're the sole source.
- **Do not exceed the five themes without permission** — interrogation fatigue kills the next interview.
- **Do not mint MISSION/PLAN for a small tool** (the ambition gate), and do not write the same fact into two docs.
- **Do not skip the read-back** — the summary confirmation is the interview's gate.
- **Do not commit.**
