---
description: Bring one project up to the current gravity version — re-copy the protocol card, bump the router stamp, surface the changelog deltas that need human judgment. Mechanical parts applied; breaking changes reported, never auto-migrated.
argument-hint: <project-or-alias>
---

You are running `/sync-gravity` from `ai-workspace/` to bring project **`$ARGUMENTS`** up to the current gravity version. The mechanical layer (protocol card + stamp) is applied for the user; the judgment layer (rule changes a project must adapt to) is **reported as a checklist, never auto-applied**. Built so a weaker agent can't invent a version or silently "migrate" a project.

## Steps

1. **Resolve the project** via `.claude/scripts/resolve_project.py`. Not found → list candidates and stop.

2. **Read the versions — never invent them:**
   - **Target** = major.minor from the workspace root `VERSION` file.
   - **Router stamp** = the `> gravity: vX.Y` line in the project's root `CLAUDE.md`.
   - **Card stamp** = the `gravity protocol · vX.Y` line in `.gravity/GRAVITY.md` (`.gravity/` projects only).

   If the project has **no router stamp at all**, stop and say so — an unstamped project hasn't adopted gravity's versioned conventions; the fix is adoption (`/adopt-gravity`, or adding a light stamp by hand), not a sync. If both stamps already equal the target, report "already current" and stop.

3. **Read the delta from `CHANGELOG.md`** — every released section between the project's router stamp and the target (e.g. stamped `v1.2`, target `v1.5` → read `[1.3.0]`, `[1.4.0]`, `[1.5.0]`). Sort what you find into:
   - **Mechanical** — the card re-copy and stamp bump (step 4 does these).
   - **Judgment** — any *major*-worthy or convention-shape change the project may violate (renamed conventions, moved files, new required wiring). These become the step-6 checklist. Quote the changelog line; never paraphrase a rule from memory.

4. **Apply the mechanical layer:**
   - `.gravity/` projects: re-copy `templates/GRAVITY-PROTOCOL.template.md` → `.gravity/GRAVITY.md` (overwrite — the card is a verbatim copy by contract), delete the template's top comment block, fill the `v<X.Y>` stamp with the target version.
   - All projects: update the router's `> gravity: vX.Y` line to the target.
   - Flat (non-`.gravity/`) projects get **only** the stamp bump — no card, no ceremony.

5. **Verify.** For `.gravity/` projects run `python .claude/scenarios/check.py consistency --project <path>` and confirm no `PROTOCOL_MISSING`/`PROTOCOL_STALE` remains (other findings: report, don't fix here). Then reconcile the project's row in the `PROJECTS.md` **Gravity adoption** table (stamp + card columns).

6. **Report:** old → new versions, what was re-copied/bumped, and the **judgment checklist** from step 3 — each item as a one-line "changed in vX.Y: <quoted change> → check <what to look at in this project>". An empty checklist is a valid (and common) result for minor-only deltas. **Do not commit** — the diff is the user's review checkpoint.

## What NOT to do

- **Never invent or guess a version** — every version comes from `VERSION`, a stamp line, or a `CHANGELOG.md` heading.
- **Never auto-migrate a judgment item** — restructuring a project to satisfy a new convention is its own task, done with the user, not a side effect of a sync.
- **Never hand-edit the card's content** — it is always a fresh copy of the template.
- **Don't sync an unstamped or archived project** — adoption first; archives are read-only.
- **Don't commit.**
