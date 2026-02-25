# Migrating from Azure OEA to OSS Framework

## Overview

This guide helps you migrate from Microsoft's Azure-based Open Education Analytics (OEA) framework to the open-source OSS Framework. The migration preserves your data architecture while eliminating cloud costs and Azure dependencies.

## Migration Strategy Options

### Option A: Greenfield (Recommended for Small Districts)

**Best for**: Districts with <1TB data, starting fresh analytics

**Timeline**: 2-4 weeks

**Approach**: Deploy OSS Framework alongside Azure, migrate modules one-by-one

**Advantages**:
- Clean start with optimized architecture
- Parallel operation reduces risk
- Immediate cost savings after cutover

### Option B: In-Place Migration

**Best for**: Large districts with significant Azure investment

**Timeline**: 3-6 months

**Approach**: Export Azure data, rebuild pipelines in OSS Framework

**Advantages**:
- Preserve historical data
- Complete Azure exit
- Full migration validation

### Option C: Hybrid

**Best for**: Districts committed to cloud but want cost savings

**Timeline**: 1-2 months

**Approach**: Keep Azure storage, replace compute with OSS

**Advantages**:
- Lower migration risk
- Keep some Azure benefits
- Gradual transition

## Pre-Migration Checklist

- [ ] **Inventory Azure Resources**: List all Synapse objects, pipelines, notebooks
- [ ] **Document Data Sources**: API endpoints, credentials, refresh schedules
- [ ] **Export Current Data**: Download data lake contents to local storage
- [ ] **Map Dependencies**: Identify module interdependencies
- [ ] **Plan Downtime**: Schedule maintenance window for cutover
- [ ] **Backup Everything**: Full backup of Azure resources
- [ ] **Test OSS Environment**: Deploy and validate OSS Framework
- [ ] **Train Staff**: Ensure team familiarity with new stack

## Migration Steps

### Phase 1: Assessment (Week 1)

#### 1.1 Inventory Azure Resources

```bash
# Export Synapse workspace configuration
az synapse workspace show \
  --name your-workspace \
  --resource-group your-rg \
  --output json > azure_workspace.json

# List all pipelines
az synapse pipeline list \
  --workspace-name your-workspace \
  --output table

# List all notebooks
az synapse notebook list \
  --workspace-name your-workspace \
  --output table
```

#### 1.2 Document Data Lake Structure

```bash
# Download data lake structure (without data)
az storage blob directory list \
  --account-name yourstorageaccount \
  --container-name stage1 \
  --output table > stage1_structure.txt

az storage blob directory list \
  --account-name yourstorageaccount \
  --container-name stage2 \
  --output table > stage2_structure.txt

az storage blob directory list \
  --account-name yourstorageaccount \
  --container-name stage3 \
  --output table > stage3_structure.txt
```

#### 1.3 Calculate Costs

```bash
# Current Azure spend
az consumption usage list \
  --start-date 2025-12-01 \
  --end-date 2026-01-01 \
  --query "[?contains(instanceName, 'synapse') || contains(instanceName, 'storage')].{Service:meterCategory, Cost:pretaxCost}" \
  --output table
```

### Phase 2: Deploy OSS Framework (Week 2)

#### 2.1 Setup Infrastructure

Follow the [Setup Guide](../tech_docs/setup_guide.md) to deploy OSS Framework:

```bash
# Clone and setup
git clone https://github.com/flucido/openedDataEstate.git
cd openedDataEstate/oss_framework

# Install dependencies
pip install -r requirements.txt

# Start services
docker compose up -d

# Verify deployment
./verify_setup.sh
```

#### 2.2 Recreate Data Lake Structure

```bash
# Create Stage 1/2/3 directories matching Azure structure
python3 << EOF
import os
from pathlib import Path

# Read Azure structure exports
with open('stage1_structure.txt') as f:
    stage1_paths = f.readlines()

# Create local directories
for path in stage1_paths:
    path = path.strip()
    if path:
        local_path = Path('data/stage1') / path
        local_path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {local_path}")

# Repeat for stage2 and stage3
print("✓ Data lake structure recreated")
EOF
```

### Phase 3: Data Migration (Week 3)

#### 3.1 Export Data from Azure

```bash
# Download data from Azure Data Lake
# Option 1: Using AzCopy (fastest for large datasets)
azcopy copy \
  "https://yourstorageaccount.dfs.core.windows.net/stage2/*" \
  "data/stage2/" \
  --recursive \
  --check-length=false

# Option 2: Using Azure CLI (simpler, slower)
az storage blob download-batch \
  --account-name yourstorageaccount \
  --source stage2 \
  --destination data/stage2/ \
  --pattern "*"

# Verify download
find data/stage2 -name "*.parquet" | wc -l
```

