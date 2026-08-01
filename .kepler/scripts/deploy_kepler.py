#!/usr/bin/env python3
"""deploy_kepler.py — propagate the Kepler skeleton to a sibling workspace.

The third leg of portability: install_lib.py makes the protocol travel,
bootstrap.py rebuilds a manager from nothing, this UPDATES a manager that
already lives on another drive (the user maintains several Kepler-applied
workspaces and previously copy-pasted by hand).

Doctrine (all mechanical, no judgment):
  * The manifest IS `git ls-files` at the source HEAD — the .gitignore
    whitelist made executable. By construction it can never contain
    .claude/settings.json, PROJECTS.md, repos/, or the tier folders.
  * Kepler's "version" is the skeleton repo's commit (hash + date) — the
    manager deliberately has no SemVer (CLAUDE.md §2).
  * A `.kepler-deployed` stamp (JSON: commit, date, file hashes) in the
    target records what was last deployed, so the next run can tell a
    file WE updated apart from a file the TARGET's owner edited.
  * Default is a dry-run report. --apply writes. Locally-modified files
    are never overwritten without --force; orphans never deleted without
    --prune. Refuses a dirty source (tracked files) unless --allow-dirty:
    a deploy should be reproducible from a commit.

Usage:
  python .kepler/scripts/deploy_kepler.py <target-workspace> [--apply]
         [--prune] [--force] [--allow-dirty]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

# cp949-safe console (Windows): keep output ASCII anyway.
for stream in (sys.stdout, sys.stderr):
    enc = (stream.encoding or "").lower()
    if enc not in ("utf-8", "utf8"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SOURCE = pathlib.Path(__file__).resolve().parents[2]
STAMP_NAME = ".kepler-deployed"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(SOURCE), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Propagate the Kepler skeleton to a sibling workspace.")
    ap.add_argument("target", help="target workspace root (another drive's Kepler workspace)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run report)")
    ap.add_argument("--prune", action="store_true", help="delete files a previous deploy placed that the source no longer ships")
    ap.add_argument("--force", action="store_true", help="overwrite files the target's owner modified locally")
    ap.add_argument("--allow-dirty", action="store_true", help="deploy even if source tracked files are uncommitted")
    args = ap.parse_args()

    target = pathlib.Path(args.target).resolve()

    # --- guards -------------------------------------------------------------
    if not target.is_dir():
        print(f"ERROR: target is not a directory: {target}")
        return 2
    if target == SOURCE or SOURCE in target.parents or target in SOURCE.parents:
        print("ERROR: target overlaps the source workspace — refusing.")
        return 2
    if (target / ".git").exists():
        print("NOTE: target has a .git — if it is a clone of ai-workspace, prefer")
        print("      `git pull --ff-only` there; this script is for plain copies.")
        print("      Continuing in copy mode (its .git is left untouched).")
    dirty = git("status", "--porcelain", "--untracked-files=no").strip()
    if dirty and not args.allow_dirty:
        print("ERROR: source has uncommitted tracked changes — a deploy should be")
        print("       reproducible from a commit. Commit first, or pass --allow-dirty.")
        print(dirty)
        return 2

    # --- source identity + manifest ------------------------------------------
    commit = git("rev-parse", "--short", "HEAD").strip()
    cdate = git("log", "-1", "--format=%cs").strip()
    manifest = [p for p in git("ls-files", "-z").split("\0") if p]

    # --- target stamp ---------------------------------------------------------
    stamp_path = target / STAMP_NAME
    stamp = {"commit": None, "date": None, "files": {}}
    if stamp_path.exists():
        try:
            stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
        except Exception:
            print(f"WARN: unreadable stamp {stamp_path} — treating as first deploy.")

    # --- classify -------------------------------------------------------------
    new, update, modified, current = [], [], [], []
    src_hashes: dict[str, str] = {}
    for rel in manifest:
        sp, tp = SOURCE / rel, target / rel
        sh = sha256(sp)
        src_hashes[rel] = sh
        if not tp.exists():
            new.append(rel)
        else:
            th = sha256(tp)
            if th == sh:
                current.append(rel)
            elif stamp["files"].get(rel) == th:
                update.append(rel)          # unchanged since last deploy -> safe
            else:
                modified.append(rel)        # target edited (or unknown provenance)

    orphaned = [rel for rel in stamp["files"]
                if rel not in src_hashes and (target / rel).exists()]

    # --- report ---------------------------------------------------------------
    mode = "DRY RUN" if not args.apply else "APPLY"
    prev = f"{stamp['commit']} ({stamp['date']})" if stamp.get("commit") else "none — first deploy"
    print(f"deploy-kepler [{mode}]")
    print(f"  source : {SOURCE}  @ {commit} ({cdate}){' [DIRTY]' if dirty else ''}")
    print(f"  target : {target}")
    print(f"  stamp  : {prev}")
    print(f"  manifest: {len(manifest)} files (git ls-files — settings.json/PROJECTS.md/tiers are outside it by construction)")
    print(f"    current        : {len(current)}")
    print(f"    new            : {len(new)}")
    print(f"    update         : {len(update)}   (target untouched since last deploy -> safe)")
    print(f"    local-modified : {len(modified)}   ({'OVERWRITING (--force)' if args.force else 'kept — pass --force to overwrite'})")
    print(f"    orphaned       : {len(orphaned)}   ({'DELETING (--prune)' if args.prune else 'kept — pass --prune to delete'})")
    for rel in modified:
        print(f"      [modified] {rel}")
    for rel in orphaned:
        print(f"      [orphaned] {rel}")

    if not args.apply:
        print("nothing written. Re-run with --apply.")
        return 0

    # --- apply ----------------------------------------------------------------
    to_copy = new + update + (modified if args.force else [])
    for rel in to_copy:
        tp = target / rel
        tp.parent.mkdir(parents=True, exist_ok=True)
        tp.write_bytes((SOURCE / rel).read_bytes())
    pruned = 0
    if args.prune:
        for rel in orphaned:
            (target / rel).unlink()
            pruned += 1

    stamp_out = {"commit": commit, "date": cdate, "files": src_hashes}
    stamp_path.write_text(json.dumps(stamp_out, indent=1), encoding="utf-8")
    kept = len(modified) if not args.force else 0
    print(f"applied: {len(to_copy)} copied, {pruned} pruned, {kept} local-modified kept; stamp -> {commit}")
    print("next: /sync-gravity per project in that workspace; bootstrap.py only if tiers/junctions are broken.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
