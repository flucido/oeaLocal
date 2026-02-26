# Local Data Stack - Architecture

High-level architecture and design decisions for the 100% local education analytics platform.

---

## Overview

The **local-data-stack** implements an **In-Process Data Stack** architecture - a fully local alternative to cloud-based Open Education Analytics (OEA). All data processing happens on a single machine using DuckDB's embedded analytics engine.

### Design Principles

1. **Local-First**: Zero cloud dependencies - all data stays on your infrastructure
2. **Embedded Analytics**: DuckDB runs in-process, no separate database server
3. **Medallion Architecture**: Bronze → Silver → Gold data refinement stages
4. **Declarative Transformations**: dbt for reproducible, testable data models
5. **Interactive BI**: Rill dashboards powered directly by DuckDB

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL DATA SOURCES                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Aeries SIS API  │  Excel Reports  │  CSV Imports  │  Manual Uploads   │
└────────┬─────────┴─────────┬───────┴──────┬────────┴──────────┬─────────┘
         │                   │              │                   │
         └───────────────────┴──────────────┴───────────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │   dlt (Data Load Tool)  │
                         │  Python-based ingestion │
                         └───────────┬────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │         STAGE 1: DATA INGESTION (Bronze Layer)         │
         ├────────────────────────────────────────────────────────┤
         │  Format: Parquet files + Delta Lake                    │
         │  Location: ./data/stage1/                              │
         │  Schema: Raw, unprocessed (mirrors source systems)     │
         │  Partitioning: By load_date, entity type               │
         └────────────────────────┬───────────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   dbt (Data Build Tool)     │
                    │   Stage 2 models (staging)  │
                    └─────────────┬───────────────┘
                                  │
         ┌────────────────────────┴────────────────────────────────┐
         │       STAGE 2: DATA REFINEMENT (Silver Layer)           │
         ├─────────────────────────────────────────────────────────┤
         │  Storage: DuckDB tables (./oss_framework/data/oea.duckdb)│
         │  Schema: mart_core (dimensions & facts)                 │
         │  Transformations:                                       │
         │    • Data cleaning & validation                         │
         │    • Deduplication & merge logic                        │
         │    • Type casting & standardization                     │
         │    • Primary/foreign key enforcement                    │
         │  Models: dim_students, dim_staff, fact_attendance, etc. │
         └─────────────────────────┬───────────────────────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │   dbt Stage 3 models        │
                     │   (marts & analytics)       │
                     └─────────────┬───────────────┘
                                   │
         ┌─────────────────────────┴──────────────────────────────┐
         │      STAGE 3: ANALYTICS MARTS (Gold Layer)             │
         ├────────────────────────────────────────────────────────┤
         │  Storage: DuckDB tables (same database)                │
         │  Schemas:                                              │
         │    • mart_features - Engineered features (GPA trends)  │
         │    • mart_scoring - Risk scores (dropout, chronic abs) │
         │    • mart_analytics - Pre-aggregated metrics           │
         │    • mart_privacy - Pseudonymized views                │
         │  Optimizations: Indexed, analyzed, query-ready         │
         └────────────────────────┬───────────────────────────────┘
                                  │
            ┌─────────────────────┴────────────────────┐
            │                                          │
   ┌────────▼──────────┐                    ┌─────────▼────────┐
   │  Rill Developer    │                    │   JupyterLab     │
   │  (BI Dashboards)   │                    │  (Ad-hoc queries)│
   ├────────────────────┤                    ├──────────────────┤
   │ • Live metrics     │                    │ • Python/SQL     │
   │ • Time series      │                    │ • DuckDB API     │
   │ • Drill-down       │                    │ • Polars/Pandas  │
   │ • Exports          │                    │ • Custom analysis│
   └────────────────────┘                    └──────────────────┘
         │                                            │
         └────────────────┬───────────────────────────┘
                          │
                ┌─────────▼──────────┐
                │   End Users        │
                │ • Administrators   │
                │ • Counselors       │
                │ • Teachers         │
                │ • Data analysts    │
                └────────────────────┘
```

---

## Data Flow

### Stage 1: Ingestion (Bronze Layer)

**Objective**: Extract raw data from source systems with minimal transformation.

**Process:**
1. **dlt pipelines** connect to Aeries API and read Excel files
2. Data is written as **Parquet files** to `./data/stage1/`
3. **Delta Lake** format provides ACID transactions and time-travel
4. Each entity type (students, attendance, grades) gets its own subdirectory
5. Files are partitioned by `load_date` for incremental processing

**Key characteristics:**
- Schema mirrors source systems exactly
- No data quality checks (yet)
- Idempotent loads (can re-run safely)
- Metadata tracked in Delta Lake transaction log

**Output example:**
```
data/stage1/
├── students/
│   ├── load_date=2026-02-24/
│   │   └── part-0.parquet
│   └── _delta_log/
├── attendance/
│   ├── load_date=2026-02-24/
│   │   └── part-0.parquet
│   └── _delta_log/
└── grades/
    └── ...
