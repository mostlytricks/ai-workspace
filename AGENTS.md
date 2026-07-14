# Agent Instructions

**`CLAUDE.md` is the canonical operating manual for this workspace.** Everything in this file is *routing*, not rules — do not duplicate rules here; when workspace instructions change, change `CLAUDE.md`.

## Required reading protocol — do this, in this order

1. **Before any work:** read the workspace `CLAUDE.md` — tiers, storage invariants, git boundaries, the doc system, the command index. Do not operate on the workspace without it.
2. **When entering a project** (under `active/`, `stable/`, `dormant/`, or `repos/`): switch to *that project's* protocol — read its `AGENTS.md`/`CLAUDE.md` and `CONTEXT.md`; if it has a `.gravity/` directory, read `.gravity/GRAVITY.md` before touching anything inside `.gravity/`, and the relevant `.gravity/<domain>/SPEC.md` before changing a domain.
3. **Before ending a project session:** update that project's `CONTEXT.md` (Completed / Current State / Next Step). A session that doesn't update it is incomplete.

## If instructions conflict

1. Higher-priority system/developer instructions.
2. Explicit user instructions in the current conversation.
3. The nearest project `CLAUDE.md` / `CONTEXT.md` (and its `.gravity/` protocol card + SPECs).
4. This workspace `CLAUDE.md`.
