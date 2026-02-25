# Docker Setup Documentation - Metabase Deployment

## Overview

This document explains the Docker infrastructure for running Metabase with DuckDB support in the openedDataEstate project. The setup uses a custom Docker image with pre-installed database drivers for optimal analytics performance.

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine (macOS)                     │
│                                                             │
│  /Users/flucido/projects/openedDataEstate/                 │
│  ├── oss_framework/                                        │
│  │   ├── data/oea.duckdb (24MB)          ← Analytics DB   │
│  │   └── deployment/metabase/                             │
│  │       ├── Dockerfile                   ← Custom build  │
│  │       ├── docker-compose.yml          ← Orchestration  │
│  │       └── plugins/ (301MB)            ← Drivers        │
│  └── docker-compose.yml (ROOT)           ← Main stack     │
└─────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│ oss-metabase          │   │ sis-metabase          │
│ Port: 3000            │   │ Port: 3001 (LEGACY)   │
│ Custom Image          │   │ Official Image        │
│ Metabase v0.51.4      │   │ Metabase v0.49.1      │
│ DuckDB driver: 77MB   │   │ No DuckDB driver      │
│ ✅ ACTIVE (PRIMARY)   │   │ ⚠️ Legacy (unused)    │
└───────────────────────┘   └───────────────────────┘
            │                           
            ▼                           
   ┌─────────────────┐                 
   │ DuckDB File     │                 
   │ /data/oea.duckdb│                 
   │ (read-write)    │                 
   └─────────────────┘                 
```

---

## Two Docker Compose Files Explained

### 1. **oss_framework/deployment/metabase/docker-compose.yml** ⭐ PRIMARY

**Purpose:** Run the custom-built Metabase instance with DuckDB support

**Key Characteristics:**
- **Service name:** `metabase` (container: `oss-metabase`)
- **Port:** 3000
- **Image:** Custom-built `metabase-duckdb:latest`
- **DuckDB driver:** Pre-installed (77MB JAR in `/plugins/`)
- **Purpose-built:** Specifically for OSS Framework analytics
- **Docker network:** `oss-metabase-network` (isolated)

**Location:**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d    # Starts ONLY oss-metabase
docker-compose ps       # Shows ONLY oss-metabase
```

**Volume Mounts:**
```yaml
volumes:
  - metabase-data:/metabase-data      # Persistent metadata (H2 database)
  - ../../data:/data                   # DuckDB database (read-write)
  - ./plugins:/plugins                 # Database drivers (read-only)
```

**When to use:**
- Creating analytics dashboards
- Connecting to `oss_framework/data/oea.duckdb`
- Production analytics workflow
- **THIS IS THE RECOMMENDED INSTANCE**

---

### 2. **oss_framework/docker-compose.yml** (ROOT) 🔄 LEGACY

**Purpose:** Run the complete OSS Framework stack (includes legacy Metabase)

**Services:**
- `sis-metabase` (port 3001)
- `dbt-scheduler`
- `aeries-sync`
- Other OSS Framework services

**Key Characteristics:**
- **Service name:** `sis-metabase` (container: `sis-metabase`)
- **Port:** 3001
- **Image:** Official `metabase/metabase:v0.49.1`
- **DuckDB driver:** NOT pre-installed
- **Purpose:** General-purpose BI (not OSS-specific)
- **Docker network:** `oss_framework_default` (shared with all services)

**Location:**
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose up -d    # Starts ALL services (including sis-metabase)
docker-compose ps       # Shows ALL services
```

**When to use:**
- Running the complete OSS Framework stack
- Development/testing environment
- If you need multiple services coordinated
- **NOT RECOMMENDED for analytics** (missing DuckDB driver)

---

## Dockerfile Deep Dive

**Location:** `oss_framework/deployment/metabase/Dockerfile`

### Build Process

```dockerfile
# Base image: Java 21 runtime (Debian-based)
FROM eclipse-temurin:21-jre-jammy

# Build arguments (configurable at build time)
ARG METABASE_VERSION=v0.51.4
ARG METABASE_DUCKDB_DRIVER_VERSION=1.4.3.1

# Environment variables
ENV MB_PLUGINS_DIR=/home/metabase/plugins/

