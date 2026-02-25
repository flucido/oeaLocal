# Metabase Analytics - Administrator Guide

**Version**: 1.0  
**Last Updated**: January 2026  
**Audience**: System Administrators  
**Access Level**: Full System Access

---

## Overview

As a Metabase administrator, you have complete access to all system features including:
- ✅ All 5 analytics dashboards (no data restrictions)
- ✅ User management (create, edit, delete accounts)
- ✅ Database configuration and query optimization
- ✅ SQL editor (custom queries and data exploration)
- ✅ Dashboard creation and editing
- ✅ Permission management and access controls
- ✅ System settings and integrations

**Key Responsibilities**:
- Manage user accounts and permissions
- Monitor system performance and health
- Create and maintain dashboards
- Troubleshoot data issues
- Train end users

---

## Section 1: Your Dashboard Access

### Available Dashboards (5 Total)

You have access to **ALL dashboards** with **NO filters** applied by default:

| Dashboard | Purpose | Primary Users | Your Use Case |
|-----------|---------|---------------|---------------|
| **Dashboard 1: Chronic Absenteeism Risk** | Track students at risk of chronic absenteeism | Principals, Attendance Officers | System-wide monitoring, validate data accuracy |
| **Dashboard 2: Student Wellbeing Profiles** | Multi-domain risk assessment | Counselors, Case Managers | Identify high-risk students across district |
| **Dashboard 3: Equity Outcomes Analysis** | Demographic outcome gaps | Equity Officers, Board Members | Monitor equity metrics, identify disparities |
| **Dashboard 4: Class Effectiveness Comparison** | Teacher/class performance metrics | Principals, Teachers | Validate calculations, identify outliers |
| **Dashboard 5: Performance Correlations** | Statistical relationships between factors | Analysts, Researchers | Understand data patterns, validate models |

### Quick Access to Dashboards

1. **From Home Page**: Your dashboards appear in "Pick up where you left off"
2. **From Collections**: Click "Collections" (left sidebar) → "OSS Analytics" → Select dashboard
3. **From Search**: Type dashboard name in search bar (top right)

### Dashboard Actions You Can Perform

Unlike other users, you can:
- ✅ **Edit dashboards**: Click "⋯" → Edit Dashboard
- ✅ **Add visualizations**: Drag and drop new charts
- ✅ **Modify filters**: Change filter types and defaults
- ✅ **Archive dashboards**: Remove obsolete dashboards
- ✅ **Clone dashboards**: Duplicate for testing or customization
- ✅ **Export data**: No restrictions on data export

---

## Section 2: User Management

### Creating User Accounts

**Location**: Settings (gear icon) → Admin → People

**Steps to Create a User**:

1. Click **"Add someone"** (top right)
2. Fill in details:
   - **First name**: User's first name
   - **Last name**: User's last name
   - **Email**: District email address (used for login)
   - **Groups**: Select role-based group (see table below)
3. Click **"Create"**
4. Metabase sends password setup email to user
5. **Optional**: Manually set password by clicking user → "Reset password"

### Role-Based User Groups

Create these groups for permission management:

| Group Name | Access Level | Dashboards | Data Scope | Example Users |
|------------|--------------|------------|------------|---------------|
| **Admins** | Full access | All 5 dashboards | District-wide | System admins, Data analysts |
| **Principals** | Read-only | Dashboards 1, 4 | Filtered to their school | School principals, Assistant principals |
| **Counselors** | Read-only | Dashboards 2, 3 | Filtered to their school/grade | School counselors, Social workers |
| **Teachers** | Read-only | Dashboard 4 only | Filtered to their classes | Classroom teachers |
| **Board Members** | Read-only | Dashboards 1, 3, 5 | District-wide, aggregated (no names) | Board members, Trustees |

### How to Create User Groups

1. Go to **Settings → Admin → People → Groups**
2. Click **"Create a group"**
3. Enter group name (e.g., "Principals")
4. Click **"Create"**
5. Go to **Permissions** tab to set access (see Section 3)

### Managing Existing Users

**Edit User Details**:
- Settings → Admin → People → Click user name → Edit

**Reset Password**:
- Settings → Admin → People → Click user name → "Reset password"
- User receives email with reset link

**Deactivate User** (recommended over deletion):
- Settings → Admin → People → Click user name → "Deactivate"
- Preserves audit history, prevents login

**Reactivate User**:
- Settings → Admin → People → Show "Deactivated" → Click user → "Reactivate"

