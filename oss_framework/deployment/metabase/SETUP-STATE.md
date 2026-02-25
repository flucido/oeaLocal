# Metabase Setup State Documentation

**Last Updated:** 2026-01-27 20:10 PST  
**Status:** Dual setup - requires consolidation

---

## Current Deployment Architecture

### Two Active Metabase Instances

#### Instance 1: `oss-metabase` (Primary - Recommended)
- **Container Name:** `oss-metabase`
- **Port:** 3000 (http://localhost:3000)
- **Image:** `metabase-duckdb:latest` (custom built)
- **Purpose:** OSS Framework analytics dashboards with DuckDB support
- **Docker Compose:** `oss_framework/deployment/metabase/docker-compose.yml`
- **Status:** ✅ Running (3+ hours), Healthy
- **Network:** `oss-metabase-network`

**Configuration:**
```yaml
Image: metabase-duckdb:latest (Custom Dockerfile)
Base: eclipse-temurin:21-jre-jammy
Metabase Version: v0.51.4
DuckDB Driver: v1.4.3.1 (pre-installed)
Java: JDK 21.0.9
Memory: 2GB heap (-Xmx2g -Xms512m)
Storage: H2 database at /metabase-data/metabase.db
Plugins: /plugins (mounted, includes DuckDB driver)
Data Mount: ../../data → /data (DuckDB database access)
User: root (0:0) - for data file write access
Site Name: "OSS Student Analytics"
```

**Key Features:**
- ✅ DuckDB driver pre-installed in Docker image
- ✅ Direct file access to `oea.duckdb` at `/data/oea.duckdb`
- ✅ Health check enabled (checks every 30s)
- ✅ Auto-restart enabled (`unless-stopped`)
- ✅ Dedicated volume for persistence

**Access:**
- Web UI: http://localhost:3000
- Health: http://localhost:3000/api/health
- Container: `docker exec -it oss-metabase bash`

---

#### Instance 2: `sis-metabase` (Legacy - Student Information System)
- **Container Name:** `sis-metabase`
- **Port:** 3001 (http://localhost:3001)
- **Image:** `metabase/metabase:v0.49.1` (official)
- **Purpose:** Legacy SIS analytics (appears to be from earlier setup)
- **Docker Compose:** `oss_framework/docker-compose.yml` (main stack)
- **Status:** ✅ Running (7+ hours)
- **Network:** Part of main `oss_framework` stack

**Configuration:**
```yaml
Image: metabase/metabase:v0.49.1 (Official release)
Java: JDK 11.0.22
Storage: H2 database at /metabase-data/metabase.db
Dependencies: PostgreSQL (oss_framework stack)
User: default (metabase user)
Timezone: UTC
```

**Key Differences from oss-metabase:**
- ❌ No DuckDB driver pre-installed (would need manual plugin installation)
- ❌ Older Metabase version (v0.49.1 vs v0.51.4)
- ❌ Older Java version (11 vs 21)
- ⚠️ Depends on PostgreSQL service in main stack
- ⚠️ No direct DuckDB file mount configured

**Access:**
- Web UI: http://localhost:3001
- Container: `docker exec -it sis-metabase bash`

---

## Recommended Instance: `oss-metabase` (Port 3000)

### Why oss-metabase is the Primary Choice

1. **DuckDB Native Support**
   - Driver pre-built into image
   - No manual plugin installation required
   - Latest DuckDB driver version (1.4.3.1)

2. **Modern Stack**
   - Metabase v0.51.4 (latest stable)
   - Java 21 (better performance, newer features)
   - Optimized for analytics workloads (2GB heap)

3. **Purpose-Built**
   - Specifically configured for OSS Framework
   - Branded as "OSS Student Analytics"
   - Direct access to `oea.duckdb` via volume mount

4. **Better Health Monitoring**
   - Health check endpoint configured
   - Auto-restart on failure
   - Dedicated network isolation

### When to Use sis-metabase

- Legacy SIS dashboard access only
- If you need PostgreSQL-backed dashboards
- Backward compatibility with older Metabase features

**Recommendation:** Migrate any useful content from `sis-metabase` to `oss-metabase`, then deprecate `sis-metabase`.

---

## Database Connections Status

### Expected Connection: DuckDB (`oea.duckdb`)

**File Location (Host):**
```
/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
```

**File Location (oss-metabase Container):**
```
/data/oea.duckdb
```

**Database Details:**
- Size: 24 MB (281,600 bytes)
- Schema: `main_main_analytics`
- Views: 5 analytics views
  - `v_chronic_absenteeism_risk`
  - `v_wellbeing_risk_profiles`
  - `v_equity_outcomes_by_demographics`
  - `v_class_section_comparison`
  - `v_performance_correlations`
- Data: ~3,400 students (synthetic test data)

**Connection Status:**
- ⚠️ **Unknown** - needs verification
- Expected database name in Metabase: "OSS Analytics" or "OEA Analytics"
- Connection type: DuckDB (native)

### Verification Needed

Run these checks:
1. Access Metabase → Settings → Admin → Databases
2. Look for "OSS Analytics" or similar database connection
3. Check connection status (green = working)
4. Test query: `SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;`
5. Expected result: 3400 rows

---

## Dashboard Scripts - Current State

### Script 1: `create-dashboards-api.py` (PRIMARY)
- **Location:** `oss_framework/deployment/metabase/create-dashboards-api.py`
- **Size:** 25,060 bytes (772 lines)
- **Status:** ✅ **Fixed and ready** (per RUN-DASHBOARDS.md)
- **Last Modified:** 2026-01-27 17:43
- **Target Port:** 3000 (oss-metabase) ✅ Correct

**Purpose:**
- Create 5 production dashboards via Metabase REST API
- Automatic cleanup of old/empty dashboards
- 26 visualizations total across 5 dashboards

**Capabilities:**
- ✅ Authentication with Metabase
- ✅ Database discovery
- ✅ Collection creation/reuse
- ✅ Question (visualization) creation
- ✅ Dashboard creation
- ✅ Card-to-dashboard linking
- ✅ Cleanup of existing content

**Requirements:**
- Environment variables:
  - `METABASE_EMAIL` (admin email)
  - `METABASE_PASSWORD` (admin password)
- Or command-line arguments:
  - `--email admin@example.com`
  - `--password yourpassword`

**Runtime:** 5-10 minutes (includes cleanup)

**Execution:**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
export METABASE_EMAIL="your-admin-email"
export METABASE_PASSWORD="your-password"
python3 create-dashboards-api.py
```

**What It Creates:**
1. Dashboard 1: Chronic Absenteeism Risk (6 visualizations)
2. Dashboard 2: Student Wellbeing Risk Profiles (2 visualizations)
3. Dashboard 3: Equity Outcomes Analysis (2 visualizations)
4. Dashboard 4: Class Effectiveness Comparison (1 visualization)
5. Dashboard 5: Performance Correlations (1 visualization)

**SQL Query Status:**
- ✅ All 11 queries fixed with `main_main_analytics.` schema prefix
- ✅ Tested against DuckDB schema
- ✅ Type-safe visualizations configured

---

### Script 2: `metabase_provisioning.py` (REFERENCE ONLY)
- **Location:** `oss_framework/deployment/metabase/metabase_provisioning.py`
- **Size:** 899 lines
- **Status:** ⚠️ **Not directly executable**
- **Target Port:** 3001 (sis-metabase) ❌ Wrong instance

**Purpose:**
- Template-based dashboard definition generator
- Exports JSON specifications (not executable dashboards)

**Capabilities:**
- Dashboard definition classes
- Query template generation
- JSON export for review

**Limitations:**
- Does NOT create dashboards in Metabase
- Requires separate script to import JSON
- Targets wrong Metabase instance (port 3001)
- More complex architecture (5 Python classes)

**Use Case:**
- Reference implementation for dashboard structure
- Prototype/planning tool
- Not for production deployment

---

### Script 3: `metabase_automation_script.py` (ALTERNATIVE)
- **Location:** `oss_framework/deployment/metabase/metabase_automation_script.py`
- **Size:** 381 lines
- **Status:** ⚠️ **Partially implemented**
- **Target Port:** 3001 (sis-metabase) ❌ Wrong instance

**Purpose:**
- Modular automation with separate steps
- Admin setup, DB connection, dashboard creation

**Capabilities:**
- `--init-admin` - Admin account creation (requires UI)
- `--login` - Authenticate with credentials
- `--connect-db` - Connect DuckDB database
- `--create-dashboards` - Create from JSON specs
- `--test-queries` - Performance testing (stub)
- `--full-setup` - Complete workflow

**Limitations:**
- Targets wrong Metabase instance (port 3001)
- Requires JSON definition files from `metabase_provisioning.py`
- Admin setup requires manual UI interaction
- Only creates first 2 cards per dashboard (proof of concept)

**Use Case:**
- Experimental/alternative approach
- Step-by-step automation
- Not recommended for production

---

## Script Recommendation Matrix

| Task | Recommended Script | Alternative |
|------|-------------------|-------------|
| **Create all 5 dashboards** | `create-dashboards-api.py` | None |
| **Cleanup old dashboards** | `create-dashboards-api.py` | Manual deletion in UI |
| **Generate dashboard specs** | `metabase_provisioning.py` | N/A |
| **Step-by-step setup** | `metabase_automation_script.py` | Manual UI workflow |
| **Connect DuckDB** | Manual UI setup | `metabase_automation_script.py --connect-db` |

**Primary Script:** `create-dashboards-api.py`  
**Reason:** Complete, tested, targets correct instance, includes cleanup, production-ready

---

## Port Configuration

### Current Assignments

| Instance | Port | URL | Purpose | Status |
|----------|------|-----|---------|--------|
| `oss-metabase` | 3000 | http://localhost:3000 | OSS Framework dashboards | ✅ Active |
| `sis-metabase` | 3001 | http://localhost:3001 | Legacy SIS dashboards | ⚠️ Legacy |

### Script Port Targets

| Script | Target Port | Correct? | Action Needed |
|--------|-------------|----------|---------------|
| `create-dashboards-api.py` | 3000 | ✅ Yes | None - ready to use |
| `metabase_provisioning.py` | 3001 | ❌ No | Update to 3000 if used |
| `metabase_automation_script.py` | 3001 | ❌ No | Update to 3000 if used |

**Recommendation:** All scripts should target port 3000 (`oss-metabase`)

---

## Credential Management

### Current State
- ⚠️ **Admin credentials unknown**
- ⚠️ **No .env file configured**
- ⚠️ **No .env.example template**

### Required Credentials

**For Dashboard Creation Scripts:**
```bash
METABASE_EMAIL="admin@example.com"      # Metabase admin email
METABASE_PASSWORD="your-secure-password" # Metabase admin password
```

**For Database Connection:**
- No credentials needed (file-based DuckDB)
- Database path: `/data/oea.duckdb` (inside container)

### Security Recommendations

1. **Create .env.example:**
```bash
# Metabase Admin Credentials
METABASE_EMAIL=admin@your-district.edu
METABASE_PASSWORD=your-secure-password-here

# Metabase URL (default: http://localhost:3000)
METABASE_URL=http://localhost:3000

# Database path (inside container)
DUCKDB_PATH=/data/oea.duckdb
```

2. **Create .env for local use:**
```bash
cp .env.example .env
# Edit .env with real credentials
# Add .env to .gitignore
```

3. **Verify .gitignore excludes:**
```
.env
*.env
metabase-data/
```

---

## Volume Mounts and Data Persistence

### oss-metabase Volumes

| Host Path | Container Path | Purpose | Access |
|-----------|---------------|---------|--------|
| Docker volume `oss-metabase-data` | `/metabase-data` | Metabase app data (H2 DB, settings) | Read-write |
| `../../data` (oss_framework/data) | `/data` | DuckDB database | Read-write |
| `./plugins` | `/plugins` | DuckDB driver JAR | Read-only |

**Persistence:**
- ✅ Metabase settings persist across container restarts
- ✅ Dashboards persist across container restarts
- ✅ User accounts persist across container restarts
- ✅ DuckDB database accessible from host and container

**Data Location (Host):**
- Metabase data: Docker volume (managed by Docker)
- DuckDB database: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`

---

## Docker Compose Files

### File 1: `oss_framework/deployment/metabase/docker-compose.yml` (PRIMARY)
- **Purpose:** Dedicated Metabase with DuckDB setup
- **Services:** 1 (metabase only)
- **Container:** `oss-metabase`
- **Network:** `oss-metabase-network` (isolated)
- **Custom Image:** Yes (`metabase-duckdb:latest`)
- **Status:** ✅ Active, recommended

**Build Command:**
```bash
cd oss_framework/deployment/metabase
docker-compose up -d --build
```

### File 2: `oss_framework/docker-compose.yml` (MAIN STACK)
- **Purpose:** Complete OSS Framework stack
- **Services:** Multiple (metabase, postgres, dagster, etc.)
- **Container:** `sis-metabase`
- **Network:** Shared with PostgreSQL and other services
- **Image:** Official `metabase/metabase:v0.49.1`
- **Status:** ⚠️ Legacy, consider deprecating

**Start Command:**
```bash
cd oss_framework
docker-compose up -d metabase
```

### File 3: `oss_framework/deployment/metabase/docker-compose-https.yml` (UNUSED)
- **Purpose:** HTTPS-enabled Metabase with nginx reverse proxy
- **Services:** 2 (metabase + nginx)
- **Status:** ❌ Not currently used
- **Use Case:** Production deployment with SSL/TLS

---

## Dockerfile (Custom Image)

**Location:** `oss_framework/deployment/metabase/Dockerfile`

**Base Image:** `eclipse-temurin:21-jre-jammy`

**Installed Components:**
1. Metabase v0.51.4 JAR
2. DuckDB driver v1.4.3.1 JAR
3. CA certificates
4. curl (for health checks)

**Build Arguments:**
- `METABASE_VERSION=v0.51.4`
- `METABASE_DUCKDB_DRIVER_VERSION=1.4.3.1`

**Build Process:**
```bash
cd oss_framework/deployment/metabase
docker build -t metabase-duckdb:latest .
```

**Image Size:** ~500MB (Java 21 + Metabase + DuckDB driver)

**Driver Source:** https://github.com/motherduckdb/metabase_duckdb_driver

---

## Next Steps

### Immediate Actions Required

1. **Verify Database Connection (Task #2)**
   - Access http://localhost:3000 (oss-metabase)
   - Check Settings → Admin → Databases
   - Verify "OSS Analytics" database exists and is connected
   - Test query against `main_main_analytics` schema

2. **Obtain/Verify Admin Credentials (Task #6)**
   - Determine current admin email/password
   - Create .env file with credentials
   - Create .env.example template

3. **Fix Port Conflicts (Task #3)**
   - Update `metabase_provisioning.py` to use port 3000
   - Update `metabase_automation_script.py` to use port 3000
   - Document port standardization

4. **Execute Dashboard Creation (Task #7)**
   - Run `create-dashboards-api.py` with credentials
   - Monitor output for errors
   - Verify dashboards created successfully

5. **Verify Dashboard Data (Task #8)**
   - Execute VERIFICATION-CHECKLIST.md checks
   - Confirm all 5 dashboards display correct data
   - Report any "No results" issues

### Medium-Term Actions

6. **Deprecate sis-metabase (Future)**
   - Migrate any useful content to oss-metabase
   - Stop sis-metabase container
   - Remove from docker-compose.yml

7. **Improve Documentation**
   - Create troubleshooting guide
   - Document common issues and solutions
   - Add architecture diagrams

---

## Troubleshooting Quick Reference

### Cannot Access Metabase UI

**Problem:** http://localhost:3000 not loading

**Solutions:**
1. Check container status: `docker ps | grep oss-metabase`
2. Check health: `docker exec oss-metabase curl http://localhost:3000/api/health`
3. View logs: `docker logs oss-metabase`
4. Restart: `docker restart oss-metabase`

### Database Connection Failed

**Problem:** "Could not connect to database"

**Solutions:**
1. Verify DuckDB file exists: `ls -lh oss_framework/data/oea.duckdb`
2. Check container can access file: `docker exec oss-metabase ls -lh /data/oea.duckdb`
3. Verify schema: `docker exec oss-metabase duckdb /data/oea.duckdb "SELECT * FROM information_schema.tables WHERE table_schema='main_main_analytics';"`
4. Check permissions: File should be readable by container

### Dashboard Shows "No Results"

**Problem:** Dashboard created but empty

**Solutions:**
1. Click "Show Editor" on visualization
2. Run query manually in SQL editor
3. Verify schema name: `main_main_analytics.v_...`
4. Check data exists: `SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;`
5. Expected: 3400 rows

### Script Authentication Fails

**Problem:** "Authentication failed: 401"

**Solutions:**
1. Verify credentials are correct
2. Check admin account exists in Metabase UI
3. Try manual login at http://localhost:3000
4. Reset password if needed through UI

---

## Documentation Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Installation and setup guide | ✅ Complete |
| `RUN-DASHBOARDS.md` | Dashboard creation instructions | ✅ Complete |
| `VERIFICATION-CHECKLIST.md` | Dashboard verification steps | ✅ Complete |
| `SETUP-STATE.md` | **This file** - current state documentation | ✅ Complete |
| `.env.example` | Credential template | ❌ **Needs creation** |
| `TROUBLESHOOTING.md` | Issue resolution guide | ⏳ **Planned** |

---

**End of Setup State Documentation**
