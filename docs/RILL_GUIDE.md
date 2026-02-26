# Rill Guide - Creating Custom Dashboards

Complete guide to creating interactive BI dashboards in the local-data-stack using Rill.

---

## What is Rill?

**Rill** is a local-first BI tool that generates interactive dashboards directly from SQL models. Unlike traditional BI tools (Tableau, Metabase), Rill:

- **Runs locally** - No cloud account required (http://localhost:9009)
- **Queries DuckDB directly** - No data copying or ETL to a separate BI database
- **Version controlled** - Dashboards defined in YAML (commit to git)
- **Fast** - Sub-second query response with pre-aggregation
- **Developer-friendly** - SQL models + YAML configs (no drag-and-drop UI)

---

## Rill Project Structure

```
local-data-stack/
├── rill.yaml                           # Rill project configuration
├── connectors/
│   └── duckdb.yaml                     # DuckDB connection settings
├── models/
│   ├── chronic_absenteeism_risk.sql    # SQL model (queries DuckDB)
│   └── equity_outcomes_by_demographics.sql
└── dashboards/
    ├── chronic_absenteeism_risk.yaml   # Dashboard definition
    └── equity_outcomes_by_demographics.yaml
```

**Workflow:**
1. **SQL Model** - Queries dbt output tables from DuckDB
2. **Dashboard YAML** - Defines metrics, dimensions, visualizations
3. **Rill Developer** - Renders interactive UI at http://localhost:9009

---

## Rill Working Directory Requirements

### Critical: Working Directory Matters

Rill resolves **all file paths relative to the directory where `rill start` is executed**. This affects connector DSN paths, model imports, and dashboard references.

### Canonical Rill Project Location

The canonical Rill project is located at **`rill_project/`** (tracked in git):

```
local-data-stack/
├── rill_project/              # ✅ Canonical Rill configuration
│   ├── rill.yaml
│   ├── connectors/
│   ├── dashboards/
│   ├── models/
│   └── sources/
└── archive/obsolete-rill-root/  # ❌ Obsolete (archived root files)
```

### Correct Usage

**Always start Rill from the `rill_project/` directory:**

```bash
# From repository root
cd rill_project/
rill start
# Opens http://localhost:9009
```

**Why this works:**
- Connector DSN: `./oss_framework/data/oea.duckdb` resolves to `rill_project/../oss_framework/data/oea.duckdb`
- Dashboard/model references resolve correctly
- Rill caches build artifacts in `rill_project/.rill/`

### Incorrect Usage (Will Fail)

**❌ Starting from repository root:**

```bash
# From repository root
rill start rill_project/
```

**Why this fails:**
- Working directory is still repo root
- Connector DSN `./oss_framework/data/oea.duckdb` resolves incorrectly
- Rill cannot find DuckDB database
- Dashboards may fail to load

**❌ Starting from obsolete root Rill files:**

```bash
# From repository root
rill start  # Uses archive/obsolete-rill-root/ files (outdated)
```

**Why this is wrong:**
- Uses archived/obsolete configuration
- Missing percentage/risk level fixes from `rill_project/`
- Dashboard definitions may be inconsistent

### CI/CD Implications

When automating Rill in CI/CD pipelines, **always `cd` into `rill_project/` first:**

```yaml
# GitHub Actions example
- name: Start Rill Developer
  run: |
    cd rill_project/
    rill start --no-open
```

```dockerfile
# Dockerfile example
WORKDIR /app/rill_project
CMD ["rill", "start", "--host", "0.0.0.0"]
```

### Troubleshooting

**"DuckDB file not found" error:**

1. Verify you're in `rill_project/` directory: `pwd`
2. Check connector DSN path: `cat connectors/duckdb.yaml`
3. Verify DuckDB exists: `ls -la ../oss_framework/data/oea.duckdb`

**Dashboard changes not appearing:**

1. Confirm you're editing files in `rill_project/dashboards/` (not `archive/obsolete-rill-root/`)
2. Rill auto-reloads on save — check terminal for errors
3. Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)

**Build artifacts in wrong location:**

- Rill creates `.rill/` directory in working directory where `rill start` was executed
- If you see `.rill/` in repo root instead of `rill_project/.rill/`, you started from the wrong directory
---

## Step 1: Create a SQL Model

SQL models query DuckDB tables (typically from Stage 3 dbt output).

### Example: `models/chronic_absenteeism_risk.sql`

