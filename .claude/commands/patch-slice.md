---
description: Patch one slice under the patch-loop ritual — git anchor before, bare-gated verify after, bounded fix loop, mandatory re-plan. The script owns the walls; you own the patch and the prose.
argument-hint: <project> [slug]
---

You are running `/patch-slice` from `ai-workspace/`. The user wants to land one slice in project **`$ARGUMENTS`** under the patch-loop ritual (`docs/PLAN.patch-loop.md` — the 7 steps and findings F1–F8 live there). The mechanical walls are **`.claude/scripts/patch_slice.py`**; every step below that has a subcommand is run *through it*, never re-implemented by hand — it was built so a weaker agent can't skip a step, trust a piped exit code, or report a rollback it never proved. You keep exactly two judgment steps: **writing the patch** and **writing the re-plan prose**.

Exit codes from the script: `0` ok · `1` a wall failed (stop, read its output) · `75` fix-loop exhausted, rollback required.

## Step 0 — Resolve the project and the gate

1. Resolve `<project>` via `python .claude/scripts/resolve_project.py <name>`; `cd` into the project (junction or real path — the script finds the repo root itself). Not a git repo → stop; the ritual needs one.
2. Find the **real gate** the `/new-spec` way: the affected domain's `.gravity/<domain>/SPEC.md` **Gate** line first, else the runnable scripts in `package.json` / `pyproject.toml` (`test`, `typecheck`, `lint` — commands that exit non-zero). **Never invent a gate.** No gate at all → say so plainly; the user owns the risk, and `preflight --skip-gate` logs the skip loudly.

## Step 1 — Intent first: the slice PLAN

A slice PLAN must exist **before any edit** (`templates/PLAN.template.md` shape, at `.gravity/<domain>/PLAN.<slug>.md`). If it doesn't, write it now — Goal, Scenario, Slice, Verification. Derive `<slug>` from it if the user didn't give one.

**Bug intake rule:** if this slice is a bug fix, the Scenario block must state the repro as a **currently-false** `given/when/then` — the observable behavior the system does *not* yet exhibit. That failing scenario is the slice's contract-to-be: the fix isn't done until a named test asserts it (step 5). Don't patch a bug you can't state.

## Step 2 — Preflight (walls: clean tree, green baseline, CONTEXT drift — F2/F8)

```bash
python <workspace>/.claude/scripts/patch_slice.py preflight --gate "<gate cmd>"
```

- **Dirty tree** → the script prints the F2 remedy: the dirt is usually an *unclosed previous loop* — verify it, land it as its own commit, don't stash it. Do that, then re-run preflight.
- **CONTEXT-drift lines** → report them to the user verbatim; fix stale CONTEXT claims as part of this session's re-plan.
- **Red baseline** → stop. Never patch on red; failures become unattributable.

## Step 3 — Anchor + snap (walls: escape hatch in the doc, state git can't see — F6)

```bash
python <workspace>/.claude/scripts/patch_slice.py anchor --plan <plan path> --slug <slug>
python <workspace>/.claude/scripts/patch_slice.py snap --spec <domain SPEC> --plan <plan path>
```

The script writes the anchor SHA into the PLAN's Execution block and creates `slice/<slug>`. Snap resolution order is `--paths` > SPEC `Stateful paths:` line > PLAN declaration; "no paths declared" is a clean skip, not an error — most domains have none.

## Step 4 — Patch, then verify (walls: bare gate, N=3 — F4)

**PATCH** — yours: the actual edits, per the slice PLAN. Load the domain SPEC first (the contract), normal working discipline. No auto-commit-per-edit noise.

```bash
python <workspace>/.claude/scripts/patch_slice.py verify --gate "<gate cmd>" --plan <plan path>
```

Then the **behavioral drive**: run the changed flow once for real (the actual API route / CLI invocation / skill run — a fixture counts only if it hits the real entry point). Tests passing ≠ feature working.

- Red → fix and re-verify. The script counts attempts; **exit 75 means the loop is exhausted — it is a stop, not a suggestion:**

```bash
python <workspace>/.claude/scripts/patch_slice.py rollback --to <anchor SHA> --gate "<gate cmd>" --plan <plan path> [--probe "<cmd that exercises restored state>"]
```

Give a `--probe` whenever state was snapped ("restored state actually functions" is the fourth proof — F7; without one the script warns SKIPPED). A rollback is a **finding for re-plan, never a failure to hide** — the script records it in the PLAN; you carry it into step 5.

## Step 5 — Fork green: checkpoint + re-plan (yours)

1. **Checkpoint commit** on the slice branch (project-appropriate message). Fire-drills, if the user wants one, happen **only after this commit** — a drill against uncommitted state destroys the patch (F3).
2. ```bash
   python <workspace>/.claude/scripts/patch_slice.py cleanup
   ```
3. **RE-PLAN** — the step that closes the loop, same session:
   - Slice PLAN: status → ✓ (or the rollback finding), Execution block already carries the mechanical story.
   - `CONTEXT.md`: Completed bullet + fresh Next Step; fix any preflight drift findings.
   - Shipping something reviewable → a WALKTHROUGH (`templates/WALKTHROUGH.template.md`), linked not restated.
   - **Bug graduation:** the once-false scenario now has a named test → promote it into the domain SPEC's **Behavioral Contract** as a `[test:<name>]` line. Intent graduates to contract by earning a wall — bug fixes are the fastest source of honest contract lines.

## Report back

```
Patch-slice: <project> · slice/<slug>
  Anchor:      <sha> → checkpoint <sha>        ← or "rolled back to <sha> (finding recorded)"
  Gate:        "<gate cmd>" green on attempt N/3
  Behavioral:  <the real drive you ran + what it showed>
  Re-plan:     PLAN ✓ · CONTEXT refreshed · <WALKTHROUGH / SPEC graduation if any>
  Merge:       slice branch left for your review — merge/push is your checkpoint
```

## What NOT to do

- **Never run a gate piped** (`| head`, `| tail`) or trust anything but the gate's own exit code — that's why `verify` exists (F4).
- **Never fire-drill or tamper against uncommitted state** — drills only ever run post-checkpoint (F3 wiped a whole patch once).
- **Never push past exit 75** — three swings at the whole gate, then rollback; partial green does not reset the counter.
- **Never delete a snap on red** — `cleanup` refuses on a dirty tree for a reason; the snap is retired only by proven rollback or green checkpoint.
- **Never invent a gate or skip the slice PLAN** — no wall, no ritual; intent before edits.
- **Never merge to main or push** — like `/cut-release`'s tag, the checkpoint commit is where the machine stops and the user reviews.
