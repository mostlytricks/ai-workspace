<!--
  WALKTHROUGH.template.md — the "what got done + proof" doc. Antigravity's ARTIFACT_TYPE_WALKTHROUGH,
  adapted to ai-workspace. OPT-IN and per-change, not one of the four live clocks (CLAUDE/CONTEXT/PLAN/MISSION).

  What it is: the trust artifact that closes a phase or feature. It pairs the narrative of what
  changed with the *evidence* it works (commands run + output, and screenshots for UI work). It's
  the human-reviewable face of agent work — the thing someone reads to TRUST the change without
  re-deriving it.

  Where it lives: repos/<project>/docs/walkthroughs/<YYYY-MM-DD>-<domain>-<slug>.md (one file per shipped slice).
  The flat dated log IS the timeline (history is read by time/event, not subject) — so walkthroughs are NOT
  foldered into .gravity/<domain>/ like the live docs. Instead the <domain> in the slug + the Domain(s) header
  below make them per-domain queryable (glob `*-<domain>-*`). A cross-cutting slice lists every domain it
  touched rather than being forced into one folder.
  Lifecycle: APPEND-ONLY. Unlike CONTEXT.md (overwritten each session), a walkthrough is written once
  when a slice ships and then frozen — it's a dated record, not live state. git versions it; don't edit
  old ones to reflect new reality (write a new walkthrough instead).

  When to bother: ships a phase from IMPLEMENTATION_PLAN.md, lands a reviewable feature, or does UI work
  worth a screenshot. Skip for trivial fixes — the mission warns against ceremony that doesn't pay.
  The CONTEXT.md "Completed" bullet for the same work should LINK here rather than restating it.
-->

# Walkthrough — <feature / phase name>

> Closes: **Phase N** of `IMPLEMENTATION_PLAN.md` — or, in a `.gravity/` project, a domain's `<domain>/PLAN.*.md` slice (or the feature it implements).
> Domain(s): `<domain>` — the subject(s) this slice touched; comma-list if cross-cutting. Matches the slug.
> Date: YYYY-MM-DD · Branch `<branch>` · Commit `<sha>` (or "uncommitted — in working tree").

## What changed

The narrative, in a few lines: what now exists that didn't before, and the shape of the change.
Link the touched files so a reviewer can jump in.

- **[NEW]** `path/to/file` — <what it does.>
- **[MODIFY]** `path:line` — <what changed and why.>

## How it was verified

The actual evidence — what was run and what came back. Paste real output, not a claim that it passed.

```bash
$ <gate / verification command>
<the real result — typecheck clean, N/N tests, build ok>
```

- [x] <verification step from the plan> — <observed result>
- [x] <endpoint / behavior checked> — <what it returned>

### Screenshots (UI work)

For visual changes, attach proof (Antigravity captures `verify_*.webp` per check). Reference images
committed under `docs/walkthroughs/img/`.

![<what this shows>](img/<file>.png)

## Outcome

What is now true that wasn't before — the one-paragraph "state of the world" after this slice.

## Follow-ups / known gaps

Anything deliberately left out, a rough edge, or a thread for next time. Feeds back into
`IMPLEMENTATION_PLAN.md` "Open questions" or the next phase. Write "none" if clean.

- <follow-up, or "none">
