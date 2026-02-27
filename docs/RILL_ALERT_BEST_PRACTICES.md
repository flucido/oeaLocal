# Rill Alert Best Practices (v0.82.1+)

Comprehensive guide to creating production-ready alert configurations for Rill v0.82.1 and later.

---

## Alert Schema v0.82.1 Reference

### Required Fields

```yaml
type: alert
display_name: "Human-Readable Alert Name"
data:
  # ONE of:
  sql: "SELECT ..."               # Raw SQL query
  metrics_sql: "SELECT ..."       # Metrics view query
  resource_status: {}             # Resource health check
notify:
  # At least ONE notification channel:
  email: { recipients: [...] }
  slack: { channels: [...], webhooks: [...] }
  webhooks: [{ url: "..." }]
```

### Optional Fields

```yaml
refresh:
  cron: "*/10 * * * *"           # Default: every 10 minutes
  time_zone: "America/Los_Angeles"  # Default: UTC
  run_in_dev: false              # Default: false (don't run in dev mode)

on_recover: false                # Default: false (send alert when recovers)
on_fail: true                    # Default: true (send alert on failure)
on_error: false                  # Default: false (send alert on error)

renotify: false                  # Default: false (repeat notifications)
renotify_after: "24h"            # Default: 24h (snooze duration)

intervals:
  duration: PT15M                # Track 15-minute intervals
  limit: 96                      # Keep last 24 hours (96 x 15min)

timeout: "30s"                   # Default: 30s (query timeout)
```

---

## Breaking Changes from v0.81.4

### Change 1: `description` Field Removed

**v0.81.4 (BROKEN in v0.82.1):**
```yaml
type: alert
description: "Monitors pipeline health metrics"  # ❌ No longer supported
display_name: "Pipeline Health"
```

**v0.82.1 (WORKING):**
```yaml
type: alert
# NO description field at root level
display_name: "Pipeline Health"  # Use this instead
```

**Why it changed:** Alert metadata consolidated into `display_name` for consistency

---

### Change 2: `webhook_url` → `webhooks` Array

**v0.81.4 (BROKEN in v0.82.1):**
```yaml
notify:
  webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"  # ❌ Changed to array
```

**v0.82.1 (WORKING):**
```yaml
notify:
  webhooks:  # Array format
    - url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    - url: "https://hooks.slack.com/services/ANOTHER/WEBHOOK/URL"  # Can have multiple
```

**Why it changed:** Support for multiple webhook destinations in one alert

---

## Alert Patterns

### Pattern 1: Data Freshness Monitoring

**Use Case:** Detect when analytics data becomes stale (e.g., data older than expected)

```yaml
type: alert
display_name: "Data Freshness Alert - Analytics Tables"

refresh:
  cron: "*/30 * * * *"  # Check every 30 minutes

data:
  sql: |
    WITH data_freshness AS (
      SELECT 
        'fct_attendance_daily' AS table_name,
        MAX(attendance_date) AS last_update,
        CURRENT_DATE - INTERVAL '2 days' AS threshold,
        CASE 
          WHEN MAX(attendance_date) < CURRENT_DATE - INTERVAL '2 days' 
          THEN 'STALE' 
          ELSE 'FRESH' 
        END AS status
      FROM analytics.fct_attendance_daily
      
      UNION ALL
      
      SELECT 
        'fct_student_grades' AS table_name,
        MAX(grade_date) AS last_update,
        CURRENT_DATE - INTERVAL '7 days' AS threshold,
        CASE 
          WHEN MAX(grade_date) < CURRENT_DATE - INTERVAL '7 days' 
          THEN 'STALE' 
          ELSE 'FRESH' 
        END AS status
      FROM analytics.fct_student_grades
    )
    
    SELECT 
      table_name,
      last_update,
      threshold,
      status,
      DATEDIFF('day', last_update, CURRENT_DATE) AS days_since_update
    FROM data_freshness
    WHERE status = 'STALE'
    ORDER BY days_since_update DESC

notify:
  email:
    recipients:
      - "data-team@school.edu"

# Send recovery notification when data becomes fresh
on_recover: true

# Re-notify if alert remains active
renotify: true
renotify_after: "4h"

intervals:
  duration: PT1H  # Check hourly intervals
  limit: 24       # Keep last 24 hours of history

timeout: "30s"
```

**Best Practices:**
- Set threshold based on pipeline schedule (e.g., 2 days for daily attendance)
- Include table name and days_since_update for debugging
- Use `on_recover: true` to confirm when data freshness is restored
- Adjust `renotify_after` to balance alert fatigue vs responsiveness

