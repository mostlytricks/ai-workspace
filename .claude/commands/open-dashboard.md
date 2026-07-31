---
description: Open the visual workspace dashboard in your browser — regenerates the HTML from PROJECTS.md so it's current, then launches it. The one-tap "just show me" companion to /dashboard (which prints the full terminal report).
allowed-tools: Read, Bash(python .claude/dashboard/generate_dashboard.py), Bash(python gravity/lib/generate_observatory.py:*), Bash(python -c:*), Bash(cmd.exe:*)
---

You are running `/open-dashboard` from `ai-workspace/`. The user wants the visual dashboard on screen with **zero fuss** — refresh it, pop it in the browser, done. No terminal report.

## Do this

1. **Refresh the observatories the dashboard links to** (~0.3s each, so ~4s for the fleet). Each project card carries a `⊙ observatory` chip linking into `repos/<name>/.gravity/_observatory/index.html`; regenerating first means every link lands on a current page instead of a stale one:

   ```bash
   for p in repos/*/.gravity; do p=${p%/.gravity}; n=$(basename "$p")
     [ -e "archive/$n" ] && continue          # archive/ is read-only (§1)
     python gravity/lib/generate_observatory.py "$p" >/dev/null 2>&1
   done
   ```

   **Skip archived projects** — `archive/` is read-only by §1, and rendering into one writes files the tier forbids. The dashboard doesn't advertise an observatory chip for them either.

   A project whose render **fails** simply keeps its previous page (or none) — the chip then shows `stale`/not-rendered, which is the honest outcome. **Never abort the command over one project.** This step is what separates `/open-dashboard` from `/dashboard`: the read-only report links and labels but never generates.

2. **Regenerate the dashboard so it's current** (fast, offline, no deps):

   ```bash
   python .claude/dashboard/generate_dashboard.py
   ```

   If `python` isn't found, try `py`. If regeneration *fails*, **don't abort** — fall through to the next step and open whatever `.claude/dashboard/dashboard.html` already exists, noting it may be stale. If no HTML exists at all and regeneration failed, report the generator's error and stop.

3. **Open it in the default browser** — use the Python launcher (cross-platform, resolves the absolute path, no shell-quoting traps):

   ```bash
   python -c "import webbrowser, pathlib; webbrowser.open(pathlib.Path('.claude/dashboard/dashboard.html').resolve().as_uri())"
   ```

   If that doesn't surface a window on Windows, fall back to: `cmd.exe //c start "" "$(pwd -W)/.claude/dashboard/dashboard.html"`.

4. **Report one line:** opened — and whether it was freshly regenerated or a stale fallback.

## What NOT to do

- **Don't print the full terminal dashboard** — that's `/dashboard`. This is the visual-only shortcut; keep it quiet.
- **Don't reconcile `PROJECTS.md` or fix drift** — the HTML mirrors `PROJECTS.md` as-is. For drift, point the user at `/dashboard` or `/triage`; don't act on it here.
- **Don't edit any source files** — the only writes are regenerated HTML artifacts (the dashboard and the per-project observatory pages; both are derived output on self-ignoring paths).