```

---

### Stage 2: Refinement (Silver Layer)

**Objective**: Clean, standardize, and structure data for analytics.

**Process:**
1. **dbt staging models** read Parquet files from Stage 1
2. Apply data quality rules:
   - Remove duplicates (based on business keys)
   - Cast types (strings → dates, integers, etc.)
   - Validate constraints (non-null student IDs, valid date ranges)
   - Standardize codes (gender, ethnicity, grade levels)
3. Build **dimension tables** (students, staff, schools, courses)
4. Build **fact tables** (attendance events, grade records, enrollment)
5. Write to DuckDB `mart_core` schema

**Key transformations:**
- **Deduplication**: `ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY load_date DESC)`
- **Type casting**: `CAST(enrollment_date AS DATE)`
- **Null handling**: `COALESCE(phone_number, 'Unknown')`
- **Referential integrity**: Ensure all attendance records link to valid student IDs

**Output schemas:**
- `mart_core.dim_students` - Student demographics, enrollment status
- `mart_core.dim_staff` - Teachers, counselors, administrators
- `mart_core.dim_schools` - School master data
- `mart_core.dim_courses` - Course catalog
- `mart_core.fact_attendance` - Daily attendance records
- `mart_core.fact_grades` - Course grades and GPA
- `mart_core.fact_enrollment` - Student-course enrollments

**dbt configuration:**
```yaml
models:
  local_data_stack:
    staging:
      +materialized: table
      +tags: ['staging']
      +schema: 'mart_core'
```

---

### Stage 3: Analytics Marts (Gold Layer)

**Objective**: Build analytics-ready aggregations, features, and risk scores.

**Process:**
1. **dbt analytics models** read from `mart_core` (Stage 2 output)
2. Engineer features:
   - GPA trends (current vs. prior term)
   - Attendance rates (daily, weekly, monthly)
   - Course completion rates
   - Demographic breakdowns
3. Calculate risk scores:
   - Chronic absenteeism risk (≥10% absences)
   - Dropout risk (multi-factor model)
   - Course failure risk
4. Pre-aggregate metrics for dashboard performance
5. Create pseudonymized views for external sharing

**Key transformations:**
- **Feature engineering**:
  ```sql
  -- GPA trend calculation
  SELECT
    student_id,
    current_term_gpa,
    LAG(current_term_gpa) OVER (PARTITION BY student_id ORDER BY term) AS prior_term_gpa,
    current_term_gpa - prior_term_gpa AS gpa_change
  FROM mart_core.fact_grades
  ```
- **Risk scoring**:
  ```sql
  -- Chronic absenteeism flag
  SELECT
    student_id,
    COUNT(*) AS total_days,
    SUM(CASE WHEN absent THEN 1 ELSE 0 END) AS absent_days,
    (absent_days * 100.0 / total_days) AS absence_rate,
    CASE WHEN absence_rate >= 10 THEN TRUE ELSE FALSE END AS is_chronic_absent
  FROM mart_core.fact_attendance
  GROUP BY student_id
  ```
- **Pre-aggregation**:
  ```sql
  -- Monthly attendance summary (for fast dashboard loading)
  SELECT
    DATE_TRUNC('month', attendance_date) AS month,
    school_id,
    grade_level,
    COUNT(DISTINCT student_id) AS total_students,
    AVG(absence_rate) AS avg_absence_rate
  FROM main_main_analytics.v_chronic_absenteeism_risk
  GROUP BY month, school_id, grade_level
  ```

**Output schemas:**
- `mart_features.student_features` - Engineered student-level features
- `mart_scoring.chronic_absenteeism_risk` - Attendance risk scores
- `mart_scoring.dropout_risk` - Dropout prediction scores
- `main_main_analytics.v_chronic_absenteeism_risk` - Chronic absenteeism metrics
- `main_main_analytics.v_equity_outcomes_by_demographics` - Demographic performance gaps
- `mart_privacy.pseudonymized_students` - De-identified views

**dbt configuration:**
```yaml
models:
  local_data_stack:
    mart_features:
      +materialized: table
      +tags: ['features']
      +schema: 'mart_features'
    mart_scoring:
      +materialized: table
      +tags: ['scoring']
      +schema: 'mart_scoring'
    mart_analytics:
      +materialized: table
      +tags: ['analytics']
      +schema: 'mart_analytics'
      +post-hook: "ANALYZE {{ this }}"  # Optimize query performance
