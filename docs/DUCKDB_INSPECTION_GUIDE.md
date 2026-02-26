# DuckDB Inspection Guide (`oea.duckdb`)

This guide shows how to inspect what is in:

- `oss_framework/data/oea.duckdb` (the OSS Framework dbt/mart database)

It also helps you avoid confusing it with:

- `aeries_to_duckdb.duckdb` (a separate root-level database with different schemas)

---

## 1) Quick sanity check: are you opening the right database?

From repo root (`/Users/flucido/projects/local-data-stack`):

```bash
uv run python - <<'PY'
import duckdb
paths=['aeries_to_duckdb.duckdb','oss_framework/data/oea.duckdb']
for p in paths:
    con=duckdb.connect(p, read_only=True)
    rows=con.execute("""
      select table_schema, count(*)
      from information_schema.tables
      where table_schema not in ('information_schema','pg_catalog')
      group by 1
      order by 1
    """).fetchall()
    print(f"\nDB: {p}")
    for schema, count in rows:
        print(f"  {schema}: {count}")
PY
```

Expected for `oss_framework/data/oea.duckdb` includes schemas like:

- `main_staging`
- `main_core`
- `main_features`
- `main_scoring`
- `main_main_analytics`

---

## 2) Open `oea.duckdb` in DuckDB CLI

From repo root:

```bash
duckdb oss_framework/data/oea.duckdb
```

If `duckdb` CLI is not installed:

```bash
brew install duckdb
```

---

## 3) Most useful SQL while exploring

### List all schemas

```sql
SELECT schema_name
FROM information_schema.schemata
ORDER BY 1;
```

### List all tables by schema

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
ORDER BY table_schema, table_name;
```

### Count tables per schema

```sql
SELECT table_schema, COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
GROUP BY table_schema
ORDER BY table_schema;
```

### Inspect columns for one table

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'main_core'
  AND table_name = 'fact_attendance'
ORDER BY ordinal_position;
```

### Row counts for all mart tables

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('main_staging','main_core','main_features','main_scoring','main_main_analytics')
ORDER BY table_schema, table_name;
```

Then run counts for each table you care about, for example:

```sql
SELECT COUNT(*) FROM main_core.fact_attendance;
SELECT COUNT(*) FROM main_features.fct_academic_features;
SELECT COUNT(*) FROM main_scoring.score_academic_risk;
SELECT COUNT(*) FROM main_main_analytics.school_summary;
```

### Preview data

```sql
SELECT *
FROM main_core.fact_attendance
LIMIT 20;
```

---

## 4) Useful one-liner from terminal (no CLI session)

```bash
uv run python - <<'PY'
import duckdb
con=duckdb.connect('oss_framework/data/oea.duckdb', read_only=True)
print(con.execute("""
select table_schema, count(*)
from information_schema.tables
where table_schema in ('main_staging','main_core','main_features','main_scoring','main_main_analytics','main_privacy')
group by 1
order by 1
""").fetchall())
PY
```

---

## 5) Common gotchas

- If you do not see mart schemas, you are likely connected to the wrong file (`aeries_to_duckdb.duckdb` instead of `oss_framework/data/oea.duckdb`).
- If queries fail during pipeline runs with lock errors, stop Rill first:

```bash
pkill -f "rill start|rill" || true
```

- dbt profile path currently points to `../data/oea.duckdb` from `oss_framework/dbt/profiles.yml`, which resolves to `oss_framework/data/oea.duckdb`.

---

## 6) Optional: inspect via Python notebook or script

```python
import duckdb

con = duckdb.connect('oss_framework/data/oea.duckdb', read_only=True)

df = con.execute("""
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
ORDER BY table_schema, table_name
""").df()

print(df.head(50))
```

---

## 7) Suggested exploration order

1. `main_staging` (cleaned staging data)
2. `main_core` (dimensions/facts)
3. `main_features` (engineered features)
4. `main_scoring` (risk scores)
5. `main_main_analytics` (dashboard/reporting-ready tables)

This progression usually makes lineage easiest to understand.
