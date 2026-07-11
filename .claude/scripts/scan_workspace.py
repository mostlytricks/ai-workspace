#!/usr/bin/env python3
"""Scan the live workspace and emit JSON facts — the mechanical backend for
/dashboard and /triage (and check.py's `workspace` checker).

Why this exists: those commands used to make the runtime LLM hand-roll disk
scanning, date arithmetic, stencil/bloat detection, and PROJECTS.md↔disk
reconciliation on every run — exactly the work a weaker model gets quietly
wrong. This script computes the FACTS once, deterministically; the LLM keeps
only judgment (doc-pipeline drift, non-goals) and formatting. Same pattern as
check.py: one scanner, many callers.

Boundary: staleness is a FACT here (days_ago + class), never a FINDING —
judging age is the caller's decision (and date-dependent checks would rot
scenario fixtures). Structural drift findings live in `check.py workspace`,
which imports scan() from this file.

Stdlib only. Reuses the dashboard's parsers (parse_projects / days_ago /
gravity_adoption) so facts stay single-sourced.

Usage:
    python .claude/scripts/scan_workspace.py             # compact JSON
    python .claude/scripts/scan_workspace.py --pretty    # indented JSON
    python .claude/scripts/scan_workspace.py --adoption-table
        # ready-to-paste markdown "Gravity adoption" table, computed from disk
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent               # .claude/scripts
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent                  # ai-workspace/
sys.path.insert(0, str(WORKSPACE_ROOT / ".claude" / "dashboard"))
from generate_dashboard import (  # noqa: E402
    TIERS, days_ago, gravity_adoption, parse_projects,
)

TIER_NAMES = [name for name, _, _ in TIERS]                # active stable dormant archive

# Literal markers left behind by an unfilled CONTEXT.template.md copy.
STENCIL_MARKERS = (
    "Last touched: YYYY-MM-DD",
    "# CONTEXT — <project name>",
    "The single most important thing for the next agent session",
    "What structural changes were made in the most recent session",
)

LAST_TOUCHED_RE = re.compile(r"^Last touched:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def _staleness(n: int | None) -> str:
    if n is None:
        return "unknown"
    if n >= 30:
        return "very-stale"
    if n >= 14:
        return "stale"
    return "fresh"


def _section_lines(text: str, header_prefix: str) -> list[str]:
    """Lines of the `## <header…>` section, up to the next `## `."""
    out: list[str] = []
    capturing = False
    for line in text.splitlines():
        if line.startswith("## "):
            if capturing:
                break
            capturing = line[3:].strip().lower().startswith(header_prefix.lower())
            continue
        if capturing:
            out.append(line)
    return out


def _context_facts(real: Path, today: date) -> dict:
    ctx = real / "CONTEXT.md"
    if not ctx.exists():
        return {"exists": False}
    try:
        text = ctx.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {"exists": False}
    m = LAST_TOUCHED_RE.search(text)
    last = m.group(1) if m else ""
    n = days_ago(last, today)
    next_lines = [ln.strip() for ln in _section_lines(text, "Next Step") if ln.strip()]
    completed = [ln for ln in _section_lines(text, "Completed") if ln.lstrip().startswith("- ")]
    return {
        "exists": True,
        "last_touched": last,
        "days_ago": n,
        "staleness": _staleness(n),
        "lines": len(text.splitlines()),
        "completed_bullets": len(completed),
        "stencil": any(mk in text for mk in STENCIL_MARKERS),
        "next_step": next_lines[0][:240] if next_lines else "",
    }


def scan(root: Path | None = None, today: date | None = None) -> dict:
    """All workspace facts as one JSON-serializable dict.

    `root` defaults to the live workspace; passing another tree (a scenario
    fixture) also repoints the dashboard module's WORKSPACE_ROOT so its
    gravity_adoption() reads the fixture's repos/, not the real one."""
    import generate_dashboard
    root = Path(root) if root else WORKSPACE_ROOT
    today = today or date.today()
    generate_dashboard.WORKSPACE_ROOT = root

    # tiers on disk — record EVERY tier a name appears in (multi-tier is drift)
    on_disk: dict[str, list[str]] = {}
    for tier in TIER_NAMES:
        tdir = root / tier
        if not tdir.is_dir():
            continue
        for p in sorted(tdir.iterdir()):
            if p.is_dir() and not p.name.startswith(".") and p.name != "_example_":
                on_disk.setdefault(p.name, []).append(tier)

    repos_dir = root / "repos"
    in_repos = {p.name for p in repos_dir.iterdir()
                if p.is_dir() and not p.name.startswith(".")} if repos_dir.is_dir() else set()

    # index rows (PROJECTS.md) — reuse the dashboard parser
    index_text = ""
    pmd = root / "PROJECTS.md"
    if pmd.exists():
        index_text = pmd.read_text(encoding="utf-8", errors="ignore")
    indexed = parse_projects(index_text)                    # {tier: [{name, stack, date, focus}]}
    index_by_name: dict[str, dict] = {}
    for tier, rows in indexed.items():
        for row in rows:
            # canonical key = first token; rows may carry alias/rename annotations
            # like "sol _(formerly `agent-view-desktop`)_"
            canonical = row["name"].split()[0]
            index_by_name[canonical] = {"listed_tier": tier, "stack": row["stack"],
                                        "row_date": row["date"], "focus": row["focus"],
                                        "row_name": row["name"]}

    all_names = sorted(set(on_disk) | set(index_by_name))
    projects: dict[str, dict] = {}
    for name in all_names:
        real = root / "repos" / name
        entry: dict = {
            "tiers": on_disk.get(name, []),
            "in_repos": name in in_repos,
            "context": _context_facts(real, today) if real.is_dir() else {"exists": False},
            "index": index_by_name.get(name),               # None = not indexed
            "adoption": gravity_adoption(name),
        }
        projects[name] = entry

    return {
        "generated": today.isoformat(),
        "tier_counts": {t: sum(1 for v in on_disk.values() if t in v) for t in TIER_NAMES},
        "projects": projects,
        "orphans": sorted(n for n in in_repos if n not in on_disk),
        "multi_tier": sorted(n for n, ts in on_disk.items() if len(ts) > 1),
        "index_only": sorted(n for n in index_by_name if n not in on_disk),
        "not_indexed": sorted(n for n in on_disk if n not in index_by_name),
    }


