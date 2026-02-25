# START HERE - DuckDB Metabase Setup

## TL;DR (Too Long; Didn't Read)

Your DuckDB database is ready to be added to Metabase. **Choose one option below:**

### Option 1: Manual Setup (5 minutes)
```bash
# 1. Open this in your browser:
http://localhost:3000

# 2. Settings (⚙️) → Admin Settings → Databases → Add database

# 3. Select DuckDB and fill in:
Database File Path: /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
Display Name: OSS Analytics
Read-only: ✓ CHECK THIS

# 4. Click Save

# 5. Verify:
python3 verify_duckdb_setup.py
```

### Option 2: Automated Setup (1 minute)
```bash
# Have your Metabase password ready, then run:
python3 setup_duckdb.py
```

---

## Full Setup Instructions

### Prerequisites
- ✓ Metabase is running (http://localhost:3000)
- ✓ DuckDB file exists (23.8 MB)
- ✓ You have Metabase admin access

### Choose Your Path

**Path A: Manual Setup** (Recommended for first-time)
1. Open http://localhost:3000
2. Log in with your credentials
3. Read: `setup_duckdb_metabase.md` (5 min read)
4. Follow the 8 steps
5. Note the Database ID
6. Run `verify_duckdb_setup.py`

**Path B: Automated Setup** (Faster, requires credentials)
1. Have your Metabase admin password ready
2. Run: `python3 setup_duckdb.py`
3. Enter username and password when prompted
4. Wait for completion
5. Note Database ID from output

---

## Configuration Details

```
Database:     OSS Analytics
Type:         DuckDB
File:         /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
Read-only:    Yes
Size:         ~23.8 MB
Status:       Ready to add
```

---

## All Documentation Files

| File | Purpose | Time |
|------|---------|------|
| **README_DUCKDB_SETUP.md** | Complete setup guide | 10 min |
| **setup_duckdb_metabase.md** | Manual instructions | 5 min |
| **DUCKDB_SETUP_GUIDE.md** | Troubleshooting | 15 min |
| **AFTER_SETUP_GUIDE.md** | What to do next | 10 min |
| **SETUP_FILES_INDEX.md** | Navigation guide | 5 min |

---

## Scripts

- **setup_duckdb.py** - Automated setup (requires credentials)
- **verify_duckdb_setup.py** - Verify setup succeeded

---

## Step-by-Step: Manual Setup

### Step 1: Access Metabase
```
http://localhost:3000
```

### Step 2: Login
Use your Metabase credentials

### Step 3: Navigate to Admin Settings
- Click gear icon (⚙️) in top right
- Click "Admin Settings"

### Step 4: Go to Databases
- In left sidebar, click "Databases"

### Step 5: Add Database
- Click "Add database" button

### Step 6: Select DuckDB
- In dropdown, select "DuckDB"

### Step 7: Configure
Fill in these fields:
```
Database File Path: /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
Display Name:       OSS Analytics
Description:        (optional)
Read-only:          ✓ CHECK THIS BOX
```

### Step 8: Save
- Click "Save" button
- Wait for connection test
- Note the Database ID

---

## After Setup

### Verify It Worked
```bash
python3 verify_duckdb_setup.py
```

Expected output:
```
✓ Metabase is running
✓ DuckDB file exists
✓ Found 'OSS Analytics' database!
   Database ID: [Your ID]
✓ DATABASE SETUP SUCCESSFUL!
```

### Next Steps
1. Open http://localhost:3000
2. Create dashboards
3. Write SQL queries
4. Visualize your data

---

## Troubleshooting

### "DuckDB not in dropdown"
- Check Metabase version (v0.47+ required)
- Look for alternative options or contact support

### "File not found"
- Check file exists: `ls oss_framework/data/oea.duckdb`
- Verify exact path in configuration

### "Permission denied"
- Make file readable: `chmod 644 oss_framework/data/oea.duckdb`

### Still stuck?
- Read: `DUCKDB_SETUP_GUIDE.md` (Troubleshooting section)
- Check Docker logs: `docker logs oss-metabase`
- View full guide: `README_DUCKDB_SETUP.md`

---

## File Locations

```
Project Root: /Users/flucido/projects/openedDataEstate/
├── START_HERE.md ................. This file
├── README_DUCKDB_SETUP.md ......... Full guide
├── setup_duckdb_metabase.md ....... Manual steps
├── DUCKDB_SETUP_GUIDE.md ......... Troubleshooting
├── AFTER_SETUP_GUIDE.md ......... Next steps
├── setup_duckdb.py ............... Setup script
├── verify_duckdb_setup.py ........ Verify script
└── oss_framework/data/
    └── oea.duckdb ................ Your database
```

---

## Quick Reference

### Commands
```bash
# Run automated setup
python3 setup_duckdb.py

# Verify setup
python3 verify_duckdb_setup.py

# Check Metabase status
docker ps | grep metabase

# View logs
docker logs oss-metabase
```

### URLs
```
Metabase:    http://localhost:3000
Admin Panel: http://localhost:3000/admin/settings/databases
Databases:   http://localhost:3000/admin/databases
```

---

## Success Indicators

Setup worked when:
- ✓ "OSS Analytics" appears in database list
- ✓ Can run SQL queries
- ✓ `verify_duckdb_setup.py` succeeds
- ✓ No errors in logs

---

## Next Steps After Setup

1. **Explore your data**
   - Run queries
   - See what tables are available

2. **Create dashboards**
   - Build visualizations
   - Share with your team

3. **Set up automation** (optional)
   - Schedule queries
   - Set alerts
   - Create scheduled reports

---

## Getting Help

### Documentation
- **Setup Issues**: `setup_duckdb_metabase.md`
- **Technical Help**: `DUCKDB_SETUP_GUIDE.md`
- **After Setup**: `AFTER_SETUP_GUIDE.md`
- **Full Guide**: `README_DUCKDB_SETUP.md`

### Online Resources
- Metabase: https://www.metabase.com/docs/
- DuckDB: https://duckdb.org/docs/

### Still need help?
1. Check the relevant guide (see Documentation above)
2. Review troubleshooting section
3. Check Docker logs: `docker logs oss-metabase`

---

## Summary

| Item | Value |
|------|-------|
| **Status** | ✓ Ready to setup |
| **Time Required** | 5-20 minutes |
| **Database Name** | OSS Analytics |
| **Database Type** | DuckDB |
| **File Location** | oss_framework/data/oea.duckdb |
| **Metabase URL** | http://localhost:3000 |

---

## Choose Your Action Now

**I want to do manual setup** → Read: `setup_duckdb_metabase.md`

**I want automated setup** → Run: `python3 setup_duckdb.py`

**I'm already done** → Run: `python3 verify_duckdb_setup.py`

**I need help** → Read: `DUCKDB_SETUP_GUIDE.md`

**I want full details** → Read: `README_DUCKDB_SETUP.md`

---

**You've got everything you need. Let's go! 🚀**

---

*Setup prepared: 2026-02-09*  
*Status: ✓ Ready for configuration*
