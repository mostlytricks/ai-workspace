---
description: Mint one new domain inside a project's .gravity/ — gate it, create the folder with a starter PLAN, and wire all four registry indexes so it's never orphaned.
argument-hint: <project-name> <domain-name>
---

You are running `/new-domain` from `ai-workspace/` to add a domain named **`<domain>`** to project **`<project>`** inside its `.gravity/` doc system (workspace CLAUDE.md §6). Parse `$ARGUMENTS` as `<project> <domain>`; if either is missing, ask for it.

The point of this command is the **gate** ("is this even a domain?") and the **index wiring** (so the new folder is discoverable, not orphaned). `knowledge-viewer` is the reference layout.

## Preconditions

1. **Locate the project** under `active/`, `dormant/`, or `repos/`. If not found, list close matches and stop.
2. **It must already have a `.gravity/` directory.** If not, tell the user to run `/adopt-gravity <project>` first (or that the project is fine on the two-doc minimum) and stop.
3. **`<domain>` must be kebab-case** and not already exist under `.gravity/`. If it exists, switch to *adding a doc to that domain* instead.

## Steps

1. **Run the gate — is it a domain?** (CLAUDE.md §6 / the project's "Adding a domain" section.) A domain earns a folder only with its own *principle*; check for most of:
   - rules an agent must respect to change it safely → wants a `SPEC.md`
   - a "how it's built" beyond a file map → wants an `ARCHITECTURE.html`
   - a multi-step arc, not a single PR → wants a `PLAN.*.md`
   - a one-line *why* + non-goal that should win arguments → wants a MISSION row

   If it fails the gate, **don't mint a folder.** Say so and recommend the alternative: a `PLAN.<slug>.md` slice under an existing domain, or an `ops/` folder for cross-cutting work. Stop there unless the user overrides.

2. **Create the folder, minimal.** Make `.gravity/<domain>/` and a starter `.gravity/<domain>/PLAN.md` — usually the *only* file on day one (docs are recognized only when present). Seed `PLAN.md` with the domain's intent, an `○ planned` status, and the first concrete next step. Add `SPEC.md` / `ARCHITECTURE.html` only if the user says they're needed now.

3. **Wire all four registry indexes** (this is the part that's easy to forget — do every one):
   - **Doc Map** in the root `CLAUDE.md` → add the `<domain>/ …` line.
   - **Router table** in the root `CLAUDE.md` → add a "If you're changing <domain> → read `.gravity/<domain>/SPEC.md`" row *(only once a `SPEC.md` exists; until then list it with a "—")*.
   - **`MISSION.html`** "the system in N domains" → add the row: why · the principle that wins arguments · the non-goal guard. *(Only once it's a confirmed durable domain. If MISSION has no such section yet, add it.)*
   - **`IMPLEMENTATION_PLAN.md`** status spine → add the `○` row pointing at the new `PLAN.md`.

4. **Back-pointer.** If you created an `ARCHITECTURE.html`, its lede points *back* to the MISSION row rather than re-deriving the domain's purpose.

5. **Report** the folder created, the files seeded, and the exact four index edits made — so the user can see nothing was left orphaned. **Do not commit.**

## What NOT to do

- **Do not** scaffold all of SPEC + ARCHITECTURE + PLAN by default — start with `PLAN.md` and let the rest earn their place.
- **Do not** skip an index — an unwired domain is invisible to the next agent and to `/triage`.
- **Do not** force a domain through the gate — if it's really a slice, a `PLAN.*.md` under an existing domain is the correct, lighter answer.
