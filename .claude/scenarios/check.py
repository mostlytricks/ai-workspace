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
  python check.py consistency --project DIR|alias
  python check.py spec        --project DIR|alias
  python check.py scenario   --scenario SCENARIO_DIR --actual DIR
  python check.py selftest

`spec` is the honesty checker: it verifies every `.gravity/<domain>/SPEC.md`'s
Gate command and enforcement tags against the repo's reality (package.json
scripts, test files), so a SPEC can't silently keep claiming walls that no
longer exist. Same under-claiming philosophy as `consistency`: FAIL only on
what is provably dead, WARN on weak signals, stay silent where we can't verify.

Importable too: `from check import check_gravity_consistency` returns the
findings list, so `/triage` can call the same core.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
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

# Every word of the root manual auto-loads into every session — the workspace's
# own CONTEXT-prune rule, applied to itself. Grow past this and push detail
# down into .claude/commands/ or docs/HANDBOOK.md (one concern, one home).
MANUAL_WORD_BUDGET = 5500


@dataclass
class Finding:
    severity: str   # FAIL | WARN
    code: str       # UNDERWIRED | ORPHAN_ROUTE | MISSING_FILE | INDEX_ABSENT | STRUCTURE
                    # | PROTOCOL_MISSING | PROTOCOL_STALE
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
    mission_path = gravity / "MISSION.html"
    plan_path = gravity / "IMPLEMENTATION_PLAN.md"
    mission = _read(mission_path)
    plan = _read(plan_path)

    doc_map = _section(claude, "Doc Map") or claude   # tolerate an unsplit CLAUDE.md
    router = _section(claude, "What to read before a change") or claude
    # Status spine = the heading mentioning BOTH "status" and "domain"
    # (e.g. "Domain status spine" / "Per-domain status"); never "Status right now".
    spine = _section_by(plan, lambda h: "status" in h and "domain" in h) or plan

    domains = discover_domains(gravity)

    # A domain can only be unwired from an index that EXISTS. A two-doc brownfield
    # project (CLAUDE.md §5 brownfield inversion: .gravity/integration/ with no
    # MISSION/PLAN yet) is a sanctioned state — skip those regions, WARN once.
    if domains and not mission_path.exists():
        findings.append(Finding(
            WARN, "INDEX_ABSENT", "", "mission",
            "no .gravity/MISSION.html — domain why-rows unchecked (two-doc/brownfield project?)"))
    if domains and not plan_path.exists():
        findings.append(Finding(
            WARN, "INDEX_ABSENT", "", "plan",
            "no .gravity/IMPLEMENTATION_PLAN.md — status spine unchecked (two-doc/brownfield project?)"))

    # PROTOCOL — the embedded protocol card (.gravity/GRAVITY.md, copied from
    # templates/GRAVITY-PROTOCOL.template.md) makes the repo self-describing
    # when opened without the workspace. Absent, unstamped, or older than the
    # workspace VERSION is drift, not breakage -> WARN, and the fix is always
    # a re-copy (the card is never hand-edited).
    card = _read(gravity / "GRAVITY.md")
    if not card:
        findings.append(Finding(
            WARN, "PROTOCOL_MISSING", "", "",
            "no .gravity/GRAVITY.md protocol card — the repo isn't self-describing "
            "off-workspace; copy templates/GRAVITY-PROTOCOL.template.md and stamp it"))
    else:
        stamp = re.search(r"gravity protocol[^\n]*?v(\d+)\.(\d+)", card, re.IGNORECASE)
        ws_ver = re.match(r"(\d+)\.(\d+)",
                          _read(Path(__file__).resolve().parents[2] / "VERSION").strip())
        if not stamp:
            findings.append(Finding(
                WARN, "PROTOCOL_STALE", "", "",
                ".gravity/GRAVITY.md has no 'gravity protocol · vX.Y' stamp "
                "(unfilled copy?) — re-copy the template and stamp from VERSION"))
        elif ws_ver and (int(stamp[1]), int(stamp[2])) < (int(ws_ver[1]), int(ws_ver[2])):
            findings.append(Finding(
                WARN, "PROTOCOL_STALE", "", "",
                f".gravity/GRAVITY.md is stamped v{stamp[1]}.{stamp[2]} but workspace "
                f"gravity is v{ws_ver[1]}.{ws_ver[2]} — re-copy the template"))

    # UNDERWIRED — a folder missing from an index it's *required* to be in.
    # Required everywhere: Doc Map (navigation), MISSION row (why), PLAN spine (status).
    # Router-table row is gravity-gated: required ONLY once the domain has a SPEC.md
    # (CLAUDE.md §6 / GRAVITY.template — the router row is added when a SPEC exists).
    for slug in sorted(domains):
        folder = gravity / slug
        checks = [("doc_map", _slug_in(doc_map, slug))]
        if mission_path.exists():
            checks.append(("mission", _slug_in(mission, slug)))
        if plan_path.exists():
            checks.append(("plan", _slug_in(spine, slug)))
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
# the spec-honesty check
# --------------------------------------------------------------------------- #

# Template leftovers that mean a SPEC.md was never fully filled in.
UNFILLED_PATTERNS = ("<FILL", "[FILL", "[test:name]", "\\<domain\\>", "<domain>")

# The recognized enforcement-tag grammar (SPEC.template.md legend). Order
# matters: "lint warn" before "lint". `[-]` is tolerated as ASCII for `[—]`.
TAG_RE = re.compile(r"\[(lint warn|lint|type|test:[^\]]+|review|—|-)\]")

_GATE_RE = re.compile(r"\*{0,2}gate:", re.IGNORECASE)

# Never descend into these when hunting for test files.
_SKIP_DIRS = {"node_modules", "dist", "build", "out", "coverage",
              ".venv", "venv", "__pycache__", ".next"}


