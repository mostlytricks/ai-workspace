# patch-loop — PLAN

Status: ◑ building <!-- ○ planned · ◑ building · ✓ shipped -->

> **Adopted 2026-07-06.** The workspace-level "patch → verify → re-plan"
> ritual. Gravity today walls *intent* (PLAN + Scenario) and *proof* (WALKTHROUGH, gates)
> but the middle — the act of patching — is undisciplined agent behavior with no wall.
> This plan designs that wall and proves it on one real slice **before** minting a skill.

## Goal

A safe execution loop any agent runs when patching a slice: **git anchor before, gated
verify after, bounded fix loop, mandatory re-plan** — plus a declared-paths snapshot for
the state git can't see. Proven manually on one real pilot slice; the `/patch-slice`
skill is minted only from what the pilot teaches (ritual first, automation second —
same order `/new-spec` and the scenario harness followed).

## The ritual (the design under test)

```
1. PREFLIGHT   tree clean + gate green on HEAD. Never patch on red — a red baseline
               makes failures unattributable to the patch.
2. ANCHOR      record `git rev-parse HEAD` into the slice PLAN's ## Execution block;
               branch `slice/<domain>-<slug>`. The artifact carries its own escape
               hatch — a fresh session finds the rollback point by reading the doc.
3. STATE-SNAP  only if the domain SPEC declares `stateful paths:` (gitignored DBs,
               ledgers, generated state) — copy them to `.patch-snap/<sha>/`
               (gitignored). Most domains declare none and skip this step.
4. PATCH       the actual edits. Normal work; no auto-commit-per-edit noise.
5. VERIFY      two tiers:
               a) mechanical — the slice PLAN's Verification gate (the SPEC's walls)
               b) behavioral — drive the changed flow once for real; tests passing
                  ≠ feature working
6. FORK        green → checkpoint commit; outcome appended to the Execution block.
               red   → bounded fix loop (N attempts), then HARD ROLLBACK:
                       `git reset --hard <anchor>` + restore `.patch-snap/<sha>/`.
                       Rollback is a finding for re-plan, not a failure to hide.
7. RE-PLAN     update the slice PLAN status (✓ or the finding), CONTEXT.md Next Step,
               WALKTHROUGH if the slice ships, scenario → SPEC Behavioral Contract
               once a named test asserts it. The step that closes the loop.
```

Deliberate non-features: whole-project filesystem snapshots (git + junctions makes
them redundant and Windows-slow) · auto-merge to main (merge stays the human
checkpoint, like push in `/cut-release`) · worktree isolation by default (opt-in
later, only for projects with live serving state — see Open questions).

## Scenario

- given a clean tree and a green gate, when an agent starts a slice patch → the anchor
  SHA is written into the slice PLAN's Execution block and `slice/<domain>-<slug>`
  exists **before any edit lands**
- given a patch whose gate is still red after the fix-loop bound, when the bound hits →
  hard rollback (reset to anchor + state-snap restore) and the failure is recorded in
  the PLAN as a finding — never silent thrash past the bound
- given a domain SPEC declaring `stateful paths:`, when a patch begins → those paths are
  copied to `.patch-snap/<sha>/`, and after a rollback they are byte-identical to
  pre-patch
- given a green gate, when the slice checkpoints → PLAN status, CONTEXT.md Next Step,
  and (if shipping) a WALKTHROUGH are updated in the same session

## Slice

The smallest change that proves the ritual — **run it by hand, no skill yet**:

- **[NEW]** `docs/PLAN.patch-loop.md` — this file: the ritual spec + Execution block
  format (the 7 steps above are the deliverable, not commentary).
- **[NEW]** optional `stateful paths:` line documented in `templates/SPEC.template.md`
  (one line under Gate; absent = step 3 skipped).
- **[PILOT]** execute the ritual manually on **knowledge-viewer's hybrid-search slice**
  (add `hybrid.ts`, wire `/api/search` + chat tool + ⌘K — already planned, half-built,
  has a real gate). Record every step in an Execution block; append findings here.
- **[FIRE-DRILL]** during the pilot, deliberately trigger the rollback path once
  (break the gate, exhaust the bound, roll back) — an untested rollback is not a wall.

Minting `/patch-slice` + a `.claude/scenarios/` fixture for it = the **next** slice,
gated on pilot findings.

## Verification

1. Pilot branch history: checkpoint commit(s) whose parent chain starts at the recorded
   anchor SHA — expect the Execution block and `git log` to agree exactly.
2. Fire-drill: after forced rollback, `git status` clean at anchor SHA and stateful
   paths byte-identical to `.patch-snap/<sha>/` (`diff -r` empty).
3. A fresh session (or `/mission knowledge-viewer`) can reconstruct what happened —
   anchor, attempts, outcome — from the docs alone, no conversation memory.
