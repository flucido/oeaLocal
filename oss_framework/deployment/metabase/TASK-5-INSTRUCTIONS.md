# Task 5: Manual Filter Connection - Complete Instructions

## 🎯 Current Status

**Automated Work Complete**: 4/6 tasks (67%)
- ✅ Task 1: Pre-flight verification
- ✅ Task 2: Dashboard creation (5 dashboards, IDs: 1-5)
- ✅ Task 3: Filter script updates
- ✅ Task 4: Filter addition (16 filters created)

**Manual Work Required**: Task 5 (this document)

**What's Ready**:
- Metabase running at http://localhost:3000
- 5 dashboards created with visualizations
- 16 filters created but NOT connected to cards (0 mappings)
- Login credentials: `admin@example.com` / `admin123456`

---

## ⏱️ Time Required

- **Fast approach**: 15-25 minutes
- **Careful approach**: 30-50 minutes
- **Per dashboard**: 5-10 minutes each

---

## 📋 Quick Reference: Dashboard IDs & Filters

| Dashboard ID | Name | Filters | URL |
|-------------|------|---------|-----|
| 1 | Chronic Absenteeism Risk | 4 | http://localhost:3000/dashboard/1 |
| 2 | Student Wellbeing Risk Profiles | 3 | http://localhost:3000/dashboard/2 |
| 3 | Equity Outcomes Analysis | 3 | http://localhost:3000/dashboard/3 |
| 4 | Class Effectiveness Comparison | 4 | http://localhost:3000/dashboard/4 |
| 5 | Performance Correlations | 2 | http://localhost:3000/dashboard/5 |

**Total**: 16 filters across 5 dashboards

---

## 🚀 Step-by-Step Instructions

### Dashboard 1: Chronic Absenteeism Risk

**URL**: http://localhost:3000/dashboard/1

1. **Open Dashboard** → Click **pencil icon** (top right) → "Edit dashboard"

2. **Connect Filter 1: "School"**
   - Click the "School" filter dropdown
   - Click "Edit" button
   - Click "Connect to cards" or "Select cards"
   - Select ALL 5 cards (check all boxes)
   - For each card, map to field: `primary_school`
   - Click "Done"

3. **Connect Filter 2: "Grade Level"**
   - Click "Grade Level" filter → Edit
   - Select ALL 5 cards
   - Map to field: `grade_level`
   - Click "Done"

4. **Connect Filter 3: "Risk Level"**
   - Click "Risk Level" filter → Edit
   - Select ALL 5 cards
   - Map to field: `wellbeing_risk_level`
   - Click "Done"

5. **Connect Filter 4: "Number of Students"**
   - Click "Number of Students" filter → Edit
   - Select the card "Top 20 At-Risk Students"
   - Map to: SQL `LIMIT` clause (or row limit option)
   - **Note**: If no LIMIT option appears, skip this filter
   - Click "Done"

6. **Save Dashboard** → Click blue "Save" button (top right)

---

### Dashboard 2: Student Wellbeing Risk Profiles

**URL**: http://localhost:3000/dashboard/2

1. **Open Dashboard** → Click **pencil icon** → "Edit dashboard"

2. **Connect Filter 1: "School"**
   - Click "School" → Edit → Connect to ALL cards (2 cards)
   - Map to: `primary_school`
   - Done

3. **Connect Filter 2: "Grade Level"**
   - Click "Grade Level" → Edit → Connect to ALL cards
   - Map to: `grade_level`
   - Done

4. **Connect Filter 3: "Compound Risk"**
   - Click "Compound Risk" → Edit → Connect to ALL cards
   - Map to: `compound_risk_level`
   - Done

5. **Save Dashboard**

---

### Dashboard 3: Equity Outcomes Analysis

**URL**: http://localhost:3000/dashboard/3

1. **Open Dashboard** → Click **pencil icon** → "Edit dashboard"

2. **Connect Filter 1: "School"**
   - Click "School" → Edit → Connect to ALL cards (2 cards)
   - Map to: `primary_school`
   - **Note**: If `primary_school` not available, skip this filter (aggregated view)
   - Done

3. **Connect Filter 2: "Demographic"**
   - Click "Demographic" → Edit → Connect to ALL cards
   - Map to: `demographic_category`
   - Done

4. **Connect Filter 3: "Min Cohort"**
   - Click "Min Cohort" → Edit → Connect to ALL cards
   - Map to: SQL `WHERE` clause with `cohort_size` field
   - **Note**: This filters out small groups (FERPA compliance)
   - Done

5. **Save Dashboard**

---

### Dashboard 4: Class Effectiveness Comparison

**URL**: http://localhost:3000/dashboard/4

1. **Open Dashboard** → Click **pencil icon** → "Edit dashboard"

