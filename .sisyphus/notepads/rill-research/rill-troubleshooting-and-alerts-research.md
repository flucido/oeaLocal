# Rill v0.82.1+ Troubleshooting & Alert Configuration Research

**Research Date:** February 26, 2026  
**Rill Version Researched:** v0.82.1 (released Feb 25, 2026)  
**Primary Sources:** 
- https://docs.rilldata.com (Official Documentation)
- https://github.com/rilldata/rill (GitHub Repository)
- Official Release Notes

---

## 1. COMMON ERRORS & SOLUTIONS

### Model Errors

#### Connection & Credential Issues
**Error:** `Failed to connect to ...`  
**Cause:** Connector configuration or credential problems  
**Solution:**
- Check connector credentials in project settings
- Verify firewall settings for externally hosted services
- Reference: https://docs.rilldata.com/developers/build/connectors/data-source#externally-hosted-services

#### Missing Table/Data Issues
**Error:** `Table with name ... does not exist!`  
**Diagnosis:** Run verification query:
```bash
rill query --sql "select * from {table_name} limit 1"
```
**Solution:** Verify table exists in your data source

**Error:** `IO Error: No files found that match the pattern...`  
**Cause:** Incorrect cloud storage path or missing files  
**Solution:**
- Double-check folder paths in cloud storage
- Verify files exist at specified location
- Check permissions on cloud storage bucket

#### Partition Errors
**Error:** `some partitions have errors`  
**Solution:**
```bash
rill project refresh --model {model_name} --errored-partitions
```
**Notes:** 
- Shows number of partitions during reconciliation: `Resolved model partitions {"model": "staging_to_CH", "partitions": 16}`
- Use dev/prod templating to limit partitions locally

