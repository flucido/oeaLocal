# Adding Dashboard Filters - Quick Start Guide

**Status**: Ready to Execute  
**Script**: `add-dashboard-filters.py`  
**Prerequisites**: Metabase running with dashboards already created

---

## What This Does

Adds interactive parameterized filters to all 5 Metabase dashboards:

| Dashboard | Filters Added |
|-----------|---------------|
| Dashboard 1: Chronic Absenteeism | School, Grade Level, Risk Level, Row Limit |
| Dashboard 2: Wellbeing Risk | School, Grade Level, Compound Risk Level |
| Dashboard 3: Equity Outcomes | School, Demographic Group, Min Cohort Size |
| Dashboard 4: Class Effectiveness | School, Teacher, Grade Level, Term |
| Dashboard 5: Performance Correlations | School, Date Range |

**Total**: 26 filter parameters across 5 dashboards

---

## Prerequisites Check

Before running, verify:

### 1. Python Dependencies Installed
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Install from requirements.txt
python3 -m pip install -r requirements.txt

# Verify installation
python3 -c "import requests; print(f'✅ requests {requests.__version__}')"
# Expected: ✅ requests 2.31.0 or higher
```

### 2. Docker Desktop Installed
```bash
# Should return path to docker binary
which docker

# If not installed:
brew install --cask docker-desktop
# Then start Docker Desktop application
```

### 3. Metabase Running
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d

# Wait 60-90 seconds, then verify:
curl http://localhost:3000/api/health
# Should return: {"status":"ok"}
```

### 4. Dashboards Already Created
```bash
# Check logs to verify dashboards exist
cat dashboard-creation-fixed.log | grep "Dashboard.*created"

# Expected output:
# ✅ Dashboard created (ID: 32) - Chronic Absenteeism Risk
# ✅ Dashboard created (ID: 33) - Wellbeing Risk Profiles
# ✅ Dashboard created (ID: 34) - Equity Outcomes
# ✅ Dashboard created (ID: 35) - Class Effectiveness
# ✅ Dashboard created (ID: 36) - Performance Correlations
```

### 5. Admin Credentials Available
You need the Metabase admin email and password used during initial setup.

---

## Usage

### Method 1: Environment Variables (Recommended)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Set credentials (replace with your actual credentials)
export METABASE_EMAIL="admin@oss-framework.local"
export METABASE_PASSWORD="your-admin-password"

# Run script
python3 add-dashboard-filters.py
```

### Method 2: Command Line Arguments

```bash
python3 add-dashboard-filters.py \
  --email admin@oss-framework.local \
  --password your-admin-password \
  --base-url http://localhost:3000
```

---

## Expected Output

```
🚀 METABASE DASHBOARD FILTER ADDITION
================================================================================
Target: http://localhost:3000
Admin: admin@oss-framework.local
================================================================================
🔐 Authenticating as admin@oss-framework.local...
✅ Authentication successful

================================================================================
📊 DASHBOARD 1: Chronic Absenteeism Risk (Adding Filters)
================================================================================
  📌 Adding parameter: School (string/=)
    ✅ Added parameter: School
  📌 Adding parameter: Grade Level (string/=)
    ✅ Added parameter: Grade Level
  📌 Adding parameter: Risk Level (string/=)
    ✅ Added parameter: Risk Level
  📌 Adding parameter: Number of Students (number/=)
    ✅ Added parameter: Number of Students

✅ Dashboard 1 filters added: http://localhost:3000/dashboard/32
⚠️  Note: Filter-to-card linking requires manual configuration in Metabase UI
   1. Open dashboard in Metabase
   2. Click on each filter
   3. Select 'Edit' and connect to appropriate cards/fields

[... repeats for dashboards 2-5 ...]

================================================================================
📊 FILTER ADDITION SUMMARY
================================================================================
✅ Added filters to 5/5 dashboards successfully

⚠️  IMPORTANT NEXT STEP:
   Filters have been added but need to be connected to dashboard cards.
   Manual steps required:
   1. Open each dashboard in Metabase UI
   2. Click on each filter dropdown
   3. Select 'Edit' → 'Connect to' → Select appropriate cards and fields
   4. Save dashboard