def adoption_table(facts: dict) -> str:
    """The PROJECTS.md 'Gravity adoption' table, computed live from disk."""
    lines = ["| Project | stamp | docs | card | rel | codex |", "|---|---|---|---|---|---|"]
    for name, p in facts["projects"].items():
        if not p["in_repos"]:
            continue
        a = p["adoption"]
        if a["docsys"] is None:
            continue                                        # no CLAUDE.md → not a gravity project
        stamp = f"`v{a['stamp']}`" if a["stamp"] else "—"
        docs = "`.gravity`" if a["docsys"] == "gravity" else "flat"
        card = (f"`v{a['card']}`" if a["card"] else "—") if a["docsys"] == "gravity" else "n/a"
        rel = "✓" if a["release"] else "—"
        codex = "✓" if a["shim"] else "—"
        suffix = " _(dormant)_" if p["tiers"] == ["dormant"] else ""
        lines.append(f"| {name}{suffix} | {stamp} | {docs} | {card} | {rel} | {codex} |")
    return "\n".join(lines)


def main() -> None:
    for stream in (sys.stdout, sys.stderr):                 # Windows consoles choke on ✓/—
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    facts = scan()
    if "--adoption-table" in sys.argv:
        print(adoption_table(facts))
    elif "--pretty" in sys.argv:
        print(json.dumps(facts, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(facts, ensure_ascii=False))


if __name__ == "__main__":
    main()