**Delete User** (permanent):
- Settings → Admin → People → Click user name → "Remove user"
- ⚠️ **Warning**: Cannot be undone, loses audit trail

### Bulk User Management

For adding many users at once:

**Option 1: SSO Integration** (Recommended for 50+ users)
- Settings → Admin → Authentication → Set up SSO
- Supports SAML, LDAP, Google OAuth
- Users auto-provisioned on first login

**Option 2: API Script** (Recommended for 10-50 users)
```bash
# Example: Create users from CSV using Metabase API
curl -X POST http://localhost:3000/api/user \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@district.edu",
    "group_ids": [2]
  }'
```

**Option 3: Manual Creation** (For <10 users)
- Use UI as described above

---

## Section 3: Permission Management

### Understanding Permission Levels

Metabase has 3 permission types:

| Permission Type | What It Controls |
|----------------|------------------|
| **Data Permissions** | Which databases and tables users can access |
| **Collection Permissions** | Which dashboards and saved questions users can see |
| **SQL Editor Access** | Whether users can write custom SQL queries |

### Configuring Data Permissions

**Location**: Settings → Admin → Permissions → Data

**Steps**:

1. Click **"Data Permissions"**
2. Select group (e.g., "Principals")
3. Select database ("OSS Analytics")
4. Choose permission level:
   - **No access**: Cannot see database
   - **Unrestricted**: Full access to all data
   - **Granular**: Set permissions per table/schema
   - **Block**: Explicitly deny access

**Recommended Configuration**:

| Group | Database Permission | Tables |
|-------|---------------------|--------|
| **Admins** | Unrestricted | All tables |
| **Principals** | Granular | Only `v_chronic_absenteeism_risk`, `v_class_section_comparison` |
| **Counselors** | Granular | Only `v_wellbeing_risk_profiles`, `v_equity_outcomes_by_demographics` |
| **Teachers** | Granular | Only `v_class_section_comparison` |
| **Board Members** | Granular | `v_chronic_absenteeism_risk`, `v_equity_outcomes_by_demographics`, `v_performance_correlations` |

### Configuring Collection Permissions

**Location**: Settings → Admin → Permissions → Collections

**Steps**:

1. Click **"Collection Permissions"**
2. Select collection (e.g., "OSS Analytics")
3. Select group (e.g., "Principals")
4. Choose permission level:
   - **No access**: Cannot see collection
   - **View**: Can view dashboards and questions
   - **Curate**: Can edit existing items, cannot create new

**Best Practice**:
- Create separate collections for each role
- Example structure:
  ```
  Collections/
    ├── OSS Analytics (admins only)
    ├── Principal Dashboards (principals + admins)
    ├── Counselor Dashboards (counselors + admins)
    ├── Teacher Dashboards (teachers + admins)
    └── Board Reports (board + admins)
  ```

### Configuring SQL Editor Access

**Location**: Settings → Admin → Permissions → SQL Queries

**Recommendation**:
- **Admins**: Allow SQL editor access (unrestricted)
- **All other roles**: Block SQL editor access
- **Reason**: Prevents accidental data exposure, enforces pre-built dashboards

**Steps**:
1. Click **"SQL Queries"** tab
2. Select database ("OSS Analytics")
3. For each group:
   - Admins: "Yes"
   - Others: "No"

### Row-Level Security (Filtering by School/Grade)

To restrict users to only their school's data:

**Option 1: Use Dashboard Filters with Defaults** (Easiest)
1. Edit dashboard
2. Add "School" filter
3. Click filter settings → "Default to user attribute"
4. Map to user attribute: `school_code`
5. Save dashboard

**Option 2: Create User Attributes**
1. Settings → Admin → People → Click user
2. Scroll to "Attributes"
3. Add attribute: `school_code = "Lincoln HS"`
4. Use this in dashboard filters (see Option 1)

**Option 3: Create Separate Views per School** (Most Secure)
1. Create SQL views: `v_chronic_absenteeism_risk_lincoln`, `v_chronic_absenteeism_risk_washington`, etc.
2. Assign permissions per view to appropriate groups
3. Downside: Maintenance overhead

**Recommendation**: Use **Option 1** (dashboard filters + user attributes) for simplicity.

---

## Section 4: Dashboard Creation & Management

### Creating a New Dashboard

**Steps**:

