# Full Data Stack Review Plan + Master Prompt

## Goal
Run a full, evidence-based review of data quality, semantic consistency, dashboard correctness, and performance across SQL models, dashboards, and supporting definitions.

## Confirmed Scope (current repo)
- SQL semantic layer:
  - `models/*.sql`
  - `oss_framework/dbt/models/mart_analytics/**/*.sql`
  - `oss_framework/dbt/models/mart_core/**/*.sql`
  - `oss_framework/dbt/models/mart_features/**/*.sql`
- Rill metrics/dashboards:
  - `dashboards/*.yaml`
  - `rill_project/dashboards/*.yaml`
- Rill project runtime/config:
   - `rill_project/rill.yaml`
   - `rill_project/connectors/*.yaml`
   - `rill_project/sources/*.yaml`
   - `rill_project/models/**/*` (currently empty but included for future buildout)
   - `rill_project/tmp/**/*` (runtime artifacts for diagnostics only; no source-of-truth logic)
- Dashboard definitions/specs:
  - `schema/*_definition.json`
- Python dashboards:
  - `*_dashboard.py`
- Runtime database target:
  - `aeries_to_duckdb.duckdb`
  - `oss_framework/data/oea.duckdb` (fallback)

## Guardrails (must-follow)
1. **No guessing**: every finding must include evidence query/file reference.
2. **Read-only first**: do not mutate production data/tables during analysis.
3. **Metric parity checks required**: compare KPI definitions across SQL, YAML, JSON, and Python queries.
4. **Case and type normalization checks required** for categorical fields (e.g., `risk_level`, booleans, percentages).
5. **Join cardinality validation required** on any upstream models used for dashboard KPIs.
6. **Performance checks must be reproducible** via `EXPLAIN ANALYZE` and measured runtimes.
7. **Rill parity checks required**: validate `dashboards/` and `rill_project/dashboards/` remain intentionally aligned (or document intentional divergence).
8. **Rill connector/source integrity required**: validate `rill_project/connectors/duckdb.yaml` DSN + source SQL columns match model contracts.
9. **Prioritize impact**: classify recommendations as P0/P1/P2 by business risk + effort.
10. **Do not change UX/design scope** while optimizing logic/performance.
11. **All generated scripts/reports stay in `DataAnalysisExpert/`**.

## Phased Execution Plan
1. **Inventory & lineage map**
   - Build source→model→dashboard dependency map.
   - Output: `DataAnalysisExpert/lineage_map.md`.
2. **Schema + data profiling**
   - Null rates, distinct counts, outliers, drift in key metrics.
   - Output: `DataAnalysisExpert/data_profile_report.md`.
3. **Semantic consistency audit**
   - Compare all KPI formulas/filters/grain across SQL/YAML/JSON/Python.
   - Output: `DataAnalysisExpert/semantic_consistency_matrix.csv`.
4. **SQL correctness + performance audit**
   - Query plans, expensive scans/sorts, duplicate aggregations, non-sargable patterns.
   - Output: `DataAnalysisExpert/sql_performance_findings.md`.
5. **Dashboard behavior audit**
   - Verify filters, sorting, time grain, and metric labels align with definitions.
   - Output: `DataAnalysisExpert/dashboard_validation_report.md`.
6. **Rill project audit (dedicated)**
   - Validate `rill_project` connector, sources, dashboard parity, and runtime config.
   - Identify drift between root `dashboards/` and `rill_project/dashboards/`.
   - Output: `DataAnalysisExpert/rill_project_audit_report.md`.
7. **Optimization roadmap**
   - Ranked backlog with expected impact, implementation order, and rollback notes.
   - Output: `DataAnalysisExpert/optimization_backlog.md`.

## Acceptance Criteria
- Every dashboard KPI has a single canonical formula and source model.
- No unresolved schema/semantic mismatches in high-impact metrics.
- Top 10 slowest analytical queries identified with concrete optimization actions.
- Clear, prioritized implementation roadmap with owner-ready tasks.

## Master Prompt (copy/paste)
Use this prompt to execute the full review:

"""
You are conducting a full data platform audit for this repository.

OBJECTIVE:
Review all data logic end-to-end (database models, Rill dashboards, JSON dashboard definitions, and Python dashboard queries), then propose concrete optimizations.

SCOPE:
- SQL models: models/*.sql and oss_framework/dbt/models/**
- Dashboard YAML: dashboards/*.yaml and rill_project/dashboards/*.yaml
- Rill runtime/config: rill_project/rill.yaml, rill_project/connectors/*.yaml, rill_project/sources/*.yaml
- Dashboard definitions: schema/*_definition.json
- Python dashboards: *_dashboard.py
- DuckDB files: aeries_to_duckdb.duckdb and oss_framework/data/oea.duckdb

REQUIRED METHOD:
1) Build lineage map source→model→dashboard.
2) Profile data quality (nulls, distincts, outliers, drift) for dashboard-driving columns.
3) Validate semantic consistency of each KPI across SQL, YAML, JSON, and Python.
4) Run SQL performance analysis (`EXPLAIN ANALYZE`) on dashboard-critical queries.
5) Audit rill_project connector/source wiring and dashboard parity vs root dashboards/.
6) Identify logic bugs, grain mismatches, naming/type inconsistencies, and stale/duplicate definitions.
7) Propose optimizations ranked by impact/effort and tagged P0/P1/P2.

GUARDRAILS:
- Evidence-only findings (include query or file reference for each finding).
- Read-only analysis first; no destructive changes.
- Keep outputs concise and actionable.
- Put all generated artifacts under DataAnalysisExpert/.
- If assumptions are needed, state them explicitly.

DELIVERABLES:
- Executive summary (top risks + wins)
- Findings table: issue, evidence, impact, fix, priority
- Optimization roadmap with quick wins vs structural improvements
- Optional patch plan (exact files to change) without applying changes yet

Also explicitly flag cross-layer mismatches, especially where names/formulas differ between:
- chronic_absenteeism_risk model/dashboard/definition/python
- equity_outcomes_by_demographics model/dashboard/definition/python
"""

## Early risk signals already observed
- Potential cross-layer naming mismatch: `risk_level` vs `risk_classification`.
- Potential metric field mismatch in ordering: references to `chronic_absenteeism_risk_score` vs `composite_risk_score`.
- Python dashboards use hardcoded path rooted in a different repo (`openedDataEstate`) and may drift from current local DB path.
- Rill YAML `format_preset: percentage` should be validated against whether values are already percentage points or fractions.
