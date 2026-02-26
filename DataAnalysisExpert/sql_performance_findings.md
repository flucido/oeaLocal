# SQL Performance Findings

## Method
- Used `EXPLAIN ANALYZE` for dashboard-critical queries.
- Evidence source: `DataAnalysisExpert/query_audit/*.log`, `DataAnalysisExpert/performance_times_raw.txt`, `DataAnalysisExpert/perf_*.txt`.

## Runtime Snapshot (Current Data Volume)
- Chronic (Rill):
  - `COUNT(DISTINCT student_key)` → `0.0087s`
  - `SUM(chronic_absence_flag)` → `0.0006s`
  - chronic absence rate calc → `0.0032s`
- Equity (Rill):
  - `SUM(cohort_size)` → `0.0014s`
  - `AVG(pct_good_attendance)` → `0.0009s`
  - `AVG(pct_no_discipline)` → `0.0005s`
  - `AVG(avg_gpa)` → `0.0010s`
- Python queries:
  - chronic at-risk count → `0.0020s`
  - chronic rate → `0.0022s`
  - chronic declining count → `0.0005s`
  - equity `SELECT * LIMIT 100` → `0.0023s`
- Additional baselines:
  - class row count → `0.0016s`
  - performance correlations row count → `0.0004s`

## Plan-Level Observations
1. Current runtimes are very fast due low/medium row counts (1,700 rows chronic; 11 rows equity).
2. Plans are sequential scans; no immediate bottleneck at present scale.
3. Correctness issues dominate over runtime issues right now (many JSON-definition queries fail to bind).

## Optimization Recommendations (Performance-Oriented)
- P1: Keep `v_*` marts materialized as tables (already configured in dbt) for dashboard stability.
- P1: Add periodic table-size growth monitoring and query latency guardrails (alerts when median query > 500ms).
- P2: For future scale-up, pre-aggregate common dashboard grains (risk-level distribution, demographic rollups) into dedicated aggregate tables.
- P2: Standardize benchmark suite using the existing query audit scripts to detect regressions before releases.

## Evidence References
- `DataAnalysisExpert/query_audit/rill_chronic_total_students.log`
- `DataAnalysisExpert/query_audit/rill_chronic_absence_rate.log`
- `DataAnalysisExpert/query_audit/rill_equity_cohort_size.log`
- `DataAnalysisExpert/query_audit/py_chronic_at_risk_count.log`
- `DataAnalysisExpert/query_audit/py_equity_records.log`
- `DataAnalysisExpert/perf_class_count.txt`
- `DataAnalysisExpert/perf_performance_corr_count.txt`
