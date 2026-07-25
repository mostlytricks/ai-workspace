<!--
  INTAKE.template.md — the per-batch bug/issue intake sheet (workspace CLAUDE.md §6).
  Copy to repos/<project>/docs/intake/<YYYY-MM-DD>.md — one file per batch, dated like
  walkthroughs (intake = the frozen BEFORE-record; a walkthrough = the frozen AFTER-record).
  Seeded and filled by /intake; the manual shape is below.

  RULES OF THE SHEET:
  - Items are EVIDENCE, not plans — quote reporters verbatim, never paraphrase a symptom.
  - Never invent a missing field. A field the reporter didn't give is `OPEN: awaiting <what>`.
  - Bugs are not a domain: no .gravity/bugs/ folder ever. Each accepted item routes OUT of
    this file into a slice PLAN in its owning domain (bug-intake rule, CLAUDE.md §6).
  - The file is DONE when every item's `→` line points somewhere: a slice PLAN, a rejection
    with a reason, or an OPEN naming exactly what's awaited. Then it freezes — append-only.
  - Private user data (names, logs, files) → keep the batch under a git-ignored path and
    say so in CONTEXT.md, same rule as private briefs.
  Delete this comment when filled.
-->

# INTAKE — <project> — <YYYY-MM-DD>

Batch: <N> items from <source: support channel / user emails / QA pass>.
Status: ○ triaging <!-- ○ triaging · ✓ closed (every item routed) -->

## Items

<!-- One block per report, verbatim first. The six REQUIRED fields are the minimum for a
     useful report — /intake refuses to route an item that lacks them (it elicits or marks
     OPEN instead). Severity: S1 data loss/corruption · S2 wrong output/blocked task ·
     S3 cosmetic/ergonomic. -->

### I1 — <one-line title, reporter's words>
- **Reporter · date:** <who · when>
- **Observed (verbatim):** "<what the user actually wrote/said>"
- **Expected:** <what should have happened — cite the claimed behavior/contract if one exists>
- **Repro:** <numbered steps + input that reproduce it> | `OPEN: awaiting <input/file/steps>`
- **Env:** <version/tag · OS · locale/encoding · data shape>
- **Evidence:** <error text, log line, screenshot/file pointer — privacy-safe>
- **Triage:** real: <yes|no|OPEN> · kind: <bug|feature|doc-drift> · domain: <slug> · severity: <S1|S2|S3>
- **→** <`.gravity/<domain>/PLAN.<slug>.md`> | rejected: <why> | `OPEN: awaiting <what>`

### I2 — <…>
<!-- … -->

## Root causes (dedupe)

<!-- N reports usually collapse to fewer causes. One row per accepted cause; the PLAN
     carries the currently-false scenario, this table only maps reports → causes. -->

| Cause | Items | Slice PLAN | Queue lane |
|---|---|---|---|
| <one line> | I1, I4 | `.gravity/<domain>/PLAN.<slug>.md` | now/next/later |

## Batch close

- [ ] Every item's `→` line points somewhere (PLAN / rejected / OPEN-awaiting).
- [ ] Dupes collapsed into the Root causes table.
- [ ] Queue rows added to `IMPLEMENTATION_PLAN.md` (still exactly one slice in `now`).
- [ ] CONTEXT.md gets one line: batch triaged, N routed / M open.