---

### Pattern 2: Resource Health Monitoring

**Use Case:** Monitor Rill project resources for reconciliation errors

```yaml
type: alert
display_name: "Pipeline Health Monitor"

refresh:
  cron: "*/10 * * * *"  # Check every 10 minutes (near-real-time)

# Query using resource_status to detect any project errors
data:
  resource_status:
    where_error: true  # Only include resources with errors

# Multi-channel notifications
notify:
  # Slack for team visibility
  slack:
    channels:
      - "#data-alerts"
    webhooks:
      - url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  
  # Email for permanent record
  email:
    recipients:
      - "platform-team@school.edu"

# Send recovery notification when all resources healthy
on_recover: true

# Re-notify if errors persist (moderate frequency)
renotify: true
renotify_after: "1h"

intervals:
  duration: PT15M  # Track 15-minute intervals
  limit: 96        # Keep last 24 hours (96 x 15min)

timeout: "30s"
```

**Best Practices:**
- Use `resource_status` for live monitoring (not SQL queries)
- Check frequently (every 10 minutes) for critical resources
- Send to both Slack (immediate) and email (permanent record)
- Use `on_recover: true` to confirm resolution
- Set `renotify_after` to avoid alert fatigue while maintaining awareness

---

### Pattern 3: dbt Test Failure Detection

**Use Case:** Alert when dbt tests fail during pipeline execution

```yaml
type: alert
display_name: "dbt Test Failure Detection"

refresh:
  cron: "0 */6 * * *"  # Every 6 hours (after pipeline runs)
  run_in_dev: false    # Don't run in dev mode

# Query using resource_status to detect failures
data:
  resource_status:
    where_error: true  # Only include resources with errors

notify:
  email:
    recipients:
      - "oncall@school.edu"
      - "data-engineering@school.edu"

# Send recovery notification when tests pass
on_recover: true

# Re-notify if failures persist (aggressive for critical issues)
renotify: true
renotify_after: "2h"

timeout: "1m"
```

**Best Practices:**
- Align refresh schedule with pipeline execution (e.g., every 6 hours)
- Use `run_in_dev: false` to avoid noisy alerts during development
- Send to oncall + engineering team for critical test failures
- Use shorter `renotify_after` (2h) for critical issues requiring immediate attention
- Increase timeout for long-running test queries

---

### Pattern 4: Threshold Monitoring

**Use Case:** Alert when metrics exceed expected ranges (e.g., attendance rate drops below 85%)

```yaml
type: alert
display_name: "Attendance Rate Threshold Alert"

refresh:
  cron: "0 8 * * 1-5"  # 8 AM weekdays (school days)
  time_zone: "America/Los_Angeles"

data:
  sql: |
    SELECT 
      school_id,
      school_name,
      attendance_rate,
      85.0 AS threshold,
      (85.0 - attendance_rate) AS gap
    FROM (
      SELECT 
        school_id,
        school_name,
        AVG(attendance_rate) AS attendance_rate
      FROM analytics.fct_attendance_daily
      WHERE attendance_date >= CURRENT_DATE - INTERVAL '7 days'
      GROUP BY school_id, school_name
    )
    WHERE attendance_rate < 85.0
    ORDER BY gap DESC

notify:
  email:
    recipients:
      - "principal@school.edu"
      - "attendance-coordinator@school.edu"

on_recover: true

renotify: false  # Don't spam - one alert per incident

timeout: "30s"
```

**Best Practices:**
- Use `time_zone` to run alerts in local school time
- Include threshold and gap in output for context
- Calculate averages over meaningful period (e.g., 7 days)
- Set `renotify: false` for awareness alerts (not critical incidents)
- Use cron schedules aligned with business hours

---

## Notification Channels

### Email Configuration

```yaml
notify:
  email:
    recipients:
      - "user1@example.com"
      - "user2@example.com"
      - "team-dl@example.com"
```

**Best Practices:**
- Use distribution lists for team notifications
- Separate oncall vs informational recipients
- Include at least 2 recipients for redundancy
- Avoid personal emails for production alerts

---

### Slack Configuration

```yaml
notify:
  slack:
    channels:
      - "#data-alerts"       # Public channel for visibility
      - "#platform-oncall"   # Oncall channel for critical issues
    webhooks:
      - url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
      - url: "https://hooks.slack.com/services/T11111111/B11111111/YYYYYYYYYYYYYYYYYYYY"
```

