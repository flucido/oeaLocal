# Phase 4: MotherDuck Integration - Implementation Plan

**Date**: 2026-02-22
**Status**: Planning (Phase 3 complete, Phase 4 starting)
**Research**: 3 background agents gathering patterns

---

## Objectives

1. Configure dbt to use MotherDuck as a target
2. Create Python script to publish tables from local DuckDB to MotherDuck cloud
3. Verify data integrity after publication
4. Test hybrid queries (local + cloud data)

---

## Prerequisites (Already Complete ✅)

- ✅ MotherDuck connection infrastructure (`src/db/connection.py`)
- ✅ MOTHERDUCK_TOKEN in `.env` file (verified JWT valid)
- ✅ All dbt models materialized as tables (Phase 3)
- ✅ Local DuckDB database with complete star schema
- ✅ 11 tables ready for publication (5 staging + 2 dim + 4 fact)

---

## Task Breakdown

### Task 4.1: Add MotherDuck Target to dbt profiles.yml

**File**: `oss_framework/dbt/profiles.yml`

**Expected Changes**:
```yaml
oea_student_analytics:
  outputs:
    dev:
      type: duckdb
      path: ../data/oea.duckdb
      threads: 4
      
    motherduck:  # NEW TARGET
      type: duckdb
      path: md:aeries_data_mart?motherduck_token={{ env_var('MOTHERDUCK_TOKEN') }}
      threads: 4
      settings:
        dbinstance_inactivity_ttl: 0s  # Prevent 15-min cache conflicts
  
  target: dev  # Default to local
```

**Verification**:
1. Run: `dbt debug --target motherduck`
2. Should connect to MotherDuck successfully
3. Should show `aeries_data_mart` database

**Delegation Category**: `quick` (single file, config change)

---

### Task 4.2: Create publish_to_motherduck.py Script

**File**: `oss_framework/scripts/publish_to_motherduck.py`

**Core Functionality**:
1. Import MotherDuckConnection from `src.db.connection`
2. Connect to both local DuckDB and MotherDuck
3. Create schemas in MotherDuck (staging, core, analytics)
4. For each table in local DB:
   - Read from local: `SELECT * FROM main_staging.stg_aeries__students`
   - Write to cloud: `CREATE TABLE md:aeries_data_mart.staging.stg_aeries__students AS ...`
5. Verify row counts match (local vs cloud)
6. Generate data integrity report

**Key Patterns to Use** (from research/motherduck_duckdb_research.md):
```python
from src.db.connection import get_motherduck_connection, get_hybrid_connection

# Hybrid connection for copying data
hybrid_conn = get_hybrid_connection(
    local_path="oss_framework/data/oea.duckdb",
    motherduck_database="aeries_data_mart"
)

# Create cloud table from local
hybrid_conn.execute("""
    CREATE TABLE IF NOT EXISTS md:aeries_data_mart.staging.stg_aeries__students AS
    SELECT * FROM local_db.main_staging.stg_aeries__students
""")
```

**Verification**:
1. Run script: `python oss_framework/scripts/publish_to_motherduck.py`
2. Check MotherDuck UI: All 11 tables visible
3. Query cloud table: `SELECT COUNT(*) FROM md:aeries_data_mart.staging.stg_aeries__students`
4. Row counts match local

**Delegation Category**: `unspecified-high` (new script, requires careful error handling)

---

### Task 4.3: Test dbt Run Against MotherDuck

**Command**: `dbt run --target motherduck --select stg_aeries__students`

**Expected Behavior**:
- dbt connects to MotherDuck cloud
- Runs single model as test
- Model materializes as table in cloud
- Query succeeds

**If Successful**:
- Run full dbt: `dbt run --target motherduck`
- All models should build in cloud

**Verification**:
1. Check dbt logs for success
2. Query MotherDuck to verify tables exist
3. Compare row counts: local vs cloud

**Delegation Category**: `quick` (just testing existing setup)

---

