---
description: Triage a batch of user bug/issue reports into the gravity docs — verify each report carries the minimum useful facts (eliciting or marking OPEN what's missing, never inventing), run the real?/domain?/kind? triage per item, dedupe to root causes, and route each into a slice PLAN + queue row. Bugs are not a domain; the intake sheet is the evidence log they route out of. Reach for this ONLY when the input is a batch of claims reported by users/QA — NOT for analyzing code or a domain (read the code + domain SPEC directly), not for brownfield archaeology (/excavate), not for a bug you found yourself mid-development (write the bug-intake slice PLAN directly; a batch of one needs no sheet).
argument-hint: <project-name>
---

You are running `/intake` from `ai-workspace/` to triage a batch of user-reported bugs/issues into project **`$ARGUMENTS`**'s gravity docs. This is the front half of the maintenance loop — `/patch-slice` is the back half. The honesty discipline is `/interview`'s pointed at *reports* instead of intent: **a report is evidence; never paraphrase a symptom, never invent a missing fact, never plan from an unreproduced report.** Bugs are not a domain — there is never a `.gravity/bugs/` folder; items route *out* of the intake sheet into slice PLANs in their owning domains.

## When NOT to reach for this (the trigger fence)

The test: **is the input a claim someone *else* reported, that must be verified before it's actionable?** If no, this command adds ceremony, not evidence:

- **"Analyze this code / this domain"** with no reports in hand → read the code; the router table + domain SPEC are the entry points, not a sheet.
- **Surveying an unfamiliar/legacy system** → `/excavate`.
- **A bug you found yourself while developing** → write the bug-intake slice PLAN directly in its owning domain and land it with `/patch-slice` — a batch of one needs no sheet.
- **A feature idea** (yours or a user's, arriving alone) → `/interview <project> <feature>`.

## Step 0 — Locate & collect

1. **Resolve the project** under `active/`, `stable/`, or `repos/`. Not found → list candidates and stop.
2. **Collect the raw reports** from whatever the user gives you (pasted text, files, a support-channel dump). If nothing was provided, ask for the batch — this command has no other input.
3. **Seed the sheet**: copy `templates/INTAKE.template.md` → `<project>/docs/intake/<YYYY-MM-DD>.md` (date from the system, never hardcoded; a second batch the same day gets `-b` suffixed). One item block per report, **reporter's words quoted verbatim** in *Observed*. If the reports carry private user data, put the sheet under a git-ignored path instead and note that in CONTEXT.md.

## Step 1 — The required-fields check (per item, before any triage)

A report is *useful* when it carries six facts: **Reporter·date · Observed · Expected · Repro · Env · Evidence**. For each item, mark each field **present** (fill it from the report) or **missing**. For missing fields:

- **Elicit strawman-first** if the user is in the room: draft your best guess *from what the report does say* and ask them to confirm or correct ("From the log line, I'd guess this ran on the v0.2.1 tag under a cp949 console — right?"). Label every guess as a guess.
- **Mark `OPEN: awaiting <exactly what>`** if only the original reporter can answer — and that item **stops here**: it stays in the sheet, untriaged, until the fact arrives. An OPEN repro especially: *no repro, no slice, no exceptions.*

**Hard rule: never fill a field plausibly.** A fabricated repro step or environment is this command's version of a fabricated wall — it sends `/patch-slice` chasing a bug that may not exist.

## Step 2 — Triage trio (per item that survived Step 1)

1. **Real?** Reproduce it now if the repro is runnable in this session (fixtures, synthetic input); otherwise mark how it will be verified and by whom. A report that reproduces differently than described gets its *Observed* corrected **with a note** — never silently.
2. **Whose domain?** Route with the project's router table (root `CLAUDE.md`, "what to read before a change") — the same navigation as any change. Spans domains → the `integration`/seam domain owns it. No `.gravity/` → the fix routes to the flat docs; the ritual still applies.
3. **What kind?**
   - **bug** — behavior the docs/SPEC already claim is violated → slice PLAN via the bug-intake rule (Step 3).
   - **feature** — the user wants something never promised → hand off to `/interview <project> <feature>` (the is-it-a-domain gate); record the handoff in the `→` line.
   - **doc-drift** — the system is right, the doc/expectation is wrong → fix the doc now, no slice; `→` points at the doc commit.

Assign severity (S1 data loss/corruption · S2 wrong output/blocked task · S3 cosmetic) — it decides queue order, nothing else.

## Step 3 — Dedupe & route

1. **Collapse to root causes**: N reports usually share fewer causes. Fill the sheet's *Root causes* table (cause · items · PLAN · lane). Dedupe against causes, not symptoms.
2. **One slice PLAN per accepted cause** (never per report): seed `.gravity/<domain>/PLAN.<slug>.md` from `PLAN.template.md` with the **bug-intake shape** — the repro enters the Scenario block as a *currently-false* `given/when/then`, and the Verification names the regression test the fix must leave (which later graduates the scenario into the domain SPEC's Behavioral Contract). Cite the item IDs (`I3, I7`) in the PLAN for two-way traceability.
3. **Queue, don't juggle**: add one row per slice to `IMPLEMENTATION_PLAN.md`'s slice queue — severity orders the lanes, and the queue's own rules hold: **exactly one slice in `now`**, `next` ≤3 ordered, the rest `later`. An S1 may swap `now`; say so out loud.
4. **Point every `→` line somewhere**: slice PLAN / rejected-with-reason / `OPEN: awaiting <what>`. Tick the *Batch close* checklist; a sheet with every row routed flips its Status to ✓ and freezes (append-only, like a walkthrough).
5. **Prove it mechanically**: `python .claude/scenarios/check.py intake --project <project>` — the wall that catches a missing fact, an unrouted row on a closed sheet, a dead PLAN route, or a `.gravity/bugs/` folder. Green before you report.

## Step 4 — Report & hand off

Print the routing table (item → verdict → destination), the root-cause collapse (N reports → M slices), what's OPEN and awaiting whom, and the queue's new shape. Then stop:

- **Do not fix anything here** — execution is `/patch-slice <project> <slug>`, one slice at a time, `now` first.
- **Do not commit** — the sheet + PLANs + queue rows in the working tree are the user's review checkpoint.

## What NOT to do

- **Never invent a repro, environment, or expected behavior** — elicit or mark `OPEN: awaiting …`.
- **Never route an unreproduced report to a slice PLAN** — it waits in the sheet.
- **Never create a `.gravity/bugs/` folder or a standing BUGS.md registry** — the dated sheet routes out and freezes; domains own their fixes.
- **Never make one PLAN per report** — dedupe to causes first, or 10 reports become 10 half-slices.
- **Never put more than one slice in `now`** — the queue's rule survives bug season too.
- **Never paraphrase a reporter** — *Observed* is verbatim; your interpretation lives in *Triage* and the PLAN.
