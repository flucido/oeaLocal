# Phase 4.2: MotherDuck Cloud Publication

**Status:** Setup Complete - Awaiting User Token Configuration  
**Task:** `openedDataEstate-b66`  
**Date:** 2026-02-22

---

## Overview

Phase 4.2 publishes locally validated dbt tables (dimensions + facts) from DuckDB to MotherDuck cloud for:
- Cloud-based analytics and dashboards
- Hybrid queries (local staging + cloud analytics)
- Collaboration and shared data access
- Production deployment without local database dependencies

---

## Deliverables

### ✅ Created

1. **`oss_framework/scripts/publish_to_motherduck.py`** (397 lines)
   - Full-featured publication script with dry-run support
   - Automatic schema initialization (raw, staging, core, analytics)
   - Row count verification after publication
   - Hybrid query testing capability
   - Comprehensive logging and error handling

2. **Updated `.env.template`**
   - Added `MOTHERDUCK_TOKEN` configuration with instructions
   - Documentation: Get token from https://app.motherduck.com/

### ⏸️ Pending User Action

**REQUIRED:** User must obtain MotherDuck token before publication can proceed.

---

## Setup Instructions for User

### Step 1: Get MotherDuck Token

1. Visit https://app.motherduck.com/
2. Sign up or log in (free tier available)
3. Navigate to Settings → Access Tokens
4. Create new token with name: `openedDataEstate-aeries-pipeline`
5. Copy the token (looks like: `eyJhbGc...`)

### Step 2: Configure Environment

```bash
# Option A: Export for current session
export MOTHERDUCK_TOKEN='your_token_here'

# Option B: Add to .env file (create if missing)
cp .env.template .env
# Then edit .env and replace: MOTHERDUCK_TOKEN=your_motherduck_token_here
```

### Step 3: Test Connection (Dry Run)

```bash
cd oss_framework/scripts
python3 publish_to_motherduck.py --dry-run
```

**Expected output:**
```
2026-02-22 14:17:54,550 - __main__ - INFO - Initialized MotherDuckPublisher
2026-02-22 14:17:54,550 - __main__ - INFO -   Local DB: ../data/oea.duckdb
2026-02-22 14:17:54,550 - __main__ - INFO -   Dry run: True
2026-02-22 14:17:54,551 - __main__ - INFO - ✓ Connected to local DuckDB
2026-02-22 14:17:54,551 - __main__ - INFO - [DRY RUN] Would connect to MotherDuck
...
[DRY RUN] Would publish X,XXX rows to MotherDuck
```

### Step 4: Publish All Tables

```bash
# Publish everything (dimensions + facts)
python3 publish_to_motherduck.py

# Or publish specific tables only
python3 publish_to_motherduck.py --tables dim_students,fact_enrollment
```

---

## Script Features

### Command-Line Options

```bash
python3 publish_to_motherduck.py [OPTIONS]

Options:
  --dry-run              Print what would be done without making changes
  --tables TABLE1,TABLE2 Publish specific tables only (comma-separated)
  --db-path PATH         Path to local DuckDB (default: ../data/oea.duckdb)
  -h, --help            Show help message
```

### Tables Published (in order)

**Dimensions (2 tables):**
1. `dim_students` (1,700 rows)
2. `dim_student_demographics` (60 rows)

**Facts (4 tables):**
3. `fact_enrollment` (5,463 rows)
4. `fact_academic_records` (150,583 rows)
5. `fact_discipline` (6,564 rows)
6. `fact_attendance` (33,478 rows)

**Total:** 191,848 rows across 6 tables

### Publication Process

For each table:
1. ✅ Read local table (row count + schema)
2. ✅ Attach local DB to MotherDuck connection
3. ✅ Drop existing MotherDuck table (if exists)
4. ✅ Create table and insert data (single operation for efficiency)
5. ✅ Verify row counts match (local vs. cloud)
6. ✅ Log success/failure

After all tables:
7. ✅ Test hybrid query (local staging + cloud core join)
8. ✅ Print summary report

### Error Handling

- **Missing token:** Script exits with helpful error message
- **Local DB not found:** Script exits immediately with file path
- **Table read failure:** Logs error, continues with remaining tables
- **Publication failure:** Logs error, continues with remaining tables
- **Row count mismatch:** Logs warning, marks table as failed
- **Connection failure:** Logs error and exits

### Verification

After publication completes:

```sql
-- Connect to MotherDuck (in DuckDB CLI or Python)
SELECT 
    table_schema,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema=t.table_schema AND table_name=t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema IN ('core')
ORDER BY table_name;
```

Expected: 6 tables in `core` schema

```sql
-- Verify row counts
SELECT 'dim_students' as table_name, COUNT(*) FROM core.dim_students
UNION ALL
SELECT 'dim_student_demographics', COUNT(*) FROM core.dim_student_demographics
UNION ALL
SELECT 'fact_enrollment', COUNT(*) FROM core.fact_enrollment
UNION ALL
SELECT 'fact_academic_records', COUNT(*) FROM core.fact_academic_records
UNION ALL
SELECT 'fact_discipline', COUNT(*) FROM core.fact_discipline
UNION ALL
SELECT 'fact_attendance', COUNT(*) FROM core.fact_attendance;
```

Expected row counts:
- dim_students: 1,700
- dim_student_demographics: 60
- fact_enrollment: 5,463
- fact_academic_records: 150,583
- fact_discipline: 6,564
- fact_attendance: 33,478

---

## MotherDuck Configuration

