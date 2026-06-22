<!-- SPEC.template.md — the compact, AGENT-LOADABLE rule sheet for one domain (workspace CLAUDE.md §6, "audience split").
     Copy to repos/<project>/.gravity/<domain>/SPEC.md (or the flat SPEC.<domain>.md) and fill the <FILL> spots.
     This is the file you hand an agent directly before a change in <domain>. It is BOTH halves of a spec:
       - GENERATIVE: the Minimal Shape + Generate loop let an agent instantiate a correct unit FROM the spec.
       - LIMITING: every Rule names the wall that enforces it, so generation is bounded by checkable contracts.
     It is the OPPOSITE of an architecture doc — rules and shapes only, not rationale. The full human "why"
     lives in its paired ARCHITECTURE.<facet>.html; this file LINKS UP to it. Keep it SHORT; if it starts
     explaining "why", that prose belongs in the facet HTML.

     RATE-OF-CHANGE BOUNDARY (so this doesn't eat PLAN): SPEC holds what is true of EVERY valid unit, forever.
     The intent of THIS change lives in PLAN.*.md; the proof THIS change works lives in WALKTHROUGH.md.
     Test: "true of every valid unit?" → SPEC.  "true of this change?" → PLAN.

     Recognized only when present, never mandated. Delete this comment block once filled. knowledge-viewer is the worked example. -->

# SPEC.\<domain\>.md

Canonical human-readable reference: `ARCHITECTURE.<facet>.html`.

This is the compact agent-loadable contract for `<domain>` — enough to **build** a valid unit and the **walls** it can't cross. Keep it short. Full rationale belongs in the facet HTML above.

**Gate:** `<FILL: the one command that proves a change, e.g. `npm run test:<domain> && npm run lint:docs`>` — exits non-zero on a violation, so run it after touching anything this spec governs.

<!-- Enforcement legend — used in the Rules + Contract tags below. Keep it; it's what makes the contract honest.
     [lint]      a doc/static linter check fails on violation
     [type]      the type system / schema rejects it
     [test:name] a named automated test asserts it
     [review]    a human reviewer is the only check (no tooling — say so, don't pretend)
     [—]         guidance, not enforced at all -->

## Core Definition

<FILL: one or two sentences — what a valid unit in this domain *is* (a doc, a schema, an endpoint, a migration…). State the thing, not the history.>

## Minimal Shape

<!-- The smallest valid example an agent can copy to GENERATE a new unit. Code-fence it. Real, not abstract.
     This is the generative seed: step 1 of Generate below is literally "copy this". -->

```<FILL: lang>
<FILL: the minimal valid example>
```

## Generate (the loop)

<!-- The three-step loop that turns this spec into a correct change. Keep it to three lines. -->

1. Copy the **Minimal Shape**.
2. Satisfy every tagged **Rule** + the **Behavioral Contract**.
3. Run the **Gate** → green. (Then record the change + proof in `WALKTHROUGH.md`; intent stays in `PLAN.*.md`.)

## Rules

<!-- The enforceable contract, as a flat checklist. One rule per line, imperative, checkable.
     EACH rule starts with its enforcement tag (legend above) — the tag is the wall; an untagged rule is a lie.
     A [review]/[—] rule is honest about being unenforced by tooling; don't dress it as [lint]. -->

- `[FILL:tag]` `<FILL: rule — e.g. "field X is required and must be one of A | B | C">`
- `[FILL:tag]` `<FILL: rule>`
- `[FILL:tag]` `<FILL: rule>`
- `[FILL:tag]` `<FILL: rule>`

## Behavioral Contract

<!-- OPTIONAL — only for domains with behavior, not just shape (endpoints, parsers, retrieval, migrations).
     Each line is a given/when/then invariant of the domain (true forever, not just this change), bound to the
     test that proves it. Delete this whole section for shape-only domains (most docs/schemas). Don't pad. -->

- `[test:<name>]` given `<state>`, when `<action>` → `<observable outcome>`
- `[test:<name>]` given `<state>`, when `<action>` → `<observable outcome>`

## Gotchas

<!-- The few traps that bite agents specifically — collisions, silent-no-ops, ordering requirements.
     Delete if none; don't pad. -->

- `<FILL: the non-obvious trap, stated as the rule that avoids it>`

---

<!-- Pointer, not prose: anything that wants more than a line of explanation belongs in ARCHITECTURE.<facet>.html. -->
Full rationale and human review criteria live in `ARCHITECTURE.<facet>.html`.