#### Memory Issues
**Error:** `Out of Memory Error: ...`  
**Solution:** Contact Rill support (https://docs.rilldata.com/contact)  
**Prevention:** Optimize queries, limit data in dev environment

### Metrics View & Dashboard Errors

#### Dependency Errors
**Pattern:** Cascading failures with `dependency_error: true` flag  
**Root Cause:** Upstream model failure causes downstream resources to fail  
**Diagnosis:**
```bash
# Local development
Check Status tab in Rill Developer UI

# Deployed projects
rill project status <project-name>
```
**Solution:** Always trace to root cause - fix the upstream resource first

**Example Log Pattern:**
```
WARN Reconcile failed {"name": "orders", "type": "Model", "error": "..."}
INFO Reconciled resource {"name": "orders_customers_model", "type": "Model", 
     "error": "dependency error: resource \"orders\" has an error", "dependency_error": true}
```

#### Type Mismatch Errors
**Error:** `measure "earliest_commit_date_measure" is of type CODE_TIMESTAMP, but must be a numeric type`  
**Cause:** Timestamp fields used as measures (only numeric types allowed)  
**Solution:** 
- Convert to numeric (e.g., UNIX timestamp)
- Use dimension instead
- Remove from measures list

#### Missing Fields
**Error:** `table "model_name" does not exist`  
**Cause:** Underlying model failed, metrics view references non-existent table  
**Solution:** Check model status first (see dependency errors above)

### Parser Errors
**Common Patterns:**
- YAML syntax errors (indentation, quotes, colons)
- Unrecognized properties in YAML files
- Template variable resolution failures

**Error Example:** `failed to resolve templated property "google_application_credentials": template: :1:6: executing "" at <.env.GOOGLE_APPLICATION_CREDENTIALS>: map has no entry for key "GOOGLE_APPLICATION_CREDENTIALS"`  
**Cause:** Environment variable not set  
**Solution:**
```bash
# Check environment variables
rill env ls

# Set missing variable
rill env set GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

---

## 2. DIAGNOSTIC COMMANDS

### Validation & Status

#### `rill validate`
**Purpose:** Validate project resources before deployment  
**Usage:**
```bash
rill validate [<path>] [flags]
```

**Key Flags:**
- `--reset` - Clear and re-ingest source data
- `--pull-env` - Pull environment variables from Rill Cloud (default: true)
- `--environment string` - Environment name (default: "dev")
- `--verbose` - Enable debug logging
- `--silent` - Suppress all log output
- `--debug` - Collect additional debug info
- `--log-format string` - Log format ("console" or "json")
- `--model-timeout-seconds uint32` - Timeout for model reconciliation (default: 60, set 0 for no timeout)
- `-o, --output-file string` - Output validation results to JSON file

**Reference:** https://docs.rilldata.com/reference/cli/validate

#### `rill project status`
**Purpose:** Check project health and resource status  
**Usage:**
```bash
# Deployed project
rill project status <project-name>

# Local project
rill project status --local
```

**Shows:**
- Resource reconciliation status
- Error states for individual resources
- Dependency relationships
- Overall project health

**Reference:** https://docs.rilldata.com/reference/cli/project/status

#### `rill project logs`
**Purpose:** View project logs from deployed instances  
**Usage:**
```bash
# View recent logs
rill project logs <project-name>

# Follow logs in real-time (like tail -f)
rill project logs <project-name> --follow

# Show only last N lines
rill project logs <project-name> --tail 100

# Filter by log level
rill project logs <project-name> --level DEBUG
```

### Debugging Flags

#### `rill start` with debugging options
**Usage:**
```bash
# Increase log verbosity (debug level)
rill start --verbose

# Collect additional debug info
rill start --debug

# Combine for maximum detail
rill start --debug --verbose

# JSON log format (for parsing/filtering)
rill start --log-format json
```

**When to Use:**
- `--verbose`: Need more detail about operations
- `--debug`: Troubleshooting complex issues, enables Trace Viewer
- `--log-format json`: Programmatic log processing

**Reference:** https://docs.rilldata.com/reference/cli/start

### Query Testing

#### `rill query`
**Purpose:** Test SQL queries directly against project data  
**Usage:**
```bash
# Test table exists
rill query --sql "select * from {table_name} limit 1"

# Test model query
rill query --sql "select count(*) from my_model"
```

### Refresh Commands

#### Model Refresh
```bash
# Refresh specific model
rill project refresh --model {model_name}

# Refresh errored partitions only
rill project refresh --model {model_name} --errored-partitions

# Refresh all resources
rill project refresh
```

---

## 3. ALERT SCHEMA v0.82.1

### Required Fields

```yaml
type: alert                    # REQUIRED: Must be "alert"
display_name: "Alert Name"     # REQUIRED: Display name
data: {...}                    # REQUIRED: Data source configuration
notify: {...}                  # REQUIRED: Notification targets
```

### Optional Fields

```yaml
description: "Alert purpose"   # OPTIONAL: Alert description (text field)
refresh:                       # OPTIONAL: Schedule (defaults to model refresh)
  cron: "0 * * * *"           # Cron expression OR
  every: "24h"                 # Go duration
  time_zone: "UTC"            # Timezone for cron
  disable: false              # Disable without deleting
  ref_update: true            # Run when dependency updates
  run_in_dev: false           # Allow in dev mode

intervals:                     # OPTIONAL: Define check intervals
  duration: "P1D"             # ISO8601 duration (e.g., P1D = 1 day)
  limit: 5                    # Max intervals to check
  check_unclosed: false       # Check incomplete intervals

watermark: "trigger_time"      # OPTIONAL: "trigger_time" or "inherit"
timeout: "300"                 # OPTIONAL: Alert timeout in seconds

# Notification behavior
on_recover: false              # OPTIONAL: Alert when recovering (default: false)
on_fail: true                  # OPTIONAL: Alert on failure (default: true)
on_error: false                # OPTIONAL: Alert on evaluation error (default: false)
renotify: false                # OPTIONAL: Enable repeated notifications (default: false)
renotify_after: "24h"         # OPTIONAL: Re-notification interval (snooze duration)

# Security context
for:                           # OPTIONAL: User context for policies
  user_id: "user123"          # OR user_email OR attributes
  
annotations: {}                # OPTIONAL: Key-value metadata
```

### Data Source Options (OneOf Required)

#### Option 1: Raw SQL
```yaml
data:
  sql: "SELECT * FROM model WHERE value > threshold"
  connector: "duckdb"  # Optional: specify connector
```

#### Option 2: Metrics SQL
```yaml
data:
  metrics_sql: "SELECT measure_name FROM metrics_view WHERE ..."
```

#### Option 3: Custom API
```yaml
data:
  api: "my_custom_api"
  args:
    param1: value1
```

#### Option 4: Glob Pattern
```yaml
data:
  glob: "gs://bucket/path/*.parquet"  # String OR object
  connector: "gcs"
```

#### Option 5: Resource Status
```yaml
data:
  resource_status:
    where_error: true  # Alert when resource is in error state
```

#### Option 6: AI-Generated Insights (Reports Only)
```yaml
data:
  ai:
    prompt: "Analyze metric trends"
    time_range:
      iso_duration: "P7D"
    comparison_time_range:
      iso_offset: "P7D"
    context:
      explore: "my_dashboard"
      dimensions: ["country", "campaign"]
      measures: ["revenue", "clicks"]
```

### Notification Targets

#### Email (Default - Always Available)
```yaml
notify:
  email:
    recipients:
      - "team@example.com"
      - "oncall@example.com"
```

#### Slack (Must Be Configured First)
```yaml
notify:
  slack:
    users:
      - "U123456"          # Slack user IDs
    channels:
      - "#alerts"          # Channel names (public/private)
      - "#data-quality"
    webhooks:
      - "https://hooks.slack.com/services/..."  # Webhook URLs
```

**Important:** Add Slack bot to channels first using `/invite @bot-name`

**Reference:** https://docs.rilldata.com/developers/build/connectors/services/slack

### Common Properties (All Resources)

```yaml
name: "alert_name"            # Usually inferred from filename
refs:                          # Resource dependencies
  - "model_name"
  - "metrics_view_name"
  
dev:                           # Dev environment overrides
  refresh:
    disable: true             # Disable alerts in dev
    
prod:                          # Prod environment overrides
  refresh:
    cron: "0 */6 * * *"      # Different schedule in prod
```

---

## 4. ALERT SCHEMA CHANGES (v0.81.4 → v0.82.1)

### Breaking Changes: NONE FOUND

**Research Notes:**
- v0.82.1 released Feb 25, 2026 with minimal changelog (pagination fix)
- v0.82.0 released Feb 2026 with features but no alert schema changes documented
- `description` field exists as **optional** string field (not new in v0.82+)
- `notify.slack.webhooks` field exists as **array** (consistent with schema)

### Current Schema State (v0.82.1)
- `description`: **Optional** text field for alert description
- `display_name`: **Required** for display name (replaces deprecated `title`)
- `notify.slack.webhooks`: **Array of strings** for webhook URLs
- All fields backward compatible with v0.81.4

**Conclusion:** No breaking changes found between v0.81.4 and v0.82.1 for alert schema.

---

## 5. ALERT TESTING PATTERNS

### Pre-Deployment Validation

#### 1. Syntax Validation
```bash
# Validate alert YAML syntax
rill validate alerts/my_alert.yaml --verbose
```

#### 2. Data Query Testing
```bash
# Test alert query returns expected results
rill query --sql "$(cat alerts/my_alert.yaml | grep -A 10 'sql:' | sed 's/  sql: //')"
```

#### 3. Local Testing in Rill Developer
```bash
# Start with alert enabled in dev
rill start --pull-env

# Monitor logs for alert execution
# Look for: "Reconciling resource" {"name": "my_alert", "type": "Alert"}
```

### Testing Best Practices

#### Start Small
```yaml
# Test alert with short interval first
refresh:
  every: "5m"  # 5 minutes for testing
  
# Switch to production schedule after validation
# refresh:
#   cron: "0 */6 * * *"  # Every 6 hours
```

#### Use Dev Overrides
```yaml
# Disable in dev, enable in prod
dev:
  refresh:
    disable: true
    
prod:
  refresh:
    cron: "0 * * * *"
```

#### Test Notification Channels
```yaml
# Test email to yourself first
notify:
  email:
    recipients:
      - "your.email@example.com"
      
# After validation, add team
# notify:
#   email:
#     recipients:
#       - "team@example.com"
```

---

## 6. ALERT BEST PRACTICES

### Alert Design Patterns

#### 1. Data Freshness Alerts
```yaml
type: alert
display_name: "Data Staleness Alert"
description: "Alert when data is more than 1 day old"

refresh:
  cron: "0 * * * *"  # Check hourly

data:
  sql: |
    SELECT * FROM (
      SELECT MAX(event_time) AS max_time
      FROM rill_metrics_model
    )
    WHERE max_time < NOW() - INTERVAL '1 day'

notify:
  slack:
    channels: ["#data-monitoring"]
```

#### 2. Threshold Alerts
```yaml
type: alert
display_name: "High Error Rate"
description: "Alert when error rate exceeds 5%"

refresh:
  cron: "*/15 * * * *"  # Every 15 minutes

data:
  sql: |
    SELECT 
      error_rate,
      total_requests
    FROM error_metrics
    WHERE error_rate > 0.05
    AND total_requests > 100  -- Avoid low-volume noise

notify:
  email:
    recipients: ["oncall@example.com"]
  slack:
    channels: ["#incidents"]
```

#### 3. Resource Health Alerts
```yaml
type: alert
display_name: "Model Reconciliation Failure"
description: "Alert when critical model fails"

data:
  resource_status:
    where_error: true

notify:
  slack:
    channels: ["#data-engineering"]
```

#### 4. Volume Anomaly Detection
```yaml
type: alert
display_name: "Unusual Traffic Volume"
description: "Alert on significant traffic changes"

intervals:
  duration: "PT1H"  # 1-hour intervals
  limit: 24         # Check last 24 hours

data:
  sql: |
    SELECT 
      hour,
      request_count,
      avg_count
    FROM (
      SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        COUNT(*) as request_count,
        AVG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('hour', timestamp) ROWS BETWEEN 23 PRECEDING AND 1 PRECEDING) as avg_count
      FROM requests
      GROUP BY hour
    )
    WHERE request_count > avg_count * 2  -- 2x average
    OR request_count < avg_count * 0.5   -- 50% below average

