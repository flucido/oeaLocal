# Rill Project Audit Report (Initial)

## Scope Reviewed
- `rill_project/rill.yaml`
- `rill_project/connectors/duckdb.yaml`
- `rill_project/sources/*.yaml`
- `rill_project/dashboards/*.yaml`
- parity against root `dashboards/*.yaml`

## Key Findings

### 1) `rill_project` is active but partially slimmed vs root dashboards
- `rill_project/dashboards/chronic_absenteeism_risk.yaml` has fewer dimensions/measures than `dashboards/chronic_absenteeism_risk.yaml`.
- Missing in `rill_project` (present in root):
  - dimension `attendance_trend_90d`
  - measures `avg_attendance_rate_30d`, `avg_risk_score`, `high_risk_students`
  - `default_sort` on `composite_risk_score`
- Impact: users get fewer analytical capabilities in the Rill-focused project than expected from root definitions.

### 2) Equity dashboard also has reduced measure coverage in `rill_project`
- `rill_project/dashboards/equity_outcomes_by_demographics.yaml` omits root measures:
  - `avg_gpa_above_2_5`
  - `avg_below_c`
  - `default_sort` by `cohort_size`
- Impact: fewer KPI slices and potentially different default UX behavior.

### 3) Source SQL parity is logically intact
- `rill_project/sources/chronic_absenteeism_risk.yaml` and root `models/chronic_absenteeism_risk.sql` select the same fields from `main_main_analytics.v_chronic_absenteeism_risk`.
- `rill_project/sources/equity_outcomes_by_demographics.yaml` and root `models/equity_outcomes_by_demographics.sql` are also aligned in selected fields.
- Impact: ingestion/query surface appears consistent; drift is mainly in metrics-view definitions.

### 4) Connector path is explicit and local (good), but environment-rigid
- `rill_project/connectors/duckdb.yaml` points to an absolute DSN path under the current machine.
- Impact: reliable locally, but brittle across machines/CI unless parameterized.

### 5) `rill_project/models/` currently empty
- This is valid if sources + metrics views are sufficient for current MVP.
- Impact: if you plan model-level transformations inside Rill, this folder needs to be populated or design intentionally documented.

## Recommended Actions (Rill-specific)
- P0: Decide whether dashboard drift between root and `rill_project` is intentional.
  - If not intentional, synchronize dashboard measures/dimensions and sort settings.
- P1: Parameterize connector DSN via environment strategy for portability.
- P1: Add a short `rill_project/README.md` documenting purpose, expected parity policy, and how to run.
- P2: Add optional Rill model files only if transformations are intended in-project.

## Notes for Full Audit Execution
These findings are initial and structural. Full execution should still validate metric math, type formatting (`percentage` semantics), and runtime performance with representative query plans.
