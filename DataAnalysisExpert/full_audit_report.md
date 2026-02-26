# Full Data Platform Audit Report

## Executive Summary
Top risks:
1. **Definition-layer breakage:** JSON dashboard definitions are not executable against current mart schemas (23/23 validation failures).
2. **Cross-layer semantic drift:** key fields diverge by layer (`risk_level` vs `risk_classification`, missing `attendance_rate_60d`, etc.).
3. **Rill parity drift:** root dashboards and `rill_project` dashboards are not equivalent, causing inconsistent KPI surface area.

Top wins:
1. Core marts are present and queryable in DuckDB (`main_main_analytics` relations discovered and accessible).
2. Core chronic/equity Rill metrics execute successfully with low latency.
3. Core data quality checks (null/range/FERPA-size) are clean for sampled chronic/equity marts.

Assumptions:
- `oss_framework/data/oea.duckdb` is the primary active runtime database for this audit.
- JSON definition files are intended to be executable contract artifacts (not historical docs).

## Findings Table
| Issue | Evidence | Impact | Fix | Priority |
|---|---|---|---|---|
| JSON chronic uses `risk_classification` not in mart | `DataAnalysisExpert/query_audit/json_chronic_students_at_risk.log` | Card query failure | replace with `risk_level` or add compatibility column/view | P0 |
| JSON chronic references `attendance_trend_30d` absent in mart | `.../json_chronic_declining_attendance.log` | Card query failure | use `attendance_trend_90d` or add 30d trend upstream | P0 |
| JSON chronic references `attendance_rate_60d` absent in mart | `.../json_chronic_trends_analysis.log` | Trend tab failure | remove 60d or materialize 60d metric | P0 |
| JSON equity expects normalized demographic/intervention fields absent in wide mart | `.../json_equity_achievement_outcomes.log`, `.../json_equity_intervention_roi.log` | Entire dashboard definition fails | rewrite JSON queries to current schema or create transformed compatibility view | P0 |
| JSON class definition references `class_id/subject/avg_student_learning_gain` absent in class mart | `DataAnalysisExpert/query_audit_extended/json_class_perf_vs_peer.log` | Entire dashboard definition fails | align queries to actual class mart (`course_id`, pass metrics) | P0 |
| JSON performance definition references `correlation_name/p_value/intervention_*` absent in mart | `.../json_perf_key_correlations.log`, `.../json_perf_intervention_status.log` | Entire dashboard definition fails | align to current correlation schema or materialize expected fields | P0 |
| JSON wellbeing definition references `overall_risk_level` and flags absent in mart | `.../json_wellbeing_high_risk.log`, `.../json_wellbeing_domain_breakdown.log` | Entire dashboard definition fails | align to `wellbeing_risk_level` + available score fields | P0 |
| Root vs `rill_project` dashboards drift in measures/dimensions/sort | `DataAnalysisExpert/rill_project_audit_report.md` | Different KPI outputs by entrypoint | enforce sync or document intentional fork | P0 |
| Python dashboards use hardcoded external repo DB path | dashboard python files | portability/deploy risk | use env-configurable path | P1 |
| Percentage formatting semantics may be inconsistent with data scale | dashboard YAML + dbt outputs | potential misrendered percentages | normalize metric scale contract | P1 |
| Chronic trend/risk category diversity collapsed in current snapshot | `DataAnalysisExpert/profile_chronic_trend_values.txt`, `.../profile_chronic_risk_levels.txt` | reduced analytical signal | add upstream QA tests and feature checks | P1 |

## Optimization Roadmap
### Quick Wins
1. Fix JSON query bindings for chronic/equity to current schema.
2. Parameterize all dashboard DB paths and connector DSN.
3. Decide and apply parity policy between `dashboards/` and `rill_project/dashboards/`.

### Structural Improvements
1. Introduce compatibility views or schema-contract versioning for legacy JSON definitions.
2. Add CI contract tests that execute all dashboard queries against DuckDB.
3. Add benchmark regression checks from EXPLAIN logs as data scales.

## Optional Patch Plan (No Changes Applied)
1. **Schema/contract alignment**
   - `schema/chronic_absenteeism_definition.json`
   - `schema/equity_outcomes_definition.json`
   - `schema/class_effectiveness_definition.json`
   - `schema/performance_correlations_definition.json`
   - `schema/wellbeing_risk_definition.json`

2. **Rill parity alignment**
   - `rill_project/dashboards/chronic_absenteeism_risk.yaml`
   - `rill_project/dashboards/equity_outcomes_by_demographics.yaml`
   - (optionally) root `dashboards/*.yaml` if canonicalization goes opposite direction

3. **Runtime portability**
   - `rill_project/connectors/duckdb.yaml`
   - `chronic_absenteeism_dashboard.py`
   - `equity_outcomes_dashboard.py`
   - `class_effectiveness_dashboard.py`
   - `performance_correlations_dashboard.py`
   - `wellbeing_risk_dashboard.py`

4. **Automated guardrails**
   - Add a contract test script under `DataAnalysisExpert/` or `scripts/` to run query bind checks per PR.

## Evidence Bundle
- `DataAnalysisExpert/lineage_map.md`
- `DataAnalysisExpert/data_profile_report.md`
- `DataAnalysisExpert/semantic_consistency_matrix.csv`
- `DataAnalysisExpert/sql_performance_findings.md`
- `DataAnalysisExpert/dashboard_validation_report.md`
- `DataAnalysisExpert/optimization_backlog.md`
- `DataAnalysisExpert/query_audit/summary.txt`
- `DataAnalysisExpert/query_audit_extended/summary.txt`
