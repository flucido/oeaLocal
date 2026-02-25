# Metabase Troubleshooting Guide

## Overview

This guide covers common issues encountered during Metabase setup and dashboard creation for the openedDataEstate OSS Framework. Use this guide when things don't work as expected.

---

## Quick Diagnostic Commands

Run these first when troubleshooting any issue:

```bash
# Check if containers are running
docker ps | grep metabase

# Check container health
docker inspect oss-metabase | grep -A 10 "Health"

# Check logs
docker logs --tail 100 oss-metabase

# Test API health
curl http://localhost:3000/api/health

# Test database file access
docker exec oss-metabase ls -lh /data/oea.duckdb

# Check port availability
lsof -i :3000
```

---

## Issue #1: Cannot Access Metabase UI

### Symptom
- Browser shows "Connection refused" at `http://localhost:3000`
- Or: "This site can't be reached"

### Diagnostic Steps

**1. Check if container is running:**
```bash
docker ps | grep oss-metabase
```

**Expected output:**
```
oss-metabase   Up 5 minutes (healthy)   0.0.0.0:3000->3000/tcp
```

**If NOT running:**
```bash
docker ps -a | grep oss-metabase   # Check if exited
docker logs oss-metabase           # Check why it exited
```

**2. Check health status:**
```bash
docker inspect oss-metabase | grep -A 5 "Health"
```

**Expected:** `"Status": "healthy"`

**If "unhealthy" or "starting":**
- Wait 2-3 minutes (startup time)
- Check logs: `docker logs -f oss-metabase`

**3. Verify port binding:**
```bash
lsof -i :3000
```

**Expected:** Shows `docker-pr` (Docker proxy)

**If nothing returned:**
- Port mapping failed
- Check `docker-compose.yml` ports section

### Solutions

**Solution A: Container not running**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d
docker logs -f oss-metabase   # Watch for "Metabase Initialization COMPLETE"
```

**Solution B: Port conflict**
```bash
# Find what's using port 3000
lsof -i :3000 | grep LISTEN

# Option 1: Stop conflicting process
kill -9 <PID>

# Option 2: Change Metabase port
# Edit docker-compose.yml: ports: "3001:3000"
docker-compose down && docker-compose up -d
```

**Solution C: Container keeps restarting**
```bash
# Check exit code
docker inspect oss-metabase | grep -A 5 "State"

# Common causes:
# - Exit code 137: Out of memory → Increase JAVA_OPTS -Xmx
# - Exit code 1: Configuration error → Check environment variables
```

**Solution D: Firewall/network issue**
```bash
# Test from inside container
docker exec oss-metabase curl -f http://localhost:3000/api/health

# If this works but browser doesn't: Check macOS firewall settings
```

---

## Issue #2: Database Connection Failed

### Symptom
- Metabase UI loads, but "Cannot connect to database"
- Or: Database appears in list but queries fail
- Or: "DuckDB" not available in database type dropdown

### Diagnostic Steps

**1. Verify DuckDB file exists:**
```bash
# On host
ls -lh /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# In container
docker exec oss-metabase ls -lh /data/oea.duckdb
```

**Expected:** File exists, ~24MB, readable

**2. Check DuckDB driver loaded:**
```bash
docker logs oss-metabase | grep -i duckdb
```

**Expected:** 
```
Loaded plugin: DuckDB (duckdb.metabase-driver.jar)
```

**3. Test direct DuckDB connection:**
```bash
docker exec oss-metabase \
  java -cp /plugins/duckdb.metabase-driver.jar \
  -jar /home/metabase/metabase.jar \
  -c "SELECT 1" /data/oea.duckdb
```

**If this fails:** DuckDB driver or database issue

### Solutions

**Solution A: DuckDB file not found**
```bash
# Check volume mount in docker-compose.yml
cat oss_framework/deployment/metabase/docker-compose.yml | grep -A 2 "volumes:"

