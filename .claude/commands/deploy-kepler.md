---
description: Propagate the Kepler skeleton to a sibling workspace on another drive — version-compared, dry-run first, local files untouchable by construction.
argument-hint: <target-workspace-path>
---

You are running `/deploy-kepler` from `ai-workspace/` to update the sibling Kepler workspace at `$ARGUMENTS` (the user maintains several per-purpose workspaces on different drives; they were created as plain copies).

All mechanics live in one deterministic script — **do not** copy files by hand.

## Do this

1. **Dry-run first, always:**

```bash
python .kepler/scripts/deploy_kepler.py "$ARGUMENTS"
```

2. **Relay the report** — source commit vs target stamp, and the four buckets: `new` / `update` (safe — target untouched since last deploy) / `local-modified` (the sibling's owner edited it) / `orphaned` (a previous deploy shipped it; the source no longer does).
3. **Confirm with the user before `--apply`** — especially the flags:
   - `--force` overwrites *local-modified* files. On a **first deploy** (no stamp) every difference reads as local-modified because provenance is unknown — show the list, get an explicit yes.
   - `--prune` deletes *orphaned* files.
4. Apply what was agreed, relay the result line, and remind: **`/sync-gravity` per project in that workspace** is the user's own next step (gravity side is deliberately not this command's job); `bootstrap.py` only if tiers/junctions there are broken.

## What the script guarantees (don't re-derive, don't re-check by hand)

- The manifest is `git ls-files` at the source HEAD — `.claude/settings.json`, `PROJECTS.md`, `repos/`, and the tier folders are **outside it by construction** and can never be touched.
- Kepler's version *is* the skeleton commit (hash + date); the target's `.kepler-deployed` stamp records what was last deployed, which is how *update* is told apart from *local-modified*.
- It refuses a dirty source (commit first — a deploy must be reproducible from a commit) and refuses a target that overlaps the source tree.

## What NOT to do

- **Never run `--apply --force` without showing the modified list first** — that list is someone's (usually the user's own) local work on the other drive.
- **Do not touch the target's `.claude/settings.json` or `PROJECTS.md`** for any reason — not even to "helpfully fix" them; they are that workspace's private state.
- **Do not run gravity-side syncs from here** — `/sync-gravity` runs *in* the target workspace, per project, at the user's initiative.
