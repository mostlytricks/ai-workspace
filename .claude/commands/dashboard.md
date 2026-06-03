---
description: One-screen dashboard across active/, incubator/, dormant/, archive/ — counts, last-touched, next step, and drift flags. Also regenerates the visual HTML dashboard.
---

You are running the `/dashboard` workspace command from `ai-workspace/`. Print a single-screen status view across all four tiers so the user can see workspace state at a glance. Read-only.

## Steps

1. **List each tier.** Glob `active/*/`, `incubator/*/`, `dormant/*/`, `archive/*/`. `active`, `dormant`, `archive` entries are directory junctions into `repos/<name>/`; `incubator/` entries are real folders. Reads through junctions work transparently.

2. **For each project, gather** (skip what's missing):
   - From `CONTEXT.md`: `Last touched` date, the Next Step line (or, for dormant, the resume blocker).
   - From `CLAUDE.md`: stack (one short phrase — language/framework). If absent, fall back to inferring from `package.json`, `pyproject.toml`, `Cargo.toml`, etc.; if still unknown, write `—`.
   - **For `active/` only, if the project is on the four-doc pipeline:** the one-line mission from `MISSION.html`'s `.lede`, and the current phase from `IMPLEMENTATION_PLAN.md` (the phase tagged `next`, else the highest `done`). Skip silently for projects without these docs — they just don't get a mission line.
   - If both `CONTEXT.md` and `CLAUDE.md` are missing, mark the project `uninitialized`.

3. **Staleness** (active only): days since `Last touched` vs today.
   - `0–13 d` → fresh, no marker.
   - `14–29 d` → ⚠ stale.
   - `≥30 d` → 🚨 very stale (suggest demoting to dormant).

4. **Drift checks** (one combined line at the bottom):
   - Projects in `repos/` with no junction in any tier (orphans).
   - Projects junctioned into more than one tier.
   - Rows in `PROJECTS.md` that don't match disk (missing or wrong tier).
   - Uninitialized projects (no `CONTEXT.md`).
   - `incubator/` items older than 30 days (consider `/promote` or delete).

5. **Print this exact shape** — keep it tight, fit one screen, truncate names to ~20 chars with `…`:

```
WORKSPACE DASHBOARD — <YYYY-MM-DD>

ACTIVE (<N>)
  <name>             <stack>            <Nd ago>   next: <Next Step, truncated>
       └ <phase> · <one-line mission>          # only if on the four-doc pipeline
  ⚠ <name>           <stack>            <Nd ago>   next: <…>
  🚨 <name>          <stack>            <Nd ago>   next: <…>

INCUBATOR (<N>)
  <name>             <Nd ago>           <one-line note if any>

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
   - **Visual source of truth:** the HTML's design system (premium glassmorphism, deep-navy palette, glow gradients, vendored fonts) is specified in `.claude/dashboard/DESIGN.dashboard.md`. It's deliberately **distinct** from the muted-teal flat doc theme (`DOC_THEME.md`) — the dashboard is built for *scanning*, docs for *reading*. To restyle the dashboard, edit `DESIGN.dashboard.md` and the `TEMPLATE` in `generate_dashboard.py` together (and re-vendor any new fonts).
   - The HTML is derived from `PROJECTS.md`, **not** from the live disk scan above — so if step 4 surfaced index drift, the HTML inherits it. Mention that in one line and offer to reconcile `PROJECTS.md` first.
   - Then offer to open it: `start .claude/dashboard/dashboard.html`. Don't open it unprompted.

## Notes

- Today's date comes from the environment — use it for staleness math.
- If `CONTEXT.md` has the literal stencil placeholder `YYYY-MM-DD` in `Last touched`, treat it as uninitialized rather than parsing the date.
- For `incubator/`, "Nd ago" = days since the folder's mtime; CONTEXT.md is not expected there.
- Prefer terse stack labels: `Node/TS CLI`, `Fastify+Vite`, `Python/FastAPI` — not full dependency lists.
