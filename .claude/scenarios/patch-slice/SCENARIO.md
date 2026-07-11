# Scenario: `/patch-slice` lands one slice without losing code, state, or the story

**Command under test:** `/patch-slice <project> [slug]` (the thin wrapper over `.claude/scripts/patch_slice.py`)
**The failure it guards against:** an *undisciplined patch* — edits landing on a red or dirty baseline, a piped gate reporting green while red (F4), a fix loop thrashing past N=3, a rollback that quietly loses gitignored state (the snap exists for exactly this), or a session ending with no re-plan so the next agent can't reconstruct what happened.

## What's golden here

The agent step (an LLM running the command) is **not** automated. What's golden is:

1. **The input** — `fixture/`, a mini `.gravity/` project (`fixture-shop`) with a *green gate over a live bug*: `apply_discount` goes negative past 100% and nothing asserts the clamp — untested behavior, which is how real bugs survive. `.gravity/demo/PLAN.fix.md` is the **bug-intake worked example**: its Scenario states the repro as a *currently-false* given/when/then. `state/data.txt` is the declared stateful path (demo SPEC), so the snap/rollback walls have real state to protect.
2. **The assertion** — the **`check.py selftest` patch-loop branch**, which drives `patch_slice.py` over this same fixture mechanically through *both* fork branches (green: preflight→anchor→snap→fix→verify→cleanup; red: 3 failed verifies → exit 75 → four-proof rollback with the corrupted ledger restored byte-identical). The script's walls are self-asserting; the selftest proves they hold.

Replay this whenever you change `patch-slice.md` (the command), `patch_slice.py` (the walls), or the ritual itself (`docs/PLAN.patch-loop.md`).

## Replay

From `ai-workspace/`:

```bash
# 1. Copy the golden input to a scratch dir (never mutate the fixture) and give it
#    the git history + .gitignore the fixture deliberately ships without:
ACTUAL="$(mktemp -d)/shop"
cp -r .claude/scenarios/patch-slice/fixture "$ACTUAL"
cd "$ACTUAL"
printf 'state/\n' > .gitignore          # state is git-invisible — only the snap protects it
git init -q -b main && git add -A && git commit -qm "fixture baseline"

# 2. Open an agent at $ACTUAL and run the command under test:
#       /patch-slice fixture-shop demo-fix
#    (Gate: `python gate.py` from the demo SPEC. The slice PLAN already exists —
#     .gravity/demo/PLAN.fix.md — so the agent goes straight to preflight.)

# 3. Assert the mechanical postconditions (the script's own walls):
git log --oneline            # checkpoint commit on slice/demo-fix, parented at the anchor
python gate.py               # green — including the NEW test_clamp_over_100
grep "attempt" .gravity/demo/PLAN.fix.md   # Execution block tells the whole story
test ! -d .patch-snap && echo "snap retired"
```

**Pass** = the checkpoint commit's parent chain starts at the anchor SHA recorded in `PLAN.fix.md`'s Execution block; the gate is green *with* `test_clamp_over_100` present; the PLAN's status flipped and the scenario was **graduated** into `demo/SPEC.md`'s Behavioral Contract as `[test:test_clamp_over_100]`; CONTEXT.md was refreshed the same session. **Fail** = any edit before the anchor, a gate run through a pipe, attempts past 3/3, or a session ending with the PLAN/CONTEXT untouched (the unclosed-loop bug this ritual exists to catch — F2).

The judgment layer (PLAN status flipped · scenario graduated with its `[test:…]` tag · CONTEXT refreshed) is asserted by reading, not by a checker — it's the half the script deliberately leaves to the agent.

## Checking the checker

`python .claude/scenarios/check.py selftest` drives `patch_slice.py` over this fixture end-to-end, both branches — including the exit-75 exhaustion wall and the four-proof rollback with a deliberately corrupted `state/data.txt` restored byte-identical. Run it after editing `patch_slice.py` or this fixture.
