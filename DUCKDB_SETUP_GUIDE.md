# DuckDB Database Setup - Complete Guide

## Current Status
- ✅ DuckDB file exists: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- ✅ Metabase running on: http://localhost:3000
- ⚠️ Requires manual setup via browser (API authentication needed)

---

## QUICK START (What You Need to Do)

### 1. Open Metabase
```
http://localhost:3000
```

### 2. Login
- Use your Metabase credentials
- If you haven't logged in yet, complete the initial setup

### 3. Navigate to Settings
```
Settings (gear ⚙️) → Admin Settings → Databases
```

### 4. Add DuckDB Database
- Click "Add database" button
- Select "DuckDB" from the database type dropdown

### 5. Fill in Configuration
```
Database File Path: /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
Display Name: OSS Analytics
Description: Open Source Student Analytics Database
Read-only: ✓ (checked)
```

### 6. Save
- Click the "Save" button
- Wait for the connection test to complete

### 7. Note the Database ID
- After saving, note the database ID from:
  - URL: `http://localhost:3000/admin/databases/[ID]`
  - Or from the database listing page

---

## Verification

After setup, verify the connection:

```bash
# Check if the DuckDB file is accessible
ls -lh /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Test DuckDB directly (if you have DuckDB CLI)
duckdb /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
# Then in the prompt:
# .tables  (to list tables)
```

---

## Alternative: Programmatic Setup (If You Have Admin Credentials)

If you know your Metabase admin credentials, you can run:

```bash
cd /Users/flucido/projects/openedDataEstate
python3 setup_duckdb.py
# Enter username and password when prompted
```

---

## Troubleshooting

### Problem: DuckDB option not showing
**What this means**: Your Metabase version may not support DuckDB
**Solution**: 
- Check Metabase version (v0.47+required)
- Go to http://localhost:3000 and check version in footer

### Problem: File not found
**What this means**: Metabase can't access the DuckDB file
**Solution**:
- Verify file exists: `ls /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Check permissions: `chmod 644 oea.duckdb`
- Check path is exactly: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`

### Problem: Permission denied
**What this means**: Metabase container can't read the file
**Solution**:
- Make file world-readable: `chmod 644 oea.duckdb`
- Check Docker can access the path

### Problem: Can't login to Metabase
**What this means**: Credentials are wrong or setup not completed
**Solution**:
- Check if Metabase is showing setup screen
- If setup screen appears, complete the initial setup first
- Create admin user when prompted

---

## Database Information (Fill This In After Setup)

```
┌─────────────────────────────────────────────────────────┐
│           CONFIGURATION REFERENCE                       │
├─────────────────────────────────────────────────────────┤
│ Database Name:   OSS Analytics                          │
│ Database ID:     [Your ID - to be filled]               │
│ Engine:          DuckDB                                 │
│ File Path:       /Users/.../oea.duckdb                 │
│ Read-only:       ✓ Yes                                  │
│ Status:          [To be updated after setup]            │
└─────────────────────────────────────────────────────────┘
```

---

## Next Steps After Setup

1. **Test Connection**
   - Go to the database settings
   - Run a test query

2. **Create Dashboards**
   - Create a new dashboard
   - Add cards from OSS Analytics database
   - Build visualizations

3. **Set Permissions**
   - Configure who can access the database
   - Set up roles and access levels

4. **Configure Caching** (Optional)
   - Set cache TTL for better performance
   - Balance freshness vs. speed

---

## File Locations

- **DuckDB File**: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- **Setup Script**: `/Users/flucido/projects/openedDataEstate/setup_duckdb.py`
- **Documentation**: `/Users/flucido/projects/openedDataEstate/setup_duckdb_metabase.md`

---

## System Information

```
Metabase Version:   v0.49.1
Metabase URL:       http://localhost:3000
Container Name:     oss-metabase
Docker Port:        3000 → 3000

DuckDB File:        oea.duckdb
File Size:          ~23.8 MB
Location:           oss_framework/data/
```

---

## Support Resources

- **Metabase Docs**: https://www.metabase.com/docs/latest/
- **DuckDB Docs**: https://duckdb.org/docs/
- **Project Docs**: oss_framework/docs/

---

**Status**: Ready for manual setup in browser  
**Last Updated**: 2026-02-09