4. `[review]` re-plan artifacts updated in the same session: PLAN status flipped,
   CONTEXT.md Next Step no longer stale.

## Decisions (resolved 2026-07-06, at adoption)

- **Fix-loop bound: N=3 attempts per slice.** Partial green does NOT reset the counter —
  thrash is thrash; three swings at the whole gate, then rollback.
- **Behavioral verify (5b): a fixture counts as the drive IF it exercises the real
  entry point** (the actual API route / CLI invocation / skill run), not just the
  changed function. Otherwise one real invocation with real input is required.
- **`.patch-snap/` retention: delete on green checkpoint** (the checkpoint commit is
  the new safety floor); gitignored per-project when first used, promoted to the
  template only if the pilot proves the pattern.
- **Worktree isolation: deferred** until a project with live serving state (astra)
  needs patch-while-serving. Branch-per-slice is the default.

## Open questions

- OPEN: where the ritual lives long-term — HANDBOOK workflow + `/patch-slice` skill,
  or also a template Execution block stencil inside `PLAN.template.md`? Decide from
  pilot findings.

## Execution (pilot log)

**2026-07-06 — PREFLIGHT (knowledge-viewer).** Two findings before a single edit:

- **F1 — the planned pilot target was stale.** Hybrid search (the slice this plan named)
  had already shipped (`server/src/search/hybrid.ts`, Phase 2.5 marked shipped in the
  spine); PROJECTS.md's row was 5 days behind the repo. *Lesson: preflight must re-read
  the target's PLAN/CONTEXT, never trust the workspace index — the index is a cache.*
- **F2 — the dirty tree was a finished, gate-green slice never committed**
  (config-load visibility, 9 files). Exactly the failure step 7 (re-plan) exists to
  prevent: verify ran, commit didn't. Remedy: ran the integration gate fresh
  (tsc ×2 + build + lint:docs — all green), landed it as `a8bd7f6`, kept it separate
  from anything the pilot will add. *Lesson: "dirty tree" usually means an unclosed
  previous loop, and the remedy is to close it, not stash it.*

Preflight now clean: HEAD `a8bd7f6`, tree clean, gate green.

**2026-07-06 — PILOT RUN (knowledge-viewer · agent-console/fallback-visibility).**
User picked **ADK fallback-visibility** as the replacement slice. Full ritual executed:

| step | what happened |
|---|---|
| 2 ANCHOR | slice PLAN written first (intent), anchor `a8bd7f6` recorded in its Execution block, branch `slice/agent-console-fallback-visibility` |
| 3 STATE-SNAP | skipped — agent-console SPEC declares no `stateful paths:` (the absent-line = skip rule worked; zero ceremony) |
| 4 PATCH | 6 files across 3 tiers (pydantic contract → SSE seam → TS unions → UI row) + the runtime's **first pytest suite** |
| 5 VERIFY | green on attempt **1/3** (pytest 3/3 + tsc ×2 + build + lint:docs); fail-on-tamper proven (lying stamp → red) |
| 6 FORK | checkpoint `de78731`; **fire-drill PASS** — deliberate type break → red gate → `git reset --hard de78731` → clean + green |
| 7 RE-PLAN | scenarios graduated to SPEC Behavioral Contract (`[test:…]`), slice PLAN closed, CHANGELOG + CONTEXT refreshed, first WALKTHROUGH written (`4fa3592`). Merge left to the user. |

**Findings (beyond F1/F2):**

- **F3 — the tamper drill destroyed the uncommitted patch.** Reverting a deliberate
  tamper with `git checkout <file>` restored the file to the *anchor*, wiping the whole
  uncommitted patch to it (recovered by re-applying). **Rule for the skill: checkpoint-commit
  BEFORE any tamper/fire drill; drills only ever run against committed state.** The fire-drill
  belongs after step 6's checkpoint, never during step 4–5.
- **F4 — piped gates lie about exit codes.** `tsc … | head` reported exit 0 from `head`
  while tsc was red. **Rule: the skill must run gate commands bare (or with `set -o pipefail`)
  and read the gate's own exit code, never a pipe tail's.**
- **F5 — the ritual's doc order held up.** Writing the slice PLAN *before* patching made
  the anchor/Execution block feel natural, not ceremonial — and the closed PLAN + walkthrough
  now reconstruct the whole run without conversation memory (verification #3 satisfied).

**Verification against this plan:** #1 ✓ (`a8bd7f6 → de78731 → 4fa3592`, Execution block
and `git log` agree) · #2 ✓ (fire-drill; stateful-restore untested — no stateful domain; test
on AMOS when its slice comes) · #3 ✓ (docs alone reconstruct the run) · #4 ✓ (PLAN flipped,
CONTEXT refreshed same session).