def _strip_html_comments(text: str) -> str:
    """Drop <!-- … --> blocks: the enforcement legend legitimately spells out
    the tag grammar (`[test:name]` etc.) inside a comment, and commented-out
    template blocks are not active contract. Only what renders counts."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _gate_line(spec_text: str) -> str:
    """The SPEC's `**Gate:** …` line (whole line, prose included). '' if none."""
    for line in spec_text.splitlines():
        if _GATE_RE.match(line.strip()):
            return line
    return ""


def spec_tag_census(spec_text: str) -> dict[str, int]:
    """Occurrence count per tag family — the 'walls vs judgment' snapshot.
    HTML comments (the legend) don't count as claims."""
    census: dict[str, int] = {}
    for tag in TAG_RE.findall(_strip_html_comments(spec_text)):
        key = "test" if tag.startswith("test:") else ("—" if tag == "-" else tag)
        census[key] = census.get(key, 0) + 1
    return census


def _npm_reality(project: Path) -> tuple[dict[str, str] | None, list[Path]]:
    """(merged npm scripts, workspace dirs) from the root package.json plus one
    level of workspaces. Scripts are None when there is no root package.json —
    not an npm project, so every npm-based check must stay silent."""
    root_pkg = project / "package.json"
    if not root_pkg.exists():
        return None, []

    def _load(p: Path) -> dict:
        try:
            return json.loads(_read(p) or "{}")
        except json.JSONDecodeError:
            return {}

    data = _load(root_pkg)
    scripts: dict[str, str] = dict(data.get("scripts") or {})
    patterns = data.get("workspaces") or []
    if isinstance(patterns, dict):
        patterns = patterns.get("packages") or []
    ws_dirs: list[Path] = []
    for pattern in patterns:
        for pkg in sorted(project.glob(f"{pattern}/package.json")):
            ws_dirs.append(pkg.parent)
            scripts.update(_load(pkg).get("scripts") or {})
    return scripts, ws_dirs


def _path_exists_anywhere(project: Path, ws_dirs: list[Path], token: str) -> bool:
    """A Gate-referenced path counts as alive if it exists relative to the
    project root, any workspace dir, or .gravity/ (Gate lines legitimately
    reference sibling domain docs like `doc/SPEC.md`)."""
    return any((base / token).exists()
               for base in [project, project / ".gravity", *ws_dirs])


def _test_files(project: Path) -> list[Path]:
    """Test-ish files a `[test:<name>]` may live in: *.test.* / *.spec.* files
    anywhere, plus everything under tests/ test/ __tests__/ references/."""
    hits: list[Path] = []
    test_dir_names = {"tests", "test", "__tests__", "references"}
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs
                   if d not in _SKIP_DIRS and not d.startswith(".")]
        in_test_dir = bool(test_dir_names & set(Path(root).parts))
        for fn in files:
            if in_test_dir or re.search(r"\.(test|spec)\.", fn):
                p = Path(root) / fn
                try:
                    if p.stat().st_size <= 2_000_000:
                        hits.append(p)
                except OSError:
                    pass
    return hits


def check_spec_honesty(project_dir: str | Path) -> list[Finding]:
    """Verify every .gravity/<domain>/SPEC.md against the repo's reality:
    the Gate's npm scripts + paths must exist, every [test:<name>] must point
    at a real script or test file, lint/type claims need something to back
    them, and no template leftovers survive. Empty list == honest."""
    project = Path(project_dir)
    gravity = project / ".gravity"
    if not gravity.is_dir():
        return [Finding(FAIL, "STRUCTURE", "", "",
                        f"no .gravity/ directory at {project}")]

    findings: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()

    def add(severity: str, code: str, slug: str, message: str) -> None:
        key = (code, slug, message)
        if key not in seen:
            seen.add(key)
            findings.append(Finding(severity, code, slug, "", message))

    scripts, ws_dirs = _npm_reality(project)
    test_files: list[Path] | None = None  # scanned lazily, once

    for slug in sorted(discover_domains(gravity)):
        spec_path = gravity / slug / "SPEC.md"
        if not spec_path.exists():
            continue
        text = _strip_html_comments(_read(spec_path))

        # SPEC_UNFILLED — a template leftover is a lie by definition.
        for pat in UNFILLED_PATTERNS:
            if pat in text:
                add(FAIL, "SPEC_UNFILLED", slug,
                    f"SPEC.md still contains template leftover '{pat}'")

        gate = _gate_line(text)
        if not gate:
            add(WARN, "GATE_MISSING", slug,
                "SPEC.md has no 'Gate:' line — an agent has no command to prove a change")

        census = spec_tag_census(text)

        if scripts is not None:
            # GATE_DEAD — every npm script / path named on the Gate line must exist.
            for span in re.findall(r"`([^`]+)`", gate):
                for script in re.findall(r"npm(?:\s+-w\s+\S+)?\s+run\s+([\w:.-]+)", span):
                    if script not in scripts:
                        add(FAIL, "GATE_DEAD", slug,
                            f"Gate names `npm run {script}` but no such script exists in package.json")
                for token in span.split():
                    token = token.strip("(),;`—→")
                    if ("/" in token and "." in Path(token).name
                            and "://" not in token and "<" not in token
                            and "*" not in token):
                        if not _path_exists_anywhere(project, ws_dirs, token):
                            add(FAIL, "GATE_DEAD", slug,
                                f"Gate references path `{token}` which does not exist")

            # TAG_DEAD — a [test:<name>] must resolve to a script or a test file.
            for tag in TAG_RE.findall(text):
                if not tag.startswith("test:"):
                    continue
                name = tag[5:].strip()
                if name == "name" or name in scripts:
                    continue  # 'name' is the template leftover, already FAILed above
                if test_files is None:
                    test_files = _test_files(project)
                if not any(name in _read(p) for p in test_files):
                    add(FAIL, "TAG_DEAD", slug,
                        f"[test:{name}] — no npm script and no test-ish file mentions '{name}'")

            # TAG_UNBACKED — lint/type claims need SOME lint/type reality.
            hay = " ".join([gate, *scripts.keys(),
                            *map(str, scripts.values())]).lower()
            if (census.get("lint") or census.get("lint warn")) and "lint" not in hay:
                add(WARN, "TAG_UNBACKED", slug,
                    "[lint] tags present but no lint command in the Gate or package.json scripts")
            if census.get("type") and not any(k in hay for k in ("tsc", "typecheck", "noemit")):
                add(WARN, "TAG_UNBACKED", slug,
                    "[type] tags present but no tsc/typecheck in the Gate or package.json scripts")

        # RULES_UNTAGGED — a Rules section in the legacy fully-untagged form.
        bullets = [ln for ln in _section(text, "Rules").splitlines()
                   if ln.startswith("- ")]
        if bullets and not any(re.match(r"-\s+`?\[", b) for b in bullets):
            add(WARN, "RULES_UNTAGGED", slug,
                f"## Rules has {len(bullets)} bullet(s), none carrying an enforcement tag")

    return findings


