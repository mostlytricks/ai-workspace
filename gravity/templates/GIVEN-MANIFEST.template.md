<!--
  GIVEN-MANIFEST.template.md — the provenance sheet for the GIVEN layer (workspace CLAUDE.md §6).
  Copy to .gravity/given/MANIFEST.md (cross-cutting) or .gravity/<domain>/given/MANIFEST.md
  (domain-scoped). Seeded and filled by /given, which routes files out of .gravity/inbox/.

  THE LAYER'S RULES:
  - given/ holds RECEIVED truth — what the project was TOLD (data dictionaries, business
    rules, vendor docs, domain explainers) — never what it decided. Authored truth lives
    in SPEC/MISSION/PLAN.
  - QUARRY, NOT CONTRACT: a given doc never becomes a shadow SPEC. A fact agents rely on
    repeatedly graduates into its owner-doc WITH a back-citation (`source: given/<file> §n`).
  - PROVENANCE SURVIVES MODIFICATION: agents may render readable copies, but every file
    carries a fidelity mark, and disputes resolve against the raw original — never the
    rendering. raw/ holds originals as-received (git-ignore when heavy or private; the
    manifest row stays, marked `private`, as the committed pointer).
  - A file in given/ with no row here, or a non-private row pointing at a ghost file, is
    drift — `check.py given` flags both, and any file still sitting in .gravity/inbox/.
  Delete this comment when filled.
-->

# GIVEN — <project><, domain: <slug>> — manifest

Received domain knowledge. Quarry, not contract: cite rows, don't restate them;
facts graduate to SPEC/MISSION/PLAN with a back-citation. Disputes → the raw.

| File | Source (who gave it) | Received | Version / validity | Authoritative for | Fidelity | Privacy |
|---|---|---|---|---|---|---|
| `<slug>.md` | <person/team/system> | <YYYY-MM-DD> | <e.g. ERP v11; valid until re-export> | <the one scope this answers> | reformatted (from `raw/<file>`) | committable |
| `raw/<file>` | <same> | <YYYY-MM-DD> | <same> | tiebreak original | verbatim | private — local only, git-ignored |

<!-- Fidelity marks:
     verbatim     — the file IS what was received, untouched.
     reformatted  — structure/markdown only; content unchanged (diffable back to raw).
     distilled    — summarized/selected; judgment applied — say in the row what was
                    dropped or scoped out. Missing provenance = `OPEN: awaiting <what>`,
                    never a plausible guess. -->
