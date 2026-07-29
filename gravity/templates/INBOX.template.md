<!--
INBOX.template.md — the drop-zone door. Copy to <project>/.gravity/inbox/README.md
at adoption (/adopt-gravity) or on first /given run.

Why a README in an empty folder: the inbox used to be created lazily, by the
command that empties it — so on a fresh project the user had a file in hand and
NO directory that said "put it here". A door that appears only after you knew
the magic word is not a door. This file is the sign on it, and the project's
.gitignore keeps it visible in clones (`.gravity/inbox/*` + `!README.md`) while
everything you drop stays untracked until routing decides its privacy.
-->

# Inbox — the drop zone

**Put files here.** Anything the project was *told* rather than *decided*:
data dictionaries, DB metadata exports, business-rule sheets, vendor docs,
ERD exports, meeting notes that carry decisions.

Then run **`/given <project>`** — it proposes where each file lives (which
domain, how it's rendered, whether it may be committed), writes provenance
rows, and empties this folder. Nothing in here reaches git before that
routing decides its privacy class.

Two kinds of material have a more specific door — you can still drop them
here and `/given` will route them, or go direct:

| Material | Direct destination |
|---|---|
| **DB evidence** — DDL scripts you scraped (`CREATE TABLE` from SQL Developer / DBeaver / migrations) or the metadata CSVs a DBA exports | `.gravity/integration/structural/db/` (DDL under `ddl/`) beside its `MANIFEST.md`; then `python .gravity/lib/scan_db.py` reads it. No row data is ever needed |
| **Bug / issue report batches** | not files — run `/intake <project>`, which builds the dated sheet |

Rules of the door:
- **This folder is never committed** (only this README is tracked).
- **The inbox ends empty** — after routing, a file lives in a `given/` layer
  with a manifest row, or it has an explicit `OPEN:` row saying why not.
- Don't work *from* here: agents read the routed copy, never the drop zone.
