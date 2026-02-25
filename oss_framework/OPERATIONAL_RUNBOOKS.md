# Operational Runbooks - Post-Launch Support

## Overview

Comprehensive operational procedures for managing the analytics platform in production. These runbooks are designed for 24/7 support operations.

## 1. Incident Response Runbook

### 1.1 Dashboard Not Loading

**Severity**: High  
**SLA**: 1 hour resolution

**Diagnosis**:
```bash
# Check Metabase pod status
kubectl get pods -n oea-production -l app=metabase
kubectl logs -f deployment/metabase -n oea-production

# Check database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never \
  -- psql -h postgres.oea-production -U oea_admin -d oea -c "SELECT 1;"

# Check DuckDB availability
kubectl get svc duckdb -n oea-production
```

**Common Causes & Solutions**:

| Symptom | Cause | Solution |
|---------|-------|----------|
| 502 Bad Gateway | Metabase crashed | `kubectl rollout restart deployment/metabase -n oea-production` |
| Empty dataset | dbt refresh failed | Check `dbt logs` for errors; manually re-run dbt |
| Slow load (>10s) | High database load | Check Prometheus for query latency; scale up pods if needed |
| Authentication error | Service down | Verify LDAP/OAuth connectivity |

**Resolution Steps**:
1. Identify affected users/dashboards (check application logs)
2. Determine if issue is Metabase or database
3. Check if data refresh is running (dbt CronJob)
4. Restart pods if needed: `kubectl rollout restart deployment/metabase`
5. Verify fix: Test dashboard load in browser
6. Document incident with timeline and root cause

**Escalation**:
- If not resolved in 30 min → page on-call database engineer
- If not resolved in 1 hour → page infrastructure lead

---

### 1.2 Data Quality Issues

**Severity**: Medium  
**SLA**: 4 hours resolution

**Detection**:
- Automated tests fail during dbt refresh
- Users report data doesn't match expected values
- Unusual distributions in risk scores
- Missing data for recent dates

**Diagnosis**:
```bash
# Check dbt test results
kubectl logs job/dbt-refresh-* -n oea-production | grep -A 5 "FAILED"

# Check data freshness
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea -c "
SELECT MAX(created_at) FROM v_chronic_absenteeism_risk;
SELECT COUNT(*) FROM raw_students WHERE DATE(created_at) = CURRENT_DATE;
"

# Check for duplicate records
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea -c "
SELECT student_id_hash, COUNT(*) FROM v_chronic_absenteeism_risk 
GROUP BY student_id_hash HAVING COUNT(*) > 1;
"
```

**Resolution Steps**:
1. Identify which view/table is affected
2. Check dbt logs for transformation errors
3. If source data issue: contact data collection team
4. If transformation error: 
   - Fix dbt model
   - Re-run: `kubectl create job -n oea-production dbt-manual --from=cronjob/dbt-refresh`
5. Verify data quality tests pass
6. Alert users once fixed

**Root Cause Analysis**:
- Did data format change in source system?
- Was dbt code modified recently?
- Are upstream dependencies healthy?
- Check git history: `git log --oneline oss_framework/dbt/models/`

---

### 1.3 High Query Latency

**Severity**: Medium  
**SLA**: 2 hours resolution

**Detection**:
- Dashboards slow to load (>5 seconds)
- Users reporting sluggish interface
- Prometheus alerts for high query time

**Diagnosis**:
```bash
# Check query performance metrics
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090
# Query: histogram_quantile(0.95, metabase_query_duration_seconds)

# Check database resource usage
kubectl top pods postgres-0 -n oea-production
kubectl exec -it postgres-0 -n oea-production -- \
  psql -U oea_admin -d oea -c "
    SELECT query, calls, mean_time 
    FROM pg_stat_statements 
    ORDER BY mean_time DESC LIMIT 10;
  "

# Check active connections
kubectl exec -it postgres-0 -n oea-production -- \
  psql -U oea_admin -d oea -c "SELECT * FROM pg_stat_activity;"
```

**Common Causes & Solutions**:

| Cause | Solution |
|-------|----------|
| dbt refresh running | Wait for completion; adjust refresh window |
| Missing indexes | Review query plan; add index if needed |
| High concurrent users | Scale Metabase: `kubectl scale deployment metabase --replicas=5` |
| Large table scan | Check if view needs optimization |
| Database memory pressure | Increase resource limits: `kubectl set resources` |

**Resolution Steps**:
1. Identify slow queries (use query logs)
2. Get execution plan: `EXPLAIN ANALYZE <query>`
3. If index missing: `CREATE INDEX ...`
4. If query inefficient: Optimize view/dbt model
5. If resource constrained: Scale up
6. Re-test query latency

