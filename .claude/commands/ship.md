---
description: Move a shipped project from active/ to stable/ — verify release evidence, set the reactivation trigger, move the junction, reconcile PROJECTS.md. The "it works, stop nagging me" ritual.
argument-hint: <project-name>
---

You are running `/ship` from the `ai-workspace/` root. The user wants to move `$ARGUMENTS` to `stable/` — the tier for projects that **shipped well**: in real use, release cut, nothing in flight (`CLAUDE.md` §1). Stable is staleness-exempt; its CONTEXT.md carries a **reactivation trigger** instead of a task.

The point of the ritual is honesty at the gate: a project enters stable because it *works*, not because you're tired of its red staleness marker. If something *blocks* progress, that's `dormant/` (resume blocker), not stable.

## Validation

1. **Empty name** — if `$ARGUMENTS` is empty/whitespace, ask which project and stop.
2. **In active/** — `active/<name>` must exist (a junction). If the project is elsewhere (`stable/` already, `dormant/`, `archive/`), say where it is and stop — shipping is active→stable only. Resolve aliases via `python .claude/scripts/resolve_project.py <name>` if the literal name isn't found.
3. **Two docs present** — `CLAUDE.md` + `CONTEXT.md` must exist in the project. If missing, stop and suggest fixing that first (a project without docs isn't "shipped well").

## Step 1 — Check the entry gate (read-only). Print an evidence card.

Gather from the real folder (`repos/<name>` via the junction):

- **Release evidence** — `git -C <real> tag --list` (latest tag) and/or a version heading in the project's `CHANGELOG.md`. Either counts.
- **Working tree** — `git -C <real> status --short`. Uncommitted work is a smell: "shipped" things don't usually have half-finished edits. Surface it.
- **Current Next Step** — quote the CONTEXT.md Next Step verbatim. If it names concrete in-flight work (not a wish), the project may not be done — surface it.

```
Ship assessment — <name>
  Release evidence:  tag v0.1.0 (2026-07-05) · CHANGELOG [0.1.0]     ← or "none found ⚠"
  Working tree:      clean                                            ← or "3 dirty files ⚠"
  Next Step (now):   "<verbatim>"
```

**If there is no release evidence**, don't refuse — some shipped things are used, not versioned (a skill set, a doc site). Show what you found and ask the user to confirm the project really is in use as-is. Proceed only on an explicit yes.

## Step 2 — Write the reactivation trigger

Derive a candidate trigger from the current CONTEXT.md (often the old Next Step *is* the future arc: "cut v0.2.0 when …", "resume when real data exists"). Propose it strawman-style; let the user correct. Then rewrite the project's `CONTEXT.md`:

- **Next Step** → exactly one line: `Reactivate when <X> — then <first move>.`
- **Current State** → overwrite to the shipped steady state (version, where it runs, what uses it).
- Bump `Last touched`.

## Step 3 — Move the junction

```bash
mv "active/$ARGUMENTS" "stable/$ARGUMENTS"
```

Instant metadata move — it's a junction, never the real files.

## Step 4 — Reconcile PROJECTS.md

Move the project's row from `## active/` to `## stable/`. Rewrite the date column to `shipped <today> (<version or milestone>)` and the focus column to the steady state + the reactivation trigger (same line as CONTEXT.md's Next Step). Today's date from the environment.

## Step 5 — Regenerate the dashboard

```bash
python .claude/dashboard/generate_dashboard.py
```

Report the new tier counts.

## Report back

```
Shipped: <name> → stable/
  Evidence:    <tag/CHANGELOG version | "unversioned, user-confirmed in use">
  Trigger:     "Reactivate when <X>"
  PROJECTS.md: row moved to stable/
  Dashboard:   regenerated (active=N · stable=N · dormant=N · archive=N)
```

## What NOT to do

- **Do not** ship a project just because it's stale — staleness means *decide* (ship / demote / work it), not *hide it in stable*.
- **Do not** invent release evidence. If the gate is thin, show it and let the user own the call.
- **Do not** leave the old Next Step in place — a stable project whose CONTEXT still lists tasks will lie to the next agent.
- **Do not** commit or push anything — in the project or the skeleton repo.
- **Reactivation** is deliberately manual (`mv stable/<name> active/` + fresh CONTEXT.md): new arcs need fresh intent that only the user can write.
