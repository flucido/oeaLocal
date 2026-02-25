# DuckDB Database Setup Summary

## Status ✓ Ready for Setup

Your Metabase instance is running and the DuckDB database file is available. You have **two options** to add the database:

---

## Option 1: Manual Setup (Recommended for First-Time)

### Quick Steps (2 minutes)

1. **Open Metabase**
   ```
   http://localhost:3000
   ```

2. **Navigate to Admin**
   - Click the gear icon (⚙️) in top right
   - Select "Admin Settings" or just "Admin"

3. **Go to Databases**
   - Click the "Databases" tab/option on the left sidebar

4. **Add Database**
   - Click the "Add database" button (usually blue/green)
   - Select "DuckDB" from the dropdown

5. **Configure**
   ```
   Database File Path: /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
   Display Name:       OSS Analytics
   Description:        (optional) Open Source Student Analytics Database
   Read-only:          ✓ CHECK THIS BOX
   ```

6. **Save**
   - Click the "Save" button
   - Wait for connection test

7. **Note the ID**
   - After successful save, note the database ID
   - It appears in the URL: `http://localhost:3000/admin/databases/[ID]`

---

## Option 2: Programmatic Setup (If You Have Admin Credentials)

### Steps

1. **Run the Setup Script**
   ```bash
   cd /Users/flucido/projects/openedDataEstate
   python3 setup_duckdb.py
   ```

2. **Enter Credentials**
   - Username: (default: admin)
   - Password: (your Metabase password)

3. **Wait for Completion**
   - Script will add the database and show the ID

---

## After Setup: Verification

Verify everything worked:

```bash
# Quick verification
python3 /Users/flucido/projects/openedDataEstate/verify_duckdb_setup.py
```

This script will:
- ✓ Check Metabase is running
- ✓ Verify DuckDB file exists
- ✓ List all databases
- ✓ Confirm OSS Analytics database is present
- ✓ Show database ID and table count

---

## Important Information

### Database Details
```
Name:           OSS Analytics
File Path:      /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
File Size:      ~23.8 MB
Engine:         DuckDB
Read-only:      Yes (recommended)
Metabase URL:   http://localhost:3000
Container:      oss-metabase (Docker)
```

### What Gets Populated
- Database ID: (you'll see this after adding)
- Tables: (will be scanned and indexed by Metabase)
- Columns: (automatically detected)

---

## Troubleshooting

### "DuckDB not in dropdown"
- Your Metabase version may be older
- Check version: http://localhost:3000 (footer)
- Metabase v0.47+ supports DuckDB
- Contact support if you need upgrade assistance

### "File not found"
- Verify exact path: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Check file exists: `ls /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Check permissions: `chmod 644 /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`

### "Permission denied"
- Make file readable: `chmod 644 /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Check Docker has access to your home directory

### "Connection test failed"
- Verify Metabase is running: `docker ps | grep metabase`
- Check Metabase logs: `docker logs oss-metabase | tail -20`
- Try again after waiting 30 seconds

---

## Next Steps After Adding Database

1. **Test the Connection**
   - Click on "OSS Analytics" in the database list
   - Try running a simple SQL query

2. **Create a Dashboard**
   - Click "New Dashboard"
   - Add questions from "OSS Analytics" database
   - Build your visualizations

3. **Set Permissions** (Optional)
   - Go to Admin Settings > Databases > OSS Analytics
   - Configure who can access the database
   - Set role-based access if needed

4. **Configure Caching** (Optional)
   - Set cache TTL to balance freshness vs. performance
   - Default: 3600 seconds (1 hour) is good

---

## Reference Files

- **Setup Guide**: `DUCKDB_SETUP_GUIDE.md`
- **Setup Script**: `setup_duckdb.py` (requires credentials)
- **Verification Script**: `verify_duckdb_setup.py`
- **Manual Instructions**: `setup_duckdb_metabase.md`

---

## Support

### Documentation
- **Metabase**: https://www.metabase.com/docs/latest/
- **DuckDB**: https://duckdb.org/docs/
- **OSS Framework**: `oss_framework/docs/README.md`

### Common Commands

```bash
# Verify DuckDB file
ls -lh oss_framework/data/oea.duckdb

# Check Metabase is running
docker ps | grep metabase

# View Metabase logs
docker logs oss-metabase

# List Docker volumes
docker volume ls | grep metabase

# Test DuckDB directly (if CLI installed)
duckdb oss_framework/data/oea.duckdb
```

---

## Final Checklist

- [ ] DuckDB file exists at `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- [ ] Metabase is running at http://localhost:3000
- [ ] You can access Metabase (browser loads the page)
- [ ] You know your Metabase admin credentials (or plan to use manual setup)
- [ ] You've completed manual setup OR will run the setup script
- [ ] Database "OSS Analytics" appears in the databases list
- [ ] You've noted the Database ID
- [ ] Verification script shows success

---

**Ready to proceed?** Follow Option 1 (Manual) or Option 2 (Programmatic) above.

**Questions?** Check the troubleshooting section or review the detailed guides.

---

*Setup guide created: 2026-02-09*  
*Status: ✓ Verified and ready for configuration*
