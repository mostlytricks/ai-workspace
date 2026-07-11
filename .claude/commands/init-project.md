---
description: Scaffold a new project from scratch — one script does folder, junction, templates, git init, and the PROJECTS.md row.
argument-hint: <project-name>
---

You are running `/init-project` from the `ai-workspace/` root to create a brand-new project named `$ARGUMENTS` (Workflow 1, CLAUDE.md §3).

All the work lives in one deterministic script — **do not** run the steps by hand. Just invoke it and relay the result.

## Do this

Run from the workspace root:

```bash
python .claude/scripts/new_project.py "$ARGUMENTS"
```

If `python` isn't found, retry with `py .claude/scripts/new_project.py "$ARGUMENTS"`.

The script handles everything in one shot:
- **Validates** the name (kebab-case; not already in repos/active/stable/dormant/archive; templates present) and stops with a clear `ERROR:` if anything is off.
- Creates `repos/<name>/`, junctions `active/<name>` → `repos/<name>`, copies the starter templates (`CLAUDE.md`, `CONTEXT.md`, and the `AGENTS.md` Codex shim), runs `git init`, and appends the `## active/` row in `PROJECTS.md`.
- Prints a summary + next steps.

## Report back

- On success: relay the script's summary block as-is.
- On failure: the script exits non-zero and prints an `ERROR:` line — surface that to the user verbatim and stop. If it says the name already exists, point them at Workflow 2 (bring-in existing).

## What NOT to do

- **Do not** re-run individual `mklink` / `cp` / `git init` commands yourself — the script is the single source of truth and avoids the shell-quoting pitfalls of doing it by hand.
- **Do not** fill in CLAUDE.md / CONTEXT.md content — the user does that next, in the project.
- **Do not** create a first commit, add a remote, or install dependencies.
