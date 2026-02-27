
## [2026-02-26T12:00:00Z] DuckDB & dbt Pipeline Patterns

### DuckDB Connections
- File: /Users/flucido/projects/local-data-stack/src/db/connection.py — Python DuckDB connection helper using duckdb.connect; confirms path-based database usage via DUCKDB_DATABASE_PATH and relative/absolute DB paths.
- File: /Users/flucido/projects/local-data-stack/rill_project/connectors/duckdb.yaml — DuckDB DSN/DSN path configuration for local_duckdb.
- File: /Users/flucido/projects/local-data-stack/oss_framework/scripts/validate_preimplementation.py — shows tests that validate connection to oss_framework/data/oea.duckdb.
- File: /Users/flucido/projects/local-data-stack/k8s-deployment.yaml — k8s deployment mentions /data/oea.duckdb and duckdb usage.

### dbt Model Lineage
- Staging models: /Users/flucido/projects/local-data-stack/oss_framework/dbt/models/staging/aeries/stg_aeries__students.sql; /staging/aeries/stg_aeries__academic_records.sql; /staging/aeries/stg_aeries__enrollment.sql
- Mart models: /Users/flucido/projects/local-data-stack/oss_framework/dbt/models/mart_core/core/fact_attendance_daily.sql; /Users/flucido/projects/local-data-stack/oss_framework/dbt/models/mart_core/core/dim_students.sql; /Users/flucido/projects/local-data-stack/oss_framework/dbt/models/mart_analytics/analytics/v_performance_correlations.sql
- Dependencies: staging_aeries_* -> mart_core/core and mart_analytics; Data lineage is visible in the mart schemas and the v_* analytics views under /oss_framework/dbt/models/mart_analytics/* and /mart_features/*

### Export Patterns
- File: /Users/flucido/projects/local-data-stack/oss_framework/pipelines/aeries_to_parquet.py — demonstrates export of data to Parquet via DuckDB integration; includes Parquet partitioning logic in export (see export_to_rill.py references)
- File: /Users/flucido/projects/local-data-stack/oss_framework/pipelines/excel_imports_dlt_pipeline.py — supports exporting to Parquet with DuckDB as destination as part of DLt pipelines
- File: /Users/flucido/projects/local-data-stack/scripts/export_to_rill.py — contains logic to export analytics views to Parquet and partitioning via dynamic get_partition_columns

### Analytics Views & Data Flow
- File: /Users/flucido/projects/local-data-stack/docs/DATA_FLOW_DIAGRAM.md — high-level mapping of DuckDB staging to mart to analytics views and parquet outputs
- File: /Users/flucido/projects/local-data-stack/oss_framework/dbt/models/mart_analytics/analytics/v_class_section_comparison.sql; /v_equity_outcomes_by_demographics.sql; /v_wellbeing_risk_profiles.sql — analytics view SQL definitions for consolidated metrics
- File: /Users/flucido/projects/local-data-stack/PHASE3_PRODUCTION_READINESS.md and /oss_framework/config/duckdb_production.sql — show production DuckDB usage and view export flows

### Data Exports & Partitions
- File: /Users/flucido/projects/local-data-stack/scripts/export_to_rill.py — parquet partitioning code references (partition_cols, PARTITION_BY)
- File: /Users/flucido/projects/local-data-stack/docs/RILL_TROUBLESHOOTING.md — partition_cols usage examples

### Quick reference mappings (evidence indices)
- DuckDB connection call examples: /Users/flucido/projects/local-data-stack/test_uat.py, /Users/flucido/projects/local-data-stack/docs/architecture/data-model.md (connect calls)
- Parquet export hooks: oss_framework/pipelines/aeries_to_parquet.py, oss_framework/scripts/import_demographic_data.py, scripts/export_to_rill.py
