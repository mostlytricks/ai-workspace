# Runbook

<!-- Per-project stencil for OPERATIONS knowledge — how it deploys, where it runs, how it
     recovers. Copy to <project>/RUNBOOK.md (flat projects) or <project>/.gravity/RUNBOOK.md
     (.gravity/ projects — route it from the Doc Map). Recognized only when present and
     NEVER mandated: only for projects that deploy/run somewhere beyond `npm run dev` —
     skip it for local tools, libraries, and scripts.
     The ownership test (workspace CLAUDE.md §6): "would you need this at 2am when it's
     down?" If yes, it lives here — not in your head, not in CONTEXT.md.
     Rate of change: on deploy-shape changes (rare) — like CLAUDE.md, not like CONTEXT.md.
     Delete sections that don't apply; keep every command runnable AS WRITTEN in the
     target environment (if production is GitHub-less or offline, the steps must be too).
     Delete this comment when filled. -->

Operations reference for anyone (human or agent) who has to deploy, check, or revive this project. Everything here must be **runnable as written** — a runbook that requires tribal knowledge to execute is a diary, not a runbook.

---

## Where it runs

| Env | Host / platform | URL / entry | Who uses it |
|---|---|---|---|
| prod | <FILL: e.g. `svr-web-01`, k8s ns, IIS site, a scheduled task on the office PC> | <FILL: URL / port / path> | <FILL: the real consumers> |
| staging | <FILL — delete the row if none> | | |

## Deploy

<!-- How a change gets from this repo to running. Exact commands in order, what triggers
     them (push? manual? CI job name?), and roughly how long until it's live. -->

1. <FILL: build/package command>
2. <FILL: ship step — scp/rsync/pipeline/copy to the air-gapped share>
3. <FILL: activate step — restart command, reload, service name>

Trigger: <FILL: on tag? manual? who may run it?> · Takes: <FILL: ~minutes> · Deploy window/constraints: <FILL or delete>

## Config & secrets

<!-- POINTERS ONLY — env-var names, vault paths, config file locations per env.
     Never values. Same rule as CLAUDE.md: a secret in a doc is a leak. -->

- Config lives at: <FILL: path per env>
- Secrets: <FILL: names + where they're issued/stored, e.g. `DB_PASSWORD` via <vault/team>> — **values never in this file**
- Differences between envs worth knowing: <FILL or delete>

## Healthy looks like

<!-- The checks that prove it's up — and the first place to look when it isn't. -->

- <FILL: check command / URL> → expect <FILL: status/output>
- Logs: <FILL: where, and the one line/pattern that means trouble>
- First place to look when it's down: <FILL: the usual suspect, honestly>

## Rollback

<!-- How to revert a bad deploy. If the answer is "redeploy the previous version",
     say exactly how the previous version is identified and retrieved. -->

1. Previous good version is found by: <FILL: tag scheme / kept artifact / backup path>
2. <FILL: the revert steps, same rigor as Deploy>
3. Verify with the **Healthy looks like** checks above.

## Dependencies

<!-- What this project needs at runtime and what breaks when each is down. -->

| Depends on | What breaks without it | Owner / contact |
|---|---|---|
| <FILL: DB / API / share / license server> | <FILL: the symptom you'd actually see> | <FILL or —> |

---

<!-- This file is operations identity — it changes on deploy-shape changes, rarely.
     In-flight incidents and one-off fixes belong in CONTEXT.md (now) or a
     walkthrough (proof), not here. -->