1. Click **"New"** (top right) → **"Dashboard"**
2. Enter dashboard name: "My Custom Dashboard"
3. Optional: Add description
4. Click **"Create"**
5. Click **"Add a question"** to add visualizations

### Adding Visualizations to Dashboard

**Method 1: Add Existing Saved Question**
1. Click **"Add a question"** on dashboard
2. Select from list of saved questions
3. Resize and position chart

**Method 2: Create New Question**
1. Click **"New"** → **"Question"**
2. Choose data source: "OSS Analytics"
3. Select table: e.g., `v_chronic_absenteeism_risk`
4. Build query using visual query builder
5. Click **"Visualize"**
6. Choose chart type (bar, line, pie, table, etc.)
7. Click **"Save"** → Add to dashboard

**Method 3: Write SQL Query** (Admin only)
1. Click **"New"** → **"SQL Query"**
2. Select database: "OSS Analytics"
3. Write query:
   ```sql
   SELECT grade_level, COUNT(*) as student_count
   FROM main_main_analytics.v_chronic_absenteeism_risk
   WHERE wellbeing_risk_level = 'High'
   GROUP BY grade_level
   ORDER BY student_count DESC;
   ```
4. Click **"Visualize"**
5. Choose chart type
6. Click **"Save"** → Add to dashboard

### Dashboard Layout Best Practices

**Grid Layout**:
- Metabase uses 24-column grid
- Most visualizations: 6-12 columns wide (1/4 to 1/2 screen)
- KPI cards: 4-6 columns wide (1/6 to 1/4 screen)
- Full-width tables: 24 columns (entire screen)

**Visual Hierarchy**:
1. **Top row**: KPI metric cards (most important numbers)
2. **Second row**: Primary visualization (largest chart)
3. **Below**: Supporting charts (2-3 per row)
4. **Bottom**: Detailed tables (for drill-down)

**Example Layout**:
```
Row 1: [Total Students] [At-Risk Count] [% Change] [Avg Attendance]  (4 cards)
Row 2: [Risk Distribution Pie Chart      ] [Attendance Trend Line    ]  (2 charts)
Row 3: [School Comparison Bar Chart      ] [Top 20 At-Risk Table     ]  (2 viz)
Row 4: [Detailed Student List Table - Full Width                       ]  (1 table)
```

### Adding Dashboard Filters

**Steps**:

1. Click **"Edit"** on dashboard
2. Click **"Add a Filter"** (top right)
3. Choose filter type:
   - **Text**: For searching (student name, school)
   - **Number**: For numeric ranges (risk score, attendance %)
   - **Date**: For time ranges (last 30 days, custom range)
   - **Dropdown**: For categories (school, grade, risk level)
4. Configure filter:
   - Label: "School"
   - Type: "Dropdown"
   - Options: "From connected fields" or "Custom list"
5. Click **"Done"**
6. Connect filter to visualizations:
   - Click filter → "Connect to..."
   - Select which charts use this filter
   - Map to appropriate field (e.g., `primary_school`)
7. Click **"Save"**

### Dashboard Refresh Schedule

To auto-refresh dashboards:

1. Edit dashboard
2. Click **"⋯"** (top right) → **"Dashboard settings"**
3. Scroll to **"Auto-refresh"**
4. Set interval: 1 min / 5 min / 15 min / 1 hour / Never
5. **Recommendation**: Use 15 minutes or 1 hour (avoid server load)
6. Click **"Save"**

---

## Section 5: Database Management

### Monitoring Database Connection

**Check Connection Health**:

1. Settings → Admin → Databases
2. Click **"OSS Analytics"** database
3. Look for:
   - ✅ Green checkmark: "Connection looks good!"
   - ❌ Red X: "Connection failed"
4. If failed, click **"Test connection"** to diagnose

**Common Connection Issues**:

| Issue | Cause | Solution |
|-------|-------|----------|
| "File not found" | DuckDB file missing or moved | Verify `/data/oea.duckdb` exists in container |
| "Permission denied" | File permissions issue | Check file is readable: `chmod 644 oea.duckdb` |
| "Database locked" | Another process has file open | Close DuckDB CLI or other connections |
| "Driver not found" | DuckDB JDBC driver missing | Install driver in `/plugins/` directory |

### Running Manual Data Sync

Metabase caches database schema (tables, columns) for performance.

**When to Re-sync**:
- After adding new views to DuckDB
- After changing column names/types
- After dbt model updates

**Steps to Re-sync**:

