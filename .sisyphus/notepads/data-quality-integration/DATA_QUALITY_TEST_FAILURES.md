# Data Quality Test Failures Report

**Generated:** 2026-02-27
**dbt Build Status:** 73 PASS, 6 ERROR, 98 SKIP

## Executive Summary

After fixing all schema mismatches (8 → 6 errors), the remaining 6 test failures are:
- **1 Data Model Mismatch** (critical - blocks 98 downstream tests)
- **5 Data Quality Issues** (minor - unexpected values in real data)

---

## Critical Issue: Attendance Data Model Mismatch

### Error Details

```
[FAIL] source_not_null_raw_raw_attendance_attendance_date
Got 5756 results, configured to fail if != 0
```

### Root Cause

**Data Model Incompatibility:**
- **Staging model expects**: Daily attendance records with `attendance_date` column
- **Source data provides**: Pre-aggregated attendance summaries (no daily dates)

**Evidence:**
```sql
-- Staging model (line 14-58): stg_aeries__attendance.sql
SELECT
    CAST(EXTRACT(YEAR FROM attendance_date) AS VARCHAR) as academic_year,
    COUNT(*) as days_enrolled,
    SUM(...) as days_present,
    ...
FROM {{ source('raw', 'raw_attendance') }}
GROUP BY 1, 2, 3, 4  -- Expects to aggregate daily records
```

**Actual Data:**
- 5,756 pre-aggregated attendance records (851 students × ~7 academic years)
- All `attendance_date` values are NULL (data already summarized)
- Columns: `days_enrolled`, `days_present`, `attendance_rate` (already calculated)

### Impact

**Downstream Effects:**
- `stg_aeries__attendance` model **SKIPPED** (depends on failing test)
- 98 downstream models **SKIPPED** (blocked by attendance staging failure)
- Analytics views reference `legacy_raw_attendance` (1,700 synthetic students) instead of real data

**Current State:**
- ✅ Students: 851 real (correct)
- ✅ Academic records: 14,652 real (correct)
- ❌ Attendance: 1,700 synthetic (WRONG - should be 851 real)

### Recommended Solutions

**Option A: Modify Staging Model (Recommended)**

**Rationale:** Source data is already aggregated correctly. Staging model should pass through, not re-aggregate.

**Changes needed:**
1. Remove GROUP BY logic from `stg_aeries__attendance.sql`
2. Map aggregated columns directly:
   ```sql
   SELECT
       student_id,
       school_id,
       academic_year,  -- Already provided in source
       days_enrolled,  -- Already calculated
       days_present,   -- Already calculated
       attendance_rate -- Already calculated
   FROM {{ source('raw', 'raw_attendance') }}
   ```

3. Update `sources.yml` to remove `attendance_date` NOT NULL test

**Estimated effort:** 15 minutes

**Option B: Re-extract Daily Data**

**Rationale:** Match staging model expectations with daily-level data.

**Changes needed:**
1. Modify `aeries_to_parquet.py` to extract daily attendance API endpoint
2. Update `attendance_transformed` domain to preserve daily dates
3. Potentially large data volume (851 students × 180 school days × 7 years = ~1M records)

**Estimated effort:** 2-4 hours + API testing

**Recommendation:** **Option A** - Modify staging model to match available data.

---

## Data Quality Issues (5 failures)

### 1. Unexpected Grade Value

```
[FAIL] accepted_values_stg_aeries__academic_records_grade
Got 1 result, configured to fail if != 0
```

**Expected values:** `A, A+, B+, B, B-, C+, C, C-, D+, D, D-, F, P, NP, I, W, INCOMPLETE`

**Action needed:**
```sql
-- Query to identify unexpected value:
SELECT DISTINCT grade, COUNT(*) as count
FROM main_staging.stg_aeries__academic_records
WHERE grade NOT IN ('A', 'A+', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP', 'I', 'W', 'INCOMPLETE')
GROUP BY grade;
```

