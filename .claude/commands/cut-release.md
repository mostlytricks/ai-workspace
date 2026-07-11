---
description: Cut a versioned release — context-aware (workspace root → bump gravity itself; a project name → bump that project). Runs the changelog + version-bump + commit + tag Change Order in the right order, stops before push. Built so the version is never invented and broken code is never tagged.
argument-hint: "[project-name]   (omit to release gravity itself)"
disable-model-invocation: true
---

You are running `/cut-release` from `ai-workspace/`. It performs **one release Change Order** against the correct target, in the correct order, and **stops before pushing** (the push is the user's call). The whole reason this command exists is to remove the foot-guns of a manual bump — wrong file bumped, hardcoded date, forgotten tag, releasing red code. So it is mostly a **verification procedure**: never invent a version, never tag a failing gate, never push.

Parse `$ARGUMENTS`:
- **empty** → target is **gravity itself** (the `ai-workspace` skeleton repo). Version source: root `VERSION` + tag on `ai-workspace`. Changelog: root `CHANGELOG.md`.
- **`<project>`** → target is **that project**. Locate it under `active/`, `dormant/`, or `repos/` (run all git commands *inside* the project dir so they hit its real `.git`). Version source: its manifest (`package.json` `version`, or `pyproject.toml` / `Cargo.toml` / a `VERSION` file — whatever it uses). Changelog: `<project>/CHANGELOG.md`.

## Step 1 — Resolve target & current version (don't guess)

1. **Find the version source** for the target (above). Read the current version from it.
2. **Cross-check against git:** `git describe --tags --abbrev=0` (in the right repo). 
   - If the manifest/VERSION and the latest tag **disagree** (e.g. file says `0.2.0`, latest tag is `v0.3.0`), **STOP and surface it** — that's drift the user must resolve, not something you pick.
   - If there are **no tags yet**, this is the **first cut** — the current manifest/VERSION value *is* the version to release (don't bump it); say so.
3. **Confirm the changelog exists.** If the target has **no `CHANGELOG.md`**, do **not** fabricate a release: stop and offer to establish the light layer first (seed `CHANGELOG.md` + the `## Releasing` section — workspace CLAUDE.md §2 / the project pattern). Resume once it exists.

## Step 2 — Determine the bump (propose from evidence, then CONFIRM)

Read the changelog's `[Unreleased]` block. **If it's empty, STOP** — there's nothing to release.

Propose major/minor/patch **from what's actually in `[Unreleased]`**, then **ask the user to confirm** — "is this breaking?" is judgment, never assume:

- **Gravity target:** major = *a rule projects depend on breaks* (renamed/moved convention, changed doc-ownership boundary, a restructure existing projects would now violate); minor = new template / command / optional doc / additive rule; patch = clarification, tighter wording, typo/format.
- **Project target (post-1.0 SemVer):** major = breaking API/CLI/manifest-shape change; minor = new backward-compatible capability; patch = fix-only. **Pre-1.0** (`0.y.z`): a breaking change bumps the **minor**, a feature/fix bumps the patch.

State your proposed bump *with the one-line reason from the `[Unreleased]` evidence*, and the resulting version (e.g. "minor → `0.3.0`, because Unreleased adds a new `/api/search` capability"). **Wait for confirmation before writing anything.** On first cut (no prior tag), there is no bump — confirm the existing version instead.

## Step 3 — Run the gate (refuse to tag red code)

- **Project target:** find the real gate in `package.json` the way `/new-spec` does (`test`/`typecheck`/`lint` that exits non-zero), and run it. If it needs a server/fixture/env, note the precondition. **If the gate fails, STOP — do not tag.** A release of broken code is the exact bug this prevents. If the project genuinely has no automated gate, say so plainly and proceed (the user owns the risk).
- **Gravity target:** there is **no build gate** — say so honestly. Do a lightweight sanity pass instead: `[Unreleased]` has real content, `VERSION` matches the version you're about to cut, no obviously-unfilled stencil among the tracked skeleton. Don't invent a gate that doesn't exist.

## Step 4 — Apply the Change Order (the strict sequence)

Get the date from the system (`date +%F`) — **never hardcode it**. Then, in order:

1. **Changelog:** rename `## [Unreleased]` → `## [X.Y.Z] - <date>`, and insert a fresh empty `## [Unreleased]` above it. Update the compare/link reference lines at the bottom if present (`[Unreleased]: …compare/vX.Y.Z...HEAD`, add `[X.Y.Z]: …releases/tag/vX.Y.Z`).
2. **Version source:** set the manifest/`VERSION` to `X.Y.Z` (skip on a first cut where it already matches).
3. **Commit** — staged to the target repo only: gravity → `gravity vX.Y.Z`; project → `release: vX.Y.Z`.
4. **Tag** — annotated: `git tag -a vX.Y.Z -m "vX.Y.Z"` (in the target repo).
5. **STOP.** Do **not** push.

## Step 5 — Report & hand off the push

Report: target repo, **old → new** version, the confirmed bump + its one-line reason, the gate result (or "no gate"), the files changed, and the **exact push command** for the user to run:

```
git push && git push --tags          # project: run inside the project dir
```

If the target was **gravity** and the bump was minor/major, add a note: *projects carry a `> gravity: vX.Y` stamp that may now be stale — `/triage` flags the drift; re-sync each project's skeleton when ready.*

## What NOT to do

- **Never invent or hardcode** the version or the date — derive the version from current + confirmed bump; read the date from the system.
- **Never push.** The command stops at the tag; the push is the user's checkpoint.
- **Never tag a failing gate** (project target) or an empty `[Unreleased]`.
- **Never silently pick** when the version file and the latest tag disagree — surface the drift and stop.
- **Never fabricate a release** for a target with no `CHANGELOG.md` — establish the light layer first.
- **Don't bump on a first cut** — the existing manifest/VERSION value is the version; just cut it.
