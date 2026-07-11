---
description: One-screen dashboard across active/, stable/, dormant/, archive/ — counts, last-touched, next step, and drift flags. Also regenerates the visual HTML dashboard.
---

You are running the `/dashboard` workspace command from `ai-workspace/`. Print a single-screen status view across all four tiers so the user can see workspace state at a glance. Read-only.

## Steps

1. **Get the facts mechanically — never re-derive them by hand:**

   ```bash
   python .claude/scripts/scan_workspace.py --pretty
   ```

   The JSON has everything the sections below need: per-project `tiers`, `context` (`last_touched`, `days_ago`, `staleness` — already classified at the 14/30 boundaries — `next_step`, `stencil`, `lines`/`completed_bullets`), `index` (row + focus), `adoption` stamps, plus `orphans` / `multi_tier` / `index_only` / `not_indexed` and `tier_counts`. **Do not** glob tiers, parse dates, or count days yourself — the scanner already did, deterministically.

2. **Gather the one thing the scanner can't** (judgment, `active/` + four-doc-pipeline projects only): the one-line mission from `MISSION.html`'s `.lede`, and the current phase from `IMPLEMENTATION_PLAN.md` (the phase tagged `next`, else the highest `done`) — at the project root, or under `.gravity/` (CLAUDE.md §6). Skip silently for projects without these docs.

3. **Staleness markers** come straight from the scan's `staleness` field (active only — stable/dormant/archive quiet is intentional): `fresh` → no marker · `stale` → ⚠ · `very-stale` → 🚨 (decide: `/ship` it if it shipped, demote to dormant if blocked, or work it).

4. **Drift flags** — run the mechanical checker and fold its findings into the `Flags:` line:

   ```bash
   python .claude/scenarios/check.py workspace
   ```

   FAILs (multi-tier, index↔disk mismatches) and WARNs (orphans, stencils, missing triggers/blockers, adoption-table rot) map onto the flag counts. Don't re-check what it already proved; don't suppress a FAIL.

5. **Print this exact shape** — keep it tight, fit one screen, truncate names to ~20 chars with `…`:

```
WORKSPACE DASHBOARD — <YYYY-MM-DD>

ACTIVE (<N>)
  <name>             <stack>            <Nd ago>   next: <Next Step, truncated>
       └ <phase> · <one-line mission>          # only if on the four-doc pipeline
  ⚠ <name>           <stack>            <Nd ago>   next: <…>
  🚨 <name>          <stack>            <Nd ago>   next: <…>

STABLE (<N>)
  <name>             <stack>            shipped    reactivate when: <trigger, truncated>
  ❓ <name>          <stack>            shipped    NO REACTIVATION TRIGGER NAMED

DORMANT (<N>)
  <name>             paused <Nd ago>    blocker: <…>
  ❓ <name>          paused <Nd ago>    NO BLOCKER NAMED

ARCHIVE (<N>)
  <name>, <name>, <name>     # one line, comma-separated, no detail

Flags: <N stale> · <N very stale> · <N uninitialized> · <N orphans> · <N index drift>
```

Rules for the output:
- If a tier is empty, print `ACTIVE (0)  —  empty` (one line) instead of a section block.
- If `Flags:` are all zero, print `Flags: clean ✅`.
- Use exactly the markers above (`⚠`, `🚨`, `❓`) — they're how the user scans.
- The `└ <phase> · <mission>` sub-line appears **only** under active projects that have a `MISSION.html` + plan; omit it entirely otherwise (no empty line). Truncate the mission to ~60 chars. This is the cross-project re-orientation — it's why someone scans the dashboard after juggling several projects.
- Don't list per-project detail for `archive/` — names only.

6. **Do not modify any source files.** This command is read-only over the workspace. The *one* allowed write is the regenerated HTML artifact in step 7 (derived output, not source). If the user follows up asking to fix specific drift, then act.

7. **Regenerate the HTML dashboard.** After printing the terminal view, run the generator so the visual dashboard reflects the same `PROJECTS.md` state:

   ```bash
   python .claude/dashboard/generate_dashboard.py
   ```

   - It parses `PROJECTS.md` and writes the self-contained `.claude/dashboard/dashboard.html` (offline, no deps — Chart.js and the Outfit/Inter/Fira Code fonts are vendored under `vendor/`). If `python` isn't found, try `py`.
   - **Visual source of truth:** the HTML's design system (premium glassmorphism, deep-navy palette, glow gradients, vendored fonts) is specified in `.claude/dashboard/DESIGN.dashboard.md`. It's deliberately **distinct** from the muted-teal flat doc theme (`DESIGN.docs.md`) — the dashboard is built for *scanning*, docs for *reading*. To restyle the dashboard, edit `DESIGN.dashboard.md` and the `TEMPLATE` in `generate_dashboard.py` together (and re-vendor any new fonts).
   - The HTML is derived from `PROJECTS.md`, **not** from the live disk scan above — so if step 4 surfaced index drift, the HTML inherits it. Mention that in one line and offer to reconcile `PROJECTS.md` first.
   - Then offer to open it: `start .claude/dashboard/dashboard.html`. Don't open it unprompted.

## Notes

- Dates, staleness classes, and stencil detection all come from `scan_workspace.py` — never compute them yourself (that hand-math is the bug this pipeline removed).
- Prefer terse stack labels: `Node/TS CLI`, `Fastify+Vite`, `Python/FastAPI` — not full dependency lists (shorten the scan's `index.stack` if it's long).