```yaml
# Chronic Absenteeism Risk Model
# Reads from dbt-generated table in DuckDB

type: model
sql: |
  SELECT
    student_key,
    grade_level,
    school_id,
    gender,
    race_ethnicity,
    english_learner,
    special_education,
    economically_disadvantaged,
    homeless_flag,
    attendance_rate_30d,
    unexcused_absence_rate_30d,
    discipline_incidents_30d,
    attendance_rate_90d,
    attendance_trend_90d,
    chronic_absence_flag,
    composite_risk_score,
    risk_level,
    intervention_recommendation,
    _loaded_at
  FROM main_main_analytics.v_chronic_absenteeism_risk
```

**Key elements:**
- `type: model` - Declares this as a Rill model
- `sql: |` - Multi-line SQL query (YAML literal block)
- `FROM main_main_analytics.v_chronic_absenteeism_risk` - Queries current analytics mart table
- `_loaded_at` - Timestamp column for time-series analysis

### Model File Naming

- **Filename** = Model name (used in dashboards)
- `chronic_absenteeism_risk.sql` → model name: `chronic_absenteeism_risk`
- Use lowercase with underscores (SQL-friendly names)

---

## Step 2: Create a Dashboard YAML

Dashboards define **dimensions** (categorical), **measures** (numeric aggregations), and **visualizations**.

### Example: `dashboards/chronic_absenteeism_risk.yaml`

```yaml
# Chronic Absenteeism Risk Dashboard
# Source: dbt model v_chronic_absenteeism_risk
# Monitors students at risk of chronic absenteeism

type: metrics_view
title: "Chronic Absenteeism Risk"
model: chronic_absenteeism_risk  # References models/chronic_absenteeism_risk.sql
timeseries: _loaded_at           # Time dimension for trend analysis

dimensions:
  - name: student_key
    label: "Student ID"
    column: student_key
    description: "Anonymized student identifier"

  - name: grade_level
    label: "Grade Level"
    column: grade_level
    description: "Current grade level"

  - name: school_id
    label: "School"
    column: school_id
    description: "School identifier"

  - name: gender
    label: "Gender"
    column: gender

  - name: race_ethnicity
    label: "Race/Ethnicity"
    column: race_ethnicity

  - name: english_learner
    label: "English Learner"
    column: english_learner

  - name: special_education
    label: "Special Education"
    column: special_education

  - name: economically_disadvantaged
    label: "Economically Disadvantaged"
    column: economically_disadvantaged

  - name: chronic_absence_flag
    label: "Chronic Absence Flag"
    column: chronic_absence_flag
    description: "1 if student has missed 10%+ of school days"

  - name: risk_level
    label: "Risk Level"
    column: risk_level
    description: "Low, Medium, High, Critical"

  - name: attendance_trend_90d
    label: "90-Day Trend"
    column: attendance_trend_90d
    description: "improving, stable, declining"

measures:
  - name: total_students
    label: "Total Students"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize

  - name: chronic_absence_count
    label: "Chronically Absent Students"
    expression: SUM(chronic_absence_flag)
    format_preset: humanize

  - name: chronic_absence_rate
    label: "Chronic Absence Rate"
    expression: SUM(chronic_absence_flag) * 1.0 / NULLIF(COUNT(DISTINCT student_key), 0)
    format_preset: percentage

  - name: avg_attendance_rate_30d
    label: "Avg 30-Day Attendance Rate"
    expression: AVG(attendance_rate_30d) / 100.0
    format_preset: percentage

  - name: avg_risk_score
    label: "Avg Risk Score"
    expression: AVG(composite_risk_score)
    format_preset: humanize

  - name: high_risk_students
    label: "High Risk Students"
    expression: SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END)
    format_preset: humanize

# Default sorting
default_sort:
  - name: composite_risk_score
    desc: true
```

---

## Dashboard YAML Anatomy

### Required Fields

```yaml
type: metrics_view         # Dashboard type (always metrics_view for analytics)
title: "Dashboard Title"   # Display name in Rill UI
model: model_name          # SQL model to query (from models/ directory)
```

### Optional Fields

```yaml
timeseries: column_name    # Timestamp column for time-series charts
default_sort:              # Default sort order for data tables
  - name: measure_name
    desc: true
```

---

## Dimensions vs Measures

### Dimensions (Categorical)

**Dimensions** are categorical columns used for:
- Filtering (dropdown menus)
- Grouping (breakdowns by grade, school, demographics)
- Drill-down (click to filter)