# Expected:
# - ../../data:/data

# If wrong path: Fix and restart
docker-compose down && docker-compose up -d
```

**Solution B: DuckDB driver not loaded**
```bash
# Check if driver file exists
ls -lh oss_framework/deployment/metabase/plugins/duckdb.metabase-driver.jar

# If missing: Download driver
cd oss_framework/deployment/metabase/plugins
curl -L -O https://github.com/motherduckdb/metabase_duckdb_driver/releases/download/1.4.3.1/duckdb.metabase-driver.jar

# Restart container
docker-compose restart
```

**Solution C: Permission denied**
```bash
# Check file permissions
ls -l /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# If not readable: Fix permissions
chmod 644 /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Or run container as root (already configured in docker-compose.yml)
# user: "0:0"
```

**Solution D: Wrong connection settings**

In Metabase UI (Admin → Databases → Edit):
- **Database type:** DuckDB (not "Generic SQL" or "PostgreSQL")
- **Database path:** `/data/oea.duckdb` (not `/Users/.../oea.duckdb`)
- **Read-only:** ✅ Checked

**Solution E: DuckDB database corrupted**
```bash
# Test with DuckDB CLI
docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
  duckdb/duckdb:latest /data/oea.duckdb \
  "SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;"

# If this fails: Regenerate database
cd /Users/flucido/projects/openedDataEstate/oss_framework
python scripts/run_dbt_build.py --stage 3
```

---

## Issue #3: Dashboard Creation Script Fails

### Symptom
- `create-dashboards-api.py` exits with error
- Or: Partial dashboard creation (some dashboards missing)
- Or: Authentication failed

### Diagnostic Steps

**1. Check credentials:**
```bash
echo $METABASE_EMAIL
echo $METABASE_PASSWORD   # Should not be empty
```

**2. Test authentication manually:**
```bash
curl -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@example.com", "password": "your-password"}'
```

**Expected:** Returns session token JSON

**3. Check script logs:**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
python3 create-dashboards-api.py 2>&1 | tee dashboard-creation.log
```

### Solutions

**Solution A: Missing credentials**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add credentials
nano .env

# Export variables
export $(cat .env | xargs)

# Verify
echo $METABASE_EMAIL
echo $METABASE_PASSWORD
```

**Solution B: Wrong port**
```bash
# Check script targets correct port
grep "METABASE_URL" create-dashboards-api.py

# Expected: http://localhost:3000 (not 3001)
# If wrong: Already fixed in previous session
```

**Solution C: Authentication failed**

**Possible causes:**
1. Admin account not created yet
   - **Fix:** Access `http://localhost:3000` and complete setup wizard

2. Wrong password
   - **Fix:** Reset password via Metabase UI (Settings → Admin → People)

3. Account locked (too many failed attempts)
   - **Fix:** Wait 15 minutes, or restart Metabase

**Solution D: Database not connected**
```bash
# Verify database is connected in Metabase
curl -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  http://localhost:3000/api/database

# Should return list with "OSS Analytics" database
# If empty: Connect database first (see Issue #2)
```

**Solution E: Network timeout**
```bash
# Increase timeout in script (if needed)
# Edit create-dashboards-api.py:
# timeout=30  (increase from 10)

# Or check Metabase performance:
docker stats oss-metabase   # Watch CPU/Memory
```

---

## Issue #4: Dashboards Created but Show "No Results"

### Symptom
- Dashboards appear in Metabase
- Visualizations are empty or show "No results"
- Or: "Error: Table not found"

### Diagnostic Steps

**1. Check if schema exists:**
```bash
docker exec oss-metabase \
  java -jar /home/metabase/metabase.jar \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main_main_analytics';" \
  /data/oea.duckdb
```

**Expected:** 5 analytics views listed

**2. Check view contents:**
```bash
docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
  duckdb/duckdb:latest /data/oea.duckdb \
  "SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;"
```

**Expected:** 3400 rows

