---
description: One project, one page — the unified per-project view. Tabs compose the cosmos (domains), the boundary seam graph, and the Spec Health instrument over a single live scan; Overview carries the goal, the now, the spine, and doc links.
argument-hint: <project-or-alias> [theme]
allowed-tools: Read, Glob, Grep, Bash(python gravity/lib/generate_observatory.py:*), Bash(python .claude/scripts/install_lib.py:*)
---

You are running `/observatory` from `ai-workspace/`. It renders one `.gravity/` project as **one page with seven tabs**, all fed by a single scan (`gravity/lib/scan_project.py` — one scanner, many callers), so the views can never disagree with each other:

| Tab | Contents | Renderer (module) |
|---|---|---|
| **Overview** | goal (MISSION/PLAN) · the now (CONTEXT: last touched, next step) · the **drift card** (live `check.py` consistency + spec-honesty findings, imported never reimplemented; "checkers unavailable" renders as a warning, never as clean) · the spine table (per-domain status/SPEC/ARCH/PLANs/why) · the **tracks card** (the direction axis, when the IMPLEMENTATION_PLAN has a Tracks table — name, direction, MISSION § pointer, carrying-domain chips; a missing § pointer or a carrying PLAN absent from disk renders loud) · clickable authored-doc links | native (`generate_observatory.py`) |
| **Queue** | every `PLAN.*.md` across the domains as one work table — status glyph + note, Goal snippet, Next line, last-touched — building first, shipped dimmed last. A PLAN without a `Status:` line is flagged (it can't be mirrored into the spine). Slices carried by a track wear its ⟡ chip. | native |
| **Seams** | the boundary seam graph: Boundary Map rows as flowing edges (packets = direction), evidence citations per seam, `OPEN:` rows dashed guard-red, unparseable rows listed loud — or an honest empty state pointing to `/new-spec <p> integration` / `/excavate` when no integration SPEC exists | `generate_boundary.render` |
| **Spec Health** | per-domain contract honesty: walls (`[lint]/[type]/[test:…]`) vs judgment (`[review]`) vs guidance (`[—]`), gate presence, Behavioral Contract lines bound to tests, template `FILL` leftovers. Freeform (pre-v2) SPECs get a **tag census** and are labeled `freeform` — the census never invents discrete rules. | native |
| **Graduation** | intent → contract, per domain: PLAN **Scenario** bullets paired with SPEC **Behavioral Contract** lines (token-overlap heuristic — the page says so). Shows ✔ graduated (test-bound), ○ still intent, and the two dishonesty smells loud: a scenario **reworded into the BC without a test**, and **unbound BC lines**. A shipped PLAN whose scenarios never graduated is flagged (its wall may live in a gate — check before judging). | native |
| **Timeline** | `docs/walkthroughs/` as a reverse-chron proof strip — date · domain chips (from the `Domain(s):` header, filename fallback) · title, each linking to its file. Honest empty state pointing at `WALKTHROUGH.template.md` when the log doesn't exist. | native |
| **Orbit 3D** | the analytical 3D system: health rings (solid arc = walls share), **coupling arcs** between domains from doc cross-references, **track arcs** (⟡ dashed, labeled chains over the domains carrying one cross-domain direction — green once the track is ✓), comet trails on recently-touched domains, guard-red pulse on unfenced ◑ domains; HUD toggles for arcs/tracks/trails | `generate_cosmos.render_3d` |

(The former `/cosmos` and `/boundary` commands were folded in here. Their generator scripts remain as the renderer modules above — each keeps a debug CLI writing beside the page (`<name>.3d.html` / `<name>.seams.html`), but the user-facing door is this command. The 2D Domains tab was retired 2026-07-25 — the 3D view superseded it — and the `render_2d` code was removed the same day; git history keeps it.)

## Run it

Parse `$ARGUMENTS` as `<project> [theme]` — theme is one of `aurora` (default) / `daylight` / `sandstone` / `forest` / `slate` — the workspace-wide dashboard family (`DESIGN.dashboard.md`). Then:

```bash
python gravity/lib/generate_observatory.py <project> --theme <theme> --open
```

- The project token goes through `resolve_project.py`; if ambiguous the script prints candidates and exits — relay them, don't guess.
- **The nav carries attention badges** — count chips only where something wants a look: Overview (checker findings; guard-red when any FAIL), Queue (◑ building), Seams (`OPEN:` rows), Spec Health (unfenced ◑ domains), Graduation (the two dishonesty smells). No badge = nothing pending there.
- **Tabs are deep-linkable** — `<page>.html#queue`, `#grad`, etc.; docs and packets can link straight to one instrument of one project.
- **Theming is live in the page** — the header's five swatch buttons switch the chrome *and* the embedded instruments in place (every palette is pre-rendered into the file; the choice persists in `localStorage` as `dash-theme` — shared with the workspace dashboard and the MISSION/ARCHITECTURE doc pages, so one pick follows you everywhere). The two light themes render instruments as a paper chart (dark ink on a pale canvas). `--theme` only sets the first-load default, so don't regenerate just to change color.
- Requires a `.gravity/` directory (the scan stops with a pointer to `/adopt-gravity` otherwise). A missing integration SPEC is fine — the Seams tab shows the pointer instead.
- **Output lands inside the project** — `<project>/.gravity/observatory/index.html`; `--open` launches the browser. The folder carries a `.gitignore` of `*` so it ignores itself: the page is visible to anyone who opens the repo but never becomes a tracked artifact that can go stale in git. Doc links are relative, so the page is not pinned to the machine that rendered it.
- **The renderer is protocol-side** (`gravity/lib/`), so a project carrying `.gravity/lib/` renders itself with no workspace at all: `python .gravity/lib/generate_observatory.py` — no arguments, the lib's own location names its project. If a project has no `.gravity/lib/` yet, `check.py` says so (`LIB_MISSING`); install it with `python .claude/scripts/install_lib.py <project>`.

## Reading it (mention what's notable, briefly)

Glance at the script's summary line and the facts you already have; note anything diagnostic, e.g.:
- **Unfenced active domains** — a `◑` domain with no SPEC is an agent working without walls.
- **Low wall-share** — a domain whose rules are mostly `[review]` promises; suggest promoting rules by giving them tests (`/new-spec` retrofit).
- **No Gate line** — nothing proves a change in that domain; the SPEC template wants one.
- **Unbound Behavioral Contract lines** — scenario intent dressed as contract; it graduates only with a named test.
- **Shipped-but-never-graduated scenarios** (Graduation tab) — a ✓ PLAN whose given/when/then never earned a `[test:…]` line; either the wall lives in a gate (fine — say where) or the regression test was skipped.
- **Drift findings on Overview** — the card is `/triage` for this one project; FAILs mean a domain is unwired from an index. Relay them; the fix is always in the docs.
- **Status-less PLANs piling up** (Queue tab) — intent stubs that can't be mirrored into the spine; either give them a `Status: ○ planned` line or fold them into a neighbor.
- **A sick tracks card** — a track with no MISSION § pointer is scope creep with a label (drop it or earn the MISSION row); a carrying PLAN missing on disk is a dangling index; more than 3 active tracks isn't direction, it's drift.
- **A stale CONTEXT next-step** against a busy spine — session-ritual drift; suggest `/triage`.

Keep it short — the page is the report.

## What NOT to do

- Don't hand-edit the generated HTML — every fact is scanned; fix the docs and rerun.
- Don't add data files or a registry — the project's docs *are* the data.
- Don't "fix" a freeform SPEC's census by rewording this command — retrofit the SPEC to the v2 template (`/new-spec`) if you want structured rule counts.
- Don't commit `.gravity/observatory/` output — the folder ignores itself by design; a committed page is a page that can be stale in git, and this one's own footer says a wrong page means doc drift.
- Don't hand-edit an installed `.gravity/lib/` — it's a verbatim copy of the distribution. Fix `gravity/lib/` and re-install (`/sync-gravity`).