# --------------------------------------------------------------------------- #
# CLI subcommands
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# workspace checker — tier/index structural drift over the whole tree
# --------------------------------------------------------------------------- #

def _scan_workspace(root: Path | None):
    """Import the fact scanner (.claude/scripts/scan_workspace.py) and run it.
    The checker judges facts; it never re-scans disk itself."""
    scripts = Path(__file__).resolve().parent.parent / "scripts"
    sys.path.insert(0, str(scripts))
    import scan_workspace  # type: ignore  # noqa: E402
    return scan_workspace.scan(root)


def check_workspace(root: str | Path | None = None) -> list[Finding]:
    """Structural drift across the tier folders + PROJECTS.md.

    Severity bar (scenarios/README.md): FAIL = provable contradiction between
    two sources of truth; WARN = hygiene/heuristic. Staleness is deliberately
    NOT judged here — it's a fact in the scan (days_ago), and a decision
    prompt for the human, not drift. Date-dependent findings would also rot
    scenario fixtures.
    """
    root = Path(root) if root else None
    facts = _scan_workspace(root)
    findings: list[Finding] = []

    def add(sev, code, name, message):
        findings.append(Finding(sev, code, name, "", message))

    for name in facts["multi_tier"]:
        tiers = facts["projects"][name]["tiers"]
        add(FAIL, "MULTI_TIER", name,
            f"junctioned into {len(tiers)} tiers at once ({', '.join(tiers)}) — one tier per project")
    for name in facts["index_only"]:
        listed = (facts["projects"][name]["index"] or {}).get("listed_tier", "?")
        add(FAIL, "INDEX_MISSING_ON_DISK", name,
            f"PROJECTS.md lists it under {listed}/ but no folder or junction exists on disk")

    for name, p in facts["projects"].items():
        tiers, idx, ctx = p["tiers"], p["index"], p["context"]
        tier = tiers[0] if len(tiers) == 1 else None
        if tier and idx and idx["listed_tier"] != tier:
            add(FAIL, "INDEX_WRONG_TIER", name,
                f"PROJECTS.md says {idx['listed_tier']}/ but the junction is in {tier}/")
        if not tiers:
            continue                     # orphans handled below; index-only above
        if tier == "archive":
            continue                     # frozen — no CONTEXT-quality checks
        if not ctx.get("exists"):
            add(WARN, "UNINITIALIZED", name, "no CONTEXT.md — no recorded state")
            continue
        if ctx.get("stencil"):
            add(WARN, "STENCIL", name, "CONTEXT.md still carries template placeholder text")
        if ctx.get("completed_bullets", 0) > 6 or ctx.get("lines", 0) > 80:
            add(WARN, "BLOAT", name,
                f"CONTEXT.md needs a prune ({ctx['lines']} lines / "
                f"{ctx['completed_bullets']} Completed bullets; thresholds ~80/~6)")
        nxt = ctx.get("next_step", "").lower()
        if tier == "stable" and "reactivate" not in nxt:
            add(WARN, "MISSING_TRIGGER", name,
                "stable project whose CONTEXT.md Next Step doesn't read as a "
                "reactivation trigger ('Reactivate when …')")
        if tier == "dormant" and "resume" not in nxt and "blocker" not in nxt:
            add(WARN, "MISSING_BLOCKER", name,
                "dormant project whose CONTEXT.md Next Step names no resume blocker")

    for name in facts["orphans"]:
        add(WARN, "REPO_ORPHAN", name, "repos/ folder with no junction in any tier")
    for name in facts["not_indexed"]:
        add(WARN, "NOT_INDEXED", name, "on disk in a tier but has no PROJECTS.md row")

    # The manual's own bloat wall — projects get a CONTEXT prune trigger (~80
    # lines); the root CLAUDE.md gets a word budget, because it auto-loads
    # into every session across every project.
    manual = (root or Path(__file__).resolve().parents[2]) / "CLAUDE.md"
    if manual.exists():
        words = len(manual.read_text(encoding="utf-8").split())
        if words > MANUAL_WORD_BUDGET:
            add(WARN, "MANUAL_BLOAT", "ai-workspace",
                f"root CLAUDE.md is {words} words (budget {MANUAL_WORD_BUDGET}) "
                f"— push detail down to .claude/commands/ or docs/HANDBOOK.md "
                f"(one concern, one home)")

    findings += _check_adoption_table(root, facts)
    return findings


# ---------------------------------------------------------------------------
# intake sheets — docs/intake/*.md (the /intake command's output)

