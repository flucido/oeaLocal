# Data Refresh Runbook

## Overview

This document describes how to refresh the Aeries data pipeline from source files through local DuckDB analytics.

## Architecture

```
┌─────────────────────┐
│  Aeries CSV Exports │
│  (Desktop folder)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 1: Raw       │
│  Parquet files      │
│  data/stage1/       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 2: DuckDB    │
│  oea.duckdb         │
│  raw_* tables       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 3: dbt       │
│  Transformations    │
│  staging → core     │
└─────────────────────┘
```

## Course Code Reference

**IMPORTANT**: Aeries course codes have leading zeros stripped in the pipeline.

| Aeries Code | Our Code | Course Name |
|-------------|----------|-------------|
| 000325 | 325 | Math 8 |
| 000329 | 329 | Apex Math 8 |
| 000308 | 308 | Algebra 1 |
| 001205 | 1205 | LEAD Program |

## Refresh Steps

### Step 1: Update Source Data

1. Export new data from Aeries (or prepare CSV files)
2. Place files in: `data/stage1/raw/aeries/`
3. Ensure CSV files are named consistently:
   - `students/students_YYYY_YYYY.csv`
   - `programs/programs_YYYY_YYYY.csv`
   - etc.

### Step 2: Run Data Pipeline

```bash
cd /path/to/local-data-stack

# Run full 3-stage pipeline
python scripts/run_pipeline.py

# Or run stages individually:
python scripts/run_pipeline.py --stage 1  # Ingestion only
python scripts/run_pipeline.py --stage 2  # dbt refinement only
python scripts/run_pipeline.py --stage 3  # dbt analytics only
```

### Step 3: Verify Results

```bash
# Check DuckDB data
duckdb oss_framework/data/oea.duckdb

# Query available tables
SELECT table_schema, table_name, estimated_size 
FROM information_schema.tables 
WHERE table_schema IN ('staging', 'core', 'analytics')
ORDER BY table_schema, table_name;

# Sample query
SELECT COUNT(*) FROM core.dim_students;
```

### Step 4: Launch Rill Dashboard

```bash
# Start Rill server
rill start

# Opens browser to http://localhost:9009
# Browse available dashboards and metrics
```

## Available Analytics Tables

### Core Tables
- `core.dim_students` - Student dimension with demographics
- `core.fact_attendance` - Attendance records
- `core.fact_discipline` - Discipline incidents
- `core.fact_academic_records` - Grades and courses
- `core.fact_enrollment` - Enrollment history

### Analytics Tables (for Rill/Jupyter)
- `analytics.chronic_absenteeism_risk` - Students at risk of chronic absenteeism
- `analytics.equity_outcomes_by_demographics` - Equity metrics by subgroup
- `analytics.math_pathways_7th_grade` - Math 8 vs Apex Math 8
- `analytics.algebra_1_outcomes` - Algebra 1 grade distribution
- `analytics.lead_program_enrollment` - LEAD program demographics

## Troubleshooting

### "Course code not found"
- Check if leading zeros were stripped
- Use 325, 329, 308, 1205 instead of 000325, 000329, 000308, 001205

### "DuckDB file not found"
- Ensure `oss_framework/data/oea.duckdb` exists
- Run `python scripts/run_pipeline.py --stage 1` to initialize

### "dbt command not found"
- Activate virtual environment: `source venv/bin/activate`
- Or install dbt: `pip install dbt-duckdb`

### "Rill command not found"
- Install Rill: `brew install rilldata/tap/rill` (macOS)
- Or download from: https://github.com/rilldata/rill/releases

## Schedule

Recommended refresh schedule:
- **Daily**: Attendance, discipline updates
- **Weekly**: Enrollment changes
- **End of Term**: Grades, academic records
- **Annual**: Full refresh with new school year data

## Quick Refresh Script

```bash
#!/bin/bash
# save as: scripts/quick_refresh.sh

cd /path/to/local-data-stack

echo "Running full data pipeline..."
python scripts/run_pipeline.py

echo "Starting Rill dashboard..."
rill start

echo "Refresh complete! Dashboard at http://localhost:9009"
```

Make executable: `chmod +x scripts/quick_refresh.sh`

---

*Last updated: 2026-02-25*
