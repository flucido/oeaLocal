# Lineage Map (Source → Model → Dashboard)

## Chronic Absenteeism
- dbt model logic: `oss_framework/dbt/models/mart_analytics/analytics/v_chronic_absenteeism_risk.sql`
- exposed SQL model: `models/chronic_absenteeism_risk.sql`
- Rill source: `rill_project/sources/chronic_absenteeism_risk.yaml`
- Rill dashboards:
  - `rill_project/dashboards/chronic_absenteeism_risk.yaml`
  - `dashboards/chronic_absenteeism_risk.yaml`
- JSON definition: `schema/chronic_absenteeism_definition.json`
- Python app: `chronic_absenteeism_dashboard.py`
- Physical relation observed in DuckDB: `main_main_analytics.v_chronic_absenteeism_risk` (`BASE TABLE`)

Upstream dependencies from dbt SQL:
- `dim_students`
- `agg_attendance_windows` (`30d`, `90d` windows)

## Equity Outcomes
- dbt model logic: `oss_framework/dbt/models/mart_analytics/analytics/v_equity_outcomes_by_demographics.sql`
- exposed SQL model: `models/equity_outcomes_by_demographics.sql`
- Rill source: `rill_project/sources/equity_outcomes_by_demographics.yaml`
- Rill dashboards:
  - `rill_project/dashboards/equity_outcomes_by_demographics.yaml`
  - `dashboards/equity_outcomes_by_demographics.yaml`
- JSON definition: `schema/equity_outcomes_definition.json`
- Python app: `equity_outcomes_dashboard.py`
- Physical relation observed in DuckDB: `main_main_analytics.v_equity_outcomes_by_demographics` (`BASE TABLE`)

Upstream dependencies from dbt SQL:
- `dim_students`
- `agg_attendance_windows` (`term` window)
- `agg_discipline_windows` (`term` window)
- `fact_academic_performance`

## Class Effectiveness
- JSON definition: `schema/class_effectiveness_definition.json`
- Python app: `class_effectiveness_dashboard.py`
- Physical relation observed in DuckDB: `main_main_analytics.v_class_section_comparison` (`BASE TABLE`)

## Performance Correlations
- JSON definition: `schema/performance_correlations_definition.json`
- Python app: `performance_correlations_dashboard.py`
- Physical relation observed in DuckDB: `main_main_analytics.v_performance_correlations` (`BASE TABLE`)

## Wellbeing Risk
- JSON definition: `schema/wellbeing_risk_definition.json`
- Python app: `wellbeing_risk_dashboard.py`
- Physical relation observed in DuckDB: `main_main_analytics.v_wellbeing_risk_profiles` (`BASE TABLE`)

## Rill Project Runtime Lineage
- project config: `rill_project/rill.yaml`
- connector: `rill_project/connectors/duckdb.yaml`
- source SQL references map directly to:
  - `main_main_analytics.v_chronic_absenteeism_risk`
  - `main_main_analytics.v_equity_outcomes_by_demographics`
- dashboards consume models named:
  - `chronic_absenteeism_risk`
  - `equity_outcomes_by_demographics`