### Task 4.4: Verify Data Integrity

**Script**: Can be part of publish_to_motherduck.py or separate

**Checks**:
1. Row count comparison (local vs cloud)
2. Schema comparison (columns, types)
3. Sample data comparison (first 100 rows)
4. Aggregate metrics (sums, counts, averages)
5. Foreign key integrity (check joins still work)

**Expected Output**:
```
INTEGRITY CHECK RESULTS:
✅ stg_aeries__students: 5,232 rows (local) = 5,232 rows (cloud)
✅ stg_aeries__attendance: 33,478 rows (local) = 33,478 rows (cloud)
✅ stg_aeries__academic_records: 150,583 rows (local) = 150,583 rows (cloud)
...
✅ All schemas match
✅ Sample data matches
✅ Aggregate metrics match
✅ Foreign keys valid
```

**Delegation Category**: `unspecified-low` (straightforward queries)

---

### Task 4.5: Test Hybrid Queries

**Purpose**: Verify local + cloud queries work together

**Test Queries**:
```sql
-- Query cloud data
SELECT COUNT(*) FROM md:aeries_data_mart.staging.stg_aeries__students;

-- Query local data
SELECT COUNT(*) FROM local_db.main_staging.stg_aeries__students;

-- Hybrid query (join local + cloud)
SELECT 
    cloud.student_id_hash,
    cloud.grade_level,
    local.age
FROM md:aeries_data_mart.staging.stg_aeries__students AS cloud
JOIN local_db.main_staging.stg_aeries__students AS local
    ON cloud.student_id_raw = local.student_id_raw
LIMIT 10;
```

**Expected**: All queries succeed, results match expectations

**Delegation Category**: `quick` (just run queries and report)

---

## Research Questions (Waiting for Background Agents)

**Agent 1** (`bg_4b728b63` - explore): ⏳ Running
- Find dbt MotherDuck target configurations in this codebase
- Any existing profiles.yml with motherduck://
- Environment variable patterns

**Agent 2** (`bg_01890eaf` - librarian): ⏳ Running
- Official dbt-duckdb MotherDuck documentation
- Example profiles.yml configurations
- Best practices and gotchas

**Agent 3** (`bg_aa9104ee` - explore): ✅ **COMPLETED**
- Python scripts that publish to MotherDuck
- MotherDuckConnection usage patterns
- Data upload patterns

---

## Risks & Mitigations

**Risk 1**: MotherDuck token expires during publication
- **Mitigation**: Token is long-lived JWT, check expiry first
- **Fallback**: Regenerate token from MotherDuck UI

**Risk 2**: Network issues during large table upload
- **Mitigation**: Upload in batches, add retry logic
- **Fallback**: Resume from last successful table

**Risk 3**: dbt adapter doesn't support MotherDuck path syntax
- **Mitigation**: Research showed dbt-duckdb supports `md:` prefix
- **Fallback**: Use Python script for publication, skip dbt cloud target

**Risk 4**: Row count mismatches after publication
- **Mitigation**: Comprehensive integrity checks built into script
- **Fallback**: Re-publish specific tables, investigate mismatches

---

## Success Criteria

- [ ] dbt can connect to MotherDuck (`dbt debug --target motherduck` succeeds)
- [ ] All 11 tables published to cloud with correct row counts
- [ ] Data integrity verified (schemas, row counts, sample data match)
- [ ] Hybrid queries work (local + cloud joins)
- [ ] dbt can run models against MotherDuck target
- [ ] Performance acceptable (< 2 min for full publication)
- [ ] Documentation updated with MotherDuck setup instructions

---

## Next Actions (Pending Background Research)

1. Collect background agent outputs
2. Review patterns and best practices
3. Delegate Task 4.1: Add MotherDuck target to profiles.yml
4. Verify dbt connection works
5. Delegate Task 4.2: Create publish script
6. Run publication and verify integrity
7. Test hybrid queries
8. Update master plan with Phase 4 completion

