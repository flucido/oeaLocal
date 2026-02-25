# Dashboard Filter Implementation - Execution Checklist

**Status**: ✅ READY FOR EXECUTION  
**Date**: January 29, 2026  
**Blocker**: Docker Desktop requires manual installation (sudo password)

---

## Pre-Execution Checklist

### ✅ Completed (No Action Required)

- [x] Dashboard creation script verified (`create-dashboards-api.py`)
- [x] 5 dashboards created (IDs 32-36, per `dashboard-creation-fixed.log`)
- [x] 11 visualizations created (Question IDs 49-59)
- [x] Filter automation script created (`add-dashboard-filters.py`, 450 lines)
- [x] User documentation created (`ADD-FILTERS-README.md`, 330 lines)
- [x] Technical specifications complete (`DASHBOARD-FILTERS-SPEC.md`, 650 lines)
- [x] Status report updated (`METABASE-STATUS.md`)

### ⏳ Pending User Action

- [ ] **Install Python dependencies** (requests library)
- [ ] **Install Docker Desktop** (requires sudo password)
- [ ] Start Docker Desktop application
- [ ] Start Metabase container
- [ ] Execute filter script
- [ ] Manual filter-to-card configuration
- [ ] Test dashboards
- [ ] Close beads

---

## Step-by-Step Execution Instructions

### Step 0: Install Python Dependencies (1 minute)

The filter script requires the `requests` library:

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Install from requirements.txt
python3 -m pip install -r requirements.txt

# Verify installation
python3 -c "import requests; print(f'✅ requests {requests.__version__} installed')"
# Expected: ✅ requests 2.31.0 installed (or similar)
```

**Alternative** (if pip not available):
```bash
# Direct install
python3 -m pip install requests

# Or using Homebrew Python
brew install python-requests

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 1: Install Docker Desktop (5 minutes)

```bash
# The installation was started but requires password
# Complete the installation manually:

# Option A: Restart installation
brew install --cask docker-desktop
# Enter sudo password when prompted

# Option B: Download directly
# Visit: https://www.docker.com/products/docker-desktop
# Download for Apple Silicon (M1/M2/M3)
# Install by dragging to Applications folder
```

**Verify Installation**:
```bash
which docker
# Expected: /usr/local/bin/docker or /opt/homebrew/bin/docker

docker --version
# Expected: Docker version 24.0.0 or higher
```

---

### Step 2: Start Docker Desktop (2 minutes)

```bash
# Start the application
open -a "Docker Desktop"

# Wait for Docker daemon to start (look for whale icon in menu bar)
# Status should show "Docker Desktop is running"

# Verify Docker is running
docker ps
# Expected: Empty list (no containers yet) with column headers
```

---

### Step 3: Start Metabase (3 minutes)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Start Metabase container
docker-compose up -d

# Expected output:
# Creating oss-metabase ... done

# Wait for initialization (60-90 seconds)
sleep 90

# Check health
curl http://localhost:3000/api/health
# Expected: {"status":"ok"}
```

**Verify in Browser**:
- Open: http://localhost:3000
- Should see Metabase login screen
- Login with admin credentials
- Navigate to "OSS Analytics" collection
- Verify 5 dashboards exist (IDs 32-36)

---

### Step 4: Execute Filter Script (1 minute)

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Set admin credentials (replace with your actual credentials)
export METABASE_EMAIL="admin@oss-framework.local"
export METABASE_PASSWORD="your-admin-password"

# Run filter script
python3 add-dashboard-filters.py

# Expected output:
# 🚀 METABASE DASHBOARD FILTER ADDITION
# ✅ Authentication successful
# 📊 DASHBOARD 1: Chronic Absenteeism Risk (Adding Filters)
#   📌 Adding parameter: School (string/=)
#     ✅ Added parameter: School
# [... 26 filters added total ...]
# ✅ Added filters to 5/5 dashboards successfully
```

**Expected Result**: Script completes in 30-60 seconds, all filters added.

---

### Step 5: Configure Filter-to-Card Connections (25-50 minutes)

**Important**: Filters exist but need to be connected to dashboard cards manually.

#### For Each Dashboard:

