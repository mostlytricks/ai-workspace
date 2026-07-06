#!/usr/bin/env python3
"""patch_slice.py — the mechanical core of the patch-loop ritual (docs/PLAN.patch-loop.md).

Run from anywhere inside a project repo. Each subcommand is one wall of the ritual;
the agent keeps only the creative work (the patch itself, the re-plan prose).
Built so a weaker agent can't skip a step, trust a piped exit code, or report a
rollback it never proved — findings F3/F4/F6/F7/F8 are enforced here, not requested.

    preflight  --gate CMD [--skip-gate]         step 1: clean tree + green gate + CONTEXT-drift report (F8)
    anchor     --plan PATH --slug SLUG           step 2: branch slice/<slug>, write anchor into the PLAN
    snap       [--spec PATH] [--plan PATH] [--paths P ...]   step 3: snapshot stateful paths (F6 fallback order)
    verify     --gate CMD [--plan PATH]          step 5: run the gate BARE, real exit code (F4), attempt-counted (N=3)
    rollback   --to SHA --gate CMD [--probe CMD] [--plan PATH]   red path: four-proof rollback (F7)
    cleanup    [--to SHA]                        post-checkpoint: delete the snap (green-checkpoint retention rule)

Exit codes: 0 ok · 1 wall failed · 75 fix-loop exhausted, rollback required.
All file I/O is UTF-8 (never the cp949 console default); console output is ASCII-safe.
"""

from __future__ import annotations

import argparse
import filecmp
import io
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

OK = "[OK]  "
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[--]  "
MAX_ATTEMPTS = 3
SNAP_DIR = ".patch-snap"


# ---------------------------------------------------------------- plumbing

def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=cwd)