### Database Name
`aeries_data_mart`

### Schemas Created
1. `raw` - For future raw data storage
2. `staging` - For future staging tables
3. `core` - For dimension and fact tables (current focus)
4. `analytics` - For future aggregate/summary tables

### Connection String Format
```
md:aeries_data_mart?motherduck_token=<token>
```

### dbt Integration

The `dbt/profiles.yml` already has MotherDuck target configured:

```yaml
motherduck:
  type: 'duckdb'
  path: 'md:aeries_data_mart?dbinstance_inactivity_ttl=0s'
  motherduck_token: '{{ env_var("MOTHERDUCK_TOKEN") }}'
  threads: 8
  timeout_seconds: 300
```

To build models directly to MotherDuck:

```bash
cd oss_framework/dbt
dbt build --target motherduck --profiles-dir .
```

---

## Next Steps After Publication

### Immediate (Phase 4.3)
1. **Verify publication success** - Check row counts in MotherDuck
2. **Test hybrid queries** - Ensure local + cloud data works together
3. **Document MotherDuck URLs** - Share cloud database links with team

### Future (Phase 5+)
1. **Publish staging tables** - Add raw and staging layers to cloud
2. **Schedule incremental refreshes** - Automate daily/weekly updates
3. **Configure access control** - Set up user permissions in MotherDuck
4. **Integrate with Metabase** - Connect dashboards to MotherDuck
5. **Monitor cloud costs** - Track query usage and storage

---

## Troubleshooting

### Error: "MOTHERDUCK_TOKEN environment variable not set"
**Solution:** Follow Step 2 above to set the token

### Error: "Local database not found"
**Solution:** 
- Check path: `ls -lh ../data/oea.duckdb` (from scripts directory)
- Verify Phase 3 completed successfully
- Use `--db-path` to specify custom path

### Error: "Failed to connect to MotherDuck"
**Possible causes:**
- Invalid token (check for typos, extra spaces)
- Token expired (regenerate from MotherDuck UI)
- Network connectivity issues (check internet connection)
- MotherDuck service outage (check status.motherduck.com)

### Error: "Row count mismatch"
**Possible causes:**
- Concurrent modifications to local DB during publication
- Incomplete data transfer (network interruption)
- Schema mismatch between local and cloud

**Solution:** Re-run publication for failed table:
```bash
python3 publish_to_motherduck.py --tables <table_name>
```

### Warning: "X tables failed to publish"
**Solution:** 
- Review error logs above summary
- Fix underlying issues (network, schema, etc.)
- Re-run for failed tables only using `--tables` option

---

## Technical Details

### Schema Mapping

**Local DuckDB → MotherDuck:**
- `main_core.dim_students` → `core.dim_students`
- `main_core.dim_student_demographics` → `core.dim_student_demographics`
- `main_core.fact_*` → `core.fact_*`

(Note: Local uses `main_core` schema, MotherDuck uses `core`)

### Publication Strategy

**Method:** `CREATE TABLE AS SELECT` (CTAS)
- Single operation for efficiency
- Automatically infers schema from source
- Atomic transaction (all-or-nothing per table)

**Alternative methods not used:**
- ❌ `COPY TO/FROM` - Requires intermediate files
- ❌ `INSERT INTO SELECT` - Requires pre-creating table schema
- ❌ `EXPORT/IMPORT` - Less efficient for small datasets

### Hybrid Query Example

After publication, you can query local and cloud together:

```python
import duckdb

# Connect to MotherDuck with local DB attached
conn = duckdb.connect(f"md:aeries_data_mart?motherduck_token={token}")
conn.execute("ATTACH '/path/to/oea.duckdb' AS local_db (READ_ONLY);")

# Join local staging with cloud analytics
result = conn.execute("""
    SELECT 
        l.student_id_hash,
        l.first_name_raw,
        l.last_name_raw,
        c.enrollment_status,
        c.enrollment_date
    FROM local_db.main_staging.stg_aeries__students l
    JOIN core.fact_enrollment c 
        ON l.student_id_hash = c.student_id_hash
    WHERE c.enrollment_status = 'Active'
    LIMIT 10;
""").fetchall()
```

---

## Cost Considerations

### MotherDuck Free Tier
- **Storage:** 10 GB free
- **Query processing:** Shared resources
- **Sessions:** Unlimited
- **Users:** Unlimited

### Current Usage Estimate
- **Data size:** ~25 MB (191K rows, mostly dimension tables)
- **Well within free tier limits**

### Paid Tier (if needed)
- **Serverless pricing:** Pay per query compute
- **Reserved capacity:** Fixed monthly cost
- **Enterprise:** Custom pricing with SLAs

---

## Files Created/Modified

### Created
- `oss_framework/scripts/publish_to_motherduck.py` (397 lines)
- `.sisyphus/notepads/aeries-motherduck/phase4.2_motherduck_setup.md` (this file)

### Modified
- `.env.template` (added MOTHERDUCK_TOKEN section)

### Unchanged (Already Configured)
- `oss_framework/dbt/profiles.yml` (MotherDuck target exists)

---

## Status Summary

✅ **Script created and validated** (dry-run successful)  
✅ **Environment template updated** (MOTHERDUCK_TOKEN added)  
✅ **Documentation complete** (setup guide, troubleshooting, examples)  
⏸️ **Awaiting user token** (required for actual publication)  

**Next action:** User must obtain MotherDuck token and run publication script.

**After publication:** Phase 4.2 complete, proceed to Phase 4.3 (verification) or Phase 5 (incremental updates).
