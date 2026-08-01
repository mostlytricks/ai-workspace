<!--
  ROADMAP.template.md — the rolling plan sheet (the business layer above IMPLEMENTATION_PLAN.md).
  Copy to <project>/.gravity/_roadmap/ROADMAP.md — ONE living file per project, seeded by /urd
  on the first URD analysis. COMMITTED, unlike _observatory/ — this is authored analysis, not
  generated output. `_roadmap/` is sigiled machinery: never a domain, never wired into the indexes.

  RULES OF THE SHEET:
  - The unit here is the CHUNK — a URD-sized requirement, deliberately bigger than a slice.
    Chunks are NEVER pre-cut into slices; slicing happens just-in-time at the `active`
    transition. The work-layer law is untouched: this sheet is an index over future slices.
  - Every chunk CITES its URD item in `_given/` (`_given/<file> §n`) — the URD is the frozen
    agreement record, this sheet is derived analysis. Never restate a requirement; quote the
    citation. Lose this sheet → regenerate from evidence. Lose the URD → nothing can.
  - Status is one-way: proposed → agreed → active → shipped.
      proposed  = analyzed, not yet agreed with users/stakeholders
      agreed    = in the signed URD scope; waiting its turn
      active    = THE TRANSITION WITH TEETH — mint the IMPLEMENTATION_PLAN.md track/queue
                  rows now, link them in `→`, and slice just-in-time. Respect ≤3 active tracks.
      shipped   = all its slices landed; prune the row on the next update (git is the history).
  - ESTIMATES CARRY A BASIS TAG, same honesty move as SPEC enforcement tags:
      [measured] = from this project's own slice throughput (registry/CHANGELOG actuals)
      [drivers]  = sized from the evidence drivers below (domain count · crossings · OPENs)
      [guess]    = gut feeling — allowed, but never disguised as the other two
    MM = traditional man-month figure for the stakeholder conversation; agent-adj = expected
    duration with agent execution. Never tag [measured]/[drivers] without the evidence.
  - Size drivers are cheap, defensible integers: D = domains touched · X = boundary crossings
    (integration SPEC) · O = open unknowns. A 3D/2X chunk is objectively bigger than a 1D/0X one.
  - Prune shipped rows and stale analysis pointers on every update — a plan sheet nobody trims
    stops being read. `git log` recovers everything.
  - THE A&D GATE (the traditional Analysis & Design phase, made visible): a chunk never flips
    `active` while its O count > 0. The phase lives between `agreed` and `active` — it is the
    work that resolves each OPEN (frozen question, on the dated analysis sheet) into a dated
    row in Design decisions below (living answer, here). Deep technical design artifacts still
    land in the domains (ARCHITECTURE/SPEC) at activation; this ledger is the stakeholder-
    readable layer.
  Delete this comment when filled.
-->

# Roadmap — <project>

> Plan sheet: the URD-derived improvement plan. Chunks, not slices — see `.gravity/GRAVITY.md`.
> Last updated: <YYYY-MM-DD> · Analyses: `<YYYY-MM-DD>-<slug>.md`<!-- one pointer per routed URD analysis in this folder -->

## Chunks

| ID | Chunk (one line) | Benefit (one line) | URD | Domains | D/X/O | Est MM | Agent-adj | Status | → |
|---|---|---|---|---|---|---|---|---|---|
| R1 | <what gets built> | <what it buys the users/business> | `_given/<file> §n` | <domain, domain> | 2/1/0 | <n.n> `[drivers]` | <n wk> `[guess]` | proposed | — |
| R2 | <…> | <…> | `_given/<file> §n` | <domain> | 1/0/1 | <n.n> `[guess]` | — | agreed | — |

<!-- `→` stays "—" until `active`, then points at the IMPLEMENTATION_PLAN.md track/queue rows
     it minted (e.g. `track: <name>` + `PLAN.<slug>.md` once sliced). -->

**Legend** — `D/X/O` = size drivers: **D**omains touched · boundary **X**-ings (integration seams) · **O**pen unknowns.
Estimate basis tags: `[measured]` from this project's slice actuals · `[drivers]` sized from D/X/O · `[guess]` gut feeling, undisguised. Never blend tags into one total.
**Benefit** is the proposal's soul — what the chunk buys the users/business, in *their* words; elicit it in the URD meeting (a chunk whose benefit nobody can state is a chunk to question).

## Design decisions (the A&D ledger)

<!-- One row per resolved OPEN — the Analysis & Design phase, visible. The question stays
     frozen on its dated analysis sheet; the answer lands here with a date and an owner.
     A chunk's O count falls as rows land; `active` requires O = 0 (the A&D gate). -->

| Date | Chunk | Resolves | Decision | Agreed with |
|---|---|---|---|---|
| <YYYY-MM-DD> | R<n> | <U<n> OPEN: one line> | <what was decided + why, one line> | <who/meeting> |

## The `active` transition (checklist, per chunk)

- [ ] **O = 0** — every OPEN on this chunk resolved to a Design-decisions row (the A&D gate).
- [ ] Track row added to `IMPLEMENTATION_PLAN.md` (≤3 active tracks still holds — swap one out loud if needed).
- [ ] Queue rows added (slice queue rules hold: exactly one slice in `now`).
- [ ] First slice PLAN minted just-in-time in its owning domain — carry the URD citation into it.
- [ ] This row's `→` points at what it minted; status flipped to `active`.

## Notes

<!-- Optional per-chunk notes that don't fit a cell: wall collisions to renegotiate
     ("conflicts with <domain>/SPEC.md rule N — conversation, not task"), sequencing
     constraints between chunks, agreed descoping. Keep it short; the cited analysis
     sheet carries the full reasoning. -->
