# MotherDuck & DuckDB Data Lake/Data Mart Research
**Educational Operations Data - Best Practices & Recommendations**
*Research Date: February 22, 2026*

---

## 1. MotherDuck Architecture & Capabilities

### 1.1 Core Architecture Concepts
- **Isolated Compute Tenancy**: Each user gets their own "duckling" (isolated compute) on top of MotherDuck storage layer
- **Aggressively Serverless**: Auto-scales compute, minimal operational overhead
- **DuckLake Integration**: Open table format (MIT license) for petabyte-scale workloads with ACID compliance
- **Current Compatibility**: DuckDB 1.4.4 (as of Feb 2026)

### 1.2 Data Ingestion Options
MotherDuck supports multiple ingestion patterns:
- **dlt** (Data Load Tool): Python library for extracting from REST APIs, SQL databases, cloud storage
- **Streamkap**: CDC (Change Data Capture) platform for streaming operational data
- **Airbyte**: General data integration platform
- **Artie**: Fully managed CDC for real-time replication

**Recommendation**: For educational data (SIS exports, attendance, grades), batch ingestion via dlt or direct Parquet loading is most appropriate.

---

## 2. DuckLake Table Format

### 2.1 Why DuckLake vs Delta/Iceberg
DuckLake innovates by storing **metadata in database tables** rather than files:
- Faster lookups via database indexes
- More efficient partition pruning via SQL queries
- Simpler architecture (fewer metadata files)
- Full ACID compliance with transaction management

### 2.2 Key Features
```sql
-- Partitioning by function-derived columns
ALTER TABLE student_enrollments 
SET PARTITIONED BY (year(enrollment_date), month(enrollment_date));

-- Time travel / point-in-time queries
SELECT * FROM student_enrollments FOR SYSTEM_TIME AS OF '2026-01-15';

-- Change data feed (track modifications)
SELECT * FROM table_changes('enrollments', now() - INTERVAL '1 week', now());
```

### 2.3 Schema Evolution Support
- Add/drop columns tracked across snapshots
- Historical queries use appropriate schema version
- Default values applied when querying older data with new columns

---

## 3. File Format Recommendations

### 3.1 Parquet Best Practices

**File Sizing** (from DuckDB docs):
- **Optimal range**: 100 MB - 10 GB per file
- DuckDB parallelizes across multiple files
- Ensure row groups ≥ number of CPU threads for full parallelism
- Example: 10 files × 1 row group each = 10-thread parallelism

**Compression & Row Groups**:
```sql
COPY (SELECT * FROM staging_students) 
TO 'students.parquet' (
    COMPRESSION 'zstd',
    COMPRESSION_LEVEL 5,
    ROW_GROUP_SIZE_BYTES '256MB'
);
```

**Compression Options**:
- `zstd` (Zstandard): Best balance of speed and compression ratio
- Compression level 5: Good default (1-22 scale)
- Row group size: 256MB works well for analytical queries

### 3.2 Partitioned Writes

For time-series educational data (attendance, grades):
```sql
COPY attendance_records 
TO 'attendance/' (
    FORMAT parquet,
    PARTITION_BY (year, month)
);
```

Creates directory structure:
```
attendance/
  year=2025/month=09/data_001.parquet
  year=2025/month=10/data_001.parquet
  year=2026/month=01/data_001.parquet
```

**Benefits**:
- Query-time partition pruning (skip irrelevant files)
- Faster queries on recent data
- Efficient incremental updates

---

## 4. Schema Design for Educational Data

### 4.1 Star Schema Approach

Star schema is the **industry standard** for analytical data warehouses:
- Central **fact tables** (transactions/events)
- Surrounding **dimension tables** (descriptive attributes)
- Optimized for query performance and user comprehension
- Denormalized for fast aggregations

**Structure**:
```
        dim_date
            |
        dim_student ---- fact_enrollments ---- dim_program
            |                   |
        dim_school         dim_course
```

### 4.2 Fact Table Design

**Fact tables store measurements/events** (attendance, grades, enrollments):

```sql
CREATE TABLE fact_attendance (
    attendance_key BIGINT PRIMARY KEY,  -- Surrogate key
    student_key INTEGER,                -- FK to dim_student
    date_key INTEGER,                   -- FK to dim_date  
    school_key INTEGER,                 -- FK to dim_school
    course_key INTEGER,                 -- FK to dim_course (optional)
    
    -- Measurements
    attendance_status VARCHAR(20),      -- Present, Absent, Tardy, Excused
    minutes_present DECIMAL(5,2),
    
    -- Audit columns
    source_system_id VARCHAR(100),      -- Original SIS ID
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Partition for query performance
ALTER TABLE fact_attendance 
SET PARTITIONED BY (year(date_key), month(date_key));
```

