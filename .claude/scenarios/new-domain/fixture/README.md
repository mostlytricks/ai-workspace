# fixture-app

A minimal `.gravity/` project used only as the **golden input** for the `/new-domain` golden-scenario (`.claude/scenarios/new-domain/`). Not a real project — do not promote, junction, or build it.

It ships one fully-wired domain (`model`). The scenario copies this fixture, runs `/new-domain` to add a second domain, and `check.py` asserts the new domain is wired into all four registry indexes with nothing orphaned.
