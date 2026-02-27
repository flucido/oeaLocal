# Rill Dashboard Guide

Complete guide to using and maintaining the Rill dashboards in the local-data-stack project.

---

## Quick Start

```bash
# 1. Ensure data pipeline has run
cd oss_framework/dbt && dbt build

# 2. Export analytics views to Parquet
cd ../.. && python3 scripts/export_to_rill.py

# 3. Start Rill
cd rill_project && rill start
# Opens http://localhost:9009
```

---

## Available Dashboards

All 5 analytics dashboards are now operational:

### 1. Chronic Absenteeism Risk
**Purpose:** Monitors students at risk of chronic absenteeism

**Key Metrics:**
- Total students tracked
- Chronically absent students (10%+ absences)
- Chronic absence rate
- 30-day attendance trends
- Average risk scores
- High-risk student count

**Dimensions:**
- Student demographics (grade, school, gender, race/ethnicity)
- Program participation (ELL, SpEd, FRL)
- Risk level (Low, Moderate, High)
- Attendance trend (Improving, Stable, Declining)

**Use Cases:**
- Identify students needing intervention
- Track attendance trends over time
- Compare risk across demographic groups
- Monitor intervention effectiveness

---

### 2. Equity Outcomes by Demographics
**Purpose:** Analyzes outcome disparities across demographic groups

**Key Metrics:**
- Cohort sizes
- Good attendance rate (>90%)
- No discipline incidents rate
- Average GPA
- GPA 2.5+ rate
- Below C average rate

**Dimensions:**
- Race/Ethnicity
- English Learner status
- Special Education status
- Economically Disadvantaged status

**Use Cases:**
- Identify equity gaps in outcomes
- Compare performance across groups
- Track progress on equity initiatives
- Support data-driven equity planning

---

### 3. Class Effectiveness Analysis
**Purpose:** Compares class/section performance across schools and courses

**Key Metrics:**
- Total sections analyzed
- Total student enrollment
- Average grades (numeric)
- Pass rates (overall and by subgroup)
- A/B grade percentages
- ELL/SpEd/FRL pass rates
- Effectiveness ratings

**Dimensions:**
- Course ID
- School
- Grade level
- Term (Q1, Q2, Q3, Q4)
- Effectiveness rating (Highly Effective, Effective, Needs Support, Underperforming)

**Use Cases:**
- Identify high-performing sections
- Compare teacher effectiveness
- Track equity in course outcomes
- Support professional development planning

---

### 4. Performance Correlations Analysis
**Purpose:** Analyzes correlations between attendance, discipline, and academic performance

**Key Metrics:**
- Total correlations tracked
- Average correlation coefficients
- Strong/Moderate/Weak correlation counts
- Total data points analyzed

**Dimensions:**
- Correlation pairs (e.g., "Attendance vs GPA")
- Expected direction (Positive, Negative)
- Strength category (Strong, Moderate, Weak)

**Use Cases:**
- Validate intervention logic
- Understand performance drivers
- Identify unexpected patterns
- Support evidence-based decision making

---

### 5. Student Wellbeing Risk Profiles
**Purpose:** Identifies students at risk across attendance, discipline, and academic domains

**Key Metrics:**
- Total students profiled
- Critical/High/Moderate/Low risk counts
- Average wellbeing risk scores
- Domain-specific risk scores (attendance, discipline, academic)
- Multiple high-risk domain counts
- Primary concern breakdowns

**Dimensions:**
- Student ID (anonymized)
- Grade level
- School
- Wellbeing risk level (Critical, High, Moderate, Low)
- Primary concern (Attendance, Discipline, Academic, Multiple)
- High-risk domain count (0-3)

**Use Cases:**
- Multi-tiered intervention planning
- Identify students needing comprehensive support
- Track holistic student wellbeing
- Coordinate cross-functional support teams

---

## Dashboard Architecture

### Data Flow