# Steps:
# 1. Create metabase user/group (security: don't run as root)
# 2. Install dependencies (curl, ca-certificates)
# 3. Download Metabase JAR (140MB)
# 4. Download DuckDB driver JAR (77MB)
# 5. Set permissions and expose port 3000
# 6. Switch to non-root user
# 7. Start Metabase
```

### Why Custom Image?

**Problem:** Official `metabase/metabase` image doesn't include DuckDB driver

**Solution:** Build custom image with driver pre-installed

**Advantages:**
1. ✅ **No manual plugin installation** - Driver included in image
2. ✅ **Reproducible** - Same image works on any machine
3. ✅ **Version control** - Pin Metabase and driver versions
4. ✅ **Faster startup** - No need to download driver at runtime

**Build Command** (if you need to rebuild):
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker build -t metabase-duckdb:latest .
```

**Rebuild triggers:**
- Upgrade Metabase version (change `METABASE_VERSION`)
- Upgrade DuckDB driver (change `METABASE_DUCKDB_DRIVER_VERSION`)
- Modify Dockerfile

---

## Plugins Directory Explained

**Location:** `oss_framework/deployment/metabase/plugins/`

**Size:** 301 MB total (19 database drivers)

**Purpose:** Contains JDBC drivers for multiple database types that Metabase can connect to

### Key Drivers

| Driver File | Size | Database | Status |
|-------------|------|----------|--------|
| `duckdb.metabase-driver.jar` | 77MB | DuckDB | ✅ **ACTIVE - PRIMARY USE** |
| `bigquery-cloud-sdk.metabase-driver.jar` | 43MB | Google BigQuery | 📦 Available |
| `snowflake.metabase-driver.jar` | 76MB | Snowflake | 📦 Available |
| `databricks.metabase-driver.jar` | 20MB | Databricks | 📦 Available |
| `athena.metabase-driver.jar` | 15MB | Amazon Athena | 📦 Available |
| `sqlite.metabase-driver.jar` | 13MB | SQLite | 📦 Available |
| Other drivers | ~60MB | Various | 📦 Available |

### How Plugins Work

1. **At container startup:**
   - Metabase scans `/plugins/` directory
   - Loads all `.jar` files
   - Registers database types

2. **In Metabase UI:**
   - Admin → Databases → Add Database
   - Dropdown shows all available types (including DuckDB)

3. **Plugin loading log:**
   ```bash
   docker logs oss-metabase | grep -i plugin
   # Output: "Loaded plugin: DuckDB from duckdb.metabase-driver.jar"
   ```

### Volume Mount

```yaml
volumes:
  - ./plugins:/plugins:ro   # Read-only mount
```

**Why read-only?**
- Prevents container from modifying drivers
- Security best practice
- Drivers should only be updated via rebuilding image

---

## Volume Management

### 1. **oss-metabase-data** (Named Volume)

**Purpose:** Persist Metabase application data across container restarts

**Contents:**
- H2 metadata database (`metabase.db.mv.db`)
- User accounts and authentication
- Dashboard definitions
- Saved queries
- Collections and permissions
- Application settings

**Location:** Managed by Docker (not directly accessible)

**Size:** ~50-200 MB (grows with usage)

**Lifecycle:**
```bash
# Create (automatic on first docker-compose up)
docker volume create oss-metabase-data

# Inspect
docker volume inspect oss-metabase-data

# List all Metabase volumes
docker volume ls | grep metabase

# Backup (IMPORTANT before major changes)
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/metabase-backup-$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/metabase-backup-20260127.tar.gz -C /

# Delete (⚠️ DESTRUCTIVE - loses all data)
docker-compose down -v
# OR
docker volume rm oss-metabase-data
```

**When to backup:**
- Before upgrading Metabase version
- After creating dashboards (weekly)
- Before major configuration changes

---

### 2. **Data Mount** (Host Directory)

**Purpose:** Make DuckDB database accessible to Metabase container

**Host Path:** `/Users/flucido/projects/openedDataEstate/oss_framework/data/`

**Container Path:** `/data/`

**Mount Type:** Bind mount (read-write)

**Contents:**
```
oss_framework/data/
├── oea.duckdb              # Main database (24MB)
├── oea.duckdb.wal          # Write-ahead log (DuckDB uses this for transactions)
└── [other data files]
```

