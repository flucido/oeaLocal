# Stage 4 - Task 4.01: Metabase Installation - Learnings

## Completed: January 26, 2026

### Successful Approaches

1. **Docker Compose Setup**
   - Used official `metabase/metabase:latest` image (503MB download, ~30 seconds)
   - Named container `oss-metabase` for clarity and easy management
   - Port 3000 mapped correctly, no conflicts
   - Health check endpoint (`/api/health`) responds immediately after initialization
   - Container reached healthy state in ~17 seconds after startup

2. **Volume Configuration**
   - Created named volume `oss-metabase-data` for persistence
   - Mounted DuckDB database as **read-only** (`:ro`) to prevent accidental writes
   - Volume mount path `/data` inside container maps to `../../data` (2 levels up from deployment dir)
   - Verified database accessible: `/data/oea.duckdb` (25MB) visible inside container

3. **Environment Variables**
   - H2 database for Metabase metadata: Simple, single-file, no external DB needed
   - Java heap size: 2GB max (`-Xmx2g`), 512MB initial (`-Xms512m`)
   - Site name: "OSS Student Analytics" - displays in UI
   - Plugin directory: `/plugins` for future DuckDB JDBC driver if needed

4. **Initialization and Startup**
   - Metabase initialization completed in **14.6 seconds**
   - Logs show successful: "Metabase Initialization COMPLETE"
   - Sample database automatically loaded (H2 with example data)
   - Search indexes created automatically (693ms)
   - Health check passed: `{"status":"ok"}`

5. **Documentation Quality**
   - Created comprehensive 600+ line README.md
   - Covers: Installation, first-time setup, troubleshooting, security, SQL examples
   - Includes Quick Reference Card for common operations
   - Documents all 5 analytics views with row counts and purposes
   - Step-by-step DuckDB connection instructions (3 options: Generic SQL, Native DuckDB, Plugin install)

### Technical Insights

1. **Metabase Architecture**
   - Uses H2 embedded database for metadata (users, dashboards, queries)
   - Separate from analytics database (DuckDB)
   - Quartz scheduler manages background tasks (sync, cache refresh)
   - REST API available at `/api/*` endpoints

2. **DuckDB Integration Considerations**
   - Native DuckDB driver may not be included in all Metabase versions
   - Fallback options: Generic SQL, PostgreSQL compatibility mode
   - JDBC driver can be added via plugins directory
   - Read-only mount prevents accidental data modification

3. **Performance Observations**
   - Container startup: ~17 seconds to healthy state
   - Initialization: 14.6 seconds from start to ready
   - Image pull: 503MB took ~30 seconds on fast connection
   - Health endpoint response: < 10ms

4. **Directory Structure Best Practice**
   - Deployment configs in: `deployment/metabase/`
   - Keeps infrastructure separate from data and code
   - Relative paths in docker-compose: `../../data` works cleanly
   - Plugin directory created but empty (ready for future use)

### Patterns and Conventions

1. **Container Naming**
   - Pattern: `oss-{service-name}` (e.g., `oss-metabase`, `oss-postgres`)
   - Consistent with existing `sis-postgres` naming
   - Easy to identify in `docker ps` output

2. **Volume Naming**
   - Pattern: `oss-{service}-data` (e.g., `oss-metabase-data`)
   - Descriptive and prevents conflicts
   - Persists across container recreations

3. **Network Naming**
   - Pattern: `oss-{service}-network`
   - Isolated network per service
   - Can be bridged later if needed for multi-container apps

4. **Documentation Standards**
   - Quick Start section first (most users need this)
   - Architecture diagram (ASCII art)
   - Prerequisites with verification commands
   - Troubleshooting with symptoms, diagnostics, solutions
   - Quick Reference Card at bottom

### Configuration Decisions

1. **Why H2 for Metadata?**
   - Simple, no external database needed
   - Single-file storage
   - Sufficient for single-instance deployment
   - Can migrate to PostgreSQL later if needed for HA

2. **Why Read-Only Mount?**
   - Prevents accidental data corruption
   - Analytics database should only be written by dbt
   - Metabase is a **read-only** BI tool for this use case
   - Security best practice

3. **Why Port 3000?**
   - Metabase default port (user familiarity)
   - No conflict in current environment
   - Documented how to change if needed