notify:
  email:
    recipients: ["team@example.com"]
```

### Alert Anti-Patterns (What to Avoid)

#### ❌ DON'T: Poll Too Frequently
```yaml
# BAD: Checking every minute creates noise
refresh:
  cron: "* * * * *"  # Every minute - too frequent!
```
**Better:** Align with data refresh schedule or business needs (hourly, daily)

#### ❌ DON'T: Alert on Low-Volume Changes
```yaml
# BAD: Alerts on 1 error out of 10 requests (10% error rate)
data:
  sql: SELECT * FROM errors WHERE error_count > 0
```
**Better:** Add minimum volume thresholds
```yaml
# GOOD: Only alert on statistically significant volumes
data:
  sql: |
    SELECT * FROM errors 
    WHERE error_count > 10 
    AND total_requests > 100
```

#### ❌ DON'T: Create Alert Fatigue
```yaml
# BAD: Re-notify every hour for unresolved issue
renotify: true
renotify_after: "1h"
```
**Better:** Use longer snooze periods or fix root cause
```yaml
# GOOD: Give team time to respond
renotify: true
renotify_after: "24h"
```

#### ❌ DON'T: Use Vague Alert Names
```yaml
# BAD
display_name: "Data Alert"
description: "Check data"
```
**Better:**
```yaml
# GOOD
display_name: "Revenue Data Stale > 24h"
description: "Alert when revenue_events table hasn't updated in 24 hours"
```

#### ❌ DON'T: Ignore Testing
**Bad Practice:** Deploy alert directly to production  
**Better Practice:** Test in dev environment first with short intervals

### Recommended Patterns by Use Case

#### Troubleshooting Alerts
- **Pattern:** Binary checks (data exists, resource healthy)
- **Criteria:** `> 0` or `resource_status.where_error`
- **Example:** Impressions > 0 for all campaigns
- **Frequency:** Aligned with data refresh

#### Pacing Alerts
- **Pattern:** Progress toward goals with multiple thresholds
- **Criteria:** Absolute values (50%, 75%, 100% of target)
- **Example:** Budget spend alerts at 50%, 75%, 90%
- **Frequency:** Daily or when data updates

#### Monitoring Alerts
- **Pattern:** Relative comparisons to historical data
- **Criteria:** Percentage change from prior period
- **Example:** Revenue down 20% week-over-week
- **Frequency:** Hourly or daily based on data granularity

---

## 7. SUPPORTED NOTIFICATION CHANNELS

### Available Targets (v0.82.1)

| Channel | Support | Configuration Required | Notes |
|---------|---------|----------------------|-------|
| Email | ✅ Default | None - always enabled | Recipients as array of strings |
| Slack | ✅ Available | Yes - requires Slack app setup | Supports channels, users, webhooks |
| Webhooks | ⚠️ Via Slack | Use `slack.webhooks` field | Generic webhook support through Slack |
| PagerDuty | ❌ Not documented | - | Feature request to Rill team |
| Microsoft Teams | ❌ Not documented | - | Feature request to Rill team |
| Opsgenie | ❌ Not documented | - | Feature request to Rill team |

**Reference for Feature Requests:** https://docs.rilldata.com/contact

### Slack Configuration Details

#### Prerequisites
1. Create Slack app in workspace
2. Add required bot permissions (chat:write, channels:read)
3. Install app to workspace
4. Add bot to target channels: `/invite @bot-name`

#### Configuration in Rill
```bash
# Set Slack credentials via CLI
rill env set SLACK_BOT_TOKEN=xoxb-your-token
rill env set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

