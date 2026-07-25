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

## Pack status

| P | File | Answers | Status |
|---|---|---|---|
| P1 | `tables-columns.csv` | table/column inventory + **comments** (the semantics) | OPEN: not collected |
| P1 | `constraints.csv` | PK/FK/UK — the **entity graph** (vertical-domain clustering) | OPEN: not collected |
| P2 | `db-source.sql` | procedures/functions/packages/views/triggers — queries living **in** the DB | OPEN: not collected |
| P2 | `grants.csv` | which account (→ which service) can touch which tables | OPEN: not collected |
| P2 | `rowcounts.csv` | live vs dead tables (`NUM_ROWS`, `LAST_ANALYZED`) | OPEN: not collected |
| P3 | `activity.csv` | runtime truth — actually-executed SQL per module/schema | OPEN: needs DBA (`V$SQL`/AWR) |
| — | `docs/` | human artifacts: ERD exports, table-definition sheets, interface defs | OPEN: none gathered |

Set each row to `present (<date>)` as files land. Human `docs/` are **claims to verify** against the CSVs, not evidence by themselves.

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
