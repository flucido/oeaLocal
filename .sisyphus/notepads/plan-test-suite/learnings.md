# Rill Testing & Validation Research - Feb 26, 2026

## EXECUTIVE SUMMARY

Rill provides a comprehensive testing and validation framework with three primary layers:
1. **Data Quality Tests** - Model-level validation that runs during refresh
2. **Alerts** - Scheduled monitoring for data freshness, thresholds, and resource status
3. **CLI Validation** - Project-wide validation for CI/CD integration

**Key Finding:** Use tests for Rill-managed models, alerts for live connectors (ClickHouse, Druid, etc.)

---

## OFFICIAL DOCUMENTATION SOURCES

### Primary Rill Docs (https://docs.rilldata.com)
- **Data Quality Tests**: https://docs.rilldata.com/developers/build/models/data-quality-tests
- **Alert Configuration**: https://docs.rilldata.com/reference/project-files/alerts  
- **CLI Validation**: https://docs.rilldata.com/reference/cli/validate
- **Debugging Guide**: https://docs.rilldata.com/developers/build/debugging
- **Main Quickstart**: https://docs.rilldata.com/developers/get-started/quickstart

### Example Repository
- **GitHub**: https://github.com/rilldata/rill-examples
- Contains: app-engagement, cost-monitoring, github-analytics, openrtb-prog-ads projects
- Each has working alert.yaml examples

---

## 1. DATA QUALITY TESTS (Model-Level Testing)

### When to Use
✅ **Use for models Rill manages** (SQL models, incremental models, partitioned models)
❌ **Use alerts instead** for live connectors (ClickHouse, Druid, Pinot, StarRocks)

### Test Syntax Options

#### Option A: Assert Tests (Row-Level Conditions)
```yaml
type: model
sql: SELECT * FROM my_source
tests:
  - name: No Null Campaign ID
    assert: campaign_id IS NOT NULL
  
  - name: Valid Bid Price
    assert: bid_price >= 0 AND bid_price <= 100
  
  - name: Valid Status Values
    assert: status IN ('active', 'paused', 'completed', 'draft')
```

**How Assert Works:**
- You write: `assert: value > 0`
- Rill converts to: `SELECT * FROM model WHERE NOT (value > 0)`
- **Test passes** if no rows returned (all rows satisfy condition)
- **Test fails** if any rows returned (violations found)

#### Option B: SQL Tests (Explicit Failure Queries)
```yaml
tests:
  # Row count validation
  - name: Minimum Impression Count
    sql: SELECT 'Too few impressions' WHERE (SELECT COUNT(*) FROM model) < 1000
  
  # Duplicate detection
  - name: No Duplicate Impression IDs
    sql: |
      SELECT impression_id, COUNT(*) as count
      FROM model
      GROUP BY impression_id
      HAVING COUNT(*) > 1
  
  # Referential integrity
  - name: Valid Campaign References
    sql: |
      SELECT i.campaign_id
      FROM model i
      LEFT JOIN campaigns c ON i.campaign_id = c.id
      WHERE c.id IS NULL
```

**How SQL Works:**
- You query for rows representing failures
- **Test passes** if query returns zero rows
- **Test fails** if query returns any rows

### Choosing Between Assert vs SQL

| Use Assert When | Use SQL When |
|----------------|--------------|
| Testing row-level conditions | Testing aggregate values (COUNT, SUM, AVG) |
| Simple constraints | Relationships between tables |
| Want Rill to handle NOT logic | Complex validation logic |
| Straightforward checks | Need custom error messages |

### Test Execution Behavior

1. Tests run **after** model refresh succeeds
2. **Model remains queryable** even if tests fail
3. All tests run independently (one failure ≠ stop others)
4. Results stored in model state, visible via:
   - Rill logs
   - Runtime API (`test_errors` field)
   - `rill project logs` (Cloud)

### Testing Strategy (Start → Add → Monitor)

**Critical Validations (Start Here):**
1. Null checks on required fields
2. Uniqueness constraints (primary keys)
3. Referential integrity
4. Range validations

**Domain-Specific (Add Later):**
1. Business rules
2. Data completeness
3. Custom validation logic

**Monitor & Iterate:**
1. Review failures regularly
2. Add tests when issues discovered
3. Remove/update obsolete tests

---

## 2. ALERTS (Scheduled Monitoring)

