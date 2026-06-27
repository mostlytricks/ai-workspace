---
description: Promote an incubator project to active — mv into repos/, junction into active/, git init if needed, copy missing templates, update PROJECTS.md.
argument-hint: <project-name>
---

You are running `/promote` from the `ai-workspace/` root. The user wants to graduate `incubator/$ARGUMENTS` into a real project following **Workflow 3** in `HANDBOOK.md`.

This command is for **incubator promotion only**. If the project already lives under `repos/`, or exists at an external path you'd junction in, use Workflow 1 (`/init-project`) or Workflow 2 in HANDBOOK §Workflow-2 instead, and stop.

## Validation

1. **Empty name** — if `$ARGUMENTS` is empty or whitespace, ask the user for a project name and stop.
2. **Name format** — must be kebab-case: lowercase letters, digits, and hyphens only. No spaces, underscores, or uppercase. If invalid, explain the rule and stop.
3. **Source exists** — `incubator/<name>` must exist as a real directory. If missing, stop and tell the user. If it exists but is itself a junction or symlink, stop — incubator entries should be real folders.
4. **Target free** — `<name>` must NOT already exist as a folder under `repos/`, `active/`, `dormant/`, or `archive/`. If it exists anywhere besides `incubator/`, stop and tell the user where the collision is.
5. **Templates present** — verify `templates/CLAUDE.template.md`, `templates/CONTEXT.template.md`, and `templates/AGENTS.template.md` exist (stencils live in `templates/`, CLAUDE.md §1). If any is missing, stop and tell the user to restore them.

## Execute

Run from the workspace root. Default to Bash (Git Bash on Windows); if Bash isn't available, use PowerShell equivalents. Do these steps in order — stop on any failure and report which step failed.

**Bash:**
```bash
name="$ARGUMENTS"
mv "incubator/$name" "repos/$name"
python .claude/scripts/link_project.py "active/$name" "repos/$name"   # junction (Win) / symlink (POSIX)
(cd "repos/$name" && { [ -d ".git" ] || git init -q; })
[ -f "repos/$name/CLAUDE.md" ]  || cp templates/CLAUDE.template.md  "repos/$name/CLAUDE.md"
[ -f "repos/$name/CONTEXT.md" ] || cp templates/CONTEXT.template.md "repos/$name/CONTEXT.md"
[ -f "repos/$name/AGENTS.md" ]  || cp templates/AGENTS.template.md  "repos/$name/AGENTS.md"   # Codex shim
```

> Use the `link_project.py` helper, **not** `cmd //c "mklink /J active\\$name …"` — that Git-Bash
> form silently eats the `$name` variable and creates a bogus `active$name` junction. If `python`
> isn't found, fall back to the PowerShell block below (its `New-Item -ItemType Junction` is also safe).

**PowerShell equivalent (if Bash unavailable):**
```powershell
$name = "$ARGUMENTS"
Move-Item "incubator\$name" "repos\$name"
New-Item -ItemType Junction -Path "active\$name" -Target "repos\$name" | Out-Null
Push-Location "repos\$name"
if (-not (Test-Path ".git"))       { git init -q }
if (-not (Test-Path "CLAUDE.md"))  { Copy-Item ..\..\templates\CLAUDE.template.md  CLAUDE.md }
if (-not (Test-Path "CONTEXT.md")) { Copy-Item ..\..\templates\CONTEXT.template.md CONTEXT.md }
if (-not (Test-Path "AGENTS.md"))  { Copy-Item ..\..\templates\AGENTS.template.md  AGENTS.md }
Pop-Location
```

Track which of these were already present vs. freshly created — you'll report it back.

## Update PROJECTS.md

Append a row under the `## active/` section in `PROJECTS.md`. Use today's date (from the environment) in `YYYY-MM-DD` form. Format:

```
- <name> | tbd | <today> | promoted from incubator, fill in CLAUDE.md + CONTEXT.md
```

If the project already had a CLAUDE.md and/or CONTEXT.md in incubator (so you didn't copy a template), soften the focus text to:

```
- <name> | tbd | <today> | promoted from incubator
```

If `## active/` contains only the italic `_example_` placeholder, leave the placeholder alone and add the real row below it.

## Report back

Print exactly this kind of summary (substitute real values; show `created` vs `preserved existing` for each file/git state):

```
Promoted: <name>
  Real path:  repos/<name>/   (moved from incubator/<name>/)
  Junction:   active/<name>/  →  repos/<name>/
  Git:        <initialized | already a repo, preserved>
  CLAUDE.md:  <created from template | preserved existing>
  CONTEXT.md: <created from template | preserved existing>
  AGENTS.md:  <created from template | preserved existing>
  PROJECTS.md: row added under active/

Next steps:
  1. Edit repos/<name>/CLAUDE.md   — stack, run/test commands, conventions  (skip if already filled in)
  2. Edit repos/<name>/CONTEXT.md  — set Completed / Current State / Next Step
  3. cd active/<name> to continue working
```

## What NOT to do

- **Do not** overwrite an existing `CLAUDE.md`, `CONTEXT.md`, or `AGENTS.md` inside the incubator project. If the user already wrote one, preserve it (the `[ -f ]` / `Test-Path` guards handle this).
- **Do not** reinitialize git if `.git` already exists — that destroys history.
- **Do not** fill in CLAUDE.md or CONTEXT.md content yourself. Leave templates as-is.
- **Do not** create a first commit, add a remote, or install dependencies.
- **Do not** delete anything in `incubator/<name>/` separately — the `mv` is the whole move.