```
Aeries API / Excel Files
         ↓
   Stage 1: Bronze Layer (Parquet)
   - Raw data ingestion
   - Partitioned by load_date
         ↓
   Stage 2: Silver Layer (DuckDB + dbt)
   - Privacy transformations (SHA256 hashing)
   - Data quality validation
   - Dimension tables (students, schools, courses)
         ↓
   Stage 3: Gold Layer (Analytics Views)
   - Aggregated analytics
   - Risk scoring
   - Correlation analysis
         ↓
   Export to Parquet (scripts/export_to_rill.py)
   - DuckDB → Parquet files
   - Located in rill_project/data/
         ↓
   Rill SQL Models
   - SELECT * FROM read_parquet('data/*.parquet')
   - Located in rill_project/models/
         ↓
   Rill Dashboards
   - Metrics views with dimensions & measures
   - Located in rill_project/dashboards/
```

### File Structure

```
rill_project/
├── rill.yaml                          # Project configuration
├── connectors/
│   └── duckdb.yaml                   # DuckDB connector (local)
├── data/                             # Parquet files (exported)
│   ├── chronic_absenteeism_risk.parquet
│   ├── equity_outcomes_by_demographics.parquet
│   ├── class_effectiveness.parquet
│   ├── performance_correlations.parquet
│   └── wellbeing_risk_profiles.parquet
├── models/                           # SQL models (read Parquet)
│   ├── chronic_absenteeism_risk.sql
│   ├── equity_outcomes_by_demographics.sql
│   ├── class_effectiveness.sql
│   ├── performance_correlations.sql
│   └── wellbeing_risk_profiles.sql
└── dashboards/                       # Dashboard definitions (YAML)
    ├── chronic_absenteeism_risk.yaml
    ├── equity_outcomes_by_demographics.yaml
    ├── class_effectiveness.yaml
    ├── performance_correlations.yaml
    └── wellbeing_risk_profiles.yaml
```

---

## Updating Dashboards After Data Changes

### Full Pipeline Run

```bash
# 1. Run dbt transformations (Stage 2 & 3)
cd oss_framework/dbt
dbt build

# 2. Export analytics views to Parquet
cd ../..
python3 scripts/export_to_rill.py

# 3. Rill auto-refreshes when Parquet files change
# (If Rill is already running, it detects changes automatically)
cd rill_project && rill start
```

### Export Specific Views Only

```bash
# Export only views matching "chronic"
python3 scripts/export_to_rill.py --view chronic

# Export only views matching "equity"
python3 scripts/export_to_rill.py --view equity

# Preview exports without writing files (dry run)
python3 scripts/export_to_rill.py --dry-run
```

### Verify Export Success

```bash
# Check Parquet files exist and are recent
ls -lh rill_project/data/*.parquet

# Check DuckDB views directly
duckdb oss_framework/data/oea.duckdb
→ SELECT COUNT(*) FROM main_analytics.v_chronic_absenteeism_risk;
→ SELECT COUNT(*) FROM main_analytics.v_class_section_comparison;
→ .quit
```

---

## Dashboard Customization

### Adding New Measures

Edit the dashboard YAML file to add new measures:

```yaml
# Example: Add a new measure to chronic_absenteeism_risk.yaml
measures:
  - name: severe_risk_students
    label: "Severe Risk Students (>20% absences)"
    expression: SUM(CASE WHEN chronic_absence_flag = 1 AND attendance_rate_30d < 80 THEN 1 ELSE 0 END)
    format_preset: humanize
```

### Adding New Dimensions

```yaml
# Example: Add a new dimension
dimensions:
  - name: foster_care
    label: "Foster Care Status"
    column: foster_care
    description: "Student in foster care system"
```

### Changing Time Series

```yaml
# Change the time series field (default: _loaded_at)
timeseries: enrollment_date
```

---

## Common Operations

### Filter Data in Dashboards

