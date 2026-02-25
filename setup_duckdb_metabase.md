# DuckDB Database Setup in Metabase

## Quick Reference
- **Metabase URL**: http://localhost:3000 (oss-metabase)
- **DuckDB File Path**: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- **Display Name**: `OSS Analytics`
- **Configuration**: Read-only

## Manual Setup Steps

### Step 1: Access Metabase
1. Open your browser and navigate to: **http://localhost:3000**

### Step 2: Login
- If you see a setup screen, complete the initial setup
- If you see a login screen, use your credentials
- If you see the dashboard directly, proceed to Step 3

### Step 3: Navigate to Settings
1. Click the **Settings icon (gear ⚙️)** in the top right corner
2. Select **Admin Settings** or **Admin** from the dropdown

### Step 4: Go to Databases
1. In the Admin Settings sidebar, click **Databases**
2. You'll see a list of configured databases

### Step 5: Add New Database
1. Click the **Add Database** button (usually blue/green button)
2. A dialog or form will appear asking for database type

### Step 6: Select DuckDB
1. In the database type dropdown, scroll to find **DuckDB**
2. If DuckDB is not visible, look for:
   - "DuckDB"
   - "Generic SQL"  
   - "PostgreSQL" (as fallback)
3. Click on **DuckDB**

### Step 7: Configure Database
Fill in the form with these values:

| Field | Value |
|-------|-------|
| **Database File Path** | `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb` |
| **Display Name** | `OSS Analytics` |
| **Description** | `Open Source Student Analytics Database` (optional) |
| **Read-only** | ✅ **Checked** |
| **Cache TTL** | 3600 (default is fine) |

### Step 8: Save
1. Click the **Save** button
2. Metabase will test the connection
3. If successful, you'll see a confirmation message

## Finding Your Database ID

After successful setup, the database will appear in the Databases list. To find the ID:

**Method 1: From the URL**
- Click on the OSS Analytics database in the list
- The URL will be something like: `http://localhost:3000/admin/databases/2`
- The **ID is 2** (the number at the end)

**Method 2: From the UI**
- Look at the database details page
- The ID may be displayed in parentheses or as a reference number

## If DuckDB is Not Available

### Option A: Try Generic SQL (not recommended)
- DuckDB requires native driver support
- Generic SQL won't work for DuckDB

### Option B: Try PostgreSQL Driver
- Metabase may not have DuckDB in older versions
- You'd need to configure a PostgreSQL proxy to DuckDB
- Not recommended for this setup

### Option C: Upgrade Metabase
- The current version is v0.49.1
- Newer versions may have better DuckDB support
- Check: https://www.metabase.com/docs/latest/databases/connecting.html

## Troubleshooting

### Problem: "DuckDB" option not showing
**Solution**: 
- Check if your Metabase version supports DuckDB (v0.47+)
- Try accessing the admin panel again
- Clear browser cache and refresh

### Problem: Connection fails
**Solution**:
- Verify file path is correct: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Check file exists: `ls -la /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
- Verify file permissions are readable: `chmod 644 oea.duckdb`

### Problem: Read-only option missing
**Solution**:
- Some Metabase versions don't have per-database read-only toggle
- You can set this in the query editor by disabling query execution

## Next Steps

After adding the database:
1. Go to **Databases** > **OSS Analytics**
2. Run a test query to verify connection
3. Create dashboards using the OSS Analytics data
4. Set up database permissions for team members

## Database ID Reference

Once created, note your database ID here:
```
Database Name: OSS Analytics
Database ID: [To be filled after setup]
Engine: DuckDB
Read-only: true
```

## Additional Resources

- [Metabase Database Documentation](https://www.metabase.com/docs/latest/databases/connecting.html)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [OSS Framework Documentation](../docs/README.md)