**Likely causes:**
- Letter grade with extra whitespace
- Numeric score instead of letter grade
- Special grade code (e.g., 'NG' for no grade)

**Resolution:** Add unexpected value to accepted list OR exclude invalid records.

---

### 2. Unexpected Discipline Incident Types

```
[FAIL] accepted_values_stg_aeries__discipline_short_description
Got 45 results, configured to fail if != 0
```

**Expected values:** `Behavior, Class_Disruption, Other, Tardy`

**Action needed:**
```sql
-- Query to identify unexpected types:
SELECT DISTINCT short_description, COUNT(*) as count
FROM main_staging.stg_aeries__discipline
WHERE short_description NOT IN ('Behavior', 'Class_Disruption', 'Other', 'Tardy')
GROUP BY short_description
ORDER BY count DESC;
```

**Likely causes:**
- More granular incident types in real data (e.g., 'Fighting', 'Bullying', 'Weapons')
- Free-text descriptions instead of standardized codes
- District-specific incident categories

**Resolution:** Update accepted values to include all real incident types OR create mapping logic.

---

### 3. Non-Unique Discipline Incident IDs

```
[FAIL] unique_stg_aeries__discipline_incident_id
Got 98 results, configured to fail if != 0
```

**Action needed:**
```sql
-- Query to find duplicates:
SELECT incident_id, COUNT(*) as duplicate_count
FROM main_staging.stg_aeries__discipline
GROUP BY incident_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

**Likely causes:**
- Multi-student incidents (same `incident_id` for multiple students involved)
- Multiple consequences per incident (1 incident → 3 rows: detention, suspension, parent contact)
- Data extraction issue (duplicate rows)

**Resolution:** 
- If multi-student: Use composite key `(incident_id, student_id)`
- If multi-consequence: Add `consequence_id` to grain
- If duplicate: Deduplicate with `ROW_NUMBER()` window function

---

### 4. Unexpected Enrollment Status

```
[FAIL] accepted_values_stg_aeries__enrollment_enrollment_status
Got 1 result, configured to fail if != 0
```

**Expected values:** `ACTIVE, COMPLETED, DROPPED, FAILED`

**Action needed:**
```sql
-- Query to identify unexpected status:
SELECT DISTINCT enrollment_status, COUNT(*) as count
FROM main_staging.stg_aeries__enrollment
WHERE enrollment_status NOT IN ('ACTIVE', 'COMPLETED', 'DROPPED', 'FAILED')
GROUP BY enrollment_status;
```

**Likely causes:**
- NULL status (no `EnterDate` or `LeaveDate`)
- Additional statuses (e.g., 'TRANSFERRED', 'WITHDRAWN', 'GRADUATED')
- Case sensitivity issue

**Resolution:** Add unexpected status to accepted list OR handle NULL with default value.

---

### 5. Unexpected Grade Level

```
[FAIL] accepted_values_stg_aeries__students_grade_level
Got 1 result, configured to fail if != 0
```

**Expected values:** `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12`

**Action needed:**
```sql
-- Query to identify unexpected grade:
SELECT DISTINCT grade_level, COUNT(*) as count
FROM main_staging.stg_aeries__students
WHERE grade_level NOT IN ('1','2','3','4','5','6','7','8','9','10','11','12')
GROUP BY grade_level;
```

**Likely causes:**
- Kindergarten (`K`, `0`, `-1`)
- Pre-K (`PK`, `-2`)
- Adult education (`13`, `14`)
- Special program codes

**Resolution:** Add kindergarten and pre-K to accepted values.

---

## Summary Statistics

### Schema Issues: RESOLVED ✅

**Original errors (8):**
1. ✅ `source_not_null_raw_raw_students_student_id` - FIXED
2. ✅ `source_not_null_raw_raw_attendance_student_id` - FIXED
3. ✅ `source_not_null_raw_raw_discipline_student_id` - FIXED
4. ✅ `source_not_null_raw_raw_academic_records_student_id` - FIXED (not in latest run)
5. ✅ `source_not_null_raw_raw_enrollment_student_id` - FIXED (not in latest run)
6. ✅ `source_not_null_raw_raw_enrollment_enrollment_id` - FIXED (not in latest run)
7. ✅ `source_relationships_raw_raw_attendance...` - FIXED
8. ✅ `stg_aeries__academic_records` missing `score` column - FIXED

**Column mapping fixes applied:**
- Discipline: `SchoolCode` → `SchoolOfIncidentCode`
- Attendance: Added `attendance_date` (NULL for aggregated data)
- Academic records: Added `score` (NULL, only letter grades available)
- Discipline: Added `resolution`, `suspension_days`, `severity`
- Discipline: Fixed `incident_date` type (VARCHAR → DATE)

### Data Validation: 6 Remaining Issues

| Test | Status | Impact | Priority |
|------|--------|--------|----------|
| `attendance_date` NOT NULL | ❌ FAIL (5756) | Blocks 98 models | **CRITICAL** |
| `academic_records_grade` accepted values | ❌ FAIL (1) | Minor | Low |
| `discipline_short_description` accepted values | ❌ FAIL (45) | Minor | Low |
| `discipline_incident_id` unique | ❌ FAIL (98) | Minor | Medium |
| `enrollment_enrollment_status` accepted values | ❌ FAIL (1) | Minor | Low |
| `students_grade_level` accepted values | ❌ FAIL (1) | Minor | Low |

### Real Data Verification

**Source Data (Parquet):**
- Students: 851 rows ✅
- Attendance: 5,756 rows ✅
- Grades: 14,652 rows ✅
- Discipline: 631 rows ✅
- Enrollment: 895 rows ✅

**Staging Models (dbt):**
- `stg_aeries__students`: 851 unique students ✅
- `stg_aeries__academic_records`: 14,652 records, 630 students ✅
- `stg_aeries__discipline`: 631 incidents ✅
- `stg_aeries__enrollment`: 895 enrollments ✅
- `stg_aeries__attendance`: **SKIPPED** (blocked by attendance_date test) ❌

---

## Next Steps

### Immediate (Unblock Pipeline)

1. **Fix attendance data model mismatch:**
   - Modify `stg_aeries__attendance.sql` to handle aggregated data
   - Update `sources.yml` to remove/modify `attendance_date` test
   - Estimated: 15 minutes

2. **Verify analytics views:**
   - Confirm 851 real students in all downstream models
   - Check Rill dashboards display real data

### Follow-up (Data Quality)

3. **Investigate and resolve 5 data quality failures:**
   - Query each failure to identify root cause
   - Update accepted value lists OR fix data issues
   - Estimated: 1-2 hours

4. **Document learnings:**
   - Add findings to `.sisyphus/notepads/data-quality-integration/learnings.md`
   - Update data quality profile with real data statistics

---

## Appendix: Diagnostic Queries

### Check attendance_date values
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(attendance_date) as non_null_dates,
    COUNT(*) - COUNT(attendance_date) as null_dates
FROM raw_attendance;
```

### Find unexpected grade values
```sql
SELECT grade, COUNT(*) as count
FROM main_staging.stg_aeries__academic_records
GROUP BY grade
ORDER BY count DESC;
```

### Find duplicate incident IDs
```sql
SELECT incident_id, student_id_raw, COUNT(*) as occurrences
FROM main_staging.stg_aeries__discipline
GROUP BY incident_id, student_id_raw
HAVING COUNT(*) > 1;
```

### Check grade level distribution
```sql
SELECT grade_level, COUNT(*) as student_count
FROM main_staging.stg_aeries__students
GROUP BY grade_level
ORDER BY 
    CASE 
        WHEN grade_level ~ '^[0-9]+$' THEN CAST(grade_level AS INTEGER)
        ELSE 999 
    END;
```

---

**Report Status:** ✅ COMPLETE
**Last Updated:** 2026-02-27 08:51 PST