**Syntax:**
```yaml
dimensions:
  - name: grade_level        # Column name (as returned by SQL model)
    label: "Grade Level"     # Display name in UI
    column: grade_level      # Column reference (usually same as name)
    description: "Student's current grade level"  # Tooltip help text
```

**Common dimension patterns:**
- **Identifiers**: `student_key`, `school_id`, `teacher_id`
- **Demographics**: `gender`, `race_ethnicity`, `english_learner`
- **Categories**: `risk_level`, `intervention_tier`, `program_participation`
- **Flags**: `chronic_absence_flag`, `special_education`, `homeless_flag`
- **Dates**: Use `timeseries` instead of dimension for date/timestamp columns

---

### Measures (Numeric Aggregations)

**Measures** are aggregated numeric values:
- Counts (`COUNT`, `COUNT DISTINCT`)
- Sums (`SUM`)
- Averages (`AVG`)
- Calculated metrics (rates, percentages)

**Syntax:**
```yaml
measures:
  - name: total_students
    label: "Total Students"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize    # Formats: humanize, percentage, currency_usd
```

**Measure expression examples:**

```yaml
# Count distinct students
expression: COUNT(DISTINCT student_key)

# Sum a numeric column
expression: SUM(days_absent)

# Average a rate
expression: AVG(attendance_rate)

# Calculate percentage (fraction form for format_preset: percentage)
expression: SUM(chronic_absence_flag) * 1.0 / NULLIF(COUNT(DISTINCT student_key), 0)

# Conditional aggregation
expression: SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END)

# Multiple conditions
expression: SUM(CASE WHEN attendance_rate < 90 AND discipline_incidents > 0 THEN 1 ELSE 0 END)
```

---

## Format Presets

Rill provides built-in format presets for measures:

| Format Preset | Example Output | Use Case |
|---------------|----------------|----------|
| `humanize` | 1,234 | Counts, scores, raw numbers |
| `percentage` | 85.3% | Rates, percentages (0-1 fraction expression) |
| `currency_usd` | $1,234.56 | Dollar amounts |
| (none) | 1234.5678 | Raw values |

**Usage:**
```yaml
measures:
  - name: chronic_absence_rate
    expression: SUM(chronic_absence_flag) * 1.0 / COUNT(DISTINCT student_key)
    format_preset: percentage  # Displays as "15.3%" when expression returns 0.153
```

---

## Time Series Configuration

For dashboards with time-based trends, specify a `timeseries` column:

```yaml
type: metrics_view
title: "Monthly Attendance Trends"
model: attendance_trends
timeseries: month_start_date  # Date or timestamp column
```

**Rill automatically provides:**
- Time range selector (last 7 days, last 30 days, YTD)
- Line charts for measures over time
- Time-based drill-down

### Academic Year Configuration

For K-12 data with July-June academic years:

```yaml
# In rill.yaml (project-level config)
first_month_of_year: 7  # July = start of academic year
```

**Effect:**
- "YTD" (Year-to-Date) means July 1 - Today (not Jan 1 - Today)
- Rill respects academic year boundaries in time range filters

---

## Dashboard Examples

### Example 1: Chronic Absenteeism Risk Dashboard

**Use case:** Monitor students at risk of chronic absenteeism (≥10% absences)

**SQL Model** (`models/chronic_absenteeism_risk.sql`):
```yaml
type: model
sql: |
  SELECT
    student_key,
    grade_level,
    school_id,
    gender,
    race_ethnicity,
    attendance_rate_30d,
    chronic_absence_flag,
    risk_level,
    _loaded_at AS date
  FROM main_main_analytics.v_chronic_absenteeism_risk
```

**Dashboard YAML** (`dashboards/chronic_absenteeism_risk.yaml`):
```yaml
type: metrics_view
title: "Chronic Absenteeism Risk"
model: chronic_absenteeism_risk
timeseries: date

dimensions:
  - name: grade_level
    label: "Grade Level"
    column: grade_level

  - name: school_id
    label: "School"
    column: school_id

  - name: gender
    label: "Gender"
    column: gender

  - name: race_ethnicity
    label: "Race/Ethnicity"
    column: race_ethnicity

  - name: risk_level
    label: "Risk Level"
    column: risk_level
    description: "Low, Medium, High, Critical"

measures:
  - name: total_students
    label: "Total Students"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize

  - name: chronic_absence_count
    label: "Chronically Absent"
    expression: SUM(chronic_absence_flag)
    format_preset: humanize

  - name: chronic_absence_rate
    label: "Chronic Absence Rate"
    expression: SUM(chronic_absence_flag) * 1.0 / NULLIF(COUNT(DISTINCT student_key), 0)
    format_preset: percentage

  - name: high_risk_students
    label: "High Risk Students"
    expression: SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END)
    format_preset: humanize

default_sort:
  - name: chronic_absence_rate
    desc: true
```

