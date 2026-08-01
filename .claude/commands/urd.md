---
description: Analyze an agreed User Request Document (URD) against a project's domain system and turn it into the rolling plan sheet — route the URD through the given door as frozen evidence, classify each requirement with citations (domains touched, boundary crossings, wall collisions, new-domain candidates, OPENs), size chunks with basis-tagged estimates (traditional MM + agent-adjusted), and emit the question list for the next user meeting. The future-facing sibling of /intake: a bug is a currently-false scenario, a URD item is a desired-future one — same maturation boundary, opposite direction. Reach for this ONLY when the input is an agreed requirements document from system/application users — NOT for a lone feature idea (/interview), not for bug batches (/intake), not for surveying an unfamiliar system (/excavate).
argument-hint: <project-name>
---

You are running `/urd` from `ai-workspace/` to analyze a User Request Document into project **`$ARGUMENTS`**'s gravity docs. This is the third evidence door: `/intake` receives the past (bugs), `/given` receives knowledge, `/urd` receives the agreed future. The honesty discipline is `/excavate`'s pointed at *requirements*: **every classification is cited against the docs or marked `OPEN:` — never plausibly filled**, and the URD itself is an agreement record: **verbatim, frozen, never paraphrased into something easier to build.**

## The layer this feeds (don't blur it)

The plan sheet (`.gravity/_roadmap/ROADMAP.md`) is the **business layer** — URD-sized **chunks**, man-month figures, stakeholder language. It sits *above* `IMPLEMENTATION_PLAN.md` (the code arc) and is deliberately detached from it: the connection exists only through the one-way `active` transition, which mints track/queue rows just-in-time. **Chunks are never pre-cut into slices** — the work-layer law is untouched; the sheet is an index over *future* slices.

## When NOT to reach for this (the trigger fence)

The test: **is the input an agreed, multi-item requirements document from users/stakeholders?** If no:

- **One feature idea**, yours or a user's → `/interview <project> <feature>` (a batch of one needs no sheet).
- **A batch of bug reports** → `/intake` — bugs enter the past-facing door.
- **"What should we build?" with no document** → hold the meeting first; this command analyzes agreements, it doesn't invent them.
- **An unfamiliar/legacy system with no domain map yet** → `/excavate` first — this command's whole value is throwing the URD against an *analyzed* domain system.

## Step 0 — Locate & route the evidence

1. **Resolve the project** under `active/`, `stable/`, or `repos/`. Not found → list candidates and stop.
2. **Get the URD**: a file in `.gravity/_inbox/`, a paste, or a path the user gives. If nothing was provided, ask — this command has no other input.
3. **Route it through the given door**: the URD lands in `.gravity/_given/` (root — it's cross-cutting) with a `MANIFEST.md` provenance row (source meeting, date agreed, who agreed), per `/given`'s rules. The URD is now the frozen agreement record; everything below cites into it. Private stakeholder data → git-ignored path, noted in CONTEXT.md, same rule as private briefs.
4. **Seed the analysis sheet**: copy `gravity/templates/URD-ANALYSIS.template.md` → `.gravity/_roadmap/<YYYY-MM-DD>-<slug>.md` (date from the system; slug from the URD's subject). First `/urd` on a project also seeds `.gravity/_roadmap/ROADMAP.md` from `ROADMAP.template.md`. `_roadmap/` is sigiled machinery — committed (it's authored analysis, unlike `_observatory/`), never a domain, never wired into the indexes.

## Step 1 — Read the domain system first

Before classifying anything, load the map: `.gravity/ROUTER.md` (Doc Map + router table), `MISSION.html` domain rows, `integration/SPEC.md` if present (the Boundary Map is the crossing detector), and skim each domain `SPEC.md`'s Rules. No `.gravity/` on this project → stop and say so: adopt first (`/adopt-gravity`, or `/excavate` for brownfield). An unanalyzed system can't receive a cited analysis.

## Step 2 — Classify per requirement (cited or OPEN)

One item block per URD requirement, **requirement quoted verbatim** with its `_given/<file> §n` citation. Then classify, each field cited:

1. **Kind** — new capability · change to existing · boundary change · non-functional.
2. **Domains touched** — name each SPEC. Unmappable → `OPEN: unmapped`, never a guessed folder.
3. **Crossings** — seams the requirement crosses, per the Boundary Map. No integration SPEC but an obvious crossing → note it as a finding (the project may have just earned one).
4. **Wall collisions** — an existing SPEC rule the requirement would violate. **A collision is a conversation, not a task**: it goes on the question list; it never silently enters the roadmap as work.
5. **New-domain candidate?** — run the is-it-a-domain gate from ROUTER.md, record the verdict. **Do not mint** — `/new-domain` runs at the `active` transition, not during analysis.
6. **Drivers** — count D (domains) / X (crossings) / O (OPENs). Cheap, defensible integers.
7. **Estimate** — traditional **MM** for the stakeholder conversation + **agent-adjusted** expected duration, each with a **basis tag**: `[measured]` (this project's slice throughput actuals) · `[drivers]` (sized from D/X/O) · `[guess]`. **Never tag a basis you don't have** — under-claim to `[guess]`, the same honesty rule as SPEC enforcement tags.

## Step 3 — Route to the plan sheet

1. **One ROADMAP chunk per accepted requirement** (dedupe first — N requirements sometimes share one chunk). Status `proposed`, or `agreed` when the URD itself is the signed agreement. Every row cites its URD item.
2. **Point every `→` line somewhere**: ROADMAP `R<n>` / rejected-with-reason / `OPEN: awaiting <what>`. A sheet with every row routed flips Status to ✓ and freezes (append-only, like intake).
3. **Roll up the Questions section** — every OPEN and every wall collision, phrased as askable questions. **This is a deliverable**: it's the prep sheet for the next user meeting, generated by the analysis instead of after it.
4. **Touch nothing in IMPLEMENTATION_PLAN.md.** The `active` transition is a separate, later act (its checklist lives in ROADMAP.md): when the user says a chunk goes active — mint the track row (≤3 active), the queue rows, the first slice PLAN just-in-time, and the backlink. Not today, not by default.

## Step 4 — Report & hand off

Print: the routing table (item → kind → domains → chunk), total sized scope (ΣMM by basis tag — never sum `[guess]` and `[drivers]` into one unlabeled number), the question list, and what the roadmap now holds. Then stop:

- **Do not slice, do not mint domains, do not edit IMPLEMENTATION_PLAN.md** — the `active` transition is the user's call, per chunk.
- **Do not commit** — the routed URD + sheets in the working tree are the user's review checkpoint.

## What NOT to do

- **Never paraphrase a requirement** — verbatim + citation; your interpretation lives in the classification fields.
- **Never classify without a citation** — an uncited domain mapping is a guess; write `OPEN:`.
- **Never pre-cut chunks into slices** — slicing is just-in-time at `active`; the sheet indexes future work, it doesn't hold it.
- **Never let a wall collision slide into the roadmap as a task** — it's a question until the users renegotiate the wall or drop the ask.
- **Never emit an untagged estimate** — every number names its basis, and totals stay segregated by tag.
- **Never mint `_roadmap/` as a domain or wire it into the indexes** — it's machinery, same standing as `_given/`.
