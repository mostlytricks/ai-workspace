#!/usr/bin/env python3
"""Scaffold a brand-new ai-workspace project in one shot.

Does everything Workflow 1 (CLAUDE.md §3) requires, deterministically:
  validate name -> mkdir repos/<name> -> junction active/<name> -> copy
  templates -> git init -> add PROJECTS.md row -> print summary.

Stdlib only. Windows-only (junctions via mklink). Idempotent-ish: it refuses
to touch a name that already exists anywhere, so re-running is safe.

Usage:  python .claude/scripts/new_project.py <kebab-case-name>
Exit codes: 0 ok, 1 validation/precondition failure, 2 a step failed.
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from link_project import make_link                     # noqa: E402  (sibling helper)

SCRIPT_DIR = Path(__file__).resolve().parent          # .claude/scripts
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent             # ai-workspace/
TIERS = ("repos", "active", "stable", "dormant", "archive")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PROJECTS_MD = WORKSPACE_ROOT / "PROJECTS.md"
TEMPLATES_DIR = WORKSPACE_ROOT / "templates"          # stencils live here (CLAUDE.md §1)
TEMPLATES = {
    "CLAUDE.md": TEMPLATES_DIR / "CLAUDE.template.md",
    "CONTEXT.md": TEMPLATES_DIR / "CONTEXT.template.md",
    "AGENTS.md": TEMPLATES_DIR / "AGENTS.template.md",   # Codex-compatible shim → CLAUDE.md
}


def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def validate(name):
    if not name or not name.strip():
        fail("no project name given. Usage: new_project.py <kebab-case-name>")
    if not NAME_RE.match(name):
        fail(f"'{name}' is not kebab-case. Use lowercase letters, digits and "
             "single hyphens (e.g. my-new-thing). No spaces/underscores/caps.")
    for tier in TIERS:
        if (WORKSPACE_ROOT / tier / name).exists():
            fail(f"'{name}' already exists in {tier}/. "
                 "Use Workflow 2/3 (bring-in / promote) instead of init.")
    for label, tpl in TEMPLATES.items():
        if not tpl.exists():
            fail(f"missing templates/{tpl.name} — restore it first "
                 f"(needed to create {label}).")


def run(cmd, cwd=WORKSPACE_ROOT, **kw):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True,
                         text=True, **kw)
    if res.returncode != 0:
        fail(f"step failed: {' '.join(cmd)}\n{res.stdout}{res.stderr}", code=2)
    return res


def scaffold(name):
    (WORKSPACE_ROOT / "repos" / name).mkdir(parents=True, exist_ok=False)
    # Junction (Windows) / symlink (POSIX) via the shared helper — argv-driven,
    # so no bash/MSYS/cmd quoting can corrupt the name (the bug that bit us before).
    try:
        make_link(WORKSPACE_ROOT / "active" / name, WORKSPACE_ROOT / "repos" / name)
    except OSError as e:
        fail(f"could not link active/{name} -> repos/{name}: {e}", code=2)
    for out_name, tpl in TEMPLATES.items():
        (WORKSPACE_ROOT / "repos" / name / out_name).write_text(
            tpl.read_text(encoding="utf-8"), encoding="utf-8")
    run(["git", "init", "-q"], cwd=WORKSPACE_ROOT / "repos" / name)


def add_projects_row(name):
    """Insert a row at the end of the `## active/` section. Cosmetic column
    alignment is skipped — the pipe-delimited content is what matters."""
    if not PROJECTS_MD.exists():
        print("note: PROJECTS.md not found — skipped index row.")
        return False
    lines = PROJECTS_MD.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip() == "## active/")
    except StopIteration:
        print("note: no '## active/' section in PROJECTS.md — skipped row.")
        return False
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    # insert after the last non-blank line within the section
    insert_at = end
    for i in range(end - 1, start, -1):
        if lines[i].strip():
            insert_at = i + 1
            break
    row = f"- {name} | tbd | {date.today():%Y-%m-%d} | scaffolded, fill in CLAUDE.md"
    lines.insert(insert_at, row)
    PROJECTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main():
    name = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    validate(name)
    scaffold(name)
    indexed = add_projects_row(name)
    print(f"""Created project: {name}
  Real path:   repos/{name}/
  Junction:    active/{name}  ->  repos/{name}
  Git:         initialized
  PROJECTS.md: {'row added under active/' if indexed else 'NOT updated (see note above)'}

Next steps:
  1. Edit repos/{name}/CLAUDE.md   - stack, run/test commands, conventions
  2. Edit repos/{name}/CONTEXT.md  - set initial Next Step
  3. cd active/{name} to start working""")


if __name__ == "__main__":
    main()
