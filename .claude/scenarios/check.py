#!/usr/bin/env python3
"""
check.py — structural-invariant checker for a `.gravity/` doc system.

The one asset behind gravity's golden-scenarios (acceptance) AND `/triage`
(drift detection). It answers a single mechanical question that gravity used to
trust to prose: **is every `.gravity/<domain>/` folder wired into all four
registry indexes, and does every index row point at a real folder?**

The four registry owners (workspace CLAUDE.md §6):
  1. existence  -> the `.gravity/<domain>/` folder itself
  2. routing    -> root CLAUDE.md  (Doc Map block + the router table)
  3. why        -> .gravity/MISSION.html  ("the system in N domains" row)
  4. status     -> .gravity/IMPLEMENTATION_PLAN.md  (the per-domain status spine)

Parsing is **heuristic slug-match** (by design — see scenarios/README.md): a
domain is "wired" into an index region if its kebab-case slug appears in that
region. Fixtures are author-controlled, so this is robust enough; harden with
machine-readable anchors only if real projects start tripping it.

Usage:
  python check.py consistency --project DIR
  python check.py scenario   --scenario SCENARIO_DIR --actual DIR
  python check.py selftest

Importable too: `from check import check_gravity_consistency` returns the
findings list, so `/triage` can call the same core.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# Top-level .gravity/ entries that are cross-cutting docs, NOT subject domains.
CROSS_CUTTING = {
    "MISSION.html",
    "ARCHITECTURE.html",
    "IMPLEMENTATION_PLAN.md",
    "DESIGN.md",
    "README.md",
}

# The four index regions a domain must appear in, by id -> human label.
REGIONS = {
    "doc_map": "CLAUDE.md Doc Map",
    "router": "CLAUDE.md router table (it has a SPEC.md, so it needs a read-first row)",
    "mission": "MISSION.html domain row",
    "plan": "IMPLEMENTATION_PLAN.md status spine",
}

FAIL = "FAIL"
WARN = "WARN"


@dataclass
class Finding:
    severity: str   # FAIL | WARN
    code: str       # UNDERWIRED | ORPHAN_ROUTE | MISSING_FILE | STRUCTURE
    domain: str     # the slug it concerns ("" if structural)
    region: str     # which index/region ("" if n/a)
    message: str

    def __str__(self) -> str:
        tag = f"[{self.severity}] {self.code}"
        where = f" {self.domain}" if self.domain else ""
        return f"{tag}{where}: {self.message}"


# --------------------------------------------------------------------------- #
# parsing helpers
# --------------------------------------------------------------------------- #

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _section(text: str, header_prefix: str) -> str:
    """Return the markdown section whose `## ` heading starts with header_prefix,
    up to (but excluding) the next `## ` heading. Empty string if not found."""
    return _section_by(text, lambda h: h.startswith(header_prefix.lower()))


def _section_by(text: str, predicate) -> str:
    """Return the markdown section whose `## ` heading text (lowercased) satisfies
    `predicate`, up to the next `## `. Empty string if none matches."""
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            if predicate(line[3:].strip().lower()):
                capturing = True
                continue
        if capturing:
            out.append(line)
    return "\n".join(out)


def _slug_in(text: str, slug: str) -> bool:
    """True if the kebab-case slug appears as a token in text."""
    return re.search(rf"(?<![\w-]){re.escape(slug)}(?![\w-])", text) is not None


def discover_domains(gravity_dir: Path) -> set[str]:
    """The subject-domain folders under .gravity/ (directories only, minus
    cross-cutting docs which are files anyway)."""
    if not gravity_dir.is_dir():
        return set()
    return {
        p.name
        for p in gravity_dir.iterdir()
        if p.is_dir() and p.name not in CROSS_CUTTING and not p.name.startswith(".")
    }


# --------------------------------------------------------------------------- #
# the core check
# --------------------------------------------------------------------------- #

def check_gravity_consistency(project_dir: str | Path) -> list[Finding]:
    """Return every structural inconsistency between the .gravity/ domain folders
    and the four registry indexes. Empty list == clean."""
    project = Path(project_dir)
    gravity = project / ".gravity"
    findings: list[Finding] = []

    if not gravity.is_dir():
        return [Finding(FAIL, "STRUCTURE", "", "",
                        f"no .gravity/ directory at {project}")]

    claude = _read(project / "CLAUDE.md")
    mission = _read(gravity / "MISSION.html")
    plan = _read(gravity / "IMPLEMENTATION_PLAN.md")

    doc_map = _section(claude, "Doc Map") or claude   # tolerate an unsplit CLAUDE.md
    router = _section(claude, "What to read before a change") or claude
    # Status spine = the heading mentioning BOTH "status" and "domain"
    # (e.g. "Domain status spine" / "Per-domain status"); never "Status right now".
    spine = _section_by(plan, lambda h: "status" in h and "domain" in h) or plan

    domains = discover_domains(gravity)

    # UNDERWIRED — a folder missing from an index it's *required* to be in.
    # Required everywhere: Doc Map (navigation), MISSION row (why), PLAN spine (status).
    # Router-table row is gravity-gated: required ONLY once the domain has a SPEC.md
    # (CLAUDE.md §6 / GRAVITY.template — the router row is added when a SPEC exists).
    for slug in sorted(domains):
        folder = gravity / slug
        checks = [
            ("doc_map", _slug_in(doc_map, slug)),
            ("mission", _slug_in(mission, slug)),
            ("plan", _slug_in(spine, slug)),
        ]
        if (folder / "SPEC.md").exists():
            checks.append(("router", _slug_in(router, slug)))
        for region_id, present in checks:
            if not present:
                findings.append(Finding(
                    FAIL, "UNDERWIRED", slug, region_id,
                    f"folder .gravity/{slug}/ is not wired into the {REGIONS[region_id]}",
                ))
        # A domain folder with NO recognized doc at all is an empty husk.
        recognized = (list(folder.glob("PLAN*.md"))
                      + list(folder.glob("SPEC.md"))
                      + list(folder.glob("ARCHITECTURE.html")))
        if not recognized:
            findings.append(Finding(
                WARN, "MISSING_FILE", slug, "",
                f".gravity/{slug}/ has no PLAN/SPEC/ARCHITECTURE doc (empty domain folder)",
            ))

    # 2. ORPHAN_ROUTE — a `.gravity/<slug>/` reference with no such folder.
    #    WARN, not FAIL: templates legitimately ship example rows (e.g. integration).
    for slug in sorted(set(re.findall(r"\.gravity/([a-z0-9][a-z0-9-]*)/", claude))):
        if slug not in domains and slug not in CROSS_CUTTING:
            findings.append(Finding(
                WARN, "ORPHAN_ROUTE", slug, "router",
                f"CLAUDE.md references .gravity/{slug}/ but no such folder exists",
            ))

    return findings


# --------------------------------------------------------------------------- #
# CLI subcommands
# --------------------------------------------------------------------------- #

def _print(findings: list[Finding]) -> tuple[int, int]:
    fails = sum(1 for f in findings if f.severity == FAIL)
    warns = sum(1 for f in findings if f.severity == WARN)
    for f in findings:
        print("  " + str(f))
    return fails, warns


def _resolve_project_arg(arg: str) -> str:
    """Accept a path OR a project alias (e.g. 'amos'). If arg isn't an existing
    dir, hand it to the shared resolver in .claude/scripts/resolve_project.py."""
    if Path(arg).is_dir():
        return arg
    scripts = Path(__file__).resolve().parent.parent / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        import resolve_project  # type: ignore
        _, path = resolve_project.resolve(arg)
        return str(path)
    except Exception:
        return arg  # let the caller surface a clear "no .gravity/" error


def cmd_consistency(args) -> int:
    project = _resolve_project_arg(args.project)
    findings = check_gravity_consistency(project)
    domains = discover_domains(Path(project) / ".gravity")
    print(f"project: {project}")
    print(f"domains: {', '.join(sorted(domains)) or '(none)'}")
    if not findings:
        print("OK — all domains wired into all four indexes, no orphan routes.")
        return 0
    fails, warns = _print(findings)
    print(f"{fails} fail(s), {warns} warning(s).")
    return 1 if fails else 0


def cmd_scenario(args) -> int:
    scenario_dir = Path(args.scenario)
    expect = json.loads(_read(scenario_dir / "expect.json") or "{}")
    actual = Path(args.actual)
    domain = expect.get("expect_domain")

    print(f"scenario: {scenario_dir.name}  (command: {expect.get('command', '?')})")
    print(f"actual:   {actual}")
    print(f"expect:   domain '{domain}' wired into all four indexes")

    findings = check_gravity_consistency(actual)
    domains = discover_domains(actual / ".gravity")

    fails = 0
    # The added domain's folder must exist.
    if domain not in domains:
        print(f"  [FAIL] domain '{domain}' folder was not created under .gravity/")
        fails += 1
    # Required files inside the new domain folder.
    for rel in expect.get("require_files", []):
        if not (actual / ".gravity" / domain / rel).exists():
            print(f"  [FAIL] missing required file .gravity/{domain}/{rel}")
            fails += 1
    # No UNDERWIRED anywhere (the whole point — nothing orphaned).
    underwired = [f for f in findings if f.code == "UNDERWIRED" and f.severity == FAIL]
    for f in underwired:
        print("  " + str(f))
    fails += len(underwired)
    # Surface warnings but don't fail on them.
    for f in findings:
        if f.severity == WARN:
            print("  " + str(f))

    if fails:
        print(f"SCENARIO FAILED — {fails} structural problem(s).")
        return 1
    print(f"SCENARIO PASSED — '{domain}' wired into all four indexes, nothing orphaned.")
    return 0


def cmd_selftest(args) -> int:
    """Prove the checker itself: the bundled good fixture must pass, and a
    deliberately under-wired copy must fail with UNDERWIRED. Guards against the
    checker silently going blind."""
    fixture = Path(__file__).parent / "new-domain" / "fixture"
    if not fixture.is_dir():
        print(f"selftest: fixture not found at {fixture}")
        return 2

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "good"
        shutil.copytree(fixture, good)
        good_findings = [f for f in check_gravity_consistency(good) if f.severity == FAIL]
        if good_findings:
            ok = False
            print("selftest: EXPECTED good fixture to pass, but it FAILED:")
            _print(good_findings)
        else:
            print("selftest: good fixture passes (no FAIL findings).")

        # Break it: strip the existing domain's line out of the Doc Map.
        bad = Path(tmp) / "bad"
        shutil.copytree(fixture, bad)
        claude_path = bad / "CLAUDE.md"
        seed_domain = sorted(discover_domains(fixture / ".gravity"))[0]
        text = claude_path.read_text(encoding="utf-8")
        broken = "\n".join(
            ln for ln in text.splitlines()
            if not (f"{seed_domain}/" in ln and ".gravity" not in ln.lower()
                    or re.search(rf"^\s*{re.escape(seed_domain)}/", ln))
        )
        claude_path.write_text(broken, encoding="utf-8")
        bad_findings = check_gravity_consistency(bad)
        caught = [f for f in bad_findings
                  if f.code == "UNDERWIRED" and f.domain == seed_domain
                  and f.region == "doc_map"]
        if caught:
            print(f"selftest: under-wired '{seed_domain}' correctly caught "
                  f"(removed from Doc Map -> UNDERWIRED).")
        else:
            ok = False
            print(f"selftest: EXPECTED to catch under-wired '{seed_domain}' in the "
                  f"Doc Map, but the checker stayed silent.")

    print("SELFTEST PASSED" if ok else "SELFTEST FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    # Windows consoles default to a legacy codepage (cp949/cp1252) that chokes on
    # the em-dash etc.; force UTF-8 so output is portable.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("consistency", help="check one .gravity/ project for drift")
    c.add_argument("--project", required=True, help="path to the project root")
    c.set_defaults(func=cmd_consistency)

    s = sub.add_parser("scenario", help="assert a golden-scenario's postconditions")
    s.add_argument("--scenario", required=True, help="path to the scenario dir (has expect.json)")
    s.add_argument("--actual", required=True, help="path to the post-run project to check")
    s.set_defaults(func=cmd_scenario)

    t = sub.add_parser("selftest", help="prove the checker on the bundled fixture")
    t.set_defaults(func=cmd_selftest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