**3. Check query syntax in dashboard:**
```bash
# In Metabase UI:
# - Open dashboard
# - Click on visualization
# - Click "..." → View query
# - Look for schema prefix
```

**Expected:** Queries should use `main_main_analytics.` prefix

### Solutions

**Solution A: Missing schema prefix**

**Problem:** Old queries used table names without schema prefix

**Fix:** Dashboards were recreated with correct prefix in previous session
```bash
# Verify queries have schema prefix
grep -r "FROM v_" create-dashboards-api.py

# Should show: FROM main_main_analytics.v_*
```

**If still broken:** Delete and recreate dashboards
```bash
python3 create-dashboards-api.py
# Script automatically cleans up old dashboards first
```

**Solution B: Views don't exist**
```bash
# Regenerate analytics views
cd /Users/flucido/projects/openedDataEstate/oss_framework
python scripts/run_dbt_build.py --stage 3

# Wait for completion (~5-10 minutes)
# Then refresh Metabase database schema:
# Admin → Databases → OSS Analytics → "Sync database schema now"
```

**Solution C: Database sync needed**

In Metabase UI:
1. Settings → Admin → Databases
2. Find "OSS Analytics"
3. Click "Sync database schema now"
4. Wait 30-60 seconds
5. Return to dashboard and refresh

**Solution D: Query timeout**

For slow queries:
1. Settings → Admin → Databases → OSS Analytics
2. Advanced options → "Query timeout" → Increase to 60 seconds
3. Save changes
4. Re-run query

---

## Issue #5: Slow Dashboard Performance

### Symptom
- Dashboards take > 10 seconds to load
- Queries timeout
- Metabase UI is sluggish

### Diagnostic Steps

**1. Check container resources:**
```bash
docker stats oss-metabase --no-stream
```

**Look for:**
- **High CPU (> 90%):** Queries are expensive
- **High memory (> 1.8GB):** Close to heap limit
- **Memory increasing:** Potential memory leak

**2. Test query performance directly:**
```bash
time docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
  duckdb/duckdb:latest /data/oea.duckdb \
  "SELECT * FROM main_main_analytics.v_chronic_absenteeism_risk LIMIT 100;"
```

**Expected:** < 1 second

**3. Check query plan:**
```sql
-- In Metabase SQL query editor:
EXPLAIN SELECT * FROM main_main_analytics.v_chronic_absenteeism_risk;
```

### Solutions

**Solution A: Increase Java heap memory**

Edit `docker-compose.yml`:
```yaml
environment:
  JAVA_OPTS: "-Xmx4g -Xms1g"   # Changed from 2g to 4g
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

**Solution B: Enable query caching**

In Metabase UI:
1. Settings → Admin → Caching
2. Enable "Cache question results"
3. Set TTL: 10 minutes
4. Save changes

**Solution C: Optimize queries**

**For slow queries:**
- Add LIMIT clause for exploration
- Use aggregations (COUNT, AVG) instead of SELECT *
- Filter by indexed columns (student_id_hash, date)

**Solution D: Prewarm cache**

Run queries before presenting to users:
```bash
# Script to prewarm all 5 views
for view in v_chronic_absenteeism_risk v_wellbeing_risk_profiles v_equity_outcomes_by_demographics v_class_section_comparison v_performance_correlations; do
  echo "Prewarming $view..."
  docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
    duckdb/duckdb:latest /data/oea.duckdb \
    "SELECT COUNT(*) FROM main_main_analytics.$view;"
