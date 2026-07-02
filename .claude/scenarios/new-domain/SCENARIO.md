# Scenario: `/new-domain` wires all four indexes

**Command under test:** `/new-domain <project> <domain>`
**The failure it guards against:** an *orphaned domain* — the folder gets created but one of the four registry indexes (Doc Map, router table, MISSION row, PLAN status spine) is silently left unwired, so the next agent and `/triage` never see it.

## What's golden here

The agent step (an LLM running the command) is **not** automated. What's golden is:

1. **The input** — `fixture/`, a clean minimal `.gravity/` project with exactly one already-wired domain (`model`).
2. **The assertion** — `check.py`, which mechanically verifies the postconditions. No one eyeballs whether all four indexes got wired.

You replay this whenever you change `/new-domain` (the command), `GRAVITY.template.md`, or the index conventions.

## Replay

From `ai-workspace/`:

```bash
# 1. Copy the golden input to a scratch dir (never mutate the fixture).
ACTUAL="$(mktemp -d)/fixture-app"
cp -r .claude/scenarios/new-domain/fixture "$ACTUAL"

# 2. Open an agent at $ACTUAL and run the command under test:
#       /new-domain fixture-app scoring
#    (Run the gate honestly: 'scoring' is a real domain — rules worth a SPEC,
#     a multi-step arc — so it should pass the gate and get minted.)

# 3. Assert the postconditions.
python .claude/scenarios/check.py scenario \
    --scenario .claude/scenarios/new-domain \
    --actual "$ACTUAL"
```

**Pass** = `scoring` folder exists with a `PLAN.md`, and is wired into all four indexes with no orphaned routes. **Fail** = any index left unwired (the bug this scenario exists to catch).

## Expected postconditions (`expect.json`)

- `.gravity/scoring/` created, containing at least `PLAN.md`.
- `scoring` appears in the **Doc Map**, the **router table**, the **MISSION** "system in N domains" rows, and the **IMPLEMENTATION_PLAN** status spine.
- No `UNDERWIRED` findings anywhere in the project.

## Checking the checker

`python .claude/scenarios/check.py selftest` proves `check.py` itself: the good fixture passes, and a copy with `model` stripped from the Doc Map is correctly caught as `UNDERWIRED`. Run it after editing `check.py`.
