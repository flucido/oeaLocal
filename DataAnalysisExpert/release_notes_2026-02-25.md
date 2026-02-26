# Release Notes — Data Audit & Contract Hardening

**Release Date:** 2026-02-25
**Scope:** End-to-end audit, semantic alignment, query contract enforcement, CI gating, portability updates, and documentation consistency cleanup.

## Summary

This release finalizes the full cross-layer analytics review and implements remediation across SQL models, dashboard definitions, Rill assets, Python dashboards, CI, and operational docs. The main outcome is a more reliable and portable analytics stack with automated contract checks preventing regression.

## What Shipped

### 1) Audit + Evidence Pack
- Completed full review planning and guarded execution workflow.
- Produced audit artifacts in `DataAnalysisExpert/` including:
  - review plan and master prompt
  - lineage map
  - data profile report
  - semantic consistency matrix
  - SQL performance findings
  - dashboard validation report
  - optimization backlog
  - full audit report

### 2) P0 Semantic/Schema Corrections
- Patched all schema definition JSON files to match current analytics marts and query contracts.
- Synced root and `rill_project` dashboard definitions for parity.
- Corrected risk-level casing inconsistencies (standardized expected values).
- Post-fix validation result: **25 PASS / 0 FAIL** for contract query checks.

### 3) P1 Portability + Metric Semantics
- Replaced hardcoded DuckDB paths in Python dashboards with environment-variable strategy (`DUCKDB_DATABASE_PATH`) and local fallback behavior.
- Normalized percentage metric semantics to fraction expressions so percentage formatting is consistent across dashboard layers.
- Updated Rill connector configuration for relative-path portability.

### 4) P2 Contract Testing + CI Enforcement
- Added canonical contract manifest and runners under `scripts/contracts/`:
  - `contract_query_manifest.json`
  - `contract_tests.py`
  - `run_query_audit_phase2.sh`
  - `README.md`
- Updated GitHub Actions workflow to:
  - run dedicated `contract-tests` job once
  - gate matrix `test` job on `contract-tests` via job dependency
  - trigger on contract-relevant paths (`scripts/contracts/**`, `schema/**`, `dashboards/**`, `rill_project/**`).

### 5) Documentation and Runbook Harmonization
- Added contract-tool discoverability to user-facing docs.
- Updated stale examples and schema/table references in active operational documentation.
- Verified latest edits in:
  - `SECURITY.md`
  - `oss_framework/OPERATIONAL_RUNBOOKS.md`
- Completed final stale-pattern sweep across active markdown (excluding historical `DataAnalysisExpert` reports).

## Validation Snapshot

- Contract runner status: passing with manifest-driven checks.
- JSON definition validation: integrated in contract test flow.
- YAML/dashboard consistency: aligned between root and `rill_project` counterparts.
- CI wiring: contract tests run once and gate broader test matrix.
- Rill runtime note: `rill_project` startup is expected to succeed from project directory; root invocation behavior differs by project context.

## Operational Impact

- **Risk Reduced:** Regression risk lowered via contract-first checks in CI.
- **Portability Improved:** Fewer machine-specific path failures.
- **Semantic Consistency:** Percentage and risk-label behavior now consistent across SQL/YAML/Python layers.
- **Supportability:** Runbooks and security docs now reference current analytics objects.

## Compatibility / Breaking Notes

- No intentional external API breakage introduced.
- Contract test failures should now be treated as release blockers for analytics-layer changes.
- Historical files in `DataAnalysisExpert/` intentionally retain prior findings for audit traceability.

## Recommended Post-Release Practice

1. Run `python scripts/contracts/contract_tests.py` before merging analytics/dashboard changes.
2. Keep `scripts/contracts/contract_query_manifest.json` as single source of truth for query contracts.
3. Update contract manifest and docs together when schema/model semantics evolve.
4. Re-run stale-example sweep on active docs as part of release checklist.

## Final Status

✅ Full review executed
✅ Phase 2 remediation complete (P0/P1/P2)
✅ CI contract gating active
✅ Tooling relocated and documented
✅ Active docs/runbooks/security examples cleaned and aligned