done
```

**Solution E: Database needs optimization**

Contact dev team to:
- Add indexes to DuckDB views
- Materialize aggregations
- Partition large tables

---

## Issue #6: Two Metabase Instances - Confusion

### Symptom
- Trying to access wrong instance (port 3001 instead of 3000)
- Dashboards exist in one instance but not the other
- Database connected in one but not the other

### Diagnostic Steps

**1. Check which instances are running:**
```bash
docker ps --format "{{.Names}}: {{.Ports}}" | grep metabase
```

**Expected:**
```
oss-metabase: 0.0.0.0:3000->3000/tcp
sis-metabase: 0.0.0.0:3001->3000/tcp   (optional)
```

**2. Check which instance you're accessing:**
```bash
# Check browser URL
# Should be: http://localhost:3000 (not 3001)
```

**3. Check database connection in each:**
```bash
# oss-metabase (port 3000)
curl http://localhost:3000/api/database

# sis-metabase (port 3001)  
curl http://localhost:3001/api/database
```

### Solutions

**Solution A: Use oss-metabase only (RECOMMENDED)**

**Stop using sis-metabase:**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework
# Edit docker-compose.yml and comment out sis-metabase service
# Or just stop it:
docker stop sis-metabase
```

**Always use:** `http://localhost:3000`

**Solution B: Clearly label instances**

In each Metabase UI:
1. Settings → Admin → Settings → General
2. Site Name:
   - Port 3000: "OSS Analytics (PRIMARY)"
   - Port 3001: "Legacy Metabase (DO NOT USE)"

**Solution C: Document which to use**

**Already documented:**
- `SETUP-STATE.md` → Recommendation section
- `SCRIPTS-CONSOLIDATION.md` → Port configuration
- `DOCKER-SETUP.md` → Comparison table

**Refer users to these docs when confused**

---

## Issue #7: Forgot Admin Password

### Symptom
- Cannot log into Metabase
- Password reset email not working
- No access to admin account

### Solutions

**Solution A: Reset via H2 database (ADVANCED)**

⚠️ **This requires H2 tools and SQL knowledge**

```bash
# Stop Metabase
docker-compose down

# Install H2 tools (if not installed)
brew install h2

# Access H2 database (requires H2 Console)
# This is complex - not recommended
```

**Solution B: Reset by recreating volume (DESTRUCTIVE)**

⚠️ **This deletes ALL data: users, dashboards, queries**

```bash
# Backup first (IMPORTANT)
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/metabase-backup-$(date +%Y%m%d).tar.gz /data

# Remove volume (destroys data)
docker-compose down
docker volume rm oss-metabase-data

# Recreate
docker-compose up -d

# Complete setup wizard again at http://localhost:3000
```

**Solution C: Create new admin via API (if one admin exists)**

If you can log in with any admin account:
1. Settings → Admin → People
2. Add new admin user
3. Demote old admin to viewer (optional)

---

## Issue #8: Container Keeps Restarting

### Symptom
- `docker ps` shows container restarting constantly
- Container status: "Restarting (1) 3 seconds ago"

### Diagnostic Steps

**1. Check restart count:**
```bash
docker ps -a | grep oss-metabase
# LOOK FOR: "Restarting (5)"  ← number keeps increasing
```

**2. Check logs:**
```bash
docker logs --tail 100 oss-metabase
```

**3. Check exit code:**
```bash
docker inspect oss-metabase | grep -A 5 "State"
# LOOK FOR: "ExitCode": 137 (out of memory)
#           "ExitCode": 1   (configuration error)
```

### Solutions

**Solution A: Out of memory (Exit code 137)**

**Increase heap size:**

Edit `docker-compose.yml`:
```yaml
environment:
  JAVA_OPTS: "-Xmx4g -Xms1g"
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

**Solution B: Configuration error (Exit code 1)**

**Check for typos in docker-compose.yml:**
```bash
# Validate YAML syntax
docker-compose config

# If errors: Fix them and restart
```

**Common mistakes:**
- Missing quotes around strings
- Wrong indentation
- Invalid environment variable names

**Solution C: Port already in use**

```bash
# Find what's using port 3000
lsof -i :3000

# Option 1: Stop conflicting process
kill -9 <PID>

