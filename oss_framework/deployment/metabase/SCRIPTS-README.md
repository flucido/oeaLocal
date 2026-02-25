# Dashboard Creation Scripts - README

## Overview

This directory contains scripts to automate Metabase dashboard creation for the OSS Analytics platform.

## Available Scripts

### 1. `create-dashboards-api.py` ⭐ **RECOMMENDED**

**Purpose**: Create all 5 dashboards programmatically using Metabase REST API

**Advantages**:
- ✅ Fully automated (5-10 minutes runtime)
- ✅ Repeatable and version-controlled
- ✅ No manual clicking required
- ✅ Creates all 26 visualizations + 5 dashboards
- ✅ Proper error handling and status reporting

**Prerequisites**:
1. Metabase running at http://localhost:3000
2. Admin account configured (email/password)
3. Database connection established in Metabase UI
4. Python 3.x with `requests` library

**Usage**:

```bash
# Option 1: Environment variables (recommended)
export METABASE_EMAIL="admin@oss-framework.local"
export METABASE_PASSWORD="your-secure-password"
python3 create-dashboards-api.py

# Option 2: Command-line arguments
python3 create-dashboards-api.py --email admin@oss-framework.local --password YOUR_PASS

# Option 3: Skip specific dashboards
python3 create-dashboards-api.py --skip-dashboard 5  # Skip Dashboard 5

# Help
python3 create-dashboards-api.py --help
```

**Output**:
```
🚀 METABASE DASHBOARD CREATION - API APPROACH
================================================================================
URL: http://localhost:3000
User: admin@oss-framework.local

🔐 Authenticating as admin@oss-framework.local...
✅ Authentication successful
📊 Fetching databases...
✅ Found 1 database(s)
   - OSS Analytics (ID: 2, Engine: sqlite)
✅ Using database: OSS Analytics (ID: 2)
📁 Creating collection: OSS Analytics...
✅ Collection created (ID: 1)

================================================================================
📊 DASHBOARD 1: CHRONIC ABSENTEEISM RISK
================================================================================
  📈 Creating question: Risk Distribution by Level...
    ✅ Created (ID: 1)
  📈 Creating question: Total Students Monitored...
    ✅ Created (ID: 2)
[...]

✅ Dashboard 1 complete: http://localhost:3000/dashboard/1

[Similar output for Dashboards 2-5]

================================================================================
📊 DASHBOARD CREATION SUMMARY
================================================================================
✅ Successfully created: 5 dashboard(s)
⏭️  Skipped: 0 dashboard(s)

🌐 View dashboards at: http://localhost:3000/collection/1
================================================================================
```

**Troubleshooting**:

| Issue | Solution |
|-------|----------|
| `Authentication failed` | Verify email/password are correct |
| `No database found` | Connect database in Metabase UI first (Admin → Databases) |
| `Connection refused` | Ensure Metabase is running: `curl http://localhost:3000/api/health` |
| `Failed to create question` | Check SQL syntax or database connection |
| `Module not found: requests` | Install: `pip install requests` |

---

### 2. Manual Dashboard Creation (Fallback)

If the API script fails, you can create dashboards manually using the Metabase UI:

1. **Open Metabase**: http://localhost:3000
2. **Login** with admin credentials
3. **Follow plan specifications**: See `.sisyphus/plans/stage-4-metabase-dashboards.md` lines 78-467
4. **Create each dashboard**:
   - New → Dashboard
   - Add visualizations (New Question → SQL)
   - Configure filters
   - Save to "OSS Analytics" collection

**Estimated Time**: 12-15 hours

---

## Dashboard Specifications

All 5 dashboards follow the plan in `.sisyphus/plans/stage-4-metabase-dashboards.md`:

### Dashboard 1: Chronic Absenteeism Risk
- **Target Audience**: Principals, Counselors, Administrators
- **Visualizations**: 6 (risk distribution pie chart, key metrics, at-risk student table, grade comparison, attendance trend, school comparison)
- **Data Source**: `v_chronic_absenteeism_risk`

### Dashboard 2: Student Wellbeing Risk Profiles
- **Target Audience**: Counselors, Social Workers
- **Visualizations**: 5 (risk matrix bubble chart, wellbeing breakdown, primary concern distribution, student table, risk trend)
- **Data Source**: `v_wellbeing_risk_profiles`

### Dashboard 3: Equity Outcomes Analysis
- **Target Audience**: Administrators, Board Members, Counselors
- **Visualizations**: 5 (attendance by subgroup, GPA distribution, discipline disparities, opportunity gap table, key metrics)
- **Data Source**: `v_equity_outcomes_by_demographics`

### Dashboard 4: Class Effectiveness Comparison
- **Target Audience**: Principals, Teachers
- **Visualizations**: 5 (class pass rates bar chart, attendance impact scatter, effectiveness indicators, class detail table, grade distribution)
- **Data Source**: `v_class_section_comparison`

### Dashboard 5: Performance Correlations
- **Target Audience**: Administrators, Board Members
- **Visualizations**: 3 (key correlations cards, correlation matrix heatmap, correlation table)
- **Data Source**: `v_performance_correlations`

---

## Files in This Directory

```
/oss_framework/deployment/metabase/
├── docker-compose.yml           # Metabase container config
├── README.md                     # Metabase installation guide
├── deployment-guide.md           # Production deployment procedures
├── create-dashboards-api.py     # ⭐ API automation script
├── SCRIPTS-README.md             # This file
├── training/                     # User training materials (8 guides)
│   ├── quick-start-guide.md
│   ├── admin-guide.md
│   ├── principal-guide.md
│   ├── counselor-guide.md
│   ├── teacher-guide.md
│   ├── board-member-guide.md
│   ├── troubleshooting-guide.md
│   └── faq.md
└── uat/                          # User Acceptance Testing materials (8 files)
    ├── uat-plan.md
    ├── uat-checklist-administrators.md
    ├── uat-checklist-principals.md
    ├── uat-checklist-counselors.md
    ├── uat-checklist-teachers.md
    ├── uat-checklist-board-members.md
    ├── uat-feedback-form.md
    └── uat-issues-log-template.md
```

---

## Next Steps After Dashboard Creation

1. **Verify Dashboards**: Open http://localhost:3000/collection/1 and verify all 5 dashboards are present
2. **Configure Access Controls**: Continue to Task 4.07 (see plan)
3. **Run User Acceptance Testing**: Follow `uat/uat-plan.md`
4. **Deploy to Production**: Follow `deployment-guide.md`
5. **Train Staff**: Use materials in `training/` directory

---

## Support

**Documentation**:
- Installation guide: `README.md`
- Deployment guide: `deployment-guide.md`
- Training materials: `training/` directory
- UAT materials: `uat/` directory

**For Issues**:
1. Check `troubleshooting-guide.md`
2. Review Metabase logs: `docker logs oss-metabase`
3. Verify database connection: Metabase Admin → Databases
4. Test SQL queries directly in Metabase SQL editor

---

**Last Updated**: January 27, 2026  
**Author**: OSS Framework Team
