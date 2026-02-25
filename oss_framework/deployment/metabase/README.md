# Metabase BI Platform - OSS Student Analytics

## Overview

Metabase is an open-source business intelligence platform that provides a user-friendly interface for querying, visualizing, and sharing data from the OSS Framework analytics database. This deployment connects Metabase to the DuckDB analytics database containing student wellbeing and performance data.

**Key Features:**
- 🔍 **Interactive SQL queries** - Write queries or use visual query builder
- 📊 **Customizable dashboards** - Create real-time analytics dashboards
- 🎯 **Drill-down analytics** - Click to explore detailed data
- 🔒 **Self-hosted** - Complete data control within district infrastructure
- 🚀 **Fast** - Optimized for analytical workloads with DuckDB

## Architecture

```
┌─────────────────────┐
│   Web Browser       │
│  (Port 3000)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Metabase          │
│   (Docker)          │
│   - H2 metadata DB  │
│   - User auth       │
└──────────┬──────────┘
           │ read-only
           ▼
┌─────────────────────┐
│   DuckDB Database   │
│   oea.duckdb (24MB) │
│   - 5 Analytics Views│
│   - 3,400+ students │
└─────────────────────┘
```

## Prerequisites

Before installation, ensure you have:

1. **Docker** installed and running
   ```bash
   docker --version  # Should return Docker version 20.10+
   docker ps         # Should run without errors
   ```

2. **DuckDB database** exists at:
   ```
   /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
   ```

3. **Port 3000** is available (not in use by another application)
   ```bash
   lsof -i :3000  # Should return nothing
   ```

4. **Disk space**: At least 2GB free for Metabase container and data

## Installation

### Quick Start (5 minutes)

1. **Navigate to deployment directory:**
   ```bash
   cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
   ```

2. **Start Metabase:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for initialization (60-90 seconds):**
   ```bash
   docker logs -f oss-metabase
   # Watch for: "Metabase Initialization COMPLETE"
   ```

4. **Verify health:**
   ```bash
   curl http://localhost:3000/api/health
   # Should return: {"status":"ok"}
   ```

5. **Open in browser:**
   ```
   http://localhost:3000
   ```

### First-Time Setup (One-Time Only)

When you first access Metabase at `http://localhost:3000`, you'll see a setup wizard:

#### Step 1: Create Admin Account
- **Language**: Select "English"
- **Email**: `admin@district.local` (or your preferred admin email)
- **Password**: Choose a strong password (SAVE THIS SECURELY!)
- **First name**: Your name
- **Last name**: Your name
- **Company**: "School District Analytics" (or your district name)

#### Step 2: Add Database Connection

**Important**: Metabase requires a DuckDB driver to connect. There are two approaches:

##### Option A: Generic SQL Connection (Fallback)
If native DuckDB driver is not available in your Metabase version:
1. Click "I'll add my data later" to complete setup
2. Go to Settings (gear icon) → Admin → Databases → Add Database
3. Select "Generic SQL" or "PostgreSQL" (compatibility mode)
4. Note: This may have limited functionality

##### Option B: Native DuckDB Connection (Recommended)
If Metabase includes DuckDB driver:
1. **Database type**: Select "DuckDB"
2. **Display name**: "OSS Analytics"
3. **Database file path**: `/data/oea.duckdb`
4. **Advanced options**:
   - **Read-only**: ✅ Yes (IMPORTANT - prevent accidental writes)
   - **Rerun queries for simple exploration**: ✅ Yes
   - **Choose when syncs and scans happen**: Default (every hour)
5. Click "Save"

##### Option C: Install DuckDB Driver Plugin
If DuckDB is not available, install the driver:
1. Download DuckDB JDBC driver from: https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/
2. Place `.jar` file in: `/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/plugins/`
3. Restart Metabase: `docker-compose restart`
4. Return to Step 2 and select "DuckDB"

#### Step 3: Verify Connection

Once connected, test the database:

1. Click **"Explore"** → Select "OSS Analytics" database
2. You should see schema: `main_main_analytics`
3. Click on the schema to see 5 analytics views:
   - `v_chronic_absenteeism_risk`
   - `v_wellbeing_risk_profiles`
   - `v_equity_outcomes_by_demographics`
   - `v_class_section_comparison`
   - `v_performance_correlations`

#### Step 4: Run Test Query