**Why read-write (not read-only)?**
DuckDB requires write access for:
1. **`.wal` file** - Write-ahead log for transaction safety
2. **Query caching** - Temporary query results
3. **Schema caching** - Metadata caching

Even with read-only queries, DuckDB needs write access to the directory.

**Security consideration:**
- Metabase queries are SELECT-only (configured in Metabase connection settings)
- Even with write access, Metabase won't modify data if connection is set to "read-only"

---

### 3. **Plugins Mount** (Host Directory)

**Purpose:** Share database drivers with container

**Host Path:** `/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/plugins/`

**Container Path:** `/plugins/`

**Mount Type:** Bind mount (read-only)

**Contents:** 19 JDBC driver JAR files (301 MB total)

**Why external mount?**
- Share drivers across multiple containers
- Easier to update drivers without rebuilding image
- Inspect drivers on host filesystem

---

## Network Configuration

### oss-metabase-network (Bridge Network)

**Purpose:** Isolated network for oss-metabase container

**Type:** Bridge (default Docker network type)

**CIDR:** Auto-assigned by Docker (e.g., 172.20.0.0/16)

**Isolation:**
- oss-metabase cannot communicate with sis-metabase (different networks)
- oss-metabase can access host filesystem (via volume mounts)
- oss-metabase can access internet (for downloading resources)

**Port Forwarding:**
```
Host Port 3000 → Container Port 3000
```

**Access:**
- From host: `http://localhost:3000`
- From container: `http://metabase:3000` (hostname)

---

## Environment Variables Reference

### Core Metabase Settings

| Variable | Value | Purpose |
|----------|-------|---------|
| `MB_DB_TYPE` | `h2` | Metabase metadata database type (H2 = embedded file database) |
| `MB_DB_FILE` | `/metabase-data/metabase.db` | Path to H2 database file |
| `MB_SITE_NAME` | "OSS Student Analytics" | Displayed in browser title and UI |
| `MB_SITE_LOCALE` | `en` | Language (English) |

### Java/Performance Settings

| Variable | Value | Purpose |
|----------|-------|---------|
| `JAVA_OPTS` | `-Xmx2g -Xms512m` | Java heap memory (512MB initial, 2GB max) |

**Why 2GB?**
- Metabase default: 1GB
- Analytics workloads: Need more memory for complex queries
- 2GB is recommended minimum for production

**To increase (if needed):**
Edit `docker-compose.yml`:
```yaml
JAVA_OPTS: "-Xmx4g -Xms1g"   # 4GB max heap
```

### Plugin Configuration

| Variable | Value | Purpose |
|----------|-------|---------|
| `MB_PLUGINS_DIR` | `/plugins` | Directory to scan for JDBC drivers |

---

## Health Check Configuration

**Purpose:** Automatically detect if Metabase is responsive

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
  interval: 30s        # Check every 30 seconds
  timeout: 10s         # Wait max 10s for response
  retries: 5           # Try 5 times before marking unhealthy
  start_period: 120s   # Wait 2 minutes before first check (startup time)
```

**Health States:**
- `starting` (first 2 minutes) - Not checked yet
- `healthy` - `/api/health` returns 200 OK
- `unhealthy` - 5 consecutive failures

**Check status:**
```bash
docker ps | grep oss-metabase
# LOOK FOR: "healthy" in STATUS column
```

**Manual health check:**
```bash
curl http://localhost:3000/api/health
# Expected: {"status":"ok"}
```

---

## Restart Policy

```yaml
restart: unless-stopped
```

**Behavior:**
| Scenario | Restart? |
|----------|----------|
| Container crashes | ✅ Yes (automatic) |
| Host machine reboots | ✅ Yes (automatic) |
| User runs `docker stop` | ❌ No (stays stopped) |
| Docker daemon restarts | ✅ Yes (automatic) |

**Alternative policies:**
- `no` - Never restart (manual start only)
- `always` - Always restart (even after manual stop)
- `on-failure` - Only restart on error exit codes

**Why `unless-stopped`?**
- Automatic recovery from crashes
- Survives host reboots
- Respects manual stops (for maintenance)

---

## Common Operations

### Start Both Instances

```bash
# Start oss-metabase (port 3000)
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d