🎉 All dashboards available at http://localhost:3000
================================================================================
```

**Runtime**: 30-60 seconds

---

## Post-Execution Steps

### Step 1: Verify Filters Were Added

1. Open http://localhost:3000 in browser
2. Navigate to "OSS Analytics" collection
3. Open "Dashboard 1: Chronic Absenteeism Risk"
4. You should see filter dropdowns at the top: **School**, **Grade Level**, **Risk Level**, **Number of Students**

### Step 2: Connect Filters to Dashboard Cards (Manual)

Metabase requires manual configuration to link filters to specific visualizations:

#### For Dashboard 1 (Example):

1. **Open dashboard**: http://localhost:3000/dashboard/32
2. **Click gear icon** (⚙️) → **Edit dashboard**
3. **Click on "School" filter** dropdown
4. **Click "Edit"** button
5. **Select "This should apply to"** → Choose all cards (charts/tables)
6. **Map to field**: Select `primary_school` field
7. **Save**
8. **Repeat** for Grade Level, Risk Level, and Row Limit filters

**Field Mappings for Dashboard 1:**
- School filter → `primary_school` field
- Grade Level filter → `grade_level` field
- Risk Level filter → `wellbeing_risk_level` field
- Row Limit filter → Query `LIMIT` clause (requires SQL modification)

#### For Other Dashboards:

Repeat the same process. Refer to `DASHBOARD-FILTERS-SPEC.md` for complete field mappings for each dashboard.

---

## Troubleshooting

### Issue: "Authentication failed"

**Solution**:
- Verify email/password are correct
- Try logging into Metabase UI manually first
- Check if account has admin privileges

### Issue: "Dashboard not found (404)"

**Solution**:
```bash
# Verify dashboards exist in Metabase
curl -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  http://localhost:3000/api/dashboard/32

# If not found, re-run dashboard creation:
python3 create-dashboards-api.py
```

### Issue: "Parameters not showing in UI"

**Solution**:
- Refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- Clear browser cache
- Try different browser
- Check Metabase logs: `docker logs oss-metabase`

### Issue: "Filters showing but not affecting visualizations"

**Cause**: This is expected! Filters need to be manually connected (see Step 2 above).

**Solution**: Follow "Post-Execution Steps" to connect filters to cards.

---

## Alternative: Manual Filter Addition (No Script)

If the script fails or you prefer UI configuration:

### Manual Steps for Each Dashboard:

1. Open dashboard in Metabase
2. Click **⚙️ (gear icon)** → **Edit dashboard**
3. Click **Filter** button
4. Select filter type (Text, Number, Date, etc.)
5. Configure:
   - **Name**: Filter display name
   - **Type**: Dropdown, search box, etc.
   - **Default value**: Optional
6. Connect to cards:
   - Click filter → **Edit**
   - Select cards to apply to
   - Map to database field
7. Click **Save**

Refer to `DASHBOARD-FILTERS-SPEC.md` for complete specifications.

---

## Files Created/Modified

| File | Purpose |
|------|---------|
| `add-dashboard-filters.py` | Main Python script (executable) |
| `ADD-FILTERS-README.md` | This usage guide |
| `DASHBOARD-FILTERS-SPEC.md` | Complete filter specifications (reference) |

---

## Next Actions

After filters are added and connected:

1. ✅ **Test each filter** - Verify dropdowns populate with data
2. ✅ **Test filter interactions** - Ensure visualizations update when filters change
3. ✅ **Close Beads** - Mark dashboard filter tasks complete
   ```bash
   bd close openedDataEstate-3ih -m "Dashboard 1 filters added"
   bd close openedDataEstate-z8v -m "Dashboard 2 filters added"
   bd close openedDataEstate-65q -m "Dashboard 3 filters added"
   bd close openedDataEstate-7qb -m "Dashboard 4 filters added"
   bd close openedDataEstate-e6p -m "Dashboard 5 filters added"
   ```
4. ✅ **UAT Testing** - Run user acceptance tests with end users
5. ✅ **Training** - Deliver training to staff using updated training guides

---

## Support

**Issues**: Check `TROUBLESHOOTING.md` in same directory  
**Dashboard Specs**: See `DASHBOARD-FILTERS-SPEC.md`  
**Metabase Docs**: https://www.metabase.com/docs/latest/

---

**Created**: January 29, 2026  
**Author**: OSS Framework Development Team  
**Status**: Ready for Production Use