1. Click **"New"** → **"SQL Query"**
2. Select database: "OSS Analytics"
3. Run this query:
   ```sql
   SELECT COUNT(*) as row_count 
   FROM main_main_analytics.v_chronic_absenteeism_risk;
   ```
4. **Expected result**: `3400` rows
5. **Query time**: Should be < 2 seconds

✅ **If this works, your setup is complete!**

## Available Analytics Views

Your DuckDB database contains 5 production-ready analytics views:

| View Name | Rows | Purpose | Key Columns |
|-----------|------|---------|-------------|
| `v_chronic_absenteeism_risk` | 3,400 | Student-level chronic absenteeism risk scores | `student_id_hash`, `grade_level`, `attendance_rate_30d`, `risk_score` |
| `v_wellbeing_risk_profiles` | 3,400 | Multi-domain risk assessment (attendance + discipline + academic) | `student_id_hash`, `attendance_risk`, `discipline_risk`, `academic_risk`, `compound_risk` |
| `v_equity_outcomes_by_demographics` | 5 | Aggregated outcomes by race/ethnicity, ELL, SPED, FRL | `demographic_group`, `cohort_size`, `pct_good_attendance`, `avg_gpa` |
| `v_class_section_comparison` | 300 | Class-level effectiveness metrics for teachers | `course_name`, `teacher_id_hash`, `enrollment_count`, `pct_passed`, `effectiveness_rating` |
| `v_performance_correlations` | 3 | Pearson correlations (Attendance ↔ GPA, Discipline ↔ GPA, etc.) | `correlation_name`, `correlation_value`, `strength`, `direction` |

**Performance**: All queries run in < 50ms (optimized with indexes and aggregations)

## Common Operations

### Start Metabase
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d
```

### Stop Metabase
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose down
```
**Note**: This preserves data (users, dashboards, queries). Data is stored in Docker volume `oss-metabase-data`.

### View Logs
```bash
# Real-time logs
docker logs -f oss-metabase

# Last 100 lines
docker logs --tail 100 oss-metabase
```

### Check Status
```bash
# Container status
docker ps | grep oss-metabase

# Health check
curl http://localhost:3000/api/health

# View detailed container info
docker inspect oss-metabase
```

### Restart Metabase
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose restart
```

### Access Metabase Shell (Advanced)
```bash
docker exec -it oss-metabase /bin/bash
```

## File Structure

```
/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/
├── docker-compose.yml       # Container configuration
├── README.md                 # This file
└── plugins/                  # Optional DuckDB JDBC driver directory
    └── duckdb_jdbc-*.jar     # Place driver here if needed

/Users/flucido/projects/openedDataEstate/oss_framework/data/
└── oea.duckdb                # Analytics database (read-only mount)

Docker Volumes:
└── oss-metabase-data/        # Metabase metadata (users, dashboards, settings)
```

## Configuration Details

### Docker Compose Configuration

- **Image**: `metabase/metabase:latest` (official Metabase image)
- **Container name**: `oss-metabase`
- **Port mapping**: `3000:3000` (host:container)
- **Memory allocation**: 2GB max heap (`-Xmx2g`)
- **Restart policy**: `unless-stopped` (auto-restart on host reboot)
- **Health check**: `/api/health` endpoint every 30s

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `MB_DB_TYPE` | `h2` | Use H2 for Metabase metadata (simple, single-file) |
| `MB_DB_FILE` | `/metabase-data/metabase.db` | Path to Metabase metadata database |
| `MB_SITE_NAME` | "OSS Student Analytics" | Displayed in Metabase UI |
| `MB_SITE_LOCALE` | `en` | Language (English) |
| `JAVA_OPTS` | `-Xmx2g -Xms512m` | Java heap: 512MB initial, 2GB max |
| `MB_PLUGINS_DIR` | `/plugins` | Directory for JDBC drivers |

### Volume Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `metabase-data` volume | `/metabase-data` | Read-write | Metabase application data (persists across restarts) |
| `../../data` | `/data` | **Read-only** | DuckDB database (prevents accidental writes) |
| `./plugins` | `/plugins` | Read-only | Optional DuckDB JDBC driver |

## Troubleshooting

### Issue: Port 3000 Already in Use

**Symptoms**: 
```
Error starting container: port 3000 is already allocated
```

**Solution 1 - Change Port**:
1. Edit `docker-compose.yml`
2. Change port mapping: `"3001:3000"` (use 3001 instead)
3. Restart: `docker-compose up -d`
4. Access at: `http://localhost:3001`

