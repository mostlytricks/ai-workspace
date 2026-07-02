---
description: Render a project's .gravity/ as a star system — MISSION at the core, domains orbiting at activity speed, SPEC rings, PLAN satellites. 2D instrument or 3D observatory, themeable.
argument-hint: <project-or-alias> [3d|both] [theme]
---

You are running `/cosmos` from `ai-workspace/`. It renders one `.gravity/` project as a **star system** — the conceptual complement to `/dashboard`'s table: MISSION is the star, each domain a planet, and everything about the drawing is *derived from the live docs*, never hand-kept.

The mapping (what the user is looking at):

| Cosmic object | Gravity concept | Signal |
|---|---|---|
| star (center) | `MISSION.html` | click → the project goal |
| planet | `.gravity/<domain>/` | size = doc mass (file count) |
| ring | `SPEC.md` present | an unringed planet is an unfenced domain |
| moon | `ARCHITECTURE.html` present | the human deep-dive exists |
| satellites | `PLAN.*.md` files | slices in transit, one dot each |
| orbit distance | spine status | ◑ active inner · ✓ stable mid · ○ planned outer (dashed) |
| orbit speed | activity | `3×PLANs + mass`, ×1.6 if ◑, ×≤2 if touched <21 days |

## Run it

Parse `$ARGUMENTS` as `<project> [mode] [theme]` — mode is `3d` or `both` (default 2d); theme is one of the generator's `--list-themes` output (default `nebula`). Then:

```bash
python .claude/dashboard/generate_cosmos.py <project> --mode <2d|3d|both> --theme <theme> --open
```

- The project token goes through `resolve_project.py` (exact name → declared alias → unique acronym → unique substring); if it's ambiguous the script prints candidates and exits — relay them, don't guess.
- Requires a `.gravity/` directory; for flat projects the script stops with a pointer to `/adopt-gravity`. Don't work around it — a two-doc project has no domains to draw.
- Output lands in `.claude/dashboard/cosmos/<name>[.3d].html` (gitignored, regenerate-at-will); `--open` launches the browser.

## Reading the sky (mention what's notable, briefly)

After generating, glance at the data you already have and note anything diagnostic, e.g.:
- **Unringed planets** — domains without a SPEC (`check.py spec` WARNs on these too).
- **A readout showing "no MISSION row — unwired?"** — registry drift; suggest `/triage`.
- **A fast outer planet or a frozen inner one** — status/activity mismatch worth a look (a ○ planned domain touched yesterday, or a ◑ active one untouched for months).

Keep it to a line or two — the picture is the point, not a report.

## What NOT to do

- Don't hand-edit the generated HTML — every fact in it is scanned; fix the docs instead.
- Don't add data files or a registry for the cosmos — the `.gravity/` directory *is* the data.
- Don't commit `cosmos/` output (gitignored) — only the generator and this command are skeleton.
