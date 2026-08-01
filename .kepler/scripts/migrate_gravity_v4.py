#!/usr/bin/env python3
"""
migrate_gravity_v4.py — the mechanical half of the gravity v4.0.0 upgrade:
rename a project's machinery dirs to their `_` sigil names and repoint every
project-authored reference.

v4's rule: a leading `_` marks gravity machinery, never a domain —
    .gravity/lib/          -> .gravity/_lib/
    .gravity/observatory/  -> .gravity/_observatory/
    .gravity/inbox/        -> .gravity/_inbox/
    .gravity/given/        -> .gravity/_given/     (root AND per-domain)

What it does, in order (per project):
  1. refuse a dirty worktree — the rename must be the only thing in the commit
  2. `git mv` (or plain rename, for untracked dirs) the four machinery dirs
  3. rewrite project-authored path references with ANCHORED patterns
     (`\\.gravity/lib\\b` can never touch a domain named `library`); historical
     files (project CHANGELOG.md, docs/walkthroughs/) stay verbatim
  4. reinstall the lib (install_lib.py -> `_lib/`, drops a stale `lib/`),
     re-copy the protocol family (card + both HTML guides — they never
     separate), bump the router fences to the current version
  5. run `check.py consistency` and report
  6. commit `gravity v4.0.0 migration: machinery dirs -> _sigil` (--apply only)

Never pushes. Dry-run is the default: it prints every rename and rewrite it
would do and changes nothing.

Usage:
    python .kepler/scripts/migrate_gravity_v4.py <project-or-alias> [--apply]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SCRIPTS = WORKSPACE / ".kepler" / "scripts"

RENAMES = [("lib", "_lib"), ("observatory", "_observatory"),
           ("inbox", "_inbox"), ("given", "_given")]

# Anchored path rewrites. `\b` after `lib` cannot match `library` (b->r is not
# a word boundary), and `(?<!_)` keeps an already-migrated reference stable.
REWRITE_RULES = [
    (re.compile(r"\.gravity/(?!_)(lib|observatory|inbox|given)\b"), r".gravity/_\1"),
    (re.compile(r"\.gravity\\(?!_)(lib|observatory|inbox|given)\b"), r".gravity\\_\1"),
    # per-domain given: `<slug>/given/...` and the manifest citation form
    (re.compile(r"(?<![\w/])([A-Za-z0-9][\w.-]*)/given/"), r"\1/_given/"),
    (re.compile(r"source:\s*given/"), "source: _given/"),
]
# ROUTER.md Doc-Map trees list machinery dirs bare at line start.
ROUTER_TREE_RULE = (re.compile(r"^(\s*)(lib|observatory|inbox|given)/", re.M),
                    r"\1_\2/")

TEXT_SUFFIXES = {".md", ".html", ".txt", ".js", ".ts", ".tsx", ".jsx", ".py",
                 ".json", ".yaml", ".yml", ".toml", ".css", ".mjs", ".cjs"}
SKIP_PARTS = {".git", "node_modules", ".venv", "dist", "build", "coverage",
              "_lib", "_observatory", "lib", "observatory"}
# The durable record stays as written: pruning history is not migration.
HISTORICAL = ("CHANGELOG.md",)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    # Child output is UTF-8 (check.py reconfigures its streams); decoding with
    # the Windows-default cp949 kills the reader thread mid-run.
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def resolve(token: str) -> tuple[str, Path]:
    as_path = Path(token).expanduser()
    if as_path.is_dir():
        root = as_path.resolve()
        return root.name, root
    sys.path.insert(0, str(SCRIPTS))
    from resolve_project import resolve as _resolve  # noqa: E402
    return _resolve(token)


def machinery_targets(gravity: Path) -> list[tuple[Path, Path]]:
    """Every (old, new) rename this project actually needs."""
    out = []
    for old, new in RENAMES:
        if (gravity / old).is_dir():
            out.append((gravity / old, gravity / new))
    for p in sorted(gravity.glob("*/given")):
        if p.is_dir() and not p.parent.name.startswith("_"):
            out.append((p, p.parent / "_given"))
    return out


def is_historical(rel: Path) -> bool:
    if rel.name in HISTORICAL and len(rel.parts) == 1:
        return True
    return "walkthroughs" in rel.parts


def rewrite_files(project: Path, apply: bool) -> list[str]:
    """Anchored path rewrites over project-authored text files. Returns the
    list of `path (n)` entries touched (or that would be)."""
    touched = []
    candidates = [p for p in project.rglob("*")
                  if p.is_file()
                  and (p.suffix.lower() in TEXT_SUFFIXES or p.name == ".gitignore")
                  and not (set(p.relative_to(project).parts) & SKIP_PARTS)]
    for p in sorted(candidates):
        rel = p.relative_to(project)
        if is_historical(rel):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new_text, n = text, 0
        for rx, repl in REWRITE_RULES:
            new_text, k = rx.subn(repl, new_text)
            n += k
        if rel.name == "ROUTER.md":
            new_text, k = ROUTER_TREE_RULE[0].subn(ROUTER_TREE_RULE[1], new_text)
            n += k
        if n:
            touched.append(f"{rel.as_posix()} ({n})")
            if apply:
                p.write_text(new_text, encoding="utf-8")
    return touched


def rename_dirs(project: Path, targets, apply: bool) -> None:
    for old, new in targets:
        tracked = run(["git", "ls-files", "--", str(old.relative_to(project).as_posix())],
                      project).stdout.strip()
        verb = "git mv" if tracked else "rename"
        print(f"  {verb}: {old.relative_to(project).as_posix()} -> "
              f"{new.relative_to(project).as_posix()}")
        if not apply:
            continue
        if tracked:
            cp = run(["git", "mv", str(old), str(new)], project)
            if cp.returncode != 0:
                sys.exit(f"git mv failed: {cp.stderr.strip()}")
        else:
            shutil.move(str(old), str(new))


def bump_fences(project: Path, version_mm: str, apply: bool) -> list[str]:
    """Rewrite the fenced gravity:router block in every root harness file from
    the template, stamped with the target major.minor."""
    template = (WORKSPACE / "gravity" / "templates" / "GRAVITY.template.md"
                ).read_text(encoding="utf-8")
    fenced = template.split("-->\n", 1)[1].strip()          # drop the top comment
    fenced = fenced.replace("v<X.Y>", f"v{version_mm}")
    fence_rx = re.compile(
        r"<!-- gravity:router[^\n]*-->.*?<!-- /gravity:router -->", re.S)
    done = []
    for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules"):
        f = project / name
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        if not fence_rx.search(text):
            continue
        if apply:
            f.write_text(fence_rx.sub(lambda _: fenced, text, count=1),
                         encoding="utf-8")
        done.append(name)
    return done


# The protocol family travels together (v4.2.0): the stamped card plus the two
# unstamped browser-read guides — the card carries the version for all three.
# Copying the card without the guides leaves a project at the current stamp
# with its human half missing, which no checker catches (PROTOCOL_STALE only
# reads the card).
PROTOCOL_FAMILY = [
    ("GRAVITY-PROTOCOL.md", "GRAVITY.md"),
    ("GRAVITY-GUIDE.html", "GRAVITY.html"),
    ("GRAVITY-GUIDE.ko.html", "GRAVITY.ko.html"),
]


def strip_header_comment(text: str) -> str:
    """Drop the source's own copy-note comment, keeping anything before it
    (the guides open with `<!doctype html>` ahead of theirs)."""
    start = text.find("<!--")
    end = text.find("-->", start)
    if start == -1 or end == -1:
        sys.exit("protocol source carries no header comment — refusing to copy raw")
    head = text[:start].rstrip("\n")
    body = text[end + 3:].lstrip("\n")
    return (head + "\n" + body) if head else body


def recopy_card(project: Path, version_mm: str, apply: bool) -> bool:
    if not (project / ".gravity" / "GRAVITY.md").exists():
        return False
    for src_name, dst_name in PROTOCOL_FAMILY:
        body = strip_header_comment(
            (WORKSPACE / "gravity" / src_name).read_text(encoding="utf-8"))
        body = body.replace("v<X.Y>", f"v{version_mm}")
        if apply:
            (project / ".gravity" / dst_name).write_text(body, encoding="utf-8")
    return True


def migrate(token: str, apply: bool) -> int:
    name, project = resolve(token)
    gravity = project / ".gravity"
    if not gravity.is_dir():
        print(f"{name}: no .gravity/ — nothing to migrate")
        return 0
    if not (project / ".git").exists():
        sys.exit(f"{name}: not a git repo — refusing (the rename must be a commit)")

    dirty = run(["git", "status", "--porcelain"], project).stdout.strip()
    if dirty:
        sys.exit(f"{name}: worktree not clean — commit or stash first:\n{dirty}")

    version = (WORKSPACE / "gravity" / "VERSION").read_text(encoding="utf-8").strip()
    version_mm = ".".join(version.split(".")[:2])
    mode = "APPLY" if apply else "DRY RUN (nothing written; pass --apply)"
    print(f"== {name} -> gravity v{version} == {mode}")

    targets = machinery_targets(gravity)
    if not targets:
        print("  machinery dirs: already migrated (or absent)")
    rename_dirs(project, targets, apply)

    touched = rewrite_files(project, apply)
    for t in touched:
        print(f"  rewrite: {t}")
    if not touched:
        print("  rewrite: no project-authored references found")

    if apply:
        cp = run([sys.executable, str(SCRIPTS / "install_lib.py"), str(project)],
                 WORKSPACE)
        print("  " + (cp.stdout.strip().splitlines() or ["install_lib: no output"])[0])
        if cp.returncode != 0:
            sys.exit(f"install_lib failed: {cp.stderr.strip()}")
    else:
        print(f"  would reinstall lib -> .gravity/_lib/ (v{version})")

    if recopy_card(project, version_mm, apply):
        print(f"  protocol family: GRAVITY.md + GRAVITY.html + GRAVITY.ko.html "
              f"re-copied, card stamped v{version_mm}")
    fences = bump_fences(project, version_mm, apply)
    if fences:
        print(f"  fences -> v{version_mm}: {', '.join(fences)}")

    if apply:
        check = run([sys.executable,
                     str(WORKSPACE / ".kepler" / "scenarios" / "check.py"),
                     "consistency", "--project", str(project)], WORKSPACE)
        tail = (check.stdout.strip().splitlines() or [""])[-1]
        print(f"  check consistency: {tail}")
        for bad in ("MACHINERY_UNMIGRATED", "LIB_MISSING", "LIB_STALE",
                    "PROTOCOL_MISSING", "PROTOCOL_STALE"):
            if bad in check.stdout:
                sys.exit(f"{name}: {bad} still present after migration — inspect before committing")
        run(["git", "add", "-A"], project)
        cp = run(["git", "commit", "-m",
                  "gravity v4.0.0 migration: machinery dirs -> _sigil\n\n"
                  "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"], project)
        if cp.returncode != 0:
            sys.exit(f"git commit failed: {cp.stderr.strip() or cp.stdout.strip()}")
        print(f"  committed: {run(['git', 'rev-parse', '--short', 'HEAD'], project).stdout.strip()}")
    return 0


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="gravity v4 machinery-dir migration")
    ap.add_argument("projects", nargs="+", help="project name(s), alias(es), or path(s)")
    ap.add_argument("--apply", action="store_true",
                    help="write, reinstall, verify and commit (default: dry run)")
    args = ap.parse_args(argv)
    for token in args.projects:
        migrate(token, args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