**What you get:**
- Time-series chart of chronic absence rate over time
- Filters by grade, school, gender, race/ethnicity
- Drill-down by clicking on chart/table rows
- Exportable data (CSV, JSON)

---

### Example 2: Equity Outcomes by Demographics

**Use case:** Identify outcome disparities across demographic groups

**SQL Model** (`models/equity_outcomes_by_demographics.sql`):
```yaml
type: model
sql: |
  SELECT
    race_ethnicity,
    english_learner,
    special_education,
    economically_disadvantaged,
    cohort_size,
    pct_good_attendance,
    pct_no_discipline,
    avg_gpa,
    pct_gpa_2_5_plus,
    pct_below_c,
    _loaded_at
  FROM main_main_analytics.v_equity_outcomes_by_demographics
```

**Dashboard YAML** (`dashboards/equity_outcomes_by_demographics.yaml`):
```yaml
type: metrics_view
title: "Equity Outcomes by Demographics"
model: equity_outcomes_by_demographics
timeseries: _loaded_at

dimensions:
  - name: race_ethnicity
    label: "Race/Ethnicity"
    column: race_ethnicity

  - name: english_learner
    label: "English Learner"
    column: english_learner

  - name: special_education
    label: "Special Education"
    column: special_education

  - name: economically_disadvantaged
    label: "Economically Disadvantaged"
    column: economically_disadvantaged

measures:
  - name: cohort_size
    label: "Cohort Size"
    expression: SUM(cohort_size)
    format_preset: humanize

  - name: avg_attendance
    label: "% Good Attendance (>90%)"
    expression: AVG(pct_good_attendance) / 100.0
    format_preset: percentage

  - name: avg_no_discipline
    label: "% No Discipline Incidents"
    expression: AVG(pct_no_discipline) / 100.0
    format_preset: percentage

  - name: avg_gpa
    label: "Average GPA"
    expression: AVG(avg_gpa)
    format_preset: humanize

  - name: avg_gpa_above_2_5
    label: "% GPA 2.5+"
    expression: AVG(pct_gpa_2_5_plus) / 100.0
    format_preset: percentage

  - name: avg_below_c
    label: "% Below C Average"
    expression: AVG(pct_below_c) / 100.0
    format_preset: percentage

default_sort:
  - name: cohort_size
    desc: true
```

**What you get:**
- Compare attendance, discipline, and GPA across demographic groups
- Identify equity gaps (e.g., lower attendance for English Learners)
- Filter by multiple demographic dimensions simultaneously

---

## Creating Your Own Dashboard

### Step-by-Step Workflow

#### 1. Identify the Data Source

Start with an analytics mart table (typically in `main_main_analytics`):

```bash
# Connect to DuckDB and list available tables
duckdb ./oss_framework/data/oea.duckdb

# List tables in analytics schema
SHOW TABLES IN main_main_analytics;

# Preview table structure
DESCRIBE main_main_analytics.your_table_name;

# Sample data
SELECT * FROM main_main_analytics.your_table_name LIMIT 10;
```

#### 2. Create SQL Model

Create `models/your_dashboard_name.sql`:

```yaml
type: model
sql: |
  SELECT
    -- Dimension columns (categorical)
    student_key,
    grade_level,
    school_id,

    -- Measure columns (numeric)
    gpa,
    attendance_rate,
    discipline_count,

    -- Timestamp column (for time series)
    report_date
  FROM main_main_analytics.your_table_name
  WHERE school_year = '2025-2026'  -- Optional filter
```

**Tips:**
- Include all columns you want to filter/group by (dimensions)
- Include all columns you want to aggregate (measures)
- Include a timestamp column if you want time-series charts
- Pre-filter in SQL if you only want specific data (e.g., current school year)

#### 3. Create Dashboard YAML

Create `dashboards/your_dashboard_name.yaml`:

```yaml
type: metrics_view
title: "Your Dashboard Title"
model: your_dashboard_name  # Matches filename (without .sql)
timeseries: report_date     # Optional: timestamp column

dimensions:
  - name: grade_level
    label: "Grade Level"
    column: grade_level

  # Add more dimensions...

measures:
  - name: total_students
    label: "Total Students"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize

  - name: avg_gpa
    label: "Average GPA"
    expression: AVG(gpa)
    format_preset: humanize

  # Add more measures...

default_sort:
  - name: avg_gpa
    desc: true
```

#### 4. Launch Rill Developer

```bash
rill start
```

Open browser at **http://localhost:9009** and navigate to your new dashboard.

#### 5. Iterate

- **Edit SQL model** → Save → Rill auto-reloads
- **Edit dashboard YAML** → Save → Rill auto-reloads
- Test filters, drill-downs, and time ranges
- Adjust measures and dimensions as needed

---

## Advanced Patterns

### Calculated Measures (Multiple Columns)

```yaml
measures:
  - name: attendance_to_gpa_ratio
    label: "Attendance/GPA Ratio"
    expression: (AVG(attendance_rate) / NULLIF(AVG(gpa), 0)) * 100
    format_preset: humanize
```

### Conditional Measures

```yaml
measures:
  - name: high_performers
    label: "High Performers (GPA ≥ 3.5, Attendance ≥ 95%)"
    expression: |
      SUM(CASE
        WHEN gpa >= 3.5 AND attendance_rate >= 95 THEN 1
        ELSE 0
      END)
    format_preset: humanize
```

### Multiple Sorting Levels

```yaml
default_sort:
  - name: risk_level
    desc: true
  - name: chronic_absence_rate
    desc: true
```

### Hidden Dimensions (For Filtering Only)

Omit `label` to hide from UI but keep for filtering:

```yaml
dimensions:
  - name: internal_flag
    column: internal_flag
    # No label = hidden from UI, but available in filters
```

---

## Troubleshooting

### Dashboard Doesn't Appear in Rill UI

**Cause**: File naming or syntax error.

**Fix:**
1. Check filename matches model name:
   - Model: `models/my_dashboard.sql`
   - Dashboard: `dashboards/my_dashboard.yaml`
2. Verify YAML syntax (use YAML linter)
3. Check Rill logs: `rill start` shows errors in terminal

### "Model not found" Error

**Cause**: Dashboard references non-existent model.

**Fix:**
1. Verify `model:` in dashboard YAML matches SQL model filename (without `.sql`)
2. Check `models/` directory contains the referenced file

### "Column not found" Error

**Cause**: Dashboard references column not returned by SQL model.

**Fix:**
1. Run SQL model query in DuckDB CLI:
   ```bash
   duckdb ./oss_framework/data/oea.duckdb
   ```
   ```sql
  SELECT * FROM main_main_analytics.your_table LIMIT 5;
   ```
2. Verify column names match exactly (case-sensitive)
3. Update dashboard YAML `column:` fields to match SQL output

### Dashboard Loads Slowly

**Cause**: SQL model queries unaggregated Stage 2 data.

**Fix:**
1. Create pre-aggregated Stage 3 dbt model
2. Update Rill SQL model to query Stage 3 (not Stage 2)
3. Add indexes in DuckDB (if needed):
   ```sql
  CREATE INDEX idx_student_key ON main_main_analytics.your_table(student_key);
   ```

### Time Series Not Working

**Cause**: `timeseries` column is not timestamp/date type.

**Fix:**
1. Verify column type in SQL model:
   ```sql
  DESCRIBE main_main_analytics.your_table;
   ```
2. Cast to timestamp if needed:
   ```yaml
   sql: |
     SELECT
       CAST(report_date AS TIMESTAMP) AS report_date,
       ...
   ```

### Contract Validation Before Commit

Run contract checks after changing Rill models/dashboards to catch schema and query drift early:

```bash
# CI-equivalent contract checks
python3 scripts/contracts/contract_tests.py

# Detailed per-query logs
scripts/contracts/run_query_audit_phase2.sh
```

See: [scripts/contracts/README.md](../scripts/contracts/README.md)

---

## Configuration Reference

### Project Configuration (`rill.yaml`)

```yaml
compiler: rillv1
display_name: "Local Education Analytics"
description: "Student analytics dashboard powered by local DuckDB data mart"

# DuckDB connector (defined in connectors/duckdb.yaml)
olap_connector: duckdb

# Development server settings
server:
  port: 9009
  host: localhost

# Academic year configuration (July-June)
first_month_of_year: 7

# AI features (disabled for local-only use)
ai:
  enabled: false
```