**Best Practices:**
- Use separate channels for different severity levels
- Include both public channels (visibility) and oncall channels (action)
- Use multiple webhooks for redundancy
- Test webhook URLs before deploying

**Creating Slack Webhooks:**
1. Go to https://api.slack.com/apps
2. Create new app → "Incoming Webhooks"
3. Activate incoming webhooks
4. Add new webhook to workspace
5. Select channel and copy webhook URL

---

### Generic Webhooks

```yaml
notify:
  webhooks:
    - url: "https://example.com/webhook/endpoint"
      headers:
        Authorization: "Bearer YOUR_TOKEN"
    - url: "https://pagerduty.com/integration/xxx/enqueue"
```

**Best Practices:**
- Use for PagerDuty, Opsgenie, custom integrations
- Include authentication headers if required
- Test webhook endpoints before production deployment
- Monitor webhook delivery failures

---

## Testing Alert Configurations

### Pre-Deployment Validation

```bash
# 1. Validate YAML syntax
yamllint rill_project/alerts/my_alert.yaml

# 2. Validate Rill schema
cd rill_project && rill project validate

# 3. Start Rill and check logs
cd rill_project && rill start --log-level debug

# 4. Look for reconciliation success
# Expected: "Reconciled resource name=my_alert type=Alert"
```

---

### Test Alert Query

```bash
# Test SQL query directly in DuckDB
duckdb oss_framework/data/oea.duckdb <<SQL
-- Copy SQL from alert data.sql field
SELECT * FROM analytics.fct_attendance_daily
WHERE attendance_date < CURRENT_DATE - INTERVAL '2 days';
SQL

# Expected: Query returns rows if condition met (alert would trigger)
# Expected: Query returns 0 rows if condition not met (alert silent)
```

---

### Test Webhook Integration

```bash
# Test Slack webhook manually
curl -X POST \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test alert from Rill"}'

# Expected: Message appears in Slack channel
```

---

### Trigger Alert Manually

```yaml
# Temporarily change cron to run immediately (for testing only)
refresh:
  cron: "* * * * *"  # Every minute (remove after testing!)

# Or use run_in_dev to test during development
refresh:
  run_in_dev: true  # WARNING: Sends real notifications!
```

**IMPORTANT:** Revert `run_in_dev: true` and frequent cron schedules after testing to avoid alert fatigue!

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Alert Fatigue

```yaml
# BAD: Too frequent checks
refresh:
  cron: "* * * * *"  # Every minute (960 alerts/day if condition met!)

# BAD: Too aggressive re-notification
renotify: true
renotify_after: "5m"  # Re-sends every 5 minutes
```

**Fix:** Match refresh frequency to data update frequency + buffer
```yaml
# GOOD: Aligned with pipeline schedule
refresh:
  cron: "0 */6 * * *"  # Every 6 hours (after pipeline runs)

# GOOD: Balanced re-notification
renotify: true
renotify_after: "2h"  # Reminder without spam
```

---

### ❌ Anti-Pattern 2: Noisy Development Alerts

```yaml
# BAD: Alerts trigger during local development
refresh:
  run_in_dev: true  # Sends notifications from dev environment!
```

**Fix:** Disable alerts in dev mode
```yaml
# GOOD: Production only
refresh:
  run_in_dev: false  # Default behavior
```

---

### ❌ Anti-Pattern 3: Missing Recovery Notifications

```yaml
# BAD: Only notified when problem starts, never when resolved
on_recover: false  # Default - no recovery notification
```

**Fix:** Enable recovery notifications for actionable alerts
```yaml
# GOOD: Know when issue is resolved
on_recover: true  # Confirm recovery
```

---

### ❌ Anti-Pattern 4: Insufficient Context in Alerts

```yaml
# BAD: Alert triggers but provides no actionable information
data:
  sql: "SELECT 1 WHERE (SELECT COUNT(*) FROM table) = 0"
  # Output: Single row with value "1" - no context!
```

**Fix:** Include diagnostic information in query output
```yaml
# GOOD: Alert includes context for debugging
data:
  sql: |
    SELECT 
      'table_name' AS table_name,
      COUNT(*) AS row_count,
      MAX(updated_at) AS last_update,
      'Expected at least 1000 rows' AS error_message
    FROM table
    WHERE COUNT(*) < 1000
```

---

### ❌ Anti-Pattern 5: Timeout Too Short for Complex Queries

```yaml
# BAD: Complex query times out before completing
data:
  sql: |
    SELECT * FROM large_table
    JOIN another_large_table ...
    -- Complex aggregation
timeout: "30s"  # Too short!
```

