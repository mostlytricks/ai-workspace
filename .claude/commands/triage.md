---
description: Survey active/ + stable/ + dormant/ projects; flag stale, stencil, and bloated CONTEXT.md files plus index drift; produce a one-page status report.
allowed-tools: Read, Glob, Grep, Bash(python .claude/scripts/scan_workspace.py:*), Bash(python .claude/scenarios/check.py:*)
---

You are running the `/triage` workspace command from `ai-workspace/`. Your job is to produce a one-page status report on every project under `active/`, `stable/`, and `dormant/` so the user can decide what to work on, what to prune, what to ship or demote, and what to archive.

## Steps

1. **Get the facts + structural findings mechanically** — the scanner computes, the checker judges; you format and add the judgment layers (step 7):

   ```bash
   python .claude/scripts/scan_workspace.py --pretty
   python .claude/scenarios/check.py workspace
   ```

   The scan JSON carries per-project `tiers`, `context` (`last_touched` · `days_ago` · `staleness` at the canonical 14/30 boundaries · `next_step` · `stencil` · `lines`/`completed_bullets`), `index` row, `adoption` stamps, and the cross-cuts (`orphans` · `multi_tier` · `index_only` · `not_indexed`). The checker turns those facts into findings: FAILs `MULTI_TIER` / `INDEX_MISSING_ON_DISK` / `INDEX_WRONG_TIER`; WARNs `UNINITIALIZED` / `STENCIL` / `BLOAT` / `MISSING_TRIGGER` / `MISSING_BLOCKER` / `REPO_ORPHAN` / `NOT_INDEXED` / `ADOPTION_STALE` / `ADOPTION_MISSING_ROW`. **Do not** re-derive any of this by hand (no date math, no tier globbing, no stencil grepping) — and don't suppress a finding you don't understand; surface it.

