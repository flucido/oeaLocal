# Validation Research: Best Practices Audit

**Date**: February 22, 2026  
**Purpose**: Validate our MotherDuck + dbt + Aeries implementation against industry best practices for education data warehousing, FERPA compliance, and modern data engineering patterns.

---

## Executive Summary

### Key Findings ✅
- MotherDuck + dbt is a proven production pattern for education data pipelines
- Our token management via environment variables aligns with 2026 security best practices
- Microbatch incremental strategy is recommended for time-series education data
- Star schema design with fact/dimension separation is industry standard
- FERPA compliance requires k-anonymity (k≥5), de-identification, and access controls

### Critical Gaps 🚨
- **Missing**: Physical data partitioning strategy for MotherDuck/DuckLake
- **Missing**: FERPA-specific data retention and deletion policies
- **Missing**: Slowly Changing Dimensions (SCD) strategy for student demographics
- **Missing**: Academic calendar dimension for proper time intelligence

---

## MotherDuck Best Practices (2026)

### 1. Token Management & Authentication
**Source**: [MotherDuck Docs - Authentication](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/)

#### ✅ What We're Doing Right
- Storing `motherduck_token` as environment variable (best practice)
- Using token-based authentication instead of interactive auth (production-ready)
- Avoiding token exposure in code/configs

#### ⚠️ Areas for Improvement
1. **Token Rotation**: No documented rotation strategy
   - **Recommendation**: Implement 90-day token rotation policy
   - Set token expiration when creating in UI
   - Document renewal process in runbook

2. **Token Scope**: Not using Read Scaling tokens for analytics workloads
   - **Recommendation**: Consider read-only tokens for BI tool connections
   - Prevents accidental writes from analytics tools
   - Reduces blast radius of token compromise

3. **SaaS Mode**: Not leveraging `saas_mode=true` for third-party tool connections
   - **Recommendation**: Enable SaaS mode for any external BI/reporting tools
   - Prevents local file access from cloud-hosted tools
   - Example: `md:my_db?motherduck_token=<token>&saas_mode=true`

**Reference Code**:
```bash
# Current approach (GOOD)
export motherduck_token='<token>'

# Enhanced approach for production (BETTER)
# 1. Token rotation policy in secrets manager
# 2. Read-only tokens for analytics:
#    Create token → Select "Read Scaling" type
# 3. SaaS mode for BI tools:
#    md:aeries_warehouse?saas_mode=true
```

