---
description: Survey active/ + dormant/ projects; flag stale, stencil, and bloated CONTEXT.md files plus index drift; produce a one-page status report.
---

You are running the `/triage` workspace command from `ai-workspace/`. Your job is to produce a one-page status report on every project under `active/` and `dormant/` so the user can decide what to work on, what to prune, what to demote, and what to archive.

## Steps

1. **List projects.** Glob `active/*/` and `dormant/*/`. These entries are directory junctions pointing into `repos/<name>/`; file reads through them work transparently. Also read `PROJECTS.md` to know what the index claims exists, and `ls repos/` to detect projects that exist in storage but aren't junctioned into any tier.

2. **For each project, read** (in this order, skip what's missing):
   - `CONTEXT.md` → grab `Last touched`, Current State, Next Step. Also note its **line count** and the **number of bullets under `## Completed`** (you'll need these for the bloat + stencil checks).
   - `CLAUDE.md` → grab the one-line description and stack (only if needed for the report).
   - `MISSION.html`, `IMPLEMENTATION_PLAN.md`, and `ARCHITECTURE.html` → only if present (the optional four-doc pipeline + fifth doc, CLAUDE.md §6). **For projects on the `.gravity/` doc system** (a `.gravity/` directory present) these live under `.gravity/` — read the root `CLAUDE.md` **Doc Map** to find them and to list the domain folders. Note the current phase from the plan and the Non-Goals list from the mission — you'll need them for the drift check. If `MISSION.html` is present, also skim it against `CLAUDE.md` for the **doc-collision** check (step 7).
   - If neither `CONTEXT.md` nor `CLAUDE.md` exists, mark the project as **uninitialized**.

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
   - **Missing Codex shim:** flag any project with a `CLAUDE.md` but **no `AGENTS.md`** — it won't be discoverable by agents that look for `AGENTS.md` (Codex). The fix is `cp templates/AGENTS.template.md <project>/AGENTS.md`. New projects get it automatically via `/init-project` / `/promote`; this catches ones created before the shim existed.

7. **Doc-pipeline drift** (only for projects that adopted the optional four-doc pipeline — have `MISSION.html` and/or `IMPLEMENTATION_PLAN.md`):
   - **Non-goal drift:** does anything in CONTEXT.md Completed / Current State push toward something MISSION lists under Current Non-Goals? Flag it — this is the highest-value catch.
   - **Phase contradiction:** the plan tags a phase `done` but CONTEXT implies it isn't (or CONTEXT claims work the plan still marks `todo`).
   - **Missing mission doc:** an ambitious-looking active project (multi-phase plan, long-lived, several entry points) that has `CLAUDE.md` + `CONTEXT.md` but **no** `MISSION.html` — suggest adopting the pipeline. Don't flag small/young projects; the two-doc setup is correct for them.
   - **Stale plan:** `IMPLEMENTATION_PLAN.md` "last updated" date far behind CONTEXT.md `Last touched` — the roadmap probably lies.
   - **Doc collision:** the same fact is *stated* in two docs that don't own it (per the §6 ownership rule) — most often the architectural seam or the one-line description appearing in **both** `MISSION.html` and `CLAUDE.md`, or a non-goal duplicated as a constraint. Flag it so the non-owner can be turned into a reference (MISSION owns *why*/the principle; CLAUDE.md owns *how*/the mechanics). Verbatim-or-near duplication is the signal; a brief pointer like "preserve the seam (MISSION §04)" is correct and not a collision.
   - **`.gravity/` registry drift** (only for `.gravity/` projects): the directory *is* the domain registry, kept in sync across four owners (CLAUDE.md §6). **Run the checker rather than eyeballing the indexes:**
     ```bash
     python .claude/scenarios/check.py consistency --project repos/<name>
     ```
     It mechanically reads all four registry owners and reports `UNDERWIRED` (a `.gravity/<domain>/` folder missing from the Doc Map, the router table, the MISSION "system in N domains" row, or the `IMPLEMENTATION_PLAN.md` status spine — an orphaned domain the next agent won't find) and `ORPHAN_ROUTE` (a `.gravity/<domain>/` reference whose folder is gone). Fold every `FAIL` into the 🧭 flag below; surface `WARN`s (orphan routes, a domain folder with no `PLAN*.md`) only when notable. The same core (`check_gravity_consistency`) backs the `/new-domain` golden-scenario, so triage and the scenario agree by construction. If `check.py` is somehow unavailable, fall back to checking the four indexes by hand; also still flag a domain with a `SPEC.md` but **no router-table row** in `CLAUDE.md` (the checker treats that as a WARN, not a FAIL).

8. **Produce the report** with this exact structure (omit a section entirely if it has no entries):

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
- 🧩 <name> | NO AGENTS.md — Codex shim missing; `cp templates/AGENTS.template.md <project>/AGENTS.md`

## Doc-pipeline drift
Only for projects on the four-doc pipeline. Omit if none.
- 🎯 <name> | NON-GOAL DRIFT — recent work touches "<non-goal>" from MISSION
- 🔀 <name> | PHASE MISMATCH — plan says Phase N done, CONTEXT says otherwise
- 📄 <name> | no MISSION.html on an ambitious project — consider adopting the pipeline
- 🔁 <name> | DOC COLLISION — "<fact>" restated in MISSION + CLAUDE.md; make the non-owner a reference
- 🧭 <name> | .gravity REGISTRY DRIFT — domain "<domain>" unwired (missing Doc-Map/MISSION/status row), or a row points at a gone folder

## Recommended actions
A short numbered list of the 3-5 most important triage moves the user should make this week. Be specific — name projects and the action (fill stencil / prune / demote / archive / fix index row).
```

A single project can carry more than one flag (e.g. stale *and* bloated). List it once under the most severe status and mention the secondary flag inline.

9. **Do not modify any files** unless the user asks. This command is read-only by default. If the user follows up with "fix the drift," "prune X," or "demote X," then make the edits.

## Notes

- Be concise. The whole report should fit on one screen.
- Use the emoji prefixes consistently — they let the user scan the report visually.
- If `active/` is empty or has no `CONTEXT.md` files at all, say so plainly and suggest the user run through initial setup before triaging.
- Today's date is provided by the environment — use it for staleness math.