---

### 1.4 dbt Refresh Failure

**Severity**: High  
**SLA**: 2 hours resolution

**Detection**:
- dbt CronJob fails (check Kubernetes events)
- Slack notification: "❌ dbt refresh failed"
- Data freshness warning (data >24h old)

**Diagnosis**:
```bash
# Check job status
kubectl get jobs -n oea-production | grep dbt

# View full logs
kubectl logs job/<job-name> -n oea-production

# Check dbt project
cd oss_framework/dbt
dbt debug --profiles-dir ~/.dbt

# Test specific model
dbt run --select <model-name> --profiles-dir ~/.dbt
```

**Common Errors & Solutions**:

```
ERROR: Database connection failed
  → Check database credentials
  → Verify network connectivity
  → Check if database is running: kubectl get statefulsets postgres

ERROR: Insufficient disk space
  → Check: kubectl top nodes
  → Clean up old backups
  → Expand PVC if needed

ERROR: dbt model parsing failed
  → Check YAML syntax in schema.yml
  → Verify references in upstream models
  → Run: dbt parse

ERROR: Test assertion failed
  → Review test definition
  → Check actual vs expected data
  → Decide if test is correct or data is incorrect
```

**Resolution Steps**:
1. Check logs for specific error message
2. Fix root cause (syntax, data, connectivity, etc.)
3. Re-run refresh: `kubectl create job -n oea-production dbt-manual --from=cronjob/dbt-refresh`
4. Monitor job: `kubectl logs job/dbt-manual -n oea-production -f`
5. Verify data freshness once complete
6. Document incident

---

## 2. Maintenance Procedures

### 2.1 Database Backup Verification

**Frequency**: Daily (automated), Manual weekly verification  
**Duration**: 15 minutes

```bash
#!/bin/bash
# Weekly backup verification script

echo "=== Backup Verification Report ==="
echo "Date: $(date)"

# List recent backups
echo ""
echo "Recent Backups:"
aws s3 ls s3://oea-backups/ --recursive --human-readable | tail -10

# Test restore procedure (dry-run)
echo ""
echo "Testing backup integrity..."
LATEST_BACKUP=$(aws s3 ls s3://oea-backups/ | tail -1 | awk '{print $NF}')
aws s3 cp s3://oea-backups/$LATEST_BACKUP /tmp/
gunzip -t /tmp/$LATEST_BACKUP && echo "✅ Backup is valid" || echo "❌ Backup corrupted"

# Check backup age
echo ""
echo "Backup Freshness:"
find /var/backups -name "oea_backup_*.sql.gz" -mtime -1 | wc -l | xargs echo "Backups in last 24h:"

echo ""
echo "=== Verification Complete ==="
```

### 2.2 Kubernetes Health Check

**Frequency**: 4x daily  
**Duration**: 10 minutes

```bash
#!/bin/bash
# Daily health check script

echo "=== Production Health Check ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

# Pod status
echo "POD STATUS:"
kubectl get pods -n oea-production --no-headers | grep -v Running && echo "⚠️ Non-running pods detected" || echo "✅ All pods running"

# Disk usage
echo ""
echo "DISK USAGE:"
kubectl exec -it postgres-0 -n oea-production -- df -h | grep -E "sda|Filesystem"

# Database connections
echo ""
echo "DATABASE CONNECTIONS:"
CONN_COUNT=$(kubectl exec -it postgres-0 -n oea-production -- \
  psql -U oea_admin -d oea -t -c "SELECT count(*) FROM pg_stat_activity;")
echo "Active connections: $CONN_COUNT (Target: <50)"

# Memory usage
echo ""
echo "MEMORY USAGE:"
kubectl top pods -n oea-production --no-headers | sort -k3 -nr | head -5

# Network issues
echo ""
echo "NETWORK STATUS:"
kubectl get endpoints -n oea-production

# Recent errors
echo ""
echo "RECENT ERRORS (Last 10 min):"
kubectl logs -n oea-production --all-containers=true --timestamps=true \
  --since=10m | grep -i error | tail -5

echo ""
echo "=== Health Check Complete ==="
```

### 2.3 Monthly Maintenance Window

**Frequency**: Last Sunday each month, 2 AM UTC  
**Duration**: 1-2 hours  
**Downtime**: ~30 minutes (planned)

**Procedure**:

