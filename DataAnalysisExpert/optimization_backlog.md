# Optimization Backlog (Prioritized)

## P0 (High Impact / Near-Term)
1. **Reconcile JSON definitions to actual marts (or regenerate marts to match contracts)**
   - Why: 23/23 JSON definition queries currently fail.
   - Fix options:
     - A) Update JSON queries to current column names and available grain.
     - B) Introduce compatibility views exposing expected legacy fields.
   - Evidence: `DataAnalysisExpert/query_failures_summary.txt`.

2. **Canonicalize metric field names across layers**
   - Why: cross-layer breakage (`risk_level` vs `risk_classification`; trend/rate field drift).
   - Fix: adopt canonical dictionary and enforce through lint checks.
   - Evidence: `DataAnalysisExpert/semantic_consistency_matrix.csv`.

3. **Fix Rill parity policy between root dashboards and rill_project dashboards**
   - Why: different measures/dimensions produce inconsistent analytics across entry points.
   - Fix: sync or explicitly document intentional divergence.
   - Evidence: `DataAnalysisExpert/rill_project_audit_report.md`.

## P1 (Medium Impact)
4. **Parameterize DuckDB paths in Python dashboards and Rill connector**
   - Why: hardcoded `openedDataEstate` path and absolute DSN reduce portability.
   - Fix: environment-variable based path resolution with fallback.
   - Evidence: dashboard python files + `rill_project/connectors/duckdb.yaml`.

5. **Normalize percentage semantics in dashboards**
   - Why: some marts store `0..100` values while dashboards use `format_preset: percentage` (risk of double-scaling in some tooling contexts).
   - Fix: choose one convention (`0..1` or `0..100`) and enforce per metric.
   - Evidence: root and rill dashboard YAML + dbt metric SQL output ranges.

6. **Strengthen data diversity checks for risk outputs**
   - Why: chronic trend currently only `stable`; risk levels only `Low/High` in snapshot.
   - Fix: add QA tests to detect category collapse and feature sparsity.
   - Evidence: `DataAnalysisExpert/profile_chronic_risk_levels.txt`, `.../profile_chronic_trend_values.txt`.

## P2 (Low / Structural)
7. **Add automated cross-layer contract tests in CI**
   - Compare fields in dbt marts vs dashboard query references.
   - Run SQL bind tests similar to `run_query_audit*.sh` per PR.

8. **Add release benchmark harness**
   - Keep EXPLAIN baselines and detect >X% regressions as data grows.
   - Evidence: `DataAnalysisExpert/performance_times_raw.txt`.

9. **Document dashboard contract versioning**
   - Keep explicit schema versions for marts consumed by Rill/JSON/Python layers.

## Quick Wins vs Structural
- **Quick wins (1–3 days):** P0-1, P0-2, P1-4.
- **Structural (1–3 sprints):** P0-3 (if broad sync), P1-5, P2-7/8/9.