### Connector Configuration (`connectors/duckdb.yaml`)

```yaml
type: connector
driver: duckdb

# Connection DSN (uses environment variable with fallback)
dsn: "{{ env \"DUCKDB_DATABASE_PATH\" \"./oss_framework/data/oea.duckdb\" }}"

# Initialization SQL - load extensions and configure DuckDB
init_sql: |
  -- Load Delta extension for reading Delta Lake tables
  INSTALL delta;
  LOAD delta;

  -- Load httpfs for potential remote file access
  INSTALL httpfs;
  LOAD httpfs;

  -- Load JSON extension
  INSTALL json;
  LOAD json;

  -- Set memory limits (8GB for development)
  SET memory_limit='8GB';
  SET max_memory='8GB';

  -- Configure for analytics workloads
  SET threads=4;
  SET default_null_order='nulls_last';

# Connection pooling (optional for local use)
pool:
  max_size: 4
  max_idle_time: 300s
```

---

## Best Practices

### 1. Pre-Aggregate in dbt (Stage 3)

**Bad** (queries unaggregated data):
```yaml
sql: |
  SELECT
    student_key,
    DATE_TRUNC('month', attendance_date) AS month,
    AVG(attendance_rate) AS avg_attendance
  FROM mart_core.fact_attendance  -- Stage 2 (millions of rows)
  GROUP BY student_key, month
```

**Good** (queries pre-aggregated dbt model):
```yaml
sql: |
  SELECT
    student_key,
    month,
    avg_attendance
  FROM main_main_analytics.monthly_attendance_summary  -- Stage 3 (pre-aggregated)
```

### 2. Use Descriptive Labels

**Bad**:
```yaml
dimensions:
  - name: race_ethnicity
    label: "race_ethnicity"  # Same as column name
```

**Good**:
```yaml
dimensions:
  - name: race_ethnicity
    label: "Race/Ethnicity"
    description: "Primary race/ethnicity category (CALPADS aligned)"
```

### 3. Include Contextual Measures

Always include count measures alongside rates/percentages:

```yaml
measures:
  - name: cohort_size
    label: "Cohort Size"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize

  - name: chronic_absence_rate
    label: "Chronic Absence Rate"
    expression: SUM(chronic_absence_flag) * 1.0 / NULLIF(COUNT(DISTINCT student_key), 0)
    format_preset: percentage
```

**Why:** A 50% chronic absence rate for 2 students is less concerning than 50% for 200 students.

### 4. Version Control Everything

Commit all Rill files to git:
```bash
git add rill.yaml connectors/ models/ dashboards/
git commit -m "Add chronic absenteeism dashboard"
```

**Benefits:**
- Dashboard history tracked
- Team collaboration (code review)
- Rollback if dashboard breaks

### 5. Test SQL Models Independently

Before creating a dashboard, test SQL in DuckDB CLI:

```bash
duckdb ./oss_framework/data/oea.duckdb
```

```sql
-- Copy SQL from models/your_dashboard.sql and test
SELECT
  student_key,
  grade_level,
  AVG(attendance_rate) AS avg_attendance
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY student_key, grade_level
LIMIT 10;
```

Verify:
- Query runs without errors
- Column names match expectations
- Data types are correct
- Results look reasonable

---

## Next Steps

1. **Explore existing dashboards** - Open http://localhost:9009 and interact with pre-built dashboards
2. **Review dbt Stage 3 models** - Explore `oss_framework/dbt/models/mart_analytics/` for available tables
3. **Read official Rill docs** - https://docs.rilldata.com for advanced features (alerts, exports, embedding)
4. **Create your first custom dashboard** - Follow the step-by-step workflow above

---

## Resources

- **Rill Documentation**: https://docs.rilldata.com
- **Rill GitHub**: https://github.com/rilldata/rill
- **Rill Examples**: https://github.com/rilldata/rill-examples
- **DuckDB SQL Reference**: https://duckdb.org/docs/sql/introduction
- **YAML Syntax Guide**: https://yaml.org/spec/1.2/spec.html

---

## Getting Help

- **Project Issues**: https://github.com/flucido/local-data-stack/issues
- **Rill Community**: https://discord.gg/DJ5qcsxE (Rill Discord)
- **Rill Documentation**: https://docs.rilldata.com