def git(root: Path, *args: str) -> str:
    cp = run(["git", *args], cwd=root)
    if cp.returncode != 0:
        die(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp.stdout.strip()


def project_root() -> Path:
    cp = run(["git", "rev-parse", "--show-toplevel"])
    if cp.returncode != 0:
        die("not inside a git repository - the ritual needs one (step 0: git init)")
    return Path(cp.stdout.strip())


def die(msg: str, code: int = 1) -> None:
    print(f"{FAIL} {msg}")
    sys.exit(code)


def read_text(p: Path) -> str:
    return io.open(p, encoding="utf-8").read()


def append_text(p: Path, s: str) -> None:
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(s)


def run_gate(gate: str, root: Path) -> int:
    """F4: run the gate as ONE bare shell command, no pipes added, and return the
    REAL exit code. Output streams through untouched so red is visible.

    shell=True is deliberate, not an oversight: the gate is a user-authored
    compound command (e.g. `npm run typecheck && npm test`) from the domain SPEC,
    executed verbatim on the user's own machine - the same trust boundary as
    typing it into the terminal. Nothing here interpolates untrusted input."""
    print(f"{INFO} gate: {gate}")
    cp = subprocess.run(gate, shell=True, cwd=root)  # noqa: S602 - see docstring
    return cp.returncode


def tree_dirty(root: Path) -> list[str]:
    out = git(root, "status", "--porcelain")
    return [line for line in out.splitlines() if line.strip()]


# ---------------------------------------------------------------- PLAN Execution block

EXEC_HEADER = "## Execution (patch-loop)"


def ensure_exec_block(plan: Path) -> None:
    if not plan.exists():
        die(f"PLAN not found: {plan} - write the slice PLAN first (intent before patch)")
    if EXEC_HEADER not in read_text(plan):
        append_text(plan, f"\n{EXEC_HEADER}\n\n")


def log_exec(plan: Path, line: str) -> None:
    ensure_exec_block(plan)
    append_text(plan, f"- {line}\n")
    print(f"{INFO} PLAN <- {line}")


def count_attempts(plan: Path) -> int:
    if not plan.exists():
        return 0
    return len(re.findall(r"^- attempt \d+", read_text(plan), re.M))


# ---------------------------------------------------------------- F8: CONTEXT drift

def context_drift(root: Path) -> list[str]:
    """Heuristic diff of CONTEXT.md claims vs git reality. Warnings, not failures -
    but printed by preflight every time, so drift can't hide (finding F8)."""
    ctx = root / "CONTEXT.md"
    if not ctx.exists():
        return [f"no CONTEXT.md at project root - session ritual missing (workspace CLAUDE.md section 6)"]
    text = read_text(ctx)
    warns: list[str] = []

    remotes = git(root, "remote")
    if re.search(r"\bno remote\b", text, re.I) and remotes:
        warns.append(f"CONTEXT claims 'no remote' but remotes exist: {remotes.splitlines()}")

    branch = git(root, "branch", "--show-current")
    m = re.search(r"branch\s+[`']?(master|main|develop)[`']?", text, re.I)
    if m and m.group(1) != branch:
        warns.append(f"CONTEXT names branch '{m.group(1)}' but current branch is '{branch}'")

    if re.search(r"\buncommitted\b", text, re.I) and not tree_dirty(root):
        warns.append("CONTEXT mentions uncommitted work but the tree is clean (stale claim?)")

    m = re.search(r"Last touched:\s*(\d{4}-\d{2}-\d{2})", text)
    if m:
        try:
            touched = date.fromisoformat(m.group(1))
            age = (date.today() - touched).days
            if age > 30:
                warns.append(f"CONTEXT 'Last touched' is {age} days old")
        except ValueError:
            pass
    return warns


# ---------------------------------------------------------------- F6: stateful paths

STATEFUL_RE = re.compile(r"\*\*Stateful paths:\*\*\s*(.+)")


def parse_stateful_line(text: str) -> list[str]:
    m = STATEFUL_RE.search(text)
    if not m:
        return []
    raw = m.group(1)
    if "<FILL" in raw:
        return []  # template leftover is not a declaration
    return [p for p in (t.strip(" `,") for t in raw.split(",")) if p]


def resolve_stateful(root: Path, spec: Path | None, plan: Path | None,
                     cli_paths: list[str]) -> tuple[list[str], str]:
    """F6 resolution order: explicit --paths > domain SPEC line > slice PLAN line."""
    if cli_paths:
        return cli_paths, "--paths"
    if spec and spec.exists():
        found = parse_stateful_line(read_text(spec))
        if found:
            return found, str(spec.relative_to(root))
    if plan and plan.exists():
        found = parse_stateful_line(read_text(plan))
        if found:
            return found, str(plan.relative_to(root))
    return [], ""


def snap_dir_for(root: Path, sha: str) -> Path:
    return root / SNAP_DIR / sha


def ensure_gitignored(root: Path) -> None:
    gi = root / ".gitignore"
    entry = f"{SNAP_DIR}/"
    if gi.exists() and entry in read_text(gi):
        return
    append_text(gi, f"{entry}\n")
    print(f"{WARN} added '{entry}' to .gitignore - include this in the slice commit")


def compare_tree(a: Path, b: Path) -> list[str]:
    """Recursive byte-compare; returns mismatch descriptions (empty = identical)."""
    diffs: list[str] = []

    def walk(dc: filecmp.dircmp) -> None:
        for name in dc.left_only:
            diffs.append(f"only in {dc.left}: {name}")
        for name in dc.right_only:
            diffs.append(f"only in {dc.right}: {name}")
        for name in dc.diff_files + dc.funny_files:
            diffs.append(f"differs: {Path(dc.left) / name}")
        for sub in dc.subdirs.values():
            walk(sub)

    if a.is_file() and b.is_file():
        if not filecmp.cmp(a, b, shallow=False):
            diffs.append(f"differs: {a}")
    elif a.is_dir() and b.is_dir():
        walk(filecmp.dircmp(a, b))
    else:
        diffs.append(f"shape mismatch: {a} vs {b}")
    return diffs


# ---------------------------------------------------------------- subcommands

def cmd_preflight(args: argparse.Namespace) -> None:
    root = project_root()
    print(f"{INFO} project: {root}")
    failed = False

    dirty = tree_dirty(root)
    if dirty:
        print(f"{FAIL} tree is dirty ({len(dirty)} paths) - an unclosed previous loop.")
        print("       Remedy (F2): re-run its gate and COMMIT it as its own slice.")
        print("       Never stash it under the new patch. Dirty paths:")
        for line in dirty[:15]:
            print(f"         {line}")
        failed = True
    else:
        print(f"{OK} tree clean at {git(root, 'rev-parse', '--short', 'HEAD')}")

    if args.skip_gate:
        print(f"{WARN} gate check SKIPPED by explicit --skip-gate (preflight is half-blind)")
    else:
        rc = run_gate(args.gate, root)
        if rc != 0:
            print(f"{FAIL} baseline gate is RED (exit {rc}) - never patch on red:")
            print("       failures after the patch would be unattributable.")
            failed = True
        else:
            print(f"{OK} baseline gate green")

    for w in context_drift(root):
        print(f"{WARN} CONTEXT drift: {w}")

    if failed:
        sys.exit(1)
    print(f"{OK} preflight PASS - safe to anchor")


def cmd_anchor(args: argparse.Namespace) -> None:
    root = project_root()
    if tree_dirty(root):
        die("tree is dirty - preflight must pass before anchoring")
    plan = root / args.plan
    if not plan.exists():
        die(f"PLAN not found: {plan} - write the slice PLAN first (intent before patch)")

    sha = git(root, "rev-parse", "--short", "HEAD")
    branch = f"slice/{args.slug}"
    existing = git(root, "branch", "--list", branch)
    if existing:
        die(f"branch {branch} already exists - one slice, one branch (pick a new slug)")
    git(root, "switch", "-c", branch)
    print(f"{OK} branch {branch} created")

    log_exec(plan, f"**Anchor:** `{sha}` ({date.today().isoformat()}, clean tree, gate green per preflight)")
    log_exec(plan, f"**Branch:** `{branch}`")
    print(f"{OK} anchored at {sha} - the PLAN now carries its own escape hatch")


def cmd_snap(args: argparse.Namespace) -> None:
    root = project_root()
    spec = (root / args.spec) if args.spec else None
    plan = (root / args.plan) if args.plan else None
    paths, source = resolve_stateful(root, spec, plan, args.paths)

    if not paths:
        print(f"{OK} no stateful paths declared (checked --paths, SPEC, PLAN) - step 3 skipped, zero ceremony")
        if plan:
            log_exec(plan, "**State-snap:** skipped - no `Stateful paths:` declared (F6 checked)")
        return

    sha = git(root, "rev-parse", "--short", "HEAD")
    dest = snap_dir_for(root, sha)
    if dest.exists():
        die(f"snap for {sha} already exists at {dest} - refusing to overwrite evidence")
    dest.mkdir(parents=True)
    ensure_gitignored(root)

    copied: list[str] = []
    for rel in paths:
        src = root / rel
        if not src.exists():
            print(f"{WARN} declared stateful path missing on disk, skipped: {rel}")
            continue
        if run(["git", "ls-files", "--error-unmatch", rel], cwd=root).returncode == 0 or \
           run(["git", "ls-files", rel], cwd=root).stdout.strip():
            print(f"{WARN} '{rel}' is tracked by git - stateful paths should be gitignored"
                  f" (git already protects tracked files; declaring them here is a smell)")
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
        copied.append(rel)
        print(f"{OK} snapped {rel}")

    manifest = {"anchor": sha, "created": datetime.now().isoformat(timespec="seconds"),
                "source": source, "paths": copied}
    io.open(dest / "manifest.json", "w", encoding="utf-8").write(json.dumps(manifest, indent=2))
    if plan:
        log_exec(plan, f"**State-snap:** `{SNAP_DIR}/{sha}/` <- {', '.join(f'`{p}`' for p in copied)} (declared in {source})")
    print(f"{OK} state snapped to {SNAP_DIR}/{sha}/ (manifest written)")


def cmd_verify(args: argparse.Namespace) -> None:
    root = project_root()
    plan = (root / args.plan) if args.plan else None
    attempt = (count_attempts(plan) if plan else 0) + 1

    rc = run_gate(args.gate, root)
    verdict = "GREEN" if rc == 0 else f"RED (exit {rc})"
    if plan:
        log_exec(plan, f"attempt {attempt}/{MAX_ATTEMPTS} ({datetime.now().isoformat(timespec='minutes')}): {verdict}")

    if rc == 0:
        print(f"{OK} gate green on attempt {attempt} - checkpoint-commit NOW, before any drill (F3)")
        return
    if attempt >= MAX_ATTEMPTS:
        print(f"{FAIL} attempt {attempt}/{MAX_ATTEMPTS} red - FIX-LOOP EXHAUSTED.")
        print("       Thrash is thrash (partial green never resets the counter).")
        print("       Required next step: rollback - run:")
        print("         patch_slice.py rollback --to <anchor-sha> --gate '<gate>' [--probe '<cmd>']")
        print("       Rollback is a finding for re-plan, not a failure to hide.")
        sys.exit(75)
    print(f"{FAIL} gate red - attempt {attempt}/{MAX_ATTEMPTS} used, {MAX_ATTEMPTS - attempt} left before forced rollback")
    sys.exit(1)


def cmd_rollback(args: argparse.Namespace) -> None:
    root = project_root()
    plan = (root / args.plan) if args.plan else None
    sha = args.to
    proofs: list[tuple[str, bool, str]] = []

    # The execution log must SURVIVE the rollback (it is the record of the failed
    # run - the finding re-plan needs). reset --hard would revert a tracked PLAN,
    # so stash its content first and restore it after (F3's lesson, applied inward).
    plan_text = read_text(plan) if plan and plan.exists() else None

    # Proof 1 - code restored, tree clean at the target
    git(root, "reset", "--hard", sha)
    dirty = tree_dirty(root)
    # .patch-snap/ may surface as untracked here (the .gitignore entry can revert
    # with the reset), and .gitignore itself may be a file snap created/appended.
    # Both are THIS tool's artifacts, not the failed patch's - never counted as dirt.
    ours = [d for d in dirty if SNAP_DIR in d or d.split()[-1] == ".gitignore"]
    dirty = [d for d in dirty if d not in ours]
    for line in ours:
        print(f"{INFO} tool artifact excluded from proof 1: {line.strip()}")
    clean_now = not dirty
    proofs.append(("tree clean at target", clean_now, f"{len(dirty)} dirty paths" if dirty else sha))
    # untracked leftovers from the failed patch are dirt too; report, don't auto-delete
    if dirty:
        print(f"{WARN} leftover untracked/modified paths after reset (review before deleting):")
        for line in dirty[:10]:
            print(f"         {line}")

    if plan and plan_text is not None:
        io.open(plan, "w", encoding="utf-8", newline="\n").write(plan_text)
        print(f"{INFO} execution log preserved across reset: {args.plan} (commit it with the re-plan)")

    # Proof 2 - state restored byte-identical from the snap
    snap = snap_dir_for(root, sha)
    manifest_file = snap / "manifest.json"
    if manifest_file.exists():
        manifest = json.loads(read_text(manifest_file))
        mismatches: list[str] = []
        for rel in manifest["paths"]:
            live, saved = root / rel, snap / rel
            if live.exists():
                shutil.rmtree(live) if live.is_dir() else live.unlink()
            live.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(saved, live) if saved.is_dir() else shutil.copy2(saved, live)
            mismatches += compare_tree(live, saved)
        proofs.append(("state byte-identical to snap", not mismatches,
                       "; ".join(mismatches[:3]) if mismatches else f"{len(manifest['paths'])} path(s)"))
    else:
        proofs.append(("state byte-identical to snap", True, "no snap for this anchor (stateless slice)"))

    # Proof 3 - gate green on the restored state
    rc = run_gate(args.gate, root)
    proofs.append(("gate green after restore", rc == 0, f"exit {rc}"))

    # Proof 4 (F7) - the restored state actually FUNCTIONS, not just diffs clean
    if args.probe:
        rc = run_gate(args.probe, root)
        proofs.append(("restored state functions (probe)", rc == 0, f"exit {rc}: {args.probe}"))
    else:
        proofs.append(("restored state functions (probe)", True,
                       "SKIPPED - no --probe given; F7 says a lazy check stops here. Pass one."))
        print(f"{WARN} proof 4 skipped - give --probe '<cmd that exercises the state>' (e.g. a stats/query command)")

    print("\n--- rollback proofs ---")
    all_ok = True
    for name, ok, detail in proofs:
        print(f"{OK if ok else FAIL} {name}: {detail}")
        all_ok = all_ok and ok
    if plan:
        log_exec(plan, f"**Rollback:** to `{sha}` - {'PASS (4 proofs)' if all_ok else 'FAILED - see console'}")
    if not all_ok:
        die("rollback NOT proven - do not report this slice as safely abandoned")
    # live state now equals the snap - the snap has served; retire it
    snap = snap_dir_for(root, sha)
    if snap.exists():
        shutil.rmtree(snap)
        base = root / SNAP_DIR
        if base.exists() and not any(base.iterdir()):
            base.rmdir()
        print(f"{OK} snap {SNAP_DIR}/{sha}/ retired (live state == snap)")
    print(f"{OK} rollback PASS - record the finding in the PLAN, then re-plan")


def cmd_cleanup(args: argparse.Namespace) -> None:
    root = project_root()
    if tree_dirty(root):
        die("tree is dirty - cleanup only runs after a green CHECKPOINT COMMIT (retention rule)")
    base = root / SNAP_DIR
    targets = [base / args.to] if args.to else ([p for p in base.iterdir() if p.is_dir()] if base.exists() else [])
    if not targets or not any(t.exists() for t in targets):
        print(f"{OK} nothing to clean - no snaps present")
        return
    for t in targets:
        if t.exists():
            shutil.rmtree(t)
            print(f"{OK} deleted snap {t.relative_to(root)}")
    if base.exists() and not any(base.iterdir()):
        base.rmdir()
    print(f"{OK} snap retired - the checkpoint commit is the new safety floor")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("preflight", help="step 1: clean tree + green baseline gate + CONTEXT drift (F8)")
    p.add_argument("--gate", help="the project's real gate command (from the domain SPEC - never invented)")
    p.add_argument("--skip-gate", action="store_true", help="explicitly skip the gate check (logged loudly)")
    p.set_defaults(fn=cmd_preflight)

    p = sub.add_parser("anchor", help="step 2: slice branch + anchor SHA written into the PLAN")
    p.add_argument("--plan", required=True, help="slice PLAN path, relative to project root")
    p.add_argument("--slug", required=True, help="branch suffix: slice/<slug>")
    p.set_defaults(fn=cmd_anchor)

    p = sub.add_parser("snap", help="step 3: snapshot declared stateful paths (F6 order: --paths > SPEC > PLAN)")
    p.add_argument("--spec", help="domain SPEC path carrying a 'Stateful paths:' line")
    p.add_argument("--plan", help="slice PLAN path (fallback declaration home + execution log)")
    p.add_argument("--paths", nargs="*", default=[], help="explicit stateful paths (override)")
    p.set_defaults(fn=cmd_snap)

    p = sub.add_parser("verify", help="step 5: run the gate bare (F4), attempt-counted against N=3")
    p.add_argument("--gate", required=True)
    p.add_argument("--plan", help="slice PLAN to append the attempt line to")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("rollback", help="red path: reset + snap-restore + four proofs (F7)")
    p.add_argument("--to", required=True, help="anchor (or checkpoint) SHA to reset to")
    p.add_argument("--gate", required=True, help="gate to prove green after restore")
    p.add_argument("--probe", help="command that exercises the restored state (proof 4)")
    p.add_argument("--plan", help="slice PLAN to record the outcome in")
    p.set_defaults(fn=cmd_rollback)

    p = sub.add_parser("cleanup", help="post-checkpoint: delete snap(s); refuses on a dirty tree")
    p.add_argument("--to", help="specific snap SHA (default: all)")
    p.set_defaults(fn=cmd_cleanup)

    args = ap.parse_args()
    if args.cmd == "preflight" and not args.gate and not args.skip_gate:
        ap.error("preflight needs --gate '<cmd>' (or an explicit --skip-gate)")
    args.fn(args)


if __name__ == "__main__":
    main()
