<!--
  PLAN.template.md — the per-domain / per-slice "what/next" doc (workspace CLAUDE.md §6).
  Copy to repos/<project>/.gravity/<domain>/PLAN.md — or PLAN.<slug>.md when the domain
  already has a PLAN and this is another slice. Seeded by /new-domain and /interview
  <project> <feature>; recognized only when present, never mandated.

  RATE-OF-CHANGE BOUNDARY: this file holds ONE slice's intent. The roadmap spine
  (which slice is now/next) lives in IMPLEMENTATION_PLAN.md; *now* lives in CONTEXT.md;
  the proof a shipped slice works lives in its WALKTHROUGH.md; what's true of every
  valid unit forever lives in SPEC.md. Link across, don't restate.

  Delete sections that don't apply — don't pad. Delete this comment when filled.
-->

# <domain> — PLAN<.slug>

Status: ○ planned <!-- ○ planned · ◑ building · ✓ shipped — mirror into the IMPLEMENTATION_PLAN.md spine/queue -->

## Goal

<FILL: what this slice delivers and why, 2–3 lines — the end state a reviewer can check against.>

## Scenario

<!-- The use scenario(s) that earn this slice its existence, as given/when/then — who is doing
     what differently when it works. These are SEEDS for the domain SPEC's Behavioral Contract:
     once a named test asserts one, /new-spec graduates it to a tagged `[test:name]` line.
     Until then they are intent, not contract — no enforcement tags here.
     BUG INTAKE: a bug enters here as a CURRENTLY-FALSE scenario — the repro, stated as the
     behavior the system doesn't yet exhibit. Its fix must leave the named regression test
     that graduates it; a bug you can't state this way isn't understood enough to patch. -->

- given <FILL: state>, when <FILL: action> → <FILL: observable outcome>
- given <FILL: state>, when <FILL: action> → <FILL: observable outcome>

## Slice

<!-- The smallest change that proves the Goal — concrete enough to execute.
     Tag [NEW]/[MODIFY]/[DELETE] like the IMPLEMENTATION_PLAN phase spec, but lighter. -->

- **[NEW]** `<FILL: path>` — <FILL: what it adds.>
- **[MODIFY]** `<FILL: path>` — <FILL: the change.>

## Verification

<!-- The runnable/observable check for THIS slice — numbered, reproducible.
     "I'll eyeball it" is honest: write `[review]` and say what to look at. -->

1. <FILL: run command / open surface> — expect <FILL: observable result>.

## Open questions

<!-- Unresolved items blocking or shaping this slice. Write them as `OPEN:` so /interview,
     /mission, and the next agent see them. Delete the section if none. -->

- OPEN: <FILL: the question, with enough context to act on it.>

## Next

<FILL: the one concrete next step for this slice.>