4. **Why `unless-stopped` Restart Policy?**
   - Auto-restart on host reboot
   - Manual `docker stop` respects user intent (doesn't restart)
   - More controlled than `always`

### Next Task Preparation

**Task 4.02: Build Dashboard 1 (Chronic Absenteeism)**

Prerequisites now complete:
- ✅ Metabase installed and running
- ✅ Container healthy and accessible
- ✅ DuckDB database mounted and verified
- ✅ Documentation complete

Required for Task 4.02:
- [ ] Complete initial Metabase setup wizard (manual, browser-based)
- [ ] Add DuckDB database connection (manual, browser-based)
- [ ] Verify analytics views are accessible
- [ ] Run test query to confirm data

**Important**: Task 4.01 completes the *infrastructure* setup. The initial Metabase configuration (admin account, database connection) must be done manually via the web UI. This is documented in README.md Section "First-Time Setup".

### Potential Issues to Watch

1. **DuckDB Driver Availability**
   - If native driver missing: Install JDBC driver via plugins
   - Documented in README.md with curl command
   - Alternative: Use Generic SQL connection (may have limitations)

2. **Memory Usage**
   - Allocated 2GB heap, should be sufficient for 3,400 students
   - Monitor with: `docker stats oss-metabase`
   - Can increase if needed by editing docker-compose.yml

3. **Query Performance**
   - Analytics views are pre-optimized (< 50ms in dbt)
   - Metabase adds ~10-50ms overhead (acceptable)
   - If slow: Enable Metabase caching (Settings → Caching)

4. **Data Refresh Confusion**
   - Metabase shows *current* data in DuckDB
   - Data is refreshed by dbt (separate process, nightly)
   - Users may expect "real-time" data (it's daily)
   - Document this clearly in training

### Commands for Reference

```bash
# Start Metabase
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d

# Check status
docker ps | grep oss-metabase

# View logs
docker logs -f oss-metabase

# Health check
curl http://localhost:3000/api/health

# Stop Metabase
docker-compose down

# Restart (after config changes)
docker-compose restart

# Access container shell
docker exec -it oss-metabase /bin/bash

# Verify database mount
docker exec oss-metabase ls -lh /data/

# Remove everything (including data volume - DESTRUCTIVE)
docker-compose down -v
```

### Time Investment

- Planning and research: ~10 minutes
- Docker Compose configuration: ~5 minutes
- Container startup and verification: ~3 minutes
- README.md documentation: ~30 minutes
- Testing and validation: ~5 minutes
- Notepad documentation: ~10 minutes

**Total: ~63 minutes** (within 1-hour estimate)

### Success Metrics

All criteria met:
- ✅ Metabase container running on port 3000
- ✅ Health check passing (`{"status":"ok"}`)
- ✅ DuckDB database accessible inside container
- ✅ Docker Compose configuration created
- ✅ Comprehensive documentation (README.md)
- ✅ Ready for next task (dashboard creation)

**Task 4.01: COMPLETE** ✅

## Research: MotherDuck, DuckDB, and Educational Data Warehouse (2026-02-22)

### MotherDuck Connection Patterns
- **Three auth methods**: config dict, connection string, environment variable (recommended)
- **Connection format**: `duckdb.connect("md:database_name")`
- **Token storage**: Use `motherduck_token` or `MOTHERDUCK_TOKEN` env var (never hardcode)
- **Supported versions**: DuckDB 1.4.4 (us-east-1: 1.3.0-1.4.4, eu-central-1: 1.4.1-1.4.4)
- **Hybrid queries**: Can query local and cloud data simultaneously

### DuckDB Parquet Optimization
- **ZSTD compression**: Best compression, levels 1-22 (recommend 5-7 for balance)
- **Row group sizing**: 100k-200k rows for educational data
  - High selectivity (filtering): 50k-100k rows → better pruning
  - Full scans (aggregations): 200k-500k rows → less overhead
- **Partition strategy**: Use Hive-style partitioning by `school_year`
- **Small files problem**: Consolidate into larger files, avoid thousands of tiny Parquets
- **Performance**: DuckDB uses Parquet min/max stats for row group pruning

### Type 2 SCD in dbt
- **Use dbt snapshots**: Built-in Type 2 SCD functionality
- **Timestamp strategy**: `strategy='timestamp'` with `updated_at` column (recommended)
- **Check strategy**: `strategy='check'` with `check_cols=['col1', 'col2']`
- **Generated columns**: `dbt_valid_from`, `dbt_valid_to`, `dbt_updated_at`, `dbt_scd_id`
- **MetricFlow support**: SCD Type II with `validity_params: is_start/is_end`
- **Entity type**: Use `type: natural` for SCD dimensions (allows multiple rows per key)

### Educational Data Warehouse Star Schema
- **CEDS reference**: Common Education Data Standards provides open-source star schema
- **Core dimensions**: Student, School, Course, Staff, Time
- **Core facts**: Attendance, Grades, Assessment, Discipline
- **Granularity**: Prefer atomic fact tables (one row per event) for flexibility
- **Conformed dimensions**: Share dimensions across fact tables for consistent reporting
- **Type 2 SCD**: Student (grade, status), School (principal), Course (description), Staff (role)

### Key Design Patterns
1. **dim_student**: Demographics, enrollment, special programs + Type 2 SCD tracking
2. **dim_time**: School calendar aware (school_year, academic_term, is_school_day)
3. **fact_attendance**: Atomic (daily per student) with status, minutes, excused flag
4. **fact_grades**: Term-based with GPA calculation support
5. **fact_assessment**: Standardized tests with performance levels and benchmarks
6. **Partition by school_year**: Enables efficient year-over-year queries

### Implementation Stack
- **Extract**: Raw data → MotherDuck cloud
- **Transform**: dbt with dbt-duckdb adapter
- **Store**: Parquet with ZSTD compression, Hive partitioning
- **Query**: DuckDB hybrid local/cloud queries
- **SCD**: dbt snapshots for automatic Type 2 tracking

### Code Examples Location
Full research document saved to: `/tmp/motherduck_duckdb_research.md`


## Educational Data Warehouse Reference Implementations - Research Findings

### Key Resources Discovered

#### 1. CEDS (Common Education Data Standards) Data Warehouse
- **Repository**: https://github.com/CEDStandards/CEDS-Data-Warehouse
- **Commit SHA**: ff14dab1f29553f0d493800ec74f56aef320d9b5
- **License**: Apache 2.0
- **Description**: Official CEDS star schema implementation for P-20W (Pre-K through Workforce) data

**Key Findings**:
- **DimPeople Table** - Type 2 SCD implementation for student dimension
  - Permalink: https://github.com/CEDStandards/CEDS-Data-Warehouse/blob/ff14dab1f29553f0d493800ec74f56aef320d9b5/src/CEDS-Data-Warehouse-Project/RDS/Tables/DimPeople.sql
  - Columns: `RecordStartDateTime`, `RecordEndDateTime` for Type 2 SCD tracking
  - Multiple student identifiers: State, District, National Migrant
  - Tracks `IsActiveK12Student`, `IsActivePsStudent` flags
  - Includes PII fields: SSN, emails, phone numbers, birthdate
  
- **FactK12StudentAttendanceRates** - Attendance fact table
  - Permalink: https://github.com/CEDStandards/CEDS-Data-Warehouse/blob/ff14dab1f29553f0d493800ec74f56aef320d9b5/src/CEDS-Data-Warehouse-Project/RDS/Tables/FactK12StudentAttendanceRates.sql
  - Grain: Student x School x Year x Demographics x GradeLevel
  - Measure: `StudentAttendanceRate DECIMAL(18,3)`
  - Foreign keys to SEA, LEA, K12School, K12Student, Demographics, GradeLevel

- **FactK12StudentEnrollments** - Enrollment fact table
  - Permalink: https://github.com/CEDStandards/CEDS-Data-Warehouse/blob/ff14dab1f29553f0d493800ec74f56aef320d9b5/src/CEDS-Data-Warehouse-Project/RDS/Tables/FactK12StudentEnrollments.sql
  - Tracks enrollment periods with `EnrollmentEntryDateId`, `EnrollmentExitDateId`
  - Status dimensions: English Learner, IDEA, Economically Disadvantaged, Homeless, Foster Care, Immigrant, Migrant, Military
  - Entry/Exit grade levels tracked
  - `FullTimeEquivalency DECIMAL(5,2)`, `StudentCount INT`

- **FactK12StudentDisciplines** - Discipline fact table
  - Permalink: https://github.com/CEDStandards/CEDS-Data-Warehouse/blob/ff14dab1f29553f0d493800ec74f56aef320d9b5/src/CEDS-Data-Warehouse-Project/RDS/Tables/FactK12StudentDisciplines.sql
  - Links to incident dimension via `IncidentId`, `IncidentIdentifier`
  - Measures: `DurationOfDisciplinaryAction DECIMAL(18,2)`, `DisciplineCount INT`
  - Tracks firearm-related incidents separately

#### 2. Ed-Fi Analytics Middle Tier (AMT)
- **Repository**: https://github.com/Ed-Fi-Alliance-OSS/Ed-Fi-Analytics-Middle-Tier
- **Commit SHA**: 5ff60d9617e9ef6b9d5b50f368783bdc053fa495
- **Description**: Denormalized views over Ed-Fi ODS for analytics

**Key Findings**:
- Creates analytics-friendly views on top of normalized Ed-Fi ODS
- StudentSchoolDim view provides denormalized student/school context
- Sample queries available for attendance, grades, enrollment trends
- Supports both SQL Server and PostgreSQL

#### 3. Naming Conventions Observed

**Dimension Tables**:
- Prefix: `Dim` + entity name (e.g., `DimPeople`, `DimK12Demographics`, `DimGradeLevels`)
- Surrogate key pattern: `Dim{TableName}Id` (e.g., `DimPersonId`, `DimK12SchoolId`)
- Type 2 SCD columns: `RecordStartDateTime`, `RecordEndDateTime`

**Fact Tables**:
- Prefix: `Fact` + grain descriptor (e.g., `FactK12StudentAttendanceRates`, `FactK12StudentEnrollments`)
- Foreign key pattern: dimension name + `Id` (e.g., `K12StudentId`, `SchoolYearId`)
- Date dimensions: separate FK for each date role (e.g., `EnrollmentEntryDateId`, `EnrollmentExitDateId`)

**Bridge Tables**:
- Prefix: `Bridge` + fact + many-to-many entity (e.g., `BridgeK12StudentEnrollmentRaces`)
- Used for handling multi-valued attributes (races, disabilities, languages)

**CEDS Element Metadata**:
- Extended properties link columns to CEDS elements
- Properties: `CEDS_GlobalId`, `CEDS_Element`, `CEDS_URL`, `CEDS_Def_Desc`
- Example: GlobalId `000271` = "Student Attendance Rate"
- URLs: https://ceds.ed.gov/CEDSElementDetails.aspx?TermId={id}

#### 4. Privacy/PII Handling Patterns

**Two-Table Pattern for PII**:
- `DimPeople` - Full historical person records with PII
- `DimPeople_Current` - Current snapshot for faster queries
- Fact tables reference both: `K12StudentId` (historical), `K12Student_CurrentId` (current)

**PII Fields in DimPeople**:
- SSN: `PersonIdentifierSSN`
- Contact: `ElectronicMailAddressHome`, `TelephoneNumberHome`, `TelephoneNumberMobile`
- Address: Stored in separate dimension (PersonAddress) linked via bridge table

#### 5. Best Practices Identified

1. **Index Strategy**:
   - Clustered index on surrogate key
   - Non-clustered indexes on FKs
   - Covering indexes for common query patterns
   - `WITH (FILLFACTOR = 80, DATA_COMPRESSION = PAGE)` for large dimensions

2. **Default Values**:
   - Use `-1` for missing dimension references (not NULL)
   - Requires `-1` record in each dimension for "Unknown" or "Missing"

3. **Grain Definition**:
   - Fact tables explicitly document grain in comments
   - One row per student x school x date x demographic slice

4. **Date Dimension Usage**:
   - Separate date dimension (`DimDates`) referenced by FK
   - Multiple date roles in same fact (entry date, exit date, incident date)

5. **Slowly Changing Dimensions**:
   - DimPeople uses Type 2 SCD with `RecordStartDateTime`/`RecordEndDateTime`
   - Facts link to specific historical version via temporal FK
   - Current dimension table (`DimPeople_Current`) for latest state

#### 6. Additional Resources Found

- **Ed-Fi Documentation**: https://docs.ed-fi.org/reference/analytics-middle-tier/
- **CEDS Element Lookup**: https://ceds.ed.gov/
- **K12 Analytics Engineering**: https://docs.k12analyticsengineering.dev/data-warehouse/overview
- **Ed Analytics dbt Package**: https://github.com/edanalytics/edu_wh (dbt models for Ed-Fi)

#### 7. Specific AeRIES Schema Guidance

**For Attendance Fact Table**:
- Model after `FactK12StudentAttendanceRates` structure
- Consider daily grain (`FactK12StudentDailyAttendances`) for detailed tracking
- Measures: attendance rate (decimal), days present/absent (integers)

**For Student Dimension**:
- Follow `DimPeople` pattern with Type 2 SCD
- Include AeRIES-specific identifiers (SSID, PermID, StudentID)
- Consider separate current/historical tables for performance

**For Discipline/Grades**:
- Use incident/assessment paradigm from CEDS
- Link facts to student via temporal FK to capture student state at event time
- Store measures (GPA, discipline duration) as decimals for aggregation flexibility

