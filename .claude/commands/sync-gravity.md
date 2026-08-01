---
description: Bring one project up to the current gravity version — re-copy the protocol card, bump the router stamp, surface the changelog deltas that need human judgment. Mechanical parts applied; breaking changes reported, never auto-migrated.
argument-hint: <project-or-alias>
---

You are running `/sync-gravity` from `ai-workspace/` to bring project **`$ARGUMENTS`** up to the current gravity version. The mechanical layer (protocol card + stamp) is applied for the user; the judgment layer (rule changes a project must adapt to) is **reported as a checklist, never auto-applied**. Built so a weaker agent can't invent a version or silently "migrate" a project.

## Steps

1. **Resolve the project** via `.claude/scripts/resolve_project.py`. Not found → list candidates and stop.

2. **Read the versions — never invent them:**
   - **Target** = major.minor from the `gravity/VERSION` file.
   - **Router stamp** = the `> gravity: vX.Y` line in the project's root `CLAUDE.md` (v3: inside the fenced `<!-- gravity:router -->` block; pre-v3: a bare blockquote).
   - **Card stamp** = the `gravity protocol · vX.Y` line in `.gravity/GRAVITY.md` (`.gravity/` projects only).

   If the project has **no router stamp at all**, stop and say so — an unstamped project hasn't adopted gravity's versioned conventions; the fix is adoption (`/adopt-gravity`, or adding a light stamp by hand), not a sync. If both stamps already equal the target, report "already current" and stop.

3. **Read the delta from `gravity/CHANGELOG.md`** — every released section between the project's router stamp and the target (e.g. stamped `v1.2`, target `v1.5` → read `[1.3.0]`, `[1.4.0]`, `[1.5.0]`). Sort what you find into:
   - **Mechanical** — the card re-copy and stamp bump (step 4 does these).
   - **Judgment** — any *major*-worthy or convention-shape change the project may violate (renamed conventions, moved files, new required wiring). These become the step-6 checklist. Quote the changelog line; never paraphrase a rule from memory.
   - **Exception — the v4 machinery-dir rename** (`lib/`→`_lib/`, `observatory/`→`_observatory/`, `inbox/`→`_inbox/`, `given/`→`_given/`) has a dedicated mechanical migrator. When the project still has bare-named machinery dirs, offer `python .claude/scripts/migrate_gravity_v4.py <project>` (dry-run by default) **now, before step 4, from the still-clean worktree** — the migrator refuses a dirty tree, and step 4's `install_lib.py` would delete the old `lib/` before it could be `git mv`'d. On the user's yes, run it with `--apply` and **skip step 4 entirely**: the migrator subsumes the mechanical layer (renames + reference rewrites + lib reinstall + card re-copy + fence bump + consistency check + its own commit). On a no, proceed with step 4 as usual and leave the rename in the step-6 checklist.

4. **Apply the mechanical layer** (skip this step entirely if the v4 migrator ran in step 3 — it already did all of it):
   - `.gravity/` projects: re-copy `gravity/GRAVITY-PROTOCOL.md` → `.gravity/GRAVITY.md` (overwrite — the card is a verbatim copy by contract), delete the template's top comment block, fill the `v<X.Y>` stamp with the target version. **In the same breath, re-copy `gravity/GRAVITY-GUIDE.html` → `.gravity/GRAVITY.html` and `gravity/GRAVITY-GUIDE.ko.html` → `.gravity/GRAVITY.ko.html`** (overwrite, drop each top comment block, no stamps — the card carries the version for the family). They always move together: the same protocol written for the two audiences (and the two languages), and a project carrying some without the others is half-synced.
   - **Re-install the lib** — `python .claude/scripts/install_lib.py <project>` overwrites `.gravity/_lib/` with the current modules and re-stamps its `VERSION`. Same contract as the card: a **verbatim copy, never hand-edited per project**, so upgrading means re-copying. The script prints `lib <old> -> <new>`; quote that line in the report.
   - **Fenced (v3) projects:** rewrite the content **between the fence markers** in every root harness file that carries the block (`CLAUDE.md`, `AGENTS.md`, others) from `gravity/templates/GRAVITY.template.md` with the target version — identical in every file, never touching anything outside the fences.
   - **Pre-v3 projects (no fences):** bump the bare `> gravity: vX.Y` stamp only. The **v2→v3 router migration** (move the Doc Map / read-first table / Adding-a-domain sections out of root `CLAUDE.md` into `.gravity/ROUTER.md`, then replace them with the fenced block — see `/adopt-gravity` step 5) is a **judgment item**: offer it in the step-6 checklist with the concrete before→after, and perform it only on the user's yes.
   - Flat (non-`.gravity/`) projects get **only** the stamp bump — no card, no ceremony.

5. **Verify.** For `.gravity/` projects run `python .claude/scenarios/check.py consistency --project <path>` and confirm no `PROTOCOL_MISSING`/`PROTOCOL_STALE`/`LIB_MISSING`/`LIB_STALE`/`MACHINERY_UNMIGRATED` remains (other findings: report, don't fix here). Then reconcile the project's row in the `PROJECTS.md` **Gravity adoption** table (stamp + card columns).

6. **Report:** old → new versions, what was re-copied/bumped, and the **judgment checklist** from step 3 — each item as a one-line "changed in vX.Y: <quoted change> → check <what to look at in this project>". An empty checklist is a valid (and common) result for minor-only deltas. **Do not commit** — the diff is the user's review checkpoint.

## What NOT to do

- **Never invent or guess a version** — every version comes from `VERSION`, a stamp line, or a `CHANGELOG.md` heading.
- **Never auto-migrate a judgment item** — restructuring a project to satisfy a new convention is its own task, done with the user, not a side effect of a sync.
- **Never hand-edit the card's content, or anything in `.gravity/_lib/`** — both are always fresh copies of the distribution. A per-project patch to an installed module is drift the next sync silently overwrites; fix it in `gravity/lib/` and re-install.
- **Don't sync an unstamped or archived project** — adoption first; archives are read-only.
- **Don't commit** — with one exception: the v4 migrator commits its own rename by design (the rename must be the only thing in that commit); everything else stays uncommitted for the user's review.
