# Data Refresh Runbook

## Overview

This document describes how to refresh the Aeries data pipeline from source files to MotherDuck analytics.

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
│  oss_framework/data/│
│  stage1/aeries/     │
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
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Stage 4: MotherDuck│
│  Cloud publishing   │
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

1. Export new data from Aeries to Desktop folder:
   ```
   /Users/flucido/Desktop/AeRIES test data/
   ```

2. Ensure CSV files are named consistently:
   - `students/students_YYYY_YYYY.csv`
   - `programs/programs_YYYY_YYYY.csv`
   - etc.

### Step 2: Ingest to Parquet (Stage 1)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/pipelines
python3 aeries_to_parquet.py
```

This reads from Desktop CSVs and writes Parquet files to:
```
oss_framework/data/stage1/aeries/
```

### Step 3: Sync to DuckDB (Stage 2)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/scripts
python3 sync_to_duckdb.py
```

### Step 4: Run dbt Transformations (Stage 3)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/dbt

# Full refresh (rebuild all tables)
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['run', '--full-refresh'])"

# Incremental refresh (faster)
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['run'])"

# Run tests
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['test'])"
```

### Step 5: Publish to MotherDuck (Stage 4)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/scripts
export $(grep -v '^#' ../.env | xargs)
python3 publish_to_motherduck.py
```

## Quick Refresh (All Steps)

```bash
#!/bin/bash
# Quick refresh script

cd /Users/flucido/projects/openedDataEstate

# Stage 1: Ingest
echo "Stage 1: Ingesting to Parquet..."
cd oss_framework/pipelines
python3 aeries_to_parquet.py

# Stage 2-3: dbt
echo "Stage 2-3: Running dbt..."
cd ../dbt
python3 -c "from dbt.cli.main import dbtRunner; dbtRunner().invoke(['run', '--full-refresh'])"

# Stage 4: Publish
echo "Stage 4: Publishing to MotherDuck..."
cd ../scripts
export $(grep -v '^#' ../.env | xargs)
python3 publish_to_motherduck.py

echo "Refresh complete!"
```

## Available Analytics Tables

### Core Tables
- `core.dim_students` - Student dimension with demographics
- `core.fact_attendance` - Attendance records
- `core.fact_discipline` - Discipline incidents
- `core.fact_academic_records` - Grades and courses
- `core.fact_enrollment` - Enrollment history

### Analytics Tables (for Hex)
- `analytics.analytics_for_hex` - Student-level analytics
- `analytics.equity_by_race` - Equity outcomes by race
- `analytics.school_summary` - School-level metrics
- `analytics.math_pathways_7th_grade` - Math 8 vs Apex Math 8
- `analytics.algebra_1_outcomes` - Algebra 1 grade distribution
- `analytics.lead_program_enrollment` - LEAD program demographics

## Troubleshooting

### "Course code not found"
- Check if leading zeros were stripped
- Use 325, 329, 308, 1205 instead of 000325, 000329, 000308, 001205

### "MOTHERDUCK_TOKEN not set"
- Ensure `.env` file exists in `oss_framework/`
- Check that `MOTHERDUCK_TOKEN` is defined

### "No data in MotherDuck"
- Run `publish_to_motherduck.py` after dbt transformations

## Schedule

Recommended refresh schedule:
- **Daily**: Attendance, discipline updates
- **Weekly**: Enrollment changes
- **End of Term**: Grades, academic records
- **Annual**: Full refresh with new school year data

---

*Last updated: 2026-02-23*
