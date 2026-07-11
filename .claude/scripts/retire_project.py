#!/usr/bin/env python3
"""Retire an ai-workspace project — the destructive twin of new_project.py.

Two dispositions:
  archive  — keep the real files, move the project's view into archive/ (reversible).
  delete   — remove every junction AND the real folder (permanent).

Why this exists
---------------
Deleting a tier entry by hand has a specific footgun: a tier folder holds a
*directory junction*, and `rm -rf active/<name>` (or Explorer delete) can recurse
*through* the junction and destroy the real files in repos/. This script removes a
junction with `rmdir` (Windows) / `unlink` (POSIX) — which detaches the link only,
never the target — and deletes the real folder by an *independently resolved* real
path that it refuses to touch if it's actually a reparse point. argv-driven, so no
shell (bash/MSYS/cmd/PowerShell) can corrupt the name. Mirrors link_project.py.

Scope: filesystem mechanics only. The /retire command does the risk assessment,
PROJECTS.md reconciliation, and dashboard regen around this.

Usage:   python .claude/scripts/retire_project.py <archive|delete> <name>
Exit codes: 0 ok, 1 bad args / precondition, 2 a step failed.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent          # .claude/scripts
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent             # ai-workspace/
TIER_VIEWS = ("active", "stable", "dormant", "archive")


def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def is_reparse(p: Path) -> bool:
    """True if p is a junction/symlink rather than a real directory.
    realpath != abspath means the entry redirects elsewhere."""
    return os.path.realpath(p) != os.path.abspath(p)


def remove_link(link: Path):
    """Detach a junction/symlink WITHOUT following it into the target."""
    if os.name == "nt":
        # rmdir on a junction removes only the reparse point (never the target).
        res = subprocess.run(["cmd", "/c", "rmdir", str(link)],
                             capture_output=True, text=True)
        if res.returncode != 0:
            fail(f"could not detach junction {link}: "
                 f"{(res.stdout + res.stderr).strip()}", code=2)
    else:
        link.unlink()


def remove_real(folder: Path):
    """Delete a REAL directory tree. Refuses if it's actually a link, so we can
    never nuke a target through a junction."""
    if is_reparse(folder):
        fail(f"refusing to rmtree {folder}: it is a junction/symlink, not a real "
             "folder (would destroy the target). Detach it with remove_link instead.",
             code=2)
    shutil.rmtree(folder)


def find_views(name: str):
    """Return {tier: Path} for every tier view that currently holds <name>."""
    out = {}
    for tier in TIER_VIEWS:
        p = WORKSPACE_ROOT / tier / name
        if p.exists() or p.is_symlink():
            out[tier] = p
    return out


def find_real(name: str):
    """The real folder for <name>: repos/<name>."""
    repo = WORKSPACE_ROOT / "repos" / name
    if repo.exists() and not is_reparse(repo):
        return repo
    return None


def do_archive(name, views, real):
    if real is None:
        fail(f"no real folder found for '{name}' — nothing to archive.")
    # Detach any non-archive views (active/stable/dormant link).
    for tier, p in views.items():
        if tier == "archive":
            continue
        if is_reparse(p):
            remove_link(p)
            print(f"  detached {tier}/{name}")
    # Create the archive junction if absent.
    archive_link = WORKSPACE_ROOT / "archive" / name
    if not (archive_link.exists() or archive_link.is_symlink()):
        sys.path.insert(0, str(SCRIPT_DIR))
        from link_project import make_link  # noqa: E402
        make_link(archive_link, real)
        print(f"  archive/{name} -> repos/{name}")
    print(f"OK archived: {name} (real files preserved in repos/{name})")


def do_delete(name, views, real):
    # 1. Detach every junction view first (link-only removal).
    for tier, p in views.items():
        if is_reparse(p):
            remove_link(p)
            print(f"  detached {tier}/{name}")
    # 2. Delete the real folder.
    if real is not None:
        remove_real(real)
        print(f"  deleted real folder repos/{name}")
    elif not views:
        fail(f"'{name}' not found in any tier or repos/ — nothing to delete.")
    print(f"OK deleted: {name} (PERMANENT — no files remain)")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("archive", "delete"):
        fail("usage: retire_project.py <archive|delete> <name>")
    disposition, name = sys.argv[1], sys.argv[2].strip()
    if not name:
        fail("no project name given.")
    views = find_views(name)
    real = find_real(name)
    if not views and real is None:
        fail(f"'{name}' not found in any tier or in repos/.")
    print(f"Retiring '{name}' ({disposition}) — "
          f"views: {', '.join(views) or 'none'}; "
          f"real: {real.relative_to(WORKSPACE_ROOT) if real else 'none'}")
    if disposition == "archive":
        do_archive(name, views, real)
    else:
        do_delete(name, views, real)


if __name__ == "__main__":
    main()