#### 3.2 Convert Delta Lake (if needed)

Azure OEA uses Delta Lake format, which DuckDB supports natively. Verify compatibility:

```python
import duckdb

con = duckdb.connect(':memory:')
con.execute("INSTALL delta; LOAD delta")

# Test read
try:
    result = con.execute("""
        SELECT COUNT(*) FROM delta_scan('data/stage2/Refined/contoso/students')
    """).fetchone()
    print(f"✓ Successfully read {result[0]} rows from Delta table")
except Exception as e:
    print(f"✗ Error reading Delta: {e}")
    print("You may need to convert Delta to Parquet format")
```

**If conversion needed**:
```python
# Convert Delta to Parquet
import pyarrow.dataset as ds

# Read Delta
delta_ds = ds.dataset('data/stage2/Refined/contoso/students', format='delta')

# Write as Parquet
ds.write_dataset(
    delta_ds,
    'data/stage2/Refined/contoso/students_parquet',
    format='parquet',
    partitioning='hive'
)
```

### Phase 4: Pipeline Migration (Week 4)

#### 4.1 Convert Synapse Pipelines to dlt

**Azure Synapse Pipeline** (JSON):
```json
{
  "name": "Land_SIS_Data",
  "activities": [
    {
      "name": "Copy_Students",
      "type": "Copy",
      "inputs": [{"referenceName": "SIS_API"}],
      "outputs": [{"referenceName": "Stage1"}]
    }
  ]
}
```

**OSS Framework Pipeline** (Python + dlt):
```python
# scripts/ingest_sis.py
import dlt
import requests
from datetime import datetime

@dlt.source
def sis_source():
    @dlt.resource(write_disposition="append")
    def students():
        # Fetch from SIS API
        response = requests.get(
            "https://sis.example.com/api/students",
            headers={"Authorization": f"Bearer {os.getenv('SIS_API_KEY')}"}
        )
        return response.json()
    
    return students

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="sis_ingestion",
        destination="filesystem",
        dataset_name="stage1_sis"
    )
    
    load_info = pipeline.run(sis_source())
    print(f"✓ Loaded {load_info.metrics['rows']} rows")
```

#### 4.2 Convert Synapse Notebooks to dbt Models

**Azure Synapse Notebook** (Python):
```python
# Synapse notebook: Refine Students
from pyspark.sql.functions import col, sha2, concat, lit

# Read from Stage 1
df = spark.read.parquet("abfss://stage1@storage.dfs.core.windows.net/sis/students/")

# Pseudonymize PII
df_refined = df.withColumn(
    "student_id_hashed",
    sha2(concat(col("student_id"), lit(salt)), 256)
)

# Write to Stage 2
df_refined.write.mode("overwrite").parquet("abfss://stage2@storage.dfs.core.windows.net/sis/students/")
```

**OSS Framework dbt Model** (SQL):
```sql
-- dbt/models/stage2/sis_students_refined.sql
{{
  config(
    materialized='incremental',
    unique_key='student_id_hashed'
  )
}}

WITH source AS (
    SELECT * FROM read_parquet('{{ var("stage1_path") }}/sis/students/**/*.parquet')
),

refined AS (
    SELECT
        {{ pseudonymize('student_id') }} AS student_id_hashed,
        first_name,
        last_name,
        grade_level,
        school_name,
        enrollment_status,
        enrollment_date,
        CURRENT_TIMESTAMP AS _refined_at
    FROM source
)

SELECT * FROM refined

{% if is_incremental() %}
WHERE _refined_at > (SELECT MAX(_refined_at) FROM {{ this }})
{% endif %}
```

#### 4.3 Convert Pipeline Schedules

**Azure Synapse Trigger** (JSON):
```json
{
  "name": "Daily_Ingest_Trigger",
  "type": "ScheduleTrigger",
  "recurrence": {
    "frequency": "Day",
    "interval": 1,
    "startTime": "2026-01-01T02:00:00Z"
  }
}
```

**OSS Framework Schedule** (Dagster):
```python
# scripts/dagster/schedules.py
from dagster import schedule, RunRequest
from datetime import datetime

@schedule(
    cron_schedule="0 2 * * *",  # Daily at 2 AM
    job_name="sis_ingestion_job"
)
def daily_sis_schedule(context):
    return RunRequest(
        run_key=f"sis_ingest_{datetime.now().strftime('%Y%m%d')}",
        tags={"source": "sis", "frequency": "daily"}
    )
```