```

---

## DuckDB Schema Naming Convention

### Schema Prefixing Behavior

dbt automatically prefixes schema names with the **profile name** and **target name** from `profiles.yml`. This is standard dbt behavior for namespace isolation.

**Configuration:**
```yaml
# profiles.yml
duckdb_oss:        # Profile name
  target: 'dev'     # Target name (or 'prod')
```

**dbt Model Configuration:**
```yaml
# dbt_project.yml
models:
  local_data_stack:
    mart_analytics:
      +schema: 'mart_analytics'  # Configured schema name
```

**Resulting DuckDB Schema:**
```
{profile}_{target}_{configured_schema}
main_dev_mart_analytics  (when target: dev)
main_prod_mart_analytics (when target: prod)
```

### Current Schema Mapping

| dbt Config (`schema=`) | DuckDB Schema (Actual) | Usage |
|------------------------|------------------------|-------|
| `'mart_core'` | `main_dev_core` | Dimensions, facts |
| `'mart_features'` | `main_dev_features` | Engineered features |
| `'mart_scoring'` | `main_dev_scoring` | Risk scores |
| `'mart_analytics'` | `main_dev_mart_analytics` | Pre-aggregated metrics for dashboards |
| `'mart_privacy'` | `main_dev_privacy` | Pseudonymized views |

**Note:** All SQL queries (Rill dashboards, Python scripts, contract tests) must reference the **full DuckDB schema name** (e.g., `main_dev_mart_analytics`), not the dbt configured name.

### Why This Matters

1. **Dashboard SQL models** query DuckDB directly → must use `main_dev_mart_analytics`
2. **Python analytics scripts** connect to DuckDB → must use `main_dev_mart_analytics`
3. **Contract tests** validate schema → must use `main_dev_mart_analytics`
4. **dbt model configs** reference logical name → use `schema='mart_analytics'`

**Example:**
```sql
-- ❌ WRONG: Rill SQL model using dbt logical name
SELECT * FROM mart_analytics.v_chronic_absenteeism_risk

-- ✅ CORRECT: Rill SQL model using actual DuckDB schema
SELECT * FROM main_dev_mart_analytics.v_chronic_absenteeism_risk
```

### Production Environment

When deploying to production with `target: prod`, schema names change:
- `main_dev_mart_analytics` → `main_prod_mart_analytics`
- Update all dashboard SQL, Python scripts, and contract tests accordingly
- Or use environment variables to dynamically construct schema names

---

## Component Details

### DuckDB - Embedded Analytics Database

**Why DuckDB?**
- **Embedded**: No separate server process, runs in-process with Python/CLI
- **Columnar**: Optimized for analytical queries (aggregations, scans)
- **Fast**: Vectorized execution engine, parallelized queries
- **SQL Standard**: PostgreSQL-compatible syntax
- **Extensions**: Delta Lake, Parquet, JSON, httpfs support
- **File-based**: Single `.duckdb` file, easy backups

**Configuration** (`oss_framework/dbt/profiles.yml`):
```yaml
duckdb_oss:
  target: 'dev'
  outputs:
    dev:
      type: 'duckdb'
      path: '../data/oea.duckdb'
      threads: 4
      extensions:
        - delta    # Delta Lake tables
        - httpfs   # HTTP/S3 file access
        - json     # JSON parsing
