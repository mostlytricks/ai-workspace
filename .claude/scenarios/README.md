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

## How parsing works (and its limits)

`check.py` uses **heuristic slug-match**: a domain is "wired" into an index region if its kebab-case slug appears in that region (the Doc Map code block, the router table, the MISSION rows, the PLAN status spine). Fixtures are author-controlled, so this is robust enough. If real projects start tripping it (a slug that's also a common English word, say), harden with machine-readable anchors in the templates — not before.

Severity: missing wiring is a **FAIL** (the orphaned-domain bug). A `.gravity/<slug>/` route pointing at a non-existent folder, or a domain folder with no `PLAN*.md`, is a **WARN** (templates legitimately ship example rows like `integration/`).

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

It also prints a per-domain **tag census** (`review 11 · lint 4 · test 2 …`) — the at-a-glance view of how much of each contract is real walls vs reviewer judgment. HTML comments are stripped before scanning: the enforcement legend legitimately spells out the tag grammar (`[test:name]` etc.) inside a comment, and commented-out template blocks are not active contract. `/triage` runs this per `.gravity/` project alongside `consistency`; `selftest` proves both checkers.

## Scenarios

| Command | Guards against | Folder |
|---|---|---|
| `/new-domain` | an orphaned domain — folder created but an index left unwired | `new-domain/` |
| `/new-spec` | a fabricated wall — a SPEC whose Gate/tags claim enforcement that doesn't exist | `new-spec/` |

Add the next one (`/init-project`, `/adopt-gravity`) by copying the `new-domain/` shape: a clean fixture, an `expect.json`, a `SCENARIO.md` replay recipe. `selftest` automatically validates every `*/fixture` (consistency + spec honesty), so a rotted fixture can't silently make its scenario prove nothing.
