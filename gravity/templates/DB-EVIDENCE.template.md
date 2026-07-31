<!--
DB-EVIDENCE.template.md — the DB evidence pack: checklist + manifest.
Copy to `.gravity/integration/structural/db/MANIFEST.md` in the project (or hub)
being excavated. It is BOTH the shopping list you hand a DBA and the living
manifest of what the pack currently contains — /excavate consumes whatever is
`present` and leaves the rest as honest `OPEN:` lines.

Why it exists: when services carry no readable queries (dynamic/string-built
SQL, logic in stored procedures, a shared DB touched by repos you can't see),
code archaeology can't trace the DB side of the seams. The missing evidence
comes from the database's own METADATA — collected offline, as flat files, by
a read-only account. The agent never needs DB access.

WHAT THE MANIFEST IS FOR (say this to the human handing files in):
the manifest is what stops the analysis from claiming coverage it doesn't
have. Every row is `present (date)` or `OPEN:`, so when a Boundary Map says
"clustered from constraints.csv" anyone can check whether that file was ever
collected. Without it, "we analyzed the DB" is unfalsifiable — the analysis
sounds equally confident whether it saw six files or one. The manifest is the
difference between a finding and a vibe; `scan_db.py` reads it the same way.

WHY CSVs FOR TABLES AND .sql FOR SOURCE: not a preference. The tabular files
are read by machines (`.gravity/_lib/scan_db.py` parses them into the entity
graph), so they must be structured; `db-source.sql` is code a human reads, so
it stays code. Same audience split as SPEC.md vs ARCHITECTURE.html.

Rules:
- **Metadata only, never row data.** Structure, comments, constraints, source,
  grants, activity stats — no table contents, so no PII leaves the DB.
- **Partial is fine.** Every item is optional; analysis starts with whatever
  exists. P1 alone unblocks most vertical-domain work. Absent = `OPEN:`.
- **Regenerable, never hand-edited** (except this manifest's status column).
  Re-run the queries after schema change; don't patch the CSVs.
- Fill `&SCHEMAS` with the application schema owner(s), not SYS/SYSTEM.
-->

# DB Evidence Pack — <system/project>

**Database:** <vendor + version, e.g. Oracle 19c> · **Schemas:** <OWNER1, OWNER2>
**Collected:** <YYYY-MM-DD> by <who> using account <read-only user> · **Refresh:** re-run all queries; never hand-edit CSVs.

## What can you actually get? (start here — cheapest first)

The analysis starts from whichever of these you can obtain **today**; nothing blocks on the ideal pack. **No option ever involves row data** — everything below is structure, the database's own catalog of your tables.

1. **DDL you scrap yourself** → `ddl/*.sql`. `CREATE TABLE` scripts from SQL Developer / DBeaver (*export DDL*), or the repo's migration files. Needs no DBA, no special account — this is the most commonly obtainable artifact, and it carries the load-bearing facts (tables, columns, PK/FK, comments). Caveat the tool states for you: scripts can drift from the deployed schema and cover only what you scraped.
2. **The two P1 CSVs** — the live data dictionary exported by any read-only account (queries below). Stronger than DDL: it's what the database *actually* has, complete.
3. **The rest of the pack** (P2/P3) — each file below sharpens one question; collect opportunistically.

## Pack status

| P | File | Answers | Status |
|---|---|---|---|
| P1 | `ddl/*.sql` | **CREATE TABLE scripts** — the scrap-it-yourself equivalent of the two P1 CSVs (graph + inventory + comments) | OPEN: not collected |
| P1 | `tables-columns.csv` | table/column inventory + **comments** (the semantics) | OPEN: not collected |
| P1 | `constraints.csv` | PK/FK/UK — the **entity graph** (vertical-domain clustering) | OPEN: not collected |
| P2 | `db-source.sql` | procedures/functions/packages/views/triggers — queries living **in** the DB | OPEN: not collected |
| P2 | `grants.csv` | which account (→ which service) can touch which tables | OPEN: not collected |
| P2 | `rowcounts.csv` | live vs dead tables (`NUM_ROWS`, `LAST_ANALYZED`) | OPEN: not collected |
| P3 | `activity.csv` | runtime truth — actually-executed SQL per module/schema | OPEN: needs DBA (`V$SQL`/AWR) |
| — | `docs/` | human artifacts: ERD exports, table-definition sheets, interface defs | OPEN: none gathered |

The graph needs **one of** `ddl/` or `constraints.csv`; when both exist the dictionary wins and DDL disagreements are reported as drift, never merged silently.

Set each row to `present (<date>)` as files land. Human `docs/` are **claims to verify** against the CSVs, not evidence by themselves.

**Where to put the files:** in this directory, beside this manifest (or drop them in `.gravity/_inbox/` and `/given` routes them here). **As soon as anything lands:** `python .gravity/_lib/scan_db.py` — it reads whatever is present, derives candidate vertical domains + seams from the FK graph, and reports every absent file as `unknown`, never as zero. `constraints.csv` is the one load-bearing file; without it no graph can be derived at all.

## Collection queries (Oracle)

Run as a read-only account; spool each to CSV with a header row (`SET MARKUP CSV ON` in SQL*Plus, or export from SQL Developer).

**P1 — `tables-columns.csv`**
```sql
SELECT c.owner, c.table_name, c.column_id, c.column_name, c.data_type,
       c.data_length, c.nullable, tc.comments AS table_comment,
       cc.comments AS column_comment
FROM   all_tab_columns c
LEFT JOIN all_tab_comments tc ON tc.owner = c.owner AND tc.table_name = c.table_name
LEFT JOIN all_col_comments cc ON cc.owner = c.owner AND cc.table_name = c.table_name
                              AND cc.column_name = c.column_name
WHERE  c.owner IN ('&SCHEMAS')
ORDER  BY c.owner, c.table_name, c.column_id;
```

**P1 — `constraints.csv`**
```sql
SELECT c.owner, c.table_name, c.constraint_name, c.constraint_type,
       cc.column_name, cc.position, c.r_owner,
       rc.table_name AS referenced_table
FROM   all_constraints c
JOIN   all_cons_columns cc ON cc.owner = c.owner AND cc.constraint_name = c.constraint_name
LEFT JOIN all_constraints rc ON rc.owner = c.r_owner AND rc.constraint_name = c.r_constraint_name
WHERE  c.owner IN ('&SCHEMAS') AND c.constraint_type IN ('P','R','U')
ORDER  BY c.owner, c.table_name, c.constraint_name, cc.position;
```

**P2 — `db-source.sql`** (three spools appended into one file is fine)
```sql
SELECT owner, type, name, line, text FROM all_source
WHERE  owner IN ('&SCHEMAS') ORDER BY owner, type, name, line;
SELECT owner, view_name, text FROM all_views WHERE owner IN ('&SCHEMAS');
SELECT owner, trigger_name, table_name, trigger_body FROM all_triggers
WHERE  owner IN ('&SCHEMAS');
```

**P2 — `grants.csv`** — plus, per service, note the DB account its datasource config uses (that mapping lives in each service's config, not the DB).
```sql
SELECT grantee, owner, table_name, privilege FROM all_tab_privs
WHERE  owner IN ('&SCHEMAS') ORDER BY grantee, owner, table_name;
```

**P2 — `rowcounts.csv`**
```sql
SELECT owner, table_name, num_rows, last_analyzed FROM all_tables
WHERE  owner IN ('&SCHEMAS') ORDER BY owner, table_name;
```

**P3 — `activity.csv`** — needs DBA-level views; ask for a representative window (a business day minimum). If refused, the app-side fallback is enabling MyBatis SQL logging / p6spy in a test environment while exercising the app.
```sql
SELECT parsing_schema_name, module, sql_id, executions,
       DBMS_LOB.SUBSTR(sql_fulltext, 3000, 1) AS sql_text
FROM   v$sql
WHERE  parsing_schema_name IN ('&SCHEMAS')
ORDER  BY executions DESC;
```

*Non-Oracle:* the same pack maps to `information_schema` (+ `pg_catalog` / `pg_stat_statements` on PostgreSQL, `performance_schema` on MySQL) — same files, same priorities.

## OPEN items

- OPEN: <anything above still missing, and who/what it's waiting on>