### Phase 5: Visualization Migration (Week 5)

#### 5.1 Export Power BI Reports

1. Open Power BI Desktop
2. File → Export → Export as PDF (for reference)
3. Document all queries:
   - Right-click each visual → Edit query
   - Copy SQL to text file

#### 5.2 Recreate Dashboards in Metabase

```sql
-- Example: Student Enrollment Report (Power BI)
SELECT 
    school_year,
    grade_level,
    COUNT(DISTINCT student_id) as enrollment_count
FROM students
WHERE enrollment_status = 'Active'
GROUP BY school_year, grade_level
ORDER BY school_year DESC, grade_level

-- Same query works in Metabase with DuckDB!
```

**Metabase Dashboard Creation**:
1. Navigate to http://localhost:3000
2. New → Question → Native Query
3. Paste SQL query
4. Visualize (choose chart type)
5. Save to dashboard

### Phase 6: Testing & Validation (Week 6)

#### 6.1 Data Quality Checks

```python
# Validation script: compare Azure vs OSS results
import duckdb
import pyodbc

# Connect to Azure SQL Serverless
azure_conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=your-workspace.sql.azuresynapse.net;'
    'DATABASE=your_db;'
    'UID=your_user;PWD=your_password'
)

# Connect to DuckDB
oss_conn = duckdb.connect('data/oea.duckdb')

# Compare row counts
azure_cursor = azure_conn.cursor()
azure_cursor.execute("SELECT COUNT(*) FROM students")
azure_count = azure_cursor.fetchone()[0]

oss_count = oss_conn.execute("""
    SELECT COUNT(*) FROM delta_scan('data/stage2/refined/sis/students')
""").fetchone()[0]

print(f"Azure: {azure_count} rows")
print(f"OSS: {oss_count} rows")
print(f"Match: {azure_count == oss_count}")

# Compare aggregations
azure_cursor.execute("""
    SELECT grade_level, COUNT(*) as cnt 
    FROM students 
    GROUP BY grade_level 
    ORDER BY grade_level
""")
azure_agg = azure_cursor.fetchall()

oss_agg = oss_conn.execute("""
    SELECT grade_level, COUNT(*) as cnt
    FROM delta_scan('data/stage2/refined/sis/students')
    GROUP BY grade_level
    ORDER BY grade_level
""").fetchall()

print("\nAggregation comparison:")
for az, oss in zip(azure_agg, oss_agg):
    match = "✓" if az == oss else "✗"
    print(f"{match} Grade {az[0]}: Azure={az[1]}, OSS={oss[1]}")
```

#### 6.2 Performance Benchmarks

```python
import time

# Benchmark query performance
queries = [
    "SELECT COUNT(*) FROM students",
    "SELECT grade_level, AVG(gpa) FROM students GROUP BY grade_level",
    "SELECT * FROM students WHERE enrollment_status = 'Active'"
]

for query in queries:
    # Azure timing
    start = time.time()
    azure_cursor.execute(query)
    azure_cursor.fetchall()
    azure_time = time.time() - start
    
    # OSS timing
    start = time.time()
    oss_conn.execute(query.replace('students', "delta_scan('data/stage2/refined/sis/students')")).fetchall()
    oss_time = time.time() - start
    
    print(f"\nQuery: {query[:50]}...")
    print(f"  Azure: {azure_time:.2f}s")
    print(f"  OSS: {oss_time:.2f}s")
    print(f"  Speedup: {azure_time/oss_time:.1f}x")
```

### Phase 7: Cutover (Week 7)

#### 7.1 Parallel Operation

Run both systems for 1-2 weeks:
```bash
# Daily validation script
#!/bin/bash
DATE=$(date +%Y-%m-%d)

echo "=== Daily Validation: $DATE ==="

# Run OSS ingestion
python scripts/ingest_sis.py

# Run OSS transformations
cd dbt && dbt build && cd ..

# Compare results
python scripts/validate_against_azure.py

# Send report
python scripts/send_validation_report.py
```

#### 7.2 Final Cutover

```bash
# Stop Azure pipelines
az synapse trigger stop \
  --name Daily_Ingest_Trigger \
  --workspace-name your-workspace

# Verify OSS is stable
./verify_setup.sh
docker compose ps

# Update DNS/URLs
# Point dashboards to OSS Framework

# Monitor for 24 hours
# Check Dagster runs, Metabase queries

# If stable, proceed to decommission Azure
```

#### 7.3 Decommission Azure

**⚠️ WARNING: Do not delete Azure resources until OSS is fully validated!**

