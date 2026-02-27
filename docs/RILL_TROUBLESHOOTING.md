# Rill Troubleshooting Guide

Quick diagnostics and solutions for common Rill issues.

---

## Quick Diagnostics

### Health Check Commands

```bash
# Check Rill version
rill version

# Verify project structure (must run from rill_project/)
cd rill_project && rill start --no-open

# Validate all YAML configurations
cd rill_project && rill project validate

# Start with verbose logging
cd rill_project && rill start --log-level debug

# Check for port conflicts (default: 9009)
lsof -i :9009
```

---

## Common Errors

### 1. Parser Errors (v0.82.1 Schema Changes)

**Symptom:**
```
Parser error: field description not found in type parser.AlertYAML
Parser error: field webhook_url not found in type parser.NotifySpec
```

**Cause:** Alert YAML files using deprecated v0.81.4 schema

**Solution:**
```yaml
# ❌ OLD (v0.81.4 - BROKEN in v0.82.1)
type: alert
description: "Monitor pipeline health"  # ❌ Not supported
webhook_url: "https://hooks.slack.com/..."  # ❌ Changed to array

# ✅ NEW (v0.82.1 - WORKING)
type: alert
# NO description field at root level
display_name: "Pipeline Health"
notify:
  webhooks:  # Array format
    - url: "https://hooks.slack.com/..."
```

**Reference:** See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md#rill-alert-schema-changes-v0821---resolved-) for full details

---

### 2. Working Directory Path Resolution Errors

**Symptom:**
```
Failed to connect to DuckDB: file not found
Dashboard won't load: reconciliation error
```

**Cause:** Starting Rill from wrong directory - all paths are resolved relative to `rill start` location

**Solution:**

✅ **Correct - Start from rill_project/ directory:**
```bash
cd rill_project/
rill start
# Connector DSN ./oss_framework/data/oea.duckdb resolves correctly
```

❌ **Incorrect - Starting from repo root:**
```bash
# From repository root
rill start rill_project/  # Working directory is still repo root!
# Connector DSN path will fail to resolve
```

**Why it matters:**
- Connector DSN paths are relative to working directory
- Dashboard/model references resolve from working directory
- Rill caches build artifacts in `{working_dir}/.rill/`

