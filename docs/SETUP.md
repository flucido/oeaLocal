# Local Data Stack - Setup Guide

Complete setup instructions for the 100% local education analytics platform.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** with pip
- **Git** for version control
- **Docker & Docker Compose** (optional, for containerized deployment)
- **8GB+ RAM** (16GB recommended for production workloads)
- **10GB+ disk space** for data storage

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/flucido/local-data-stack.git
cd local-data-stack
```

### 2. Install Python Dependencies

Install the project in editable mode:

```bash
pip install -e .
```

This installs all required packages from `pyproject.toml`:
- `duckdb` - Local embedded analytics database
- `dlt` (data load tool) - Data ingestion framework
- `dbt-duckdb` - dbt adapter for DuckDB
- `polars` - Fast DataFrame library
- `faker` - Test data generation
- Additional dependencies for Aeries API and Excel imports

### 3. Verify DuckDB Installation

```bash
# Check DuckDB CLI is available
duckdb --version
# Expected output: v0.x.x or higher
```

If DuckDB CLI is not installed, install via your package manager:

```bash
# macOS (Homebrew)
brew install duckdb

# Linux (APT)
wget https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
sudo mv duckdb /usr/local/bin/

# Windows (Scoop)
scoop install duckdb
```

### 4. Install Rill

Rill provides interactive BI dashboards powered by DuckDB:

```bash
# Install via official installer
curl https://rill.sh | sh

# Verify installation
rill version
# Expected output: Rill version v0.x.x
```

For manual installation or troubleshooting, see [Rill installation docs](https://docs.rilldata.com/install).

### 5. Configure Environment Variables

Copy the environment template and configure for your environment:

```bash
cp .env.template .env
```

Edit `.env` with your settings:

```bash
# === Aeries API Configuration ===
# Option A: API Key Authentication (Recommended)
AERIES_API_URL=https://api.aeries.com/v5
AERIES_API_KEY=your_api_key_here
AERIES_AUTH_METHOD=api_key

# === DuckDB Configuration ===
DUCKDB_DATABASE_PATH=./oss_framework/data/oea.duckdb
DUCKDB_MEMORY_LIMIT=8GB

# === Local Data Paths ===
STAGE1_PATH=./data/stage1
STAGE2_PATH=./data/stage2
STAGE3_PATH=./data/stage3

# === Rill Configuration ===
RILL_PORT=9009

# === Privacy & Security ===
PRIVACY_SALT=<generate_with_openssl>
AUDIT_LOGGING_ENABLED=true
```

**Important security notes:**

- **Never commit `.env` to version control** - it's already in `.gitignore`
- **Generate a random PRIVACY_SALT** for pseudonymization:
  ```bash
  openssl rand -base64 32
  ```
- **Store Aeries API credentials securely** - request from your Aeries administrator
- **Limit file permissions** on `.env`:
  ```bash
  chmod 600 .env
  ```

### 6. Create Data Directories

```bash
mkdir -p data/stage1 data/stage2 data/stage3
mkdir -p oss_framework/data
mkdir -p oss_framework/logs
```

---

## Understanding the Pipeline

The local-data-stack uses a **three-stage medallion architecture**:

### Stage 1: Data Ingestion (Bronze Layer)
- **Purpose**: Extract raw data from external sources
- **Tools**: `dlt` (data load tool) for Aeries API and Excel imports
- **Output**: Parquet files in `data/stage1/`
- **Run command**: `python scripts/run_pipeline.py --stage 1`

### Stage 2: Data Refinement (Silver Layer)
- **Purpose**: Standardize, deduplicate, and clean raw data
- **Tools**: `dbt` models tagged with `staging`
- **Output**: DuckDB tables in `mart_core` schema
- **Run command**: `python scripts/run_pipeline.py --stage 2`

### Stage 3: Analytics Marts (Gold Layer)
- **Purpose**: Build analytics-ready aggregations and features
- **Tools**: `dbt` models in `mart_features`, `mart_analytics`, `mart_scoring`
- **Output**: DuckDB tables optimized for BI dashboards
- **Run command**: `python scripts/run_pipeline.py --stage 3`

### dbt Configuration

The dbt project is configured in `oss_framework/dbt/profiles.yml`:

```yaml
duckdb_oss:
  target: 'dev'
  outputs:
    dev:
      type: 'duckdb'
      path: '../data/oea.duckdb'
      threads: 4
      extensions:
        - delta    # Delta Lake support
        - httpfs   # HTTP/S3 file access
        - json     # JSON parsing
