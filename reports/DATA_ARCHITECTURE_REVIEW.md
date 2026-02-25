# Data Architecture Review Report

**Date:** 2026-02-23  
**Scope:** Full review of dbt data models, analytics views, scoring models, and feature engineering  
**Purpose:** Identify architectural flaws causing incorrect analytics results in MotherDuck

---

## Executive Summary

A deep review of the data architecture uncovered **15 defects** across the dbt model layers, including **7 critical** issues that would cause queries to fail or produce fundamentally wrong results. The root cause of most problems is a **grain mismatch**: the Aeries SIS API provides attendance data as annual summaries (one row per student per year), but downstream analytics models were written as if daily attendance records exist. This caused every attendance-based analytics view to either fail or return default/zero values, making dashboards report incorrect risk scores, attendance rates, and correlations.

All critical and high-severity issues have been fixed. This document serves as a reference for the issues found and the fixes applied.

---

## Architecture Overview

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│   Raw Sources  │    │    Staging      │    │   Core (Mart)  │
│  (Aeries API)  │───▶│  stg_aeries__* │───▶│  dim_students  │
│  (CDE Data)    │    │  stg_cde__*    │    │  fact_attend.  │
└────────────────┘    └────────────────┘    │  fact_academic │
                                           │  fact_discipl. │
                                           └───────┬────────┘
                                                   │
                      ┌────────────────────────────┼────────────────┐
                      │                            │                │
                      ▼                            ▼                ▼
               ┌──────────────┐          ┌─────────────────┐  ┌──────────┐
               │ Aggregations │          │    Features      │  │ Privacy  │
               │ agg_attend_  │          │ fct_chronic_abs  │  │ priv_*   │
               │ agg_discipl_ │          │ fct_academic_    │  └──────────┘
               │ fact_acad_   │          └────────┬─────────┘
               │ fact_class_  │                   │
               └──────┬───────┘                   ▼
                      │                   ┌──────────────┐
                      ▼                   │   Scoring    │
               ┌──────────────┐           │ score_*_risk │
               │  Analytics   │           └──────────────┘
               │ v_chronic_*  │
               │ v_equity_*   │
               │ v_wellbeing_ │
               │ v_performanc │
               │ v_cde_bench  │
               └──────────────┘
```

---

## Issues Found and Fixes Applied

### CRITICAL Issues (Would Cause Wrong Answers or Query Failures)

#### 1. Grain Mismatch: `agg_attendance_windows.sql` ← `fact_attendance`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | ALL attendance-based analytics produced wrong/empty results |
| **File** | `oss_framework/dbt/models/mart_analytics/aggregations/agg_attendance_windows.sql` |

**Problem:** `agg_attendance_windows` referenced columns that do not exist in `fact_attendance`:
- `attendance_date` — does not exist (annual grain has `academic_year`)
- `present_flag` — does not exist (annual grain has `days_present` count)
- `absent_flag` — does not exist (annual grain has `days_absent` count)
- `excused_flag` — does not exist (annual grain has `days_excused` count)
- `unexcused_flag` — does not exist (annual grain has `days_unexcused` count)
- `tardy_flag_numeric` — does not exist (annual grain has `days_tardy` count)

The Aeries SIS API returns attendance as **annual summaries** per student (DaysEnrolled, DaysPresent, DaysAbsence, etc.), not daily records. The staging model `stg_aeries__attendance` correctly maps these annual fields, and `fact_attendance` passes them through. But `agg_attendance_windows` was written assuming daily records exist.

**Downstream Impact:**
- `v_chronic_absenteeism_risk` — risk scores defaulted to 0 (all students appeared low-risk)
- `v_equity_outcomes_by_demographics` — attendance outcomes were wrong
- `v_wellbeing_risk_profiles` — attendance component was missing
- `v_performance_correlations` — attendance correlations were empty
- `v_cde_school_benchmarks` — internal metrics were wrong

**Fix:** Rewrote `agg_attendance_windows` to use the actual annual-grain columns from `fact_attendance`. All window types (30d, 60d, 90d, term) now use the annual data as the best available proxy. Added discipline incident counts from `fact_discipline` (previously hardcoded to 0).

**Future Improvement:** When daily attendance data becomes available (via a different API endpoint or data source), this model should be updated to compute true rolling windows.

---

#### 2. Non-Existent Column References: `fct_chronic_absence_features.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | All chronic absence feature engineering produced zeros |
| **File** | `oss_framework/dbt/models/mart_features/features/fct_chronic_absence_features.sql` |