Rill provides interactive filters in the UI:
1. Click any dimension value to filter
2. Use the time picker to change date range
3. Apply multiple filters simultaneously
4. Export filtered data to CSV

### Create Custom Views

1. Use Rill's pivot table feature
2. Select dimensions and measures
3. Apply filters
4. Save view (Rill auto-saves state in URL)
5. Share URL with colleagues

### Export Reports

1. Filter to desired data
2. Click "Export" button
3. Choose format (CSV, Excel, JSON)
4. Download file

---

## Troubleshooting

### Dashboard Shows "No Data"

**Symptoms:** Dashboard loads but shows 0 rows

**Solutions:**
```bash
# 1. Check if Parquet files exist
ls -lh rill_project/data/*.parquet

# 2. Re-export from DuckDB
python3 scripts/export_to_rill.py

# 3. Check DuckDB views have data
duckdb oss_framework/data/oea.duckdb
→ SELECT COUNT(*) FROM main_analytics.v_chronic_absenteeism_risk;
```

---

### Dashboard Shows Old Data

**Symptoms:** Dashboard data doesn't reflect recent pipeline runs

**Solutions:**
```bash
# 1. Re-export Parquet files
python3 scripts/export_to_rill.py

# 2. Restart Rill to force reload
# (In terminal where Rill is running, press Ctrl+C)
cd rill_project && rill start

# 3. Verify _loaded_at timestamps
# Open dashboard and check the latest _loaded_at value
```

---

### Dashboard Shows Error "Cannot read parquet"

**Symptoms:** Rill shows error loading Parquet file

**Solutions:**
```bash
# 1. Check Parquet file permissions
ls -l rill_project/data/*.parquet

# 2. Validate Parquet file integrity
duckdb -c "SELECT COUNT(*) FROM read_parquet('rill_project/data/chronic_absenteeism_risk.parquet')"

# 3. Re-export from source
python3 scripts/export_to_rill.py --view chronic
```

---

### Rill Won't Start

**Symptoms:** `rill start` fails or shows errors

**Solutions:**
```bash
# 1. Check Rill version
rill version

# 2. Upgrade Rill if needed
rill upgrade

# 3. Verify rill.yaml is valid
cd rill_project
cat rill.yaml

# 4. Check for port conflicts (default: 9009)
lsof -i :9009
# Kill conflicting process if needed

# 5. Start Rill with verbose logging
rill start --log-level debug
```

---

## Performance Optimization

### Dashboard Loading Slow

**Symptoms:** Dashboard takes >5 seconds to load

**Optimizations:**

1. **Limit default time range** in dashboard YAML:
   ```yaml
   defaults:
     time_range: P30D  # Last 30 days instead of all time
   ```

2. **Pre-aggregate data** in dbt before export:
   ```sql
   -- In dbt model
   SELECT
       date_trunc('week', date) as week,
       school_id,
       COUNT(*) as student_count,
       AVG(attendance_rate) as avg_attendance
   FROM fact_attendance
   GROUP BY 1, 2
   ```

3. **Reduce measure complexity**:
   ```yaml
   # Instead of complex CASE statements in dashboard
   # Pre-calculate in dbt and expose as simple SUM
   measures:
     - name: high_risk_count
       expression: SUM(high_risk_flag)  # Pre-calculated in dbt
   ```

---

## Best Practices

