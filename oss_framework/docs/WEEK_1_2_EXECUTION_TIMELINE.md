# Week 1-2 Execution Timeline & Checklist

**Status**: READY FOR EXECUTION  
**Timeline**: 8-10 minutes total (one-command execution)  
**Prerequisites**: Clarification questions answered + .env configured

---

## Pre-Week 1: Environment Setup (Day 0)

### Setup Phase (5 minutes)

```bash
# Step 1: Navigate to project
cd /Users/flucido/projects/openedDataEstate

# Step 2: Run setup script
bash oss_framework/scripts/setup_week1_automated.sh

# Step 3: Activate virtual environment
source venv/bin/activate

# Step 4: Create .env file
cp .env.template .env
# ← Edit .env with your Aeries credentials
```

**Output**:
- ✅ Virtual environment created
- ✅ Dependencies installed (20+ packages)
- ✅ Python modules created (config.py, logging_config.py, etc.)
- ✅ Test infrastructure ready
- ✅ .env template generated

---

### Validation Phase (1 minute)

```bash
# Run pre-implementation validation
python oss_framework/scripts/validate_preimplementation.py
```

**Expected Output**:
```
Pre-Implementation Validation Suite
========================================================

✅ Python Version
✅ Package: DuckDB
✅ Package: Pandas
✅ Package: Requests
✅ Package: python-dotenv
✅ Aeries API Key
✅ DuckDB Connection
✅ Directory: ./oss_framework/data/stage1
✅ Directory: ./oss_framework/data/stage2
✅ Directory: ./oss_framework/data/stage3
✅ Directory: ./oss_framework/logs
✅ Excel: D&F Report
✅ Excel: Demographic Report
✅ D&F Update Frequency
✅ Demographic Update Frequency
✅ RFEP Update Frequency
✅ Clarification Answers

Results: 16✅ 0❌ 1⏭️ (Total: 17)
========================================================
✅ All checks passed! Ready for Week 1-2 implementation.
```

**If validation fails**:
- Read error messages carefully
- Most common: Missing .env variable or file not found
- Fix issue and re-run validation
- All checks must pass before proceeding

---

## Week 1-2: Main Execution (2-10 minutes)

### Orchestration Phase (6-10 minutes)

```bash
# Run complete Week 1-2 data foundation
python oss_framework/scripts/run_week1_orchestrator.py
```

**Execution Flow**:

```
STEP 1: Validating prerequisites...
  ✅ Configuration validated

STEP 2: Creating Stage 1 landing zone tables...
  ✅ raw_students table created (26 columns)
  ✅ raw_attendance table created (22 columns)
  ✅ raw_academic_records table created (23 columns)
  ✅ raw_discipline table created (18 columns)
  ✅ raw_enrollment table created (23 columns)

STEP 3: Ingesting data from Aeries API...
  ✅ Fetching 1,700 student records
  ✅ Loaded 1,700 student records
  ✅ Fetching 45,000 attendance records
  ✅ Loaded 45,000 attendance records
  ✅ Fetching 200,000 grade records
  ✅ Loaded 200,000 grade records
  ✅ Fetching 2,000 discipline records
  ✅ Loaded 2,000 discipline records

STEP 4: Importing D&F report from Excel...
  ✅ Read 456 records from Excel
  ✅ Updated 456 student records with D&F data

STEP 5: Importing demographic data from Excel...
  ✅ Read 1,700 demographic records
  ✅ Updated demographic data for 1,700 records

STEP 6: Running data quality validation tests...
  ✅ raw_students: 1,700 rows
  ✅ raw_attendance: 45,000 rows
  ✅ No null student_ids in attendance
  ✅ All attendance dates valid
  ✅ All grades have required fields
  ✅ All discipline dates valid
  ✅ All references have valid students
  ... (9 more tests)

============================================================
Week 1-2 Data Foundation - Execution Report
============================================================

Total Duration: 487.3 seconds (8.1 minutes)

Results:
  stage1_tables: success
  aeries_ingest: {'students': 1700, 'attendance': 45000, 'grades': 200000, 'discipline': 2000}
  d_and_f_import: 456
  demographic_import: 1700
  data_quality: all_passed

Next Steps:
1. Review data quality report
2. Run Week 3-4 feature engineering (when ready)
3. Check dashboards at http://localhost:3000 (Metabase)

For detailed logs, see: ./oss_framework/logs/oea.log
```

---

## Post-Execution: Verification (2 minutes)

### Verify in DuckDB

```bash
# Connect to DuckDB
duckdb oss_framework/data/oea.duckdb

# Check tables created
.tables

# Verify row counts
SELECT 'raw_students' as table_name, COUNT(*) as row_count FROM raw_students
UNION ALL
SELECT 'raw_attendance', COUNT(*) FROM raw_attendance
UNION ALL
SELECT 'raw_academic_records', COUNT(*) FROM raw_academic_records
UNION ALL
SELECT 'raw_discipline', COUNT(*) FROM raw_discipline
UNION ALL
SELECT 'raw_enrollment', COUNT(*) FROM raw_enrollment;

# Check data samples
SELECT student_id, first_name, last_name, grade_level FROM raw_students LIMIT 5;
SELECT * FROM raw_attendance LIMIT 5;

# Exit
.quit
```