1. Settings → Admin → Databases
2. Click **"OSS Analytics"**
3. Scroll to **"Database syncing"** section
4. Click **"Sync database schema now"**
5. Wait 10-30 seconds for completion
6. Refresh page to verify new tables appear

**Schedule Settings**:
- **Schema sync**: How often Metabase checks for new tables/columns
  - Recommendation: Every hour (default)
- **Scan field values**: How often Metabase updates dropdown options
  - Recommendation: Daily at 2 AM (after dbt refresh)

### Query Performance Monitoring

**View Slow Queries**:

1. Settings → Admin → Performance
2. Click **"Query Performance"**
3. Sort by **"Average duration"** (slowest first)
4. Investigate queries taking > 5 seconds

**Optimization Strategies**:

| Issue | Solution |
|-------|----------|
| Query scans entire table | Add WHERE clause to filter rows |
| Joining large tables | Pre-aggregate in dbt view |
| Complex calculations | Move calculation to DuckDB view (faster) |
| Dashboard loads slowly | Cache dashboard results (see Caching section) |

### Enabling Query Caching

**What it does**: Stores query results for reuse, speeds up dashboard loads

**Steps**:

1. Settings → Admin → Caching
2. Toggle **"Enable caching"** to ON
3. Set **"Minimum query duration"**: 1 second (cache queries slower than this)
4. Set **"Cache Time-To-Live (TTL)**:
   - For frequently updated data: 15 minutes
   - For daily refreshed data: 24 hours (recommended for OSS Analytics)
5. Click **"Save changes"**

**Clear Cache** (when data is refreshed):
```bash
# Option 1: Clear via UI
Settings → Admin → Caching → "Clear cache now"

# Option 2: Clear via API
curl -X POST http://localhost:3000/api/cache/clear \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

---

## Section 6: Advanced Administration

### Audit Logging

Track user activity for security and compliance.

**Enable Audit Log**:
1. Settings → Admin → Audit
2. Toggle **"Enable audit logging"** to ON
3. Configure retention: 90 days (default)

**View Audit Log**:
1. Settings → Admin → Audit → "View logs"
2. Filter by:
   - User: Which user performed action
   - Event: Login, Query, Export, Edit, Delete
   - Date range: Last 7/30/90 days

**Common Use Cases**:
- Track data exports (FERPA compliance)
- Monitor failed login attempts (security)
- Audit dashboard changes (change management)
- Investigate slow queries (performance)

### Email Configuration (Alerts & Reports)

**Configure SMTP**:

1. Settings → Admin → Email
2. Enter SMTP details:
   - **SMTP Host**: `smtp.gmail.com` (or your mail server)
   - **SMTP Port**: 587 (TLS) or 465 (SSL)
   - **Username**: Your email address
   - **Password**: App-specific password
   - **From Address**: `analytics@district.edu`
3. Click **"Save changes"**
4. Click **"Send test email"** to verify

**Set Up Automated Reports**:

1. Open dashboard
2. Click **"⋯"** → **"Subscriptions"**
3. Click **"Create a subscription"**
4. Configure:
   - **Recipients**: Email addresses
   - **Frequency**: Daily / Weekly / Monthly
   - **Time**: 8:00 AM (recommended)
   - **Format**: PDF or CSV
5. Click **"Done"**

**Example Use Cases**:
- Daily attendance report to principals (8 AM)
- Weekly risk summary to counselors (Monday 9 AM)
- Monthly equity report to board (1st of month, 6 PM)

### Slack Integration (Optional)

Send dashboard alerts to Slack channels.

**Steps**:

1. Settings → Admin → Slack
2. Click **"Connect to Slack"**
3. Authorize Metabase app in your Slack workspace
4. Configure:
   - **Default channel**: `#data-analytics`
   - **Bot name**: "Metabase Bot"
5. Click **"Save"**

**Create Slack Alert**:

1. Open dashboard
2. Click **"⋯"** → **"Subscriptions"**
3. Choose **"Send to Slack"**
4. Select channel: `#counselor-alerts`
5. Set frequency and conditions

**Example Use Cases**:
- Alert when >10 students move to "Critical" risk
- Notify when attendance drops below 80% at any school
- Weekly summary of key metrics to leadership channel

### Backup & Disaster Recovery

**What to Back Up**:
- Metabase metadata database (H2 file): `/metabase-data/metabase.db.mv.db`
- Contains: users, dashboards, saved questions, permissions, settings