**Solution 2 - Stop Conflicting Process**:
```bash
# Find process using port 3000
lsof -i :3000

# Stop the process (replace PID)
kill -9 <PID>
```

### Issue: Cannot Connect to DuckDB

**Symptoms**:
- "Database connection failed"
- "File not found: /data/oea.duckdb"

**Diagnostic Steps**:
1. **Verify database exists on host**:
   ```bash
   ls -lh /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
   ```

2. **Verify database is accessible in container**:
   ```bash
   docker exec oss-metabase ls -lh /data/oea.duckdb
   ```

3. **Check volume mount**:
   ```bash
   docker inspect oss-metabase | grep -A 10 "Mounts"
   ```

**Solutions**:
- If file doesn't exist on host → Regenerate with: `dbt build` (Stage 3)
- If file not accessible in container → Check `docker-compose.yml` volume mount
- If permissions issue → Ensure DuckDB file has read permissions: `chmod 644 oea.duckdb`

### Issue: Metabase Won't Start

**Symptoms**:
- Container exits immediately
- Health check fails after 2 minutes

**Diagnostic Steps**:
1. **Check logs**:
   ```bash
   docker logs oss-metabase
   ```

2. **Look for error patterns**:
   - `OutOfMemoryError` → Increase heap size in `docker-compose.yml`
   - `Port already in use` → See "Port 3000 Already in Use" above
   - `Database locked` → Ensure no other process has `metabase.db` open

**Solutions**:
- **Memory issues**: Edit `docker-compose.yml`, increase `JAVA_OPTS: "-Xmx4g"` (4GB)
- **Corrupted metadata**: Remove and recreate volume:
  ```bash
  docker-compose down
  docker volume rm oss-metabase-data
  docker-compose up -d
  ```
  **Warning**: This deletes all users, dashboards, and saved queries!

### Issue: Slow Query Performance

**Symptoms**:
- Queries take > 5 seconds
- Metabase UI is sluggish

**Diagnostic Steps**:
1. **Test query directly in DuckDB**:
   ```bash
   docker run --rm -v /Users/flucido/projects/openedDataEstate/oss_framework/data:/data \
     duckdb/duckdb:latest /data/oea.duckdb \
     "SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;"
   ```

2. **Check container resources**:
   ```bash
   docker stats oss-metabase
   ```

**Solutions**:
- **DuckDB issue**: Views may need optimization (contact dev team)
- **Metabase caching**: Enable question caching in Settings → Admin → Caching
- **Resource limits**: Increase memory allocation in `docker-compose.yml`

### Issue: DuckDB Driver Not Found

**Symptoms**:
- "DuckDB" not available in database type dropdown
- Generic SQL connection doesn't work

**Solution**:
1. Download DuckDB JDBC driver:
   ```bash
   cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/plugins
   curl -O https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/0.10.0/duckdb_jdbc-0.10.0.jar
   ```

2. Restart Metabase:
   ```bash
   cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
   docker-compose restart
   ```

3. Verify driver loaded:
   ```bash
   docker logs oss-metabase | grep -i duckdb
   ```

4. Return to Admin → Databases → Add Database → Select "DuckDB"

### Issue: Forgot Admin Password

**Symptoms**: Cannot log into Metabase

**Solution** (Reset via database):
```bash
# Stop Metabase
docker-compose down

# Access H2 database (advanced - requires H2 tools)
# Recommended: Reset by recreating volume (loses all data)
docker volume rm oss-metabase-data
docker-compose up -d
# Then complete setup wizard again
```

### Issue: Container Keeps Restarting

**Diagnostic Steps**:
```bash
# Check restart count
docker ps -a | grep oss-metabase

# View last 50 log lines
docker logs --tail 50 oss-metabase

# Check container exit code
docker inspect oss-metabase | grep -A 5 "State"
```

**Common Causes**:
- Out of memory → Increase `JAVA_OPTS` heap size
- Invalid configuration → Check `docker-compose.yml` syntax
- Port conflict → Change port mapping
- Database corruption → Remove volume and recreate

## Security Considerations