# Option 2: Change port
# Edit docker-compose.yml: ports: "3001:3000"
```

**Solution D: Database locked**

```bash
# Check if another process has H2 database open
lsof | grep metabase.db

# If found: Stop that process

# Or remove lock file (CAREFUL)
docker run --rm -v oss-metabase-data:/data \
  alpine rm /data/metabase.db.lock
```

---

## Issue #9: Dashboards Suddenly Disappeared

### Symptom
- Dashboards existed yesterday, gone today
- Or: Blank Metabase UI (no collections)

### Diagnostic Steps

**1. Check if logged into correct instance:**
```bash
# Check browser URL
# Should be: http://localhost:3000
```

**2. Check if database connection exists:**
```bash
curl http://localhost:3000/api/database
# Should return OSS Analytics database
```

**3. Check if volume was deleted:**
```bash
docker volume ls | grep metabase
# Should show: oss-metabase-data
```

### Solutions

**Solution A: Wrong instance**

Switch to port 3000: `http://localhost:3000`

**Solution B: Wrong user account**

Dashboards might be in a collection you don't have access to:
1. Log in as admin
2. Settings → Admin → People → Check user permissions
3. Collections → Share collections with appropriate users

**Solution C: Volume was deleted**

**If backup exists:**
```bash
# Restore from backup
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/metabase-backup-20260127.tar.gz -C /

# Restart
docker-compose restart
```

**If no backup:**
- Dashboards must be recreated
- Run `create-dashboards-api.py` again

---

## Issue #10: Cannot Install DuckDB Driver

### Symptom
- "DuckDB" not appearing in database type dropdown
- Or: Manual driver installation fails

### Diagnostic Steps

**1. Check if driver file exists:**
```bash
ls -lh oss_framework/deployment/metabase/plugins/duckdb.metabase-driver.jar
```

**Expected:** 77MB file

**2. Check if plugins directory mounted:**
```bash
docker inspect oss-metabase | grep -A 10 "Mounts"
# Should show: ./plugins:/plugins
```

**3. Check Metabase logs for driver loading:**
```bash
docker logs oss-metabase | grep -i plugin
```

### Solutions

**Solution A: Driver missing**

Download driver:
```bash
cd oss_framework/deployment/metabase/plugins
curl -L -O https://github.com/motherduckdb/metabase_duckdb_driver/releases/download/1.4.3.1/duckdb.metabase-driver.jar

# Verify download
ls -lh duckdb.metabase-driver.jar
# Should be ~77MB
```

Restart Metabase:
```bash
docker-compose restart
```

**Solution B: Plugin directory not mounted**

Edit `docker-compose.yml`:
```yaml
volumes:
  - ./plugins:/plugins:ro
```

Restart:
```bash
docker-compose down && docker-compose up -d
```

**Solution C: Driver version incompatibility**

Check Metabase version:
```bash
docker exec oss-metabase java -jar /home/metabase/metabase.jar version
```

Download compatible driver:
- Metabase v0.50+: Driver v1.4.3+
- Metabase v0.49: Driver v1.3.0+

**Solution D: Use custom image**

The custom Dockerfile already includes driver:
```bash
cd oss_framework/deployment/metabase
docker build -t metabase-duckdb:latest .
docker-compose down && docker-compose up -d
```

---

## Common Error Messages Decoded

### Error: "Unable to connect to Metabase server"

**Cause:** Container not running or health check failing

**Fix:**
```bash
docker ps | grep oss-metabase
docker logs oss-metabase
docker-compose restart
```

---

### Error: "Database connection failed: No such table"

**Cause:** Schema prefix missing in query

**Fix:** Queries must use `main_main_analytics.view_name`

**Verify:**
```sql
-- Wrong:
SELECT * FROM v_chronic_absenteeism_risk;

-- Correct:
SELECT * FROM main_main_analytics.v_chronic_absenteeism_risk;
```

---

### Error: "Authentication failed: Wrong username or password"

**Cause:** Invalid credentials or account not created yet