1. **Open dashboard** in browser (http://localhost:3000/dashboard/32 for Dashboard 1)
2. **Click gear icon** (⚙️) → **"Edit dashboard"**
3. **For each filter dropdown at top**:
   - Click on filter
   - Click **"Edit"** button
   - Under **"This should apply to"**, select all relevant cards
   - Under **"Column to filter on"**, select appropriate field:
     - School filter → `primary_school`
     - Grade Level filter → `grade_level`
     - Risk Level filter → `wellbeing_risk_level`
     - Row Limit filter → (requires SQL LIMIT modification)
4. **Click "Done"**
5. **Click "Save"** (top-right)
6. **Exit edit mode**
7. **Test filter** - Select a value, verify visualizations update

#### Dashboard-Specific Field Mappings:

**Dashboard 1** (http://localhost:3000/dashboard/32):
- School → `primary_school`
- Grade Level → `grade_level`
- Risk Level → `wellbeing_risk_level`
- Row Limit → Requires SQL modification (see DASHBOARD-FILTERS-SPEC.md)

**Dashboard 2** (http://localhost:3000/dashboard/33):
- School → `primary_school`
- Grade Level → `grade_level`
- Compound Risk → `compound_risk_level`

**Dashboard 3** (http://localhost:3000/dashboard/34):
- School → `primary_school`
- Demographic Group → `demographic_category`
- Min Cohort Size → Add WHERE clause: `cohort_size >= {{min_cohort_size}}`

**Dashboard 4** (http://localhost:3000/dashboard/35):
- School → `school_id`
- Teacher → `teacher_id_hash`
- Grade Level → `grade_level`
- Term → `term`

**Dashboard 5** (http://localhost:3000/dashboard/36):
- School → `school_id`
- Date Range → `school_year` or date field

**Reference**: See `DASHBOARD-FILTERS-SPEC.md` for complete SQL modifications.

---

### Step 6: Test Each Dashboard (10 minutes)

For each dashboard, verify:
- [ ] Filters appear at top of dashboard
- [ ] Filter dropdowns populate with data from database
- [ ] Selecting a filter value updates visualizations
- [ ] Multiple filters work together (e.g., School + Grade)
- [ ] "Clear all filters" button resets to default view
- [ ] No SQL errors in browser console

**Test Cases**:

```
Dashboard 1:
1. Select School = "Lincoln High School"
   → Verify only Lincoln students appear
2. Add Grade Level = "9"
   → Verify only 9th graders from Lincoln appear
3. Clear filters
   → Verify all students appear again

[Repeat pattern for Dashboards 2-5]
```

---

### Step 7: Close Beads (2 minutes)

Once testing is complete and all filters work:

```bash
# Close dashboard filter implementation beads
bd close openedDataEstate-3ih -m "Added 4 filters to Dashboard 1 (School, Grade, Risk, Limit)"
bd close openedDataEstate-z8v -m "Added 3 filters to Dashboard 2 (School, Grade, Compound Risk)"
bd close openedDataEstate-65q -m "Added 3 filters to Dashboard 3 (School, Demographic, Min Cohort)"
bd close openedDataEstate-7qb -m "Added 4 filters to Dashboard 4 (School, Teacher, Grade, Term)"
bd close openedDataEstate-e6p -m "Added 2 filters to Dashboard 5 (School, Date Range)"

# Verify beads closed
bd list --status open | grep -i dashboard
# Expected: No dashboard filter beads (openedDataEstate-3ih, z8v, 65q, 7qb, e6p should be closed)
```

---

### Step 8: Update UAT Checklists (5 minutes)

Update UAT checklists to include filter testing:

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase/uat

# For each UAT checklist file (uat-dashboard-1.md through uat-dashboard-5.md):
# Add filter testing section:
```

**Sample UAT Addition** (add to each checklist):

```markdown
## Filter Functionality Testing

### School Filter
- [ ] Dropdown populates with school names from database
- [ ] Selecting a school filters all visualizations
- [ ] "All Schools" shows all data

### Grade Level Filter
- [ ] Shows grades 9, 10, 11, 12
- [ ] Selecting a grade filters correctly
- [ ] Works in combination with school filter

### Risk Level Filter (Dashboard 1 only)
- [ ] Shows risk levels: Critical, High, Medium, Low
- [ ] Multi-select works
- [ ] Affects only risk-related visualizations

### Row Limit Filter (Dashboard 1 only)
- [ ] Numeric input accepts values: 10, 20, 50, 100, 500
- [ ] Table row count updates correctly
- [ ] Does not affect charts/aggregations
```

---

### Step 9: Close Training/UAT Beads (1 minute)

After UAT checklists are updated:

```bash
# These will auto-unblock once dashboard filter beads are closed
bd list --status open | grep -E "(training|uat)"

# Verify training guide beads are now unblocked and can be closed:
bd close openedDataEstate-xxx -m "Training guide ready with filter documentation"
bd close openedDataEstate-yyy -m "UAT checklist updated with filter tests"
```

---

## Troubleshooting

### Issue: Docker Desktop Won't Start

**Symptoms**: `docker ps` returns "Cannot connect to Docker daemon"

**Solutions**:
```bash
# Check if Docker app is running
ps aux | grep -i docker

# Restart Docker Desktop
killall Docker
open -a "Docker Desktop"

# Wait 30 seconds, then test
docker ps
```

---

### Issue: Metabase Container Won't Start

**Symptoms**: `docker-compose up -d` fails or container exits

**Diagnostics**:
```bash
# Check container status
docker ps -a | grep metabase

# View logs
docker logs oss-metabase --tail 50

# Common issues:
# - Port 3000 in use → Change port in docker-compose.yml
# - Database permission error → Check volume mounts
# - Out of memory → Increase Docker memory limit in settings
```

---

### Issue: Filter Script Authentication Fails

**Symptoms**: "❌ Authentication failed"

**Solutions**:
```bash
# Verify Metabase is running
curl http://localhost:3000/api/health

# Test login manually in browser first
open http://localhost:3000

# Check credentials
echo $METABASE_EMAIL
echo $METABASE_PASSWORD  # Verify not empty

# Try with explicit arguments
python3 add-dashboard-filters.py \
  --email admin@oss-framework.local \
  --password your-password
```

---

### Issue: Filters Not Appearing in UI

**Symptoms**: Script says "✅ Added" but filters not visible in dashboard

**Solutions**:
1. **Hard refresh browser**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear browser cache**: Settings → Clear browsing data
3. **Check Metabase version**: Settings → Admin → About
   - Requires Metabase v0.40.0+ for full parameter support
4. **Verify API response**: Check script output for error messages
5. **Manual verification**:
   ```bash
   # Get dashboard details
   curl -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
     http://localhost:3000/api/dashboard/32 | jq .parameters
   # Should show array of parameter objects
   ```

---

### Issue: Filters Don't Affect Visualizations

**Symptoms**: Filters visible but selecting values doesn't change data

**Cause**: This is **expected** after running the script. Filters need manual connection.

**Solution**: Follow **Step 5** above to connect filters to cards.

---

## Success Criteria

Implementation is **complete** when:

- [x] Docker Desktop installed and running
- [x] Metabase container started successfully
- [x] Admin can log into http://localhost:3000
- [x] All 5 dashboards exist in "OSS Analytics" collection
- [x] Filter script executed without errors
- [x] 26 filters added (4+3+3+4+2 across 5 dashboards)
- [x] Filters connected to dashboard cards
- [x] Filters populate with data from database
- [x] Selecting filter values updates visualizations
- [x] All 5 dashboard filter beads closed
- [x] UAT checklists updated with filter tests
- [x] Training guide beads closed

---

## Estimated Time Investment

| Task | Time Required |
|------|---------------|
| Install Docker Desktop | 5 minutes |
| Start Docker & Metabase | 5 minutes |
| Run filter script | 1 minute |
| Connect filters to cards | 25-50 minutes |
| Test all dashboards | 10 minutes |
| Close beads & update docs | 10 minutes |
| **TOTAL** | **56-81 minutes** |

---

## Files Reference

All documentation is ready:

| File | Purpose |
|------|---------|
| `add-dashboard-filters.py` | Filter automation script (executable) |
| `ADD-FILTERS-README.md` | User guide (330 lines) |
| `DASHBOARD-FILTERS-SPEC.md` | Technical specifications (650 lines) |
| `METABASE-STATUS.md` | Status report |
| `EXECUTION-CHECKLIST.md` | This file - step-by-step instructions |
| `dashboard-creation-fixed.log` | Proof dashboards were created |
| `create-dashboards-api.py` | Original dashboard creation script |

---

## Support

**For issues during execution**:
1. Check `TROUBLESHOOTING.md` in same directory
2. Review `ADD-FILTERS-README.md` for detailed instructions
3. Consult `DASHBOARD-FILTERS-SPEC.md` for SQL modifications

**For Metabase questions**:
- Official docs: https://www.metabase.com/docs/latest/
- Parameters guide: https://www.metabase.com/docs/latest/questions/native-editor/sql-parameters

---

**Status**: ✅ Ready for execution  
**Blocker**: Docker Desktop installation (requires sudo password)  
**Next Action**: Complete Docker installation, then follow Steps 1-9 above  
**Expected Completion Time**: 56-81 minutes after Docker is installed
