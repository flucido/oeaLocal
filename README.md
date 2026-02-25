# local-data-stack

100% local education analytics platform with DuckDB, dbt, and Rill. No cloud dependencies.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-available-brightgreen.svg)](docs/README.md)

## Why this project exists

`local-data-stack` provides a complete local analytics stack:

- **Data ingestion** from Aeries API and Excel imports
- **DuckDB + Delta/Parquet** lakehouse storage (all local)
- **dbt transformations** for data modeling
- **Rill dashboards** for BI and analytics
- **Simple orchestration** with Python scripts (no Dagster)

## Repository layout

```text
local-data-stack/
-- oss_framework/               # Core pipelines and transformations
-- src/                         # Database connection utilities
-- rill.yaml                    # Rill project configuration
-- connectors/                  # Rill connector configs
-- models/                      # Rill SQL models
-- metrics/                     # Rill dashboard definitions
-- scripts/                     # Orchestration scripts
-- data/                        # Local data storage (stage1, stage2, stage3)
-- README.md                    # Project overview (this file)

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
python scripts/run_pipeline.py
```

### 6) Start Rill Developer

```bash
rill start
# Opens http://localhost:9009
```

## Core docs

- **Setup guide:** [docs/SETUP.md](docs/SETUP.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Rill guide:** [docs/RILL_GUIDE.md](docs/RILL_GUIDE.md)

## Forked from openedDataEstate

This project is a local-only fork of [openedDataEstate](https://github.com/flucido/openedDataEstate), removing all cloud dependencies (MotherDuck, AWS S3) and replacing Metabase with Rill.

## License

- **Code:** [MIT License](LICENSE)
- **Documentation:** [Creative Commons Attribution 4.0](LICENSE)
