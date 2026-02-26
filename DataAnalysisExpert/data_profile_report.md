# Data Profile Report

## Scope and Method
- Database profiled: `oss_framework/data/oea.duckdb`
- Relations profiled:
  - `main_main_analytics.v_chronic_absenteeism_risk`
  - `main_main_analytics.v_equity_outcomes_by_demographics`
  - schema checks for class/performance/wellbeing marts
- Read-only SQL profiling only.

## Chronic Absenteeism Profile
Evidence: `DataAnalysisExpert/profile_chronic_summary.txt`, `DataAnalysisExpert/profile_chronic_risk_levels.txt`, `DataAnalysisExpert/profile_chronic_trend_values.txt`, `DataAnalysisExpert/profile_chronic_range_checks.txt`.

- Row count: 1,700
- Distinct `student_key`: 1,700 (1 row per student at current grain)
- Null checks (`student_key`, `risk_level`, `chronic_absence_flag`): all 0 nulls
- Value range checks:
  - `attendance_rate_30d`: min 0.0, max 100.0, no out-of-range rows
  - `unexcused_absence_rate_30d`: no out-of-range rows
  - `chronic_absenteeism_risk_score`: no out-of-range rows
- Category distribution:
  - `risk_level`: `Low=1615`, `High=85` (no `Medium`/`Critical` present)
  - `attendance_trend_90d`: only `stable=1700`
- Timestamp coverage:
  - single snapshot (`min_loaded_at == max_loaded_at`)

### Observations
- Data quality is structurally clean for null/range checks.
- Risk and trend domains are narrow in current data snapshot (possible logic/feature sparsity upstream).

## Equity Outcomes Profile
Evidence: `DataAnalysisExpert/profile_equity_summary.txt`, `DataAnalysisExpert/profile_equity_groups.txt`, `DataAnalysisExpert/profile_equity_range_checks.txt`.

- Row count: 11 demographic groups
- Cohort size stats:
  - avg 154.55, min 85, max 255
  - `cohort_size < 5`: 0 groups
- Null checks (`race_ethnicity`, `pct_good_attendance`, `avg_gpa`): all 0 nulls
- Percentage metric range checks (`pct_*`): all within 0–100
- Timestamp coverage:
  - single snapshot (`min_loaded_at == max_loaded_at`)

### Observations
- Equity table passes immediate FERPA threshold guard (`>=5`) in current snapshot.
- Snapshot is small; trend/drift analysis over time is currently limited by single-load state.

## Additional Schema Profiling (Broader Dashboards)
Evidence:
- `DataAnalysisExpert/schema_class_section_comparison.txt`
- `DataAnalysisExpert/schema_performance_correlations.txt`
- `DataAnalysisExpert/schema_wellbeing_risk_profiles.txt`

- `v_class_section_comparison` columns center on `course_id`, `pct_passed`, ranking/effectiveness fields.
- `v_performance_correlations` columns center on `correlation_pair`, `correlation_coefficient`, `expected_direction`, `strength`.
- `v_wellbeing_risk_profiles` columns center on score fields (`*_risk_score`) and `wellbeing_risk_level`.

### Observations
- These schemas do not match many fields referenced by JSON dashboard definitions (validated in query compatibility audit).
