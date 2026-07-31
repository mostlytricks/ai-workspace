# Golden scenarios — testing gravity's own commands

Gravity's slash commands *claim* to wire things up (a new domain into four indexes, a new project into the tier model, a release into the changelog). Until now nothing **checked** that claim — the proof was prose. These scenarios make the proof mechanical.

## The idea

A slash command runs inside an LLM agent, so you can't unit-test the agent. But you **can** test the command's **structural postconditions**. A scenario is therefore a triple:

```
(command, golden-input fixture, deterministic structural assertions)
```

- The **agent step** (running the command) stays manual — you replay it when you change the command or the templates it depends on.
- The **assertion** is a script (`check.py`), so no one ever again eyeballs "did all four indexes get wired?"

This is the **acceptance** half of gravity testing ("did our improvement work as intended?"). Its companion is **conformance** ("did a feature follow its domain SPEC?") — whose first slice has shipped as `check.py spec`, the **spec-honesty checker** (below).

## Layout

```
.claude/scenarios/
  check.py            # the structural-invariant library + CLI (the real asset)
  README.md           # this file
  <command>/          # one folder per command under test
    SCENARIO.md        # the replay recipe
    expect.json        # declarative postconditions
    fixture/           # the golden input project
  db-pack/pack/       # NOT a command scenario — the synthetic Oracle-shaped DB
                      # evidence pack (CSVs) that `selftest` drives scan_db.py
                      # against: separation, census, seams, honest degradation
```

`check.py` is deliberately reusable: its core, `check_gravity_consistency(project_dir)`, is the same index-drift check `/triage` should call on real projects. Build it once; two callers (scenarios on fixtures, `/triage` on live repos).

## Running

```bash
# Prove the checker itself (run after editing check.py):
python .claude/scenarios/check.py selftest

# Check any real .gravity/ project for index drift:
python .claude/scenarios/check.py consistency --project repos/<project>

# Verify a project's SPEC.md Gates + enforcement tags against reality:
python .claude/scenarios/check.py spec --project repos/<project>

# Replay a scenario (see the command's SCENARIO.md for the agent step):
python .claude/scenarios/check.py scenario \
    --scenario .claude/scenarios/<command> --actual <post-run-project>
```

## Where the checks live

The checker is **split by scope**. `gravity/lib/check_project.py` holds everything that judges one
project from its own docs (`consistency`, `spec`, `intake`, `given`) — it travels with the protocol
into `<project>/.gravity/_lib/`, so a clone with no workspace runs the same checks against itself
(`python .gravity/_lib/check_project.py`). This file's `check.py` re-exports all of it and adds what
is workspace-scoped and therefore never embedded in a project: `workspace` (tiers, junctions,
`PROJECTS.md`), the fixtures, and the `selftest` harness. Every existing import site
(`from check import check_gravity_consistency`) still works.

## How parsing works (and its limits)

