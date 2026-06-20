---
description: Re-orient on one project — read its four docs, summarize what it's for and where it stands, and generate the sharp questions worth asking the agent next.
---

You are running the `/mission <project>` workspace command from `ai-workspace/`. Its job is to **re-orient the user on a single project** when they've lost the thread: what is this for, where does it stand, and — most importantly — *what should I be asking the agent to improve it?*

The argument is a project name (matches a folder under `active/`, `dormant/`, `incubator/`, or `repos/`). If no argument is given, list the `active/` projects and ask which one.

## Steps

1. **Locate the project.** Find `<name>` under `active/`, `dormant/`, `incubator/`, or `repos/` (junctions read through transparently). If it's not found, say so and list the closest matches.

2. **Locate the docs.** `CLAUDE.md` + `CONTEXT.md` always live at the project root. For a project on the **`.gravity/` doc system** (CLAUDE.md §6 — `.gravity/` directory present), the rest live under `.gravity/`: `.gravity/MISSION.html`, `.gravity/IMPLEMENTATION_PLAN.md`, `.gravity/ARCHITECTURE.html`, and per-domain docs in `.gravity/<domain>/`. For a flat project they're at the root. Read the root `CLAUDE.md` **Doc Map** first if present — it tells you exactly where each doc is.

3. **Read its four docs, in this order** (skip what's missing, note what's absent):
   - `MISSION.html` → the durable why. Pull the `.lede` line, the mission statement, principles, and especially the **Current Non-Goals**. For `.gravity/` projects also note the **per-domain "system in N domains"** rows (each domain's principle + non-goal guard).
   - `CLAUDE.md` → identity, stack, constraints, entry points; for `.gravity/` projects it's the **router** (Doc Map + read-first table).
   - `IMPLEMENTATION_PLAN.md` (or `.html`) → current phase, locked decisions, the gate, any **Open Questions**, and (for `.gravity/` projects) the **per-domain `✓/◑/○` status spine**.
   - `CONTEXT.md` → current state + the immediate next step + `Last touched`.
   - `ARCHITECTURE.html` (only if present — the optional fifth doc) → the load-bearing seam's mechanics, component boundaries, and data contracts.

4. **Print the re-orientation** in this exact shape (keep it to one screen):

```
MISSION — <name>

What it's for
  <3 lines max, drawn from MISSION.lede + mission statement. If no MISSION doc exists,
   synthesize from CLAUDE.md and say "(no MISSION.html — synthesized from CLAUDE.md)".>

Where it stands
  phase:   <current phase from the plan, or "—">
  state:   <one line from CONTEXT.md Current State>
  next:    <the single Next Step>
  touched: <Last touched> (<N days ago>)

Questions worth asking the agent
  1. <sharp, specific question>
  2. <…>
  3. <…>
```

5. **Generate the questions — this is the point of the command.** Don't produce generic advice. Derive each question from a real tension you found across the four docs. Hunt specifically for:
   - **Non-goal drift** — does recent work (CONTEXT Completed) push toward something MISSION lists as a non-goal? Ask about it.
   - **Unlocked decisions** — an Open Question in the plan that's gone stale, or a choice made in CONTEXT that was never promoted to a Locked Decision.
   - **Gate gaps** — the plan names a verification gate; does CONTEXT say tests are passing / written? If "no tests yet" persists across phases, ask about it.
   - **Principle vs reality** — a stated product principle that the current state seems to bend.
   - **Stalled next step** — if `Next Step` has been the same across the last couple of sessions (check `git log -p CONTEXT.md` if useful), ask what's blocking it.
   - **Phase/state contradiction** — the plan says a phase is done but CONTEXT implies it isn't (or vice versa).
   - **Doc collision** — the architectural seam or the one-line description is restated in both MISSION and CLAUDE.md (per the §6 ownership rule). Ask whether the non-owner should become a reference before the two copies drift apart.

   Prefer 3-5 questions, each naming the specific doc/decision/file it came from so the user can act immediately. A question the user can't act on is noise — cut it.

6. **Read-only.** This command never edits files. If the user follows up ("update the plan", "lock that decision", "prune CONTEXT"), then make the edit.

## Notes

- Today's date comes from the environment — use it for the "days ago" math.
- If the project has only `CLAUDE.md` + `CONTEXT.md` (the light two-doc setup, no MISSION/PLAN), still produce the report — just note the missing docs and, if the project looks ambitious enough to deserve them, suggest adopting the full pipeline (see HANDBOOK "Adopt the full doc pipeline").
- Keep the whole thing scannable. The user runs this to get un-lost fast, not to read an essay.
