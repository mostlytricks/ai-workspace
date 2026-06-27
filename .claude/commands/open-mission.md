---
description: Open a project's MISSION.html in the browser (or the workspace's own with no arg). Finds the doc at the project root or under .gravity/, then launches it. No regeneration — it's an authored static doc.
argument-hint: "[project-name]   (omit for the workspace mission)"
---

You are running `/open-mission` from `ai-workspace/`. Goal: get the right `MISSION.html` on screen with **zero fuss** — locate it, pop it in the browser, done. One-line report, nothing more.

## 1. Resolve the target

Parse `$ARGUMENTS` as an optional `<project-name>`.

- **No arg** → the workspace's own mission: `docs/MISSION.html`.
- **`<project-name>`** → find the project under `active/<name>`, `dormant/<name>`, or `repos/<name>` (tier folders are junctions; reads pass through transparently). If not found, say so, list close matches, and stop.
  Then locate its mission, **first hit wins**:
  1. `<project>/.gravity/MISSION.html` — faceted projects (check the root `CLAUDE.md` **Doc Map** if unsure where it lives).
  2. `<project>/MISSION.html` — flat projects.

  If neither exists: MISSION is **recognized only when present** (CLAUDE.md §6). Say the project has no mission doc, suggest `/mission <name>` (to synthesize an orientation) or adopting the four-doc pipeline — and **stop**. Don't fabricate a file.

## 2. Open it

Use the cross-platform launcher (resolves the absolute path; no shell-quoting traps). Substitute the path you found:

```bash
python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('<resolved-path>').resolve().as_uri())"
```

If `python` isn't found, try `py`. If no window surfaces on Windows, fall back to: `cmd.exe //c start "" "$(pwd -W)/<resolved-path>"`. The path through a tier junction (`active/<name>/…`) or `repos/<name>/…` both resolve — use whichever you located.

## 3. Report one line

`opened <path>` — or, if the doc is absent, the "no mission doc" note from step 1.

## What NOT to do

- **Don't regenerate or edit anything** — `MISSION.html` is an authored static doc, not derived output (unlike the dashboard). This command only *opens* it.
- **Don't synthesize a mission** — that's `/mission`. If the file is missing, say so; never write one here.
- **Don't open more than one file** — one mission per run.
