# Phase 6: End-to-End Pipeline Refresh Test

**Test Date**: 2026-02-23  
**Objective**: Validate complete pipeline refresh from source CSVs to MotherDuck  
**Baseline**: 215,975 total rows across 22 tables (from Phase 3)

---

## Test Plan

### Stage 1: CSV → Parquet Ingestion
- **Script**: `oss_framework/pipelines/aeries_to_parquet.py`
- **Source**: `/Users/flucido/Desktop/AeRIES test data/`
- **Target**: `oss_framework/data/stage1/aeries/*.parquet`
- **Success Criteria**: All CSV files successfully converted to Parquet

### Stage 2: Parquet → DuckDB Sync
- **Script**: `oss_framework/scripts/sync_to_duckdb.py`
- **Source**: `oss_framework/data/stage1/aeries/*.parquet`
- **Target**: `oss_framework/data/oea.duckdb` (raw_* tables)
- **Success Criteria**: All raw tables populated with matching row counts

### Stage 3: dbt Transformations
- **Script**: `dbt run --full-refresh` (via Python dbtRunner)
- **Working Directory**: `oss_framework/dbt/`
- **Models**: staging → core → analytics (6 + 6 + 10 = 22 tables)
- **Success Criteria**: 
  - All models build without errors
  - dbt tests pass
  - Row counts match baseline

### Stage 4: MotherDuck Publishing
- **Script**: `oss_framework/scripts/publish_to_motherduck.py`
- **Source**: Local DuckDB `oea.duckdb`
- **Target**: MotherDuck `aeries_data_mart` database
- **Success Criteria**: 215,975 rows published across 22 tables

---

## Execution Log

### Pre-Test Environment Check
**Status**: ⏸️ PENDING

**Checks**:
- [ ] MOTHERDUCK_TOKEN set in .env
- [ ] Source CSV files present in Desktop directory
- [ ] Local DuckDB accessible
- [ ] dbt profiles.yml configured
- [ ] Python dependencies installed

---

### Stage 1 Execution: CSV → Parquet
**Status**: ⏸️ PENDING  
**Start Time**: TBD  
**End Time**: TBD  
**Duration**: TBD  

**Command**:
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/pipelines
python3 aeries_to_parquet.py
```

**Results**:
- Files processed: TBD
- Parquet files created: TBD
- Errors encountered: TBD

---

### Stage 2 Execution: Parquet → DuckDB
**Status**: ⏸️ PENDING  
**Start Time**: TBD  
**End Time**: TBD  
**Duration**: TBD  

**Command**:
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/scripts
python3 sync_to_duckdb.py
```

**Results**:
- Tables synced: TBD
- Total rows loaded: TBD
- Errors encountered: TBD

---

### Stage 3 Execution: dbt Transformations (Full Refresh)
**Status**: ⏸️ PENDING  
**Start Time**: TBD  
**End Time**: TBD  
**Duration**: TBD  

**Command**:
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/dbt
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['run', '--full-refresh'])"
```

**Results**:
- Models run: TBD / 22
- Models passed: TBD
- Models failed: TBD
- Tests run: TBD
- Tests passed: TBD

---

### Stage 3b Execution: dbt Transformations (Incremental)
**Status**: ⏸️ PENDING  
**Start Time**: TBD  
**End Time**: TBD  
**Duration**: TBD  

**Command**:
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/dbt
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['run'])"
```

**Results**:
- Models run: TBD
- Performance vs full-refresh: TBD
- Errors encountered: TBD

---

### Stage 4 Execution: MotherDuck Publishing
**Status**: ⏸️ PENDING  
**Start Time**: TBD  
**End Time**: TBD  
**Duration**: TBD  

**Command**:
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/scripts
export $(grep -v '^#' ../.env | xargs)
python3 publish_to_motherduck.py
```

**Results**:
- Tables published: TBD / 22
- Total rows published: TBD (Baseline: 215,975)
- Errors encountered: TBD

---

## Row Count Validation

### Expected Baseline (From Phase 3)
```
Total rows across 22 tables: 215,975

Staging tables (6):
- stg_aeries__students
- stg_aeries__programs
- stg_aeries__academic_records
- stg_aeries__attendance
- stg_aeries__discipline
- stg_aeries__enrollment

Core tables (6):
- dim_students
- dim_courses
- dim_schools
- fact_attendance
- fact_discipline
- fact_academic_records

Analytics tables (10):
- analytics_for_hex
- equity_by_race
- school_summary
- math_pathways_7th_grade
- algebra_1_outcomes
- lead_program_enrollment
- [4 more analytics tables]
```

### Actual Results (Post-Refresh)
**Status**: ⏸️ PENDING

```
# Will populate after Stage 4 completes
```

---

## Performance Metrics

### Stage Timing Summary
| Stage | Operation | Duration | Status |
|-------|-----------|----------|--------|
| 1 | CSV → Parquet | TBD | ⏸️ |
| 2 | Parquet → DuckDB | TBD | ⏸️ |
| 3a | dbt full-refresh | TBD | ⏸️ |
| 3b | dbt incremental | TBD | ⏸️ |
| 4 | MotherDuck publish | TBD | ⏸️ |
| **Total** | **End-to-End** | **TBD** | ⏸️ |

### Bottleneck Analysis
**Status**: ⏸️ PENDING

- Slowest stage: TBD
- Optimization opportunities: TBD

---

## Error Handling Tests

### Test 1: Invalid CSV Data
**Status**: ⏸️ PENDING

**Scenario**: Introduce malformed CSV data  
**Expected**: Pipeline should fail gracefully with clear error message  
**Actual**: TBD

### Test 2: Missing Environment Variable
**Status**: ⏸️ PENDING

**Scenario**: Unset MOTHERDUCK_TOKEN  
**Expected**: Stage 4 should fail with "MOTHERDUCK_TOKEN not set" error  
**Actual**: TBD

### Test 3: Schema Mismatch
**Status**: ⏸️ PENDING

**Scenario**: Add unexpected column to CSV  
**Expected**: Pipeline should handle gracefully or fail with clear message  
**Actual**: TBD

---

## Rollback Procedures Tested

### Test 1: Restore Previous DuckDB State
**Status**: ⏸️ PENDING

**Steps**:
1. Backup current `oea.duckdb`
2. Run pipeline with bad data
3. Restore from backup

**Result**: TBD

### Test 2: MotherDuck Rollback
**Status**: ⏸️ PENDING

**Steps**:
1. Query MotherDuck for previous state
2. Publish corrupted data
3. Restore previous state

**Result**: TBD

---

## Issues Discovered

### Issue 1: [Title]
**Severity**: TBD  
**Stage**: TBD  
**Description**: TBD  
**Resolution**: TBD

---

## Recommendations

### Performance Optimizations
**Status**: ⏸️ PENDING

### Pipeline Improvements
**Status**: ⏸️ PENDING

### Documentation Updates Needed
**Status**: ⏸️ PENDING

---

## Summary

**Overall Status**: ⏸️ NOT STARTED  
**Test Duration**: TBD  
**Critical Issues**: TBD  
**Pass/Fail**: TBD  

**Production Readiness Assessment**: TBD

---

*Test execution begins below...*