#### Alert Usage
```yaml
notify:
  slack:
    channels: ["#alerts"]     # Requires bot invited to channel
    users: ["U123456"]        # Direct message to user
    webhooks:                 # Webhook URLs (array)
      - "https://hooks.slack.com/services/T00/B00/xxx"
```

**Full Guide:** https://docs.rilldata.com/developers/build/connectors/services/slack

---

## 8. DATA QUALITY TESTS (Alternative to Alerts for Models)

### When to Use Tests vs Alerts

| Feature | Data Quality Tests | Alerts |
|---------|-------------------|--------|
| **Trigger** | On model refresh | On schedule (cron) |
| **Use Case** | Rill-managed models (DuckDB) | Live connectors (ClickHouse, etc.) |
| **Failure Impact** | Model still available | Notification sent |
| **Best For** | Schema validation, referential integrity | Monitoring production data |

### Data Quality Test Examples

#### Null Checks
```yaml
type: model
sql: SELECT * FROM source_table
tests:
  - name: "No Null Campaign IDs"
    assert: campaign_id IS NOT NULL
    
  - name: "No Null Timestamps"
    assert: event_timestamp IS NOT NULL
```

#### Uniqueness Constraints
```yaml
tests:
  - name: "No Duplicate IDs"
    sql: |
      SELECT impression_id, COUNT(*) as count
      FROM model
      GROUP BY impression_id
      HAVING COUNT(*) > 1
```

