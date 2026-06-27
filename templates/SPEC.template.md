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

     INTEGRATION VARIANT (one template, two shapes): when <domain> is `integration`, this same sheet describes
     the contracts BETWEEN services/domains instead of a unit WITHIN one. There is nothing to "generate", so the
     integration form SWAPS two sections — Minimal Shape → Boundary Map, Generate → Change Order — and keeps the
     rest. The swap is a self-contained block below ("INTEGRATION VARIANT"); use it for integration, delete it
     otherwise. See workspace CLAUDE.md §5 for what an integration SPEC owns.

     Recognized only when present, never mandated. Delete this comment block once filled. knowledge-viewer is the worked example. -->

# SPEC.\<domain\>.md

Canonical human-readable reference: `ARCHITECTURE.<facet>.html`.

This is the compact agent-loadable contract for `<domain>` — enough to **build** a valid unit and the **walls** it can't cross. Keep it short. Full rationale belongs in the facet HTML above.

> **Integration domain?** This same template flexes into a **boundary contract**: it owns only the seams *between* services/domains — the wire envelope, generated client types, auth/session flow, ports/base URLs, the database-access boundary, and the **change order** — while each service's internals stay in its own domain SPEC. Use the **INTEGRATION VARIANT** block below (swap Minimal Shape → Boundary Map, Generate → Change Order); delete it for a normal domain. Load this SPEC *first* before any cross-boundary edit, then the affected domain SPECs.

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
     This is the generative seed: step 1 of Generate below is literally "copy this".
     INTEGRATION domain? Delete this section — use the **Boundary Map** in the INTEGRATION VARIANT block below instead. -->

```<FILL: lang>
<FILL: the minimal valid example>
```

## Generate (the loop)

<!-- The three-step loop that turns this spec into a correct change. Keep it to three lines.
     INTEGRATION domain? Delete this section — use **Change Order** in the INTEGRATION VARIANT block below instead. -->

1. Copy the **Minimal Shape**.
2. Satisfy every tagged **Rule** + the **Behavioral Contract**.
3. Run the **Gate** → green. (Then record the change + proof in `WALKTHROUGH.md`; intent stays in `PLAN.*.md`.)

<!-- ============================================================================
     INTEGRATION VARIANT — use ONLY when <domain> is `integration`; delete this
     whole block (the two sections below) for any normal domain. It SWAPS the two
     sections above: Minimal Shape → Boundary Map, Generate → Change Order. Keep
     Rules / Behavioral Contract / Gotchas — seed them with the cross-boundary
     walls listed at the end of this block.
     ============================================================================ -->

## Boundary Map

<!-- Every seam this SPEC governs — each place one part talks to another. One row per seam.
     This replaces Minimal Shape: there is no unit to generate, only boundaries to honor. -->

| From → To | What crosses | Transport / where |
|---|---|---|
| `<FILL: web>` → `<FILL: api>` | `<FILL: typed JSON envelope via the generated client>` | `<FILL: HTTP · base URL · port>` |
| `<FILL: api>` → `<FILL: data>` | `<FILL: queries + migrations only>` | `<FILL: DB driver — never reached from web>` |

**Ports / base URLs (local):**

| Service | Dev URL | Notes |
|---|---|---|
| `<FILL: web>` | `<FILL: http://localhost:PORT>` | `<FILL: proxies /api → api>` |
| `<FILL: api>` | `<FILL: http://localhost:PORT>` | `<FILL>` |

## Change Order

<!-- The STRICT sequence for a cross-boundary change (esp. a data-mutation loop).
     Out-of-order edits are the exact bug this SPEC exists to prevent. Bind the last step to the Gate. -->

1. `<FILL: change the backend entity / DTO / schema first>`
2. `<FILL: run the schema or type export, if one exists>`
3. `<FILL: regenerate / update the client types + frontend models>`
4. Run the **Gate** → green; the contract holds. (Proof → `WALKTHROUGH.md`; intent → `PLAN.*.md`.)

<!-- Lift these into the **Rules** section below and tag each HONESTLY (a generated-types check is [test]
     or [type] only if it really runs; otherwise [review]). These are the typical integration walls: -->
<!--
- `[FILL:tag]` the wire envelope is `<FILL: shape, e.g. { data, error }>` — clients depend on it; never change shape without bumping the contract.
- `[FILL:tag]` client types are regenerated from `<FILL: source of truth>` — never hand-edited; drift fails `<FILL: check>`.
- `[FILL:tag]` every mutating call carries `<FILL: auth/session credential>`; missing → `<FILL: 401>`.
- `[review]` `<FILL: web>` never reaches `<FILL: the database>` directly — only through `<FILL: api>`.
- `[—]` the **Change Order** above is mandatory for any data-mutation change.
-->
<!-- ===================== END INTEGRATION VARIANT ===================== -->

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
