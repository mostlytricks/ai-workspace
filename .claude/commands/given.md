---
description: Route the drop zone into the given layer — take files the user dropped in .gravity/inbox/ (domain knowledge, data dictionaries, business rules, vendor docs), propose a routing table (domain, rendering, privacy), render readable copies with fidelity marks, write provenance manifest rows, and mv everything so the inbox ends empty. Reach for this ONLY when the user hands in outside material to register ("route my inbox", "I uploaded the docs") — NOT for bug/issue reports (/intake), not for authoring project docs (SPEC/PLAN/MISSION are decided, not given), not for code exploration.
argument-hint: <project-name>
---

You are running `/given` from `ai-workspace/` to route project **`$ARGUMENTS`**'s drop zone (`.gravity/inbox/`) into its **given layer** — the home for *received* truth: what the project was **told** (domain knowledge, production data dictionaries, business rules, vendor docs), as opposed to what it decided (SPEC/MISSION/PLAN). The honesty discipline: **provenance is evidence — never invent who gave a thing, when, or what version it describes;** a missing fact is `OPEN: awaiting <what>` in the manifest, elicited strawman-first when the user is in the room.

## When NOT to reach for this (the trigger fence)

The test: **is the input outside material the project should keep and cite?** If no:

- **Bug/issue reports** → `/intake` (claims to verify, not knowledge to keep).
- **Authoring project docs** — SPEC rules, PLAN slices, MISSION principles are *decided* truth; they cite given docs, they don't live there.
- **"Analyze this code/domain"** → read the code; the router table is the entry point.
- **A brief for a deck/feature in the user's head** → `/interview`.

## Step 0 — Locate & scan

1. **Resolve the project**; not found → list candidates and stop.
2. **Scan `.gravity/inbox/`.** Empty → say so and stop (nothing to route). Missing → create it and ensure the project's `.gitignore` covers `.gravity/inbox/` (the drop zone is *never* tracked: nothing the user drops may reach a commit before triage decides its privacy class).

## Step 1 — Propose the routing table (one batch, confirm before touching disk)

For each file: read enough to know its subject, then propose one row:

| Inbox file | Domain | Render? | Fidelity | Privacy | Provenance gaps |
|---|---|---|---|---|---|

- **Domain** — route by the router table, same navigation as any change; genuinely cross-cutting ("what is the earth"-level context) → `.gravity/given/`; domain-scoped → `.gravity/<domain>/given/`.
- **Render?** — binaries and walls-of-text get a readable `<slug>.md` rendering; clean markdown routes as-is (`verbatim`).
- **Fidelity** — `verbatim` · `reformatted` (structure only, diffable back) · `distilled` (judgment applied — say what was dropped).
- **Privacy** — `committable`, or `private` (raw stays git-ignored; the manifest row is the committed pointer). Default to `private` when unsure — un-ignoring later is trivial, unleaking is not.
- **Provenance gaps** — source/date/version the file doesn't state: elicit strawman-first ("this reads like the ERP v11 export Kim mentioned — right?") or mark `OPEN: awaiting <what>`.

**Confirm the whole table with the user, then execute.** Never route silently.

## Step 2 — Execute

Per confirmed row: move the original to `given/raw/` (or leave a `private` pointer row if it must stay local-only), write the rendering beside the manifest, add **both** manifest rows (copy `GIVEN-MANIFEST.template.md` on first use), extend `.gitignore` for private paths. The inbox **ends empty** — that is the postcondition, not a nicety.

## Step 3 — Prove & report

1. `python .claude/scenarios/check.py given --project <project>` — green: inbox empty, every file manifested, no ghost rows.
2. Report the routing table as executed, plus any `OPEN:` provenance still awaiting the user.

## The consumption rules (what routing buys)

- *"As the docs I gave you, prepare plans"* → read the manifests, load the cited files, and **every claim in the resulting PLAN/SPEC cites its given source** (`source: given/<file> §n`) — that citation is what makes the plan auditable.
- **Quarry, not contract:** a given doc never becomes a shadow SPEC; repeatedly-used facts graduate into owner-docs with back-citations.
- **Raw wins:** disputes resolve against `raw/`, never against a rendering.

## What NOT to do

- **Never invent provenance** — source, date, and version are facts only the giver knows.
- **Never commit inbox contents or private raws** — privacy is decided at routing, enforced by `.gitignore`.
- **Never distill silently** — `distilled` rows state what was dropped; when in doubt, `reformatted` + keep the raw.
- **Never leave residue in the inbox** — an unroutable file gets an explicit `OPEN:` row in the nearest manifest and stays *tracked as pending there*, not forgotten in the drop zone.
- **Never restate a given doc inside SPEC/MISSION** — cite it (one concern, one home).