INTAKE_FIELDS = ("Reporter", "Observed", "Expected", "Repro", "Env", "Evidence")
_INTAKE_ITEM_RE = re.compile(r"^### +(I\d+)[^\n]*", re.MULTILINE)


def _intake_value(block: str, label: str) -> str | None:
    """The text after a '- **<label> …:**' field line; None if the line is absent."""
    m = re.search(rf"^\s*-\s+\*\*{label}[^\n]*?\*\*:?\s*(.*)$", block, re.MULTILINE)
    return m.group(1).strip() if m else None


def _intake_unfilled(value: str) -> bool:
    """Template stubs start with '<'; honest unknowns start with 'OPEN:'."""
    v = value.strip().strip("`").strip()
    return (not v) or v.startswith("<")


def check_intake(project_dir: str | Path) -> list[Finding]:
    """Intake-sheet honesty (docs/intake/*.md, from INTAKE.template.md): every
    item carries the six required facts (filled, or an honest 'OPEN: awaiting
    …'), every row on a ✓-closed sheet routes somewhere, a route naming a PLAN
    file points at one that exists, and bugs never become a domain. Severity
    bar: FAIL = the sheet contradicts reality or itself; WARN = a required
    fact is absent or still a template stub."""
    project = Path(project_dir)
    findings: list[Finding] = []

    if (project / ".gravity" / "bugs").is_dir():
        findings.append(Finding(
            FAIL, "BUGS_FOLDER", "bugs", "",
            ".gravity/bugs/ exists — bugs are never a domain; intake rows "
            "route to owning-domain slice PLANs"))

    for sheet in sorted((project / "docs" / "intake").glob("*.md")):
        text = sheet.read_text(encoding="utf-8")
        rel = f"docs/intake/{sheet.name}"
        closed = bool(re.search(r"^Status:\s*✓", text, re.MULTILINE))
        parts = _INTAKE_ITEM_RE.split(text)
        for item_id, block in zip(parts[1::2], parts[2::2]):
            where = f"{rel} {item_id}"
            for label in INTAKE_FIELDS:
                value = _intake_value(block, label)
                if value is None:
                    findings.append(Finding(
                        WARN, "INTAKE_FIELD_MISSING", item_id, "",
                        f"{where}: required field '{label}' absent — elicit "
                        f"it or write 'OPEN: awaiting …', never leave a blank"))
                elif _intake_unfilled(value):
                    findings.append(Finding(
                        WARN, "INTAKE_FIELD_UNFILLED", item_id, "",
                        f"{where}: '{label}' still carries the template stub"))
            route = _intake_value(block, "→")
            if route is None or _intake_unfilled(route):
                findings.append(Finding(
                    FAIL if closed else WARN, "INTAKE_UNROUTED", item_id, "",
                    f"{where}: no routed '→' line" + (
                        " on a ✓-closed sheet — the Status is lying"
                        if closed else " yet (sheet still ○ triaging)")))
            else:
                for path in re.findall(r"[\w./\\-]*PLAN[\w.\\-]*\.md", route):
                    if not (project / path.replace("\\", "/")).exists():
                        findings.append(Finding(
                            FAIL, "INTAKE_DEAD_ROUTE", item_id, "",
                            f"{where}: routed to '{path}' which does not exist"))
    return findings


def _intake_fixture(base: Path) -> None:
    """A mini project whose intake sheet is honest: three items — routed to a
    real PLAN, rejected with a reason, honestly OPEN — on a ✓-closed sheet."""
    (base / ".gravity" / "support").mkdir(parents=True)
    (base / ".gravity" / "support" / "PLAN.timeout.md").write_text(
        "# support — PLAN.timeout\n\nStatus: ○ planned\n\n## Scenario\n"
        "- given a slow upstream, when sync runs → it times out at 30s "
        "(currently false — the repro from intake I1/I2)\n", encoding="utf-8")
    intake = base / "docs" / "intake"
    intake.mkdir(parents=True)
    (intake / "2026-01-15.md").write_text(
        "# INTAKE — fixture-helpdesk — 2026-01-15\n\n"
        "Batch: 3 items from support channel.\n"
        "Status: ✓ closed\n\n"
        "## Items\n\n"
        "### I1 — sync times out on big folders\n"
        "- **Reporter · date:** Kim · 2026-01-10\n"
        "- **Observed (verbatim):** \"sync hangs then dies after exactly 30 seconds\"\n"
        "- **Expected:** sync completes or reports progress past 30s\n"
        "- **Repro:** 1. seed 10k files 2. run sync — times out at 30s\n"
        "- **Env:** v1.2.0 · Windows 11 · ko-KR · 10k-file folder\n"
        "- **Evidence:** support ticket #4411, timeout stack trace attached\n"
        "- **Triage:** real: yes · kind: bug · domain: support · severity: S2\n"
        "- **→** `.gravity/support/PLAN.timeout.md`\n\n"
        "### I2 — \"same timeout as Kim\"\n"
        "- **Reporter · date:** Lee · 2026-01-11\n"
        "- **Observed (verbatim):** \"same timeout as Kim reported\"\n"
        "- **Expected:** same as I1\n"
        "- **Repro:** same as I1\n"
        "- **Env:** v1.2.0 · macOS · en-US · 8k-file folder\n"
        "- **Evidence:** ticket #4415\n"
        "- **Triage:** real: yes · kind: bug · domain: support · severity: S2\n"
        "- **→** rejected: duplicate of I1 (see Root causes)\n\n"
        "### I3 — export button greyed out sometimes\n"
        "- **Reporter · date:** Park · 2026-01-12\n"
        "- **Observed (verbatim):** \"export button is greyed out sometimes??\"\n"
        "- **Expected:** export available whenever a folder is selected\n"
        "- **Repro:** OPEN: awaiting the reporter's screen recording — cannot reproduce\n"
        "- **Env:** v1.2.0 · Windows 10 · ko-KR\n"
        "- **Evidence:** OPEN: awaiting screenshot\n"
        "- **Triage:** real: OPEN · kind: bug · domain: support · severity: S3\n"
        "- **→** OPEN: awaiting repro from Park — stays in the sheet\n\n"
        "## Root causes (dedupe)\n\n"
        "| Cause | Items | Slice PLAN | Queue lane |\n"
        "|---|---|---|---|\n"
        "| 30s hard timeout in sync client | I1, I2 | `.gravity/support/PLAN.timeout.md` | now |\n",
        encoding="utf-8")