**Reference:** See [RILL_GUIDE.md](./RILL_GUIDE.md#rill-working-directory-requirements)

---

### 3. Dashboard Reconciliation Failures

**Symptom:**
```
2026-02-26T16:38:15.588 INFO Reconciling resource name=wellbeing_risk_profiles type=Explore
ERROR Failed to reconcile resource name=wellbeing_risk_profiles
```

**Common Causes & Solutions:**

#### Cause A: Missing Parquet Data Files
```bash
# Check if Parquet files exist
ls -lh rill_project/data/

# Re-export analytics views to Parquet
python3 scripts/export_to_rill.py

# Verify export succeeded
ls -lh rill_project/data/*.parquet
```

#### Cause B: Invalid SQL Model References
```bash
# Check model SQL syntax
cd rill_project
cat models/wellbeing_risk_profiles.yaml

# Verify DuckDB connector is working
# Model should reference: read_parquet('../data/wellbeing_risk_profiles.parquet')
```

#### Cause C: DuckDB Connection Failures
```bash
# Check if DuckDB file exists
ls -lh oss_framework/data/oea.duckdb

# Verify connector configuration
cat rill_project/connectors/duckdb.yaml

# Test connection manually
duckdb oss_framework/data/oea.duckdb "SELECT 1"
```

---

### 4. SQL Comment Syntax Errors (Historical - v0.81.4)

**Symptom:**
```
Parser error: syntax error at or near "#"
```

**Cause:** Model files using `#` for comments instead of SQL `--` comments

**Solution:**
```sql
-- ❌ Wrong (Python-style comments)
# This is a comment

-- ✅ Correct (SQL comments)
-- This is a comment
```

**Reference:** See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md#sql-comment-syntax-in-model-files)

---

### 5. Unsupported Dashboard Fields (Historical - v0.81.4)

**Symptom:**
```
Parser error: field default_sort not found in type parser.MetricsViewYAML
```

**Cause:** Dashboard YAML using fields not supported in current Rill version

**Solution:**
```yaml
# Remove unsupported fields from dashboard YAML
# Check official docs for current schema: https://docs.rilldata.com/reference/project-files/dashboards

# Common unsupported fields (v0.81.4):
# - default_sort
# - default_filter
# Legacy fields from older Rill versions
```

---

## Performance Issues

### Dashboard Loading Slow (>5 seconds)

**Solutions:**

#### 1. Limit Default Time Range
```yaml
# In dashboard YAML
defaults:
  time_range: P30D  # Last 30 days instead of all time
```

#### 2. Pre-aggregate Data in dbt
```sql
-- In dbt model, aggregate before export
SELECT
    date_trunc('week', date) as week,
    school_id,
    COUNT(*) as student_count,
    AVG(attendance_rate) as avg_attendance
FROM detailed_attendance
GROUP BY 1, 2
```

#### 3. Use Partitioned Parquet Files
```python
# In export_to_rill.py - already implemented for 3 datasets
# Partitioning provides 40-60% query speedup
partition_cols = ["school_id"]  # Low cardinality, common filter
```

**Reference:** Partitioned datasets:
- `chronic_absenteeism_risk.parquet/` (partitioned by school_id)
- `class_effectiveness.parquet/` (partitioned by school_id)
- `wellbeing_risk_profiles.parquet/` (partitioned by school_id)

---

### Query Timeout Errors

**Symptom:**
```
Query timeout after 30s
```

**Solutions:**

#### 1. Increase Query Timeout in Alert Configuration
```yaml
# In alert YAML
timeout: "60s"  # Increase from default 30s
```

#### 2. Optimize DuckDB Queries
```sql
-- Add WHERE clauses to reduce data scanned
SELECT * FROM read_parquet('data/*.parquet')
WHERE school_id = 'SCH1'  -- Partition filter (fast with partitioned data)
  AND date >= CURRENT_DATE - INTERVAL '30 days'
```

#### 3. Check DuckDB Database Lock
```bash
# Kill any stale DuckDB connections
pkill -f "rill start|rill" || true

# Restart Rill
cd rill_project && rill start
```

---

## Port Conflicts

**Symptom:**
```
Failed to start server on port 9009: address already in use
```

**Solution:**

#### Option A: Kill Existing Rill Process
```bash
# Find process using port 9009
lsof -i :9009

# Kill the process
kill -9 <PID>

# Restart Rill
cd rill_project && rill start
```

#### Option B: Use Different Port
```bash
cd rill_project && rill start --port 8080
# Open http://localhost:8080
```

#### Option C: Set Port via Environment Variable
```bash
export RILL_PORT=8080
cd rill_project && rill start
```

---

## Data Freshness Issues

**Symptom:** Dashboards showing stale data

**Solutions:**

#### 1. Re-export Parquet Files
```bash
# Full pipeline refresh
cd oss_framework/dbt && dbt build

# Export analytics views to Parquet
python3 scripts/export_to_rill.py

# Rill auto-refreshes when Parquet files change
```

#### 2. Check Last Export Timestamp
```bash
# Check Parquet file modification time
ls -lht rill_project/data/*.parquet | head -5

# Compare to DuckDB view freshness
duckdb oss_framework/data/oea.duckdb <<SQL
SELECT 
  'chronic_absenteeism_risk' AS view_name,
  MAX(_loaded_at) AS last_update
FROM main_analytics.v_chronic_absenteeism_risk;
SQL
```

#### 3. Verify Data Freshness Alert
```bash
# Check alert configuration
cat rill_project/alerts/data_freshness_alert.yaml

# Alert should trigger if data older than threshold:
# - fct_attendance_daily: 2 days
# - fct_student_grades: 7 days
# - dim_students: 30 days
```

---

## Configuration Validation

### Validate All YAML Files

```bash
cd rill_project

# Validate entire project (all YAML configs)
rill project validate

# Check for parser errors in specific files
rill start --no-open --log-level debug
```

### Common Validation Errors

#### 1. Invalid YAML Syntax
```bash
# Check YAML syntax
yamllint rill_project/dashboards/*.yaml
yamllint rill_project/models/*.yaml
yamllint rill_project/alerts/*.yaml
```

#### 2. Missing Required Fields
```yaml
# All dashboards must have:
type: metrics_view
table: model_name  # Reference to model
measures: [...]    # At least one measure
dimensions: [...]  # At least one dimension

# All alerts must have:
type: alert
display_name: "Alert Name"
data: ...  # Query or resource_status
notify: ...  # At least one notification channel
```

---

## Logging and Debugging

### Enable Debug Logging

```bash
# Start Rill with debug logs
cd rill_project && rill start --log-level debug

# Output shows:
# - SQL queries executed
# - Reconciliation steps
# - Resource dependencies
# - Error stack traces
```

### Check Rill Logs

```bash
# Logs are output to terminal where `rill start` was executed
# Look for lines containing:
# - "ERROR" or "WARN" for issues
# - "Reconciling resource" for dashboard loading
# - "Reconciled resource" for successful loads
```

### Example Debug Output

```
2026-02-26T16:38:15.588 INFO Reconciling resource name=wellbeing_risk_profiles type=Explore
2026-02-26T16:38:15.588 DEBUG Executing SQL: SELECT * FROM read_parquet('../data/wellbeing_risk_profiles.parquet')
2026-02-26T16:38:15.731 INFO Reconciled resource name=wellbeing_risk_profiles type=Explore
```

---

## Getting Help

### Official Resources

- **Rill Documentation**: https://docs.rilldata.com
- **Rill GitHub**: https://github.com/rilldata/rill
- **Rill Examples**: https://github.com/rilldata/rill-examples
- **Rill Discord**: https://discord.gg/DJ5qcsxE2m

### Project-Specific Resources

- **RILL_GUIDE.md**: Complete guide to creating dashboards
- **KNOWN_ISSUES.md**: Historical issues and resolutions
- **DASHBOARD_GUIDE.md**: Dashboard usage and best practices
- **test_rill_integration.py**: Test suite validating all 5 dashboards

---

## Emergency Recovery

### Complete Rill Reset

If all else fails, clean slate:

```bash
# 1. Stop Rill
pkill -f "rill start|rill" || true

# 2. Remove Rill cache
rm -rf rill_project/.rill/

# 3. Re-export Parquet data
cd oss_framework/dbt && dbt build
python3 scripts/export_to_rill.py

# 4. Restart Rill
cd rill_project && rill start

# 5. Verify all dashboards load
# Open http://localhost:9009 and check each dashboard
```

### Verify System After Reset

```bash
# Run integration tests
python3 test_rill_integration.py

# Expected output: 21/21 tests PASSED
```
