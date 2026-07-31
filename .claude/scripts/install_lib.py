#!/usr/bin/env python3
"""
install_lib.py — copy the gravity lib into a project, so the repo carries its
own instruments.

A gravity project is its own independent repo (workspace CLAUDE.md §2), so an
agent that clones it without this workspace sees `.gravity/` full of SPECs and
PLANs. The protocol card (`.gravity/GRAVITY.md`) already makes that repo
self-*describing*; this makes it self-*rendering*: with `.gravity/_lib/` present,
the clone can scan, check and render its own observatory with no workspace and
no third-party packages.

What travels (all of `gravity/lib/`, stdlib-only by rule):
    scan_project.py          the one scanner
    check_project.py         the project-scoped checks (+ a CLI)
    project_arg.py           which-project / where-output
    generate_observatory.py  the page
    generate_cosmos.py       Orbit 3D + the palette family
    palette.py               the 5-theme anchor hues (the declared owner)
    doc_theme.py             the browser-read doc stylesheet generator
    scan_db.py               the DB evidence pack reader (FK graph -> candidate domains)
    generate_boundary.py     the seam graph
    run_gate.py              the domain gate runner

What never travels: the workspace half (`.claude/scenarios/check.py`,
`scan_workspace.py`, `resolve_project.py`) — tiers, junctions and PROJECTS.md
are workspace rules and are never embedded in a project.

Usage:
    python .claude/scripts/install_lib.py <project-or-alias> [--dry-run]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
DIST = WORKSPACE / "gravity" / "lib"

# Bytecode is per-machine and per-interpreter — never part of the installed copy.
LIB_GITIGNORE = "__pycache__/\n"


def installed_version(project: Path) -> str:
    try:
        return (project / ".gravity" / "_lib" / "VERSION").read_text(
            encoding="utf-8").strip()
    except OSError:
        return ""


def install(project: Path, dry_run: bool = False) -> list[str]:
    """Copy every lib module + a VERSION stamp into <project>/.gravity/_lib/.
    Removes a stale pre-v4 `.gravity/lib/` install so a project never carries both.
    Returns the list of file names written."""
    gravity = project / ".gravity"
    if not gravity.is_dir():
        sys.exit(f"no .gravity/ in {project} — run /adopt-gravity first")

    version = (WORKSPACE / "gravity" / "VERSION").read_text(encoding="utf-8").strip()
    target = gravity / "_lib"
    sources = sorted(DIST.glob("*.py"))
    if not sources:
        sys.exit(f"no lib modules found in {DIST}")

    written = [p.name for p in sources] + ["VERSION", ".gitignore"]
    if dry_run:
        return written

    target.mkdir(parents=True, exist_ok=True)
    for src in sources:
        shutil.copy2(src, target / src.name)
    (target / "VERSION").write_text(version + "\n", encoding="utf-8")
    (target / ".gitignore").write_text(LIB_GITIGNORE, encoding="utf-8")
    # pre-v4 install target — an exact machine-managed copy, safe to drop once
    # `_lib/` exists (gravity v4 renamed machinery dirs with a `_` sigil).
    legacy = gravity / "lib"
    if legacy.is_dir():
        shutil.rmtree(legacy)
    return written


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="project name, alias, or path")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be written, change nothing")
    args = ap.parse_args(argv)

    as_path = Path(args.project).expanduser()
    if as_path.is_dir():
        name, path = as_path.resolve().name, as_path.resolve()
    else:
        sys.path.insert(0, str(WORKSPACE / ".claude" / "scripts"))
        from resolve_project import resolve  # noqa: E402
        name, path = resolve(args.project)

    before = installed_version(path) or "none"
    written = install(path, args.dry_run)
    after = installed_version(path) or "(dry run)"

    verb = "would install" if args.dry_run else "installed"
    print(f"{verb} {len(written)} file(s) -> {path / '.gravity' / '_lib'}")
    print(f"  {name}: lib {before} -> {after}")
    if not args.dry_run:
        print(f"  render it there: python .gravity/_lib/generate_observatory.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
