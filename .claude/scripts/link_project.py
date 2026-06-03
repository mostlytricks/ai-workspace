#!/usr/bin/env python3
"""Create a workspace tier link: a junction on Windows, a symlink on POSIX.

Why this exists
---------------
The Git-Bash idiom `cmd //c "mklink /J active\\$name repos\\$name"` silently
corrupts the name: MSYS quoting eats the shell variable, leaving a bogus
`active$name` junction pointing at a non-existent `repos$name`. That was the
junction error that kept recurring. Driving the link through Python argv means
no shell quoting (bash, MSYS, cmd, or PowerShell) can touch the paths, so one
code path behaves the same in PowerShell 5/7, Git Bash, plain cmd, Linux, and WSL.

Behaviour
---------
Windows (os.name == 'nt') -> directory junction via `mklink /J`. Needs no admin
    or Developer Mode, same-volume only (matches the workspace tier model).
POSIX (Linux / WSL / macOS) -> a *relative* symlink, which keeps the workspace
    portable if the whole tree moves.

Usage:   python .claude/scripts/link_project.py <link> <target>
Example: python .claude/scripts/link_project.py active/my-proj repos/my-proj
Exit codes: 0 ok, 1 bad args / precondition, 2 the link step failed.
"""

import os
import subprocess
import sys
from pathlib import Path


def make_link(link, target) -> str:
    """Create `link` pointing at `target`. Return the kind made
    ('junction' or 'symlink'). Raise on bad preconditions or failure.

    Accepts relative or absolute paths. Relative paths resolve against the
    current working directory (run from the workspace root).
    """
    link = Path(link)
    target = Path(target)
    if not target.exists():
        raise FileNotFoundError(f"target does not exist: {target}")
    if link.exists() or link.is_symlink():
        raise FileExistsError(f"link path already exists: {link}")
    link.parent.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        # argv form (no shell string) — nothing can corrupt the names.
        res = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            raise OSError(f"mklink failed: {(res.stdout + res.stderr).strip()}")
        return "junction"

    # POSIX: relative symlink so the link survives the tree being relocated.
    rel = os.path.relpath(target.resolve(), link.parent.resolve())
    os.symlink(rel, link, target_is_directory=True)
    return "symlink"


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: link_project.py <link> <target>", file=sys.stderr)
        sys.exit(1)
    try:
        kind = make_link(sys.argv[1], sys.argv[2])
    except (FileNotFoundError, FileExistsError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"{kind} created: {sys.argv[1]} -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
