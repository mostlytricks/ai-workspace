# Scenario: `/ship` moves a shipped project to `stable/` honestly

**Command under test:** `/ship <name>`
**The failure it guards against:** a *dishonest ship* — the junction moves but the contract doesn't: CONTEXT.md's Next Step still reads as a task list (no reactivation trigger), or the PROJECTS.md row is left in `## active/`, so the next agent inherits a stable project that lies about its state.

## What's golden here

The agent step (an LLM running the command) is **not** automated. What's golden is:

1. **The input** — `fixture/`, a minimal workspace tree with one active project (`starlight`) that genuinely qualifies: release evidence (`CHANGELOG.md [1.0.0]`), a filled CONTEXT.md, nothing in flight. Plain dirs stand in for junctions — the scanner treats tier entries as views.
2. **The assertion** — `check.py workspace`, which mechanically verifies the postconditions over the whole tree. No one eyeballs whether the trigger got written.

Replay this whenever you change `/ship` (the command), the stable-tier contract (workspace CLAUDE.md §1), or `scan_workspace.py` / `check_workspace`.

## Replay

From `ai-workspace/`:

```bash
# 1. Copy the golden input to a scratch dir (never mutate the fixture).
ACTUAL="$(mktemp -d)/ws"
cp -r .claude/scenarios/ship/fixture "$ACTUAL"

# 2. Open an agent at $ACTUAL and run the command under test:
#       /ship starlight
#    (The evidence card should find tag-less but CHANGELOG-versioned v1.0.0;
#     the trigger should come from the CONTEXT's own "nothing in flight" state.)

# 3. Assert the postconditions — the workspace checker IS the expect engine here
#    (cmd_scenario's expect.json vocabulary is per-project .gravity/ shapes; a
#    workspace tree needs the workspace checker instead).
python - <<'EOF'
import sys, os
sys.path.insert(0, ".claude/scenarios")
from check import check_workspace, FAIL
ws = os.environ["ACTUAL"]
findings = check_workspace(ws)
bad = [f for f in findings if f.severity == FAIL or f.code == "MISSING_TRIGGER"]
for f in findings: print(" ", f)
print("PASS" if not bad else "FAIL")
sys.exit(1 if bad else 0)
EOF
```

**Pass** = `starlight` sits under `stable/` (not `active/`), its PROJECTS.md row moved to `## stable/`, and its CONTEXT.md Next Step reads as a reactivation trigger — 0 FAILs, no `MISSING_TRIGGER`. **Fail** = any tier↔index disagreement or a task-shaped Next Step (the dishonest-ship bug this scenario exists to catch).

## Checking the checker

`python .claude/scenarios/check.py selftest` proves the workspace checker itself: a healthy mini-workspace passes, and three seeded drifts (`MULTI_TIER`, `INDEX_MISSING_ON_DISK`, `MISSING_TRIGGER`) are each caught. Run it after editing `check.py` or `scan_workspace.py`.