def _check_adoption_table(root: Path | None, facts: dict) -> list[Finding]:
    """PROJECTS.md's hand-kept 'Gravity adoption' table vs disk reality.
    All WARN — the table is a snapshot view (the dashboard computes live);
    a wrong cell is rot, not breakage. Absent table/section → silent."""
    ws = Path(root) if root else Path(__file__).resolve().parents[2]
    section = _section(_read(ws / "PROJECTS.md"), "Gravity adoption")
    if not section.strip():
        return []
    out: list[Finding] = []
    seen: set[str] = set()
    for line in section.splitlines():
        if not line.startswith("| ") or line.startswith("|---") or line.startswith("| Project"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        name = cells[0].split()[0]
        seen.add(name)
        p = facts["projects"].get(name)
        if p is None or not p["in_repos"]:
            out.append(Finding(WARN, "ADOPTION_STALE", name, "",
                               "adoption-table row for a project not in repos/"))
            continue
        a = p["adoption"]
        want = {
            "stamp": f"`v{a['stamp']}`" if a["stamp"] else "—",
            "docs":  "`.gravity`" if a["docsys"] == "gravity" else "flat",
            "card":  ((f"`v{a['card']}`" if a["card"] else "—")
                      if a["docsys"] == "gravity" else "n/a"),
            "rel":   "✓" if a["release"] else "—",
            "codex": "✓" if a["shim"] else "—",
        }
        got = dict(zip(("stamp", "docs", "card", "rel", "codex"), cells[1:6]))
        for col, expected in want.items():
            if got.get(col) != expected:
                out.append(Finding(WARN, "ADOPTION_STALE", name, "",
                                   f"table says {col}={got.get(col)!r} but disk says {expected!r}"))
    for name, p in facts["projects"].items():
        if (p["in_repos"] and p["adoption"]["docsys"] is not None
                and name not in seen and p["tiers"] and p["tiers"][0] != "archive"):
            out.append(Finding(WARN, "ADOPTION_MISSING_ROW", name, "",
                               "gravity project with no row in the adoption table"))
    return out


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


def cmd_spec(args) -> int:
    project = _resolve_project_arg(args.project)
    gravity = Path(project) / ".gravity"
    specs = sorted(slug for slug in discover_domains(gravity)
                   if (gravity / slug / "SPEC.md").exists())
    print(f"project: {project}")
    if not specs:
        print("no .gravity/<domain>/SPEC.md files — nothing to check.")
        return 0
    print("tag census per SPEC (walls vs judgment):")
    for slug in specs:
        census = spec_tag_census(_read(gravity / slug / "SPEC.md"))
        pretty = " · ".join(f"{k} {v}" for k, v in census.items()) or "(no tags)"
        print(f"  {slug}: {pretty}")
    findings = check_spec_honesty(project)
    if not findings:
        print("OK — every Gate and tag verified (or honestly [review]/[—]).")
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
    # Optional: the authored SPEC must be honest (a fabricated wall = FAIL).
    if expect.get("spec_honesty"):
        dishonest = [f for f in check_spec_honesty(actual) if f.severity == FAIL]
        for f in dishonest:
            print("  " + str(f))
        fails += len(dishonest)
    # Optional: required substrings per file (evidence that must have been mapped).
    for rel, needles in expect.get("require_content", {}).items():
        text = _read(actual / rel)
        for needle in needles:
            if needle not in text:
                print(f"  [FAIL] {rel} must contain '{needle}' but doesn't")
                fails += 1
    # Optional: forbidden substrings inside one `## section` of a file — e.g. a
    # dead frontend call must never appear as a Boundary Map row (a seam that
    # doesn't exist is a fabricated seam; it may appear elsewhere as a finding).
    for rel, sections in expect.get("forbid_in_section", {}).items():
        text = _strip_html_comments(_read(actual / rel))
        for header, needles in sections.items():
            sec = _section(text, header)
            if not sec:
                print(f"  [FAIL] {rel} has no '## {header}' section to check")
                fails += 1
                continue
            for needle in needles:
                if needle in sec:
                    print(f"  [FAIL] {rel} '## {header}' must NOT contain "
                          f"'{needle}' — that seam doesn't exist in the fixture")
                    fails += 1
    # Surface warnings but don't fail on them.
    for f in findings:
        if f.severity == WARN:
            print("  " + str(f))

    if fails:
        print(f"SCENARIO FAILED — {fails} structural problem(s).")
        return 1
    print(f"SCENARIO PASSED — '{domain}' wired into all four indexes, nothing orphaned.")
    return 0


def _spec_fixture(root: Path) -> None:
    """A minimal honest npm project: one domain SPEC whose Gate, [test:] tag,
    and [lint] claim are all backed by reality. Used only by selftest."""
    (root / ".gravity" / "model").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "package.json").write_text(json.dumps({
        "scripts": {"check": "node check.js", "lint:model": "node lint.js"}
    }), encoding="utf-8")
    (root / "tests" / "model.test.js").write_text(
        "// covers model-roundtrip\n", encoding="utf-8")
    (root / ".gravity" / "model" / "SPEC.md").write_text(
        "# SPEC.model.md\n\n"
        "**Gate:** `npm run check` — exits non-zero on a violation.\n\n"
        # The legend comment legitimately contains the literal tag grammar —
        # it must NOT trip SPEC_UNFILLED/TAG_DEAD (comments are not contract).
        "<!-- Legend: [lint] linter fails · [test:name] a named test asserts"
        " · [review] human-only. -->\n\n"
        "## Rules\n\n"
        "- `[lint]` every field is kebab-case (checked by `npm run lint:model`)\n"
        "- `[test:model-roundtrip]` parse→serialize→parse is lossless\n"
        "- `[review]` names stay domain-language\n", encoding="utf-8")


