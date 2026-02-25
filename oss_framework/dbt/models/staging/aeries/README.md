# Aeries Staging Layer

## Overview

This directory contains staging models for data sourced from the Aeries Student Information System (SIS). Staging models form the foundation of our analytics pipeline, providing cleaned, typed, and lightly transformed data ready for downstream analytics.

## Purpose

The staging layer serves as the standardization and cleaning layer between raw source data and business-logic-heavy marts. Models in this layer:

- Cast data types consistently
- Rename columns to follow naming conventions
- Apply light business logic (flags, categorizations)
- Maintain 1:1 relationship with source tables
- Provide standardized column documentation

## Models

### `stg_aeries__students`
Student demographic and enrollment master data.

**Key Transformations:**
- Age calculation from date of birth
- Boolean flag standardization
- Grade level categorization (Elementary/Middle/High)
- Enrollment status derivation

**Row Count:** 3,400 students  
**Grain:** One row per student

### `stg_aeries__attendance`
Daily attendance records with temporal attributes.

**Key Transformations:**
- Temporal fields (day of week, school quarter, weekend flag)
- Attendance status flags (present/absent/tardy/excused)
- Consistency validation between status and flags

**Row Count:** ~90,000 records  
**Grain:** One row per student per attendance date

### `stg_aeries__academic_records`
Course grades and academic performance data.

**Key Transformations:**
- GPA conversion (4.0 scale calculation)
- Pass/fail flag (70% threshold)
- Letter grade validation
- Grade category assignment

**Row Count:** Varies by term  
**Grain:** One row per student per course per term

### `stg_aeries__discipline`
Student discipline incidents and consequences.

**Key Transformations:**
- Severity standardization (Low/Medium/High)
- Suspension flag derivation
- Incident type categorization

**Row Count:** ~4,000 incidents  
**Grain:** One row per incident

### `stg_aeries__enrollment`
Student course enrollment tracking.

**Key Transformations:**
- Enrollment status derivation from dates
- Active/withdrawn status calculation

**Row Count:** Varies by term  
**Grain:** One row per student enrollment record

## Naming Convention

All models follow the pattern: `stg_<source>__<entity>`

- `stg_` prefix identifies staging layer
- `aeries` indicates source system
- Double underscore `__` separates source from entity
- Entity name matches source table (singular form)

## Data Quality

### Tests Implemented

All staging models include:

**Uniqueness Tests:**
- Primary key uniqueness (e.g., `student_id_raw`, `attendance_id`)

**Not Null Tests:**
- Foreign keys
- Required business fields
- Date fields

**Accepted Values Tests:**
- Categorical fields (grade levels, gender, enrollment status)
- Severity levels
- Status flags

**Relationship Tests:**
- Foreign key integrity to `stg_aeries__students`

**Test Coverage:** 43 tests across 5 models (100% coverage)

### Source Freshness

Freshness checks monitor data recency:

- **Most tables:** Warn after 48 hours, error after 7 days
- **Student master:** Warn after 7 days, error after 14 days

Run: `dbt source freshness`

## Column Naming Standards

Staging models follow these conventions:

### Raw PII Fields
Suffix with `_raw` to indicate unprocessed personally identifiable information:
- `student_id_raw`
- `first_name_raw`
- `last_name_raw`
- `date_of_birth_raw`

These fields are hashed downstream in `mart_privacy` models.

### Calculated Fields
Descriptive names indicating transformation:
- `age_years` (calculated from DOB)
- `is_currently_enrolled` (derived from dates)
- `grade_level_category` (Elementary/Middle/High)
- `day_of_week_name`, `day_of_week_number`

### Boolean Flags
Suffix with `_flag` for clarity:
- `present_flag`, `absent_flag`
- `special_education_flag`
- `is_weekend` (exception: prefix with `is_` for readability)

### Temporal Fields
Standard suffixes:
- `_date` for DATE types
- `_at` for TIMESTAMP types
- `_timestamp` for dbt metadata

## Best Practices

### When to Use Staging Models

✅ **DO use staging for:**
- Type casting and parsing
- Renaming columns to standards
- Deduplication
- Light categorical transformations
- Flag calculations from source fields

❌ **DO NOT use staging for:**
- Complex business logic (use intermediate models)
- Aggregations (use marts)
- Joins across sources (use marts)
- PII hashing (use privacy layer)

### Model Structure

Each staging model follows this structure:

```sql
{{ config(
    materialized='view',
    schema='staging'
) }}

SELECT
    -- Primary/Foreign Keys
    field_id,
    
    -- Natural Keys (Raw PII)
    field_name_raw,
    
    -- Attributes
    field_category,
    
    -- Calculated Fields
    CASE ... END as derived_field,
    
    -- Metadata
    created_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp
    
FROM {{ source('raw', 'raw_table') }}
```

### Documentation Requirements

Every staging model must have:

1. **Model-level description** in `_aeries__models.yml`
2. **Column descriptions** for all fields
3. **Data tests** on keys and critical fields
4. **Relationship tests** for foreign keys

## Maintenance

### Adding New Source Tables

When adding a new Aeries source:

1. Add table definition to `models/sources.yml`
2. Create staging model: `stg_aeries__<table>.sql`
3. Add tests and docs to `_aeries__models.yml`
4. Run: `dbt run --select stg_aeries__<table>`
5. Run: `dbt test --select stg_aeries__<table>`

### Updating Existing Models

When modifying staging models:

1. Update SQL transformation
2. Update column documentation in YAML
3. Add/update tests as needed
4. Run full build: `dbt build --select stg_aeries__<table>`
5. Verify downstream marts still pass

### Performance Considerations

Staging models are materialized as **views** by default because:
- They're lightweight transformations
- Keep data fresh (no lag)
- Minimize storage costs
- Changes propagate immediately

Consider **table** materialization if:
- Source queries are slow (rare for Parquet)
- Model has complex calculations
- Downstream marts reference it heavily

## Related Documentation

- [sources.yml](../../sources.yml) - Source table definitions
- [_aeries__models.yml](./_aeries__models.yml) - Model tests and documentation
- [mart_core/](../../mart_core/) - Business logic layer
- [mart_privacy/](../../mart_privacy/) - PII pseudonymization

## Metrics

**Current State:**
- ✅ 5 staging models
- ✅ 43 data tests (100% passing)
- ✅ Source freshness monitoring enabled
- ✅ 100% column documentation coverage
- ✅ dbt 1.11 compliant (no deprecation warnings)

Last Updated: 2026-01-28