```bash
#!/bin/bash
# Monthly maintenance script

set -e

MAINTENANCE_START=$(date -Iseconds)
echo "📋 Starting monthly maintenance at $MAINTENANCE_START"

# 1. Database maintenance
echo "1️⃣ Running database maintenance..."
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea << EOF
VACUUM ANALYZE;
REINDEX DATABASE oea;
EOF

# 2. Update Kubernetes manifests
echo "2️⃣ Checking for manifest updates..."
git pull origin main oss_framework/k8s/
kubectl apply -f oss_framework/k8s/ --dry-run=client -o yaml | kubectl apply -f -

# 3. Backup before updates
echo "3️⃣ Creating pre-update backup..."
kubectl create job -n oea-production db-backup-pre-update --from=cronjob/db-backup
kubectl wait --for=condition=complete job/db-backup-pre-update -n oea-production --timeout=1h

# 4. Update container images (rolling update)
echo "4️⃣ Updating container images..."
kubectl set image deployment/metabase \
  metabase=metabase/metabase:latest -n oea-production

# 5. Run dbt refresh
echo "5️⃣ Running dbt refresh..."
kubectl create job -n oea-production dbt-manual --from=cronjob/dbt-refresh
kubectl wait --for=condition=complete job/dbt-manual -n oea-production --timeout=2h

# 6. Verify system health
echo "6️⃣ Verifying system health..."
./scripts/health-checks.sh

# 7. Cleanup old resources
echo "7️⃣ Cleaning up old resources..."
kubectl delete job -n oea-production -l app=dbt-manual --all-failed-to-clean=true

MAINTENANCE_END=$(date -Iseconds)
echo "✅ Maintenance complete at $MAINTENANCE_END"
echo "Duration: $(( ($(date +%s) - $(date -d $MAINTENANCE_START +%s)) / 60 )) minutes"

# 8. Send notification
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"✅ Monthly maintenance completed successfully\"}" \
  $SLACK_WEBHOOK_URL
```

---

## 3. Performance Tuning

### 3.1 Slow Dashboard Performance

**Symptoms**: Dashboards taking >5 seconds to load

**Optimization Steps**:

```bash
# 1. Identify slow queries
kubectl port-forward -n oea-production svc/metabase 3000:3000
# Access Metabase admin → Performance → Query Analysis

# 2. Analyze query plan
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea << EOF
EXPLAIN (ANALYZE, VERBOSE) 
SELECT * FROM v_chronic_absenteeism_risk 
WHERE school_id = 101 LIMIT 100;
EOF

# 3. Check index effectiveness
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

# 4. Add missing indexes
CREATE INDEX idx_chronic_school_id ON main_analytics.v_chronic_absenteeism_risk (school_id);
ANALYZE;

# 5. Monitor improvement
# Watch Prometheus metric: metabase_query_duration_seconds
```

### 3.2 High Memory Usage

**Symptoms**: Metabase using >3GB memory, slow queries

**Optimization Steps**:

```bash
# 1. Check memory usage by pod
kubectl top pods -n oea-production

# 2. Adjust JVM heap size
kubectl set env deployment/metabase \
  JAVA_TOOL_OPTIONS="-Xmx2g -Xms1g" \
  -n oea-production

# 3. Clear query cache
# Via Metabase admin: Admin → Settings → Caching → Clear cache

# 4. Scale horizontally
kubectl scale deployment metabase --replicas=5 -n oea-production

# 5. Monitor improvement
kubectl top pods -n oea-production -w
```

---

## 4. Data Quality Monitoring

### 4.1 Daily Data Quality Checklist

```bash
#!/bin/bash
# Run daily after dbt refresh

echo "=== Data Quality Report ==="

# 1. Check record counts
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea << EOF
SELECT 'raw_students' as table_name, COUNT(*) as record_count FROM raw_students
UNION ALL SELECT 'raw_attendance', COUNT(*) FROM raw_attendance
UNION ALL SELECT 'v_chronic_absenteeism_risk', COUNT(*) FROM v_chronic_absenteeism_risk;
EOF

# 2. Check for nulls in key columns
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea << EOF
SELECT COUNT(*) as null_key_columns
FROM v_chronic_absenteeism_risk
WHERE student_key IS NULL OR school_id IS NULL;
EOF

# 3. Check risk score distribution
kubectl exec -it postgres-0 -n oea-production -- psql -U oea_admin -d oea << EOF
SELECT 
  ROUND(chronic_absenteeism_risk_score / 10) * 10 as score_range,
  COUNT(*) as count
FROM v_chronic_absenteeism_risk
GROUP BY ROUND(chronic_absenteeism_risk_score / 10) * 10
ORDER BY score_range;
EOF

# 4. Check data freshness
HOURS_OLD=$(( ($(date +%s) - $(date -d "$(
  kubectl exec -it postgres-0 -n oea-production -- \
  psql -U oea_admin -d oea -t -c \
  "SELECT MAX(created_at) FROM v_chronic_absenteeism_risk"
)" +%s)) / 3600 ))

if [ $HOURS_OLD -gt 24 ]; then
  echo "⚠️ WARNING: Data is $HOURS_OLD hours old"
else
  echo "✅ Data is current ($HOURS_OLD hours old)"
fi
```

