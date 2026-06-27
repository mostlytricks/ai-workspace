---
description: Author (or retrofit) one domain's SPEC.md from the v2 template — the generative Minimal Shape + enforcement-tagged Rules — with a verification procedure that keeps every tag honest. Built so a less-capable agent can't fake enforcement.
argument-hint: <project-name> <domain-name>
---

You are running `/new-spec` from `ai-workspace/` to write **`.gravity/<domain>/SPEC.md`** for project **`<project>`** (workspace CLAUDE.md §6; stencil = `templates/SPEC.template.md`). Parse `$ARGUMENTS` as `<project> <domain>`; if either is missing, ask.

A SPEC is **two halves at once**: *generative* (a **Minimal Shape** + a 3-step **Generate loop** an agent builds a unit *from*) and *limiting* (a **Rules** checklist where **every rule names the wall** — `[lint]` / `[type]` / `[test:name]` / `[review]` / `[—]` — that catches a violation). The hard part, and the entire reason this command exists, is **tagging honestly**. A wrong tag is worse than no SPEC: `[lint]` on a rule nothing checks manufactures false trust. So this command is mostly a **verification procedure** — never tag from assumption; tag from evidence you went and found.

**Two worked examples to imitate** (read both first — they span the space):
- `knowledge-viewer/.gravity/doc/SPEC.md` — the **shape + lint** pole: most rules are real `[lint]` walls.
- `knowledge-viewer/.gravity/search/SPEC.md` — the **behavior + review** pole: one real `[test]` gate (server-dependent), everything else honestly `[review]`.

## Preconditions

1. **Locate the project** under `active/`, `dormant/`, or `repos/`. If not found, list close matches and stop.
2. **The domain should already exist** as a subject (a `.gravity/<domain>/` folder, or a clear code area). If there's no domain yet, this is a `/new-domain` job first.
3. **Gate — does this domain even want a SPEC?** Only domains **an agent actually changes** earn one (CLAUDE.md §6: "read-only domains stay HTML-only"). If nobody edits it, stop and recommend leaving it `ARCHITECTURE.html`-only.
4. If a `SPEC.md` already exists, this is a **retrofit** — preserve its good content, add the missing halves (Gate line, Generate loop, tagged Rules), don't gut it.

## Step 1 — Find the gate (don't invent one)

Discover what enforcement *actually exists* before writing a word of contract:

- `grep` the project's `package.json` (and any workspace `*/package.json`) for `test`, `test:*`, `lint`, `lint:*`, `eval`, `typecheck` scripts. **Read the script's source** — does it `exit`/`process.exitCode = 1` on failure (a real gate) or just print (an eval you *read*, not a wall)?
- Note **preconditions**: does the gate need a running server? a corpus/fixture file? an env var? A gate with an unmet precondition is not green — it never ran. State the preconditions in the `Gate:` line.
- If **no automated gate exists**, say so plainly in the `Gate:` line ("no automated gate — `[review]` only") and expect most rules to be `[review]`. That is an honest, common outcome (see the `search` example). **Never write a `Gate:` command that doesn't exist in `package.json`.**

## Step 2 — Read the code for the real shape

- Find the type/interface/schema that defines a valid unit (`grep` for the `interface`/`type`/`zod` that the runtime actually uses). The **Minimal Shape** is copied from *that*, not imagined.
- If there's a live surface (an endpoint, a CLI), **probe it** and paste the real result into the shape — confirm reality, don't assume it.

## Step 3 — Tag every rule from evidence (the honesty core)

For each rule, assign its wall **only** by the evidence rule below — when the evidence isn't there, **drop to the weaker tag**. The failure mode this prevents is *over-claiming*; the safe default is always `[review]`.

| Tag | You may use it **only if…** | How you verified |
|---|---|---|
| `[lint]` | you opened the linter source and **found the check** | name the linter file + the check |
| `[type]` | a real `interface`/schema in the code **rejects** the violation at compile time | name the type + file |
| `[test:<name>]` | the test/eval **exists** and asserts this; you read it (ideally ran it) | name the test + its precondition |
| `[review]` | nothing above catches it — a human is the only wall | *(this is the safe default — use it when unsure)* |
| `[—]` | it's guidance, not a rule | — |

Hard rules for a weaker agent:
- **No tag without a file you can point at.** If you can't cite the linter line / type / test, it's `[review]`.
- **When unsure, under-claim.** `[review]` is always honest; `[lint]`/`[test]` are claims you must earn.
- **Don't trust sibling docs.** An `ARCHITECTURE.html` may name a gate or behavior that drifted — verify against `package.json` + source, not prose.

## Step 4 — Write it short

Fill `templates/SPEC.template.md`: **Gate** line, **Core Definition** (1–2 sentences), **Minimal Shape** (the copied real shape), **Generate (the loop)** (3 lines), tagged **Rules**, optional **Behavioral Contract** (`given/when/then` → its test — *only* if a test backs it; else fold into Rules as `[review]`), **Gotchas**. Keep the rate-of-change boundary: **SPEC = true of every unit forever; PLAN = this change's intent; WALKTHROUGH = its proof.** If a rule needs a paragraph of *why*, that prose belongs in `ARCHITECTURE.html` — link up, don't restate. Stop when every rule is checkable; more detail past that bloats agent context and drifts from the gate.

**For an `integration` domain, use the template's INTEGRATION VARIANT** (workspace CLAUDE.md §5): swap **Minimal Shape → Boundary Map** (one row per seam: from → to · what crosses · transport/port, plus the local ports/base-URL table) and **Generate → Change Order** (the strict cross-boundary edit sequence, last step bound to the Gate). The variant block lists the typical cross-boundary walls to lift into **Rules** — wire envelope, generated client-type sync, auth/session credential, the database-access boundary (`web` never reaches the DB directly), and the mandatory change order. Tag each one *just as honestly* as any other rule (a generated-types check is `[test]`/`[type]` only if it really runs; else `[review]`). Include only cross-boundary rules; leave backend internals, frontend component rules, and schema design in their own domain SPECs.

## Step 5 — Wire the indexes & prove it

- **Doc Map** (root `CLAUDE.md`) → add `SPEC.md` to the `<domain>/` line.
- **Router table** (root `CLAUDE.md`) → set the domain's read-first cell to `.gravity/<domain>/SPEC.md` (was `—`).
- **Run the gate** you wrote in the `Gate:` line (start the server first if it needs one) and paste the result — if it can't run, say why. A SPEC whose own gate you never ran is unproven.
- If the project has no `.gravity/`, write the flat `SPEC.<domain>.md` at the project root instead and skip the Doc-Map wiring.

## Step 6 — Record & report

- Add/refresh the project's `CONTEXT.md` "Completed/Recent" with one bullet linking the new SPEC (don't restate it).
- Report: the gate you found (and its preconditions), the shape's source file, the **tag distribution** (how many `[lint]`/`[type]`/`[test]`/`[review]`), and the gate result. **Do not commit** — that's the user's call.

## What NOT to do

- **Do not invent a gate, a test name, or a `[lint]` tag.** Unverifiable → `[review]`. This is the one rule that matters most.
- **Do not let the SPEC grow into a second `ARCHITECTURE.html`.** Rules and shapes only; rationale links up.
- **Do not write a SPEC for a read-only domain** an agent never changes — leave it HTML-only.
- **Do not skip running the gate** when one exists — the proof is the point.