#### Range Validations
```yaml
tests:
  - name: "Valid Bid Price Range"
    assert: bid_price >= 0 AND bid_price <= 100
    
  - name: "Valid Date Range"
    assert: event_date >= '2020-01-01' AND event_date <= CURRENT_DATE
```

#### Referential Integrity
```yaml
tests:
  - name: "Valid Campaign References"
    sql: |
      SELECT i.campaign_id
      FROM model i
      LEFT JOIN campaigns c ON i.campaign_id = c.id
      WHERE c.id IS NULL
```

**Full Reference:** https://docs.rilldata.com/developers/build/models/data-quality-tests

---

## 9. TROUBLESHOOTING WORKFLOW

### Step-by-Step Debugging Process

#### 1. Identify the Error Source
```bash
# Check project status
rill project status --local
# OR (for deployed)
rill project status <project-name>

# Review logs
rill start --verbose
# OR (for deployed)
rill project logs <project-name> --follow
```

#### 2. Check for Dependency Errors
Look for log patterns:
```
Reconciled resource {"name": "resource_name", "type": "Type", 
                     "dependency_error": true, 
                     "error": "dependency error: resource \"upstream\" has an error"}
```
**Action:** Fix the upstream resource first (the one mentioned in error)

#### 3. Validate Configuration
```bash
# Validate YAML syntax
rill validate --verbose

# Check environment variables
rill env ls

# Test specific model
rill query --sql "SELECT * FROM model_name LIMIT 1"
```

#### 4. Enable Debug Mode
```bash
# Maximum debugging detail
rill start --debug --verbose --log-format json

# Access Trace Viewer (requires --debug flag)
# Navigate to Rill Developer UI → Trace Viewer tab
```