**Expected Results**:
```
table_name              row_count
raw_students           1700
raw_attendance         45000
raw_academic_records   200000
raw_discipline         2000
raw_enrollment         35000
```

### Check Log File

```bash
# View full execution log
tail -100 oss_framework/logs/oea.log

# Search for errors
grep -i "error\|failed\|❌" oss_framework/logs/oea.log
```

**Should show**: All steps completed, no errors

---

## Execution Checklist

### Pre-Execution
- [ ] Clarification questions answered
- [ ] .env file created with credentials
- [ ] Setup script run successfully
- [ ] Validation passed (0 ❌)

### During Execution
- [ ] Orchestrator running
- [ ] Each step shows ✅
- [ ] No error messages in console
- [ ] Progress visible (timestamps)

### Post-Execution
- [ ] All 5 Stage 1 tables created
- [ ] Row counts match expectations
- [ ] Data quality tests all passing
- [ ] Log file contains no errors
- [ ] DuckDB connection works

### Verification
- [ ] Can query students from DuckDB
- [ ] Can query attendance from DuckDB
- [ ] Can query grades from DuckDB
- [ ] No null IDs found
- [ ] Foreign key relationships valid

---

## Expected Timing Breakdown

| Step | Expected Duration | Notes |
|------|-------------------|-------|
| Setup (1st time only) | 2-3 min | Python install |
| Validation | 30 sec | Quick checks |
| Create Stage 1 tables | 10 sec | Just schema |
| Ingest Aeries data | 2-5 min | API calls |
| Import Excel reports | 30-60 sec | File I/O |
| Data quality tests | 1-2 min | 15 tests |
| **TOTAL** | **6-12 min** | One command |

---

## Common Issues & Fixes

### Issue: "Aeries API Rate Limit Exceeded"
**Fix**: Built-in backoff handles this automatically. Script will wait and retry.

### Issue: "DuckDB: Database is locked"
**Fix**: Another process has the database open. Close all DuckDB connections and retry.

### Issue: "Excel file not found"
**Fix**: Update EXCEL_DF_REPORT_PATH and EXCEL_DEMOGRAPHIC_PATH in .env with correct paths.

### Issue: "Configuration validation failed"
**Fix**: Re-run `python oss_framework/scripts/validate_preimplementation.py` to see specific errors.

### Issue: "Data quality tests failed"
**Fix**: Check logs for which test failed. Usually indicates data quality issue in source system.

---

## After Week 1-2 Completion

### Data is Ready in DuckDB!

✅ **Raw Data Loaded**:
- 1,700 students with demographics
- 45,000 attendance records
- 200,000 assignment grades
- 2,000 discipline incidents
- D&F flags (504, IEP) populated
- Demographic data updated
- All timestamped with `_loaded_at`

✅ **Data Quality Verified**:
- No null student IDs
- All dates valid
- Foreign keys intact
- 99%+ completeness

✅ **Infrastructure Ready**:
- DuckDB database operational
- Logging configured
- Test suite passing
- Ready for Week 3-4

---

## Next: Week 3-4 Feature Engineering

Once Week 1-2 is complete, run Week 3-4 (when ready):

```bash
# Week 3-4 will build Stage 2 refined models with:
# - Pseudonymization (hash PII, mask sensitive data)
# - Feature engineering (30+ features per domain)
# - Risk scoring (chronic absence, well-being)
# - Aggregation windows (30/60/90 day patterns)

# Status: Documentation prepared, ready for execution
```

---

## Support

**Questions during execution?**
- Check logs: `tail -f oss_framework/logs/oea.log`
- Run validation: `python oss_framework/scripts/validate_preimplementation.py -v`
- Query DuckDB: `duckdb oss_framework/data/oea.duckdb`

**All scripts ready?**
- ✅ setup_week1_automated.sh - Setup environment
- ✅ validate_preimplementation.py - Validate prerequisites
- ✅ run_week1_orchestrator.py - Execute Week 1-2
- ✅ create_stage1_tables.py - Create tables (called by orchestrator)
- ✅ ingest_aeries_data.py - Ingest data (called by orchestrator)
- ✅ import_d_and_f_report.py - Excel import (called by orchestrator)
- ✅ import_demographic_data.py - Demographic import (called by orchestrator)
- ✅ config.py - Configuration management
- ✅ logging_config.py - Logging setup
- ✅ data_quality.py - Quality validation

---

## 🎯 Success = Week 1-2 Complete

```
✅ Stage 1 tables created and populated
✅ 248,700 rows loaded across 5 tables
✅ All data quality tests passing
✅ DuckDB ready for Week 3-4
✅ Logs clean and documented

READY FOR WEEK 3-4 FEATURE ENGINEERING
```

---

**Ready to execute? Run:**
```bash
bash oss_framework/scripts/setup_week1_automated.sh
```

