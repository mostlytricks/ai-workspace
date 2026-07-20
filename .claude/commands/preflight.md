---
description: Assemble the pre-change packet for one domain — the ordered read-first list (integration gate, the domain SPEC, coupled domains from live doc cross-references, open PLANs), the walls (runnable gate, contract census), and honest warnings (unfenced, freeform, stale CONTEXT). Run before changing a domain; then actually read what it lists.
argument-hint: <project-or-alias> <domain>
allowed-tools: Read, Glob, Grep, Bash(python .claude/scripts/scan_project.py:*), Bash(python .claude/scripts/run_gate.py:*)
---

You are running `/preflight` from `ai-workspace/`. It turns the navigation discipline of workspace CLAUDE.md §6 ("load the SPEC before changing a domain; integration first on boundary changes") from prose an agent must remember into a **mechanically assembled packet**. Same scanner as the observatory (`scan_project.py`) — the packet and the human's page can't disagree.

## Run it

Parse `$ARGUMENTS` as `<project> <domain>`, then:

```bash
python .claude/scripts/scan_project.py <project> --preflight <domain>
```

- Unknown domain → the script lists the known ones; relay, don't guess.
- The packet is **pointer-first by design**: it gives paths, census numbers, and warnings — it never restates rule prose. The SPEC stays the one home.

## Then actually do the preflight (the packet is a checklist, not a report)

1. **Read the files it lists, in the order it lists them** — the integration SPEC line is conditional (only when the change crosses a boundary); the domain SPEC is not. Coupled-domain SPECs matter the moment your change touches anything the cross-references cover.
2. **Relay the warnings** to the user before starting work, briefly: `UNFENCED` (offer `/new-spec`), `freeform sheet` (census is tags-only), `STALE` CONTEXT (the next-step may be outdated), unbound Behavioral Contract lines, template FILLs.
3. **When the work is done**, honor the packet's "Before you finish" block: run the gate (`run_gate.py` — it exits with the gate's own code and refuses honestly with exit 2 when there is no gate), follow the integration Change Order if a boundary moved, and update CONTEXT.md.

## What NOT to do

- Don't treat the packet as a substitute for reading the SPEC — it's the map, not the territory.
- Don't proceed silently into an `UNFENCED` domain — say so, and offer to fence it first.
- Don't hand-parse a Gate line out of a SPEC when `run_gate.py` exists — that's the exact misread this tooling removes.
- Don't edit the packet's facts into docs anywhere — it's ephemeral stdout, regenerated from the docs every run.
