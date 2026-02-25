# OSS Framework: Data Lake Architecture
## Education Analytics Platform

**Version**: 1.0  
**Date**: January 27, 2026  
**Status**: Foundation Document

---

## Executive Summary

The OSS Framework uses a **three-stage data lake architecture** specifically designed for education analytics. This proven pattern provides:

- **Clear separation of concerns** between data ingestion, refinement, and publication
- **Privacy-first design** with pseudonymization at the ingest stage
- **Scalability** from small districts to large multi-state implementations
- **Auditability** with full data lineage tracking
- **Compliance** with FERPA, GDPR, and other data privacy regulations

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│    (SIS, LMS, Identity, Attendance, Assessment Systems)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               PRE-LANDING / RAW DATA ZONE                       │
│  • External data copies                                         │
│  • No transformation                                            │
│  • Short retention (7-30 days)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
      Pipeline: 1_preland_*.json (Copy external sources)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         STAGE 1: LANDING (Raw/Transactional)                   │
│  • Raw data ingestion                                           │
│  • Minimal transformation                                       │
│  • Preserves original structure                                 │
│  • Retention: Current + 1-2 years                               │
│                                                                  │
│  Tables: raw_students, raw_courses, raw_enrollment, etc.       │
└────────────────────────┬────────────────────────────────────────┘
                         │
      Pipeline: 2_land_*.json (Ingest and organize)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│      STAGE 2A: INGESTED (Flattened/Normalized)                │
│  • JSON flattening                                              │
│  • Schema normalization                                         │
│  • Standard naming conventions                                  │
│  • Retention: Current + 1-2 years                               │
│                                                                  │
│  Tables: students, courses, enrollment, etc.                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
      Pipeline: 3_ingest_*.json (Transform and pseudonymize)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│      STAGE 2B: REFINED (Business Logic Applied)                │
│  • Privacy-preserving transformations                           │
│  • Pseudonymization (hash, mask, no-op per metadata)           │
│  • Feature engineering                                          │
│  • Business rule application                                    │
│  • Retention: Current + 2-3 years                               │
│                                                                  │
│  Tables: dim_students, fact_enrollment, metric_engagement, etc.│
└────────────────────────┬────────────────────────────────────────┘
                         │
      Pipeline: 4_refine_*.json (Aggregate and publish)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│     STAGE 3: PUBLISHED (Analytics-Ready Views)                 │
│  • Aggregated metrics                                           │
│  • SQL views for BI consumption                                 │
│  • Dimensional models                                           │
│  • Retention: Current + 3+ years (archival)                     │
│                                                                  │
│  Views: v_student_demographics, v_engagement_metrics, etc.     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          BI LAYER (Dashboards & Reporting)                     │
│    • Grafana dashboards                                         │
│    • Apache Superset analytics                                  │
│    • Metabase exploration                                       │
│    • Custom applications                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stage Definitions

### Pre-Landing / Raw Zone

**Purpose**: Temporary storage for external data copies before processing

**Characteristics**:
- Direct copy from external sources
- No transformation or validation
- Fast ingestion without dependencies
- Short retention window (7-30 days)
- Can be re-copied if needed

**Access Pattern**:
- Write: Automated pipeline (1_preland)
- Read: Pipeline 2_land only
- User Access: Restricted (data pipeline team only)

**Example Data**:
```
pre_landing/
├── student_information_system/
│   ├── students_2026-01-27.json
│   ├── courses_2026-01-27.json
│   └── enrollment_2026-01-27.json
├── learning_management_system/
│   ├── user_activity_2026-01-27.json
│   └── course_engagement_2026-01-27.json
└── directory_service/
    └── users_2026-01-27.json
```

---

### Stage 1: Landing (Raw/Transactional)

**Purpose**: Organized, queryable raw data with minimal transformation

**Characteristics**:
- Data organized by logical entity (students, courses, etc.)
- Raw from source systems (before normalization)
- Preserves original structure and naming
- Clear lineage to pre-landing data
- Includes all historical records