**2026-07-06 — PILOT RUN 2 (architecture-memory-os · export/drift-check) — the STATEFUL one.**
User picked Phase 12a (diagram drift check) — fittingly, a slice about drift detection.

| step | what happened |
|---|---|
| 1 PREFLIGHT | F2 again, bigger: two whole phases (8+10) gate-passed but uncommitted since 07-04; gate re-run → landed as `eb5705b`. Also caught **stale git claims** in CONTEXT (said `master`/no-remote; reality `main` + published remote) |
| 2 ANCHOR | slice PLAN `.gravity/PLAN.drift-check.md`, anchor `eb5705b`, branch `slice/export-drift-check` |
| 3 STATE-SNAP | **first live exercise**: `.amos/` (SQLite index.db + diagrams + proposals, 704K) → `.patch-snap/eb5705b/` — instant |
| 4 PATCH | `drift.ts` + CLI `drift` + 8 tests + `.patch-snap/` gitignored |
| 5 VERIFY | green attempt **1/3** (typecheck + 76/76); behavioral drive on the real corpus (clean → exit 0; hand-relabel → named cell, exit 1); fail-on-tamper: lying `clean: true` → 4 red |
| 6 FORK | checkpoint `767b2da`; **stateful fire-drill PASS**: type break + `index.db` corrupted to 8 bytes + diagrams deleted → `git reset --hard` + snap restore → tree clean, `diff -r` **byte-identical**, gate green, restored DB queries (13 nodes) |
| 7 RE-PLAN | PLAN closed, spine `Phase 12 · ◑`, CHANGELOG, CONTEXT (stale git claims fixed), walkthrough (`d9fce55`); snap **deleted on green** per the retention decision. Merge left to the user |

**New findings:**

- **F6 — projects without domain SPECs need a fallback home for `stateful paths:`.**
  AMOS has a flat `.gravity/` (no domain folders), so there was no SPEC to carry the
  declaration. Rule: declare in the slice PLAN's Execution block when no SPEC exists;
  migrate to the domain SPEC when domains get minted.
- **F7 — the four-proof rollback standard.** Tree clean + state byte-identical
  (`diff -r`) + gate green + **the restored state actually functions** (query the DB,
  don't just diff it). The fourth proof is the one a lazy check skips.
- **F8 — preflight is a drift detector for free.** Both pilots caught CONTEXT claims
  contradicted by the repo (F1 stale index, F2 unclosed loops, now stale git facts).
  The skill should diff CONTEXT's claims against `git status`/`git remote` as a
  standard preflight output, not a lucky side effect.

**Step 3 verdict: proven.** Both halves of the ritual have now run against reality —
the stateless path (knowledge-viewer) and the stateful path (AMOS). Every step 1–7 has
fired at least once; the fire-drill has restored both code-only and code+state damage.

**2026-07-06 — SCRIPT CORE BUILT: `.claude/scripts/patch_slice.py`** (the weaker-agent
walls, self-tested end-to-end on a fixture repo — both fork branches driven):

| subcommand | wall it enforces |
|---|---|
| `preflight --gate` | dirty tree → F2 remedy text; red baseline refused; **F8 CONTEXT-drift report** (caught all 3 planted stale claims) |
| `anchor --plan --slug` | branch + anchor SHA written into the PLAN by the script (can't be mistyped); refuses dirty tree / existing branch |
| `snap --spec/--plan/--paths` | **F6 resolution order**; manifest.json; auto-gitignores `.patch-snap/`; warns when a declared path is git-tracked (a smell); "no paths declared" = clean skip |
| `verify --gate --plan` | **F4: gate runs bare, real exit code**; attempt line appended by the script; **N=3 enforced — exit 75** with rollback instructions on exhaustion |
| `rollback --to --gate --probe` | **F7 four proofs** (incl. "restored state functions" via `--probe`, loud SKIPPED warning without one); **execution log survives the reset** (F3 applied inward — the tool re-writes the PLAN after `reset --hard`); refuses to print PASS if any proof fails; retires the snap on PASS |
| `cleanup` | snap deletion refused on a dirty tree (green-checkpoint retention rule) |

Design notes: stdlib-only, UTF-8 file I/O everywhere (cp949-safe), ASCII console markers;
`shell=True` for gate/probe is deliberate and documented (user-authored compound commands,
terminal-equivalent trust). Self-test proved fail branches too: failing probe → "rollback
NOT proven", snap kept; the PLAN accumulated the full forensic story (anchor → snap →
3 attempts → failed rollback → proven rollback) across two hard resets.

## Next

Wrap it: a thin **`/patch-slice`** SKILL.md that sequences the subcommands and owns the
two judgment steps the script can't (writing the patch, writing the re-plan), plus a
`.claude/scenarios/` fixture so `check.py` covers the script. Then flip this plan to ✓.
