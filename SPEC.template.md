<!-- SPEC.template.md — the compact, AGENT-LOADABLE rule sheet for one domain (workspace CLAUDE.md §6, "audience split").
     Copy to repos/<project>/SPEC.<domain>.md (e.g. SPEC.doc.md, SPEC.schema.md, SPEC.search.md) and fill the <FILL> spots.
     This is the file you hand an agent directly before a change in <domain>. It is the OPPOSITE of an architecture doc:
       - It carries only the enforceable RULES and shapes an agent needs in context — not the rationale.
       - The full human-readable rationale lives in its paired ARCHITECTURE.<facet>.html; this file LINKS UP to it.
       - Keep it SHORT. If it starts explaining "why", that prose belongs in the facet HTML, not here.
     Recognized only when present, never mandated. Delete this comment block once filled. knowledge-viewer is the worked example. -->

# SPEC.\<domain\>.md

Canonical human-readable reference: `ARCHITECTURE.<facet>.html`.

This is the compact agent-loadable requirement sheet for `<domain>`. Keep it short. Do not let it grow into a second architecture document — full rationale belongs in the facet HTML above.

Enforced where possible by `<lint command, e.g. npm run lint:docs>` (`<linter file>`): `<one line naming the checks the linter actually runs — valid enums, required fields, dead references, etc.>`. Exits non-zero on errors, so run it after touching anything this spec governs.

## Core Definition

<FILL: one or two sentences — what a valid unit in this domain *is* (a doc, a schema, an endpoint, a migration…). State the thing, not the history.>

It must have:

- `<FILL: required property>`
- `<FILL: required property>`
- `<FILL: required property>`

## Minimal Shape

<!-- The smallest valid example an agent can copy. Code-fence it. Real, not abstract. -->

```<FILL: lang>
<FILL: the minimal valid example>
```

## Rules

<!-- The enforceable contract, as a flat checklist. One rule per line, imperative, checkable.
     Group under sub-headings only if the domain has genuinely distinct rule sets. -->

- `<FILL: rule — e.g. "field X is required and must be one of A | B | C">`
- `<FILL: rule>`
- `<FILL: rule>`
- `<FILL: rule>`

## Gotchas

<!-- The few traps that bite agents specifically — collisions, silent-no-ops, ordering requirements.
     Delete if none; don't pad. -->

- `<FILL: the non-obvious trap, stated as the rule that avoids it>`

---

<!-- Pointer, not prose: anything that wants more than a line of explanation belongs in ARCHITECTURE.<facet>.html. -->
Full rationale and human review criteria live in `ARCHITECTURE.<facet>.html`.