**Transformation Applied**:
- Copy/move to organized structure
- Basic data type conversion if needed
- Optional: Decompression, JSON array expansion
- Schema validation

**Access Pattern**:
- Write: Pipeline 2_land
- Read: Marimo notebooks, data analysis team
- User Access: Technical users (data engineers, analysts)

**Example Schema** (PostgreSQL):
```sql
-- Stage 1: Raw data tables
CREATE TABLE stage1_landing.raw_students (
    source_id VARCHAR PRIMARY KEY,
    student_id VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    date_of_birth DATE,
    -- All original fields preserved
    _loaded_date TIMESTAMP,
    _source_system VARCHAR
);

CREATE TABLE stage1_landing.raw_enrollment (
    source_id VARCHAR PRIMARY KEY,
    enrollment_id VARCHAR,
    student_id VARCHAR,
    course_id VARCHAR,
    term VARCHAR,
    enrollment_date DATE,
    -- All original fields preserved
    _loaded_date TIMESTAMP
);
```

---

### Stage 2A: Ingested (Flattened/Normalized)

**Purpose**: Standardized, queryable data with consistent schema

**Characteristics**:
- Flattened JSON structures
- Normalized naming conventions (snake_case)
- Single source of truth for each entity
- Consistent data types
- No pseudonymization yet

**Transformation Applied**:
- JSON flattening (nested → flat)
- Schema normalization
- Field renaming (CamelCase → snake_case)
- Optional: Deduplication, type casting
- Schema validation against metadata

**Access Pattern**:
- Write: Pipeline 3_ingest
- Read: Feature engineering notebooks, refinement pipelines
- User Access: Data engineers, analysts

**Example Schema** (PostgreSQL):
```sql
-- Stage 2A: Ingested/normalized data
CREATE TABLE stage2a_ingested.students (
    student_key VARCHAR PRIMARY KEY,
    student_id VARCHAR UNIQUE,
    first_name VARCHAR,
    last_name VARCHAR,
    date_of_birth DATE,
    grade_level INT,
    school_id VARCHAR,
    cohort_year INT,
    -- Consistent naming, no PII masking yet
    _loaded_date TIMESTAMP,
    _updated_date TIMESTAMP
);

CREATE TABLE stage2a_ingested.engagement_events (
    engagement_key VARCHAR PRIMARY KEY,
    student_id VARCHAR,
    event_type VARCHAR,
    event_timestamp TIMESTAMP,
    course_id VARCHAR,
    duration_minutes INT,
    resource_id VARCHAR,
    _loaded_date TIMESTAMP
);
```

---

### Stage 2B: Refined (Business Logic Applied)

**Purpose**: Privacy-safe, business-ready data with features and pseudonymization

**Characteristics**:
- Privacy-preserving transformations applied
- Pseudonymization per metadata rules
- Feature engineering completed
- Business logic applied
- Ready for analytics but not full publication

**Transformation Applied**:
- Pseudonymization (hash, mask, no-op based on metadata)
- Feature engineering (aggregations, ratios, indicators)
- Business rule application
- Dimension table creation
- Fact table aggregation

**Access Pattern**:
- Write: Pipeline 4_refine
- Read: BI layer, published views
- User Access: Analysts, BI tools (restricted fields only)

