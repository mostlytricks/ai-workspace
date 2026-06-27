# Agent Instructions

Use `CLAUDE.md` as the canonical operating manual for this workspace.

This file exists as a Codex-compatible discovery shim only. Do not duplicate
rules here; update `CLAUDE.md` when workspace agent instructions change.

If instructions conflict, follow this order:

1. Higher-priority system/developer instructions.
2. Explicit user instructions in the current conversation.
3. The nearest project `CLAUDE.md` / `CONTEXT.md`.
4. This workspace `CLAUDE.md`.