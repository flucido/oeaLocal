# AeRIES → MotherDuck Implementation Plan

**Date**: February 22, 2026  
**Project**: OpenED Data Estate  
**Dataset**: AeRIES Student Information System Data (2020-2026)

---

## Executive Summary

✅ **Assessment Complete**: AeRIES dataset is perfectly suited for DuckDB/MotherDuck transformation  
✅ **Infrastructure**: Existing DuckDB + Delta Lake setup ready  
✅ **Data Quality**: Pre-transformed attendance and discipline data (no JSON unnesting needed)  
📦 **Scope**: 6 years of data, 7 domains, ~30K records across all tables

---

## Dataset Inventory

### Available Data Domains

| Domain | Years Available | Records (2023-24) | Files | Status |
|--------|----------------|-------------------|-------|--------|
| **Students** | 2020-2026 | 849 | CSV (80+ columns) | ✅ Ready |
| **Attendance (Transformed)** | 2020-2026 | 834 | CSV (flattened) | ✅ Ready |
| **Grades (Transformed)** | 2020-2026 | 25,845 | CSV (course-level) | ✅ Ready |
| **Discipline (Transformed)** | 2020-2026 | 361 | CSV (flattened) | ✅ Ready |
| **Enrollment** | 2020-2022 | ~900/year | CSV | ⚠️ Partial |
| **Programs** | 2020-2026 | TBD | CSV | ✅ Ready |
| **GPA** | 2020-2026 | TBD | CSV | ✅ Ready |

**Source Path**: `/Users/flucido/Desktop/AeRIES test data/`

### Key Schema Elements

**Common Keys:**
- `StudentID` - Primary identifier across all domains
- `AcademicYear` - Time dimension (format: "YYYY-YYYY")
- `SchoolCode` - School identifier
- `ExtractedAt` - Data extraction timestamp

**Data Patterns:**
- ✅ Transformed attendance/discipline (no nested JSON)
- ✅ Consistent column naming
- ✅ Year-based files for partitioning
- ✅ Comprehensive student demographics

---

## Architecture Design

### Target Schema: Star Schema