**Example Schema** (PostgreSQL):
```sql
-- Stage 2B: Refined/pseudonymized data
CREATE TABLE stage2b_refined.dim_students (
    student_key VARCHAR PRIMARY KEY,
    student_hash VARCHAR,  -- Pseudonymized student ID
    grade_level INT,
    school_id VARCHAR,
    cohort_year INT,
    special_education BOOLEAN,
    English_learner BOOLEAN,
    economically_disadvantaged BOOLEAN,
    -- Other demographic fields (kept as-is or masked)
    _loaded_date TIMESTAMP,
    _rule_version VARCHAR
);

CREATE TABLE stage2b_refined.fact_engagement (
    fact_engagement_key VARCHAR PRIMARY KEY,
    student_hash VARCHAR,  -- Pseudonymized
    month_year DATE,
    course_id VARCHAR,
    event_count INT,
    avg_duration_minutes FLOAT,
    resource_access_count INT,
    assignments_submitted INT,
    _loaded_date TIMESTAMP
);

-- Metadata defining privacy rules
CREATE TABLE stage2b_refined.metadata_schema (
    entity VARCHAR,
    attribute VARCHAR,
    data_type VARCHAR,
    pseudonymization VARCHAR,  -- hash, mask, no-op
    description VARCHAR
);
```

---

### Stage 3: Published (Analytics-Ready Views)

**Purpose**: Curated views for BI consumption and external reporting

**Characteristics**:
- SQL views (not tables, for freshness)
- Fact/dimension star schema
- Fully aggregated and summarized
- Ready for Grafana/Superset/Metabase
- Includes PII-removed aggregations

**Transformation Applied**:
- View creation from Stage 2B tables
- Additional aggregations (district, school, grade level)
- KPI calculations
- Dimension lookups
- Trend calculations

**Access Pattern**:
- Write: View definitions only (no writes)
- Read: BI tools, external reporting
- User Access: Everyone (appropriate filters applied by BI tool)

**Example Schema** (PostgreSQL):
```sql
-- Stage 3: Published views for BI
CREATE VIEW stage3_published.v_student_engagement_summary AS
SELECT
    school_id,
    month_year,
    COUNT(DISTINCT student_hash) as active_students,
    AVG(event_count) as avg_events_per_student,
    SUM(assignments_submitted) as total_assignments,
    ROUND(100.0 * SUM(CASE WHEN event_count > 0 THEN 1 ELSE 0 END) 
        / COUNT(DISTINCT student_hash), 1) as engagement_pct
FROM stage2b_refined.fact_engagement
GROUP BY school_id, month_year
ORDER BY month_year DESC;

CREATE VIEW stage3_published.v_enrollment_by_grade AS
SELECT
    school_id,
    grade_level,
    COUNT(*) as student_count,
    COUNT(CASE WHEN special_education THEN 1 END) as sped_count,
    COUNT(CASE WHEN english_learner THEN 1 END) as el_count
FROM stage2b_refined.dim_students
GROUP BY school_id, grade_level
ORDER BY school_id, grade_level;
```

---

## Key Concepts

### 1. Data Lineage & Traceability

Every row includes metadata tracking:

```sql
-- All Stage 1 tables include
_loaded_date TIMESTAMP        -- When data was loaded
_source_system VARCHAR        -- Where it came from
_source_file VARCHAR          -- Which file/export

-- All Stage 2 tables include
_loaded_date TIMESTAMP        -- Transformation timestamp
_updated_date TIMESTAMP       -- Last update
_rule_version VARCHAR         -- Metadata version used
```

This enables:
- Audit trails for compliance
- Debugging transformation issues
- Validating data freshness
- Identifying affected data on schema changes

### 2. Privacy-First Design

**Pseudonymization Metadata** (`metadata_schema.csv`):
```csv
Entity,Attribute,DataType,Pseudonymization,Description
students,student_id,VARCHAR,hash,Student identifier - hashed
students,first_name,VARCHAR,mask,Student first name - masked
students,grade_level,INT,no-op,Grade level - not sensitive
courses,course_id,VARCHAR,no-op,Course identifier
```

**Rules**:
- `hash`: Cryptographic hash (one-way), enables lookup table
- `mask`: Irreversible masking (replaces with *)
- `no-op`: Keep as-is (not sensitive)

### 3. Multi-Environment Configuration

Separate configurations for each environment:

```
oss_framework/config/
├── dev.yaml          # Development (full unmasked data)
├── test.yaml         # Testing (synthetic/masked data)
├── staging.yaml      # Pre-production (masked PII)
└── prod.yaml         # Production (full pseudonymization)
```

