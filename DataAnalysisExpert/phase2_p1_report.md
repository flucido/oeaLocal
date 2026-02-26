# Phase 2 P1 Report

## Scope Completed
- Portability hardening for DuckDB paths in Python dashboards.
- Portability hardening for Rill connector DSN.
- Percentage semantic normalization in root and `rill_project` Rill dashboards.

## Files Updated
- `rill_project/connectors/duckdb.yaml`
- `dashboards/chronic_absenteeism_risk.yaml`
- `dashboards/equity_outcomes_by_demographics.yaml`
- `rill_project/dashboards/chronic_absenteeism_risk.yaml`
- `rill_project/dashboards/equity_outcomes_by_demographics.yaml`
- `chronic_absenteeism_dashboard.py`
- `equity_outcomes_dashboard.py`
- `class_effectiveness_dashboard.py`
- `performance_correlations_dashboard.py`
- `wellbeing_risk_dashboard.py`

## Portability Changes
1. Python dashboards now use:
   - `DUCKDB_DATABASE_PATH` env var if present
   - fallback to repo-local `oss_framework/data/oea.duckdb`
2. Rill connector `dsn` changed from absolute machine path to relative path:
   - `../oss_framework/data/oea.duckdb`

## Percentage Semantic Normalization
- Updated percentage measures to return fractions (`0..1`) while keeping `format_preset: percentage`.
- Chronic:
  - `chronic_absence_rate`: `SUM(flag) / COUNT(...)`
  - `avg_attendance_rate_30d`: `AVG(attendance_rate_30d) / 100`
- Equity:
  - `avg_attendance`, `avg_no_discipline`, `avg_gpa_above_2_5`, `avg_below_c`: each divided by `100`
- Applied to both root and `rill_project` dashboards.

## Validation Evidence
- Python syntax: `python3 -m py_compile ...` => `PY_COMPILE_OK`
- Legacy hardcoded path removal verified (`openedDataEstate` no longer present)
- Root and `rill_project` dashboards remain in parity
- Fraction outputs validated:
  - `DataAnalysisExpert/p1_percentage_semantics_chronic.txt`
  - `DataAnalysisExpert/p1_percentage_semantics_equity.txt`

## Notes
- P1 changes are backward-compatible for SQL execution and improve portability for local/CI environments.