def cmd_workspace(args) -> int:
    findings = check_workspace()
    facts = _scan_workspace(None)
    counts = " · ".join(f"{t}={n}" for t, n in facts["tier_counts"].items())
    print(f"workspace: {counts}")
    if not findings:
        print("OK — tiers, PROJECTS.md, and adoption table all agree.")
        return 0
    fails, warns = _print(findings)
    print(f"{fails} fail(s), {warns} warning(s).")
    return 1 if fails else 0


def _workspace_fixture(base: Path) -> None:
    """A minimal healthy workspace: one active + one stable project, indexed.
    Plain dirs stand in for junctions — the scanner treats tier entries as views."""
    for name, tier, ctx_next in (
        ("alpha", "active", "- Wire the parser to the new endpoint (src/parse.py)."),
        ("beta", "stable", "- **STABLE.** Reactivate when the upstream API ships v2."),
    ):
        real = base / "repos" / name
        real.mkdir(parents=True)
        (base / tier / name).mkdir(parents=True)
        (real / "CLAUDE.md").write_text(f"# {name}\n\nA test project.\n", encoding="utf-8")
        (real / "CONTEXT.md").write_text(
            f"# CONTEXT — {name}\n\nLast touched: 2026-01-01\n\n"
            f"## Completed\n- Did a thing.\n\n## Current State\n- Fine.\n\n"
            f"## Next Step\n{ctx_next}\n", encoding="utf-8")
    (base / "dormant").mkdir()
    (base / "archive").mkdir()
    (base / "PROJECTS.md").write_text(
        "# Projects Index\n\n## active/\n\n"
        "- alpha | Python | 2026-01-01 | wire the parser\n\n"
        "## stable/\n\n"
        "- beta | Node | shipped 2026-01-01 | steady; reactivate when upstream ships v2\n\n"
        "## dormant/\n\n## archive/\n", encoding="utf-8")