Each config specifies:
- Database connection strings
- Data retention periods
- Pseudonymization rules
- Pipeline schedules
- Alert thresholds

### 4. Retention Policies

Different stages have different retention windows:

| Stage | Raw/Pre-landing | Stage 1 | Stage 2 | Stage 3 |
|-------|---|---|---|---|
| **Typical Retention** | 7-30 days | 1-2 years | 2-3 years | 3+ years |
| **Purpose** | Temporary copy | Source of truth | Analytics | Reporting/Archival |
| **Cost** | Low | Medium | Higher | Archived |

Policies are configurable per environment and use case.

### 5. Batch Processing Patterns

Three batch processing modes supported:

**Delta Batch** (Recommended for transactional data):
```
Daily/Hourly: Load only changed records
- Identify: WHERE _updated_date > last_load_time
- Merge into Stage 1 (upsert)
- More efficient, faster loads
```

**Additive Batch** (For event logs, engagement data):
```
Append-only: Load new events
- No updates to existing records
- Only INSERT operations
- Enables time-series analysis
```

**Snapshot Batch** (For periodic full exports):
```
Full replacement: Replace entire dataset
- Complete re-export from source
- TRUNCATE and LOAD
- Used when partial loads unavailable
```

---

## Configuration Templates

### Environment Configuration (`config/dev.yaml`)

```yaml
environment: development

database:
  host: localhost
  port: 5432
  database: education_analytics_dev
  ssl: false

storage:
  type: local  # or s3, azure_blob
  path: /data/analytics
  pre_landing: /data/analytics/pre_landing
  stage1: /data/analytics/stage1
  stage2: /data/analytics/stage2
  stage3: /data/analytics/stage3

pipelines:
  pre_landing:
    retention_days: 7
    schedule: "daily at 2am"
  stage1:
    retention_years: 2
    batch_mode: delta  # delta, additive, snapshot
  stage2:
    retention_years: 3
  stage3:
    retention_years: 5  # Indefinite archival

privacy:
  pseudonymization_rules_file: metadata/schema.csv
  hash_salt: "${HASH_SALT_ENV_VAR}"
  mask_character: "*"
  allow_unmasked_access: true  # Dev only

logging:
  level: DEBUG
  destination: file
  path: /var/log/analytics/
```

### Data Retention Policy

```yaml
retention_policy:
  pre_landing:
    window: 30 days
    archive: no
    purpose: "Temporary staging for data validation"
  
  stage1:
    window: 730 days  # 2 years
    archive: after_retention
    purpose: "Source of truth raw data"
  
  stage2:
    window: 1095 days  # 3 years
    archive: after_retention
    purpose: "Analytics-ready data"
  
  stage3:
    window: indefinite
    archive: yearly_snapshots
    purpose: "Published views and reporting"
```

---

## Implementation Checklist

- [ ] Define storage backend (local, cloud, data warehouse)
- [ ] Configure database schemas for all 4 stages
- [ ] Create metadata schema table with privacy rules
- [ ] Set up environment-specific configurations
- [ ] Define data retention policies
- [ ] Create directory structures and naming conventions
- [ ] Implement logging and auditing
- [ ] Set up monitoring and alerting
- [ ] Document access controls and permissions
- [ ] Create backup and recovery procedures

---

## Next Steps

1. **Storage Backend**: Decide on database technology (PostgreSQL, Snowflake, BigQuery, etc.)
2. **Pipeline Templates**: Create JSON-based pipeline definitions (covered in next section)
3. **Utilities Library**: Build Python functions for common transformations
4. **Metadata System**: Implement schema and privacy rule management
5. **Testing**: Develop validation framework for each stage

---

## References

- Open Education Analytics (OEA) Architecture
- Modern Data Lake Design Patterns
- FERPA Compliance Guidelines
- GDPR Pseudonymization Best Practices