```

**Performance tuning:**
- Memory limit: 8GB (dev), 16GB (prod)
- Threads: 4 (dev), 8 (prod)
- Periodically run `ANALYZE` to update statistics
- Use `PRAGMA optimize_database` for compaction

---

### dbt - Data Transformation Framework

**Why dbt?**
- **Declarative**: SQL-based transformations (no boilerplate code)
- **Testable**: Built-in data quality tests (uniqueness, not-null, relationships)
- **Documented**: Auto-generated data dictionary
- **Modular**: Reusable macros, DRY principles
- **Version controlled**: All transformations in git

**Project structure:**
```
oss_framework/dbt/
├── dbt_project.yml       # Project configuration
├── profiles.yml          # Connection settings
├── models/
│   ├── staging/          # Stage 2 (refinement)
│   │   ├── stg_students.sql
│   │   ├── stg_attendance.sql
│   │   └── ...
│   ├── mart_core/        # Core dimensions & facts
│   │   ├── dim_students.sql
│   │   ├── fact_attendance.sql
│   │   └── ...
│   ├── mart_features/    # Feature engineering
│   ├── mart_scoring/     # Risk scores
│   └── mart_analytics/   # Pre-aggregated metrics
├── macros/               # Reusable SQL functions
├── tests/                # Data quality tests
└── seeds/                # Reference data (CSV imports)
```

**Model selection:**
- `dbt run --select tag:staging` - Run Stage 2 only
- `dbt run --select mart_core` - Run core dimensions/facts
- `dbt run --select mart_features+` - Run features + downstream models
- `dbt test` - Run all data quality tests

---

### Rill - Interactive BI Dashboards

**Why Rill?**
- **Local-first**: Runs on localhost, no cloud account required
- **DuckDB-native**: Queries DuckDB directly (no data copying)
- **Fast**: Sub-second query response with pre-aggregation
- **Developer-friendly**: YAML-based dashboard definitions (version controlled)
- **Live refresh**: Auto-reloads when underlying data changes

**Project structure:**
```
local-data-stack/
├── rill.yaml                   # Rill project config
├── connectors/
│   └── duckdb.yaml             # DuckDB connection
├── models/
│   ├── chronic_absenteeism_risk.sql        # SQL model (queries mart_analytics)
│   └── equity_outcomes_by_demographics.sql
└── dashboards/
    ├── chronic_absenteeism_risk.yaml       # Dashboard definition
    └── equity_outcomes_by_demographics.yaml
```

**Dashboard workflow:**
1. **SQL Model** queries DuckDB tables (Stage 3 output)
2. **Metrics View** defines dimensions, measures, time series
3. **Dashboard YAML** configures visualizations, filters, drill-downs
4. **Rill Developer** renders interactive UI at http://localhost:9009

See [RILL_GUIDE.md](RILL_GUIDE.md) for dashboard creation details.

---

### Orchestration - Python Script

**Why simple Python script (not Dagster/Airflow)?**
- **Simplicity**: No scheduler overhead for local use
- **Transparency**: Easy to read, debug, and modify
- **Portability**: Single file, no external dependencies
- **Sufficient**: For daily/weekly batch runs, complexity not needed

**Orchestration script** (`scripts/run_pipeline.py`):
```python
class PipelineOrchestrator:
    def stage1_ingestion(self):
        # Run dlt pipelines
        run("python oss_framework/pipelines/aeries_dlt_pipeline.py")

    def stage2_refinement(self):
        # Run dbt staging models
        run("dbt run --select tag:staging", workdir=dbt_dir)

    def stage3_analytics(self):
        # Run dbt analytics models
        run("dbt run --select mart_core mart_features mart_analytics", workdir=dbt_dir)

    def run_full_pipeline(self):
        # Execute all stages sequentially
        self.stage1_ingestion()
        self.stage2_refinement()
        self.stage3_analytics()
