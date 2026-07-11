#!/usr/bin/env python3
"""
resolve_project.py — turn a short token into a canonical project.

Gravity projects have long kebab-case names (`architecture-memory-os`,
`multi-system-maintenance-agent-system`). Typing those into every command is
painful, so this resolver lets you say `amos` or `compass` instead.

**Project-owned, with a derived fallback.** The alias is a per-project identity
fact, so its home is the project's own root `CLAUDE.md` — a `> alias: <slug>`
line next to the `> gravity:` stamp (seeded from `CLAUDE.template.md`). There is
deliberately NO central registry file; PROJECTS.md stays the workspace index, not
an alias table. Resolution order:

  1. exact           — the token is already a project name.
  2. declared alias  — the `> alias:` slug a project declares in its CLAUDE.md
                       (authoritative — you own it per project).
  3. unique acronym  — the hyphen-segment initials as a convenience: amos, msmas
                       (short <=2-char tail segments like `os` kept whole).
  4. unique substring — `compass` -> capability-compass.
  5. ambiguous / none — list candidates and refuse to guess.

So a project gets a free derived alias immediately, and can *claim* an intentional
one (like AMOS -> `amos`) by adding the line to its CLAUDE.md.

Importable: `from resolve_project import resolve` -> (name, path).
CLI: `python resolve_project.py <token>` prints the resolved path (exit 0),
     or the candidate list to stderr (exit 2) when it can't resolve uniquely.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Tiers scanned for projects, in precedence order (first hit wins for the path).
TIERS = ("repos", "active", "stable", "dormant", "archive")

# Names that live under a tier folder but aren't real projects.
IGNORE = {"_example_"}


def workspace_root() -> Path:
    """.claude/scripts/resolve_project.py -> ai-workspace/ (three parents up)."""
    return Path(__file__).resolve().parent.parent.parent


def find_projects(root: Path | None = None) -> dict[str, Path]:
    """Map canonical project name -> its best existing path across the tiers."""
    root = root or workspace_root()
    projects: dict[str, Path] = {}
    for tier in TIERS:
        tier_dir = root / tier
        if not tier_dir.is_dir():
            continue
        for p in sorted(tier_dir.iterdir()):
            if p.is_dir() and p.name not in IGNORE and not p.name.startswith("."):
                projects.setdefault(p.name, p)  # first tier in precedence wins
    return projects


def acronym(name: str) -> str:
    """Hyphen-segment initials, skipping empty segments (double-hyphen names)."""
    return "".join(seg[0] for seg in name.split("-") if seg)


def acronym_forms(name: str) -> set[str]:
    """The acronym(s) a human might type. Two forms:
      - pure initials:            architecture-memory-os -> 'amo'
      - short (<=2 char) segments kept whole: -> 'amos' (a + m + os)
    People keep tiny trailing tokens like 'os'/'ai'/'db' whole, so accept both."""
    segs = [s for s in name.split("-") if s]
    initials = "".join(s[0] for s in segs)
    short_whole = "".join(s if len(s) <= 2 else s[0] for s in segs)
    return {initials, short_whole}


# A `> alias: amos` (or `> **alias:** `amos``) line in a project's root CLAUDE.md.
_ALIAS_RE = re.compile(r"(?im)^>\s*\**alias:?\**\s*`?([a-z0-9][a-z0-9-]*)`?")


def declared_aliases(projects: dict[str, Path]) -> dict[str, str]:
    """Read each project's root CLAUDE.md for its self-declared `> alias:` slug.
    Returns alias -> project name. A slug two projects both claim is dropped as
    ambiguous (neither wins) rather than silently resolving to one."""
    claimed: dict[str, str] = {}
    clashed: set[str] = set()
    for name, path in projects.items():
        claude = path / "CLAUDE.md"
        if not claude.exists():
            continue
        m = _ALIAS_RE.search(claude.read_text(encoding="utf-8"))
        if not m:
            continue
        alias = m.group(1).lower()
        if alias == name:
            continue  # declaring your own name as an alias is a no-op
        if alias in claimed and claimed[alias] != name:
            clashed.add(alias)
        else:
            claimed[alias] = name
    for a in clashed:
        claimed.pop(a, None)
    return claimed


class ResolutionError(Exception):
    def __init__(self, token: str, candidates: list[str]):
        self.token = token
        self.candidates = candidates
        if candidates:
            msg = f"'{token}' is ambiguous — candidates: {', '.join(candidates)}"
        else:
            msg = f"'{token}' matched no project"
        super().__init__(msg)


def resolve(token: str, root: Path | None = None) -> tuple[str, Path]:
    """Resolve a token to (canonical_name, path). Raises ResolutionError if it
    can't land on exactly one project."""
    root = root or workspace_root()
    projects = find_projects(root)
    names = list(projects)
    t = token.strip().lower()

    # 1. exact
    if t in projects:
        return t, projects[t]

    # 2. declared alias (project-owned, from its CLAUDE.md) — authoritative
    declared = declared_aliases(projects)
    if t in declared:
        name = declared[t]
        return name, projects[name]

    # 3. unique acronym (either form — initials, or short tail segments kept whole)
    acro = [n for n in names if t in acronym_forms(n)]
    if len(acro) == 1:
        return acro[0], projects[acro[0]]

    # 4. unique substring
    sub = [n for n in names if t in n.lower()]
    if len(sub) == 1:
        return sub[0], projects[sub[0]]

    # 5. ambiguous or nothing
    candidates = sorted(set(acro) | set(sub))
    raise ResolutionError(token, candidates)


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: resolve_project.py <token>", file=sys.stderr)
        return 2
    try:
        name, path = resolve(args[0])
    except ResolutionError as e:
        print(str(e), file=sys.stderr)
        return 2
    # Print the path on stdout (usable in shell: cd "$(resolve_project.py amos)").
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