```
┌─────────────────────────────────────────────────────────────┐
│                    FACT TABLES                               │
├─────────────────────────────────────────────────────────────┤
│ fact_enrollments                                            │
│   - enrollment_key (PK)                                     │
│   - student_key (FK → dim_students)                         │
│   - school_key (FK → dim_schools)                           │
│   - enter_date_key (FK → dim_dates)                         │
│   - leave_date_key (FK → dim_dates)                         │
│   - grade, track, exit_reason                               │
├─────────────────────────────────────────────────────────────┤
│ fact_attendance                                             │
│   - attendance_key (PK)                                     │
│   - student_key (FK → dim_students)                         │
│   - school_year_key (FK → dim_dates)                        │
│   - school_key (FK → dim_schools)                           │
│   - days_enrolled, days_present, days_absent                │
│   - days_tardy, days_suspended, days_truancy                │
├─────────────────────────────────────────────────────────────┤
│ fact_grades                                                 │
│   - grade_key (PK)                                          │
│   - student_key (FK → dim_students)                         │
│   - course_key (FK → dim_courses)                           │
│   - marking_period, mark, credit                            │
│   - attendance metrics (absences, tardies)                  │
├─────────────────────────────────────────────────────────────┤
│ fact_discipline                                             │
│   - incident_key (PK)                                       │
│   - student_key (FK → dim_students)                         │
│   - incident_date_key (FK → dim_dates)                      │
│   - school_key (FK → dim_schools)                           │
│   - violation_code, disposition, days_assigned              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   DIMENSION TABLES                           │
├─────────────────────────────────────────────────────────────┤
│ dim_students (Type 2 SCD)                                   │
│   - student_key (surrogate PK)                              │
│   - student_id (natural key)                                │
│   - first_name, last_name, gender, birthdate                │
│   - ethnicity, race_codes, language                         │
│   - current_grade, current_school                           │
│   - valid_from, valid_to, is_current                        │
│   - version                                                 │
├─────────────────────────────────────────────────────────────┤
│ dim_schools                                                 │
│   - school_key (PK)                                         │
│   - school_code (natural key)                               │
│   - school_name, district_code                              │
├─────────────────────────────────────────────────────────────┤
│ dim_courses                                                 │
│   - course_key (PK)                                         │
│   - course_id (natural key)                                 │
│   - course_title, department                                │
├─────────────────────────────────────────────────────────────┤
│ dim_dates                                                   │
│   - date_key (PK, YYYYMMDD)                                 │
│   - date, academic_year, quarter, month                     │
│   - is_school_day, day_of_week                              │
├─────────────────────────────────────────────────────────────┤
│ dim_programs                                                │
│   - program_key (PK)                                        │
│   - program_code (natural key)                              │
│   - program_description                                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ STAGE 1: INGESTION                                           │
│ Source: /Users/flucido/Desktop/AeRIES test data/*.csv       │
│ Target: stage1/aeries/{domain}/year={YYYY-YYYY}/*.parquet   │
│                                                              │
│ Process:                                                     │
│ 1. Read CSV files per domain/year                           │
│ 2. Validate schemas                                          │
│ 3. Convert to Parquet (ZSTD compression, level 5)           │
│ 4. Partition by AcademicYear                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STAGE 2: DUCKDB VIEWS (Raw Layer)                           │
│ Target: DuckDB views in oea.duckdb                           │
│                                                              │
│ Views:                                                       │
│ - raw_aeries_students                                        │
│ - raw_aeries_attendance                                      │
│ - raw_aeries_grades                                          │
│ - raw_aeries_discipline                                      │
│ - raw_aeries_enrollment                                      │
│ - raw_aeries_programs                                        │
│ - raw_aeries_gpa                                             │
│                                                              │
│ Pattern: CREATE VIEW raw_aeries_X AS                         │
│          SELECT * FROM read_parquet('stage1/...')            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STAGE 3: DBT TRANSFORMATIONS (Silver/Gold Layers)           │
│ Target: Materialized tables in DuckDB                       │
│                                                              │
│ Models:                                                      │
│ - dimensions/dim_students.sql (Type 2 SCD)                   │
│ - dimensions/dim_schools.sql                                 │
│ - dimensions/dim_courses.sql                                 │
│ - dimensions/dim_dates.sql                                   │
│ - dimensions/dim_programs.sql                                │
│ - facts/fact_enrollments.sql                                 │
│ - facts/fact_attendance.sql                                  │
│ - facts/fact_grades.sql                                      │
│ - facts/fact_discipline.sql                                  │
│                                                              │
│ Tests: Schema validation, referential integrity, nulls       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ STAGE 4: MOTHERDUCK PUBLICATION (Optional)                  │
│ Target: MotherDuck cloud database                           │
│                                                              │
│ Connection: md:{database_name}                               │
│ Authentication: MOTHERDUCK_TOKEN from .env                   │
│                                                              │
│ Published Tables:                                            │
│ - All dimension tables                                       │
│ - All fact tables                                            │
│ - Pre-aggregated summary tables                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Phase 1: Configuration & Setup (Day 1)

**Task 1.1: MotherDuck Configuration**
- [ ] Create `.env.example` with MotherDuck template
- [ ] Document required environment variables
- [ ] Add MotherDuck connection to `src/db/connection.py`

**Task 1.2: Project Structure**
- [ ] Create `stage1/aeries/` directory structure
- [ ] Create `oss_framework/dbt/models/aeries/` for dbt models
- [ ] Set up logging for pipeline runs

### Phase 2: Data Ingestion (Days 2-3)

**Task 2.1: Ingestion Pipeline**
- [ ] Create `oss_framework/pipelines/aeries_to_parquet.py`
- [ ] Implement CSV → Parquet conversion with year partitioning
- [ ] Add schema validation
- [ ] Handle all 7 domains (students, attendance_transformed, grades_transformed, discipline_transformed, enrollment, programs, gpa)

**Task 2.2: DuckDB Views**
- [ ] Extend `sync_raw_views_from_stage1.py` for AeRIES data
- [ ] Create 7 raw views reading from Parquet
- [ ] Test query performance

### Phase 3: Star Schema (Days 4-6)

**Task 3.1: Dimension Tables**
- [ ] `dim_students.sql` - Type 2 SCD implementation
- [ ] `dim_schools.sql` - School master data
- [ ] `dim_courses.sql` - Course catalog
- [ ] `dim_dates.sql` - Date dimension with academic calendar
- [ ] `dim_programs.sql` - Program master data

**Task 3.2: Fact Tables**
- [ ] `fact_enrollments.sql` - Student enrollment events
- [ ] `fact_attendance.sql` - Attendance summaries
- [ ] `fact_grades.sql` - Course grades
- [ ] `fact_discipline.sql` - Discipline incidents

**Task 3.3: dbt Tests**
- [ ] Schema tests (not_null, unique, relationships)
- [ ] Data quality tests (valid date ranges, grade levels)
- [ ] Referential integrity tests

### Phase 4: MotherDuck Integration (Day 7)

**Task 4.1: Connection Setup**
- [ ] Configure MotherDuck authentication
- [ ] Test connection with sample query
- [ ] Document connection patterns

**Task 4.2: Table Publication**
- [ ] Publish dimension tables to MotherDuck
- [ ] Publish fact tables to MotherDuck
- [ ] Verify data integrity after publish

### Phase 5: Documentation & Testing (Day 8)

**Task 5.1: Documentation**
- [ ] Data dictionary with all columns
- [ ] Schema diagrams (ERD)
- [ ] Query examples for common use cases
- [ ] README for pipeline execution

**Task 5.2: End-to-End Testing**
- [ ] Full pipeline run (CSV → Parquet → DuckDB → MotherDuck)
- [ ] Query performance benchmarks
- [ ] Data quality validation report

---

## Technical Specifications

### File Formats

**Source**: CSV (provided)  
**Stage 1**: Parquet with ZSTD compression (level 5)  
**Stage 2/3**: DuckDB tables in `oea.duckdb`  
**Stage 4**: MotherDuck DuckLake format

### Partitioning Strategy

```
stage1/aeries/
├── students/
│   ├── year=2020-2021/students.parquet
│   ├── year=2021-2022/students.parquet
│   ├── year=2022-2023/students.parquet
│   ├── year=2023-2024/students.parquet
│   ├── year=2024-2025/students.parquet
│   └── year=2025-2026/students.parquet
├── attendance_transformed/
│   └── year=YYYY-YYYY/*.parquet
├── grades_transformed/
│   └── year=YYYY-YYYY/*.parquet
└── ... (other domains)
```

### Naming Conventions

**Raw Views**: `raw_aeries_{domain}`  
**Dimension Tables**: `dim_{entity}`  
**Fact Tables**: `fact_{event_type}`  
**Keys**: `{entity}_key` (surrogate), `{entity}_id` (natural)

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Ingestion Speed** | < 5 min for all years | CSV → Parquet conversion |
| **View Creation** | < 30 sec | DuckDB views over Parquet |
| **dbt Run Time** | < 10 min | All models + tests |
| **Query Performance** | < 1 sec | Typical analytical queries |
| **Storage Compression** | 70-80% | CSV → Parquet with ZSTD |

---

## Data Quality Checks

### Schema Validation
- [ ] All expected columns present
- [ ] Data types match specifications
- [ ] No unexpected null values in required fields

### Referential Integrity
- [ ] All StudentIDs in fact tables exist in dim_students
- [ ] All SchoolCodes exist in dim_schools
- [ ] All CourseIDs exist in dim_courses

### Business Rules
- [ ] AcademicYear format: "YYYY-YYYY"
- [ ] Grade levels: K-12 or valid codes
- [ ] Dates in valid ranges (not future, not before 1900)
- [ ] Attendance: days_present + days_absent ≤ days_enrolled

---

## MotherDuck Configuration

### Environment Variables

```bash
# .env
MOTHERDUCK_TOKEN=your_token_here
MOTHERDUCK_DATABASE=aeries_data_mart
DUCKDB_DATABASE_PATH=data/oea.duckdb
AERIES_SOURCE_PATH=/Users/flucido/Desktop/AeRIES test data
STAGE1_PATH=stage1/aeries
```

### Connection Pattern

```python
import duckdb
import os

# Local DuckDB
conn_local = duckdb.connect(os.getenv('DUCKDB_DATABASE_PATH'))

# MotherDuck
motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
motherduck_db = os.getenv('MOTHERDUCK_DATABASE')
conn_md = duckdb.connect(f'md:{motherduck_db}?motherduck_token={motherduck_token}')

# Publish to MotherDuck
conn_md.execute("CREATE TABLE dim_students AS SELECT * FROM oea.dim_students")
```

---

## Next Steps

1. **Review & Approve** this implementation plan
2. **Provide MotherDuck credentials** via `.env` file
3. **Execute Phase 1** (Configuration & Setup)
4. **Iterate through phases** with validation at each step

---

## Success Criteria

✅ All 7 AeRIES domains ingested to Parquet  
✅ DuckDB views created and queryable  
✅ Star schema implemented with Type 2 SCD  
✅ All dbt tests passing  
✅ Data published to MotherDuck  
✅ Query performance < 1 second for common queries  
✅ Documentation complete with examples

---

## References

- [DuckDB Documentation](https://duckdb.org/docs/)
- [MotherDuck Documentation](https://motherduck.com/docs/)
- [dbt Best Practices](https://docs.getdbt.com/best-practices)
- [Kimball Star Schema](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)
- Research: `research/motherduck_duckdb_research.md`