**Fix:** Increase timeout for complex queries
```yaml
# GOOD: Sufficient time for complex analytics
timeout: "2m"  # 2 minutes for complex query
```

---

## Alert Severity Levels

Organize alerts by severity to avoid alert fatigue:

### Critical (Immediate Action)
```yaml
# Production pipeline failures, data corruption
renotify: true
renotify_after: "30m"  # Aggressive re-notification
notify:
  email: ["oncall@school.edu"]
  slack:
    channels: ["#incidents"]
```

### High (Action Required)
```yaml
# Data freshness issues, threshold violations
renotify: true
renotify_after: "2h"  # Moderate re-notification
notify:
  email: ["data-team@school.edu"]
  slack:
    channels: ["#data-alerts"]
```

### Medium (Awareness)
```yaml
# Performance degradation, warning thresholds
renotify: false  # One notification per incident
notify:
  email: ["team-dl@school.edu"]
```

### Low (Informational)
```yaml
# Successful recoveries, scheduled summaries
on_fail: false   # Don't alert on failure
on_recover: true # Only alert on success
notify:
  email: ["team-dl@school.edu"]
```

---

## Production Checklist

Before deploying alert to production:

```
[ ] YAML syntax validated (yamllint)
[ ] Rill schema validated (rill project validate)
[ ] SQL query tested directly in DuckDB
[ ] Query returns expected rows when condition met
[ ] Query returns 0 rows when condition not met
[ ] Webhook URLs tested with curl
[ ] run_in_dev: false (no dev environment alerts)
[ ] refresh.cron aligned with pipeline schedule
[ ] renotify_after set to avoid alert fatigue
[ ] on_recover configured appropriately
[ ] timeout sufficient for query complexity
[ ] Recipients/channels confirmed correct
[ ] Alert deployed to rill_project/alerts/
[ ] Rill restarted to load new alert
[ ] Alert reconciliation successful (check logs)
[ ] Alert monitored for 24-48 hours (false positive check)
```

---

## Real-World Examples

### Example 1: Data Freshness Alert (Production)

**File:** `rill_project/alerts/data_freshness_alert.yaml`

```yaml
type: alert
display_name: "Data Freshness Alert - Analytics Tables"

refresh:
  cron: "*/30 * * * *"  # Every 30 minutes

data:
  sql: |
    WITH data_freshness AS (
      SELECT 
        'fct_attendance_daily' AS table_name,
        MAX(attendance_date) AS last_update,
        CURRENT_DATE - INTERVAL '2 days' AS threshold,
        CASE 
          WHEN MAX(attendance_date) < CURRENT_DATE - INTERVAL '2 days' 
          THEN 'STALE' 
          ELSE 'FRESH' 
        END AS status
      FROM analytics.fct_attendance_daily
    )
    SELECT * FROM data_freshness WHERE status = 'STALE'

notify:
  email:
    recipients:
      - "data-team@school.edu"

on_recover: true
renotify: true
renotify_after: "4h"

intervals:
  duration: PT1H
  limit: 24

timeout: "30s"
```

**Result:** 
- ✅ Triggers when attendance data older than 2 days
- ✅ Alerts every 4 hours until resolved
- ✅ Confirms recovery when data refreshed
- ✅ Zero parser errors in v0.82.1

---

### Example 2: Pipeline Health Monitor (Production)

**File:** `rill_project/alerts/pipeline_health.yaml`

```yaml
type: alert
display_name: "Pipeline Health Monitor"

refresh:
  cron: "*/10 * * * *"  # Every 10 minutes

data:
  resource_status:
    where_error: true

notify:
  slack:
    channels:
      - "#data-alerts"
    webhooks:
      - url: "https://hooks.slack.com/services/..."
  email:
    recipients:
      - "platform-team@school.edu"

on_recover: true
renotify: true
renotify_after: "1h"

intervals:
  duration: PT15M
  limit: 96

timeout: "30s"
```

**Result:**
- ✅ Monitors all Rill resources for errors
- ✅ Alerts to Slack + email for visibility
- ✅ Re-notifies every hour if errors persist
- ✅ Zero parser errors in v0.82.1

---

## Additional Resources

- **Official Rill Alert Docs**: https://docs.rilldata.com/reference/project-files/alerts
- **Rill Examples Repository**: https://github.com/rilldata/rill-examples
- **KNOWN_ISSUES.md**: Alert schema changes and resolutions
- **RILL_TROUBLESHOOTING.md**: Common alert errors and fixes