**Fact Table Best Practices**:
1. Use **surrogate keys** (auto-increment integers) for primary keys
2. Store **foreign keys** to dimensions (not embedded attributes)
3. Keep **additive measures** where possible (counts, sums)
4. Include **audit columns** (source IDs, timestamps)
5. **Partition** on date/time for time-series queries

### 4.3 Dimension Table Design

**Dimensions provide context** (who, what, where, when):

#### dim_student (Slowly Changing Dimension Type 2)
```sql
CREATE TABLE dim_student (
    student_key INTEGER PRIMARY KEY,    -- Surrogate key (warehouse key)
    student_id VARCHAR(50),             -- Natural key (from SIS)
    
    -- Attributes
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    ethnicity VARCHAR(50),
    grade_level INTEGER,
    
    -- SCD Type 2 tracking columns
    effective_date DATE NOT NULL,       -- When this version became active
    end_date DATE,                      -- When this version expired (NULL = current)
    is_current BOOLEAN DEFAULT TRUE,    -- Flag for current record
    version INTEGER,                    -- Version number
    
    -- Audit
    source_system VARCHAR(50),
    created_at TIMESTAMP
);

-- Index for lookups
CREATE INDEX idx_student_id_current ON dim_student(student_id, is_current);
```

**Why Type 2 SCD?**
- Tracks historical changes (student moves grade, changes name, transfers schools)
- Preserves point-in-time accuracy for historical reporting
- Enables "as-of" queries: "What grade was this student in Fall 2025?"

#### dim_date (Standard Date Dimension)
```sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,       -- YYYYMMDD format (e.g., 20260901)
    date_value DATE NOT NULL,
    
    -- Day attributes
    day_of_month TINYINT,
    day_of_week TINYINT,
    day_of_week_name VARCHAR(10),
    day_of_year SMALLINT,
    
    -- Week attributes
    week_of_year TINYINT,
    week_start_date DATE,
    week_end_date DATE,
    
    -- Month attributes
    month TINYINT,
    month_name VARCHAR(10),
    month_abbr CHAR(3),
    
    -- Quarter attributes
    quarter TINYINT,
    quarter_name VARCHAR(10),
    
    -- Year attributes
    year SMALLINT,
    
    -- School calendar attributes
    academic_year VARCHAR(10),          -- e.g., "2025-2026"
    semester VARCHAR(20),               -- Fall, Spring, Summer
    is_school_day BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100)
);
```

**Date Dimension Benefits**:
- Pre-computed date attributes (avoid expensive date functions)
- School calendar integration (academic year, semesters, holidays)
- Enables time-based filtering and grouping

#### dim_program (Slowly Changing Dimension Type 1)
```sql
CREATE TABLE dim_program (
    program_key INTEGER PRIMARY KEY,
    program_code VARCHAR(50) NOT NULL,
    program_name VARCHAR(200),
    program_type VARCHAR(50),           -- Academic, Career/Technical, Special Ed
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP                -- Overwrite (Type 1)
);
```

**Type 1 vs Type 2 Decision**:
- **Type 1** (overwrite): Use when history doesn't matter (program descriptions, codes)
- **Type 2** (track history): Use when historical context matters (student attributes, enrollments)

### 4.4 Complete Educational Star Schema Example

```
┌─────────────────┐
│   dim_student   │ (SCD Type 2)
├─────────────────┤
│ student_key PK  │
│ student_id      │
│ first_name      │
│ grade_level     │
│ effective_date  │
│ is_current      │
└─────────────────┘
         │
         │
┌─────────────────┐      ┌──────────────────┐
│    dim_date     │      │ fact_enrollments │
├─────────────────┤      ├──────────────────┤
│ date_key PK     │◄─────│ enrollment_key PK│
│ date_value      │      │ student_key FK   │───┐
│ academic_year   │      │ date_key FK      │   │
│ semester        │      │ program_key FK   │   │
│ is_school_day   │      │ school_key FK    │   │
└─────────────────┘      │                  │   │
         │               │ enrollment_status│   │
         │               │ credits_attempted│   │
┌─────────────────┐      └──────────────────┘   │
│   dim_program   │              │               │
├─────────────────┤              │               │
│ program_key PK  │◄─────────────┘               │
│ program_code    │                              │
│ program_name    │      ┌──────────────────┐    │
│ program_type    │      │   dim_school     │    │
└─────────────────┘      ├──────────────────┤    │
                         │ school_key PK    │◄───┘
                         │ school_code      │
                         │ school_name      │
                         │ district_name    │
                         └──────────────────┘
```

---

## 5. Data Type Mappings & Best Practices

### 5.1 DuckDB Type Recommendations