---

## 5. On-Call Procedures

### 5.1 On-Call Escalation

```
TIER 1: Help Desk (1st response, 15 min SLA)
├─ Troubleshoot common issues
├─ Reset passwords, clear cache
└─ Escalate to Tier 2 if unresolved

TIER 2: Data Engineering (1 hour SLA)
├─ Diagnose system issues
├─ Check dbt logs, data quality
├─ Fix queries or models
└─ Escalate to Tier 3 if critical

TIER 3: Infrastructure (1 hour SLA)
├─ Kubernetes cluster health
├─ Database connectivity
├─ Resource scaling
└─ Incident commander decides escalation

INCIDENT COMMANDER:
└─ Called for Critical/P1 issues
    - Dashboard down for >30 min
    - Data incorrect/missing
    - Security incident
```

### 5.2 Incident Communication Template

```
Subject: [INCIDENT] Analytics Platform - [Issue Summary]
Severity: [CRITICAL/HIGH/MEDIUM/LOW]
Status: [INVESTIGATING/IDENTIFIED/MITIGATING/RESOLVED]

IMPACT:
- Affected users: [number]
- Affected dashboards: [list]
- Duration: [start time to now]

ROOT CAUSE:
[Once identified]

MITIGATION:
[Actions being taken]

ETA:
[Estimated time to resolution]

Next Update: [time in minutes]
```

---

## 6. Disaster Recovery

### 6.1 Database Recovery from Backup

**RTO**: 4 hours | **RPO**: 1 day

```bash
#!/bin/bash
# Database recovery procedure

set -e

BACKUP_FILE=$1  # e.g., oea_backup_20260127_030000.sql.gz

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

echo "🔄 Starting database recovery from: $BACKUP_FILE"

# 1. Download backup
aws s3 cp s3://oea-backups/$BACKUP_FILE /tmp/

# 2. Stop applications
kubectl scale deployment metabase --replicas=0 -n oea-production

# 3. Restore database
gunzip < /tmp/$BACKUP_FILE | \
  kubectl exec -i postgres-0 -n oea-production -- \
  psql -U oea_admin

# 4. Run integrity checks
kubectl exec -it postgres-0 -n oea-production -- \
  psql -U oea_admin -d oea -c "SELECT COUNT(*) FROM raw_students;"

# 5. Restart applications
kubectl scale deployment metabase --replicas=3 -n oea-production

# 6. Verify health
./scripts/health-checks.sh

echo "✅ Database recovery complete"
```

---

## 7. Reference Information

### 7.1 Key Contacts

```
HELP DESK:
  Email: helpdesk@yourdomain.com
  Phone: 1-888-OEA-HELP
  Hours: 7 AM - 6 PM weekdays

ON-CALL ENGINEER:
  Page: https://pagerduty.com/incidents
  Escalation: ops-lead@yourdomain.com

INCIDENT COMMANDER:
  Name: [CIO or Data Director]
  Phone: [phone]
  Email: [email]
```

### 7.2 Useful Commands

```bash
# View logs
kubectl logs -f deployment/metabase -n oea-production
kubectl logs -f job/dbt-refresh -n oea-production

# Port forwarding
kubectl port-forward svc/postgres 5432:5432 -n oea-production
kubectl port-forward svc/metabase 3000:3000 -n oea-production
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Execute shell in pod
kubectl exec -it postgres-0 -n oea-production -- bash
kubectl exec -it deployment/metabase -n oea-production -- sh

# View resource usage
kubectl top nodes
kubectl top pods -n oea-production

# Describe resource issues
kubectl describe pod <pod-name> -n oea-production
kubectl describe statefulset postgres -n oea-production
```

---

## For More Information

- Production Deployment Guide: `PRODUCTION_DEPLOYMENT.md`
- Monitoring Setup: `oss_framework/monitoring/README.md`
- dbt Documentation: `oss_framework/dbt/dbt_project.yml`
- Kubernetes Manifests: `oss_framework/k8s/`
