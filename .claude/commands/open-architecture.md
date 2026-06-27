---
description: Open a project's ARCHITECTURE.html in the browser — the system overview, or a named facet (.gravity/<facet>/ARCHITECTURE.html). Finds it at the root or under .gravity/, then launches it. No regeneration. With no project arg it explains where gravity's own architecture lives (CLAUDE.md §1).
argument-hint: "[project-name] [facet]   (omit project for gravity's own)"
---

You are running `/open-architecture` from `ai-workspace/`. Goal: get the right `ARCHITECTURE.html` on screen with **zero fuss**. One-line report, nothing more.

## 1. Resolve the target

Parse `$ARGUMENTS` as `[project-name] [facet]`.

**No arg → gravity/the workspace itself.** Gravity has **no `ARCHITECTURE.html`** — by design (CLAUDE.md §6: most systems describe their architecture in CLAUDE.md's map, not a separate page). Its architecture *is* `CLAUDE.md §1` (the workspace map) plus the tier / git / `.venv` / doc-system rules in §2–§7, and that `CLAUDE.md` already auto-loads. So report this plainly and **offer to open `CLAUDE.md`** in the browser — flagging that it's Markdown, so it renders as plain text, not a themed page. Don't fabricate an `ARCHITECTURE.html`. (This is the deliberate asymmetry with `/open-mission`, whose no-arg case *does* have a real `docs/MISSION.html`.)

**`<project-name>` given** → find the project under `active/<name>`, `dormant/<name>`, or `repos/<name>` (tier folders are junctions; reads pass through). If not found, say so, list close matches, and stop. Read the root `CLAUDE.md` **Doc Map** if you're unsure where its docs live.

Then locate the architecture doc:

- **Facet given** (`<project> <facet>`) → `<project>/.gravity/<facet>/ARCHITECTURE.html`. If that's absent, list the `.gravity/<domain>/` folders that *do* have an `ARCHITECTURE.html` and stop.
- **No facet** → the system overview, **first hit wins**:
  1. `<project>/.gravity/ARCHITECTURE.html` — faceted projects.
  2. `<project>/ARCHITECTURE.html` — flat projects.

  If there's no overview but facet docs exist (`.gravity/<domain>/ARCHITECTURE.html`), there's no single page to open — **list the available facets** and ask which to open (`/open-architecture <name> <facet>`). If none exist at all: ARCHITECTURE is the **optional fifth doc, recognized only when present** (CLAUDE.md §6). Say the project has none and stop. Don't fabricate a file.

## 2. Open it

Use the cross-platform launcher (resolves the absolute path; no shell-quoting traps). Substitute the path you found:

```bash
python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('<resolved-path>').resolve().as_uri())"
```

If `python` isn't found, try `py`. If no window surfaces on Windows, fall back to: `cmd.exe //c start "" "$(pwd -W)/<resolved-path>"`. The path through a tier junction (`active/<name>/…`) or `repos/<name>/…` both resolve — use whichever you located.

## 3. Report one line

`opened <path>` (name the facet if you opened one) — or the "no architecture doc / available facets" note from step 1.

## What NOT to do

- **Don't regenerate or edit anything** — `ARCHITECTURE.html` is an authored static doc, not derived output. This command only *opens* it.
- **Don't create an ARCHITECTURE.html** — recognized only when present; if it's missing, say so, don't write one.
- **Don't open multiple facets at once** — one page per run.
