# Dashboard Creation - Ready to Run

## Status: ✅ FIXED AND READY

All SQL queries have been fixed with proper schema prefixes (`main_main_analytics.`).
The script now includes automatic cleanup of old/empty dashboards before creating new ones.

## Run Command

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

export METABASE_EMAIL="your-admin-email"
export METABASE_PASSWORD="your-password"

python3 create-dashboards-api.py
```

## What the Script Will Do

1. **Authenticate** with Metabase using your credentials
2. **Find** the "OSS Analytics" database connection
3. **Cleanup** existing empty dashboards and questions in the collection
4. **Create** 5 new dashboards with 26 visualizations (all with correct schema)
5. **Report** success status for each dashboard

## Expected Runtime

5-10 minutes (includes cleanup + creation)

## What You Should See

```
🚀 METABASE DASHBOARD CREATION - API APPROACH
================================================================================
🔐 Authenticating...
✅ Authentication successful
📊 Fetching databases...
✅ Using database: OSS Analytics (ID: X)
📁 Creating collection: OSS Analytics
✅ Collection already exists (ID: X)
🧹 Cleaning up collection ID X...
  🗑️  Deleting dashboard: Dashboard 1: Chronic Absenteeism Risk (ID: X)
    ✅ Deleted
  ... (repeats for all old items)
✅ Cleanup complete

📊 DASHBOARD 1: CHRONIC ABSENTEEISM RISK
  📈 Creating question: Risk Distribution by Level...
  ✅ Question created (ID: X)
  ... (creates 6 visualizations)
📊 Creating dashboard: Dashboard 1: Chronic Absenteeism Risk
✅ Dashboard created (ID: X)
  🔗 Adding cards...
✅ Dashboard 1 complete: http://localhost:3000/dashboard/X

... (repeats for dashboards 2-5)

📊 DASHBOARD CREATION SUMMARY
✅ Created 5/5 dashboards successfully
🎉 All dashboards available at http://localhost:3000
```

## After Running

1. Open http://localhost:3000
2. Navigate to "OSS Analytics" collection
3. Click on each dashboard to verify data displays correctly
4. Report back if any dashboard shows "No results" or errors

## If Errors Occur

- **Authentication failed**: Check email/password
- **Database not found**: Verify DuckDB is connected in Metabase settings
- **No results in dashboard**: Report which dashboard has issues
- **Script crashes**: Copy error message and report

## Backup

A backup of the original script is saved at:
`create-dashboards-api.py.backup`

## Changes Made

1. ✅ Fixed all 11 SQL queries to use `main_main_analytics.` schema prefix
2. ✅ Added `cleanup_collection()` method to delete old dashboards/questions
3. ✅ Integrated cleanup into main execution flow (runs before creation)
4. ✅ Removed unnecessary comments per code quality standards
5. ✅ Fixed type hints for Python type checker compliance

---

**Ready to run!** Execute the command above and monitor the output.