| Educational Data | DuckDB Type | Notes |
|------------------|-------------|-------|
| Student ID | VARCHAR(50) | Variable length, leading zeros preserved |
| Names | VARCHAR(100) | UTF-8 support for international names |
| Grades (A-F) | VARCHAR(2) | Store as string, not numeric |
| Grade Level | TINYINT | 0-12, small integer |
| GPA | DECIMAL(3,2) | 0.00-4.00 scale |
| Test Scores | SMALLINT | SAT/ACT scores |
| Dates | DATE | Not TIMESTAMP unless time matters |
| Enrollment Status | VARCHAR(20) | Active, Withdrawn, Graduated, etc. |
| Boolean Flags | BOOLEAN | is_current, is_active, is_special_ed |

### 5.2 Date Handling Best Practices

**Use DATE type for calendar dates**:
```sql
-- GOOD: Date only
enrollment_date DATE

-- BAD: Unnecessary precision
enrollment_date TIMESTAMP
```

**Use TIMESTAMP for audit trails**:
```sql
created_at TIMESTAMP DEFAULT current_timestamp,
updated_at TIMESTAMP
```

**Partition by date functions**:
```sql
ALTER TABLE fact_grades 
SET PARTITIONED BY (year(grade_date), quarter(grade_date));
```

---

## 6. Query Optimization Strategies

### 6.1 Partition Pruning

**Strategy**: Organize data by time periods for fast time-based queries.

```sql
-- Without partitioning: Scans ALL files
SELECT COUNT(*) 
FROM fact_attendance 
WHERE attendance_date >= '2026-01-01';

-- With partitioning: Scans ONLY year=2026 files
-- (After: ALTER TABLE fact_attendance SET PARTITIONED BY (year, month))
SELECT COUNT(*) 
FROM fact_attendance 
WHERE year = 2026 AND month >= 1;
```

### 6.2 Columnar Storage Benefits

DuckDB/Parquet reads **only needed columns**:

```sql
-- Reads only 2 columns from potentially 50+ column table
SELECT student_id, gpa 
FROM dim_student 
WHERE is_current = true;
```

### 6.3 Pre-aggregation Tables

For frequently-run reports, maintain pre-aggregated tables:

```sql
CREATE TABLE agg_daily_attendance AS
SELECT 
    date_key,
    school_key,
    COUNT(*) as total_students,
    SUM(CASE WHEN attendance_status = 'Present' THEN 1 ELSE 0 END) as present_count,
    AVG(minutes_present) as avg_minutes_present
FROM fact_attendance
GROUP BY date_key, school_key;
```

**Update strategy**: Incremental refresh daily.

---

## 7. Migration Path: Raw → Structured Data Mart

### Phase 1: Landing Zone (Raw Data)
```
s3://edu-data/landing/
  students/2026-02-22/students.csv
  enrollments/2026-02-22/enrollments.csv
  attendance/2026-02-22/attendance.csv
```

**Action**: Load CSV files as-is to temporary tables.

```sql
CREATE TABLE staging_students AS
SELECT * FROM read_csv('s3://edu-data/landing/students/*.csv', 
    AUTO_DETECT=TRUE);
```

### Phase 2: Staging (Cleaned & Typed)
```sql
CREATE TABLE staging_students_clean AS
SELECT 
    student_id::VARCHAR as student_id,
    TRIM(first_name) as first_name,
    TRIM(last_name) as last_name,
    TRY_CAST(date_of_birth AS DATE) as date_of_birth,
    COALESCE(grade_level, 0)::TINYINT as grade_level,
    current_timestamp as loaded_at
FROM staging_students
WHERE student_id IS NOT NULL;  -- Data quality filter
```

### Phase 3: Data Mart (Star Schema)

**Load Dimensions**:
```sql
-- dim_student (SCD Type 2 logic)
INSERT INTO dim_student (
    student_id, first_name, last_name, date_of_birth, grade_level,
    effective_date, end_date, is_current, version
)
SELECT 
    s.student_id,
    s.first_name,
    s.last_name,
    s.date_of_birth,
    s.grade_level,
    current_date as effective_date,
    NULL as end_date,
    TRUE as is_current,
    1 as version
FROM staging_students_clean s
LEFT JOIN dim_student d ON s.student_id = d.student_id AND d.is_current = TRUE
WHERE d.student_key IS NULL  -- New students only
    OR s.grade_level != d.grade_level;  -- Changed attributes (insert new version)
```

**Load Facts**:
```sql
INSERT INTO fact_enrollments (
    student_key, date_key, program_key, school_key,
    enrollment_status, credits_attempted
)
SELECT 
    ds.student_key,
    dd.date_key,
    dp.program_key,
    dsch.school_key,
    se.enrollment_status,
    se.credits_attempted
FROM staging_enrollments se
JOIN dim_student ds ON se.student_id = ds.student_id AND ds.is_current = TRUE
JOIN dim_date dd ON se.enrollment_date = dd.date_value
JOIN dim_program dp ON se.program_code = dp.program_code
JOIN dim_school dsch ON se.school_code = dsch.school_code;
```

