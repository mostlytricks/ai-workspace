#!/usr/bin/env python3
"""
check.py — gravity's checker CLI + the workspace-scoped structural checks.

Two halves, split by scope (the workspace's own "one concern, one home" rule
applied to its checker):

  gravity/lib/check_project.py   PORTABLE — judges one project from its own
                                 docs (consistency, spec honesty, intake,
                                 given). Travels with the protocol, so a bare
                                 clone carrying .gravity/lib/ checks itself.
  this file                      WORKSPACE — tier/junction/PROJECTS.md drift,
                                 the golden-scenario fixtures, the selftest
                                 harness, and the CLI door for all of it.

Workspace rules (tiers, junctions, PROJECTS.md) are never embedded in a
project, so `check_workspace` stays here and never moves into lib/.

Usage:
  python check.py consistency --project DIR|alias
  python check.py spec        --project DIR|alias
  python check.py intake      --project DIR|alias
  python check.py given       --project DIR|alias
  python check.py workspace   [--root DIR]
  python check.py scenario    --scenario SCENARIO_DIR --actual DIR
  python check.py selftest

`spec` is the honesty checker: it verifies every `.gravity/<domain>/SPEC.md`'s
Gate command and enforcement tags against the repo's reality (package.json
scripts, test files), so a SPEC can't silently keep claiming walls that no
longer exist. Same under-claiming philosophy as `consistency`: FAIL only on
what is provably dead, WARN on weak signals, stay silent where we can't verify.

Importable too: `from check import check_gravity_consistency` still works —
it re-exports the portable half, so every existing caller (/triage, the
observatory drift card) keeps its one import site.
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
import time
from pathlib import Path

# The portable half lives with the protocol (gravity/lib/), so it can be
# installed into a project and run off-workspace. Re-exported here so this
# module stays the single import site every existing caller already knows.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gravity" / "lib"))
from check_project import (                                       # noqa: E402,F401
    COUPLING_THRESHOLD,
    CROSS_CUTTING,
    FAIL,
    NON_DOMAIN_DIRS,
    REGIONS,
    STALE_SLICE_DAYS,
    WARN,
    Finding,
    check_gravity_consistency,
    check_given,
    check_intake,
    check_spec_honesty,
    discover_domains,
    protocol_version,
    scan_couplings,
    scan_plans,
    spec_tag_census,
    _read,
    _section,
    _section_by,
    _slug_in,
)

# Every word of the root manual auto-loads into every session — the workspace's
# own CONTEXT-prune rule, applied to itself. Grow past this and push detail
# down into .claude/commands/ or docs/HANDBOOK.md (one concern, one home).
MANUAL_WORD_BUDGET = 5500






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




def _given_fixture(base: Path) -> None:
    """A mini project whose given layer is honest: empty inbox, one cross-cutting
    doc, one domain doc + a private raw pointer, all manifested."""
    (base / ".gravity" / "inbox").mkdir(parents=True)
    cross = base / ".gravity" / "given"
    cross.mkdir()
    (cross / "company-context.md").write_text(
        "# What the earth is\n\nThe org sells sync tooling to mid-market teams.\n",
        encoding="utf-8")
    (cross / "MANIFEST.md").write_text(
        "# GIVEN — fixture-helpdesk — manifest\n\n"
        "| File | Source (who gave it) | Received | Version / validity | Authoritative for | Fidelity | Privacy |\n"
        "|---|---|---|---|---|---|---|\n"
        "| `company-context.md` | workspace owner | 2026-01-14 | evergreen | org context | verbatim | committable |\n",
        encoding="utf-8")
    dom = base / ".gravity" / "support" / "given"
    dom.mkdir(parents=True)
    (dom / "erp-data-dictionary.md").write_text(
        "# ERP data dictionary (readable)\n\n| table | meaning |\n|---|---|\n"
        "| SYNC_JOB | one sync attempt |\n", encoding="utf-8")
    (dom / "MANIFEST.md").write_text(
        "# GIVEN — fixture-helpdesk, domain: support — manifest\n\n"
        "| File | Source (who gave it) | Received | Version / validity | Authoritative for | Fidelity | Privacy |\n"
        "|---|---|---|---|---|---|---|\n"
        "| `erp-data-dictionary.md` | Kim (DBA) | 2026-01-10 | ERP v11 | table/column meanings | reformatted (from `raw/erp-dict.xlsx`) | committable |\n"
        "| `raw/erp-dict.xlsx` | Kim (DBA) | 2026-01-10 | ERP v11 | tiebreak original | verbatim | private — local only, git-ignored |\n",
        encoding="utf-8")


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


def cmd_given(args) -> int:
    project = Path(args.project).resolve()
    findings = check_given(project)
    print(f"project: {project}")
    print(f"given dirs: {len(_given_dirs(project))}")
    _print(findings)
    fails = sum(1 for f in findings if f.severity == FAIL)
    if findings:
        print(f"{fails} fail(s), {len(findings) - fails} warning(s).")
    else:
        print("OK — inbox empty, every given file manifested, no ghost rows.")
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

    # --- coupling half: strongly cross-referenced domains with no contract. ---
    if scan_couplings is not None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "coupled"
            shutil.copytree(fixture, bad)
            doms = sorted(discover_domains(bad / ".gravity"))
            a = doms[0]
            if len(doms) > 1:
                b = doms[1]
            else:
                b = "partner"
                (bad / ".gravity" / b).mkdir()
                (bad / ".gravity" / b / "PLAN.md").write_text(
                    "# PLAN — partner\n", encoding="utf-8")
            plan_a = next((bad / ".gravity" / a).glob("PLAN*.md"),
                          bad / ".gravity" / a / "PLAN.md")
            with open(plan_a, "a", encoding="utf-8") as fh:
                fh.write("\n" + "\n".join(
                    f"- see {b}/SPEC.md" for _ in range(COUPLING_THRESHOLD)) + "\n")
            caught = [f for f in check_gravity_consistency(bad)
                      if f.code == "COUPLING_UNCONTRACTED"]
            if caught:
                print("selftest: uncontracted coupling correctly caught "
                      f"({a}+{b} x{COUPLING_THRESHOLD} -> COUPLING_UNCONTRACTED).")
            else:
                ok = False
                print("selftest: EXPECTED COUPLING_UNCONTRACTED for the seeded "
                      f"{a}+{b} cross-references, but the checker stayed silent.")

    # --- comet half: an aged ○ slice must draw SLICE_STALE, by BOTH doors. ---
    if scan_plans is not None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "comet"
            shutil.copytree(fixture, bad)
            dom = sorted(discover_domains(bad / ".gravity"))[0]
            # Door 1 — mtime fallback: a ○ slice with no written date, old file.
            stale = bad / ".gravity" / dom / "PLAN.stale-chore.md"
            stale.write_text("# PLAN — stale chore\n\nStatus: ○ planned\n",
                             encoding="utf-8")
            old_ts = time.time() - (STALE_SLICE_DAYS + 10) * 86400
            os.utime(stale, (old_ts, old_ts))
            caught = [f for f in check_gravity_consistency(bad)
                      if f.code == "SLICE_STALE" and f.domain == dom]
            if caught:
                print(f"selftest: {STALE_SLICE_DAYS + 10}d-old ○ slice correctly "
                      "caught -> SLICE_STALE (mtime door).")
            else:
                ok = False
                print("selftest: EXPECTED SLICE_STALE for the aged ○ slice, "
                      "but the checker stayed silent.")
            # Door 2 — edit-immune written date: a FRESH file (mtime=now) whose
            # status note carries an old `deferred DATE` must still fire, proving
            # re-labelling can't reset the clock.
            stamp = time.strftime("%Y-%m-%d", time.localtime(
                time.time() - (STALE_SLICE_DAYS + 40) * 86400))
            dated = bad / ".gravity" / dom / "PLAN.parked-fresh.md"
            dated.write_text(
                f"# PLAN — parked fresh\n\n"
                f"Status: ○ planned — parked; deferred {stamp}\n",
                encoding="utf-8")   # mtime = now, so only the written date can catch it
            caught2 = [f for f in check_gravity_consistency(bad)
                       if f.code == "SLICE_STALE" and "deferred" in f.message
                       and dated.name in f.message]
            if caught2:
                print("selftest: freshly-written ○ slice with an old `deferred` "
                      "date correctly caught -> SLICE_STALE (edit-immune door).")
            else:
                ok = False
                print("selftest: EXPECTED SLICE_STALE via the written `deferred` "
                      "date on a fresh file, but the checker stayed silent.")

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

        # SPEC_FREEFORM — strip the whole ## Rules checklist: a pre-v2 sheet.
        bad = Path(tmp) / "spec-bad-freeform"
        _spec_fixture(bad)
        spec_path = bad / ".gravity" / "model" / "SPEC.md"
        spec_path.write_text(
            re.sub(r"^## Rules.*?(?=^## |\Z)", "",
                   spec_path.read_text(encoding="utf-8"), flags=re.M | re.S),
            encoding="utf-8")
        caught = [f for f in check_spec_honesty(bad) if f.code == "SPEC_FREEFORM"]
        if caught:
            print("selftest: freeform SPEC (no ## Rules checklist) correctly "
                  "caught -> SPEC_FREEFORM.")
        else:
            ok = False
            print("selftest: EXPECTED SPEC_FREEFORM after stripping ## Rules, "
                  "but the checker stayed silent.")

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

    # --- given half: an honest given layer passes; each drift is caught. ---
    with tempfile.TemporaryDirectory() as tmp:
        good = Path(tmp) / "given-good"
        _given_fixture(good)
        good_findings = check_given(good)
        if good_findings:
            ok = False
            print("selftest: EXPECTED honest given fixture to pass, but:")
            _print(good_findings)
        else:
            print("selftest: honest given fixture passes (inbox empty, manifested, no ghosts).")

        drifts = {
            "INBOX_UNROUTED": lambda p: (p / ".gravity" / "inbox" / "dropped.xlsx").write_text(
                "raw", encoding="utf-8"),
            "GIVEN_UNMANIFESTED": lambda p: (p / ".gravity" / "given" / "stray-notes.md").write_text(
                "unregistered", encoding="utf-8"),
            "GIVEN_GHOST_ROW": lambda p: (p / ".gravity" / "support" / "given"
                                          / "erp-data-dictionary.md").unlink(),
        }
        for code, mutate in drifts.items():
            bad = Path(tmp) / f"given-bad-{code.lower()}"
            shutil.copytree(good, bad)
            mutate(bad)
            caught = [f for f in check_given(bad) if f.code == code]
            if caught:
                print(f"selftest: given drift correctly caught -> {code}.")
            else:
                ok = False
                print(f"selftest: EXPECTED {code}, but the given checker stayed silent.")

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

    g = sub.add_parser("given", help="check the given layer — empty inbox, manifested files, no ghost rows")
    g.add_argument("--project", required=True, help="path to the project root")
    g.set_defaults(func=cmd_given)

    t = sub.add_parser("selftest", help="prove the checker on the bundled fixture")
    t.set_defaults(func=cmd_selftest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
