# Stage 4 - Task 4.01: Metabase Installation - Architectural Decisions

## Decision 1: Use Official Metabase Docker Image

**Context**: Need to install Metabase BI platform for OSS Framework analytics.

**Options Considered**:
1. Install Metabase directly on host (Java JAR)
2. Use official Docker image
3. Build custom Docker image with DuckDB driver pre-installed

**Decision**: Use official `metabase/metabase:latest` Docker image

**Rationale**:
- **Isolation**: Docker provides clean isolation from host system
- **Portability**: Easy to move to different environments (dev → prod)
- **Versioning**: Can pin to specific version if needed (`v0.48.0`)
- **Updates**: Simple upgrade path: `docker-compose pull && docker-compose up -d`
- **Official support**: Maintained by Metabase team, well-tested
- **No custom build complexity**: Plugins can be added via volume mount

**Trade-offs**:
- ✅ Pros: Easy deployment, consistent environment, portable
- ⚠️ Cons: Requires Docker (already a prerequisite), 503MB image size (acceptable)

---

## Decision 2: Use H2 Database for Metabase Metadata

**Context**: Metabase needs a database to store its own data (users, dashboards, queries, settings).

**Options Considered**:
1. H2 embedded database (file-based, no external server)
2. PostgreSQL (existing `sis-postgres` container)
3. Separate PostgreSQL container for Metabase
4. MySQL

**Decision**: Use H2 embedded database

**Rationale**:
- **Simplicity**: No external database server required
- **Single container**: Reduces operational complexity
- **Sufficient for use case**: Single-instance Metabase, ~10-20 users
- **Fast startup**: No external dependencies
- **Backup simplicity**: Single file to backup

**Trade-offs**:
- ✅ Pros: Simple, fast, self-contained, easy backup
- ⚠️ Cons: Cannot scale to multiple Metabase instances (not needed), slightly slower than PostgreSQL (negligible for this workload)

**Migration Path**: Can migrate to PostgreSQL later if High Availability (HA) is needed (documented in Metabase docs).

---

## Decision 3: Mount DuckDB Database as Read-Only

**Context**: Metabase needs access to DuckDB analytics database.

**Options Considered**:
1. Mount DuckDB as read-write
2. Mount DuckDB as read-only (`:ro`)
3. Copy DuckDB into container (separate copy)

**Decision**: Mount DuckDB as read-only (`:ro`)

**Rationale**:
- **Data integrity**: Prevents accidental writes from Metabase
- **Single source of truth**: DuckDB is only written by dbt (nightly refresh)
- **Security best practice**: Least privilege principle
- **No performance impact**: Metabase only reads data (BI tool)

**Implementation**:
```yaml
volumes:
  - ../../data:/data:ro  # Read-only mount
```

**Trade-offs**:
- ✅ Pros: Data safety, prevents corruption, clear ownership (dbt writes, Metabase reads)
- ⚠️ Cons: None for this use case (Metabase should never write to analytics DB)

---

## Decision 4: Use Named Volume for Metabase Data Persistence

**Context**: Metabase metadata must persist across container restarts/upgrades.

**Options Considered**:
1. Named Docker volume (`oss-metabase-data`)
2. Bind mount to host directory (`./metabase-data`)
3. No persistence (ephemeral, recreate on restart)

**Decision**: Use named Docker volume

**Rationale**:
- **Docker best practice**: Volumes managed by Docker
- **Portability**: Volume can be backed up/restored via Docker commands
- **No host path dependencies**: Works across different host systems
- **Permissions simplicity**: Docker manages permissions automatically

**Implementation**:
```yaml
volumes:
  metabase-data:
    driver: local
    name: oss-metabase-data
```