# Start sis-metabase (port 3001) and other services
cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose up -d
```

### Stop Both Instances

```bash
# Stop oss-metabase
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose down

# Stop all OSS Framework services (including sis-metabase)
cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose down
```

### View All Running Containers

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

Expected output:
```
NAMES           PORTS                    STATUS
oss-metabase    0.0.0.0:3000->3000/tcp   Up 2 hours (healthy)
sis-metabase    0.0.0.0:3001->3000/tcp   Up 2 hours
```

### Resource Usage

```bash
docker stats --no-stream oss-metabase sis-metabase
```

### Logs Comparison

```bash
# oss-metabase logs
docker logs -f oss-metabase

# sis-metabase logs
docker logs -f sis-metabase
```

---

## Troubleshooting Docker Issues

### Issue: Port Conflict Between Instances

**Problem:** Both instances try to use same port

**Symptom:**
```
Error: port 3000 is already allocated
```

**Solution:** Each instance uses different port (already configured correctly)
- oss-metabase: 3000
- sis-metabase: 3001

**Verification:**
```bash
docker ps --format "{{.Names}}: {{.Ports}}"
```

---

### Issue: Volume Permission Errors

**Problem:** Container can't read/write to mounted directories

**Symptom:**
```
Permission denied: /data/oea.duckdb
```

**Diagnostic:**
```bash
# Check file permissions on host
ls -lh /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Check container user
docker exec oss-metabase whoami
docker exec oss-metabase id
```

**Solution:**
```bash
# Option 1: Fix host permissions (ensure readable by container user)
chmod 644 /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Option 2: Run container as root (already configured)
# See docker-compose.yml: user: "0:0"
```

---

### Issue: Image Build Failures

**Problem:** `docker build` fails during Dockerfile execution

**Common causes:**
1. **Network timeout** downloading JARs
2. **Invalid version** in ARG variables
3. **Disk space** insufficient

**Solution:**
```bash
# Check disk space
df -h

# Clean Docker cache
docker system prune -a

# Retry build with verbose logging
docker build --no-cache --progress=plain -t metabase-duckdb:latest .
```

---

### Issue: Container Exits Immediately

**Diagnostic:**
```bash
# Check exit code and error
docker ps -a | grep oss-metabase
docker logs oss-metabase | tail -50
```

**Common causes:**
- Port conflict → Change port in docker-compose.yml
- Memory limit → Increase `JAVA_OPTS -Xmx`
- Invalid environment variable → Check syntax in docker-compose.yml

---

### Issue: Cannot Connect to DuckDB from Metabase

**Diagnostic Checklist:**
1. **Database file exists on host?**
   ```bash
   ls -lh oss_framework/data/oea.duckdb
   ```

2. **Database file accessible in container?**
   ```bash
   docker exec oss-metabase ls -lh /data/oea.duckdb
   ```

3. **DuckDB driver loaded?**
   ```bash
   docker logs oss-metabase | grep -i duckdb
   ```

4. **Correct path in Metabase connection?**
   - Should be: `/data/oea.duckdb`
   - NOT: `/Users/.../oea.duckdb`

---

## Comparison Table: Both Instances

| Feature | oss-metabase (Port 3000) | sis-metabase (Port 3001) |
|---------|--------------------------|--------------------------|
| **Metabase Version** | v0.51.4 (newer) | v0.49.1 (older) |
| **Image** | Custom-built | Official |
| **DuckDB Driver** | ✅ Pre-installed (77MB) | ❌ Not included |
| **Purpose** | OSS analytics (production) | Legacy/general BI |
| **Docker Compose** | `deployment/metabase/` | `oss_framework/` (root) |
| **Network** | `oss-metabase-network` | `oss_framework_default` |
| **Data Volume** | `oss-metabase-data` | `oss_framework_metabase-data` |
| **Health Check** | ✅ Configured | ⚠️ May not be configured |
| **Status** | ⭐ **PRIMARY - USE THIS** | 🔄 Legacy (optional) |

---

## Recommended Workflow

### For Analytics Work (Creating Dashboards)

**ALWAYS use oss-metabase (port 3000):**

```bash
# 1. Start oss-metabase
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d

