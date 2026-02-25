# Metabase Analytics - Production Deployment Guide

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Ready for Production Deployment  
**Target Audience**: System Administrators, DevOps Engineers

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Options](#deployment-options)
3. [Option A: Same-Server Deployment (Development → Production Promotion)](#option-a-same-server-deployment)
4. [Option B: Separate Production Server](#option-b-separate-production-server)
5. [Database Configuration](#database-configuration)
6. [User Account Setup](#user-account-setup)
7. [Security Hardening](#security-hardening)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Rollback Procedures](#rollback-procedures)
12. [Launch Communication](#launch-communication)

---

## Pre-Deployment Checklist

**Complete ALL items before deploying to production:**

### 1. UAT Completion
- [ ] All 5 user groups completed UAT testing
- [ ] UAT feedback forms collected and reviewed
- [ ] ≥80% average satisfaction rating achieved
- [ ] Zero **critical** issues remain (see `uat/uat-issues-log-template.md`)
- [ ] All **high-priority** issues resolved or have documented workarounds
- [ ] UAT sign-off received from project manager and QA lead

### 2. Technical Readiness
- [ ] All 5 dashboards created and tested
- [ ] Database queries run in <2 seconds
- [ ] Role-based access controls configured
- [ ] User accounts created for all stakeholders
- [ ] Training materials finalized and distributed
- [ ] Backup procedures tested and verified

### 3. Infrastructure Readiness
- [ ] Production server provisioned (8GB+ RAM, 500GB+ storage)
- [ ] Network firewall rules configured
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] Reverse proxy configured (nginx/Caddy) for HTTPS
- [ ] Database backups scheduled (daily automated backups)
- [ ] Monitoring tools installed (uptime, performance)

### 4. Security Readiness
- [ ] Security audit completed
- [ ] FERPA compliance verified (student data protection)
- [ ] Data masking configured for sensitive fields
- [ ] Admin credentials secured (password manager)
- [ ] Audit logging enabled

### 5. Stakeholder Readiness
- [ ] Superintendent approval for launch
- [ ] IT department notified of launch date/time
- [ ] End users notified of upcoming access
- [ ] Support contact info published (help desk)
- [ ] Launch communication drafted and reviewed

---

## Deployment Options

### Decision Matrix

| Criteria | Option A: Same-Server Promotion | Option B: Separate Production Server |
|----------|----------------------------------|--------------------------------------|
| **Complexity** | Low (promote dev to prod) | Medium (new server setup) |
| **Downtime** | None (rename container) | None (new server) |
| **Cost** | $0 (same server) | $50-200/month (dedicated server/VM) |
| **Isolation** | Dev and prod share resources | Complete isolation |
| **Best For** | Small districts, pilot deployments | Large districts, high availability needs |
| **Recommended?** | ✅ Yes (for initial launch) | ⚠️ Optional (for scale/compliance) |

**Recommendation**: Start with **Option A** (promote dev container to production). Migrate to **Option B** later if:
- Performance issues occur (resource contention)
- District policy requires production isolation
- High availability (99.9% uptime) is mandated

---

## Option A: Same-Server Deployment

**Scenario**: Promote existing development Metabase container to production.

### Step 1: Stop Development Container

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose down
```

**Result**: `oss-metabase` container stopped, but data persists in Docker volume `oss-metabase-data`.

---

### Step 2: Backup Development Data

**CRITICAL: Create backup before any changes**

```bash
# Create backup directory
mkdir -p /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups

# Backup Docker volume
docker run --rm -v oss-metabase-data:/source -v $(pwd):/backup alpine \
  tar czf /backup/metabase-data-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /source .

# Backup DuckDB database
cp /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb \
   /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups/oea-backup-$(date +%Y%m%d-%H%M%S).duckdb

# Verify backups exist
ls -lh
```

**Expected Output**:
```
-rw-r--r--  1 user  staff   5.2M Jan 27 14:30 metabase-data-backup-20260127-143000.tar.gz
-rw-r--r--  1 user  staff    24M Jan 27 14:30 oea-backup-20260127-143000.duckdb
```

---

### Step 3: Rename Container to Production

**Update `docker-compose.yml` for production:**

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
cp docker-compose.yml docker-compose.yml.dev  # Keep dev config for reference
```

Edit `docker-compose.yml`:

```yaml
version: '3.8'

services:
  metabase-prod:  # Renamed from oss-metabase
    image: metabase/metabase:latest
    container_name: oss-metabase-prod  # Renamed
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: h2
      MB_DB_FILE: /metabase-data/metabase.db
      MB_SITE_NAME: "OSS Student Analytics - PRODUCTION"  # Clear label
      MB_SITE_LOCALE: en
      JAVA_OPTS: "-Xmx4g -Xms1g"  # Increased heap for production (4GB max, 1GB initial)
    volumes:
      - oss-metabase-data:/metabase-data  # Same volume = all data preserved
      - ../../data:/data:ro
      - ./plugins:/plugins:ro
    restart: always  # Auto-restart on failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 90s

volumes:
  oss-metabase-data:
    external: true  # Use existing volume
```

**Key Changes**:
- Container name: `oss-metabase-prod` (clear production label)
- Site name: "OSS Student Analytics - PRODUCTION"
- Memory: Increased to 4GB max heap (better performance)
- Restart policy: `always` (auto-recover from crashes)
- Volume: Same volume = all dashboards, users, settings preserved

---

### Step 4: Start Production Container

```bash
docker-compose up -d
```

**Verify startup:**

```bash
# Watch logs for successful startup
docker logs -f oss-metabase-prod

# Expected output (after 60-90 seconds):
# "Metabase Initialization COMPLETE"

# Health check
curl http://localhost:3000/api/health
# Expected: {"status":"ok"}
```

---

### Step 5: Verify Production Configuration

**Access Metabase UI:**

```
http://localhost:3000
```

**Verification Checklist:**

1. **Login with Admin Account**:
   - Email: `admin@oss-framework.local` (or your admin email)
   - Password: [Your admin password from dev]
   - **If login fails** → Credentials changed? → Use backup to restore

2. **Verify Dashboards Exist**:
   - Navigate to: Collections → "OSS Analytics"
   - Confirm all 5 dashboards present:
     - Dashboard 1: Chronic Absenteeism Risk
     - Dashboard 2: Student Wellbeing Profiles
     - Dashboard 3: Equity Outcomes Analysis
     - Dashboard 4: Class Effectiveness Comparison
     - Dashboard 5: Performance Correlations

3. **Test Each Dashboard**:
   - Click each dashboard
   - Verify all visualizations load
   - Check query time (should be <2 seconds)
   - Verify filters work

4. **Verify User Accounts**:
   - Settings → Admin → People
   - Confirm all user accounts present
   - Test login as non-admin user (use incognito/private browser)

5. **Verify Site Name**:
   - Top-left corner should say: "OSS Student Analytics - PRODUCTION"
   - Confirms you're not in dev anymore

---

### Step 6: Update Documentation

**Update README with production info:**

Edit `/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/README.md`:

```markdown
## Production Access

**URL**: http://localhost:3000  
**Container**: oss-metabase-prod  
**Status**: PRODUCTION (as of [DATE])  
**Admin**: admin@oss-framework.local  
**Support**: [IT Help Desk Email]

## Development Environment

Development environment has been promoted to production.
To restore dev environment for testing, see `docker-compose.yml.dev`.
```

---

### Step 7: Configure Automated Backups

**Create backup script:**

```bash
# Create script
cat > /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backup-production.sh << 'SCRIPT'
#!/bin/bash
# Metabase Production Backup Script
# Run daily via cron: 0 2 * * * /path/to/backup-production.sh

BACKUP_DIR="/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=30

echo "Starting Metabase backup: $DATE"

# Backup Metabase data volume
docker run --rm -v oss-metabase-data:/source -v "$BACKUP_DIR":/backup alpine \
  tar czf /backup/metabase-prod-$DATE.tar.gz -C /source .

# Backup DuckDB database
cp /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb \
   "$BACKUP_DIR/oea-prod-$DATE.duckdb"

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.duckdb" -mtime +$RETENTION_DAYS -delete

echo "Backup complete: $DATE"
echo "Backup size: $(du -sh $BACKUP_DIR)"
SCRIPT

# Make executable
chmod +x /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backup-production.sh

# Test backup
./backup-production.sh
```

**Schedule Daily Backup (macOS):**

```bash
# Create launchd plist for daily backup at 2:00 AM
cat > ~/Library/LaunchAgents/com.oss.metabase.backup.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.oss.metabase.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backup-production.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups/backup.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/backups/backup-error.log</string>
</dict>
</plist>
PLIST

# Load launchd job
launchctl load ~/Library/LaunchAgents/com.oss.metabase.backup.plist

# Verify scheduled
launchctl list | grep metabase
```

**For Linux servers:**

```bash
# Add to crontab
crontab -e

# Add this line (runs daily at 2:00 AM):
0 2 * * * /path/to/backup-production.sh >> /path/to/backups/backup.log 2>&1
```

---

## Option B: Separate Production Server

**Scenario**: Deploy Metabase to a dedicated production server.

### Prerequisites

**Production Server Requirements**:
- OS: Ubuntu 22.04 LTS or macOS
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 500GB minimum (for Metabase data + backups)
- Docker installed and running
- Network: Accessible by district staff (not public internet)

---

### Step 1: Provision Production Server

**If using cloud provider (AWS, Azure, GCP):**

```bash
# Example: AWS EC2
- Instance type: t3.large (2 vCPU, 8GB RAM)
- OS: Ubuntu 22.04 LTS
- Storage: 500GB EBS volume
- Security group: Allow port 443 (HTTPS) from district IP range only
```

**If using on-premises server:**
- Install Ubuntu Server 22.04 LTS
- Configure static IP
- Install Docker and Docker Compose

---

### Step 2: Install Docker on Production Server

```bash
# SSH into production server
ssh admin@production-server

# Install Docker (Ubuntu)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for group to take effect
```

---

### Step 3: Transfer Configuration to Production

**On development machine:**

```bash
# Create deployment package
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
tar czf metabase-production-deploy.tar.gz \
  docker-compose.yml \
  plugins/ \
  ../../data/oea.duckdb

# Copy to production server
scp metabase-production-deploy.tar.gz admin@production-server:/opt/metabase/
```

**On production server:**

```bash
# Extract deployment package
cd /opt/metabase
tar xzf metabase-production-deploy.tar.gz

# Update docker-compose.yml for production
nano docker-compose.yml
# Follow same changes as Option A (production labeling, increased memory)
```

---

### Step 4: Export Dev Dashboards & Users

**On development machine:**

1. **Export Metabase Configuration**:
   - Open Metabase: http://localhost:3000
   - Login as admin
   - Settings → Admin → Settings → Export
   - Save file: `metabase-export-[DATE].zip`

2. **Copy Export to Production Server**:
   ```bash
   scp metabase-export-20260127.zip admin@production-server:/opt/metabase/
   ```

---

### Step 5: Deploy Metabase on Production Server

**On production server:**

```bash
cd /opt/metabase

# Start Metabase
docker-compose up -d

# Watch startup logs
docker logs -f oss-metabase-prod

# Wait for initialization (60-90 seconds)
# Expected: "Metabase Initialization COMPLETE"
```

---

### Step 6: Import Dashboards & Users

**On production server:**

1. **Access Metabase**: http://[production-server-ip]:3000
2. **Complete Setup Wizard**:
   - Create admin account
   - Connect to DuckDB database (path: `/data/oea.duckdb`)
3. **Import Configuration**:
   - Settings → Admin → Settings → Import
   - Upload `metabase-export-20260127.zip`
   - Wait for import to complete (2-5 minutes)
4. **Verify Dashboards**:
   - Navigate to Collections → "OSS Analytics"
   - Confirm all 5 dashboards present and functional

---

### Step 7: Configure Reverse Proxy (HTTPS)

**For production, enable HTTPS using nginx:**

```bash
# Install nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/metabase

# Add this configuration:
server {
    listen 80;
    server_name analytics.yourdistrict.org;  # Replace with your domain

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name analytics.yourdistrict.org;

    # SSL certificates (will be generated by certbot)
    ssl_certificate /etc/letsencrypt/live/analytics.yourdistrict.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analytics.yourdistrict.org/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Metabase
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/metabase /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d analytics.yourdistrict.org
```

**Now access via HTTPS:**
```
https://analytics.yourdistrict.org
```

---

## Database Configuration

### DuckDB Connection Settings

**For production, ensure database connection is optimized:**

1. **Metabase Admin → Databases → "OSS Analytics"**
2. **Advanced Options**:
   - **Read-only mode**: ✅ **CRITICAL** (prevents accidental writes)
   - **Rerun queries for simple exploration**: ✅ Yes
   - **Choose when syncs and scans happen**: Every 6 hours (reduce overhead)
   - **Cache TTL**: 24 hours (data refreshes daily, so cache can be long)

3. **Performance Tuning**:
   - **Max connections**: 10 (concurrent queries)
   - **Query timeout**: 30 seconds (fail slow queries)

---

## User Account Setup

### Create User Accounts for All Stakeholders

**Metabase Admin → People → Add Person**

**User Account Template:**

| Role | Group | # Users | Permissions |
|------|-------|---------|-------------|
| **Superintendent** | Administrators | 1-2 | Full access (all dashboards) |
| **Data Director** | Administrators | 1-2 | Full access, can create queries |
| **Principals** | School Leaders | 10-20 | Dashboards 1, 4 (school-filtered) |
| **Counselors** | Student Support | 15-30 | Dashboards 2, 3 (school/grade-filtered) |
| **Teachers** | Teachers | 100-500 | Dashboard 4 only (own classes) |
| **Board Members** | Board | 5-7 | Dashboards 1, 3, 5 (aggregated, no names) |

**Create Groups:**

1. **Settings → Admin → People → Groups**
2. **Create Groups**:
   - `Administrators` (full access)
   - `School Leaders` (principals, APs)
   - `Student Support` (counselors, social workers)
   - `Teachers` (classroom teachers)
   - `Board Members` (trustees)

**Assign Permissions:**

1. **Settings → Admin → Permissions**
2. **For each group, configure**:
   - Database access: "OSS Analytics"
   - Collection access: "OSS Analytics" collection
   - Dashboard access: Specific dashboards per role (see table above)

---

## Security Hardening

### 1. Enable Audit Logging

**Settings → Admin → Audit**:
- ✅ Enable audit logging
- Log all: Dashboard views, Query runs, User logins, Permission changes

**Storage**: Logs stored in Metabase database, viewable by admins only

---

### 2. Configure Session Timeout

**Settings → Admin → Settings → Authentication**:
- **Session timeout**: 8 hours (expires at end of workday)
- **Remember me**: Disabled (users must re-login)

---

### 3. Restrict Access by IP

**Docker Compose** (Option A):

```yaml
# Edit docker-compose.yml
services:
  metabase-prod:
    # ... existing config ...
    networks:
      - metabase-net

networks:
  metabase-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Internal network only
```

**Nginx** (Option B - production server):

```nginx
# Add to nginx config
location / {
    # Allow district IP range only
    allow 10.0.0.0/8;       # Example: district network
    allow 192.168.1.0/24;   # Example: admin network
    deny all;               # Block everyone else

    proxy_pass http://localhost:3000;
}
```

---

### 4. Data Masking for Sensitive Fields

**Configure in Metabase Admin → Data Model:**

1. **Student IDs**: Hash or mask (show only last 4 digits)
2. **Teacher IDs**: Hash or mask
3. **Student names**: Visible only to roles with legitimate educational interest

**Row-Level Security**:
- Principals: See only their school's data
- Counselors: See only their assigned grade levels
- Teachers: See only their own classes

---

## Post-Deployment Verification

### Verification Checklist (Run After Deployment)

```bash
# 1. Container is running
docker ps | grep metabase-prod
# Expected: Container status = healthy

# 2. Health check passes
curl http://localhost:3000/api/health
# Expected: {"status":"ok"}

# 3. Test dashboard query
curl -X POST http://localhost:3000/api/card/1/query \
  -H "Content-Type: application/json" \
  -d '{}' \
  --cookie "metabase.SESSION=[your-session-cookie]"
# Expected: JSON response with query results, response time <2 seconds

# 4. Check logs for errors
docker logs --tail 100 oss-metabase-prod | grep -i error
# Expected: No critical errors

# 5. Verify backups exist
ls -lh /path/to/backups/
# Expected: Recent backup files (<24 hours old)
```

**Manual Verification (via UI):**

1. **Test Each User Role**:
   - Login as each role (admin, principal, counselor, teacher, board member)
   - Verify correct dashboards visible
   - Verify correct data filtering (can't see other schools/teachers)

2. **Performance Check**:
   - Open each dashboard
   - Time how long it takes to load (should be <5 seconds)
   - Apply filters and time response (should be <2 seconds)

3. **Export Test**:
   - Export dashboard as PDF (should work)
   - Export table as CSV (should work)

4. **Security Test**:
   - Try to access another teacher's data (should fail)
   - Try to access student names as board member (should not be visible)

---

## Backup & Disaster Recovery

### Backup Strategy

| What | Frequency | Retention | Location |
|------|-----------|-----------|----------|
| **Metabase data volume** | Daily (2:00 AM) | 30 days | Local disk + offsite |
| **DuckDB database** | Daily (2:00 AM) | 30 days | Local disk + offsite |
| **Configuration export** | Weekly | 90 days | Local disk |

---

### Restore Procedures

#### Scenario 1: Metabase Data Corruption

**Symptoms**: Dashboards missing, users gone, login fails

**Solution**: Restore from backup

```bash
# Stop container
docker-compose down

# Delete corrupted volume
docker volume rm oss-metabase-data

# Restore from backup
cd /path/to/backups
docker run --rm -v oss-metabase-data:/target -v $(pwd):/backup alpine \
  tar xzf /backup/metabase-prod-[DATE].tar.gz -C /target

# Restart container
docker-compose up -d

# Verify
curl http://localhost:3000/api/health
```

**Downtime**: 5-10 minutes

---

#### Scenario 2: DuckDB Database Corruption

**Symptoms**: Queries fail, "database locked" errors

**Solution**: Restore DuckDB backup

```bash
# Stop Metabase (releases database lock)
docker-compose down

# Restore database
cd /path/to/backups
cp oea-prod-[DATE].duckdb /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Restart Metabase
docker-compose up -d

# Verify queries work
# Open any dashboard and check if visualizations load
```

**Downtime**: 5-10 minutes

---

#### Scenario 3: Complete Server Failure

**Symptoms**: Server crashed, hardware failure, VM terminated

**Solution**: Rebuild on new server

1. **Provision new server** (see Option B)
2. **Install Docker**
3. **Copy backups** to new server:
   ```bash
   scp backups/*.tar.gz admin@new-server:/opt/metabase/backups/
   ```
4. **Deploy Metabase** (follow Option B steps)
5. **Restore data volume** (see Scenario 1)
6. **Restore DuckDB** (see Scenario 2)
7. **Update DNS** (if using domain name)
8. **Notify users** of new IP/URL

**Downtime**: 1-2 hours

---

## Monitoring & Maintenance

### Daily Health Checks

**Automated Monitoring Script:**

```bash
# Create monitoring script
cat > /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/monitor-health.sh << 'SCRIPT'
#!/bin/bash
# Metabase Health Check Script
# Run via cron every 15 minutes

LOG_FILE="/path/to/metabase/logs/health-check.log"
ALERT_EMAIL="admin@district.org"

# Check if container is running
if ! docker ps | grep -q oss-metabase-prod; then
    echo "[$(date)] ERROR: Metabase container not running" >> "$LOG_FILE"
    echo "Metabase container is DOWN" | mail -s "ALERT: Metabase Down" "$ALERT_EMAIL"
    exit 1
fi

# Check health endpoint
HEALTH=$(curl -s http://localhost:3000/api/health)
if [[ "$HEALTH" != '{"status":"ok"}' ]]; then
    echo "[$(date)] ERROR: Health check failed: $HEALTH" >> "$LOG_FILE"
    echo "Metabase health check failed: $HEALTH" | mail -s "ALERT: Metabase Unhealthy" "$ALERT_EMAIL"
    exit 1
fi

# Check query performance (test dashboard load time)
START=$(date +%s)
curl -s http://localhost:3000/api/dashboard/1 > /dev/null
END=$(date +%s)
DURATION=$((END - START))

if [ "$DURATION" -gt 5 ]; then
    echo "[$(date)] WARNING: Dashboard load time: ${DURATION}s (threshold: 5s)" >> "$LOG_FILE"
    echo "Metabase performance degraded: ${DURATION}s load time" | mail -s "WARNING: Metabase Slow" "$ALERT_EMAIL"
fi

echo "[$(date)] OK: Health check passed, load time: ${DURATION}s" >> "$LOG_FILE"
SCRIPT

chmod +x monitor-health.sh
```

**Schedule Monitoring (every 15 minutes):**

```bash
# Add to crontab
crontab -e

# Add this line:
*/15 * * * * /path/to/monitor-health.sh
```

---

### Weekly Maintenance Tasks

**Every Monday morning:**

1. **Review Logs**:
   ```bash
   docker logs --since 168h oss-metabase-prod | grep -i error > /tmp/metabase-errors.log
   # Review errors, address recurring issues
   ```

2. **Check Disk Space**:
   ```bash
   df -h /path/to/metabase
   # Ensure >20% free space
   ```

3. **Review Backup Status**:
   ```bash
   ls -lht /path/to/backups/ | head -10
   # Verify daily backups exist
   ```

4. **Check User Activity**:
   - Metabase Admin → Audit → View activity log
   - Identify unused accounts, remove if needed

---

### Monthly Maintenance Tasks

**First Monday of each month:**

1. **Update Metabase**:
   ```bash
   docker-compose pull  # Pull latest Metabase image
   docker-compose down
   docker-compose up -d
   # Test all dashboards after update
   ```

2. **Review Dashboard Usage**:
   - Metabase Admin → Audit → Dashboard views
   - Identify unused dashboards
   - Gather feedback from users

3. **Security Audit**:
   - Review user permissions
   - Check for suspicious login attempts
   - Update admin passwords

4. **Performance Review**:
   - Run slow query report
   - Optimize indexes if needed
   - Review database size growth

---

## Rollback Procedures

### When to Rollback

**Rollback to previous version if:**
- Critical bug discovered post-deployment
- Data integrity issues (incorrect calculations)
- Performance degradation (>10 second load times)
- Security breach detected

---

### Rollback Steps (Option A: Same-Server)

```bash
# 1. Stop production container
docker-compose down

# 2. Restore from pre-deployment backup
cd /path/to/backups
docker volume rm oss-metabase-data

docker run --rm -v oss-metabase-data:/target -v $(pwd):/backup alpine \
  tar xzf /backup/metabase-data-backup-[PRE-DEPLOY-DATE].tar.gz -C /target

# 3. Restore pre-deployment docker-compose.yml
cp docker-compose.yml.dev docker-compose.yml

# 4. Restart development version
docker-compose up -d

# 5. Notify users
# Subject: "Metabase Rollback - Temporary Outage"
# Body: "We've rolled back to the previous version due to [REASON]. Access restored."
```

**Downtime**: 10-15 minutes

---

### Rollback Steps (Option B: Separate Server)

**Keep development server running during production launch.**

If rollback needed:

1. **Update DNS** (point back to dev server IP)
2. **Notify users** via email
3. **Investigate issue** on production server
4. **Fix and redeploy** when ready

**Downtime**: <5 minutes (just DNS propagation)

---

## Launch Communication

### Pre-Launch Announcement (1 Week Before)

**Subject**: New Student Analytics Dashboards Launching [DATE]

**Body**:

> Dear [Role],
>
> We're excited to announce that our new Student Analytics Dashboards will be available starting **[DATE]** at **[TIME]**.
>
> **What You'll Get**:
> - Real-time student performance data
> - Easy-to-use visualizations
> - Export capabilities for reports
>
> **Your Access**:
> - URL: https://analytics.yourdistrict.org (or http://localhost:3000)
> - Username: [Your email]
> - Password: [Temporary password - you'll be prompted to change]
>
> **Training**:
> - [Date/Time]: Live training session (optional)
> - User guides: Available at [link to training materials]
>
> **Support**:
> - Email: analytics-support@district.org
> - Phone: (555) 123-4567
>
> We look forward to hearing your feedback!
>
> [Your Name]  
> [Title]

---

### Launch Day Communication

**Subject**: Student Analytics Dashboards NOW AVAILABLE

**Body**:

> The Student Analytics Dashboards are now live!
>
> **Access Now**: https://analytics.yourdistrict.org
>
> **Quick Start**:
> 1. Login with your credentials
> 2. Navigate to "OSS Analytics" collection
> 3. Click your dashboard (see user guide for which one)
>
> **Need Help?**
> - User guides: [link]
> - Support: analytics-support@district.org
>
> Thank you!

---

### Post-Launch Check-In (1 Week After)

**Subject**: How are the analytics dashboards working for you?

**Body**:

> It's been one week since we launched the Student Analytics Dashboards.
>
> **Quick Survey** (2 minutes):
> [Link to feedback form]
>
> Your feedback helps us improve!
>
> Thank you,  
> [Your Name]

---

## Success Criteria

**Deployment is successful when:**

- ✅ All 5 dashboards accessible from production URL
- ✅ All user accounts created and tested
- ✅ Role-based access controls functioning (security test passed)
- ✅ Query performance <2 seconds for all visualizations
- ✅ Backup automation working (verified backup exists)
- ✅ Monitoring alerts configured and tested
- ✅ ≥90% user satisfaction in first week (via feedback form)
- ✅ Zero critical issues in first 2 weeks

---

## Support & Troubleshooting

### Common Post-Launch Issues

| Issue | Solution |
|-------|----------|
| **Users can't login** | Reset password via Metabase Admin → People → Reset Password |
| **Dashboard loads slowly** | Check network connection, verify query performance |
| **Can't export CSV** | Verify browser allows downloads, check popup blocker |
| **See wrong data** | Verify user is logged in with correct role |
| **Container keeps restarting** | Check logs: `docker logs oss-metabase-prod`, verify disk space |

---

## Appendix

### Useful Commands

| Task | Command |
|------|---------|
| **Stop production** | `docker-compose down` |
| **Start production** | `docker-compose up -d` |
| **View logs (real-time)** | `docker logs -f oss-metabase-prod` |
| **View logs (last 100 lines)** | `docker logs --tail 100 oss-metabase-prod` |
| **Check health** | `curl http://localhost:3000/api/health` |
| **Backup now** | `./backup-production.sh` |
| **Restore from backup** | See "Backup & Disaster Recovery" section |
| **Update Metabase** | `docker-compose pull && docker-compose up -d` |
| **Check disk space** | `df -h` |
| **List backups** | `ls -lh /path/to/backups/` |

---

**Deployment Guide Version**: 1.0  
**Last Updated**: January 2026  
**Maintained By**: OSS Framework Team

**For questions or issues, contact**: [Project Lead] at [email@district.org]
