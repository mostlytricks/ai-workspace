#!/usr/bin/env python3
"""
bootstrap.py — make a workspace runnable, on this machine or a fresh one.

The portability gap this closes
-------------------------------
The root repo tracks only the **skeleton** (workspace CLAUDE.md §2): the meta
files, `gravity/`, and `.claude/` tooling. Every tier folder is denied, and
`PROJECTS.md` is git-ignored because it names private work. That is the right
boundary — but it means a fresh clone has no `repos/`, no tier folders, no
index, and no junctions. The protocol half of portability already shipped (the
lib travels with each project, so a clone renders and checks itself); this is
the **manager** half: reconstruct the shell the tiers live in.

It is equally useful on an established machine as **junction repair** — a
dangling or missing tier link is re-made from the index, which is the one thing
`PROJECTS.md` is authoritative about (workspace CLAUDE.md §7: one index of record).

What it does
------------
1. creates `repos/` + the four tier folders when absent;
2. seeds `PROJECTS.md` from `PROJECTS.sample.md` when absent (never overwrites
   an existing index — that file is the source of truth for tiers);
3. re-links every project in `repos/` that has no working junction, into the
   tier its `PROJECTS.md` row names — junction on Windows, relative symlink on
   POSIX, both via `link_project.py` so no shell can corrupt the paths;
4. removes and re-makes links that exist but dangle.

What it deliberately does NOT do
--------------------------------
- **Never guesses a tier.** A folder in `repos/` with no index row is reported,
  not filed — "it's probably active" is exactly the kind of invention that makes
  an index untrustworthy. Add the row (or use `/init-project`), then re-run.
- **Never clones.** Remotes live in each project's own `.git/config`; a manifest
  of them would name private repos, so exporting one is a deliberate act, not a
  side effect of bootstrapping.
- **Never edits an existing `PROJECTS.md`**, and never touches project contents.

Usage:
    python .claude/scripts/bootstrap.py [--dry-run]
Exit codes: 0 ok (or nothing to do), 1 something could not be reconciled.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from link_project import make_link                                   # noqa: E402

TIERS = ("active", "stable", "dormant", "archive")


def _linked_ok(path: Path) -> bool:
    """True when the tier entry exists AND resolves to a real directory.
    A dangling junction/symlink is 'exists but not a dir' — the case hand-made
    links fail into, and the one plain `.exists()` would miss on Windows."""
    return path.is_dir()


def _present(path: Path) -> bool:
    """True when anything occupies the path, including a dangling link."""
    return path.exists() or path.is_symlink() or os.path.lexists(path)


def ensure_dirs(write: bool) -> list[str]:
    made = []
    for name in ("repos",) + TIERS:
        d = WORKSPACE / name
        if not d.is_dir():
            made.append(name)
            if write:
                d.mkdir(parents=True, exist_ok=True)
    return made


def ensure_index(write: bool) -> str:
    pmd = WORKSPACE / "PROJECTS.md"
    sample = WORKSPACE / "PROJECTS.sample.md"
    if pmd.exists():
        return "present"
    if not sample.exists():
        return "MISSING (no PROJECTS.sample.md to seed from)"
    if write:
        shutil.copyfile(sample, pmd)
    return "seeded from PROJECTS.sample.md"


def main() -> int:
    # The Windows console defaults to cp949 here; the docstring carries non-ASCII.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()
    write = not args.dry_run
    tag = "" if write else "  (dry-run - nothing written)"
    print(f"workspace: {WORKSPACE}{tag}\n")

    made = ensure_dirs(write)
    print(f"  dirs     {'created ' + ', '.join(made) if made else 'all present'}")
    print(f"  index    PROJECTS.md {ensure_index(write)}")

    # The tier folders must exist before scanning, so on a genuine dry-run over a
    # bare clone the scan simply sees nothing — reported honestly rather than faked.
    sys.path.insert(0, str(WORKSPACE / ".claude" / "dashboard"))
    from scan_workspace import scan                                  # noqa: E402
    facts = scan(WORKSPACE)

    repaired, linked, undecidable, failed = [], [], [], []

    # A repos/ folder with neither a junction nor an index row never reaches
    # facts["projects"] (that dict is keyed by on-disk tiers + index rows), so it
    # would silently vanish from this report. It is exactly the case a human must
    # decide, so it is surfaced rather than dropped.
    for name in facts["orphans"]:
        if name not in facts["projects"]:
            undecidable.append(name)

    for name, entry in sorted(facts["projects"].items()):
        if not entry["in_repos"]:
            continue                       # index row with no folder — /triage's job, not ours
        row = entry["index"]
        target = WORKSPACE / "repos" / name

        # A working junction in any tier means this project is reachable.
        live = [t for t in entry["tiers"] if _linked_ok(WORKSPACE / t / name)]
        dangling = [t for t in TIERS
                    if _present(WORKSPACE / t / name) and not _linked_ok(WORKSPACE / t / name)]

        for tier in dangling:
            link = WORKSPACE / tier / name
            repaired.append(f"{tier}/{name}")
            if write:
                try:
                    link.unlink()
                except (OSError, PermissionError):
                    try:
                        link.rmdir()
                    except OSError as e:
                        failed.append(f"{tier}/{name}: could not remove dangling link ({e})")
                        continue

        if live and not dangling:
            continue                       # already fine

        if row is None:
            undecidable.append(name)
            continue

        tier = row["listed_tier"]
        link = WORKSPACE / tier / name
        if _linked_ok(link):
            continue
        if write:
            try:
                kind = make_link(link, target)
                linked.append(f"{tier}/{name} -> repos/{name} ({kind})")
            except (OSError, FileExistsError, FileNotFoundError) as e:
                failed.append(f"{tier}/{name}: {e}")
        else:
            linked.append(f"{tier}/{name} -> repos/{name}")

    print()
    for label, items in (("repaired dangling", repaired), ("linked", linked)):
        for it in items:
            print(f"  {label:18} {it}")
    # Recount from disk AFTER the repairs — reporting the pre-run count would
    # under-report exactly the links this run just fixed.
    n_ok = sum(1 for tier in TIERS for p in (WORKSPACE / tier).iterdir()
               if _linked_ok(p)) if (WORKSPACE / TIERS[0]).is_dir() else 0
    print(f"\n  {n_ok} link(s) verified, {len(linked)} made, {len(repaired)} repaired")

    if undecidable:
        print("\n  NOT filed - no PROJECTS.md row names a tier for these "
              "(a tier is never guessed):")
        for n in sorted(set(undecidable)):
            print(f"    repos/{n}")
        print("  Add the row (or run /init-project) and re-run.")

    if failed:
        print("\n  FAILED:")
        for f in failed:
            print(f"    {f}")
        return 1

    # Honest emptiness: the seeded index carries example rows, so "no index rows"
    # is the wrong test — what matters is whether any real project is on disk.
    if not any(e["in_repos"] for e in facts["projects"].values()) and not facts["orphans"]:
        print("\n  No projects on disk yet. Clone your repos into repos/, add their "
              "PROJECTS.md rows, then re-run to create the tier links.")
    print("\nOK - workspace runnable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
