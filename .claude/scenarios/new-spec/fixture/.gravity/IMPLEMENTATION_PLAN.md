# fixture-app — Implementation plan & resume sheet

> One-line working scenario: a minimal project that exists only to test `/new-spec`.
> Branch `main` · last updated 2026-07-02.

## Status right now

Fixture with one wired domain (`model`) — real code + a real gate, no SPEC yet.

```
roadmap:  1 (next)
goal:     stay a clean, minimal, fully-wired .gravity/ project for the golden-scenario
```

## Domain status spine

`○ planned · ◑ building · ✓ shipped`

| Domain | Status | Owns |
|---|---|---|
| `model` | ◑ | the data model — record shape + validation |

## Phase roadmap

### Phase 1 — SPEC the model domain · next
Author `.gravity/model/SPEC.md` from the template with honest tags. (This is the scenario's agent step.)

## Locked decisions

- This is a test fixture — keep it minimal and fully wired.

## The gate

`npm run lint:model` (validates `data/*.json`, exits non-zero) + `npm test` (`node --test tests/`).
