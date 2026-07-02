# fixture-app

A minimal `.gravity/` project used only as the **golden input** for the `/new-spec` golden-scenario (`.claude/scenarios/new-spec/`). Not a real project — do not promote, junction, or build it.

It ships one fully-wired domain (`model`) with real code, a real gate (`npm run lint:model`), and named tests — but **no `SPEC.md`**. The scenario copies this fixture, runs `/new-spec` to author the SPEC, and `check.py` asserts the SPEC exists, stays wired, and is *honest*: its Gate and every enforcement tag verify against `package.json` + `tests/`.