### Phase 4: Export to Parquet (for MotherDuck/DuckLake)
```sql
-- Export with partitioning
COPY fact_enrollments 
TO 's3://edu-data/data-mart/enrollments/' (
    FORMAT parquet,
    COMPRESSION 'zstd',
    PARTITION_BY (year, quarter),
    ROW_GROUP_SIZE_BYTES '256MB'
);

COPY dim_student 
TO 's3://edu-data/data-mart/dim_student.parquet' (
    FORMAT parquet,
    COMPRESSION 'zstd'
);
```

### Phase 5: MotherDuck Integration
```sql
-- Attach MotherDuck database
ATTACH 'md:edu_data_warehouse' AS prod;

-- Create DuckLake tables
CREATE TABLE prod.fact_enrollments 
WITH (TABLE_FORMAT='ducklake', PARTITIONED_BY='year,quarter')
AS SELECT * FROM 's3://edu-data/data-mart/enrollments/**/*.parquet';

-- Query with time travel
SELECT * FROM prod.fact_enrollments 
FOR SYSTEM_TIME AS OF '2026-02-01';
```

---

## 8. Recommended Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                      SOURCE SYSTEMS                         │
│  (SIS, LMS, Attendance Systems, Grade Books)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   LANDING ZONE (S3)                         │
│  Raw CSV/JSON exports by date                               │
│  s3://bucket/landing/{system}/{date}/                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              STAGING (DuckDB Processing)                    │
│  - Data quality checks                                      │
│  - Type casting & validation                                │
│  - Deduplication                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          DATA MART (Star Schema - Parquet)                  │
│  Dimensions (SCD Type 2):                                   │
│    - dim_student, dim_program, dim_school                   │
│  Facts (Partitioned by date):                               │
│    - fact_enrollments, fact_attendance, fact_grades         │
│  Storage: s3://bucket/data-mart/                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           MOTHERDUCK (Cloud Analytics)                      │
│  - DuckLake tables (ACID, time travel)                      │
│  - Aggregated tables for dashboards                         │
│  - Ad-hoc analysis via SQL                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Key Recommendations Summary

### File Format
✅ **USE**: Parquet with ZSTD compression
✅ **FILE SIZE**: 100MB - 10GB per file
✅ **ROW GROUPS**: 256MB row group size
✅ **PARTITION**: By year/month for time-series data

### Schema Design
✅ **PATTERN**: Star schema (facts + dimensions)
✅ **FACT TABLES**: Measurements, foreign keys only
✅ **DIMENSIONS**: Descriptive attributes, use SCD Type 2 for student/enrollment history
✅ **DATE DIMENSION**: Pre-populate with school calendar attributes

### Data Types
✅ **IDs**: VARCHAR (preserves leading zeros)
✅ **DATES**: Use DATE type (not TIMESTAMP unless needed)
✅ **BOOLEANS**: Use BOOLEAN (not integer flags)
✅ **DECIMALS**: DECIMAL(p,s) for GPAs, financial data

### Performance
✅ **PARTITION**: Fact tables by date (year, quarter, month)
✅ **INDEXES**: On dimension natural keys and is_current flags
✅ **PRE-AGGREGATE**: Daily/monthly rollups for dashboards

### Migration Strategy
1. **Landing**: Raw CSV/JSON to S3
2. **Staging**: Clean, validate, type-cast in DuckDB
3. **Data Mart**: Load star schema, export to partitioned Parquet
4. **MotherDuck**: Create DuckLake tables for cloud analytics

---

## 10. Reference Links

**MotherDuck Documentation**:
- Data Warehousing Guide: https://motherduck.com/docs/concepts/data-warehousing/
- DuckLake Documentation: https://motherduck.com/docs/concepts/ducklake/
- Ingestion Options: https://motherduck.com/docs/integrations/ingestion/

**DuckDB Documentation**:
- Parquet Files: https://duckdb.org/docs/stable/data/parquet/overview
- Partitioned Writes: https://duckdb.org/docs/stable/data/partitioning/partitioned_writes
- Data Types: https://duckdb.org/docs/stable/sql/data_types/overview

**DuckLake**:
- Official Site: https://ducklake.select/
- Partitioning: https://ducklake.select/docs/stable/duckdb/advanced_features/partitioning

**Educational Data Standards**:
- Ed-Fi Data Standard: https://docs.ed-fi.org/reference/data-exchange/data-standard
- CEDS Data Warehouse: https://github.com/CEDStandards/CEDS-Data-Warehouse

**Star Schema References**:
- MotherDuck Star Schema Guide: https://motherduck.com/learn-more/star-schema-data-warehouse-guide/
- Slowly Changing Dimensions: https://dev.to/alexmercedcoder/slowly-changing-dimensions-types-1-3-with-examples-4751