def _patchloop_selftest() -> bool:
    """Drive .claude/scripts/patch_slice.py end-to-end over the patch-slice
    fixture, both fork branches — proves the ritual's mechanical walls still
    hold: F4 bare-gate exit codes, N=3 exhaustion (exit 75), and the F7
    four-proof rollback restoring gitignored state byte-identical. Needs git."""
    fixture = Path(__file__).parent / "patch-slice" / "fixture"
    script = Path(__file__).resolve().parent.parent / "scripts" / "patch_slice.py"
    if not fixture.is_dir() or not script.exists():
        print("selftest: patch-slice fixture or patch_slice.py missing; SKIPPED.")
        return True

    py = sys.executable
    gate = f'"{py}" gate.py'
    probe = f'"{py}" probe_state.py'
    plan_rel = ".gravity/demo/PLAN.fix.md"
    spec_rel = ".gravity/demo/SPEC.md"
    ok = True

    def sh(repo: Path, *cmd: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(list(cmd), cwd=repo, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")

    def g(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return sh(repo, "git", "-c", "user.name=selftest",
                  "-c", "user.email=selftest@local", *args)

    def ps(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return sh(repo, py, str(script), *args)

    def make_repo(base: Path, name: str) -> Path:
        # The fixture deliberately ships without .git/.gitignore; the replay adds
        # them, making state/ git-invisible so only the snap protects it.
        repo = base / name
        shutil.copytree(fixture, repo)
        # state/ = the fixture's gitignored ledger; __pycache__/ = bytecode the
        # gate's test runs write on some platforms (Linux) — without ignoring it
        # the preflight/rollback tree-clean proofs fail on dirt the tool made.
        (repo / ".gitignore").write_text("state/\n__pycache__/\n", encoding="utf-8")
        g(repo, "init", "-q", "-b", "main")
        g(repo, "add", "-A")
        g(repo, "commit", "-qm", "fixture baseline")
        return repo

    def apply_regression_test(repo: Path) -> None:
        tests = repo / "tests" / "test_app.py"
        tests.write_text(tests.read_text(encoding="utf-8").replace(
            "    def test_zero_pct(self):",
            "    def test_clamp_over_100(self):\n"
            "        self.assertEqual(apply_discount(100, 150), 0)\n\n"
            "    def test_zero_pct(self):"), encoding="utf-8")

    def expect(cond: bool, label: str,
               cp: subprocess.CompletedProcess[str] | None = None) -> None:
        nonlocal ok
        if cond:
            print(f"selftest: patch-loop {label}.")
        else:
            ok = False
            print(f"selftest: patch-loop EXPECTED {label}, but it didn't hold.")
            if cp is not None:
                print((cp.stdout or "") + (cp.stderr or ""))

    # Windows: git object files are read-only; don't let cleanup errors mask results.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        base = Path(tmp)

        # --- GREEN path: preflight → anchor → snap → patch → verify → cleanup ---
        repo = make_repo(base, "green")
        anchor = g(repo, "rev-parse", "--short", "HEAD").stdout.strip()

        cp = ps(repo, "preflight", "--gate", gate)
        expect(cp.returncode == 0, "preflight passes on a clean green baseline", cp)

        cp = ps(repo, "anchor", "--plan", plan_rel, "--slug", "demo-fix")
        on_branch = g(repo, "branch", "--show-current").stdout.strip()
        expect(cp.returncode == 0 and on_branch == "slice/demo-fix"
               and anchor in (repo / plan_rel).read_text(encoding="utf-8"),
               "anchor creates slice/demo-fix and writes the SHA into the PLAN", cp)

        cp = ps(repo, "snap", "--spec", spec_rel, "--plan", plan_rel)
        expect(cp.returncode == 0
               and (repo / ".patch-snap" / anchor / "state" / "data.txt").exists(),
               "snap copies the SPEC-declared stateful path", cp)

        # The patch an agent would write: the fix + the named regression test.
        app = repo / "app.py"
        app.write_text(app.read_text(encoding="utf-8").replace(
            "    return price * (1 - pct / 100)",
            "    pct = max(0.0, min(100.0, pct))\n"
            "    return price * (1 - pct / 100)"), encoding="utf-8")
        apply_regression_test(repo)

        cp = ps(repo, "verify", "--gate", gate, "--plan", plan_rel)
        expect(cp.returncode == 0, "verify green on the fixed patch (attempt 1/3)", cp)

        g(repo, "add", "-A")
        g(repo, "commit", "-qm", "checkpoint: clamp fix + regression test")
        cp = ps(repo, "cleanup")
        expect(cp.returncode == 0 and not (repo / ".patch-snap").exists(),
               "cleanup retires the snap after the green checkpoint", cp)

        # --- RED path: bad patch + mangled state → 3 red verifies → exit 75 → rollback ---
        repo = make_repo(base, "red")
        anchor = g(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        ps(repo, "preflight", "--gate", gate)
        ps(repo, "anchor", "--plan", plan_rel, "--slug", "demo-fix")
        ps(repo, "snap", "--spec", spec_rel, "--plan", plan_rel)

        # The bad patch: the regression test WITHOUT the fix (gate goes red)…
        apply_regression_test(repo)
        # …and it also mangles the gitignored ledger — reset --hard can't undo this.
        (repo / "state" / "data.txt").write_text("garbage", encoding="utf-8")

        rc1 = ps(repo, "verify", "--gate", gate, "--plan", plan_rel).returncode
        rc2 = ps(repo, "verify", "--gate", gate, "--plan", plan_rel).returncode
        cp3 = ps(repo, "verify", "--gate", gate, "--plan", plan_rel)
        expect((rc1, rc2, cp3.returncode) == (1, 1, 75),
               "N=3 enforced — third red verify exits 75", cp3)

        cp = ps(repo, "rollback", "--to", anchor, "--gate", gate,
                "--probe", probe, "--plan", plan_rel)
        ledger = (repo / "state" / "data.txt").read_text(encoding="utf-8")
        expect(cp.returncode == 0 and ledger == "seed=42\n"
               and not (repo / ".patch-snap" / anchor).exists(),
               "four-proof rollback restores the ledger byte-identical and retires the snap", cp)

        story = (repo / plan_rel).read_text(encoding="utf-8")
        expect("attempt 3/3" in story and "**Rollback:**" in story,
               "execution log survives the hard reset (anchor→attempts→rollback intact)")

    return ok


def _rewrite(path: Path, old: str, new: str) -> None:
    """Seed a drift into a fixture copy: replace `old` with `new` in-place."""
    path.write_text(path.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8")


def cmd_intake(args) -> int:
    project = Path(args.project).resolve()
    findings = check_intake(project)
    sheets = sorted((project / "docs" / "intake").glob("*.md"))
    print(f"project: {project}")
    print(f"intake sheets: {len(sheets)}"
          + (f" ({', '.join(s.name for s in sheets)})" if sheets else ""))
    _print(findings)
    fails = sum(1 for f in findings if f.severity == FAIL)
    if findings:
        print(f"{fails} fail(s), {len(findings) - fails} warning(s).")
    else:
        print("OK — every item carries its six facts and routes somewhere; "
              "bugs never a domain.")
    return 1 if fails else 0


def cmd_selftest(args) -> int:
    """Prove the checker itself: the bundled good fixture must pass, and a
    deliberately under-wired copy must fail with UNDERWIRED. Guards against the
    checker silently going blind."""
    fixture = Path(__file__).parent / "new-domain" / "fixture"
    if not fixture.is_dir():
        print(f"selftest: fixture not found at {fixture}")
        return 2

    ok = True

    # Every scenario's golden fixture must itself be clean — consistency AND
    # spec honesty (a rotted fixture would make its scenario prove nothing).
    # A fixture with NO .gravity/ is the input for a command that CREATES one
    # (/excavate on a virgin brownfield system) — nothing to validate yet.
    for fx in sorted(Path(__file__).parent.glob("*/fixture")):
        if not (fx / ".gravity").is_dir():
            print(f"selftest: fixture {fx.parent.name}/fixture has no .gravity/ "
                  f"(virgin input — the command under test creates it); skipped.")
            continue
        fx_fails = [f for f in check_gravity_consistency(fx) if f.severity == FAIL]
        fx_fails += [f for f in check_spec_honesty(fx) if f.severity == FAIL]
        if fx_fails:
            ok = False
            print(f"selftest: EXPECTED fixture {fx.parent.name}/fixture to be clean, but it FAILED:")
            _print(fx_fails)
        else:
            print(f"selftest: fixture {fx.parent.name}/fixture is clean (consistency + spec honesty).")

    with tempfile.TemporaryDirectory() as tmp:
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

    # --- spec-honesty half: an honest SPEC passes; each lie is caught. ---
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "spec-good"
        _spec_fixture(good)
        good_fails = [f for f in check_spec_honesty(good) if f.severity == FAIL]
        if good_fails:
            ok = False
            print("selftest: EXPECTED honest SPEC fixture to pass, but it FAILED:")
            _print(good_fails)
        else:
            print("selftest: honest SPEC fixture passes (no FAIL findings).")

        lies = {
            "GATE_DEAD": ("npm run check", "npm run nope"),
            "TAG_DEAD": ("[test:model-roundtrip]", "[test:vanished-test]"),
            "SPEC_UNFILLED": ("## Rules", "## Rules\n\n<FILL: pending>"),
        }
        for code, (old, new) in lies.items():
            bad = Path(tmp) / f"spec-bad-{code.lower()}"
            _spec_fixture(bad)
            spec_path = bad / ".gravity" / "model" / "SPEC.md"
            spec_path.write_text(
                spec_path.read_text(encoding="utf-8").replace(old, new),
                encoding="utf-8")
            caught = [f for f in check_spec_honesty(bad)
                      if f.code == code and f.severity == FAIL]
            if caught:
                print(f"selftest: dishonest SPEC ('{new}') correctly caught -> {code}.")
            else:
                ok = False
                print(f"selftest: EXPECTED {code} for '{new}', but the checker stayed silent.")

    # --- workspace half: a healthy mini-workspace passes; each drift is caught. ---
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "ws-good"
        _workspace_fixture(good)
        good_fails = [f for f in check_workspace(good) if f.severity == FAIL]
        good_trigger = [f for f in check_workspace(good) if f.code == "MISSING_TRIGGER"]
        if good_fails or good_trigger:
            ok = False
            print("selftest: EXPECTED healthy workspace fixture to pass, but:")
            _print(good_fails + good_trigger)
        else:
            print("selftest: healthy workspace fixture passes (no FAILs, trigger honored).")

        drifts = {
            "MULTI_TIER": lambda ws: (ws / "dormant" / "alpha").mkdir(),
            "INDEX_MISSING_ON_DISK": lambda ws: (ws / "PROJECTS.md").write_text(
                (ws / "PROJECTS.md").read_text(encoding="utf-8").replace(
                    "## stable/",
                    "- gamma | Rust | 2026-01-01 | a ghost project\n\n## stable/"),
                encoding="utf-8"),
            "MISSING_TRIGGER": lambda ws: (ws / "repos" / "beta" / "CONTEXT.md").write_text(
                (ws / "repos" / "beta" / "CONTEXT.md").read_text(encoding="utf-8").replace(
                    "Reactivate when the upstream API ships v2.",
                    "Refactor the cache layer next."),
                encoding="utf-8"),
        }
        for code, mutate in drifts.items():
            bad = Path(tmp) / f"ws-bad-{code.lower()}"
            shutil.copytree(good, bad)
            mutate(bad)
            caught = [f for f in check_workspace(bad) if f.code == code]
            if caught:
                print(f"selftest: workspace drift correctly caught -> {code}.")
            else:
                ok = False
                print(f"selftest: EXPECTED {code}, but the workspace checker stayed silent.")

    # --- intake half: an honest sheet passes; each drift is caught. ---
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "intake-good"
        _intake_fixture(good)
        good_findings = check_intake(good)
        if good_findings:
            ok = False
            print("selftest: EXPECTED honest intake fixture to pass, but:")
            _print(good_findings)
        else:
            print("selftest: honest intake fixture passes (six facts, routed, no bugs domain).")

        drifts = {
            "BUGS_FOLDER": lambda p: (p / ".gravity" / "bugs").mkdir(),
            "INTAKE_DEAD_ROUTE": lambda p: (p / ".gravity" / "support" / "PLAN.timeout.md").unlink(),
            "INTAKE_UNROUTED": lambda p: _rewrite(
                p / "docs" / "intake" / "2026-01-15.md",
                "- **→** `.gravity/support/PLAN.timeout.md`\n", ""),
            "INTAKE_FIELD_UNFILLED": lambda p: _rewrite(
                p / "docs" / "intake" / "2026-01-15.md",
                "v1.2.0 · Windows 11 · ko-KR · 10k-file folder",
                "<version/tag · OS · locale · data>"),
            "INTAKE_FIELD_MISSING": lambda p: _rewrite(
                p / "docs" / "intake" / "2026-01-15.md",
                "- **Evidence:** ticket #4415\n", ""),
        }
        for code, mutate in drifts.items():
            bad = Path(tmp) / f"intake-bad-{code.lower()}"
            shutil.copytree(good, bad)
            mutate(bad)
            caught = [f for f in check_intake(bad) if f.code == code]
            if caught:
                print(f"selftest: intake drift correctly caught -> {code}.")
            else:
                ok = False
                print(f"selftest: EXPECTED {code}, but the intake checker stayed silent.")

    # --- patch-loop half: drive patch_slice.py's walls end-to-end on its fixture. ---
    ok = _patchloop_selftest() and ok

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

    h = sub.add_parser("spec", help="verify SPEC.md Gates + enforcement tags against reality")
    h.add_argument("--project", required=True, help="path to the project root (or alias)")
    h.set_defaults(func=cmd_spec)

    s = sub.add_parser("scenario", help="assert a golden-scenario's postconditions")
    s.add_argument("--scenario", required=True, help="path to the scenario dir (has expect.json)")
    s.add_argument("--actual", required=True, help="path to the post-run project to check")
    s.set_defaults(func=cmd_scenario)

    w = sub.add_parser("workspace", help="check tier/index drift across the whole workspace")
    w.set_defaults(func=cmd_workspace)

    n = sub.add_parser("intake", help="check docs/intake sheets — six facts per item, routing, no bugs domain")
    n.add_argument("--project", required=True, help="path to the project root")
    n.set_defaults(func=cmd_intake)

    t = sub.add_parser("selftest", help="prove the checker on the bundled fixture")
    t.set_defaults(func=cmd_selftest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