### Alert Use Cases
- **Data lag detection** (e.g., data older than 1 day)
- **Threshold monitoring** (e.g., CTR out of expected range)
- **Resource status checks** (model reconciliation failures)
- **Live connector data quality** (since tests don't work for live data)

### Alert YAML Structure

```yaml
type: alert
display_name: Data lags by more than 1 day

# Check every hour
refresh:
  cron: 0 * * * *
  time_zone: 'America/Los_Angeles'  # Optional
  run_in_dev: false  # Don't run in dev mode

# Query returns rows if problem detected
data:
  sql: |-
    SELECT *
    FROM (
      SELECT MAX(event_time) AS max_time
      FROM rill_metrics_model
    )
    WHERE max_time < NOW() - INTERVAL '1 day'

# Notification configuration
notify:
  email:
    recipients:
      - data-team@company.com
  slack:
    channels:
      - '#rill-cloud-alerts'
    webhooks:
      - https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Advanced options
on_recover: false  # Send alert when recovers (default: false)
on_fail: true      # Send alert on failure (default: true)
on_error: false    # Send alert on error (default: false)
renotify: false    # Repeat notifications (default: false)
renotify_after: '24h'  # Re-notify interval (snooze duration)
```

### Alert Data Resolvers (6 Options)

**1. Raw SQL Query**
```yaml
data:
  sql: SELECT * FROM model WHERE issue_detected
  connector: duckdb  # Optional
```

**2. Metrics SQL (queries metrics view)**
```yaml
data:
  metrics_sql: |
    SELECT measure_value 
    FROM metrics_view 
    WHERE measure_value > threshold
```

**3. Custom API**
```yaml
data:
  api: my_custom_api
  args:
    param1: value1
```

**4. File Glob Pattern**
```yaml
data:
  glob: "data/*.parquet"
  connector: gcs
```

**5. Resource Status**
```yaml
data:
  resource_status:
    where_error: true  # Trigger when resource errors
```

**6. AI Insights (reports only)**
```yaml
data:
  ai:
    prompt: "Analyze recent trends and flag anomalies"
    time_range:
      iso_duration: P7D  # Last 7 days
```

### Real-World Alert Examples (from rill-examples repo)

All example projects use identical alert pattern:
```yaml
# From rill-cost-monitoring/alerts/alert.yaml
type: alert
display_name: Project Resource Status Check

refresh:
  cron: 0 * * * *  # Every hour

data:
  resource_status:
    where_error: true

notify:
  email:
    recipients:
      - team@example.com
```

This checks if any project resource (model, source, connector) enters error state.

---

## 3. CLI VALIDATION TOOLS

### `rill validate` Command

**Purpose:** Validate project resources without full deployment

```bash
# Validate current project
rill validate

# Validate specific path
rill validate /path/to/project

# Output to JSON for CI/CD
rill validate -o validation-results.json

# Use custom environment
rill validate --environment prod

# Reset and re-ingest sources
rill validate --reset

# Increase verbosity
rill validate --verbose

# Collect debug info
rill validate --debug
```

**Flags:**
- `-e, --env`: Set environment variables
- `--reset`: Clear and re-ingest source data
- `--environment`: Env name (default: "dev")
- `--verbose`: Debug-level logs
- `--debug`: Collect additional debug info
- `-o, --output-file`: JSON output file
- `--model-timeout-seconds`: Reconciliation timeout (default: 60)

**CI/CD Integration Pattern:**
```bash
# In GitHub Actions / GitLab CI
rill validate --environment prod -o validation.json
if [ $? -ne 0 ]; then
  echo "Validation failed"
  cat validation.json
  exit 1
fi
```

---

## 4. DEBUGGING & TROUBLESHOOTING

### Log Analysis

**Log Format (JSON structured)**
```json
{
  "name": "commits_explore",
  "type": "Explore", 
  "elapsed": "1ms",
  "error": "optional error message",
  "dependency_error": false,
  "trace_id": "3073a89ac5cee9e7",
  "span_id": "c3cb402d7b4af9b6"
}
```

**Key Fields:**
- `name`: Resource filename or YAML name
- `type`: Connector, Model, MetricsView, Explore, Alert, etc.
- `elapsed`: Processing time
- `error`: Error message (if failed)
- `dependency_error`: true = failed due to upstream resource
- `trace_id` / `span_id`: For distributed tracing

### Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| `Failed to connect to ...` | Connector credentials | Check credentials, firewall settings |
| `Table with name ... does not exist` | Missing table | Verify with `rill query --sql "select * from table limit 1"` |
| `IO Error: No files found...` | Wrong path | Check cloud storage path and file existence |
| `some partitions have errors` | Partition ingestion failure | Run `rill project refresh --model {model} --errored-partitions` |
| `Out of Memory Error` | Memory exhaustion | Contact Rill support |
| `dependency error: resource "X"...` | Upstream failure | Fix the upstream resource first |

### Debug Workflow

**Step 1: Check Project Logs**
```bash
# Local development
rill start --verbose --debug

# Deployed projects
rill project logs <project-name>
rill project logs <project-name> --follow  # Like tail -f
rill project logs <project-name> --tail 100
rill project logs <project-name> --level DEBUG
```

**Step 2: Check Resource Status**
```bash
# Cloud projects
rill project status <project-name>

# Local projects
rill project status --local
```

Shows:
- Resource reconciliation status
- Error states per resource
- Dependency relationships
- Overall project health

**Step 3: Use Trace Viewer (Advanced)**
```bash
rill start --debug
# Then access Trace Viewer in UI
```

Visualizes:
- Resource dependency chains
- Reconciliation bottlenecks
- Execution flows
- Cascading failures

**Step 4: Targeted Refresh**
```bash
# Refresh specific model
rill project refresh --model model_name

# Refresh only errored partitions
rill project refresh --model model_name --errored-partitions

# Reset and re-ingest
rill start --reset
```

### Log Format Options

```bash
# Human-readable (default)
rill start

# JSON for parsing/filtering
rill start --log-format json

# Maximum verbosity
rill start --debug --verbose --log-format json
```

---

## 5. PERFORMANCE OPTIMIZATION

### Best Practices (from docs)

**General Guidelines:**
- DuckDB works well **out-of-box for ≤50GB datasets**
- For >50GB, contact Rill support for guidance
- Use dev/prod templating to limit local data ingestion

**Model Optimization:**
- Use incremental models for large datasets
- Partition by time/category for parallel processing
- Set appropriate refresh schedules (don't over-refresh)
- Monitor `elapsed` times in logs

**Test Performance:**
- Tests add time to refresh cycle
- Complex tests (joins, aggregates) are expensive
- Balance test coverage vs. refresh time
- Use indexes on test query columns when possible

---

## 6. INTEGRATION TESTING APPROACHES

### Local Testing Workflow
```bash
# 1. Install Rill
curl https://rill.sh | sh

# 2. Start project
rill start my-project

# 3. Validate resources
rill validate --verbose

# 4. Query models directly
rill query --sql "SELECT * FROM my_model LIMIT 10"

# 5. Check for errors
rill project status --local
```

### CI/CD Testing Pattern

**GitHub Actions Example (Inferred from Best Practices):**
```yaml
name: Validate Rill Project
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Rill
        run: curl https://rill.sh | sh
      
      - name: Set environment variables
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_CREDS }}
        run: echo "Credentials configured"
      
      - name: Validate project
        run: |
          rill validate --environment prod \
            -o validation-results.json \
            --model-timeout-seconds 120
      
      - name: Check for errors
        run: |
          if grep -q '"error"' validation-results.json; then
            echo "Validation errors found"
            cat validation-results.json
            exit 1
          fi
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: validation-results.json
```

### API Testing (for embedded dashboards)

**Use Rill REST API:**
- API Reference: https://docs.rilldata.com/api/admin
- Test dashboard queries programmatically
- Validate metrics computations
- Monitor alert execution

### Browser Testing

**Use Playwright or Selenium for:**
- Dashboard rendering validation
- Interactive filter testing
- Export functionality verification
- URL parameter behavior

**Rill URL Parameters:** https://docs.rilldata.com/reference/url-syntax/url-parameters

---

## 7. DATA QUALITY VALIDATION PATTERNS

### Completeness Checks
```yaml
tests:
  - name: All Expected Ad Formats Present
    sql: |
      SELECT expected_format
      FROM (VALUES ('banner'), ('video'), ('native')) AS expected(expected_format)
      WHERE expected_format NOT IN (SELECT DISTINCT ad_format FROM model)
```

### Aggregate Validations
```yaml
tests:
  - name: Positive Total Spend
    sql: SELECT 'Negative spend' WHERE (SELECT SUM(spend) FROM model) < 0
  
  - name: CTR Within Expected Range
    sql: |
      SELECT 'CTR out of range'
      WHERE (SELECT SUM(clicks) * 1.0 / NULLIF(SUM(impressions), 0) FROM model) > 0.5
```

### Date Range Checks
```yaml
tests:
  - name: Valid Impression Date Range
    assert: impression_date >= '2020-01-01' AND impression_date <= CURRENT_DATE
  
  - name: Impressions Within Last Year
    assert: impression_date >= CURRENT_DATE - INTERVAL '1 year'
```

### Cross-Table Validation
```yaml
tests:
  - name: Clicks Must Have Impressions
    sql: SELECT * FROM model WHERE clicks > 0 AND impressions = 0
  
  - name: Click Timestamp After Impression
    sql: SELECT * FROM model WHERE click_timestamp < impression_timestamp
```

---

## 8. ANTI-PATTERNS TO AVOID

❌ **Don't use data quality tests for live connectors**
→ Use alerts with scheduled checks instead

❌ **Don't ignore dependency errors**
→ Always fix upstream resource first

❌ **Don't create overly complex tests**
→ Split into multiple simple tests for clarity

❌ **Don't test in production only**
→ Use `rill validate` in CI/CD before deploy

❌ **Don't hardcode environment-specific values**
→ Use templating: `{{ .env.VARIABLE_NAME }}`

❌ **Don't skip test naming conventions**
→ Use descriptive names: "No Null Campaign IDs" not "Test 1"

❌ **Don't forget to monitor test performance**
→ Review `elapsed` times, optimize slow tests

---

## 9. RECOMMENDED TESTING STRATEGY

### Tier 1: Model-Level Tests (Fast, Always Run)
```yaml
type: model
sql: SELECT * FROM source
tests:
  - name: Primary Key Not Null
    assert: id IS NOT NULL
  - name: No Duplicate IDs
    sql: SELECT id, COUNT(*) FROM model GROUP BY id HAVING COUNT(*) > 1
  - name: Valid Date Range
    assert: created_at >= '2020-01-01' AND created_at <= CURRENT_DATE
```

### Tier 2: Scheduled Alerts (Hourly/Daily)
```yaml
type: alert
display_name: Data Freshness Check
refresh:
  cron: 0 * * * *  # Every hour
data:
  sql: |
    SELECT MAX(event_time) AS max_time
    FROM model
    WHERE max_time < NOW() - INTERVAL '2 hours'
notify:
  slack:
    channels: ['#data-alerts']
```

### Tier 3: CI/CD Validation (On Push)
```bash
# In CI pipeline
rill validate --environment staging -o results.json
rill project refresh --model critical_model
```

### Tier 4: Manual Testing (Pre-Deploy)
```bash
# Local verification before deploy
rill start --verbose
rill validate --environment prod
rill project status --local
```

---

## 10. REAL-WORLD EXAMPLE PATTERNS

### From rill-examples Repository

**Project Structure Pattern:**
```
rill-{project-name}/
├── sources/
│   └── data_source.yaml
├── models/
│   └── model.yaml (with tests)
├── dashboards/
│   └── explore.yaml
├── alerts/
│   └── alert.yaml
└── rill.yaml
```

**Common Alert Pattern (All Examples Use This):**
```yaml
type: alert
display_name: Project Resource Status Check
refresh:
  cron: 0 * * * *
data:
  resource_status:
    where_error: true
notify:
  email:
    recipients: [team@example.com]
```

This checks **any resource error** (model, source, connector failures).

---

## KEY TAKEAWAYS

1. **Use tests for Rill-managed models, alerts for live connectors**
2. **`rill validate` is your CI/CD friend** - JSON output, exit codes
3. **Start with critical validations** (nulls, uniqueness, ranges)
4. **Dependency errors cascade** - always fix upstream first
5. **DuckDB handles ≤50GB well** - contact support for larger datasets
6. **Tests don't block models** - model remains queryable even if tests fail
7. **Alert patterns are standardized** - use examples as templates
8. **Debugging flow: logs → status → trace viewer** (in that order)
9. **JSON log format for automation**, human format for reading
10. **Real examples in rill-examples repo** - clone and learn from them

---

## REFERENCES

- Rill Data Quality Tests: https://docs.rilldata.com/developers/build/models/data-quality-tests
- Rill Alert YAML Reference: https://docs.rilldata.com/reference/project-files/alerts
- Rill CLI Validate: https://docs.rilldata.com/reference/cli/validate
- Rill Debugging Guide: https://docs.rilldata.com/developers/build/debugging
- Rill Examples Repository: https://github.com/rilldata/rill-examples
- Rill Quickstart: https://docs.rilldata.com/developers/get-started/quickstart

---

## 11. RILL INTEGRATION TESTING PATTERNS (Feb 26, 2026)

### Test Script Structure
Created `test_rill_integration.py` with comprehensive coverage of all 5 dashboards.

### Key Patterns Implemented

#### 1. Fixtures Pattern (from test_uat.py)
```python
@pytest.fixture
def rill_base_url():
    return "http://localhost:9009"

@pytest.fixture
def rill_api_timeout():
    return 10
```
- Provides reusable configuration across tests
- Makes it easy to change base URL or timeout globally

#### 2. Helper Functions Pattern
Created three validation helpers:
- `validate_response_schema()` - Checks for 'meta' and 'data' fields
- `validate_data_types()` - Ensures rows match schema
- `validate_row_counts()` - Verifies minimum row requirement

Each returns `Tuple[bool, str]` for clear pass/fail with error messages.

#### 3. Test Organization Pattern
- One test class per dashboard (5 classes total)
- 4 tests per class: accessibility, data types, row counts, measure values
- 1 integration test class for cross-dashboard validation
- **Total: 21 tests, all passing**

#### 4. Dashboard Configuration Reference

**chronic_absenteeism_risk**
- Primary dimension: school_id (also: student_key, grade_level, risk_level)
- Measures: total_students, chronic_absence_count, chronic_absence_rate, avg_attendance_rate_30d, avg_risk_score, high_risk_students
- Validates: Attendance trends, absence flags, risk scoring

**equity_outcomes_by_demographics**
- Primary dimension: race_ethnicity (also: english_learner, special_education, economically_disadvantaged)
- Measures: cohort_size, avg_attendance, avg_no_discipline, avg_gpa, avg_gpa_above_2_5, avg_below_c
- Validates: Outcome equity across demographic groups

**class_effectiveness**
- Primary dimension: school_id (also: course_id, grade_level, term, effectiveness_rating)
- Measures: total_sections, total_students, avg_class_grade, avg_pass_rate, avg_ab_grades
- Validates: Class/section performance metrics

**performance_correlations**
- Primary dimension: correlation_pair (also: expected_direction, strength)
- Measures: total_correlations, avg_correlation, strong/moderate/weak_correlations, total_data_points, avg_data_points
- Validates: Correlation analyses between metrics

**wellbeing_risk_profiles**
- Primary dimension: school_id (also: student_key, grade_level, wellbeing_risk_level, primary_concern, high_risk_domain_count)
- Measures: total_students, critical_risk_students, high_risk_students, moderate_risk_students
- Validates: Multi-domain risk assessment

### API Query Pattern
```python
response = requests.post(
    "http://localhost:9009/v1/instances/default/queries/metrics-views/{dashboard}/toplist",
    json={
        "dimensionName": "dimension_name",
        "measureNames": ["measure1", "measure2"],
        "limit": 10
    },
    timeout=10
)
```

Response structure:
```python
{
    "meta": [
        {"name": "column1", "type": "CODE_STRING", "nullable": true},
        {"name": "measure1", "type": "CODE_INT64", "nullable": true}
    ],
    "data": [
        {"column1": "value1", "measure1": 123},
        {"column1": "value2", "measure1": 456}
    ]
}
```

### Error Handling Strategy
1. **HTTP Errors**: `response.raise_for_status()` catches non-200 status codes
2. **JSON Parse**: `response.json()` handles malformed JSON
3. **Schema Validation**: Check for required 'meta' and 'data' fields
4. **Row Count**: Verify at least 1 row returned
5. **Type Validation**: Ensure rows match meta schema

### Summary Report Generation
- Direct execution: `python3 test_rill_integration.py` produces human-readable summary
- Pytest execution: `pytest test_rill_integration.py -v` produces detailed test output
- Report includes: timestamp, server URL, per-dashboard row/column counts

### Lessons Learned
1. **Fixture reuse is critical** - avoids hardcoding URLs across 21 tests
2. **Helper functions reduce duplication** - validation logic reused across dashboards
3. **Class-per-dashboard organization** - clear separation of concerns
4. **Integration tests after unit tests** - validates cross-dashboard consistency
5. **Tuple return pattern** - cleaner than raising exceptions for validation failures
6. **Documentation through docstrings** - each test explains what it validates

### Testing Best Practices Applied
- ✅ Clear test names following pytest convention
- ✅ One assertion per test (or grouped assertions for logical units)
- ✅ Fixtures for configuration management
- ✅ Helper functions for common operations
- ✅ Integration tests validate all dashboards work together
- ✅ Human-readable summary report
- ✅ Error messages indicate what failed and why
- ✅ Follows test_uat.py structure and style

### Metric Results
- **Lines of code**: 782
- **Test cases**: 21
- **Dashboards covered**: 5/5 (100%)
- **Execution time**: 0.23s
- **Pass rate**: 100% (21/21)
- **Code organization**: 5 test classes + 1 integration class