#### 5. Fix and Re-validate
```bash
# After fixing, refresh specific resource
rill project refresh --model {model_name}

# Refresh errored partitions only
rill project refresh --model {model_name} --errored-partitions

# Re-validate entire project
rill validate --output-file validation_results.json
```

### Common Troubleshooting Scenarios

#### Scenario: Alert Not Firing

**Check:**
1. Alert schedule: `rill validate alerts/my_alert.yaml --verbose`
2. Query returns data: `rill query --sql "<alert-sql-query>"`
3. Notification channel configured: `rill env ls | grep SLACK`
4. Alert enabled: Check `refresh.disable: false`

**Debug:**
```bash
# Check alert execution in logs
rill project logs <project-name> --follow | grep "my_alert"
```

#### Scenario: Model Stuck in Error State

**Check:**
1. Model logs: Look for `WARN Reconcile failed` with error details
2. Dependency status: Check upstream models/sources
3. Credentials: `rill env ls`
4. Data availability: Verify source files exist

**Fix:**
```bash
# Reset and refresh
rill project refresh --model {model_name} --reset

# If partitioned model
rill project refresh --model {model_name} --errored-partitions
```

#### Scenario: Dashboard Shows No Data

**Check:**
1. Metrics view status (depends on model)
2. Model status (depends on source)
3. Source status (connector + data availability)

**Debug:**
```bash
# Check entire dependency chain
rill project status --local

# Trace through logs for dependency_error flags
rill start --verbose | grep "dependency_error"
```

---

## 10. ADDITIONAL RESOURCES

### Official Documentation
- **Main Docs:** https://docs.rilldata.com
- **Debugging Guide:** https://docs.rilldata.com/developers/build/debugging
- **Alert Reference:** https://docs.rilldata.com/reference/project-files/alerts
- **Alert Guide:** https://docs.rilldata.com/guide/alerts
- **CLI Reference:** https://docs.rilldata.com/reference/cli
- **Data Quality Tests:** https://docs.rilldata.com/developers/build/models/data-quality-tests
- **Slack Integration:** https://docs.rilldata.com/developers/build/connectors/services/slack

### GitHub Resources
- **Repository:** https://github.com/rilldata/rill
- **Examples:** https://github.com/rilldata/rill-examples
- **Issues:** https://github.com/rilldata/rill/issues
- **Latest Release:** https://github.com/rilldata/rill/releases/tag/v0.82.1

### Community & Support
- **Discord:** https://discord.gg/DJ5qcsxE (mentioned in docs)
- **Contact Form:** https://docs.rilldata.com/contact
- **Release Notes:** https://docs.rilldata.com/notes

### Useful CLI Commands Reference

```bash
# Installation & Setup
curl https://rill.sh | sh
rill start my-rill-project

# Validation
rill validate [path] --verbose --output-file results.json

# Environment Management
rill env ls
rill env set KEY=value
rill env pull  # From Rill Cloud

# Project Management
rill project status <project-name>
rill project logs <project-name> --follow --tail 100
rill project refresh [--model name] [--errored-partitions]

# Querying
rill query --sql "SELECT * FROM table LIMIT 10"

# Debugging
rill start --debug --verbose --log-format json

# Deployment
rill deploy
rill project status <project-name>
```

---

## RESEARCH METHODOLOGY

**Data Collection:**
1. Fetched official documentation from docs.rilldata.com
2. Retrieved GitHub API release data for v0.82.1 and v0.82.0
3. Searched for community discussions and known issues (2026 dated)
4. Cross-referenced alert schema documentation with examples

**Key Findings:**
- No breaking changes found in alert schema between v0.81.4 → v0.82.1
- `description` field is optional (not a new requirement)
- `notify.slack.webhooks` accepts array (consistent with current schema)
- Primary troubleshooting approach: logs → dependency chain → root cause

**Limitations:**
- Could not access private GitHub issues (authentication required)
- rill-examples repository did not return alert.yaml examples in search
- v0.82.1 changelog is minimal (single pagination fix)

---

**Document Version:** 1.0  
**Last Updated:** February 26, 2026
