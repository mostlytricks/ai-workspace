---
description: Open the visual workspace dashboard in your browser — regenerates the HTML from PROJECTS.md so it's current, then launches it. The one-tap "just show me" companion to /dashboard (which prints the full terminal report).
---

You are running `/open-dashboard` from `ai-workspace/`. The user wants the visual dashboard on screen with **zero fuss** — refresh it, pop it in the browser, done. No terminal report.

## Do this

1. **Regenerate so it's current** (fast, offline, no deps):

   ```bash
   python .claude/dashboard/generate_dashboard.py
   ```

   If `python` isn't found, try `py`. If regeneration *fails*, **don't abort** — fall through to step 2 and open whatever `.claude/dashboard/dashboard.html` already exists, noting it may be stale. If no HTML exists at all and regeneration failed, report the generator's error and stop.

2. **Open it in the default browser** — use the Python launcher (cross-platform, resolves the absolute path, no shell-quoting traps):

   ```bash
   python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('.claude/dashboard/dashboard.html').resolve().as_uri())"
   ```

   If that doesn't surface a window on Windows, fall back to: `cmd.exe //c start "" "$(pwd -W)/.claude/dashboard/dashboard.html"`.

3. **Report one line:** opened — and whether it was freshly regenerated or a stale fallback.

## What NOT to do

- **Don't print the full terminal dashboard** — that's `/dashboard`. This is the visual-only shortcut; keep it quiet.
- **Don't reconcile `PROJECTS.md` or fix drift** — the HTML mirrors `PROJECTS.md` as-is. For drift, point the user at `/dashboard` or `/triage`; don't act on it here.
- **Don't edit any source files** — the only write is the regenerated HTML artifact (derived output, already gitignored).
