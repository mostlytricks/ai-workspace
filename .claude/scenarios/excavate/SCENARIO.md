# Scenario: `/excavate` maps a brownfield system without inventing a seam

**Command under test:** `/excavate <project>`
**The failure it guards against:** a *fabricated seam* — a Boundary Map row for a connection that doesn't exist (a dead frontend call mapped as if a backend serves it, an orphaned mapper statement mapped as a live DB seam), or real seams silently missed. On a legacy system the integration SPEC is the first thing every later change trusts; a wrong map poisons everything downstream.

## What's golden here

The agent step (an LLM running the command) is **not** automated. What's golden is:

1. **The input** — `fixture/`, a virgin fake legacy system (**no** `.gravity/`, no `CLAUDE.md` — the command creates them): `web/` (fetch client + component), `order-api/` (Spring Boot + MyBatis, port 8081), `inventory-api/` (Spring Boot, port 8082). It contains exactly **three real seams** and **two traps**:
   - real: `web → order-api` (`/api/orders`, `/api/customers/{id}`), `order-api → inventory-api` (`/api/stock` via `inventory.base-url`), `order-api → Oracle` (`ORDERS`, `CUSTOMERS` via `OrderMapper.xml`)
   - trap 1: `web/src/api.js` calls **`/api/ghost/stats`** — no controller anywhere serves it (a dead call: finding, not seam)
   - trap 2: `OrderMapper.xml` has **`selectAuditTrail`** on `LEGACY_AUDIT` — no interface method, no caller (an orphaned statement: finding, not seam)
2. **The assertion** — `check.py scenario`: `.gravity/integration/` exists with the SPEC + four structural dumps, the SPEC mentions every real seam **and** both traps (`require_content`), but neither trap appears inside the `## Boundary Map` section (`forbid_in_section`), spec honesty reports zero FAILs, and nothing is UNDERWIRED (MISSION/PLAN are legitimately absent — the checker skips indexes that don't exist on a two-doc brownfield project).

You replay this whenever you change `/excavate` (the command), the brownfield intake order (CLAUDE.md §5 / HANDBOOK), or the integration variant of `SPEC.template.md`.

## Replay

From `ai-workspace/`:

```bash
# 1. Copy the golden input to a scratch dir (never mutate the fixture).
ACTUAL="$(mktemp -d)/legacy-mart"
cp -r .claude/scenarios/excavate/fixture "$ACTUAL"

# 2. Open an agent at $ACTUAL and run the command under test:
#       /excavate legacy-mart
#    (The honest outcome: CLAUDE.md + CONTEXT.md seeded from the discovered
#     services/ports; .gravity/integration/SPEC.md with a Boundary Map whose
#     every row cites its source file; /api/ghost/stats and LEGACY_AUDIT land
#     in findings/OPEN, never in the map; structural/ dumps carry the
#     regenerable header. The DB data-dictionary pass stays an OPEN: item.)

# 3. Assert the postconditions.
python .claude/scenarios/check.py scenario \
    --scenario .claude/scenarios/excavate \
    --actual "$ACTUAL"
```

**Pass** = the integration contract exists, every real seam is mapped, both traps are surfaced as findings but kept out of the Boundary Map, and the SPEC is honest. **Fail** = a missed seam, a fabricated seam (either trap inside the map), a missing dump, or a template leftover.

## Why the traps are unambiguous

Both traps are *provably* not seams — that's what makes the assertion deterministic rather than judgment: `/api/ghost/stats` matches no `@GetMapping`/`@RequestMapping` in any service (grep the whole fixture), and `selectAuditTrail` has no method on the `OrderMapper` interface and no `sqlSession` string-call anywhere. An agent can only put them in the Boundary Map by *not checking* — which is precisely the behavior under test.