### 2. Instance Lifecycle & TTL Management
**Source**: [MotherDuck Docs - General Availability Release](https://motherduck.com/docs/about-motherduck/release-notes/)

#### Best Practices (2026)
- **Compute Limits**: Free tier has usage throttling (enforced June 2024)
- **Database Persistence**: Databases persist indefinitely (no TTL)
- **Session Management**: Compute sessions auto-terminate after inactivity
- **Cost Optimization**: Use hybrid execution (local + cloud) for development

#### ⚠️ What We Need
1. **Hybrid Execution Strategy**: No documented local vs. cloud execution pattern
   - **Pattern**: "Local dev, cloud prod" (dbt best practice)
   - Use local DuckDB for development/testing
   - Use MotherDuck (`md:`) for production pipelines
   - Reference: [dbt + MotherDuck Dual Execution](https://motherduck.com/blog/dual-execution-dbt/)

2. **Database Organization**:
   - Current: Single `aeries` database
   - **Recommendation**: Separate dev/staging/prod databases
     - `aeries_dev` - Developer sandboxes
     - `aeries_staging` - Pre-production validation
     - `aeries_prod` - Production analytics

**Reference Pattern**:
```yaml
# profiles.yml (dbt)
aeries:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: 'local.duckdb'  # Local development
    prod:
      type: duckdb
      path: 'md:aeries_prod'  # Cloud production
```

### 3. Schema Organization Patterns
**Source**: [MotherDuck Data Warehousing Overview](https://motherduck.com/docs/getting-started/data-warehouse/)

#### Industry Standard Pattern
```
raw/              # Landing zone (Aeries source data)
├── students
├── enrollments
├── grades
└── attendance

staging/          # Cleaned, typed, de-duplicated
├── stg_students
├── stg_enrollments
└── stg_grades

marts/            # Business logic, star schema
├── core/
│   ├── dim_students
│   ├── dim_schools
│   └── fact_grades
└── compliance/
    └── ferpa_reports
```

#### ✅ What We're Doing Right
- We have staging layer (models/staging/)
- We're using star schema (dim_ / fact_ naming)

#### ⚠️ Areas for Improvement
1. **Missing `raw/` schema**: Currently mixing raw ingestion with staging
   - **Recommendation**: Create `raw` schema for immutable source snapshots
   - Never transform in raw - preserve original Aeries data
   - Enables "time travel" and reprocessing

2. **Schema-level documentation**: No documented data lineage
   - **Recommendation**: Use dbt docs + MotherDuck sharing for lineage
   - Document each layer's purpose in dbt project

### 4. Cost Optimization Strategies
**Source**: [Orchestrating DuckDB with MotherDuck](https://medium.com/@hugolu87/orchestrating-duck-db-using-motherduck-and-orchestra-162ddf9436be)

#### Key Insights (2025/2026 Articles)
- Teams report **70% cost reduction** vs. traditional cloud warehouses
- DuckDB/MotherDuck cost-effective for datasets up to 10TB (covers 94% of use cases)
- Hybrid execution reduces cloud compute costs

#### 🎯 Cost Optimization Checklist
1. ✅ Using environment variables (avoiding repeated authentication costs)
2. ⚠️ Need to document query optimization patterns
   - Filter pushdown to minimize data scanned
   - Partition pruning (if using DuckLake)
   - Materialized views for repeated aggregations

3. ⚠️ No monitoring of compute usage
   - **Recommendation**: Track query costs in dbt logs
   - Monitor `EXPLAIN ANALYZE` for expensive queries
   - Document optimization wins in learnings.md

---

## dbt + MotherDuck Patterns (2025-2026)

### 1. Materialization Strategies
**Sources**: 
- [Microbatch Strategy (Feb 2026)](https://motherduck.com/blog/microbatch-dbt-duckdb/)
- [10 DuckDB Materialization Patterns (Oct 2025)](https://medium.com/@Nexumo_/10-duckdb-materialization-patterns-youll-reuse-forever-5ed193226d2b)
- [dbt Incremental Patterns (Feb 2026)](https://docs.getdbt.com/best-practices/how-we-handle-real-time-data/2-incremental-patterns)

#### Recommended Strategy by Model Type

| Model Type | Strategy | Why |
|------------|----------|-----|
| **Dimensions** (dim_students, dim_schools) | `table` or `merge` | Small, slowly changing data. Full refresh acceptable. |
| **Large Facts** (fact_attendance, fact_grades) | `microbatch` | Time-series data, needs backfill capability, robust recovery. |
| **Small Facts** | `delete+insert` | Simpler than microbatch for small datasets. |
| **Reports/Marts** | `table` | Aggregated, rebuilt daily. |

#### 🚨 Critical Insight: Microbatch for Education Data
**Source**: [Microbatch dbt-duckdb (Feb 2026)](https://motherduck.com/blog/microbatch-dbt-duckdb/)

**Why microbatch matters for education**:
1. **Backfilling**: School year starts → need to reprocess August-September data
2. **Bug fixes**: Find grading calculation error → reprocess specific month
3. **Parallel processing**: Process each day independently
4. **Recovery**: Failed job → only retry failed batches

**Configuration Example**:
```yaml
# models/marts/core/fact_attendance.sql
{{
  config(
    materialized='incremental',
    incremental_strategy='microbatch',
    event_time='attendance_date',
    begin='2024-08-01',  # School year start
    batch_size='day'
  )
}}

SELECT
  attendance_date,
  student_id,
  school_id,
  attendance_status
FROM {{ ref('stg_attendance') }}
WHERE attendance_date >= '{{ var("event_time_start") }}'
  AND attendance_date < '{{ var("event_time_end") }}'
```

#### ⚠️ Gotchas We Need to Avoid
**Source**: [Common Pitfalls - Microbatch with DuckDB](https://motherduck.com/blog/microbatch-dbt-duckdb/)

1. **Type Casting in WHERE Clause** 🚨
   ```sql
   -- ❌ BAD: Causes full table scan
   WHERE event_time >= '2024-01-15'::timestamp
   
   -- ✅ GOOD: Enables zone map filtering
   WHERE event_time >= '2024-01-15'
   ```

2. **UTC Timezone Handling** 🚨
   - dbt converts all times to UTC
   - **Our situation**: California schools (PST/PDT)
   - **Fix**: Store all timestamps in UTC, display in Pacific
   - **Example**: 8:00 AM PST attendance → Store as 16:00 UTC

3. **Row Groups vs. Partitions** 🚨
   - DuckDB uses 122k row groups (not date partitions)
   - Microbatch doesn't give true partition pruning UNLESS using DuckLake
   - **Recommendation**: Consider DuckLake for large fact tables

### 2. Testing Strategies for Cloud Warehouses
**Source**: [dbt + DuckDB End-to-End Tutorial (2026)](https://motherduck.com/videos/98/duckdb-dbt-end-to-end-data-engineering-project-23/)

#### Best Practices
1. **Unit tests without cloud dependencies**:
   - Use local DuckDB for testing
   - Mock external dependencies
   - Fast feedback loop

2. **Data quality tests**:
   ```yaml
   # models/staging/schema.yml
   models:
     - name: stg_students
       columns:
         - name: student_id
           tests:
             - unique
             - not_null
         - name: grade_level
           tests:
             - accepted_values:
                 values: ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
   ```

3. **Custom tests for education domain**:
   ```sql
   -- tests/assert_valid_enrollment_dates.sql
   -- Students can't be enrolled before birth
   SELECT *
   FROM {{ ref('dim_students') }}
   WHERE enrollment_date < birth_date
   ```

#### ⚠️ What We Need
1. **dbt test coverage**: Currently no documented tests
2. **FERPA compliance tests**: Verify PII de-identification
3. **Business rule tests**: Validate grade calculations, attendance rules

### 3. Documentation Best Practices
**Source**: [dbt + MotherDuck Integration Docs](https://motherduck.com/docs/integrations/dbt/)

#### ✅ Industry Standard
```yaml
# models/staging/schema.yml
models:
  - name: stg_students
    description: "Cleaned student demographics from Aeries SIS"
    columns:
      - name: student_id
        description: "State-assigned student identifier (SSID)"
        meta:
          ferpa: "PII - Level 1"
          source: "Aeries.STU.SN"
```

#### ⚠️ What We Need
1. Document FERPA classification in metadata
2. Link back to source Aeries tables
3. Add business glossary (e.g., "What is an 'active enrollment'?")

---

## Education Data Standards

### 1. Common Education Data Standards (CEDS)
**Source**: [CEDS Official Site](https://ceds.ed.gov/)

#### What is CEDS?
- **Purpose**: Voluntary common vocabulary for P-20W education data
- **Scope**: Student demographics, enrollment, attendance, grades, assessments
- **Governance**: National Center for Education Statistics (NCES)
- **Version**: Continuously updated (GitHub-based governance since 2025)

#### Core Principles
1. **Interoperability**: Systems can exchange data using common definitions
2. **Portability**: Students transfer between districts without data loss
3. **Comparability**: Aggregate data across states/districts

#### Key Element Categories
- **Student**: Name, identifiers, demographics, contact info
- **Enrollment**: School, grade level, entry/exit dates
- **Attendance**: Daily attendance, excused/unexcused absences
- **Assessment**: Test scores, performance levels
- **Program**: Special education, ELL, gifted/talented

#### 🎯 Application to Our Project
**Recommendation**: Map our data model to CEDS elements

| Our Field | CEDS Element | Notes |
|-----------|--------------|-------|
| `student_id` | Student Identifier | State-assigned SSID |
| `grade_level` | Grade Level | K-12 standard values |
| `enrollment_date` | Enrollment Entry Date | ISO 8601 format |
| `attendance_status` | Attendance Status | Present, Absent, Tardy |
| `gpa` | Grade Point Average Cumulative | 4.0 scale |

**Benefits**:
1. Easier integration with state reporting systems
2. Compatibility with Ed-Fi (builds on CEDS)
3. Future-proof data model

#### 📚 Resources
- CEDS Elements Explorer: https://ceds.ed.gov/explore.aspx
- CEDS Align Tool: https://ceds.ed.gov/align.aspx
- GitHub Repository: https://github.com/CEDStandards/CEDS-Elements

### 2. Ed-Fi Data Standard
**Source**: [Ed-Fi Alliance Docs](https://docs.ed-fi.org/reference/data-exchange/data-standards)

#### What is Ed-Fi?
- **Purpose**: REST API specification for K-12 data exchange
- **Relation to CEDS**: Built on CEDS vocabulary, adds API semantics
- **Current Versions**: 
  - v6.x (2025) - School years 2026-2028
  - v5.x (2023-2024) - School years 2024-2028
  - v4.x (2022) - EOL 2026

#### Ed-Fi Unifying Data Model (UDM)
- **Student-centric**: All data tied to individual students
- **Academic focus**: Student performance, teaching, learning
- **Extensible**: States/districts can add custom data elements

#### Core Domains
1. **Student**: Identity, demographics, enrollment
2. **Staff**: Teachers, counselors, administrators
3. **School**: Organizational hierarchy (district > school)
4. **Section**: Class schedules, rosters
5. **Grade**: Report cards, transcripts
6. **Assessment**: Test results, proficiency levels
7. **Attendance**: Daily attendance, class period attendance
8. **Discipline**: Incidents, actions
9. **Program**: Special education, ELL, Title I

#### 🎯 Application to Our Project
**Current State**: We're NOT implementing Ed-Fi API (we're not an SIS)

**But we CAN**:
1. **Use Ed-Fi domain model** as reference for star schema design
2. **Align dimension tables** to Ed-Fi entities:
   - `dim_students` → Ed-Fi `Student`
   - `dim_schools` → Ed-Fi `School`
   - `dim_courses` → Ed-Fi `Section`

3. **Follow Ed-Fi naming conventions**:
   ```sql
   -- Ed-Fi style
   CREATE TABLE dim_student (
     student_unique_id VARCHAR,  -- Ed-Fi: StudentUniqueId
     first_name VARCHAR,
     last_name VARCHAR,
     birth_date DATE,
     grade_level VARCHAR  -- Ed-Fi descriptor
   );
   ```

#### ⚠️ Extension Framework
Ed-Fi allows extensions for state-specific requirements:
- California might require "Foster Youth" flag
- Texas might require "At-Risk" indicator

**Our approach**: Use `meta` fields in dbt for state-specific columns:
```yaml
columns:
  - name: is_foster_youth
    description: "California AB 490 foster youth indicator"
    meta:
      ed_fi_extension: "CA-FosterYouth"
```

#### 📚 Resources
- Ed-Fi Data Standard v6: https://docs.ed-fi.org/reference/data-exchange/data-standard/
- Ed-Fi UDM: https://docs.ed-fi.org/reference/data-exchange/udm/
- Certification Program: https://www.ed-fi.org/ed-fi-data-standard/

### 3. FERPA Compliance Requirements
**Source**: [FERPA Overview (U.S. Department of Education)](https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html)

#### What is FERPA?
- **Full Name**: Family Educational Rights and Privacy Act (1974)
- **Purpose**: Protect privacy of student education records
- **Scope**: All schools receiving federal funding
- **Penalties**: Loss of federal funding for violations

#### Personally Identifiable Information (PII)
**FERPA defines PII as**:
1. **Direct identifiers**: Name, address, SSN, student ID (if linkable)
2. **Indirect identifiers**: Combination of fields that allow identification
3. **Education records**: Grades, attendance, discipline, medical

#### De-identification Requirements
**Source**: [FERPA & Big Data (2014 Guidelines)](https://tech.ed.gov/files/2014/09/Student-Privacy-and-Online-Educational-Services-February-2014.pdf)

**Two approaches**:

1. **Statistical De-identification** (Recommended for analytics):
   - **k-anonymity**: Each record indistinguishable from at least k-1 others
   - **Minimum k**: No consensus, but **k≥5** is common threshold
   - **Quasi-identifiers**: Gender, grade, ethnicity, ZIP code
   
   Example:
   ```sql
   -- ❌ BAD: Only 1 student matches (k=1)
   SELECT ethnicity, grade_level, gender, COUNT(*)
   FROM dim_students
   GROUP BY ethnicity, grade_level, gender
   HAVING COUNT(*) < 5;  -- Flag these combinations
   
   -- ✅ GOOD: Suppress or aggregate small groups
   SELECT 
     CASE WHEN count_students >= 5 THEN ethnicity ELSE 'Other' END,
     grade_level,
     COUNT(*) as count_students
   FROM student_groups
   GROUP BY ethnicity, grade_level
   HAVING COUNT(*) >= 5;
   ```

2. **Expert Determination**:
   - Hire expert to assess re-identification risk
   - More expensive, used for research datasets

#### 🚨 Critical Requirements for Our Warehouse

**1. Access Controls**:
```sql
-- Example: Role-based access control
-- Teachers: Can only see their students
-- Administrators: School-level access
-- District: All schools

CREATE ROLE teacher;
CREATE ROLE principal;
CREATE ROLE district_admin;

-- Row-level security (if supported by MotherDuck in future)
CREATE POLICY teacher_policy ON fact_grades
  FOR SELECT TO teacher
  USING (school_id = current_setting('app.school_id'));
```

**2. Audit Logging**:
- **Requirement**: Track who accessed what student data when
- **Current Gap**: No documented audit strategy
- **Recommendation**: 
  - Use MotherDuck query logs
  - Create `audit_log` table for sensitive queries
  - Example:
    ```sql
    INSERT INTO audit_log (user_id, query, accessed_at)
    VALUES (current_user, 'SELECT * FROM fact_grades WHERE student_id = ?', NOW());
    ```

**3. Data Retention**:
- **FERPA**: Schools must have retention policy
- **Common practice**: 
  - Active students: Retain all data
  - Graduated students: 5-7 years
  - Withdrawn students: 3-5 years
- **Current gap**: No documented retention policy
- **Recommendation**: Add `archived_at` timestamp, periodic purge job

**4. Consent & Directory Information**:
- **FERPA**: Parents can opt out of "directory information" sharing
- **Directory info**: Name, address, phone, email, photo
- **Current gap**: No `consent_flags` in `dim_students`
- **Recommendation**: 
  ```sql
  ALTER TABLE dim_students ADD COLUMN directory_info_consent BOOLEAN DEFAULT FALSE;
  ```

**5. Third-Party Data Sharing**:
- **FERPA**: Requires written agreement for third-party vendors
- **MotherDuck**: Counts as third party (even though it's our warehouse)
- **Recommendation**: 
  - Document data processing agreement with MotherDuck
  - Review MotherDuck Trust & Security: https://motherduck.com/trust-and-security/
  - MotherDuck is SOC 2 Type II certified ✅
  - MotherDuck is GDPR compliant ✅

#### Privacy-Preserving Analytics Patterns

**Pattern 1: Aggregated Reporting**
```sql
-- Safe: No individual student data
SELECT 
  school_id,
  grade_level,
  AVG(gpa) as avg_gpa,
  COUNT(*) as student_count
FROM fact_grades
GROUP BY school_id, grade_level
HAVING COUNT(*) >= 10;  -- Suppress small groups
```

**Pattern 2: De-identified Cohort Analysis**
```sql
-- Safe: Anonymized student IDs
SELECT 
  anonymized_student_id,  -- SHA256(student_id || salt)
  grade_level,
  achievement_level
FROM dim_students
WHERE cohort_year = 2024;
```

**Pattern 3: Differential Privacy** (Advanced)
```sql
-- Add noise to aggregate counts
SELECT 
  grade_level,
  COUNT(*) + (RANDOM() * 5 - 2.5) as noisy_count  -- Add noise ±2.5
FROM dim_students
GROUP BY grade_level;
```

#### 📚 Resources
- FERPA Guidelines: https://studentprivacy.ed.gov/
- FERPA & Big Data: https://tech.ed.gov/privacy/
- k-anonymity: Sweeney, L. (2002). "k-anonymity: A model for protecting privacy"

---

## Star Schema Design for Education

### 1. Star Schema Principles
**Source**: Multiple sources - industry standard pattern

#### What is a Star Schema?
- **Structure**: Fact tables (center) + Dimension tables (points)
- **Purpose**: Optimize for analytical queries, not transactions
- **Benefits**: 
  - Simple to understand
  - Fast aggregations
  - Flexible for BI tools

#### Fact vs. Dimension

| Aspect | Fact Table | Dimension Table |
|--------|------------|-----------------|
| **Contains** | Measurements, metrics, events | Descriptive attributes |
| **Granularity** | One row per event/transaction | One row per entity |
| **Size** | Large (millions+ rows) | Small (hundreds/thousands) |
| **Changes** | Append-only (immutable events) | Slowly changing (updates) |
| **Keys** | Foreign keys to dimensions | Surrogate keys |
| **Columns** | Mostly numeric (measures) | Mostly text/categorical |

**Education Examples**:
- **Fact**: Daily attendance record, test score, grade
- **Dimension**: Student, school, course, teacher

### 2. Education-Specific Star Schema
**Source**: Industry patterns from Ed-Fi, state data warehouses

#### Recommended Structure

```
Dimensions (WHO, WHERE, WHEN, WHAT)
├── dim_student        # WHO: Student demographics
├── dim_school         # WHERE: School organizational hierarchy
├── dim_date           # WHEN: Academic calendar
├── dim_course         # WHAT: Course catalog
└── dim_teacher        # WHO: Teacher/staff

Facts (EVENTS, MEASUREMENTS)
├── fact_attendance    # Daily attendance events
├── fact_grades        # Course grades, GPA
├── fact_assessment    # Test scores
├── fact_enrollment    # Student enrollment history
└── fact_discipline    # Behavioral incidents
```

#### Dimension Design Patterns

**dim_student** (Slowly Changing Dimension Type 2):
```sql
CREATE TABLE dim_student (
  student_key BIGINT PRIMARY KEY,  -- Surrogate key (warehouse-generated)
  student_id VARCHAR,               -- Natural key (from Aeries)
  
  -- Demographics
  first_name VARCHAR,
  last_name VARCHAR,
  birth_date DATE,
  gender VARCHAR,
  ethnicity VARCHAR,
  
  -- Program flags
  is_special_ed BOOLEAN,
  is_ell BOOLEAN,
  is_free_lunch BOOLEAN,
  
  -- SCD Type 2 fields
  effective_date DATE,              -- When this version became effective
  end_date DATE,                    -- When this version expired (NULL = current)
  is_current BOOLEAN,               -- TRUE for current record
  
  -- Audit
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**dim_date** (Academic Calendar):
```sql
CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY,     -- YYYYMMDD format (e.g., 20240815)
  
  -- Standard date fields
  date DATE,
  day_of_week VARCHAR,
  week_of_year INTEGER,
  month_name VARCHAR,
  quarter INTEGER,
  year INTEGER,
  
  -- Academic calendar fields (IMPORTANT for education!)
  school_year VARCHAR,              -- "2024-2025"
  academic_term VARCHAR,            -- "Fall", "Spring"
  is_school_day BOOLEAN,            -- TRUE if classes in session
  day_of_school_year INTEGER,       -- Day 1, 2, 3... of 180
  is_holiday BOOLEAN,
  holiday_name VARCHAR,
  
  -- Fiscal
  fiscal_year VARCHAR,              -- State fiscal year (may differ from school year)
  fiscal_quarter INTEGER
);
```

**dim_school** (Organizational Hierarchy):
```sql
CREATE TABLE dim_school (
  school_key BIGINT PRIMARY KEY,
  school_id VARCHAR,
  
  -- Hierarchy (enables drill-down)
  district_id VARCHAR,
  district_name VARCHAR,
  school_name VARCHAR,
  
  -- Attributes
  school_type VARCHAR,              -- Elementary, Middle, High
  address VARCHAR,
  city VARCHAR,
  state VARCHAR,
  zip_code VARCHAR,
  
  -- Operational
  principal_name VARCHAR,
  phone VARCHAR,
  
  -- SCD Type 2 fields
  effective_date DATE,
  end_date DATE,
  is_current BOOLEAN
);
```

#### Fact Table Design Patterns

**fact_attendance** (Daily Grain):
```sql
CREATE TABLE fact_attendance (
  -- Surrogate key (optional, for tracking)
  attendance_key BIGINT PRIMARY KEY,
  
  -- Foreign keys to dimensions
  student_key BIGINT REFERENCES dim_student(student_key),
  school_key BIGINT REFERENCES dim_school(school_key),
  date_key INTEGER REFERENCES dim_date(date_key),
  
  -- Degenerate dimension (doesn't warrant own table)
  period_number INTEGER,            -- Class period (1-7)
  
  -- Measures (numeric facts)
  is_present BOOLEAN,
  is_absent_excused BOOLEAN,
  is_absent_unexcused BOOLEAN,
  is_tardy BOOLEAN,
  minutes_absent INTEGER,
  
  -- Audit
  source_system VARCHAR,            -- "Aeries"
  loaded_at TIMESTAMP
);
```

**fact_grades** (Semester Grain):
```sql
CREATE TABLE fact_grades (
  grade_key BIGINT PRIMARY KEY,
  
  -- Foreign keys
  student_key BIGINT REFERENCES dim_student(student_key),
  school_key BIGINT REFERENCES dim_school(school_key),
  date_key INTEGER REFERENCES dim_date(date_key),  -- Semester end date
  course_key BIGINT REFERENCES dim_course(course_key),
  teacher_key BIGINT REFERENCES dim_teacher(teacher_key),
  
  -- Degenerate dimensions
  term_code VARCHAR,                -- "Fall 2024"
  
  -- Measures
  letter_grade VARCHAR,             -- "A", "B+", etc.
  numeric_grade DECIMAL(5,2),       -- 93.5
  grade_points DECIMAL(5,2),        -- 4.0 scale
  credits_attempted DECIMAL(5,2),
  credits_earned DECIMAL(5,2),
  
  -- Audit
  source_system VARCHAR,
  loaded_at TIMESTAMP
);
```

### 3. Slowly Changing Dimensions (SCD) Strategy
**Source**: Kimball Dimensional Modeling (industry standard)

#### Why SCD Matters for Education
Students change over time:
- Grade level increases each year
- Address changes (family moves)
- Program participation changes (enters/exits special ed)
- GPA accumulates over time

**Question**: How do we report historical data accurately?

#### SCD Type 1: Overwrite (Not Recommended)
```sql
-- ❌ Lose history
UPDATE dim_student 
SET grade_level = '10', address = '123 New St'
WHERE student_id = 'S001';
```

**Problem**: Can't answer "What was student's address last year?"

#### SCD Type 2: Add New Row (Recommended)
```sql
-- ✅ Preserve history
-- Step 1: Close out old record
UPDATE dim_student
SET end_date = '2024-08-31', is_current = FALSE
WHERE student_id = 'S001' AND is_current = TRUE;

-- Step 2: Insert new record
INSERT INTO dim_student (
  student_key, student_id, grade_level, address,
  effective_date, end_date, is_current
) VALUES (
  9999,  -- New surrogate key
  'S001',
  '10',
  '123 New St',
  '2024-09-01',
  NULL,
  TRUE
);
```

**Benefit**: 
- `fact_grades` from 2023 still points to old `student_key` with grade 9
- `fact_grades` from 2024 points to new `student_key` with grade 10
- Historical reports remain accurate

#### ⚠️ Current Gap: No SCD Strategy
**Recommendation**: Implement SCD Type 2 for:
1. `dim_student` - Track grade level, address, program changes
2. `dim_school` - Track principal changes, school renaming
3. `dim_teacher` - Track school reassignments

**Implementation**:
```sql
-- dbt macro: scd_type_2.sql
{% macro scd_type_2(source_table, target_table, unique_key, updated_at) %}
  -- Close out changed records
  UPDATE {{ target_table }}
  SET end_date = CURRENT_DATE - INTERVAL '1 day',
      is_current = FALSE
  WHERE {{ unique_key }} IN (
    SELECT {{ unique_key }}
    FROM {{ source_table }}
    WHERE {{ updated_at }} > (
      SELECT MAX(effective_date)
      FROM {{ target_table }}
      WHERE is_current = TRUE
    )
  );
  
  -- Insert new records
  INSERT INTO {{ target_table }}
  SELECT 
    NEXTVAL('{{ target_table }}_key_seq') as surrogate_key,
    *,
    CURRENT_DATE as effective_date,
    NULL as end_date,
    TRUE as is_current
  FROM {{ source_table }}
  WHERE {{ updated_at }} > (
    SELECT COALESCE(MAX(effective_date), '1900-01-01')
    FROM {{ target_table }}
  );
{% endmacro %}
```

### 4. Conformed Dimensions
**Source**: Kimball - ensure consistency across fact tables

#### Principle
**One dimension, shared by multiple facts**:
- `dim_student` used by `fact_attendance`, `fact_grades`, `fact_assessment`
- `dim_date` used by ALL fact tables
- `dim_school` used by ALL fact tables

#### Benefits
1. **Consistency**: Same student attributes across reports
2. **Efficiency**: Single dimension table, not duplicated
3. **Drill-across**: Compare metrics across different facts
   - Example: "Show attendance rate vs. GPA by student"

#### ⚠️ Anti-Pattern: Dimension Duplication
```sql
-- ❌ BAD: Different student dimensions per fact
CREATE TABLE fact_attendance (
  student_id VARCHAR,  -- Direct reference, duplicated attributes
  student_name VARCHAR,
  student_grade VARCHAR
);

CREATE TABLE fact_grades (
  student_id VARCHAR,  -- Same attributes, different values!
  student_name VARCHAR,
  student_grade VARCHAR
);
```

**Problem**: Student name might be inconsistent between tables

```sql
-- ✅ GOOD: Shared dimension
CREATE TABLE fact_attendance (
  student_key BIGINT REFERENCES dim_student(student_key)
);

CREATE TABLE fact_grades (
  student_key BIGINT REFERENCES dim_student(student_key)
);
```

---

## Gap Analysis

### What We're Doing Right ✅

1. **Token Security**: Environment variable storage (best practice)
2. **Star Schema**: Dimension/fact separation
3. **dbt Project**: Using modern transformation tool
4. **MotherDuck**: Cost-effective cloud warehouse choice
5. **Staging Layer**: Raw → Staging → Marts pattern

### Areas for Improvement ⚠️

1. **Data Partitioning**: 
   - Consider DuckLake for large fact tables
   - Would enable true partition pruning with microbatch

2. **Incremental Strategy**: 
   - Add `microbatch` config to time-series facts
   - Document backfill procedures

3. **SCD Implementation**:
   - Add SCD Type 2 logic to dimensions
   - Track historical changes for compliance

4. **Testing Coverage**:
   - Add dbt tests (unique, not_null, relationships)
   - Create custom FERPA compliance tests
   - Test business rules (e.g., GPA calculations)

5. **Documentation**:
   - Add column descriptions to dbt schema.yml
   - Document FERPA PII classification
   - Create data dictionary for business users

6. **Monitoring**:
   - Track query performance (EXPLAIN ANALYZE)
   - Monitor compute costs
   - Set up alerting for failed dbt jobs

7. **Hybrid Execution**:
   - Configure local dev + cloud prod in profiles.yml
   - Document when to use local vs. cloud

### Critical Issues 🚨

1. **FERPA Compliance Gaps**:
   - **Missing**: k-anonymity checks in reporting queries
   - **Missing**: Audit logging for data access
   - **Missing**: Data retention policy
   - **Missing**: Consent flags in `dim_student`
   - **Action**: Implement before production deployment

2. **No Disaster Recovery**:
   - **Missing**: Backup strategy for MotherDuck databases
   - **Missing**: Point-in-time recovery plan
   - **Action**: Document MotherDuck backup capabilities

3. **Access Control**:
   - **Missing**: Role-based access control (RBAC) design
   - **Missing**: Row-level security for sensitive data
   - **Action**: Define user roles (teacher, principal, district admin)

4. **Data Quality**:
   - **Missing**: Automated validation of source data
   - **Missing**: Error handling for bad data from Aeries
   - **Action**: Add great_expectations or dbt tests

---

## Recommended Next Steps

### Phase 1: Critical (Before Production) 🚨
1. **FERPA Compliance**:
   - [ ] Add audit logging table
   - [ ] Implement k-anonymity checks (k≥5)
   - [ ] Document data retention policy
   - [ ] Add consent flags to dim_student

2. **Access Control**:
   - [ ] Design RBAC model (roles + permissions)
   - [ ] Configure MotherDuck token per role (read-only for analysts)
   - [ ] Document who can access what data

3. **Testing**:
   - [ ] Add unique/not_null tests to all dimension keys
   - [ ] Add relationship tests (foreign key validation)
   - [ ] Create custom test for FERPA compliance

### Phase 2: High Priority ⚠️
4. **SCD Implementation**:
   - [ ] Add SCD Type 2 to dim_student
   - [ ] Add effective_date, end_date, is_current columns
   - [ ] Create dbt macro for SCD updates

5. **Incremental Strategy**:
   - [ ] Configure microbatch for fact_attendance
   - [ ] Configure microbatch for fact_grades
   - [ ] Test backfill scenarios

6. **Documentation**:
   - [ ] Add column descriptions to all models
   - [ ] Create data lineage diagram (dbt docs)
   - [ ] Write business glossary

### Phase 3: Optimization 🎯
7. **Partitioning** (if needed for scale):
   - [ ] Evaluate DuckLake for large facts
   - [ ] Implement physical partitioning by school year

8. **Monitoring**:
   - [ ] Set up dbt Cloud for job orchestration
   - [ ] Configure alerting for job failures
   - [ ] Track query costs in MotherDuck

9. **Hybrid Execution**:
   - [ ] Configure local dev in profiles.yml
   - [ ] Document dev → prod promotion workflow

---

## Sources

### MotherDuck (2025-2026)
1. [MotherDuck Documentation](https://motherduck.com/docs/) - Official docs
2. [Authenticating to MotherDuck](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/) - Token management
3. [Microbatch Strategy (Feb 2026)](https://motherduck.com/blog/microbatch-dbt-duckdb/) - Incremental patterns
4. [Dual Execution dbt (Jan 2025)](https://motherduck.com/blog/dual-execution-dbt/) - Local dev + cloud prod
5. [MotherDuck Access Management (Dec 2025)](https://www.codecentric.de/en/knowledge-hub/blog/motherduck-access-management-and-scalable-analytics-overview)
6. [Orchestrating DuckDB with MotherDuck (Sep 2025)](https://medium.com/@hugolu87/orchestrating-duck-db-using-motherduck-and-orchestra-162ddf9436be) - Cost optimization

### dbt + DuckDB (2024-2026)
7. [dbt + DuckDB End-to-End Tutorial (Feb 2026)](https://motherduck.com/videos/98/duckdb-dbt-end-to-end-data-engineering-project-23/)
8. [10 DuckDB Materialization Patterns (Oct 2025)](https://medium.com/@Nexumo_/10-duckdb-materialization-patterns-youll-reuse-forever-5ed193226d2b)
9. [dbt Incremental Patterns (Feb 2026)](https://docs.getdbt.com/best-practices/how-we-handle-real-time-data/2-incremental-patterns)
10. [dbt + DuckDB Reproducible Analytics (Jan 2026)](https://medium.com/@sendoamoronta/dbt-duckdb-for-reproducible-analytics-runtime-engineering-and-advanced-performance-patterns-3fab4e596f75)

### Education Data Standards
11. [Common Education Data Standards (CEDS)](https://ceds.ed.gov/) - Official site
12. [Ed-Fi Data Standard](https://docs.ed-fi.org/reference/data-exchange/data-standards) - Official docs
13. [Ed-Fi Alliance](https://www.ed-fi.org/ed-fi-data-standard/) - Overview
14. [How Ed-Fi Can Help (Education Analytics)](https://www.edanalytics.org/resources/how-ed-fi-can-help-you-make-the-most-of-your-data)

### FERPA & Privacy
15. [FERPA Overview (U.S. Dept of Education)](https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html)
16. [Student Privacy & Online Services (2014)](https://tech.ed.gov/files/2014/09/Student-Privacy-and-Online-Educational-Services-February-2014.pdf)
17. [FERPA Guidelines (StudentPrivacy.ed.gov)](https://studentprivacy.ed.gov/)

### Star Schema & Data Warehousing
18. Kimball, Ralph. *The Data Warehouse Toolkit* (3rd Edition, 2013) - Industry bible
19. Various GitHub examples of education data warehouses

---

## Conclusion

Our MotherDuck + dbt + Aeries implementation follows modern best practices for education data warehousing. The architecture is sound, cost-effective, and aligned with 2026 patterns.

**Key strengths**:
- Token security ✅
- Star schema design ✅
- dbt transformation layer ✅
- Cost-effective platform ✅

**Must address before production**:
- FERPA compliance gaps 🚨
- Access control model 🚨
- Testing coverage ⚠️
- SCD strategy ⚠️

**Optional enhancements**:
- Physical partitioning (DuckLake)
- Microbatch incremental strategy
- Hybrid local/cloud execution

---

**Research completed**: February 22, 2026  
**Next action**: Review with team, prioritize Phase 1 critical items
