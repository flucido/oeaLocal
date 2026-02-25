# Stage 4 Implementation Decisions

## [2026-01-27 05:52 UTC] Decision: Docker-based Metabase Deployment

### Context
Need to deploy Metabase BI platform for OSS Framework analytics dashboards.

### Options Considered
1. **Docker Compose** (standalone container)
2. **Standalone JAR** (java -jar metabase.jar)
3. **Kubernetes** (production cluster)
4. **Cloud-hosted** (Metabase Cloud)

### Decision
**Selected: Docker Compose** (Option 1)

### Rationale
- **Simplicity**: Single `docker-compose up -d` command to start
- **Isolation**: Containerized environment prevents conflicts
- **Portability**: Can move to any Docker host
- **Consistency**: Same environment dev → production
- **Resource control**: Easy to set memory limits (2GB heap)
- **Backup/restore**: Simple volume management
- **No licensing costs**: Open-source self-hosted

**Rejected Option 2 (Standalone JAR)**:
- Requires Java runtime on host
- Manual process management (systemd/init.d)
- Harder to manage multiple instances
- No resource isolation

**Rejected Option 3 (Kubernetes)**:
- Overkill for single-instance deployment
- Adds complexity (pods, services, ingress)
- Higher operational overhead
- Not needed for <5K students

**Rejected Option 4 (Cloud-hosted)**:
- Monthly costs ($85+/month)
- Data leaves district control (compliance risk)
- Internet dependency
- Vendor lock-in

### Implementation Details
- **Image**: `metabase/metabase:latest` (official)
- **Metadata DB**: H2 (simple, single-file)
- **Data mount**: DuckDB read-only at `/data/oea.duckdb`
- **Port**: 3000 (host) → 3000 (container)
- **Memory**: 2GB max heap (`-Xmx2g`)
- **Restart policy**: `unless-stopped` (auto-restart)

### Consequences
✅ Easy to deploy and maintain
✅ District retains data control
✅ No ongoing costs
✅ Portable across environments
⚠️ Requires Docker on host (acceptable trade-off)
⚠️ H2 not suitable for high concurrency (OK for <50 users)

### Alternatives for Scale
If user base exceeds 50 concurrent users:
- Switch to PostgreSQL for Metabase metadata
- Add Redis for caching
- Deploy multiple Metabase instances (load balanced)

---

## [2026-01-27 05:53 UTC] Decision: Read-Only DuckDB Mount

### Context
Metabase needs access to DuckDB analytics database. Need to prevent accidental data modifications.

### Decision
**Mount DuckDB database as read-only** (`:ro` flag)

### Rationale
- **Data safety**: Prevents accidental writes/deletes from Metabase
- **Compliance**: Audit requirement (analytics should not modify source data)
- **Performance**: Read-only hint may enable DuckDB optimizations
- **Multi-access**: Allows other processes to read simultaneously

### Implementation
```yaml
volumes:
  - ../../data:/data:ro  # Read-only mount
```

### Verification
```bash
docker exec oss-metabase touch /data/test.txt
# Expected: Permission denied (read-only file system)
```

### Consequences
✅ Data integrity protected
✅ Compliance-friendly (separation of concerns)
⚠️ If Metabase needs write access (e.g., for caching), would require separate writable volume

---

## [2026-01-27 05:54 UTC] Decision: H2 for Metabase Metadata (Not PostgreSQL)

### Context
Metabase requires a database to store its own metadata (users, dashboards, queries, settings).

### Options Considered
1. **H2** (embedded Java database, single file)
2. **PostgreSQL** (separate database server)
3. **MySQL** (separate database server)

### Decision
**Selected: H2** (Option 1)

### Rationale
- **Simplicity**: No separate database server to manage
- **Single file**: Easy backup/restore (`metabase.db.mv.db`)
- **Zero configuration**: Works out-of-box
- **Lightweight**: No additional containers/services
- **Sufficient for use case**: <50 concurrent users, <1000 dashboards

**Rejected PostgreSQL/MySQL**:
- Requires separate Docker container or external server
- Adds complexity (connection strings, user management)
- Overkill for small/medium deployment
- More moving parts = more failure points

### When to Switch to PostgreSQL
Consider upgrading if:
- Concurrent users exceed 50
- Database size exceeds 10GB
- Need high-availability (H2 is single-file, no replication)
- Experience performance issues

Migration path:
1. Export Metabase metadata: Settings → Admin → Troubleshooting → Export
2. Deploy PostgreSQL container
3. Update `MB_DB_TYPE=postgres` in docker-compose.yml
4. Import metadata into new instance

### Consequences
✅ Simple deployment and maintenance
✅ Easy backup (single file copy)
✅ Fast startup time
⚠️ Single point of failure (no replication)
⚠️ Concurrent user limit (~50 users)

---

## [2026-01-27 05:56 UTC] Decision: Manual Setup Required (Cannot Automate)

### Context
Need to initialize Metabase with admin account and database connection. Explored automation options.

### Decision
**Require manual browser-based setup** by end user

### Rationale
- **Security**: Admin password should be set by user (not stored in code)
- **Compliance**: Audit trail requires human-initiated setup
- **Reliability**: Metabase setup wizard is the supported path
- **Maintainability**: Automation would break on Metabase version changes

**Why automation was rejected**:
1. **API approach**: Metabase API requires existing admin credentials (chicken-egg problem)
2. **Playwright approach**: Would require storing user password in code (security violation)
3. **H2 injection approach**: Would require reverse-engineering H2 schema (brittle, breaks on updates)
4. **Bootstrap token approach**: Only available during first-time setup, expires after use

### User Experience Impact
- **Time cost**: 10-15 minutes of user effort
- **Benefit**: User controls admin credentials
- **Documentation**: Comprehensive README.md with step-by-step wizard guide

### Implementation
Created detailed documentation at:
`/oss_framework/deployment/metabase/README.md`
- Section: "First-Time Setup (One-Time Only)"
- Screenshots described in text
- Step-by-step instructions
- Troubleshooting guide
- Test query to verify success

### Consequences
✅ Secure (user controls credentials)
✅ Compliant (human-initiated setup)
✅ Maintainable (follows Metabase supported path)
⚠️ Requires 10-15 min user action
⚠️ Blocks Tasks 4.02-4.06 until complete

### Alternative Considered
**Metabase Enterprise "Configuration as Code"**:
- Allows YAML-based configuration
- Automates dashboard deployment
- ❌ Rejected: Requires paid Enterprise license ($500+/month)

---

**Session**: ses_402778e39ffe8SxgboI76RS5OR  
**Plan**: stage-4-metabase-dashboards  
**Progress**: 1/10 tasks complete
