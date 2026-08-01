<!--
  URD-ANALYSIS.template.md — one dated, cited analysis of one URD batch against the domain
  system. Copy to <project>/.gravity/_roadmap/<YYYY-MM-DD>-<slug>.md — one file per URD,
  dated like intake sheets (the URD itself is EVIDENCE and lives in `_given/` with a
  MANIFEST row; this sheet is the derived analysis that routes it). Seeded and filled by
  /urd; the manual shape is below.

  RULES OF THE SHEET:
  - The URD is the agreement record — verbatim, frozen, in `_given/`. This sheet QUOTES and
    CITES it (`_given/<file> §n`); it never paraphrases a requirement into something easier
    to build. Disputes resolve against the URD, not this sheet.
  - Every classification is CITED against the docs: domains name their SPEC, crossings name
    `integration/SPEC.md`, wall collisions name the rule. An uncited classification is a
    guess — mark it `OPEN:` instead. Same law as /excavate: never plausibly filled.
  - A wall collision (the requirement violates an existing SPEC rule) is a CONVERSATION,
    not a task — it goes on the question list, never silently into the roadmap.
  - New-domain candidates get the gate verdict recorded here, but /new-domain still mints —
    and only at the `active` transition, never during analysis.
  - The sheet is DONE when every item's `→` line points somewhere: a ROADMAP chunk, a
    rejection with a reason, or an `OPEN: awaiting <what>`. Then it FREEZES — append-only,
    like an intake sheet. The rolling state lives in `ROADMAP.md`.
  - The Questions section is the deliverable for the next user meeting — OPENs and wall
    collisions roll up here so the analysis pays for itself in meeting prep.
  Delete this comment when filled.
-->

# URD Analysis — <project> — <YYYY-MM-DD>

URD: `_given/<file>` (<source: which meeting/users · date agreed>) · Manifest row: ✓
Status: ○ analyzing <!-- ○ analyzing · ✓ routed (every item's → points somewhere; frozen) -->

## Items

<!-- One block per URD requirement. Quote verbatim first; classification is cited or OPEN. -->

### U1 — <one-line title>
- **Requirement (verbatim):** "<what the URD actually says>" — `_given/<file> §n`
- **Kind:** <new capability | change to existing | boundary change | non-functional>
- **Domains:** <domain> (`.gravity/<domain>/SPEC.md`), <domain> (`…`) | `OPEN: unmapped — <why>`
- **Crossings:** <seam, per `integration/SPEC.md` §…> | none
- **Wall collisions:** <`<domain>/SPEC.md` rule N — needs renegotiation> | none
- **New domain?:** <no | candidate `<slug>` — gate: <verdict + one line>>
- **Drivers:** D<n> / X<n> / O<n>
- **Estimate:** <n.n> MM `[drivers|measured|guess]` · agent-adj <n wk> `[…]`
- **→** ROADMAP `R<n>` | rejected: <why> | `OPEN: awaiting <what>`

### U2 — <…>
<!-- … -->

## Questions for the next meeting

<!-- The roll-up: every OPEN and every wall collision, phrased as an askable question.
     This list is why the analysis happens before the meeting, not after. -->

- <U1> OPEN: <exactly what only the users can answer>
- <U3> collision: <requirement> vs <`<domain>/SPEC.md` rule N> — <the trade-off to put to them>

## Sheet close

- [ ] Every item's `→` line points somewhere (chunk / rejected / OPEN-awaiting).
- [ ] ROADMAP.md rows added/updated; its Analyses pointer includes this sheet.
- [ ] Questions list handed over (or scheduled) — OPENs have an owner.
- [ ] CONTEXT.md gets one line: URD analyzed, N chunks routed / M open.
