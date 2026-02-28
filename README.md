# local-data-stack

100% local education analytics platform with DuckDB, dbt, and Rill. No cloud dependencies.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-available-brightgreen.svg)](docs/README.md)

## Why this project exists

`local-data-stack` provides a complete local analytics stack:

- **Data ingestion** from Aeries API and Excel imports (multi-year support)
- **DuckDB + Delta/Parquet** lakehouse storage (all local)
- **dbt transformations** for data modeling
- **Rill dashboards** for BI and analytics
- **Simple orchestration** with Python scripts (no Dagster)

## Dataset

**Current Dataset:** AeriesTestData2_2026
- **Student-Years:** 5,232 rows (872 unique students across 6 academic years)
- **Time Range:** 2020-2021 through 2025-2026
- **Domains:** Students, Attendance, Academic Records, Discipline, Enrollment, Programs, Schools
- **Format:** Parquet files with year-based partitioning (`oss_framework/data/stage1/aeries/`)

**Data Volume:**
- Total records: 220,084 rows across all domains
- Compressed size: 2.69 MB (ZSTD compression)
- Database: DuckDB (`oss_framework/data/oea.duckdb`, 29 MB)

## Repository layout

```text
local-data-stack/
├── oss_framework/               # Core pipelines and transformations
├── src/                         # Database connection utilities
├── rill_project/                # Rill dashboards (canonical location)
│   ├── rill.yaml
│   ├── connectors/              # DuckDB connector config
│   ├── dashboards/              # Dashboard definitions
│   ├── models/                  # SQL models
│   └── sources/                 # Data source configs
├── scripts/                     # Orchestration scripts
├── data/                        # Local data storage (gitignored)
└── README.md                    # Project overview (this file)
```

## Available Dashboards

All 5 analytics dashboards are now operational:

| Dashboard | Status | Description |
|-----------|--------|-------------|
| **Chronic Absenteeism Risk** | ✅ Working | Monitors students at risk of chronic absenteeism with attendance trends and risk scoring |
| **Equity Outcomes by Demographics** | ✅ Working | Analyzes outcome disparities across demographic groups (race, ELL, SpEd, FRL) |
| **Class Effectiveness Analysis** | ✅ Working | Compares class/section performance across schools and courses |
| **Performance Correlations** | ✅ Working | Analyzes correlations between attendance, discipline, and academic performance |
| **Student Wellbeing Risk Profiles** | ✅ Working | Identifies students at risk across attendance, discipline, and academic domains |

**Quick Access:**
```bash
cd rill_project && rill start
# Open http://localhost:9009
```

## Quick start

### 1) Clone the repository

```bash
git clone https://github.com/flucido/local-data-stack.git
cd local-data-stack

### 2) Install Python dependencies

```bash
pip install -e .

### 3) Configure environment

From the repository root, copy the template and fill in your values:

```bash
cp .env.template .env
# Edit .env with your Aeries API credentials

### 4) Install Rill

```bash
curl https://rill.sh | sh
rill version

### 5) Run the data pipeline

```bash
# Run dbt transformations
cd oss_framework/dbt && dbt build

# Export analytics views to Parquet for Rill
python3 scripts/export_to_rill.py

### 6) Start Rill Developer

**Important:** Always start Rill from the `rill_project/` directory:

```bash
cd rill_project/
rill start
# Opens http://localhost:9009
# Opens http://localhost:9009

## Data Pipeline Architecture

```
Aeries API / Excel Files
         ↓
   Stage 1: Bronze (Parquet)
         ↓
   Stage 2: Silver (DuckDB + dbt)
         ↓
   Stage 3: Gold (Analytics Views)
         ↓
   Export to Parquet
         ↓
   Rill Dashboards
```

**Update Dashboards After Data Changes:**
```bash
# Re-export analytics views to Parquet
python3 scripts/export_to_rill.py

# Rill auto-refreshes when Parquet files change
cd rill_project && rill start
```

## dbt Test Results

**Current State (Post-Migration):**
- ✅ **128/128 tests passing** (100% success rate)
- ✅ 45/45 dbt models building successfully
- ✅ Multi-year grain validation across all staging and core models
- ✅ Privacy layer propagates `academic_year` through all transformations

Run tests: `cd oss_framework/dbt && dbt test`

## Core docs

- **Setup guide:** [docs/SETUP.md](docs/SETUP.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Rill guide:** [docs/RILL_GUIDE.md](docs/RILL_GUIDE.md)
- **Contract tests:** [scripts/contracts/README.md](scripts/contracts/README.md)

## Forked from openedDataEstate

This project is a local-only fork of [openedDataEstate](https://github.com/flucido/openedDataEstate), removing all cloud dependencies (MotherDuck, AWS S3) and replacing Metabase with Rill.

## License

- **Code:** [MIT License](LICENSE)
- **Documentation:** [Creative Commons Attribution 4.0](LICENSE)
