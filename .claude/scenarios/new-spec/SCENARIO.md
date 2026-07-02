# Scenario: `/new-spec` authors an *honest* SPEC

**Command under test:** `/new-spec <project> <domain>`
**The failure it guards against:** a *fabricated wall* — a SPEC whose `Gate:` names a script that doesn't exist, whose `[test:<name>]` points at no test, or which ships template leftovers (`<FILL`, `[test:name]`). A wrong tag is worse than no SPEC: it manufactures false trust in enforcement that isn't there.

## What's golden here

The agent step (an LLM running the command) is **not** automated. What's golden is:

1. **The input** — `fixture/`, a clean `.gravity/` project whose one domain (`model`) has **real code, a real gate (`npm run lint:model`), and named tests — but no `SPEC.md`**. Everything an honest SPEC needs to cite actually exists; everything else would be fabrication.
2. **The assertion** — `check.py`, which verifies the SPEC exists, the domain stays wired (`check_gravity_consistency`), and **every tag is honest** (`check_spec_honesty`: no `SPEC_UNFILLED` / `GATE_DEAD` / `TAG_DEAD`).

You replay this whenever you change `/new-spec` (the command), `SPEC.template.md`, or the enforcement-tag conventions.

## Replay

From `ai-workspace/`:

```bash
# 1. Copy the golden input to a scratch dir (never mutate the fixture).
ACTUAL="$(mktemp -d)/fixture-app"
cp -r .claude/scenarios/new-spec/fixture "$ACTUAL"

# 2. Open an agent at $ACTUAL and run the command under test:
#       /new-spec fixture-app model
#    (The honest outcome: Gate = `npm run lint:model`; rules enforced by
#     scripts/check-model.mjs are [lint]; the two named node:test cases are
#     [test:model-required-fields] / [test:model-status-vocabulary]; anything
#     uncited is [review]. The agent must also run the gate green.)

# 3. Assert the postconditions.
python .claude/scenarios/check.py scenario \
    --scenario .claude/scenarios/new-spec \
    --actual "$ACTUAL"
```

**Pass** = `.gravity/model/SPEC.md` exists, the domain is wired into all four indexes, and spec-honesty reports zero FAILs. **Fail** = a missing SPEC, an unwired index, or any provable lie in the Gate/tags (the bug this scenario exists to catch).

## Expected postconditions (`expect.json`)

- `.gravity/model/SPEC.md` created.
- `model` still wired into the **Doc Map**, **router table** (read-first cell → the SPEC), **MISSION** rows, and **IMPLEMENTATION_PLAN** status spine; no `UNDERWIRED` findings.
- `check_spec_honesty` reports **no FAILs**: no template leftovers, the Gate's scripts/paths exist, every `[test:<name>]` resolves.

## Checking the checker

`python .claude/scenarios/check.py selftest` proves both checkers — including that every scenario's golden fixture is itself clean, and that a dead gate, dead tag, and template leftover are each caught. Run it after editing `check.py`.