```

Key dbt commands:
- `dbt run --select tag:staging` - Run Stage 2 (refinement) models
- `dbt run --select mart_core` - Run core dimension/fact tables
- `dbt run --select mart_features` - Run feature engineering models
- `dbt test` - Run data quality tests

---

## First Pipeline Run

### Option A: Run Full Pipeline (All Stages)

```bash
python scripts/run_pipeline.py
```

**What happens:**
1. Ingests data from Aeries API (students, enrollment, attendance, grades)
2. Imports Excel supplements (demographics, RFEP data)
3. Runs dbt staging models (Stage 2 refinement)
4. Runs dbt analytics models (Stage 3 marts)
5. Executes data quality tests

**Expected duration**: 15-45 minutes (depending on data volume)

### Option B: Run Specific Stage

```bash
# Stage 1 only (ingestion)
python scripts/run_pipeline.py --stage 1

# Stage 2 only (refinement)
python scripts/run_pipeline.py --stage 2

# Stage 3 only (analytics)
python scripts/run_pipeline.py --stage 3
```

### Option C: Skip Tests (Faster)

```bash
python scripts/run_pipeline.py --skip-tests
```

---

## Verify Pipeline Success

### Check DuckDB Tables

```bash
# Open DuckDB CLI
duckdb ./oss_framework/data/oea.duckdb

# List all tables
SHOW TABLES;

# Check student count (example)
SELECT COUNT(*) FROM mart_core.dim_students;

# Check attendance aggregations (example)
SELECT * FROM mart_analytics.chronic_absenteeism_risk LIMIT 10;

# Exit
.quit
```

### Check Parquet Files

```bash
# Stage 1 raw data
ls -lh data/stage1/

# Inspect Parquet file (example)
duckdb -c "SELECT * FROM 'data/stage1/students/*.parquet' LIMIT 5"
```

---

## Launch Rill Dashboards

### Start Rill Developer Mode

```bash
rill start
```

**What happens:**
- Rill reads `rill.yaml` project configuration
- Connects to DuckDB at `./oss_framework/data/oea.duckdb`
- Compiles SQL models in `models/`
- Generates interactive dashboards from `dashboards/`
- Opens browser at **http://localhost:9009**

**Available dashboards:**
1. **Chronic Absenteeism Risk** - Student-level attendance patterns
2. **Equity Outcomes by Demographics** - Performance gaps by demographic groups

### Customize Port (Optional)

```bash
# Use different port
RILL_PORT=8080 rill start

# Or edit rill.yaml:
# server:
#   port: 8080
```

---

## Docker Deployment (Optional)

For containerized deployment with Rill + JupyterLab:

### Start Services

```bash
docker-compose up -d
```

**Services:**
- **Rill**: http://localhost:9009 (BI dashboards)
- **JupyterLab**: http://localhost:8888 (data exploration)

### Check Service Health

```bash
# View logs
docker-compose logs -f rill
docker-compose logs -f jupyter

# Check running containers
docker-compose ps
```

### Stop Services

```bash
docker-compose down
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `DuckDB database is locked` | Multiple processes accessing DuckDB | Close other DuckDB connections: `pkill -f duckdb` |
| `FileNotFoundError: data/stage1` | Missing data directories | Run: `mkdir -p data/stage1 data/stage2 data/stage3` |
| `Aeries API: 401 Unauthorized` | Invalid API key | Verify `AERIES_API_KEY` in `.env`, request new key from Aeries admin |
| `dbt command not found` | dbt not installed | Run: `pip install dbt-duckdb` |
| `rill: command not found` | Rill not installed | Run: `curl https://rill.sh \| sh` |
| `ModuleNotFoundError: dlt` | Python dependencies missing | Run: `pip install -e .` from project root |
| `Insufficient memory` | DuckDB memory limit too low | Increase `DUCKDB_MEMORY_LIMIT` in `.env` (e.g., `16GB`) |
| `Permission denied: oea.duckdb` | File permissions issue | Run: `chmod 644 oss_framework/data/oea.duckdb` |