```bash
# Recommended: Keep Azure for 30 days as backup
# After 30 days of successful OSS operation:

# Stop Synapse workspace
az synapse workspace stop \
  --name your-workspace \
  --resource-group your-rg

# Delete Synapse workspace (final)
az synapse workspace delete \
  --name your-workspace \
  --resource-group your-rg \
  --yes

# Keep storage account for additional 30 days
# Final cleanup after 60 days total
az storage account delete \
  --name yourstorageaccount \
  --resource-group your-rg \
  --yes
```

## Cost Savings Realization

### Before Migration (Azure)
| Service | Monthly Cost |
|---------|--------------|
| Synapse Analytics | $3,000 |
| Data Lake Storage | $200 |
| Key Vault | $50 |
| Application Insights | $100 |
| **Total** | **$3,350/month** |

### After Migration (OSS)
| Item | Monthly Cost |
|------|--------------|
| Server (self-hosted) | $0 (existing) |
| Electricity (~300W server) | $50 |
| **Total** | **$50/month** |

**Savings**: $3,300/month = $39,600/year

## Rollback Plan

If issues arise during cutover:

### Quick Rollback (within 24 hours)

```bash
# Re-enable Azure pipelines
az synapse trigger start \
  --name Daily_Ingest_Trigger \
  --workspace-name your-workspace

# Point dashboards back to Azure
# Update DNS/URLs

# Keep OSS running for troubleshooting
```

### Full Rollback (after 1 week)

1. Restore Azure workspace from backup
2. Re-sync any data added during OSS-only period
3. Validate Azure pipelines
4. Decommission OSS Framework
5. Document lessons learned

## Common Migration Challenges

### Challenge 1: Synapse-Specific Functions

**Problem**: Synapse SQL functions not available in DuckDB

**Solution**: Map to DuckDB equivalents

| Synapse | DuckDB |
|---------|--------|
| `GETDATE()` | `CURRENT_TIMESTAMP` |
| `ISNULL(col, val)` | `COALESCE(col, val)` |
| `CONVERT(type, col)` | `CAST(col AS type)` |

### Challenge 2: Performance Differences

**Problem**: Some queries slower in DuckDB

**Solution**: Optimize queries and use DuckDB-specific features

```sql
-- Slow: Full table scan
SELECT * FROM large_table WHERE condition

-- Fast: Partition pruning
SELECT * FROM read_parquet('data/**/*.parquet', hive_partitioning=true)
WHERE date_partition = '2026-01'
  AND condition
```

### Challenge 3: User Resistance

**Problem**: Users prefer Power BI over Metabase

**Solution**: 
- Recreate favorite dashboards first
- Provide training sessions
- Highlight cost savings to leadership
- Consider keeping Power BI Desktop (free) for advanced users

### Challenge 4: Missing Enterprise Features

**Problem**: No Azure AD integration

**Solution**: 
- Use Metabase's built-in authentication
- Integrate with LDAP/SSO if needed
- Implement file-system permissions for data access

## Post-Migration Optimization

### Week 8-12: Optimization Phase

1. **Query Performance Tuning**:
```python
# Enable query profiling
con.execute("SET enable_profiling='query_tree'")

# Analyze slow queries
profile = con.execute("SELECT * FROM duckdb_query_profile()").fetchdf()

# Optimize based on findings
```

2. **Storage Optimization**:
```bash
# Compact Parquet files
python scripts/optimize_parquet.py

# Remove old data
find data/stage1 -mtime +90 -delete
```

3. **Monitoring Setup**:
```bash
# Deploy Prometheus + Grafana
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3002:3000 grafana/grafana

# Configure Dagster metrics export
```

## Success Metrics

Track these KPIs post-migration:

- [ ] **Cost Savings**: $X/month reduction
- [ ] **Query Performance**: X% faster average query time
- [ ] **Data Freshness**: <24hr latency maintained
- [ ] **User Adoption**: X% of users active on Metabase
- [ ] **Reliability**: >99% uptime
- [ ] **Staff Efficiency**: Reduced time spent on maintenance

## Next Steps

1. **Continuous Improvement**: [Deployment Guide](../developer/deployment_guide.md)
2. **Advanced Features**: [dbt Guide](../tech_docs/dbt_guide.md)
3. **Scaling Strategy**: [Architecture](../tech_docs/architecture.md)

## Support

- **Migration Issues**: [GitHub Issues](https://github.com/flucido/openedDataEstate/issues)
- **Community**: [Discussions](https://github.com/flucido/openedDataEstate/discussions)