**Backup Method 1: Docker Volume Backup**
```bash
# Stop Metabase
docker-compose down

# Backup volume
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/metabase-backup-$(date +%Y%m%d).tar.gz /data

# Restart Metabase
docker-compose up -d
```

**Backup Method 2: Copy H2 File**
```bash
# While Metabase is running
docker cp oss-metabase:/metabase-data/metabase.db.mv.db \
  ./backups/metabase-$(date +%Y%m%d).db
```

**Restore from Backup**:
```bash
# Stop Metabase
docker-compose down

# Remove current volume
docker volume rm oss-metabase-data

# Recreate volume and restore
docker volume create oss-metabase-data
docker run --rm -v oss-metabase-data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/metabase-backup-YYYYMMDD.tar.gz -C /

# Restart Metabase
docker-compose up -d
```

**Backup Schedule Recommendation**:
- **Frequency**: Daily (automated cron job)
- **Retention**: Keep last 30 days
- **Storage**: Off-server location (S3, NAS)

---

## Section 7: Troubleshooting Admin Issues

### Issue: User Cannot Log In

**Diagnostic Steps**:

1. **Check account status**:
   - Settings → Admin → People → Find user
   - Status: Active or Deactivated?

2. **Check group membership**:
   - Click user → "Groups"
   - Must be in at least one group

3. **Check permissions**:
   - Settings → Admin → Permissions → Data
   - Verify group has database access

4. **Check audit log**:
   - Settings → Admin → Audit
   - Filter by user email
   - Look for failed login attempts

**Solutions**:
- Reactivate deactivated account
- Reset password: User → "Reset password"
- Add user to appropriate group
- Clear browser cache/cookies

### Issue: Dashboard Shows "No Results"

**Diagnostic Steps**:

1. **Run test query directly**:
   - New → SQL Query
   - `SELECT COUNT(*) FROM main_main_analytics.v_chronic_absenteeism_risk;`
   - Should return 3,400 rows

2. **Check dashboard filters**:
   - Are filters too restrictive?
   - Try resetting filters: Click "Reset"

3. **Check data permissions**:
   - Settings → Admin → Permissions → Data
   - Does user's group have access to this table?

4. **Check for DuckDB connection issue**:
   - Settings → Admin → Databases → OSS Analytics
   - Click "Test connection"

**Solutions**:
- Re-sync database schema
- Adjust or remove restrictive filters
- Grant data permissions to user's group
- Verify DuckDB file exists and is readable

### Issue: Query Takes Too Long (>10 seconds)

**Diagnostic Steps**:

1. **Identify slow query**:
   - Settings → Admin → Performance → Query Performance
   - Sort by average duration

2. **Check query complexity**:
   - Does query scan entire table?
   - Are there multiple joins?
   - Is there a complex calculation?

3. **Check DuckDB performance**:
   ```bash
   # Test query directly in DuckDB
   docker exec oss-metabase duckdb /data/oea.duckdb \
     "EXPLAIN SELECT * FROM main_main_analytics.v_chronic_absenteeism_risk;"
   ```

**Solutions**:
- **Add WHERE clause**: Filter data before aggregation
- **Pre-aggregate in dbt**: Move calculation to nightly dbt refresh
- **Enable caching**: Settings → Admin → Caching → Enable
- **Optimize view**: Contact dbt developer to optimize view query

### Issue: Dashboard Export Fails

**Common Causes**:

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "File too large" | Dashboard has too much data (>50MB) | Add filters to reduce data, or export individual charts |
| "Timeout" | Query takes too long | Increase timeout: Settings → Admin → General → Query timeout |
| "Permission denied" | User lacks export permission | Check group permissions: Settings → Admin → Permissions |
| "Invalid PDF" | Browser issue | Try different browser, or export as CSV instead |

### Issue: Metabase Crashes or Restarts

**Diagnostic Steps**:

1. **Check container logs**:
   ```bash
   docker logs --tail 200 oss-metabase
   ```

2. **Look for error patterns**:
   - `OutOfMemoryError` → Java heap too small
   - `StackOverflowError` → Query too complex
   - `Connection refused` → Database connection lost

3. **Check resource usage**:
   ```bash
   docker stats oss-metabase
   ```

**Solutions**:

| Issue | Solution |
|-------|----------|
| **Out of memory** | Increase heap size in `docker-compose.yml`: `JAVA_OPTS: "-Xmx4g"` |
| **Database connection lost** | Re-sync database: Settings → Admin → Databases → Sync |
| **Too many concurrent users** | Increase memory, enable caching, or scale horizontally |
| **Corrupted metadata** | Restore from backup (see Section 6) |