**Trade-offs**:
- ✅ Pros: Portable, managed by Docker, easy backup (`docker volume backup`)
- ⚠️ Cons: Slightly less transparent than bind mount (can't browse with `ls`), but can inspect with `docker volume inspect`

**Backup Strategy**:
```bash
# Backup
docker cp oss-metabase:/metabase-data/metabase.db.mv.db ./backup.db

# Restore (if needed)
docker cp ./backup.db oss-metabase:/metabase-data/metabase.db.mv.db
docker-compose restart
```

---

## Decision 5: Expose Metabase on Port 3000 (Localhost Only)

**Context**: Need to choose port mapping and network exposure.

**Options Considered**:
1. Port 3000 (Metabase default), localhost only
2. Port 80 (HTTP), localhost only
3. Port 3000, exposed to network (`0.0.0.0`)
4. Port 3000, behind reverse proxy (nginx)

**Decision**: Port 3000, localhost only (Docker default: `0.0.0.0:3000→3000` binds to all interfaces but typically firewalled)

**Rationale**:
- **Familiarity**: 3000 is Metabase standard (documentation consistency)
- **No port conflicts**: Verified available (port 3001 used by another Metabase instance)
- **Security**: Not exposed to internet (no external access without proxy)
- **Development-friendly**: Easy to access during testing phase

**Implementation**:
```yaml
ports:
  - "3000:3000"  # host:container
```

**Future Consideration**: For production, add nginx reverse proxy with HTTPS/TLS (Task 4.09 deployment phase).

**Trade-offs**:
- ✅ Pros: Standard port, no conflicts, simple configuration
- ⚠️ Cons: No HTTPS (acceptable for localhost, add proxy for production)

---

## Decision 6: Allocate 2GB Java Heap to Metabase

**Context**: Metabase is a Java application requiring heap memory configuration.

**Options Considered**:
1. Default (typically 1GB)
2. 2GB (recommended for medium workloads)
3. 4GB (for large workloads)
4. 512MB (minimal)

**Decision**: 2GB max heap (`-Xmx2g`), 512MB initial (`-Xms512m`)

**Rationale**:
- **Analytics workload**: 3,400 students, 5 views, ~10 concurrent users
- **Metabase recommendation**: 2GB sufficient for up to 10,000 rows/query
- **Host resources**: Development machine with adequate RAM
- **Performance vs. cost**: Balances speed with resource usage

**Implementation**:
```yaml
environment:
  JAVA_OPTS: "-Xmx2g -Xms512m"
```

**Monitoring Plan**: Use `docker stats oss-metabase` to track actual usage. Increase if consistently near limit.

**Trade-offs**:
- ✅ Pros: Adequate for workload, leaves room for host processes
- ⚠️ Cons: May be overkill for current dataset (24MB), but allows growth

---

## Decision 7: Use `unless-stopped` Restart Policy

**Context**: Determine container restart behavior after crashes/reboots.

**Options Considered**:
1. `no` - Never restart
2. `always` - Always restart (even if manually stopped)
3. `unless-stopped` - Restart unless manually stopped
4. `on-failure` - Only restart on error

**Decision**: `unless-stopped`

**Rationale**:
- **Auto-recovery**: Restarts on host reboot (important for production-like deployment)
- **Respects manual stops**: `docker stop oss-metabase` won't trigger restart
- **Crash recovery**: Restarts on unexpected failures
- **Operator control**: Allows maintenance without constant restarts

**Implementation**:
```yaml
restart: unless-stopped
```

**Trade-offs**:
- ✅ Pros: Balanced automation and control
- ⚠️ Cons: None identified (best practice for this use case)

---

## Decision 8: Create Plugins Directory for Future DuckDB Driver

**Context**: Metabase may not include native DuckDB driver.

**Options Considered**:
1. Pre-install DuckDB JDBC driver in custom image
2. Create empty plugins directory, document installation
3. Don't prepare for DuckDB driver (use Generic SQL)

**Decision**: Create empty `plugins/` directory, mount as volume, document driver installation

**Rationale**:
- **Flexibility**: Can add driver without rebuilding image
- **Official image unchanged**: Stays compatible with upstream updates
- **User choice**: Driver can be added if needed (documented in README.md)
- **No bloat**: Empty directory adds no overhead

**Implementation**:
```yaml
volumes:
  - ./plugins:/plugins:ro
```

**Documentation**: README.md Section "Issue: DuckDB Driver Not Found" includes curl command to download JDBC driver.

**Trade-offs**:
- ✅ Pros: Flexible, maintainable, documented
- ⚠️ Cons: Manual step if driver needed (acceptable, may not be required)

---

## Decision 9: Document Manual Setup Steps (Don't Automate)

**Context**: Metabase requires initial setup wizard (admin account, database connection) on first run.

**Options Considered**:
1. Automate setup via Metabase API (curl commands)
2. Pre-configure via environment variables
3. Document manual setup steps (browser-based)

**Decision**: Document manual setup steps in README.md

**Rationale**:
- **Security**: Admin password should be set by user (not hardcoded)
- **Database connection**: May require DuckDB driver installation (user-dependent)
- **Metabase design**: Setup wizard is intentionally interactive
- **API limitations**: Metabase API auth requires token (not available pre-setup)

**Documentation**: README.md Section "First-Time Setup (One-Time Only)" provides step-by-step wizard walkthrough.

**Trade-offs**:
- ✅ Pros: Secure (user sets password), flexible (user chooses database approach), aligns with Metabase design
- ⚠️ Cons: Not fully automated (requires 5 minutes of manual setup), acceptable for one-time configuration

---

## Decision 10: Include Comprehensive Troubleshooting Guide

**Context**: Metabase deployment may encounter common issues (port conflicts, driver missing, etc.).

**Options Considered**:
1. Minimal README (just installation steps)
2. Basic troubleshooting (common errors)
3. Comprehensive troubleshooting (symptoms, diagnostics, solutions)

**Decision**: Comprehensive troubleshooting guide in README.md

**Rationale**:
- **User empowerment**: District IT staff can self-solve issues
- **Reduces support burden**: Documented solutions for common problems
- **Professional quality**: Matches enterprise deployment standards
- **Future-proofing**: Covers scenarios encountered during testing

**Sections Included**:
- Port conflicts (with diagnostics and 2 solutions)
- Database connection failures (with verification steps)
- Container startup issues (with log analysis)
- Performance problems (with resource monitoring)
- DuckDB driver installation (with curl commands)
- Password reset (with destructive warning)

**Trade-offs**:
- ✅ Pros: Self-service, professional, comprehensive
- ⚠️ Cons: Long document (600+ lines), mitigated with Quick Reference Card and table of contents

---

## Summary of Key Decisions

| Decision | Choice | Primary Rationale |
|----------|--------|-------------------|
| Installation method | Official Docker image | Simplicity, portability, official support |
| Metadata storage | H2 embedded database | No external dependencies, sufficient for workload |
| DuckDB mount | Read-only | Data integrity, security, single source of truth |
| Data persistence | Named Docker volume | Portability, Docker best practice |
| Port | 3000 (localhost) | Standard, no conflicts, development-friendly |
| Memory allocation | 2GB heap | Adequate for analytics workload, room for growth |
| Restart policy | `unless-stopped` | Auto-recovery with operator control |
| DuckDB driver | Prepared plugins dir | Flexible, documented, no bloat |
| Setup automation | Manual (documented) | Security, flexibility, Metabase design |
| Documentation | Comprehensive | User empowerment, professional quality |

**All decisions support the core goal**: Production-ready Metabase deployment that is secure, maintainable, and well-documented for district IT staff handoff.
