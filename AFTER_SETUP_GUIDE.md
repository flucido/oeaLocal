# DuckDB Database Setup Complete - Next Steps

## After You've Added the Database to Metabase

Once you've successfully added the "OSS Analytics" DuckDB database to Metabase and received a database ID, here are your next steps.

### Step 1: Verify Setup Success

Run the verification script to confirm everything is working:

```bash
cd /Users/flucido/projects/openedDataEstate
python3 verify_duckdb_setup.py
```

Expected output:
```
✓ Metabase is running
✓ DuckDB file exists
✓ Found 'OSS Analytics' database!
   Database ID: [Your ID]
   Engine: DuckDB
   Tables: [Number]
✓ DATABASE SETUP SUCCESSFUL!
```

### Step 2: Document Your Database ID

Once confirmed, save your database ID:

```
DATABASE ID: _________________

Use this ID to:
- Create dashboards
- Query data
- Set permissions
- Configure caching
```

### Step 3: Test the Connection

1. Go to http://localhost:3000
2. Go to Admin Settings > Databases > OSS Analytics
3. Click "Get Sample Data" or run a test query
4. Try: `SELECT COUNT(*) FROM information_schema.tables`

### Step 4: Create Your First Dashboard

1. Click "New Dashboard"
2. Click "+" to add a card
3. Select "OSS Analytics" database
4. Write a query, e.g.:
   ```sql
   SELECT * FROM information_schema.tables LIMIT 10
   ```
5. Save the question and add to dashboard

### Step 5: Configure Database Settings (Optional)

In Admin Settings > Databases > OSS Analytics:

#### Caching Settings
- **Cache TTL**: 3600 (1 hour) - good default
- Increase for better performance
- Decrease for more current data

#### Permissions
- Set up access by role/user
- By default, admins have full access

#### Metadata
- Edit table/column descriptions
- Hide sensitive columns
- Set up custom segments

### Step 6: Build Your Analytics

#### Sample Queries

```sql
-- See all tables available
SELECT table_name FROM information_schema.tables;

-- Count records in a table
SELECT COUNT(*) FROM your_table_name;

-- Basic aggregation
SELECT column1, COUNT(*) 
FROM your_table_name
GROUP BY column1;
```

#### Create Visualizations
- Tables
- Charts (bar, line, pie, etc.)
- Maps
- Funnels
- Gauges
- Pivot tables

### Reference: Typical Dashboard Setup

```
Dashboard: Student Analytics
├── Card 1: Student Attendance Trends (Line Chart)
├── Card 2: Students by Grade (Bar Chart)
├── Card 3: Attendance Distribution (Pie Chart)
├── Card 4: Recent Student Data (Table)
└── Card 5: KPI: Average Attendance Rate (Number)
```

### Useful Metabase Features

#### Filters
- Add filters to your questions
- Create dashboard filters that affect multiple cards

#### Parameters
- Use `{{ parameter }}` in SQL queries
- Create interactive dashboards

#### Schedules
- Set questions to auto-update
- Schedule alerts when thresholds are crossed

#### Notebooks
- Use visual query builder instead of SQL
- No SQL knowledge required

### Troubleshooting After Setup

#### Database appears but no tables
- Wait 30 seconds - tables may still be syncing
- Refresh the page
- Check Metabase logs: `docker logs oss-metabase`

#### Can't query the database
- Verify read-only setting is correct
- Check DuckDB file permissions: `ls -l oea.duckdb`
- Test DuckDB file directly with `duckdb oea.duckdb` if CLI installed

#### Slow queries
- Check cache TTL settings
- Optimize SQL queries
- Check system resources: `docker stats oss-metabase`

### Performance Tips

1. **Use WHERE clauses** - Limit data early
2. **Aggregate data** - Use GROUP BY for summaries
3. **Create indexes** - Define in DuckDB for repeated queries
4. **Enable caching** - Set appropriate TTL values
5. **Archive old data** - Remove unnecessary historical data

### Security Considerations

✓ **Database is Read-Only** - No accidental modifications
✓ **Verify User Permissions** - Use role-based access control
✓ **Audit Queries** - Monitor what users are querying
✓ **Protect Sensitive Data** - Hide PII columns if necessary

### Maintenance Tasks

#### Weekly
- [ ] Check dashboard refresh status
- [ ] Monitor query performance
- [ ] Review user access logs

#### Monthly
- [ ] Update cache TTL if needed
- [ ] Archive old data if applicable
- [ ] Review and optimize slow queries

#### As Needed
- [ ] Update table metadata/descriptions
- [ ] Adjust permissions for new users
- [ ] Create new dashboards for stakeholders

### Common Tasks

#### Change Database Display Name
1. Admin > Databases > OSS Analytics
2. Click "Edit database details"
3. Change "Display Name" field
4. Save

#### Hide Sensitive Columns
1. Admin > Databases > OSS Analytics > [Table]
2. Click column settings (⚙️)
3. Toggle visibility off
4. Save

#### Create a Saved Question
1. Create your query
2. Click "Save"
3. Give it a descriptive name
4. Choose a collection to save in
5. Click "Save question"

#### Export Data
1. Run any query
2. Click "Download results"
3. Choose format (CSV, Excel, JSON)

### Useful Resources

- **Metabase User Guide**: https://www.metabase.com/docs/latest/users-guide/
- **Query Language**: https://duckdb.org/docs/sql/introduction.html
- **Dashboard Best Practices**: https://www.metabase.com/learn/dashboards/

### Getting Help

1. **Check Metabase Help** - Click "?" icon in Metabase
2. **Review Documentation** - See reference files below
3. **Check Logs** - `docker logs oss-metabase`
4. **Metabase Community** - https://discourse.metabase.com/

### Files & References

```
/Users/flucido/projects/openedDataEstate/
├── README_DUCKDB_SETUP.md ........ Setup summary
├── DUCKDB_SETUP_GUIDE.md ........ Troubleshooting
├── setup_duckdb.py .............. Setup script
├── verify_duckdb_setup.py ....... Verification script
└── oss_framework/
    ├── data/
    │   └── oea.duckdb ........... Your database file
    └── docs/
        └── README.md ............ Project documentation
```

### Database Location & Access

```
File Path:     /Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb
File Size:     ~23.8 MB
Format:        DuckDB (embedded analytics DB)
Access:        Read-only via Metabase
Backup:        Stored in Docker volume (sis-metabase)
```

### Success Indicators

Your setup is successful when:
- ✓ Metabase loads without errors
- ✓ "OSS Analytics" appears in database list
- ✓ You can run SQL queries on the database
- ✓ Query results return in < 5 seconds
- ✓ You can create dashboards and visualizations
- ✓ No "access denied" or "file not found" errors

---

**Congratulations!** Your DuckDB database is now integrated with Metabase.

**Next Step**: Start exploring your data and building dashboards!

---

*Setup completed: [Date]*  
*Database ID: [To be filled]*  
*Last verified: [To be updated]*
