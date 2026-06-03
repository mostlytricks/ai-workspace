# <project name>

One-sentence description of what this project is and who it serves.

---

## Stack

- **Language / runtime:** e.g. Python 3.12, Node 20, JDK 21
- **Framework:** e.g. FastAPI, Next.js 14, Spring Boot 3
- **Key dependencies:** the 2-3 libraries that shape the architecture (DB driver, ORM, UI lib).
- **Datastore:** e.g. Postgres 16 (local Docker), Redis (optional).

## Run

```bash
# install
<command>

# start dev server / app
<command>
```

Default ports / URLs: e.g. `http://localhost:8000` (API), `http://localhost:5173` (UI).

## Test

```bash
<command>
```

Coverage expectations or "no tests yet" — be honest.

## Conventions

- Branch naming: e.g. `feat/<short-name>`, `fix/<short-name>`.
- Commit style: e.g. Conventional Commits, or "imperative one-liner, no body."
- Formatter / linter: e.g. `ruff`, `prettier`, run on save.
- Anything non-obvious about file layout, naming, or where to put new code.

## Constraints & Gotchas

- Environmental quirks: e.g. requires WSL, needs Docker running, specific Node version.
- Known sharp edges: e.g. "auth middleware is being rewritten, don't add new routes to the old one."
- External dependencies: API keys needed, services that must be running, rate limits to respect.

## Entry Points

- Main file(s) where new work usually starts.
- Where the route/controller layer lives.
- Where shared types/schemas live.

<!-- This is the lightweight architecture map and the default home for "how it's built".
     If the project grows an ARCHITECTURE.html (workspace CLAUDE.md §6), that file becomes the
     canonical "how it's built" — keep this section a pointer to it rather than duplicating boundaries. -->
- The architectural seam, if any: state the *mechanics* here (which file/type is the boundary) and link the *principle* to `MISSION.html` — don't restate it. One concern, one home.

## Git

- Remote: `<url>`
- Default branch: `main` / `master` / other

---

<!--
This file is stable identity — it changes rarely. For in-flight session state
(what was just done, what's broken, what's next), use CONTEXT.md.
-->