### Diagnostic Commands

**Check environment:**
```bash
# Python version
python --version  # Should be 3.11+

# Installed packages
pip list | grep -E 'duckdb|dbt|dlt|rill'

# Environment variables loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DUCKDB_DATABASE_PATH'))"
```

**Check DuckDB database:**
```bash
# Database integrity
duckdb ./oss_framework/data/oea.duckdb -c "PRAGMA integrity_check"

# Database size
du -h ./oss_framework/data/oea.duckdb

# Loaded extensions
duckdb ./oss_framework/data/oea.duckdb -c "SELECT * FROM duckdb_extensions() WHERE loaded = true"
```

**Check disk space:**
```bash
df -h .
```

**Check logs:**
```bash
# Pipeline execution logs
tail -f oss_framework/logs/oea.log

# dbt logs
tail -f oss_framework/dbt/logs/dbt.log
```

---

## Next Steps

Once the pipeline is running successfully:

1. **Explore dashboards** - Open http://localhost:9009 and explore pre-built Rill dashboards
2. **Create custom dashboards** - See [RILL_GUIDE.md](RILL_GUIDE.md) for dashboard creation
3. **Understand architecture** - Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
4. **Schedule pipeline runs** - Set up cron jobs or Task Scheduler for automated daily/weekly runs
5. **Explore data in Jupyter** - Open http://localhost:8888 for notebook-based analysis

---

## Generating Test Data (Optional)

For development/testing without real Aeries data:

### Option 1: Delta Lake Test Data (500 students)

```bash
python src/ingestion/mock_data.py
```

Generates comprehensive test data with realistic patterns:
- 500 students across K-12 grades
- 50 staff members
- Complete courses, enrollment, grades, attendance
- Delta Lake format (Parquet + metadata)
- Output: `data/stage1/delta/`

### Option 2: Stage 1 Parquet Test Data (1,700 students)

```bash
python oss_framework/scripts/stage1_generate_sample_parquet.py
```

Generates larger test dataset matching production pipeline output:
- 1,700 students with demographic variety
- 45,000 attendance records
- 200,000 academic records (grades, course history)
- 2,000 discipline incidents
- 35,000 enrollment records
- Output: `data/stage1/` (ready for Stage 2 ingestion)

**After generating test data, run the pipeline:**

```bash
python scripts/run_pipeline.py
```

---

## Security Checklist

Before deploying to production:

- [ ] Generate strong `PRIVACY_SALT` (32+ bytes entropy)
- [ ] Set `.env` file permissions to `600` (owner read/write only)
- [ ] Enable audit logging (`AUDIT_LOGGING_ENABLED=true`)
- [ ] Review Aeries API key permissions (minimal required scopes)
- [ ] Configure firewall rules (block external access to ports 9009, 8888)
- [ ] Set up encrypted backups for DuckDB database
- [ ] Document data retention policy (`DATA_RETENTION_YEARS=5`)
- [ ] Review FERPA compliance settings in `SECURITY.md`

---

## Getting Help

- **Documentation**: [docs/](./), especially [ARCHITECTURE.md](ARCHITECTURE.md) and [RILL_GUIDE.md](RILL_GUIDE.md)
- **Rill Docs**: https://docs.rilldata.com
- **DuckDB Docs**: https://duckdb.org/docs/
- **dbt Docs**: https://docs.getdbt.com/docs/core/connect-data-platform/duckdb-setup
- **Issues**: https://github.com/flucido/local-data-stack/issues

---

## Quick Reference

**Full pipeline run:**
```bash
python scripts/run_pipeline.py
```

**Launch dashboards:**
```bash
rill start  # http://localhost:9009
```

**Query database:**
```bash
duckdb ./oss_framework/data/oea.duckdb
```

**Generate test data:**
```bash
python src/ingestion/mock_data.py
```

**Docker stack:**
```bash
docker-compose up -d   # Start services
docker-compose down    # Stop services
```
