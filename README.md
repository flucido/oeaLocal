# local-data-stack

`local-data-stack` is an open-source, local-first analytics framework for education data. It combines Python orchestration, DuckDB, Delta/Parquet staging, dbt transformations, and Rill dashboards so contributors can explore the architecture without depending on cloud services or private student records.

## Public release guarantees

- The intended `public-release` state is a clean-slate public snapshot with no private student records, local databases, or real credentials committed.
- `oss_framework/data/` contains only empty placeholders plus a 5-row synthetic Parquet sample for schema exploration.
- dbt and Rill resolve DuckDB paths from environment variables instead of hardcoded workstation paths.
- The repository excludes local Parquet, DuckDB, and `.env` files by default.

## Repository layout

```text
local-data-stack/
├── .env.example                  # Safe configuration template
├── oss_framework/
│   ├── data/
│   │   ├── sample_data/          # Synthetic 5-row Parquet sample
│   │   ├── stage1/.gitkeep
│   │   ├── stage2/.gitkeep
│   │   └── stage3/.gitkeep
│   ├── dbt/                      # DuckDB dbt project
│   ├── pipelines/                # Ingestion pipeline definitions
│   ├── scripts/                  # Orchestration helpers
│   └── tests/                    # Python tests
├── rill_project/                 # Rill dashboards and connector config
├── scripts/                      # Root orchestration entrypoints
└── src/                          # Supporting Python modules
```

## Architecture overview

```text
Aeries API / CSV exports
         ↓
Stage 1: Delta/Parquet landing zone (oss_framework/data/stage1)
         ↓
Stage 2: DuckDB + dbt transformations (oss_framework/data/oea.duckdb)
         ↓
Stage 3: Analytics marts / exported dashboard inputs
         ↓
Rill dashboards (rill_project/)
```

The committed sample data is synthetic and anonymized. It is present only to demonstrate expected column names and lightweight local testing patterns.

## Quick start

### 1. Install Python dependencies

```bash
pip install -e '.[dev]'
```

### 2. Create your local environment file

```bash
cp .env.example .env
# edit .env with your own Aeries credentials or local source settings
```

### 3. Prepare empty local storage

The repository already includes placeholder directories under `oss_framework/data/`. Your local DuckDB database will be created on demand at the path defined by `DUCKDB_DATABASE_PATH`.

### 4. Run dbt against DuckDB

```bash
cd oss_framework/dbt
dbt deps
DBT_PROFILES_DIR=. dbt parse
DBT_PROFILES_DIR=. dbt build
```

### 5. Launch Rill

```bash
cd rill_project
rill start
```

If you keep the default `.env.example` paths, Rill will open the DuckDB file at `../oss_framework/data/oea.duckdb`.

## Synthetic sample data

A sample file is included at `oss_framework/data/sample_data/synthetic_student_metrics.parquet`.

It contains 5 anonymized rows with columns commonly used by downstream modeling and dashboard examples:

- `student_id`
- `student_alias`
- `academic_year`
- `school_id`
- `grade_level`
- `race_ethnicity`
- `ell_status`
- `special_education_status`
- `frl_status`
- `attendance_rate`
- `gpa`
- `discipline_incidents`

## Validation commands

```bash
python -m pytest oss_framework/tests/test_public_release_sanitization.py -q --no-cov
python scripts/contracts/contract_tests.py
python -m ruff check oss_framework
python -m black --check oss_framework
```

The full repository suite still has pre-existing issues unrelated to the public-release sanitization work, so the focused release test above is the canonical safeguard added in this change.

## Fork the public-release branch into a new repository

If you want to spin `copilot/public-release` into its own project, use the export helper below. It validates the sanitized snapshot, copies only tracked files from that branch, and creates a brand-new git history in the target directory so the new repo does not inherit the private repository history.

```bash
python scripts/fork_public_release.py \
  --source-branch copilot/public-release \
  --target-dir /path/to/local-data-stack \
  --remote-url https://github.com/<owner>/local-data-stack.git
```

After the script finishes, push the new repository with:

```bash
cd /path/to/local-data-stack
git push -u origin main
```

## License

- Code: [MIT License](LICENSE)
- Documentation: [CC BY 4.0](LICENSE)