---

## Section 8: Security Best Practices

### Password Policy

**Recommended Settings** (Settings → Admin → General → Password):

- **Minimum length**: 12 characters
- **Complexity**: Require uppercase, lowercase, number, special character
- **Expiration**: 90 days (optional, for high-security environments)
- **Reuse prevention**: Cannot reuse last 5 passwords

**Enforce via**:
- Settings → Admin → Authentication → Password Complexity

### Two-Factor Authentication (2FA)

**Enable 2FA** (Enterprise feature, or use SSO with 2FA):

1. Settings → Admin → Authentication
2. Select "SSO" → "SAML" or "LDAP"
3. Configure with identity provider (e.g., Okta, Azure AD)
4. Enable 2FA in identity provider settings

**Alternative**: Require VPN access to Metabase server (network-level 2FA)

### API Key Management

**Create API Key** (for programmatic access):

1. Settings → Admin → People → Your account
2. Click **"API Keys"** tab
3. Click **"Create API Key"**
4. Enter description: "Python Analytics Script"
5. Copy key immediately (only shown once)
6. Store securely (e.g., environment variable, password manager)

**Best Practices**:
- ✅ Use separate API keys per application
- ✅ Set expiration dates (e.g., 90 days)
- ✅ Revoke unused keys immediately
- ❌ Never commit API keys to git
- ❌ Never share API keys via email/Slack

### Data Privacy (FERPA Compliance)

**Critical Settings**:

1. **Disable public sharing**:
   - Settings → Admin → Public Sharing → "Enable Public Sharing" → OFF
   - Prevents anonymous access to dashboards

2. **Audit data exports**:
   - Settings → Admin → Audit → Filter by event: "Export"
   - Review monthly for unauthorized exports

3. **Minimum cell size suppression**:
   - Modify dbt views to suppress cells with <10 students
   - Example: `WHERE student_count >= 10`

4. **Row-level security**:
   - Use user attributes to filter data by school (see Section 3)
   - Principals only see their school's students

5. **Disable SQL editor** for non-admin users:
   - Settings → Admin → Permissions → SQL Queries → No

**Staff Training Reminders**:
- FERPA requires training on student data privacy
- Include Metabase usage in annual FERPA training
- Document: "Only export data for approved purposes"

---

## Quick Reference for Admins

### Common Admin Tasks

| Task | Location | Shortcut |
|------|----------|----------|
| **Create user** | Settings → Admin → People → Add someone | — |
| **Reset password** | Settings → Admin → People → [User] → Reset | — |
| **Grant dashboard access** | Settings → Admin → Permissions → Collections | — |
| **Re-sync database** | Settings → Admin → Databases → [DB] → Sync | — |
| **View audit log** | Settings → Admin → Audit → View logs | — |
| **Clear cache** | Settings → Admin → Caching → Clear cache | — |
| **Create dashboard** | New → Dashboard | Cmd+K → "dash" |
| **Write SQL query** | New → SQL Query | Cmd+K → "sql" |
| **Export dashboard** | [Dashboard] → ⋯ → Download PDF | — |
| **Schedule report** | [Dashboard] → ⋯ → Subscriptions | — |

### Emergency Contacts

| Issue | Contact | Response Time |
|-------|---------|---------------|
| **System down** | IT Helpdesk: `support@district.edu` | 1 hour |
| **Data accuracy issue** | Data Team: `analytics@district.edu` | 24 hours |
| **Security incident** | Security: `security@district.edu` | Immediate |
| **FERPA question** | Compliance: `compliance@district.edu` | 24 hours |

---

## Additional Resources

### Documentation
- **Metabase Official Docs**: https://www.metabase.com/docs/latest/
- **OSS Framework README**: `/oss_framework/deployment/metabase/README.md`
- **DuckDB SQL Reference**: https://duckdb.org/docs/sql/introduction

### Training Materials
- **Quick Start Guide**: `quick-start-guide.md` (share with all users)
- **Troubleshooting Guide**: `troubleshooting-guide.md`
- **FAQ**: `faq.md`

### Getting Help
- **Metabase Community Forum**: https://discourse.metabase.com/
- **Email Support**: analytics@district.edu

---

**Last Updated**: January 2026  
**Document Owner**: OSS Framework Data Team  
**Review Schedule**: Quarterly

