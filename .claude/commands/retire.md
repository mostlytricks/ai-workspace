---
description: Retire a project — assess risk, then archive (reversible) or delete (permanent). Detaches junctions safely, reconciles PROJECTS.md, regenerates the dashboard.
argument-hint: <project-name>
---

You are running `/retire` from the `ai-workspace/` root. The user wants to retire `$ARGUMENTS` — the end of the lifecycle (`CLAUDE.md` §1: *"Done or dead → archive/"*). This is the destructive counterpart to `/init-project` and `/ship`, so the **assessment and confirmation are the point** — never skip to deletion.

Two dispositions:
- **archive** — keep the real files, move the project's view into `archive/` (read-only, reversible).
- **delete** — remove every junction *and* the real folder (permanent; far worse with no remote).

## Validation

1. **Empty name** — if `$ARGUMENTS` is empty/whitespace, ask which project and stop.
2. **Exists** — `<name>` must exist in some tier (`active/`, `stable/`, `dormant/`, `archive/`) or in `repos/`. If nothing is found anywhere, say so and stop.
3. **Already archived?** — if its only view is already `archive/` and the user asked to archive, say it's already archived and stop.

## Step 1 — Assess (read-only). Print a risk card before doing anything.

Gather, from the workspace root (Bash; PowerShell equivalents fine):

- **Views & real path** — which tiers hold `<name>` (junctions), and the real folder `repos/<name>` + its size (`du -sh`).
- **Remote?** — `git -C <real> remote -v`. A remote means a cloud backup exists → deletion is recoverable.
- **Commits?** — `git -C <real> log --oneline -1`. "no commits yet" means git history can't recover it.
- **Uncommitted/untracked** — `git -C <real> status --short`. These are lost on delete; call out anything dirty.
- **Referenced by another project?** — grep the *other* active/stable/dormant projects and `PROJECTS.md` (incl. its "Not surfaced" notes) for `<name>`. A hit (e.g. a demo/target service, a §5 contract, a hardcoded path) means deleting may break that project — surface it.

Print a compact card, e.g.:
```
Retire assessment — <name>
  Views:        active/<name>            Real: repos/<name> (373K)
  Remote:       none  ⚠ local-only        Commits: 5d93112 "…"  (history exists)
  Uncommitted:  2 files (would be lost)
  Referenced by: multi-system-… (demo target)   ⚠
```

## Step 2 — Recommend, then confirm the disposition

State a recommendation grounded in the card, then ask the user to choose:
- **Recommend `archive`** when the project has *any* lasting value or a weak safety net — no remote, real commits, uncommitted work, or it's referenced by another project. Archiving costs almost nothing and is reversible.
- **Recommend `delete`** only when it's genuinely disposable — a never-run scaffold with no commits, or it has a remote so a copy survives.
- Always state reversibility plainly. For delete with **no remote**, say **"permanent — unrecoverable, no remote backup"** explicitly and get an unambiguous yes.

Do not proceed to Step 3 until the user has chosen archive or delete (and confirmed delete).

## Step 3 — Execute via the helper (never hand-roll the junction removal)

```bash
python .claude/scripts/retire_project.py archive "$ARGUMENTS"   # OR: delete
```

The helper detaches junctions with `rmdir`/`unlink` (link only — never recurses into the target) and refuses to `rmtree` anything that is itself a reparse point. If `python` isn't found, use the PowerShell fallback below; do **not** substitute `rm -rf active/<name>` — that can delete the real files through the junction.

**PowerShell fallback (archive shown; for delete, remove the junction(s) then `Remove-Item -Recurse -Force repos\<name>`):**
```powershell
# detach a junction = remove the link only (rmdir never follows a junction)
cmd /c rmdir "active\$($args)"
# archive: ensure repos/<name> exists, then re-link under archive/
New-Item -ItemType Junction -Path "archive\$($args)" -Target "repos\$($args)" | Out-Null
```

## Step 4 — Reconcile PROJECTS.md

- **archive** — move the project's row into the `## archive/` section, rewriting the focus column to a short past-tense note (`archived <today> — <why>`). Today's date from the environment.
- **delete** — remove the project's row entirely. If it had an entry under "Not surfaced in a tier", remove that too.

## Step 5 — Regenerate the dashboard

```bash
python .claude/dashboard/generate_dashboard.py
```
Report the new tier counts.

## Report back

```
Retired: <name>  (<archive | delete>)
  Views:       <detached active/…; archive/<name> created  |  all junctions removed>
  Real files:  <preserved in repos/<name>  |  deleted (permanent, no remote)>
  PROJECTS.md: <row moved to archive/  |  row removed>
  Dashboard:   regenerated (active=N · stable=N · dormant=N · archive=N)
```

## What NOT to do

- **Never** `rm -rf` a tier folder (`active/`, `stable/`, `dormant/`, `archive/`) or Explorer-delete it — that can recurse through the junction and destroy the real files. Detach the junction with the helper / `rmdir` first.
- **Do not** delete without completing Step 1's assessment and getting an explicit choice — especially the no-remote "permanent" confirmation.
- **Do not** `git push`, touch a remote, or alter another project to "fix" a dangling reference — just report the reference so the user decides.
- **Do not** archive by editing files — archiving is a junction move (the helper), not a copy.
