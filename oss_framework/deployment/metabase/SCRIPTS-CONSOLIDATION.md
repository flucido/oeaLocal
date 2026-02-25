# Dashboard Script Consolidation Guide

## Overview
This directory contains three dashboard creation scripts with different approaches and maturity levels. This guide clarifies which script to use for different purposes.

---

## Scripts Comparison

### 1. **create-dashboards-api.py** ⭐ **PRIMARY - READY TO USE**

**Purpose:** Complete, production-ready dashboard creation via Metabase API

**Location:** `oss_framework/deployment/metabase/create-dashboards-api.py`

**Features:**
- ✅ Full dashboard creation workflow (authenticate → cleanup → create 5 dashboards)
- ✅ Creates all 26 visualizations across 5 analytics dashboards
- ✅ Proper error handling and retry logic
- ✅ Uses correct schema prefix (`main_main_analytics.`)
- ✅ Targets correct port (3000)
- ✅ Fully tested and documented

**Use When:**
- Creating dashboards from scratch
- Recreating dashboards after SQL changes
- Production deployment
- **THIS IS THE DEFAULT SCRIPT - USE THIS ONE**

**Usage:**
```bash
cd oss_framework/deployment/metabase

# Set credentials
export METABASE_EMAIL="admin@example.com"
export METABASE_PASSWORD="your-password"

# Run script
python3 create-dashboards-api.py
```

**What It Creates:**
1. **Chronic Absenteeism Risk Dashboard** - 6 visualizations
2. **Student Wellbeing & Mental Health Dashboard** - 5 visualizations  
3. **Equity & Outcomes Dashboard** - 5 visualizations
4. **Class Effectiveness Dashboard** - 5 visualizations
5. **Performance Correlations Dashboard** - 5 visualizations

**Line Count:** 772 lines

---

### 2. **metabase_provisioning.py** 📋 **REFERENCE - TEMPLATE GENERATOR**

**Purpose:** Dashboard specification templates and JSON export (NOT API creation)

**Location:** `oss_framework/dashboards/metabase_provisioning.py`

**Features:**
- ✅ Comprehensive dashboard specifications using dataclasses
- ✅ Exports dashboard definitions to JSON files
- ✅ Well-documented query templates
- ✅ Row-level security (RBAC) specifications
- ❌ Does NOT create dashboards via API (JSON export only)

**Use When:**
- Reviewing dashboard specifications
- Understanding dashboard structure
- Exporting dashboard definitions for documentation
- Planning new dashboards

**NOT For:**
- Actually creating dashboards in Metabase
- Production deployment

**Usage:**
```bash
cd oss_framework/dashboards
python3 metabase_provisioning.py
```

**Output:** JSON files in `./metabase_exports/` directory

**Line Count:** 899 lines

---

### 3. **metabase_automation_script.py** 🚧 **EXPERIMENTAL - DO NOT USE**

**Purpose:** Modular automation attempt (incomplete)

**Location:** `oss_framework/dashboards/metabase_automation_script.py`

**Features:**
- ⚠️ Modular design with separate functions
- ⚠️ Only has 3 dashboards (missing 2)
- ⚠️ Incomplete implementation
- ⚠️ Less robust error handling
- ✅ Now targets correct port (3000) after fix

**Use When:**
- **DON'T USE THIS SCRIPT**
- It's an experimental alternative that was never completed
- Kept for reference only

**Status:** Incomplete, superseded by `create-dashboards-api.py`

**Line Count:** 381 lines

---

## Decision Tree: Which Script to Use?

```
┌─────────────────────────────────────────┐
│   What do you want to do?              │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┴─────────┐
       │                   │
   Create               Review/Export
   dashboards           specifications
   in Metabase          to JSON
       │                   │
       ▼                   ▼
   create-          metabase_
   dashboards-      provisioning.py
   api.py
   ⭐ PRIMARY       📋 REFERENCE
```

---

## Recommendation Summary

| Task | Script | Status |
|------|--------|--------|
| **Create dashboards in production** | `create-dashboards-api.py` | ✅ USE THIS |
| **Review dashboard specs** | `metabase_provisioning.py` | ✅ Reference only |
| **Export JSON definitions** | `metabase_provisioning.py` | ✅ Reference only |
| **Modular automation** | `metabase_automation_script.py` | ❌ DO NOT USE |

---

## Migration Notes

**From metabase_automation_script.py → create-dashboards-api.py:**
- All functionality moved to create-dashboards-api.py
- Port configuration fixed (3000)
- Added 2 missing dashboards
- Improved error handling
- No migration needed - just use create-dashboards-api.py

**From metabase_provisioning.py → create-dashboards-api.py:**
- Dashboard specs copied from provisioning.py
- API creation logic added
- Correct schema prefixes added
- No need to run provisioning.py first - create-dashboards-api.py is standalone

---

## Future Consolidation

**Potential Cleanup (Low Priority):**
1. Archive `metabase_automation_script.py` to `archive/` directory
2. Consider merging `metabase_provisioning.py` dataclasses into `create-dashboards-api.py`
3. Single source of truth: One script for both JSON export AND API creation

**Current Status: NOT BLOCKING**
- All three scripts coexist without conflicts
- Each serves a distinct purpose (even if one is deprecated)
- No urgent need to consolidate

---

## Troubleshooting

**Problem:** Multiple scripts targeting different ports

**Solution:** ✅ FIXED - All scripts now target port 3000

**Problem:** Don't know which script to run

**Solution:** Always use `create-dashboards-api.py` for dashboard creation

**Problem:** Want to understand dashboard structure before creating

**Solution:** Review `metabase_provisioning.py` dataclasses and queries first, then run `create-dashboards-api.py`

---

## File Locations Quick Reference

```
oss_framework/
├── deployment/metabase/
│   ├── create-dashboards-api.py        ⭐ PRIMARY
│   ├── SETUP-STATE.md                   📖 Current state doc
│   ├── SCRIPTS-CONSOLIDATION.md         📖 This file
│   └── .env.example                     🔒 Credentials template
└── dashboards/
    ├── metabase_provisioning.py         📋 Reference
    └── metabase_automation_script.py    🚧 Experimental
```

---

## Questions?

**"Should I run all three scripts?"**
No. Only run `create-dashboards-api.py`.

**"Will the other scripts cause problems?"**
No. They're standalone and won't interfere with each other.

**"Can I delete the other scripts?"**
Not recommended. Keep them as reference material.

**"Which script is maintained?"**
Only `create-dashboards-api.py` is actively maintained.

---

**Last Updated:** 2026-01-27  
**Status:** Port conflicts resolved, all scripts targeting correct instance (port 3000)