`check.py` uses **heuristic slug-match**: a domain is "wired" into an index region if its kebab-case slug appears in that region (the Doc Map code block, the router table, the MISSION rows, the PLAN status spine). Fixtures are author-controlled, so this is robust enough. If real projects start tripping it (a slug that's also a common English word, say), harden with machine-readable anchors in the templates — not before.

Severity: missing wiring is a **FAIL** (the orphaned-domain bug). A `.gravity/<slug>/` route pointing at a non-existent folder, or a domain folder with no `PLAN*.md`, is a **WARN** (templates legitimately ship example rows like `integration/`). `consistency` also emits **`COUPLING_UNCONTRACTED`** (WARN): two domains whose docs cross-reference each other ≥5 times (path-shaped mentions, from `scan_project.scan_couplings` — one scanner, many callers) while neither `integration/SPEC.md` nor `CONTRACT.md` names the pair — a strong doc seam no contract owns; the fix is naming the pair in the contract, or an honest "no seam here" judgment. And **`SLICE_STALE`** (WARN), the comet rule: a `○ planned` slice PLAN untouched past 30 days (file mtime — under-claims on fresh clones), or a dated deferral row (`… (deferred YYYY-MM-DD)`) in `IMPLEMENTATION_PLAN.md` never picked up. Deferred work must resurface by age, never by memory; the fix is pick it up, re-date it, or drop it — silence is the one wrong move. Finally **`LIB_MISSING`** / **`LIB_STALE`** (WARN), the twin of `PROTOCOL_MISSING`/`PROTOCOL_STALE`: a project with no `.gravity/_lib/`, or one older than the distribution, can't render or check itself off-workspace — the fix is always a re-install (`python .claude/scripts/install_lib.py <project>`), never a hand-edit. `LIB_STALE` is judged only when a *newer* distribution is doing the judging: run from a project's own installed lib the two versions are equal and it stays silent, because a bare clone genuinely cannot know a newer version exists. And **`MACHINERY_UNMIGRATED`** (WARN): a pre-v4 bare-named machinery dir (`lib/`, `observatory/`, `inbox/`, `given/` — root *and* per-domain) still on disk. v4 made the sigil the rule (`_lib/` …), and the old names stay in `NON_DOMAIN_DIRS` so they are never misread as domains — this is drift to report, not breakage. One finding per dir; the fix is always `python .claude/scripts/migrate_gravity_v4.py <project>`, never a hand-`mv`.

**A domain can only be unwired from an index that exists.** A two-doc brownfield project (CLAUDE.md §5 brownfield inversion: `.gravity/integration/` with no MISSION/PLAN yet) is a sanctioned state — the checker skips the absent index files and emits one `INDEX_ABSENT` WARN each instead of FAILing every domain.

## The spec-honesty check (`check.py spec`)

A SPEC.md's enforcement tags are a promise: `[lint]` means a linter really fails, `[test:x]` means test `x` really exists. `/new-spec` keeps that promise **at authoring** — `check.py spec` keeps it **over time**, catching the rot (a renamed test, a deleted npm script, a template leftover) that silently turns a wall into a lie. Same under-claiming philosophy as `consistency`: FAIL only on what is provably dead, WARN on weak signals, silence where we can't verify (e.g. non-npm projects skip all npm-based checks).

| Finding | Severity | Meaning |
|---|---|---|
| `SPEC_UNFILLED` | FAIL | template leftovers survive (`<FILL`, `[FILL`, `[test:name]`, `<domain>`) |
| `GATE_DEAD` | FAIL | the Gate names an `npm run` script or a path that no longer exists |
| `TAG_DEAD` | FAIL | a `[test:<name>]` resolves to no npm script and no test-ish file |
| `GATE_MISSING` | WARN | no `Gate:` line — an agent has no command to prove a change |
| `TAG_UNBACKED` | WARN | `[lint]`/`[type]` tags with no lint/typecheck anywhere in the Gate or scripts |
| `RULES_UNTAGGED` | WARN | a `## Rules` section in the legacy fully-untagged form |
| `SPEC_FREEFORM` | WARN | no `## Rules` checklist at all — a pre-v2 sheet whose tags ride headings/prose; retrofit with `/new-spec` |

Parsing tolerances: `_read` never crashes on a non-UTF8/unreadable file (replace + move on), and a `[test:<file>::<fn>]` pytest node id is alive when the named file exists and mentions the function (the full id string never appears verbatim anywhere).

## The architecture-anchor check (`check.py arch`)

`ARCHITECTURE.html` is the one **authored** diagram surface. The observatory next to it is generated, git-ignored and regenerated on every scan; an architecture page is committed and maintained by hand, so nothing regenerates it when the code moves underneath. This check gives the diagram something mechanical to hold onto: the grid cells and flow/trace nodes in `ARCHITECTURE.template.html` / `ARCHITECTURE.domain.template.html` each carry `data-path="<file>"`, and every one of those files must still exist. Extraction is a raw-text regex, so it is **element-agnostic**: a `data-path` on an inline-SVG `<text>` node (the v4 `fd-` flow-diagram idiom) is judged exactly like a `<code>` grid cell — `selftest` proves it with an SVG-anchored fixture node.

| Finding | Severity | Meaning |
|---|---|---|
| `ARCH_PATH_DEAD` | WARN | a `data-path` anchor names a file/dir that no longer exists — the diagram outlived the file |

**Why WARN, not FAIL.** A dead Gate breaks the change loop; a dead diagram path only misleads a reader. Putting every doc page on the critical path of every refactor is how a checker earns reflexive ignoring.

**Under-claiming, three ways.** The anchor is **opt-in** — a page with no `data-path` is silent, never nagged into migrating, so the six pre-existing domain pages stay clean until someone converts them. Unresolvable values are **skipped, not guessed**: globs (`chat/providers/*`), unfilled stencil markers, and prose (`provider base URL from .env`) all produce nothing. And a token's `:123` line suffix is dropped before the existence test, so line drift never fires it.

**What it deliberately cannot do.** It catches a *moved or deleted file*. It cannot tell you a cell is now wrong, an arrow reversed, or a fifth branch was added and never drawn. The templates stamp `authored · last reviewed <date>` precisely so the page states which half is machine-checked and which half needs a human — a page that implies the whole diagram is verified is worse than one that admits it isn't. The CLI holds the same line: a project whose anchors are all unfilled stencils reports *"no resolvable anchors — nothing verifiable"*, never a bare OK.

## The palette check (`check.py theme`)

Gravity draws the same five themes on three surfaces — the observatory/Orbit renderer, the fleet dashboard, and the browser-read doc pages — and they are **not** copy-paste duplicates: each speaks its own token vocabulary for the same palette (`--surface`/`--ink` on the dashboard, `--panel`/`--text-hi` in docs, plain dict keys in the renderer). That is why merging them was rejected; the surfaces legitimately differ. What was missing was an **owner**, so a half-finished retune could leave one surface a shade off with nothing noticing.

`gravity/lib/palette.py` is now that owner: it declares the **anchor hues** every surface must agree on (`bg`, `ink`, `dim`, plus the CSS-only `h1-grad`) and the vocabulary map the checker needs to compare tokens that were never meant to match.

| Finding | Severity | Meaning |
|---|---|---|
| `THEME_DRIFT` | FAIL | a surface's value for an anchor disagrees with `palette.py` — a partial retune |
| `THEME_MISSING` | FAIL | a surface declares no block for one of the five themes — the switcher would land on an unstyled page |
| `THEME_SOURCE_MISSING` | FAIL | a file that draws the themes moved or vanished |
| `THEME_OWNER_MISSING` | FAIL | `palette.py` is absent — nothing to check against |
| `THEME_ANCHOR_ABSENT` | WARN | a surface declares the theme but not that token — the anchor can't be verified there |

**Why FAIL, not WARN.** Unlike a dead diagram path, a drifted palette ships: it renders wrong on every page that surface generates, and it is invisible in review because each file looks internally consistent. The fix is also unambiguous — change `palette.py` first, then propagate — so there is nothing for a human to adjudicate.

**Under-claiming.** It owns the anchors *only*. Star gradients, ring and moon colours, chart axes and per-status glyph hues stay owned by whichever file draws them, because nothing cross-checks those — claiming them would be a fake wall. The `is_light` split (`daylight`, `sandstone`) is declared here too, since the paper-chart treatment depends on it.

It also prints a per-domain **tag census** (`review 11 · lint 4 · test 2 …`) — the at-a-glance view of how much of each contract is real walls vs reviewer judgment. HTML comments are stripped before scanning: the enforcement legend legitimately spells out the tag grammar (`[test:name]` etc.) inside a comment, and commented-out template blocks are not active contract. `/triage` runs this per `.gravity/` project alongside `consistency`; `selftest` proves both checkers.

## Scenarios

| Command | Guards against | Folder |
|---|---|---|
| `/new-domain` | an orphaned domain — folder created but an index left unwired | `new-domain/` |
| `/new-spec` | a fabricated wall — a SPEC whose Gate/tags claim enforcement that doesn't exist | `new-spec/` |
| `/excavate` | a fabricated seam — a dead frontend call or orphaned mapper statement mapped as a live Boundary-Map row (or real seams missed) | `excavate/` |
| `/ship` | a dishonest ship — the junction moves but CONTEXT.md keeps a task-shaped Next Step, or the PROJECTS.md row stays in active/ | `ship/` |
| `/patch-slice` | an undisciplined patch — edits before the anchor, a piped gate lying green, thrash past N=3, a rollback that loses gitignored state or the execution log | `patch-slice/` |

Beyond `expect_domain`/`require_files`/`spec_honesty`, `expect.json` supports two content assertions: **`require_content`** (`{file: [substrings]}` — evidence that must have been mapped somewhere) and **`forbid_in_section`** (`{file: {"## section": [substrings]}}` — e.g. the dead call may appear as a *finding* but never inside `## Boundary Map`). HTML comments are stripped before the forbid check.

Add the next one (`/init-project`, `/adopt-gravity`) by copying the `new-domain/` shape: a clean fixture, an `expect.json`, a `SCENARIO.md` replay recipe. `selftest` automatically validates every `*/fixture` (consistency + spec honesty); a fixture with **no** `.gravity/` is skipped as virgin input — it's the raw material for a command that *creates* the `.gravity/` (`/excavate`), or a **workspace tree** rather than a project (`ship/` — asserted by `check.py workspace`, not `cmd_scenario`).

## The workspace check (`check.py workspace`)

The workspace-level twin of `consistency`: it judges the **facts** emitted by `.claude/scripts/scan_workspace.py` (tiers on disk · PROJECTS.md rows · CONTEXT.md health · adoption stamps) and never re-scans disk itself — one scanner, many callers (`/dashboard` and `/triage` format the same JSON). Staleness is deliberately a *fact* (days_ago), never a *finding* — judging age is a human decision, and date-dependent checks would rot fixtures.

| Finding | Severity | Meaning |
|---|---|---|
| `MULTI_TIER` | FAIL | one name junctioned into two tiers at once |
| `INDEX_MISSING_ON_DISK` | FAIL | a PROJECTS.md row with no folder/junction anywhere |
| `INDEX_WRONG_TIER` | FAIL | row's section disagrees with the actual junction tier |
| `UNINITIALIZED` / `STENCIL` / `BLOAT` | WARN | CONTEXT.md missing · template leftovers · needs a prune (~80 lines / ~6 bullets) |
| `MISSING_TRIGGER` / `MISSING_BLOCKER` | WARN | stable Next Step isn't a reactivation trigger · dormant names no resume blocker |
| `REPO_ORPHAN` / `NOT_INDEXED` | WARN | repos/ folder with no junction · tiered project with no index row |
| `ADOPTION_STALE` / `ADOPTION_MISSING_ROW` | WARN | adoption-table cell ≠ disk · gravity project absent from the table (`scan_workspace.py --adoption-table` prints the correct table) |
| `MANUAL_BLOAT` | WARN | root CLAUDE.md over its word budget (5,500) — push detail down to `.claude/commands/` / HANDBOOK |

`selftest` proves this checker too: a healthy mini-workspace passes; three seeded drifts are each caught.

## The intake check (`check.py intake --project <path>`)

The `/intake` command's mechanical wall: it verifies every sheet under `docs/intake/` against the ritual's non-negotiables — the six required facts per item (filled, or an honest `OPEN: awaiting …`), routing on closed sheets, live route targets, and the bugs-are-never-a-domain rule. The agent's *judgment* (triage verdicts, dedupe, severity) stays unchecked — this asserts only what a sheet can't honestly lack. `selftest` proves it: an honest fixture sheet passes; five seeded drifts are each caught.

| Finding | Severity | Meaning |
|---|---|---|
| `BUGS_FOLDER` | FAIL | `.gravity/bugs/` exists — bugs route to owning-domain slice PLANs, never a domain |
| `INTAKE_UNROUTED` | FAIL/WARN | an item with no `→` destination: FAIL on a ✓-closed sheet (the Status is lying), WARN while still ○ triaging |
| `INTAKE_DEAD_ROUTE` | FAIL | the `→` line names a PLAN file that doesn't exist |
| `INTAKE_FIELD_MISSING` / `INTAKE_FIELD_UNFILLED` | WARN | one of the six required facts is absent · still a template stub |

## The given check (`check.py given --project <path>`)

The `/given` command's mechanical wall: nothing rots in the drop zone, every file in a `_given/` folder carries a provenance row, and the manifest never lies about what's on disk. Fidelity/privacy judgments stay the agent's; `private` rows are committed pointers to local-only files and are exempt from the ghost check. `selftest` proves it: an honest fixture passes; three seeded drifts are each caught.

| Finding | Severity | Meaning |
|---|---|---|
| `GIVEN_GHOST_ROW` | FAIL | a non-private manifest File row names a file that doesn't exist |
| `INBOX_UNROUTED` | WARN | a file sitting in `.gravity/_inbox/` — knowledge outside the system; run `/given` |
| `GIVEN_UNMANIFESTED` | WARN | a file in `_given/` with no manifest row — provenance unknown |

## The patch-loop check (the selftest's third half)

`/patch-slice`'s walls live in a script (`.claude/scripts/patch_slice.py`), not a checker — so its scenario is asserted differently: `selftest` **drives the script itself** over `patch-slice/fixture` through both fork branches. Green: preflight → anchor (SHA lands in the PLAN) → snap (SPEC-declared `state/data.txt`) → the fix + regression test → verify green → cleanup retires the snap. Red: a bad patch that also mangles the gitignored ledger → three red verifies (third exits **75**, the exhaustion wall) → four-proof rollback → the ledger is byte-identical again and the PLAN still tells the whole anchor→attempts→rollback story across the hard reset. Run it after editing `patch_slice.py`, the fixture, or `patch-slice.md`.
