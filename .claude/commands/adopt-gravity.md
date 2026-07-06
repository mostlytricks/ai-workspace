---
description: Retrofit the .gravity/ doc system into an existing project — relocate the heavy docs out of the root into domain folders, and seed the root CLAUDE.md router.
argument-hint: <project-name>
---

You are running `/adopt-gravity` from `ai-workspace/` to move project `$ARGUMENTS` onto the **`.gravity/` doc system** (workspace CLAUDE.md §6). This is the *opposite* of trivial — it relocates files and rewrites the router — so **propose the mapping and get the user's confirmation before moving anything.**

`knowledge-viewer` is the reference implementation; mirror its layout.

## Preconditions (check, then stop if unmet)

1. **Locate the project** under `active/`, `dormant/`, or `repos/` (junctions read through transparently). If not found, say so and list close matches.
2. **It must already be a git repo** — relocation uses `git mv` to preserve history. If there's no `.git`, stop and say so.
3. **It should have earned it.** `.gravity/` is for a project that *outgrew the flat root* — multiple architecture/spec/plan docs, several domains. If the project has only `CLAUDE.md` + `CONTEXT.md` (the two-doc minimum), say it doesn't need `.gravity/` yet and stop. Don't add ceremony that doesn't pay.

## Steps

1. **Inventory the root.** List the project root. Sort its docs into:
   - **Stays at root (auto-loads / user-facing):** `CLAUDE.md`, `CONTEXT.md`, `README.md` (and any `README.*.md`), `.env*`, license, config. **Never move these.**
   - **Moves into `.gravity/`:** `MISSION.html`, `ARCHITECTURE*.html`, `IMPLEMENTATION_PLAN*.md`, `SPEC*.md`, `DESIGN.md`, any `PLAN.*.md` / roadmap docs. These are the *why / what-next / how-it's-built* docs.

2. **Propose the domain grouping.** Cross-cutting docs go to the `.gravity/` top level (`MISSION.html`, `ARCHITECTURE.html` the system overview, `IMPLEMENTATION_PLAN.md`, `DESIGN.md`). Everything else groups **by subject domain** into `<domain>/` folders, renamed **by kind**:
   - `ARCHITECTURE.<facet>.html` → `.gravity/<facet>/ARCHITECTURE.html`
   - `SPEC.<domain>.md` → `.gravity/<domain>/SPEC.md`
   - `IMPLEMENTATION_PLAN.<topic>.md` → `.gravity/<domain>/PLAN.md` (or `PLAN.<slug>.md` when a domain has several)
   Present the full before→after move list as a table and **ask the user to confirm or adjust the domain boundaries** before touching disk. Domain grouping is a judgment call — it's theirs.

3. **Relocate with `git mv`** (preserves rename history), from the project's real path. Create `.gravity/` and the domain subfolders first. Move one file per `git mv`. Do **not** use plain `mv` — it loses history.

4. **Fix references.** After moving, grep the repo for links to the old paths and repair them:
   - other docs' cross-links (HTML `href`, markdown links) — relative paths shift when a file gains a `.gravity/<domain>/` prefix;
   - any **code comments / build scripts / linters** that name a doc path (rare but check — e.g. a comment pointing at `IMPLEMENTATION_PLAN.md`);
   - `README.md` / `CONTEXT.md` pointers into the moved docs.
   Report what you changed; flag anything outside the repo you can't fix (external skills, IDE files).

5. **Seed the router + embed the protocol card.** Copy the three sections from `templates/GRAVITY.template.md` into the project's **root `CLAUDE.md`** (replacing any existing flat "Docs:" pointer / Document-Authoring section): the **Doc Map**, the **read-first router table**, and the **Adding a domain** gate. Fill the Doc Map tree and the router table from the actual domains you just created. Then embed the protocol card: `cp <workspace-root>/templates/GRAVITY-PROTOCOL.template.md <project>/.gravity/GRAVITY.md`, delete the template's top comment block, and fill its `v<X.Y>` stamp with **major.minor from the workspace root `VERSION` file** (never invent a version). The card is a verbatim copy — do not rewrite it from memory or tailor it per project; it's what makes the repo self-describing when opened without the workspace. Also drop the **Codex shim** if absent: `[ -f AGENTS.md ] || cp <workspace-root>/templates/AGENTS.template.md AGENTS.md` — so the project is discoverable by agents that look for `AGENTS.md` and reach the same router. Never overwrite an existing `AGENTS.md`.

6. **Establish the four registry owners** (CLAUDE.md §6 — the directory is the registry, there's no registry file):
   - **routing** → the root `CLAUDE.md` Doc Map + router table (done in step 5);
   - **why** → add a "the system in N domains" section to `.gravity/MISSION.html` with one row per domain (why · the principle · the non-goal). If no `MISSION.html` exists, note it as a follow-up rather than inventing one.
   - **status** → add a per-domain `✓/◑/○` status spine to `.gravity/IMPLEMENTATION_PLAN.md`.
   - **existence** → the directory itself (done).
   Each domain `ARCHITECTURE.html` lede should point *back* to its MISSION row rather than re-deriving its purpose.

7. **Verify.** Run the project's doc linter / build if one exists (e.g. `npm run lint:docs`) to confirm nothing broke. Report the result honestly.

8. **Update `CONTEXT.md`** — a Completed bullet for the restructure, pointing at the new Doc Map.

## What NOT to do

- **Do not** move `CLAUDE.md`, `CONTEXT.md`, or `README.md` into `.gravity/` — they auto-load / are user-facing and must stay at root.
- **Do not** invent docs to fill the layout — `.gravity/` is *recognized only when present*. A domain with just a `PLAN.md` is fine.
- **Do not** commit — leave the staged moves for the user to review and commit.
- **Do not** use plain `mv` for tracked files — always `git mv`.