2. **Read only what judgment needs** (skip what's missing): each project's `MISSION.html`, `IMPLEMENTATION_PLAN.md`, `ARCHITECTURE.html` — at the root, or under `.gravity/` via the root `CLAUDE.md` **Doc Map** (CLAUDE.md §6). Note the current phase and the Non-Goals list; skim MISSION against `CLAUDE.md` for the **doc-collision** check (step 7). Full `CONTEXT.md` reads are only needed where the report wants more than the scan's `next_step` line.

3. **Map scan facts → report rows:** `staleness` drives the Active section markers (fresh ✅ · stale ⚠️ · very-stale 🚨 — the 🚨 decision is `/ship` if shipped, `dormant/` if blocked, or work it). `MISSING_TRIGGER` drives the Stable ❓ row; `MISSING_BLOCKER` the Dormant ❓ row; `STENCIL` 📋; `BLOAT` 📈 (recommend the prune per CLAUDE.md §6 — don't perform it unless asked); `UNINITIALIZED` fills that section.

4. **Index drift section = the checker's FAILs + index WARNs**, one line each, verbatim enough to act on. `ADOPTION_STALE`/`ADOPTION_MISSING_ROW` fixes are one command: `python .claude/scripts/scan_workspace.py --adoption-table` prints the correct table to paste into PROJECTS.md.

5. **Missing Codex shim:** flag any project whose scan `adoption.shim` is false but `adoption.docsys` isn't null — it won't be discoverable by agents that look for `AGENTS.md`. Fix: `cp templates/AGENTS.template.md <project>/AGENTS.md`.

6. *(merged into steps 1–5 — the scanner/checker own everything mechanical.)*

7. **Doc-pipeline drift** (only for projects that adopted the optional four-doc pipeline — have `MISSION.html` and/or `IMPLEMENTATION_PLAN.md`):
   - **Non-goal drift:** does anything in CONTEXT.md Completed / Current State push toward something MISSION lists under Current Non-Goals? Flag it — this is the highest-value catch.
   - **Phase contradiction:** the plan tags a phase `done` but CONTEXT implies it isn't (or CONTEXT claims work the plan still marks `todo`).
   - **Missing mission doc:** an ambitious-looking active project (multi-phase plan, long-lived, several entry points) that has `CLAUDE.md` + `CONTEXT.md` but **no** `MISSION.html` — suggest adopting the pipeline. Don't flag small/young projects; the two-doc setup is correct for them.
   - **Stale plan:** `IMPLEMENTATION_PLAN.md` "last updated" date far behind CONTEXT.md `Last touched` — the roadmap probably lies.
   - **Doc collision:** the same fact is *stated* in two docs that don't own it (per the §6 ownership rule) — most often the architectural seam or the one-line description appearing in **both** `MISSION.html` and `CLAUDE.md`, or a non-goal duplicated as a constraint. Flag it so the non-owner can be turned into a reference (MISSION owns *why*/the principle; CLAUDE.md owns *how*/the mechanics). Verbatim-or-near duplication is the signal; a brief pointer like "preserve the seam (MISSION §04)" is correct and not a collision.
   - **`.gravity/` registry drift** (only for `.gravity/` projects) — run the checker, never eyeball the four indexes:
     ```bash
     python .claude/scenarios/check.py consistency --project repos/<name>
     ```
     Fold every FAIL (`UNDERWIRED` — an orphaned domain) into the 🧭 flag; fold the protocol-card WARNs (`PROTOCOL_MISSING` / `PROTOCOL_STALE`) into 📡 (fix = re-copy `templates/GRAVITY-PROTOCOL.template.md`, stamp from `VERSION` — the card is never hand-edited); mention other WARNs only when notable. Finding meanings: `.claude/scenarios/README.md`.
   - **SPEC honesty rot** (only for projects with `SPEC.md` files) — a renamed test or deleted npm script silently turns a wall into a lie. Run:
     ```bash
     python .claude/scenarios/check.py spec --project repos/<name>
     ```
     Fold FAILs (`SPEC_UNFILLED` · `GATE_DEAD` · `TAG_DEAD`) into the 🔬 flag; note WARNs one line per project (they mark pre-tagged-form SPECs, not active lies). Quote the per-domain **tag census** when a domain is heavily `[review]`. Finding meanings: `.claude/scenarios/README.md`.

8. **Produce the report** with this exact structure (omit a section entirely if it has no entries):

```
# Workspace Triage — <today's date>

## Active (N projects)
- ✅ <name>     | last: <date> (<N days ago>) | next: <one-line Next Step>
- ⚠️ <name>     | last: <date> (STALE, <N days>) | next: <Next Step>
- 🚨 <name>     | last: <date> (VERY STALE, <N days>) — /ship if shipped, dormant/ if blocked
- 📋 <name>     | STENCIL — CONTEXT.md never filled in; no recorded state
- 📈 <name>     | last: <date> | BLOATED (<lines> lines / <bullets> Completed bullets) — prune per §6

## Stable (N projects)
- 🛰️ <name>     | shipped | reactivate when: <trigger>
- ❓ <name>     | shipped | NO REACTIVATION TRIGGER — Next Step still reads as a task list

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
- 📡 <name> | PROTOCOL CARD — .gravity/GRAVITY.md missing/unstamped/stale (v<X.Y> vs workspace v<X.Z>) — re-copy templates/GRAVITY-PROTOCOL.template.md
- 🔬 <name> | SPEC HONESTY — <domain>/SPEC.md <finding> (dead Gate/tag or template leftover); untagged/gate-less SPECs noted in one line

## Recommended actions
A short numbered list of the 3-5 most important triage moves the user should make this week. Be specific — name projects and the action (fill stencil / prune / ship / demote / archive / fix index row).
```

A single project can carry more than one flag (e.g. stale *and* bloated). List it once under the most severe status and mention the secondary flag inline.

9. **Do not modify any files** unless the user asks. This command is read-only by default. If the user follows up with "fix the drift," "prune X," or "demote X," then make the edits.

## Notes

- Be concise. The whole report should fit on one screen.
- Use the emoji prefixes consistently — they let the user scan the report visually.
- If `active/` is empty or has no `CONTEXT.md` files at all, say so plainly and suggest the user run through initial setup before triaging.
- Today's date is provided by the environment — use it for staleness math.
