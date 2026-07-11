<!--
  PROJECTS.sample.md — the tracked TEMPLATE for the workspace project index.

  The real index, PROJECTS.md, is intentionally git-IGNORED (it carries private
  project names, status, and blockers — not for a shared/public remote). This
  sample is the portable skeleton copy: on a fresh workspace, `cp PROJECTS.sample.md
  PROJECTS.md` and start listing real projects in your local copy.

  Keep this file generic — example rows only, never real project info.
-->

# Projects Index

Source of truth for what exists in this workspace and which tier each project lives in. Update this whenever a project moves between `active/`, `dormant/`, or `archive/`, or when its focus/blocker changes meaningfully. Real project files live in `repos/<name>/`; tier folders hold directory junctions pointing into `repos/`.

**Format per row:** `name | stack | last-touched (YYYY-MM-DD) | current focus or resume blocker`

---

## active/

_Touched within ~30 days. Each has CLAUDE.md + CONTEXT.md. The "focus" column should be the same as the project's CONTEXT.md → Next Step, in one line._

- example-web-app        | Node/TS (framework + DB)     | 2026-01-15 | one-line current focus = the project's CONTEXT.md → Next Step
- example-cli-tool       | Python (stdlib)              | 2026-01-12 | next: the single concrete next step for this project

## incubator/

_Experimental. Real folders OR junctions into `repos/` if intended to graduate. No CLAUDE.md/CONTEXT.md overhead. Promote with `/promote <name>` when validated._

- example-experiment     | prototype (language)         | 2026-01-08 | validating the core idea; /promote once it proves out

## dormant/

_Paused but alive. The "resume blocker" must be concrete — what specifically needs to be true before you'd pick this back up. If you can't name a blocker, this project belongs in archive/._

- example-paused-service | Node/Express                 | paused 2026-01-01 | resume blocker: upstream API v2 not yet released

## archive/

_Done, abandoned, or superseded. Read-only. Listed here only so you don't accidentally recreate something that already exists._

- example-old-scaffold   | _empty scaffold_             | archived 2025-12-01  | never had content; name free to reuse — flagged so it isn't recreated

---

## Gravity adoption

_Where each project sits on the gravity conventions (current system version: root `VERSION`). The **dashboard renders this live from disk** (chips on every card, always accurate); this table is the at-a-glance markdown view — a snapshot reconciled like the tier rows above (run `/triage` if it drifts). **stamp** = the `> gravity: vX.Y` line in `CLAUDE.md` · **docs** = `.gravity/` faceted vs `flat` two-doc · **card** = the `.gravity/GRAVITY.md` protocol-card stamp (`.gravity` projects only; `—` = missing → 📡 in `/triage`; `n/a` for flat projects) · **rel** = a `CHANGELOG.md` (release light-layer) · **codex** = the `AGENTS.md` shim._

| Project | stamp | docs | card | rel | codex |
|---|---|---|---|---|---|
| example-web-app | `v1.8` | `.gravity` | `v1.8` | ✓ | ✓ |
| example-cli-tool | `v1.8` | flat | n/a | — | ✓ |

Next adoption moves: decide per **flat** project whether it earns `.gravity` or stays a clean two-doc project with a light stamp; add release light-layer only where a project is ready to cut versions.

---

<!--
Maintenance notes:
- The /triage slash command (run from workspace root) can auto-summarize active/ and dormant/ by reading each subdir's CONTEXT.md. Use it weekly and reconcile any drift here.
- If a row hasn't been touched in 30+ days under active/, either update its CONTEXT.md or demote to dormant/.
- If a dormant row's resume blocker has resolved, promote back to active/ and refresh CONTEXT.md.
-->