### Data Protection
- ✅ **Read-only database mount** - DuckDB is mounted as `:ro` (read-only) to prevent accidental data modification
- ✅ **No external access** - Metabase is only accessible on `localhost` (not exposed to internet)
- ✅ **User authentication** - Admin account required to access Metabase
- ⚠️ **No HTTPS** - Use reverse proxy (nginx) if exposing to network

### Recommended Additional Security

For production deployment:

1. **Change default ports**:
   - Use non-standard port (e.g., 13000 instead of 3000)
   - Add to `docker-compose.yml`: `"13000:3000"`

2. **Add reverse proxy** (nginx/Caddy):
   - Enable HTTPS/TLS encryption
   - Add authentication layer
   - Rate limiting

3. **Enable Metabase security features**:
   - Settings → Admin → Authentication → Enable SSO
   - Settings → Admin → Permissions → Create user groups
   - Settings → Admin → Audit → Enable audit logging

4. **Regular backups**:
   ```bash
   # Backup Metabase metadata
   docker cp oss-metabase:/metabase-data/metabase.db.mv.db ./backup-$(date +%Y%m%d).db
   ```

5. **Keep Metabase updated**:
   ```bash
   docker-compose pull  # Pull latest image
   docker-compose up -d # Recreate container
   ```

## Next Steps

After verifying Metabase is working:

1. ✅ **Create user accounts** (Settings → Admin → People)
   - Create read-only accounts for staff
   - Create editor accounts for data analysts

2. 📊 **Build dashboards** (Task 4.02-4.06):
   - Dashboard 1: Chronic Absenteeism Risk
   - Dashboard 2: Student Wellbeing Profiles
   - Dashboard 3: Equity Outcomes Analysis
   - Dashboard 4: Class Effectiveness Comparison
   - Dashboard 5: Performance Correlations

3. 🔒 **Configure permissions** (Task 4.07):
   - Restrict sensitive data (student IDs, teacher IDs)
   - Create department-specific collections

4. 🧪 **Test with end users** (Task 4.08):
   - Gather feedback on usability
   - Validate data accuracy

5. 📚 **Training materials** (Task 4.10):
   - Create user guides
   - Record demo videos

## Data Refresh Schedule

**Analytics views are refreshed daily** via automated dbt builds:
- Schedule: Every night at 2:00 AM (server time)
- Duration: ~5-10 minutes
- Source: Aeries SIS exports (CSV files)

**Manual refresh** (if needed):
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework
python scripts/run_dbt_build.py --stage 3
```

## Support and Resources

### Documentation
- **Metabase User Guide**: https://www.metabase.com/docs/latest/
- **DuckDB SQL Reference**: https://duckdb.org/docs/sql/introduction
- **OSS Framework Docs**: `/Users/flucido/projects/openedDataEstate/oss_framework/docs/`

### Getting Help
- **View logs**: `docker logs oss-metabase`
- **Check health**: `curl http://localhost:3000/api/health`
- **Metabase forum**: https://discourse.metabase.com/

### Useful SQL Queries

**List all available views**:
```sql
SELECT table_schema, table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'main_main_analytics'
ORDER BY table_name;
```

**Sample 10 records from chronic absenteeism view**:
```sql
SELECT *
FROM main_main_analytics.v_chronic_absenteeism_risk
LIMIT 10;
```

**Count students by risk level**:
```sql
SELECT wellbeing_risk_level, COUNT(*) as student_count
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY wellbeing_risk_level
ORDER BY student_count DESC;
```

**View column definitions**:
```sql
DESCRIBE main_main_analytics.v_chronic_absenteeism_risk;
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Start Metabase | `cd /Users/.../deployment/metabase && docker-compose up -d` |
| Stop Metabase | `docker-compose down` |
| View logs | `docker logs -f oss-metabase` |
| Check status | `docker ps \| grep oss-metabase` |
| Health check | `curl http://localhost:3000/api/health` |
| Access UI | Open browser to `http://localhost:3000` |
| Restart | `docker-compose restart` |
| View volumes | `docker volume ls \| grep metabase` |
| Remove all data | `docker-compose down -v` (⚠️ DESTRUCTIVE) |

**Installation Date**: January 26, 2026  
**Metabase Version**: Latest (auto-updated)  
**Database**: DuckDB 0.10.0+  
**Data Size**: 24 MB (3,400 students, 5 views)

---

*For technical support, contact the OSS Framework development team.*
