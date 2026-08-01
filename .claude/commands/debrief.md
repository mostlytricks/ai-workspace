---
description: Author the debrief for work just finished — a themed walkthrough (why it was asked · how it was handled · key idea · flow-delta figure · proof · next move), written once and frozen.
argument-hint: <project-name> [slug]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(python .kepler/scripts/resolve_project.py:*), Bash(git -C:*), Bash(python .gravity/_lib/run_gate.py:*), Bash(cmd //c start:*)
---

You are running the `/debrief <project> [slug]` workspace command from `ai-workspace/`. Its job: **turn the work that just happened into the trust artifact** — a walkthrough in the browser-read theme, so the user gets the report they'd otherwise have to ask you to narrate. It answers, in order: *why was this asked · how was it handled · what's the key idea · what changed (with the flow delta drawn) · what proves it works · what's the suggested next move.*

This is the on-demand door to the walkthrough layer: the doc kind and its lifecycle are the protocol card's (`.gravity/GRAVITY.md`) — this command just authors one well.

## Steps

1. **Locate the project** (junctions read through transparently; `resolve_project.py` handles aliases). If no argument, use the project the session was just working in.

2. **Identify the slice being debriefed.** The `[slug]` argument names it; otherwise take the most recent work — this session's changes, or the top Completed bullet in `CONTEXT.md`, or the latest commits (`git -C <project> log --oneline -10`). If it's genuinely ambiguous, ask which piece of work to report on.

3. **Gather the six answers — from evidence, not memory alone:**
   - **Request** — what the user actually asked for (near-verbatim from the session) and the purpose behind it. If the ask lives in a slice `PLAN.*.md` Goal or an intake row, cite it.
   - **Approach** — the decisions taken and their one-line whys. Review-worthy choices, not diff narration.
   - **Key idea** — the ONE insight that makes the change hold together.
   - **What changed** — from `git -C <project> diff`/`log`, the real touched files.
   - **Proof** — run the project's gate (`.gravity/_lib/run_gate.py` or the PLAN's verification commands) and paste the **real output**. If a step wasn't run, write that it wasn't — never a fabricated pass.
   - **Next move** — exactly one primary suggestion; smaller follow-ups below it.

4. **Author the walkthrough.** Copy `gravity/templates/WALKTHROUGH.template.html` to `<project>/docs/walkthroughs/<YYYY-MM-DD>-<domain>-<slug>.html` (create the folder if absent) and fill every FILL spot; delete the stencil comments. Specifics:
   - `gravity-domains` meta = the `.gravity/` domain slugs touched (comma-list); the visible Domain(s) line matches. No `.gravity/`? Use the closest subject word and skip domain claims.
   - **The figure**: draw the *same flow* the domain's `ARCHITECTURE.html` draws (read it first if present), with `fd-new` on nodes/edges this slice added or changed and `fd-old` on what it removed. `data-path` on every file label — `check.py arch` reads those. One flow, ~12 nodes max. **Doc-only or config-only change → delete the figure**; an empty diagram is worse than none.
   - Unknowns stay `OPEN:` — never plausibly filled.

5. **Wire it in.** The `CONTEXT.md` Completed bullet for this work should **link** to the walkthrough, not restate it. If a slice `PLAN.*.md` closes with this, note the walkthrough path there too.

6. **Open it in the browser** (`cmd //c start "" <path>`) and print the one-line summary: path · domains · proof status.

## Rules

- **Append-only.** Never edit an existing walkthrough to reflect new reality — write a new one. One file per slice.
- **Evidence honesty.** Proof is pasted output from commands actually run. "Gate not run" is a valid, honest line; a green claim without output is not.
- **Skip for trivial fixes** — if the change wouldn't survive the "when to bother" test in the stencil header, say so and offer to skip; ceremony that doesn't pay is against the mission.
- This command writes only under `docs/walkthroughs/` plus the two link lines (CONTEXT, PLAN). It never commits.
