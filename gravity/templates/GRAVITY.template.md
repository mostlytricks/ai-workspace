<!--
GRAVITY.template.md — the THIN ROUTER block (gravity v3): the ONLY thing gravity
writes into a project's root harness files (CLAUDE.md, AGENTS.md, and — when the
project uses those agents — GEMINI.md, .cursorrules, …). The block is IDENTICAL in
every file and machine-managed: /adopt-gravity inserts it (right below the file's
title line, or at the top of a file with none); /sync-gravity rewrites ONLY what
sits between the fence markers. Everything outside the fences belongs to the
project — gravity never touches it. That is the whole adoption footprint: the full
Doc Map + read-first table live one hop away in .gravity/ROUTER.md
(ROUTER.template.md), the protocol itself in .gravity/GRAVITY.md.

Fill v<X.Y> with major.minor from the workspace gravity/VERSION (never invent it).
Delete this comment when copying — only the fenced block below goes into the file.
-->

<!-- gravity:router v<X.Y> — managed by /adopt-gravity + /sync-gravity; do not hand-edit inside the fences -->
> **gravity: v<X.Y>** — docs live in `.gravity/`. Before working here, read `.gravity/GRAVITY.md`
> (the protocol: doc kinds + rates, navigation discipline) and `.gravity/ROUTER.md` (the Doc Map +
> what to read before changing what). Session ritual: read `CONTEXT.md` first; update it before stopping.
<!-- /gravity:router -->