```

**Scheduling options:**
- **Cron** (Linux/macOS): `0 2 * * * cd /path/to/local-data-stack && python scripts/run_pipeline.py`
- **Task Scheduler** (Windows): Daily task at 2:00 AM
- **Manual**: `python scripts/run_pipeline.py` (for on-demand runs)

---

## Comparison with Cloud OEA

| Aspect | Cloud OEA (openedDataEstate) | Local Data Stack |
|--------|------------------------------|------------------|
| **Database** | MotherDuck (cloud DuckDB) | DuckDB (local file) |
| **Storage** | AWS S3 (Parquet/Delta) | Local filesystem (Parquet/Delta) |
| **BI Tool** | Metabase (Kubernetes) | Rill (localhost) |
| **Orchestration** | Dagster (complex) | Python script (simple) |
| **Deployment** | AWS EKS, Terraform | Docker Compose or bare metal |
| **Cost** | MotherDuck subscription + AWS | $0 (hardware only) |
| **Data residency** | Cloud provider (US/EU) | Your infrastructure (100% control) |
| **Internet dependency** | Required for operation | Optional (only for API ingestion) |
| **Scaling** | Horizontal (add nodes) | Vertical (add RAM/CPU) |
| **Best for** | Multi-school districts, SaaS | Single schools, on-prem requirements |

**When to use cloud OEA:**
- Multi-tenant SaaS deployment
- Need horizontal scaling (TB+ data)
- Distributed teams across locations
- Budget for cloud services

**When to use local-data-stack:**
- Data must stay on-premises (compliance, policy)
- Tight budget (no recurring cloud costs)
- Predictable workloads (single school/small district)
- Want full control over infrastructure

---

## Security Architecture

### Data Protection Layers

1. **At Rest**:
   - DuckDB file encrypted with filesystem-level encryption (FileVault, BitLocker, LUKS)
   - Parquet files stored on encrypted volumes
   - Backups encrypted with AES-256 before offsite storage

2. **In Transit**:
   - Aeries API connections over HTTPS (TLS 1.2+)
   - Rill dashboards served over localhost (no network exposure by default)
   - JupyterLab authentication required (token-based)

3. **Access Control**:
   - File permissions: `chmod 600 .env`, `chmod 640 oea.duckdb`
   - User accounts: Separate OS user for pipeline execution
   - Dashboard access: Rill authentication (optional, for production)

4. **Pseudonymization**:
   - `mart_privacy` schema with hashed student IDs
   - FERPA-compliant de-identification (36 data elements removed)
   - Configurable salt for hashing (`PRIVACY_SALT` in `.env`)

See [SECURITY.md](../SECURITY.md) for detailed security guidance.

---

## Performance Characteristics

### Query Performance

**Typical query latency** (on M1 MacBook Pro, 16GB RAM):
- Simple aggregation (COUNT, SUM): **10-50ms**
- Complex join (3-4 tables): **50-200ms**
- Window functions (OVER): **100-500ms**
- Full table scan (1M rows): **500ms-2s**

**Optimization techniques:**
- Run `ANALYZE` after bulk loads to update statistics
- Use `PRAGMA optimize_database` for compaction
- Partition large tables by date (`load_date` for Stage 1)
- Pre-aggregate metrics in Stage 3 (avoid dashboard-time aggregation)
- Index frequently-filtered columns (DuckDB auto-indexes)

### Data Volume Capacity

**Tested workloads:**
- **Small district**: 5,000 students, 5 years history → 2GB database, sub-second queries
- **Medium district**: 20,000 students, 5 years history → 8GB database, 1-3s queries
- **Large district** (projected): 50,000 students, 5 years history → 20GB database, 3-10s queries

**Scaling limits:**
- Single-file DuckDB works well up to **50-100GB** databases
- Memory requirement: **2-4x database size** for complex queries
- Disk I/O becomes bottleneck beyond 100GB (consider NVMe SSD)

---

## Extensibility

### Adding New Data Sources

1. Create new dlt pipeline in `oss_framework/pipelines/`:
   ```python
   # new_source_dlt_pipeline.py
   import dlt

   @dlt.resource
   def new_data_source():
       # Extract logic
       yield data_batch

   pipeline = dlt.pipeline(destination='filesystem')
   pipeline.run(new_data_source())
   ```

2. Add to Stage 2 dbt models (`models/staging/stg_new_source.sql`)

3. Integrate into `scripts/run_pipeline.py`:
   ```python
   def stage1_ingestion(self):
       # ... existing sources ...
       run("python oss_framework/pipelines/new_source_dlt_pipeline.py")
   ```

### Adding New Dashboards

See [RILL_GUIDE.md](RILL_GUIDE.md) for step-by-step dashboard creation.

---

## Troubleshooting Architecture Issues

### "DuckDB database is locked"
**Cause**: Multiple processes accessing the same `.duckdb` file.
**Fix**: Close all DuckDB connections (`pkill -f duckdb`), ensure only one process writes at a time.

### "Memory limit exceeded"
**Cause**: Query requires more memory than `DUCKDB_MEMORY_LIMIT`.
**Fix**: Increase memory limit in `.env` (e.g., `DUCKDB_MEMORY_LIMIT=16GB`) or optimize query (add filters, reduce window size).

### "Slow dashboard loading"
**Cause**: Rill dashboard querying unaggregated Stage 2 data.
**Fix**: Create pre-aggregated Stage 3 model, update Rill SQL model to query Stage 3 instead.

### "dbt model fails with type error"
**Cause**: Schema drift between Stage 1 Parquet and dbt expectations.
**Fix**: Run `dbt run --full-refresh` to rebuild from scratch, or fix schema in dlt pipeline.

---

## Next Steps

- **[SETUP.md](SETUP.md)** - Installation and configuration
- **[RILL_GUIDE.md](RILL_GUIDE.md)** - Creating custom dashboards
- **[SECURITY.md](../SECURITY.md)** - Security best practices
- **[OPERATIONAL_RUNBOOKS.md](../oss_framework/OPERATIONAL_RUNBOOKS.md)** - Production operations

---

## References

- **DuckDB Documentation**: https://duckdb.org/docs/
- **dbt Documentation**: https://docs.getdbt.com/
- **Rill Documentation**: https://docs.rilldata.com/
- **Delta Lake**: https://delta.io/
- **dlt Documentation**: https://dlthub.com/docs/
