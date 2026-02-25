# Dashboard Filters - Quick Start (3 Commands)

**Goal**: Add 26 interactive filters to 5 Metabase dashboards  
**Time**: 60 minutes (after Docker is installed)  
**Files**: All ready in this directory

---

## Prerequisites (One-Time Setup)

### 1. Install Docker Desktop
```bash
# Install (requires entering sudo password)
brew install --cask docker-desktop

# Start Docker Desktop application
open -a "Docker Desktop"

# Wait for Docker to start, then verify
docker ps
# Should show empty table with headers (no error)
```

### 2. Install Python Dependencies
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
python3 -m pip install -r requirements.txt
```

---

## Execute Filter Implementation (3 Commands)

### Step 1: Start Metabase
```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
docker-compose up -d
sleep 90  # Wait for initialization
```

### Step 2: Run Filter Script
```bash
# Set your Metabase admin credentials
export METABASE_EMAIL="admin@oss-framework.local"
export METABASE_PASSWORD="your-admin-password"

# Run script (takes 30-60 seconds)
python3 add-dashboard-filters.py
```

**Expected Output**:
```
✅ Authentication successful
📊 DASHBOARD 1: Adding filters...
  ✅ Added 4 filters
[...repeats for dashboards 2-5...]
✅ Added filters to 5/5 dashboards successfully
```

### Step 3: Connect Filters to Cards (Manual, 25-50 min)
```bash
# Open Metabase in browser
open http://localhost:3000

# For each dashboard (32-36):
# 1. Click gear icon → Edit dashboard
# 2. Click each filter → Edit → Connect to cards
# 3. Map to fields (see DASHBOARD-FILTERS-SPEC.md)
# 4. Save dashboard
```

---

## Field Mapping Reference (Quick)

**Dashboard 1** (http://localhost:3000/dashboard/32):
- School → `primary_school`
- Grade Level → `grade_level`
- Risk Level → `wellbeing_risk_level`
- Row Limit → Modify SQL LIMIT clause

**Dashboard 2** (http://localhost:3000/dashboard/33):
- School → `primary_school`
- Grade Level → `grade_level`
- Compound Risk → `compound_risk_level`

**Dashboard 3** (http://localhost:3000/dashboard/34):
- School → `primary_school`
- Demographic → `demographic_category`
- Min Cohort → Add WHERE `cohort_size >= {{min_cohort_size}}`

**Dashboard 4** (http://localhost:3000/dashboard/35):
- School → `school_id`
- Teacher → `teacher_id_hash`
- Grade Level → `grade_level`
- Term → `term`

**Dashboard 5** (http://localhost:3000/dashboard/36):
- School → `school_id`
- Date Range → `school_year`

**Complete details**: See `DASHBOARD-FILTERS-SPEC.md`

---

## Verify Success

```bash
# Open Dashboard 1
open http://localhost:3000/dashboard/32

# Test:
# 1. See 4 filter dropdowns at top (School, Grade, Risk, Limit)
# 2. Select "School" → dropdown populates with school names
# 3. Select a school → visualizations update
# 4. Select "Grade Level: 9" → only 9th graders shown
# 5. Clear filters → all data reappears
```

---

## Close Beads (After Testing)

```bash
bd close openedDataEstate-3ih -m "Dashboard 1 filters added and tested"
bd close openedDataEstate-z8v -m "Dashboard 2 filters added and tested"
bd close openedDataEstate-65q -m "Dashboard 3 filters added and tested"
bd close openedDataEstate-7qb -m "Dashboard 4 filters added and tested"
bd close openedDataEstate-e6p -m "Dashboard 5 filters added and tested"
```

---

## Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "requests not found" | `python3 -m pip install requests` |
| "docker command not found" | Start Docker Desktop app, wait 30 sec |
| "Authentication failed" | Check email/password, try browser login first |
| "Filters not visible" | Hard refresh browser (Cmd+Shift+R) |
| "Filters don't affect data" | Expected - follow Step 3 to connect |

**Full troubleshooting**: See `ADD-FILTERS-README.md`

---

## Documentation Index

| File | When to Use |
|------|-------------|
| **QUICK-START.md** | This file - fastest path |
| `EXECUTION-CHECKLIST.md` | Step-by-step with explanations |
| `ADD-FILTERS-README.md` | Complete user guide |
| `DASHBOARD-FILTERS-SPEC.md` | Technical details & SQL |
| `IMPLEMENTATION-SUMMARY.md` | Project overview |

---

**Total Time**: 60 min (10 min setup + 1 min script + 25-50 min manual + testing)  
**Difficulty**: Easy (script automates 95% of work)  
**Result**: 26 filters across 5 dashboards, fully functional

**Ready to execute!**