# 2. Wait for health check
docker logs -f oss-metabase
# Look for: "Metabase Initialization COMPLETE"

# 3. Access in browser
open http://localhost:3000

# 4. Create dashboards using create-dashboards-api.py
python3 create-dashboards-api.py
```

### For Full Stack Development

**Use root docker-compose.yml (starts all services):**

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose up -d
```

This starts:
- sis-metabase (port 3001)
- dbt-scheduler
- aeries-sync
- Other OSS Framework services

**Note:** sis-metabase (3001) lacks DuckDB driver, so analytics won't work there.

---

## Cleanup Commands

### Remove All Containers (Keep Data)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose down

cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose down
```

### Remove Everything (⚠️ DESTROYS DATA)

```bash
# Remove oss-metabase and data
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose down -v

# Remove all OSS Framework containers and data
cd /Users/flucido/projects/openedDataEstate/oss_framework
docker-compose down -v
```

### Clean Docker System (Free Space)

```bash
# Remove unused images, containers, networks
docker system prune

# Remove ALL unused images (⚠️ rebuilds required)
docker system prune -a

# Check reclaimed space
docker system df
```

---

## Security Considerations

### Container Runs as Root

```yaml
user: "0:0"   # UID 0 = root
```

**Why?**
- DuckDB file requires write permissions
- Volume mount ownership issues on macOS
- Simplifies development setup

**Production recommendation:**
- Create dedicated user with UID matching host filesystem
- Use Docker user namespace remapping

### Network Isolation

- oss-metabase has its own network (cannot talk to other containers)
- Only exposes port 3000 to host
- No direct internet access from container (unless needed)

### Secrets Management

**Current approach:**
- Admin credentials entered via UI (stored in H2 database)
- No credentials in docker-compose.yml

**Production recommendation:**
- Use Docker secrets or environment files
- Never commit credentials to git
- Rotate admin password regularly

---

## File Locations Quick Reference

```
/Users/flucido/projects/openedDataEstate/
├── oss_framework/
│   ├── deployment/metabase/
│   │   ├── Dockerfile                      # Custom image build
│   │   ├── docker-compose.yml              # oss-metabase orchestration
│   │   ├── DOCKER-SETUP.md                 # This file
│   │   ├── SETUP-STATE.md                  # Current state documentation
│   │   ├── SCRIPTS-CONSOLIDATION.md        # Script usage guide
│   │   ├── create-dashboards-api.py        # Dashboard creation script
│   │   ├── .env.example                    # Credentials template
│   │   └── plugins/ (301MB)                # Database drivers
│   │       └── duckdb.metabase-driver.jar  # 77MB DuckDB driver
│   ├── data/
│   │   ├── oea.duckdb                      # Analytics database (24MB)
│   │   └── oea.duckdb.wal                  # DuckDB write-ahead log
│   └── docker-compose.yml                  # Full stack (includes sis-metabase)
└── [other project files]

Docker Volumes:
├── oss-metabase-data/                      # oss-metabase metadata (~50-200MB)
└── oss_framework_metabase-data/            # sis-metabase metadata
```

---

## Next Steps

After understanding Docker setup:

1. ✅ **Verify both instances are running:**
   ```bash
   docker ps | grep metabase
   ```

2. ✅ **Access oss-metabase UI:**
   ```
   http://localhost:3000
   ```

3. ✅ **Complete database connection** (see README.md)

4. ✅ **Run dashboard creation script** (see SCRIPTS-CONSOLIDATION.md)

5. ✅ **Create production backup schedule:**
   ```bash
   # Weekly backup cron job
   0 2 * * 0 cd /Users/.../deployment/metabase && \
     docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
     alpine tar czf /backup/backups/metabase-$(date +\%Y\%m\%d).tar.gz /data
   ```

---

## Support Resources

- **Docker Docs**: https://docs.docker.com/
- **Metabase Docs**: https://www.metabase.com/docs/latest/
- **DuckDB Docs**: https://duckdb.org/docs/
- **Project README**: `oss_framework/deployment/metabase/README.md`

---

**Documentation Version:** 1.0  
**Last Updated:** 2026-01-27  
**Docker Compose Version:** 3.8  
**Metabase Version:** v0.51.4  
**DuckDB Driver Version:** 1.4.3.1
