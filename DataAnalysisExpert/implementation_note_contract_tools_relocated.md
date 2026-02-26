# Implementation Note: Contract Tools Relocated

To keep `DataAnalysisExpert/` focused on analysis outputs and reports, executable contract tooling was moved to `scripts/contracts/`.

## New canonical locations
- `scripts/contracts/contract_query_manifest.json`
- `scripts/contracts/contract_tests.py`
- `scripts/contracts/run_query_audit_phase2.sh`

## Updated references
- CI workflow `.github/workflows/test.yml` now watches `scripts/contracts/**` and runs:
  - `python scripts/contracts/contract_tests.py`

## Validation
- Workflow YAML parse: OK
- Contract tests: pass (`25 queries, 5 JSON files`)
- Shell audit runner: pass and writes summary to `DataAnalysisExpert/query_audit_phase2/summary.txt`