**Problem:** Referenced columns that do not exist in `fact_attendance`:
- `fa.attendance_date` — does not exist
- `fa.absent_flag` — does not exist
- `fa.unexcused_absence_flag` — does not exist
- `fa.attendance_flag` — does not exist

**Fix:** Replaced with actual columns: `fa.days_absent`, `fa.days_unexcused`, `fa.days_enrolled`, `fa.attendance_rate`. Chronic absence flag now uses the standard definition (absent ≥ 10% of enrolled days).

---

#### 3. Non-Existent Column References: `fct_academic_features.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | All academic feature engineering produced zeros or errors |
| **File** | `oss_framework/dbt/models/mart_features/features/fct_academic_features.sql` |

**Problem:** Referenced columns that do not exist in `fact_academic_records`:
- `far.score` — does not exist (only `grade`, `gpa_points`, `is_passing` are available)
- `far.academic_status` — does not exist
- `far.derived_letter_grade` — does not exist

**Fix:** Replaced with actual columns: `far.gpa_points` for numeric scores, `far.is_passing` for pass/fail, `far.grade` for letter grade distribution.

---

#### 4. Non-Existent `score` Column: `fact_academic_performance.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | `assignment_grade_percent` was always NULL or errored |
| **File** | `oss_framework/dbt/models/mart_analytics/aggregations/fact_academic_performance.sql` |

**Problem:** `CAST(ar.score AS FLOAT)` referenced a `score` column that does not exist in `fact_academic_records`. Additionally, using `CAST` instead of `TRY_CAST` would throw errors on non-numeric values.

**Fix:** Replaced `ar.score` with `ar.gpa_points`, which is the appropriate numeric field from the staging layer.

---

#### 5. Non-Existent Daily Columns: `fact_attendance_daily.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | Model would fail to build |
| **File** | `oss_framework/dbt/models/mart_core/core/fact_attendance_daily.sql` |

**Problem:** Referenced non-existent columns and a non-existent join key:
- `fa.attendance_date`, `fa.present_flag`, `fa.absent_flag`, `fa.tardy_flag`, `fa.excused_flag`, `fa.unexcused_flag` — none exist in annual-grain `fact_attendance`
- `fa.attendance_id` — does not exist (used for join to staging)
- `sta.school_quarter`, `sta.day_of_week_name`, `sta.is_weekend` — do not exist in `stg_aeries__attendance`

**Fix:** Rewrote to aggregate annual attendance data by school year, school, and grade level using actual columns.

---

#### 6. Incompatible Metric Comparison: `v_cde_school_benchmarks.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | Gap analysis compared fundamentally different metrics |
| **File** | `oss_framework/dbt/models/mart_analytics/analytics/v_cde_school_benchmarks.sql` |

**Problem:** Two issues:
1. Referenced non-existent columns (`fa.present_flag`, `fa.absent_flag`) from `fact_attendance`
2. Compared incompatible metrics:
   - Internal "attendance rate" = % of days individual students were present (e.g., 92%)
   - CDE "attendance rate" was computed as `100 - chronic_absent_rate_pct`, where chronic absent rate = % of STUDENTS who are chronically absent (e.g., 80% means 20% of students are chronically absent)
   - These are fundamentally different quantities and cannot be subtracted

**Fix:** 
1. Fixed column references to use actual `fact_attendance` columns (`days_present`, `days_absent`, `days_enrolled`)
2. Removed the misleading `cde_attendance_rate_pct` derived metric
3. Gap analysis now compares chronic absence rates only (apples-to-apples)

---

#### 7. Score Thresholds on Wrong Scale: `score_academic_risk.sql`

| | |
|---|---|
| **Severity** | 🔴 CRITICAL |
| **Impact** | ALL students classified as CRITICAL academic risk |
| **File** | `oss_framework/dbt/models/mart_scoring/scoring/score_academic_risk.sql` |

