---
description: Maintain a project's engagement book — ONE calm, stakeholder-friendly HTML file holding the whole outward conversation as tabs: a Proposal tab (scope · benefits · estimates · sign-off block, frozen at sign-off) plus one report tab per cycle (SRS × clearance fused), all rendered from the plan sheet (.gravity/_roadmap/ROADMAP.md), URD analysis sheets, and walkthroughs. Evidence-bound: every requirement keeps its agreed wording, and a "verified" clearance badge requires a named proof (dated walkthrough, green gate run, witnessed demo) — no proof, dashed badge. Delivered tabs are immutable; each cycle appends a tab, and a later URD appends its own Proposal tab. Reach for this ONLY for the outward artifact handed to users/supervisors — NOT for internal status (/observatory, /triage, /mission own that) and not for the analysis itself (/urd).
argument-hint: <project-name>
---

You are running `/report` from `ai-workspace/` to add a reporting cycle to project **`$ARGUMENTS`**'s engagement report book — the outward-facing half of the plan-sheet layer. One rule above all: **the report is a projection, never a source.** Every fact on it must exist in the plan sheet, an analysis sheet, the decisions ledger, or a walkthrough — if you find yourself writing a new fact, stop and put it in its owner-doc first.

## The book model

One engagement = **one HTML file**: `.gravity/_roadmap/report-<slug>.html`, seeded from `REPORT.template.html` on the first run with **two tabs — the Proposal** (background · scope & benefits with MM totals · sequencing · estimation-honesty note · risks & asks · sign-off block) **and Report #1**. Each later `/report` run **appends a report tab** (a button in the tab bar + a `<section class="tab">`), newest active; **a later URD on the same project appends its own Proposal tab**, then its cycles. **Delivered tabs are immutable** — corrections and progress belong to the next tab; git history holds each delivery's exact snapshot. The page is deliberately **NOT the gravity doc theme**: stakeholders get a calm, light, single-accent, print-friendly page (printing lays all tabs out in sequence — proposal first) with zero external resources.

## When NOT to reach for this (the trigger fence)

- **"How is the project doing?" for yourself/the agent** → `/observatory`, `/mission`, `/triage` — the internal instruments, always fresher.
- **A URD just arrived** → `/urd` first; a book with nothing analyzed reports nothing.
- **No `.gravity/_roadmap/ROADMAP.md`** → there is no engagement to report on; stop and say so.

## Step 0 — Locate & number

1. **Resolve the project** under `active/`, `stable/`, or `repos/`. No plan sheet → stop (fence above).
2. **Find the book** (`_roadmap/report-<slug>.html`). Exists → this run appends report tab **#N+1**, and "this period" means *since the previous tab's date* (a new URD instead appends a Proposal tab first). Doesn't exist → seed it from `gravity/templates/REPORT.template.html` and fill **both** the Proposal tab (from the sheet: benefits, estimates with the honesty note, sequencing, risks) and Report #1; the period starts at the engagement's first analysis sheet.

## Step 1 — Gather (read, never invent)

- **`ROADMAP.md`** — chunk statuses, benefits, sequencing, the Design-decisions ledger (+ which rows are provisional and who confirms).
- **The engagement's analysis sheet(s)** — each requirement's agreed wording (verbatim) and its acceptance basis.
- **`IMPLEMENTATION_PLAN.md` + `docs/walkthroughs/` since the previous tab** — what actually landed, with dates: the *only* legitimate source for "this period" and for clearance proofs.
- **Gate freshness if available** (`.gravity/_observatory/gates.json` via `run_gate.py --all`) — a green, recent gate is citable proof; a stale one is not.

## Step 2 — Fill the new tab (the two honesty walls)

1. **Requirements & clearance table** — one row per U-id, agreed wording preserved, "Done means:" in user terms beneath it. Status words are plain (`waiting · designing · building · delivered · deferred`), mapped from chunk status + slice progress. **The clearance badge is evidence-bound**: `✓ verified` *only* with a named proof in its `title` (walkthrough date, gate run, witnessed demo) · the dashed `○ not yet verified` otherwise, which no wording may dress up · `✕ failing` when something is verified failing or blocked. Delivered-but-unverified is `○`, said plainly — that combination is the report's most valuable line, never its most embarrassing. Glyph + colour always, never colour alone.
2. **Stakeholder language everywhere** — no chunks/slices/SPECs/O-counts/gravity jargon; requirements keep U-ids, work packages keep R-ids, the method appears only as its effects. The tab re-renders the standing SRS half (roles, decisions with `✓ confirmed`/`◇ provisional` badges) from the sources, so the latest tab is always the current definition. Risks & asks: only live ones, each naming its owner.

## Step 3 — Wire & deliver

1. **Tab mechanics**: append the button (`data-tab` paired to the new section id), move `active` from the previous button/section to the new ones. Touch nothing inside older tabs.
2. **Index it**: make sure `ROADMAP.md`'s Deliverables line names the book (once — it's one file).
3. **Language siblings**: if the Deliverables line names a translated copy (`report-<slug>.<lang>.html`, e.g. `.ko` — the OVERVIEW.ko precedent), mirror the new tab into it in that language, same immutability rules; the line says which copy is customer-facing.
4. **Open it** in the browser for the user (`start <path>` on Windows) so they see what ships.
5. **Do not commit** — the working tree is the user's review checkpoint.

## What NOT to do

- **Never originate a fact here** — a number, status, or decision with no source doc is drift being born; write it into its owner first, then render.
- **Never mark verified without a named proof** — the dashed badge is the honest default, and "we're pretty sure" is not a proof.
- **Never edit a delivered tab** — append the next one; git holds the snapshots.
- **Never let jargon leak** — if a stakeholder would ask "what's a slice?", rewrite the line.
- **Never apply the gravity doc theme here** — the book carries its own calm stylesheet by design (`apply_doc_theme` skips it); don't add the switcher, the dark palettes, or external resources.
