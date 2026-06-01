---
description: Survey active/ + dormant/ projects; flag stale, stencil, and bloated CONTEXT.md files plus index drift; produce a one-page status report.
---

You are running the `/triage` workspace command from `ai-workspace/`. Your job is to produce a one-page status report on every project under `active/` and `dormant/` so the user can decide what to work on, what to prune, what to demote, and what to archive.

## Steps

1. **List projects.** Glob `active/*/` and `dormant/*/`. These entries are directory junctions pointing into `repos/<name>/`; file reads through them work transparently. Also read `PROJECTS.md` to know what the index claims exists, and `ls repos/` to detect projects that exist in storage but aren't junctioned into any tier.

2. **For each project, read** (in this order, skip what's missing):
   - `CONTEXT.md` → grab `Last touched`, Current State, Next Step. Also note its **line count** and the **number of bullets under `## Completed`** (you'll need these for the bloat + stencil checks).
   - `CLAUDE.md` → grab the one-line description and stack (only if needed for the report).
   - If neither exists, mark the project as **uninitialized**.

3. **Compute staleness** for `active/` projects:
   - Compare `Last touched` to today's date (provided by the environment).
   - **Stale** = >14 days untouched. **Very stale** = >30 days (should probably move to `dormant/`).

4. **Detect unfilled stencils.** A CONTEXT.md is a **stencil** (copied from the template but never filled in) if it still contains any of these placeholder markers:
   - `Last touched: YYYY-MM-DD`
   - `# CONTEXT — <project name>`
   - literal template bullet text such as "What structural changes were made in the most recent session(s)" or "The single most important thing for the next agent session".
   A stencil is worse than stale — the project is listed as active but has *no* recorded state. Treat it as a top-priority flag.

5. **Detect bloat** (per CLAUDE.md §6 — CONTEXT.md is a rolling snapshot, not a log). Flag a CONTEXT.md for pruning if **either**:
   - more than **~6 bullets** under `## Completed`, or
   - the file is longer than **~80 lines**.
   These don't need clearing — git history preserves every past version — they need *trimming*: Completed cut to the last 1–2 sessions, Current State overwritten to present reality. Recommend the prune; don't perform it unless asked.

6. **Reconcile with PROJECTS.md and `repos/`:**
   - Flag projects that exist on disk but are missing from the index.
   - Flag rows in the index that no longer exist on disk.
   - Flag rows whose tier in the index disagrees with the actual junction location.
   - Flag rows whose `last-touched` date disagrees with the project's CONTEXT.md `Last touched`.
   - Flag entries in `repos/` that have no junction in any tier — these are orphans (storage with no view), unless `PROJECTS.md` lists them under "Not surfaced in a tier (intentional)".
   - Flag projects junctioned into more than one tier at once — only one tier per project.

7. **Produce the report** with this exact structure (omit a section entirely if it has no entries):

```
# Workspace Triage — <today's date>

## Active (N projects)
- ✅ <name>     | last: <date> (<N days ago>) | next: <one-line Next Step>
- ⚠️ <name>     | last: <date> (STALE, <N days>) | next: <Next Step>
- 🚨 <name>     | last: <date> (VERY STALE, <N days>) — consider demoting to dormant/
- 📋 <name>     | STENCIL — CONTEXT.md never filled in; no recorded state
- 📈 <name>     | last: <date> | BLOATED (<lines> lines / <bullets> Completed bullets) — prune per §6

## Dormant (N projects)
- 💤 <name>     | paused: <date> | resume blocker: <blocker>
- ❓ <name>     | paused: <date> | NO RESUME BLOCKER NAMED — consider archiving

## Uninitialized (N projects)
Projects on disk with no CONTEXT.md. Either initialize them or move to archive/.
- <path>

## Index drift
PROJECTS.md disagrees with disk. Reconcile:
- <description of each mismatch>

## Recommended actions
A short numbered list of the 3-5 most important triage moves the user should make this week. Be specific — name projects and the action (fill stencil / prune / demote / archive / fix index row).
```

A single project can carry more than one flag (e.g. stale *and* bloated). List it once under the most severe status and mention the secondary flag inline.

8. **Do not modify any files** unless the user asks. This command is read-only by default. If the user follows up with "fix the drift," "prune X," or "demote X," then make the edits.

## Notes

- Be concise. The whole report should fit on one screen.
- Use the emoji prefixes consistently — they let the user scan the report visually.
- If `active/` is empty or has no `CONTEXT.md` files at all, say so plainly and suggest the user run through initial setup before triaging.
- Today's date is provided by the environment — use it for staleness math.