**Problem:** The academic risk thresholds used percentage-based values (`avg_score < 60`, `< 70`, `< 80`, `< 90`) but the upstream `fct_academic_features.avg_score` field is now on a 0-4 GPA scale (from `gpa_points`). Since GPA max is 4.0, ALL students would have `avg_score < 60`, causing every student to be classified as 'CRITICAL' with risk score 90.

**Fix:** Updated thresholds to the GPA 0-4 scale:
- `< 1.0` → CRITICAL (F range)
- `< 2.0` → HIGH (D range)
- `< 2.5` → MEDIUM (C range)
- `< 3.0` → LOW (B range)
- `≥ 3.0` → Very Low (A/B range)

---

### HIGH Issues (Produce Significantly Misleading Results)

#### 8. Hardcoded FALSE: `v_chronic_absenteeism_risk.sql` economically_disadvantaged

| | |
|---|---|
| **Severity** | 🟠 HIGH |
| **Impact** | Economic disadvantage filter never identified any students |
| **File** | `oss_framework/dbt/models/mart_analytics/analytics/v_chronic_absenteeism_risk.sql` |

**Problem:** Line 19: `COALESCE(false, false) AS economically_disadvantaged` — always returns FALSE regardless of student's actual free/reduced lunch status.

**Fix:** Changed to `COALESCE(d.free_reduced_lunch_flag, false) AS economically_disadvantaged`.

---

#### 9. Risk Score Formula Error: `v_chronic_absenteeism_risk.sql`

| | |
|---|---|
| **Severity** | 🟠 HIGH |
| **Impact** | Risk scores were on inconsistent scales, miscategorizing students |
| **File** | `oss_framework/dbt/models/mart_analytics/analytics/v_chronic_absenteeism_risk.sql` |

**Problem:** The composite risk score formula had a misplaced `* 100` multiplier:
```sql
(unexcused_rate / 15.0) * 0.2  -- CASE result
* 100                           -- applied OUTSIDE the CASE
```
This made the unexcused component dominate (max ~13 points) while the attendance component was suppressed by `* 0.4` (max 40 points). The components were not on comparable 0-100 scales. Additionally, discipline and correlation components were always 0.

**Fix:** Restructured formula with explicit weights that sum to 100%:
- Attendance: 40% weight (0-100 scale)
- Unexcused absences: 20% weight (0-100 scale, capped)
- Discipline: 20% weight (0-100 scale, capped)
- Trend: 10% weight (binary: 0 or 100)
- Correlation: 10% weight (0-100 scale, capped)

---

#### 10. Attendance Risk Scale Mismatch: `v_wellbeing_risk_profiles.sql`

| | |
|---|---|
| **Severity** | 🟠 HIGH |
| **Impact** | Wellbeing composite score was biased away from attendance problems |
| **File** | `oss_framework/dbt/models/mart_analytics/analytics/v_wellbeing_risk_profiles.sql` |

**Problem:** Attendance risk score was computed as `(100 - attendance_rate) * 0.4`, giving a maximum of 40. But discipline risk ranged 0-100 and academic risk ranged 10-100. The three domains were averaged equally, but the attendance domain could never exceed 40, making it impossible for attendance alone to flag a student as high-risk.

Example: A student with 0% attendance (worst possible) would get attendance_risk=40, but a student with 6 discipline incidents would get discipline_risk=60. Attendance was structurally underweighted.

**Fix:** Removed the `* 0.4` multiplier so attendance risk ranges 0-100, matching the other domains.

---

#### 11. Pre-Negated Correlation: `v_performance_correlations.sql`

| | |
|---|---|
| **Severity** | 🟠 HIGH |
| **Impact** | Discipline-grades correlation sign was inverted, confusing analysts |
| **File** | `oss_framework/dbt/models/mart_analytics/analytics/v_performance_correlations.sql` |

**Problem:** `CORR(dis.incident_count * -1, acad.grade_numeric)` — discipline count was negated before computing correlation. This means:
- If more discipline → lower grades (expected negative correlation), the negation makes it appear **positive**
- The `expected_direction` label says 'Negative', creating confusion when the coefficient is positive

**Fix:** Removed the `* -1` negation. The CORR function now computes the natural correlation, which will be negative when discipline and grades move in opposite directions (as expected).

---

### MEDIUM Issues (Minor Inaccuracies)

#### 12. Missing D- Grade Mapping: `fact_class_effectiveness.sql`