2. **Connect Filter 1: "School"**
   - Click "School" → Edit → Connect to card
   - Map to: `school_id`
   - Done

3. **Connect Filter 2: "Teacher"**
   - Click "Teacher" → Edit → Connect to card
   - Map to: `teacher_id_hash`
   - Done

4. **Connect Filter 3: "Grade Level"**
   - Click "Grade Level" → Edit → Connect to card
   - Map to: `grade_level`
   - Done

5. **Connect Filter 4: "Term"**
   - Click "Term" → Edit → Connect to card
   - Map to: `term`
   - Done

6. **Save Dashboard**

---

### Dashboard 5: Performance Correlations

**URL**: http://localhost:3000/dashboard/5

1. **Open Dashboard** → Click **pencil icon** → "Edit dashboard"

2. **Connect Filter 1: "School"**
   - Click "School" → Edit → Connect to card
   - Map to: `school_id`
   - **Note**: If field not available (aggregated view), skip
   - Done

3. **Connect Filter 2: "Date Range"**
   - Click "Date Range" → Edit → Connect to card
   - Map to: `school_year` (or any date field available)
   - **Note**: If no date field available, skip
   - Done

4. **Save Dashboard**

---

## ✅ Verification Checklist

After completing all 5 dashboards, test:

```
[ ] Dashboard 1 - 4 filters connected
    [ ] Select a school → Cards update
    [ ] Select a grade level → Cards update
    [ ] Select a risk level → Cards update

[ ] Dashboard 2 - 3 filters connected
    [ ] Select a school → Cards update
    [ ] Select a compound risk → Cards update

[ ] Dashboard 3 - 3 filters connected (or 2 if school skipped)
    [ ] Select a demographic → Cards update
    [ ] Set min cohort to 10 → Small groups hidden

[ ] Dashboard 4 - 4 filters connected
    [ ] Select a school → Card updates
    [ ] Select a teacher → Only that teacher's classes show

[ ] Dashboard 5 - 2 filters connected (or fewer if fields unavailable)
    [ ] Filters work if connected
```

---

## 🎉 When Complete

Reply with: **"Task 5 complete"**

The orchestrator will:
1. Mark Task 5 checkbox in the plan
2. Execute Task 6 (automated Playwright verification + screenshots)
3. Generate final completion report
4. Mark all remaining checkboxes (100% complete)

---

## 💡 Tips & Troubleshooting

### Tip: Speed Up the Process
- Connect all filters on a dashboard BEFORE clicking "Save"
- Use Tab key to navigate between fields
- Most filters connect to "all cards" on the dashboard

### Issue: Field Not Found in Dropdown

**Solution**: The view doesn't include that field. Skip the filter.

**Example**: Dashboard 3 (Equity Outcomes) aggregates by demographics and may not have `primary_school` field. This is expected - skip the School filter.

### Issue: Filter Doesn't Update Cards

**Cause**: Filter mapped to wrong field

**Solution**: 
1. Edit the filter again
2. Click "Disconnect" to remove mapping
3. Reconnect with correct field name

### Issue: No Values in Filter Dropdown

**Cause**: Filter not connected to any cards yet

**Solution**: Connect the filter to at least one card, then values will appear

---

## 📊 Field Mapping Reference

Quick lookup table:

| Filter Name | Map to Field | Dashboards |
|-------------|--------------|-----------|
| School | `primary_school` | 1, 2 |
| School | `school_id` | 4, 5 |
| School | `school_name` | 3 (if available) |
| Grade Level | `grade_level` | 1, 2, 4 |
| Risk Level | `wellbeing_risk_level` | 1 |
| Compound Risk | `compound_risk_level` | 2 |
| Demographic | `demographic_category` | 3 |
| Min Cohort | `cohort_size` | 3 |
| Teacher | `teacher_id_hash` | 4 |
| Term | `term` | 4 |
| Date Range | `school_year` | 5 |
| Number of Students | SQL LIMIT | 1 |

---

## 🔐 Credentials

**Metabase URL**: http://localhost:3000
**Username**: admin@example.com
**Password**: admin123456

---

## 📁 Related Documentation

- **Automation Summary**: `.sisyphus/notepads/metabase-dashboard-setup/AUTOMATION-LIMIT-REACHED.md`
- **Technical Details**: `oss_framework/deployment/metabase/FILTER-CONNECTION-GUIDE.md`
- **Original Plan**: `.sisyphus/plans/metabase-dashboard-setup.md`

---

## ⏭️ Next Steps After Completion

Once Task 5 is done, the system will automatically:
1. Execute Task 6 (Playwright verification)
2. Test all filters work correctly
3. Capture screenshots as evidence
4. Mark remaining 5 checkboxes complete
5. Generate final completion report

**No manual work needed after Task 5!**

---

**Document Created**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Status**: Ready for execution  
**Estimated Completion**: 15-50 minutes