**Fix:**
1. Access `http://localhost:3000`
2. If shows setup wizard: Complete setup first
3. If shows login: Check credentials
4. If locked out: Wait 15 minutes or reset password

---

### Error: "Port 3000 is already allocated"

**Cause:** Another container using port 3000

**Fix:**
```bash
# Find conflicting container
docker ps | grep 3000

# Stop it
docker stop <container-name>

# Or change Metabase port
# Edit docker-compose.yml: ports: "3001:3000"
```

---

### Error: "OutOfMemoryError: Java heap space"

**Cause:** Java heap too small for workload

**Fix:**
Edit `docker-compose.yml`:
```yaml
JAVA_OPTS: "-Xmx4g -Xms1g"   # Increase from 2g
```

---

### Error: "Unable to read database file"

**Cause:** DuckDB file not accessible or corrupted

**Fix:**
```bash
# Check file exists
ls -lh oss_framework/data/oea.duckdb

# Check permissions
chmod 644 oss_framework/data/oea.duckdb

# Test file integrity
docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
  duckdb/duckdb:latest /data/oea.duckdb \
  "SELECT 1;"

# If corrupted: Regenerate
python scripts/run_dbt_build.py --stage 3
```

---

## Preventive Maintenance

### Weekly Tasks

**1. Backup Metabase metadata:**
```bash
docker run --rm -v oss-metabase-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/metabase-$(date +%Y%m%d).tar.gz /data
```

**2. Check container health:**
```bash
docker ps | grep metabase
docker stats oss-metabase --no-stream
```

**3. Review logs for errors:**
```bash
docker logs --tail 100 oss-metabase | grep -i error
```

### Monthly Tasks

**1. Update Metabase:**
```bash
cd oss_framework/deployment/metabase
docker-compose pull
docker-compose down && docker-compose up -d
```

**2. Clean up old backups:**
```bash
# Keep only last 4 backups
ls -t backups/metabase-*.tar.gz | tail -n +5 | xargs rm
```

**3. Review dashboard performance:**
- Check query execution times
- Optimize slow queries
- Add caching where needed

---

## Getting Help

### Before Asking for Help

Run these commands and include output:
```bash
# System info
docker --version
docker-compose --version

# Container status
docker ps -a | grep metabase

# Health check
curl http://localhost:3000/api/health

# Last 50 log lines
docker logs --tail 50 oss-metabase

# Volume status
docker volume ls | grep metabase

# Metabase version
docker exec oss-metabase java -jar /home/metabase/metabase.jar version
```

### Support Resources

- **Project Docs:** `oss_framework/deployment/metabase/README.md`
- **Docker Setup:** `oss_framework/deployment/metabase/DOCKER-SETUP.md`
- **Metabase Docs:** https://www.metabase.com/docs/latest/
- **Metabase Forum:** https://discourse.metabase.com/

---

## Troubleshooting Checklist

When nothing works, run through this systematically:

```
[ ] 1. Container is running: docker ps | grep oss-metabase
[ ] 2. Container is healthy: docker inspect oss-metabase | grep Health
[ ] 3. Port is accessible: curl http://localhost:3000/api/health
[ ] 4. Database file exists: docker exec oss-metabase ls /data/oea.duckdb
[ ] 5. Driver is loaded: docker logs oss-metabase | grep -i duckdb
[ ] 6. Volume is mounted: docker inspect oss-metabase | grep Mounts
[ ] 7. No port conflicts: lsof -i :3000
[ ] 8. Sufficient memory: docker stats oss-metabase --no-stream
[ ] 9. Recent backups exist: ls -lh backups/
[ ] 10. Correct URL used: http://localhost:3000 (not 3001)
```

If all checks pass but still broken → Contact dev team with diagnostic output

---

**Last Updated:** 2026-01-27  
**Covers:** Metabase v0.51.4, DuckDB driver 1.4.3.1, Docker Compose 3.8
