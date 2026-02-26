# Dashboard Validation Report

## Validation Coverage
- Rill YAML metrics queries: validated via `EXPLAIN ANALYZE`/execution in `DataAnalysisExpert/query_audit`.
- JSON dashboard definition queries: validated via execution in `DataAnalysisExpert/query_audit` and `DataAnalysisExpert/query_audit_extended`.
- Python dashboard queries: validated with representative execution SQL in `DataAnalysisExpert/query_audit`.

## Results Summary
- Rill YAML metrics checks: **7/7 PASS**
- Python dashboard checks: **6/6 PASS** (query compatibility)
- JSON definition checks: **0/23 PASS** (all failed with binder errors)

Evidence index:
- `DataAnalysisExpert/query_audit/summary.txt`
- `DataAnalysisExpert/query_audit_extended/summary.txt`
- `DataAnalysisExpert/query_failures_summary.txt`

## Key Failure Patterns
1. **Field naming drift**
   - Example: `risk_classification` in JSON vs actual `risk_level` in mart.
   - Evidence: `DataAnalysisExpert/query_audit/json_chronic_students_at_risk.log`.
2. **Non-existent time-grain fields**
   - Example: `attendance_trend_30d`, `attendance_rate_60d` in JSON, absent in mart.
   - Evidence: `DataAnalysisExpert/query_audit/json_chronic_declining_attendance.log`, `.../json_chronic_trends_analysis.log`.
3. **Schema shape mismatch in equity JSON**
   - JSON expects normalized long-form demographics + intervention columns not present in current wide table.
   - Evidence: `DataAnalysisExpert/query_audit/json_equity_achievement_outcomes.log`.
4. **Legacy class/performance/wellbeing JSON definitions**
   - Class JSON expects `class_id/subject/avg_student_learning_gain`; mart exposes `course_id`, pass-rate metrics.
   - Performance JSON expects intervention/p-value fields not present in correlation mart.
   - Wellbeing JSON expects flag/case-management fields not present in risk-score mart.

## Rill Project-Specific Validation
- Connector/source wiring is functional for chronic + equity.
- Parity drift exists between root and `rill_project` dashboard YAML files:
  - chronic dashboard in `rill_project` omits measures/dimension/default sort from root.
  - equity dashboard in `rill_project` omits measures/default sort from root.
- Evidence: `DataAnalysisExpert/rill_project_audit_report.md` and diff outputs previously captured.

## Conclusion
- Operational dashboard layers (`rill_project` + Python simplified dashboards) can run on current marts.
- JSON dashboard definitions are currently non-executable against current analytics schemas and need remediation before use.