### Data Privacy
- **Never export PII to Rill:** All student identifiers are SHA256 hashes
- **Verify privacy transformations:** Check dbt models apply hashing correctly
- **Audit dashboard access:** Rill is local-only (http://localhost:9009)

### Data Quality
- **Run contract tests before export:**
  ```bash
  cd scripts/contracts && python contract_tests.py
  ```
- **Validate row counts:** Check export script output for expected counts
- **Monitor _loaded_at:** Ensure timestamps update after each export

### Dashboard Design
- **Use meaningful labels:** dimension.label should be human-readable
- **Add descriptions:** Help users understand metrics
- **Set sensible defaults:** Pre-select most-used measures/dimensions
- **Choose appropriate format_preset:**
  - `humanize`: Whole numbers with commas (e.g., 1,234)
  - `percentage`: Percentages (e.g., 85.5%)
  - `currency_usd`: Dollar amounts (e.g., $1,234.56)

---

## Advanced Topics

### Creating New Dashboards

**Step 1: Create dbt analytics view** (in `oss_framework/dbt/models/mart_analytics/`)
```sql
-- models/mart_analytics/analytics/v_discipline_trends.sql
SELECT
    student_key,
    school_id,
    grade_level,
    COUNT(*) as incident_count,
    MAX(incident_date) as last_incident_date,
    CURRENT_TIMESTAMP as _loaded_at
FROM {{ ref('fact_discipline') }}
GROUP BY 1, 2, 3
```

**Step 2: Run dbt to create view**
```bash
cd oss_framework/dbt
dbt run --select v_discipline_trends
```

**Step 3: Update export script** (add to `ANALYTICS_VIEWS` in `scripts/export_to_rill.py`)
```python
ANALYTICS_VIEWS = {
    # ... existing views ...
    "main_analytics.v_discipline_trends": "discipline_trends.parquet",
}
```

**Step 4: Export to Parquet**
```bash
python3 scripts/export_to_rill.py
```

**Step 5: Create Rill SQL model** (`rill_project/models/discipline_trends.sql`)
```sql
-- Discipline Trends Model
-- Source: Parquet export from dbt model v_discipline_trends
SELECT * FROM read_parquet('data/discipline_trends.parquet')
```

**Step 6: Create Rill dashboard** (`rill_project/dashboards/discipline_trends.yaml`)
```yaml
type: metrics_view
title: "Discipline Trends Analysis"
model: discipline_trends
timeseries: _loaded_at

dimensions:
  - name: student_key
    label: "Student ID"
    column: student_key
  - name: school_id
    label: "School"
    column: school_id
  - name: grade_level
    label: "Grade Level"
    column: grade_level

measures:
  - name: total_students
    label: "Total Students"
    expression: COUNT(DISTINCT student_key)
    format_preset: humanize
  - name: total_incidents
    label: "Total Incidents"
    expression: SUM(incident_count)
    format_preset: humanize
  - name: avg_incidents_per_student
    label: "Avg Incidents per Student"
    expression: SUM(incident_count) * 1.0 / COUNT(DISTINCT student_key)
    format_preset: humanize
```

**Step 7: Test in Rill**
```bash
cd rill_project && rill start
```

---

## Resources

### Official Documentation
- **Rill Docs:** https://docs.rilldata.com
- **DuckDB Docs:** https://duckdb.org/docs/
- **dbt Docs:** https://docs.getdbt.com

### Project Documentation
- **Architecture:** `/docs/architecture/data-model.md`
- **Project Analysis:** `/docs/architecture/PROJECT_ANALYSIS_AND_PLAN.md`
- **Export Script:** `/scripts/export_to_rill.py`
- **dbt Models:** `/oss_framework/dbt/models/mart_analytics/`

### Example Dashboards
- **Rill Examples Repo:** https://github.com/rilldata/rill-examples
- **Live Demos:** https://ui.rilldata.com/demo/rill-github-analytics

---

## Changelog

### 2026-02-26
- ✅ Created 3 new dashboards: Class Effectiveness, Performance Correlations, Wellbeing Risk
- ✅ Automated Parquet export script (`scripts/export_to_rill.py`)
- ✅ Updated README with dashboard status
- ✅ All 5 dashboards operational

### Previous
- ✅ Created 2 initial dashboards: Chronic Absenteeism Risk, Equity Outcomes
- ✅ Established Rill project structure
- ✅ Configured DuckDB connector

---

**Status:** All 5 dashboards operational | Last Updated: 2026-02-26