| | |
|---|---|
| **Severity** | 🟡 MEDIUM |
| **File** | `oss_framework/dbt/models/mart_analytics/aggregations/fact_class_effectiveness.sql` |

**Problem:** Grade mapping was missing `D-`, causing it to fall through to `ELSE 0.0` (same as F). But `fact_academic_performance.sql` correctly maps `D-` → 0.7.

**Fix:** Added `WHEN ar.grade = 'D-' THEN 0.7` to the grade mapping.

---

#### 13. Risk Level Based on Wrong Score: `score_chronic_absence_risk.sql`

| | |
|---|---|
| **Severity** | 🟡 MEDIUM |
| **File** | `oss_framework/dbt/models/mart_scoring/scoring/score_chronic_absence_risk.sql` |

**Problem:** The `risk_level` classification was based solely on `recent_absence_score` (30-day component), ignoring the 90-day trend and unexcused absence components. This meant the risk level could disagree with the composite `chronic_absence_risk_score`.

**Fix:** Changed risk_level to be derived from the composite score.

---

#### 14. Discipline Fields Always Zero: `agg_attendance_windows.sql`

| | |
|---|---|
| **Severity** | 🟡 MEDIUM |
| **File** | `oss_framework/dbt/models/mart_analytics/aggregations/agg_attendance_windows.sql` |

**Problem:** `discipline_incidents_in_window` and `absence_discipline_correlation_score` were hardcoded to 0 in all window types. Downstream models like `v_chronic_absenteeism_risk` used these fields for risk scoring, but they were always zero, effectively ignoring discipline in risk calculations.

**Fix:** `discipline_incidents_in_window` is now populated from `fact_discipline` via a join. `absence_discipline_correlation_score` remains 0 pending daily-grain attendance data to compute meaningful correlations.

---

#### 15. Documentation Grain Mismatch: `_core__models.yml`

| | |
|---|---|
| **Severity** | 🟡 MEDIUM |
| **File** | `oss_framework/dbt/models/mart_core/core/_core__models.yml` |

**Problem:** `fact_attendance` was documented as "Grain: One row per student per attendance date" with columns like `attendance_id`, `attendance_date`, `attendance_status`. The actual grain is one row per student per academic year with columns like `days_enrolled`, `days_present`, `days_absent`.

**Fix:** Updated descriptions and column definitions to match the actual model.

---

## Remaining Considerations

### Data Granularity Limitation

The most significant structural limitation is that the Aeries SIS API provides **annual attendance summaries** rather than daily records. This means:

1. **Rolling windows (30d/60d/90d) cannot be computed accurately** — the current fix uses annual data as a proxy for all window types. All windows report the same attendance rate.

2. **Trend detection is not possible** — with only one data point per year, attendance trends cannot be computed. The `pattern_direction` field currently defaults to 'stable'.

3. **Absence-discipline correlation cannot be computed at the student level** — the `absence_discipline_correlation_score` remains 0.

**Recommendation:** Investigate whether the Aeries API offers a daily attendance endpoint (e.g., `/api/v5/attendance/daily`), or whether daily records can be extracted from the attendance detail tables. If daily data becomes available, `agg_attendance_windows` should be updated to compute true rolling windows.

### Staging Model Precision

The staging model `stg_aeries__academic_records` maps GPA points coarsely:
- B+, B, B- → all map to 3.0
- C+, C, C- → all map to 2.0

But the downstream analytics models (`fact_academic_performance`, `fact_class_effectiveness`) apply precise mappings (B+ → 3.3, B → 3.0, B- → 2.7). This creates a discrepancy between the `gpa_points` field in `fact_academic_records` and the `grade_numeric` computed in analytics models. The analytics models use the correct precise mapping from the `grade` letter field, so this is not a bug — but it means `gpa_points` and `grade_numeric` will differ for +/- grades.

### FERPA Compliance

The k-anonymity enforcement (minimum 5 students per group) is correctly implemented in `dim_student_demographics` and `fact_attendance_daily`. However, `v_equity_outcomes_by_demographics` does not enforce a minimum cohort size via HAVING clause — small demographic groups could be exposed. Consider adding `HAVING COUNT(DISTINCT d.student_id_hash) >= 5` to that view.
