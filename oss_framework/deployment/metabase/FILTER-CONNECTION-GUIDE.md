# Metabase Dashboard Filter Connection Guide

## Overview

This guide provides step-by-step instructions for connecting dashboard filters to their respective visualization cards in Metabase. The filters have been created programmatically but require manual UI configuration to link them to the underlying database fields.

**Time Required**: 25-50 minutes (5-10 minutes per dashboard)

**Prerequisites**:
- Metabase running at http://localhost:3000
- Logged in as: frank.lucido@gmail.com
- Dashboards already created (IDs 2-6)
- Filters already added (16 total filters)

---

## Why Manual Configuration Is Required

Metabase's API allows creating filter parameters but does NOT support:
- Auto-discovering which fields exist in visualization queries
- Automatically mapping filters to card fields
- Field ID discovery without executing queries

Therefore, the UI is required to:
1. Inspect each card's query to find available fields
2. Map filter parameters to those fields
3. Save the mappings

---

## Quick Reference: Dashboard URLs

| Dashboard | URL |
|-----------|-----|
| Dashboard 1: Chronic Absenteeism Risk | http://localhost:3000/dashboard/2 |
| Dashboard 2: Student Wellbeing Risk Profiles | http://localhost:3000/dashboard/3 |
| Dashboard 3: Equity Outcomes Analysis | http://localhost:3000/dashboard/4 |
| Dashboard 4: Class Effectiveness Comparison | http://localhost:3000/dashboard/5 |
| Dashboard 5: Performance Correlations | http://localhost:3000/dashboard/6 |

---

## General Process (Same for All Dashboards)

### Step 1: Enter Edit Mode
1. Open dashboard in browser
2. Click the **gear icon (⚙️)** in the top-right corner
3. Select **"Edit dashboard"**
4. You'll see filter dropdowns at the top of the dashboard

### Step 2: Connect Each Filter
1. Click on a **filter dropdown** (e.g., "School")
2. Click **"Edit"** button (appears when you hover)
3. Click **"+ Add a variable to [number] cards"** or **"Select..."**
4. Check the boxes for cards you want to filter
5. For each checked card, select the **database field** to map to
6. Click **"Done"**

### Step 3: Save Dashboard
1. Click the blue **"Save"** button in the top-right
2. Test the filter by selecting a value from the dropdown
3. Verify visualizations update

---

## Database Schema Reference

All visualizations query views in schema: `main_main_analytics`

### Available Views

| View Name | Key Fields |
|-----------|------------|
| `v_chronic_absenteeism_risk` | `student_id_hash`, `primary_school`, `grade_level`, `attendance_rate_30d`, `wellbeing_risk_level`, `risk_score` |
| `v_wellbeing_risk_profiles` | `student_id_hash`, `primary_school`, `grade_level`, `attendance_risk`, `discipline_risk`, `academic_risk`, `compound_risk` |
| `v_equity_outcomes_by_demographics` | `demographic_group`, `cohort_size`, `pct_good_attendance`, `avg_gpa`, `pct_chronic_absent` |
| `v_class_section_comparison` | `course_name`, `teacher_id_hash`, `school_name`, `grade_level`, `term`, `enrollment_count`, `pct_passed`, `effectiveness_rating` |
| `v_performance_correlations` | `correlation_name`, `correlation_value`, `strength`, `direction` |

---

## Dashboard 1: Chronic Absenteeism Risk

**URL**: http://localhost:3000/dashboard/2

### Filters to Connect (4 filters)

#### Filter 1: School
- **Filter Type**: `string/=`
- **Purpose**: Filter by school name
- **Connect to Cards**: All 5 cards
- **Map to Field**: `primary_school`
- **Steps**:
  1. Click "School" dropdown → "Edit"
  2. Check all 5 cards:
     - Risk Distribution by Level
     - Total Students Monitored
     - Chronic Absenteeism Rate
     - Top 20 At-Risk Students
     - Chronic Absenteeism by Grade
  3. For each card, select field: `primary_school`
  4. Click "Done"

#### Filter 2: Grade Level
- **Filter Type**: `string/=`
- **Purpose**: Filter by grade (K, 1, 2, etc.)
- **Connect to Cards**: All 5 cards
- **Map to Field**: `grade_level`
- **Steps**:
  1. Click "Grade Level" dropdown → "Edit"
  2. Check all 5 cards
  3. For each card, select field: `grade_level`
  4. Click "Done"

#### Filter 3: Risk Level
- **Filter Type**: `string/=`
- **Purpose**: Filter by wellbeing risk category (Low, Medium, High, Critical)
- **Connect to Cards**: Cards showing risk levels (3-4 cards recommended)
  - Risk Distribution by Level
  - Top 20 At-Risk Students
  - Chronic Absenteeism Rate (optional)
- **Map to Field**: `wellbeing_risk_level`
- **Steps**:
  1. Click "Risk Level" dropdown → "Edit"
  2. Check cards that display risk-level data
  3. For each card, select field: `wellbeing_risk_level`
  4. Click "Done"

#### Filter 4: Number of Students
- **Filter Type**: `number/=`
- **Purpose**: Limit number of rows displayed (row limit)
- **Connect to Cards**: "Top 20 At-Risk Students" card
- **Special Note**: This is a **row limit filter**, not a field filter
- **Steps**:
  1. Click "Number of Students" dropdown → "Edit"
  2. Check "Top 20 At-Risk Students" card
  3. Look for "Limit" or "Row Count" option (NOT a field mapping)
  4. If no option available, leave this filter unconnected
  5. Click "Done"

### Verification
After connecting all filters:
1. Save dashboard
2. Select a school from "School" dropdown
3. Verify all 5 visualizations update
4. Select a grade level
5. Verify visualizations filter correctly

---

## Dashboard 2: Student Wellbeing Risk Profiles

**URL**: http://localhost:3000/dashboard/3

### Filters to Connect (3 filters)

#### Filter 1: School
- **Filter Type**: `string/=`
- **Connect to Cards**: Both cards (2 total)
  - Students by Wellbeing Level
  - Wellbeing Risk by Grade
- **Map to Field**: `primary_school`

#### Filter 2: Grade Level
- **Filter Type**: `string/=`
- **Connect to Cards**: Both cards (2 total)
- **Map to Field**: `grade_level`

#### Filter 3: Compound Risk Level
- **Filter Type**: `string/=`
- **Purpose**: Filter by compound risk (combination of attendance + discipline + academic)
- **Connect to Cards**: Both cards (2 total)
- **Map to Field**: `compound_risk`

### Verification
1. Save dashboard
2. Select a school → Verify both charts update
3. Select a compound risk level → Verify charts filter

---

## Dashboard 3: Equity Outcomes Analysis

**URL**: http://localhost:3000/dashboard/4

### Filters to Connect (3 filters)

#### Filter 1: School
- **Filter Type**: `string/=`
- **Connect to Cards**: Both cards (2 total)
  - Attendance Rate by Demographic
  - Opportunity Gap by Subgroup
- **Map to Field**: Try these field names (in order):
  1. `primary_school` (if available)
  2. `school_name` (alternate field name)
  3. Any school-related field shown in dropdown

**Note**: This view aggregates by demographics, so school field may not be present. If no school field exists in the dropdown, skip this filter.

#### Filter 2: Demographic Group
- **Filter Type**: `string/=`
- **Purpose**: Filter by race/ethnicity, ELL, SPED, FRL status
- **Connect to Cards**: Both cards (2 total)
- **Map to Field**: `demographic_group`

#### Filter 3: Minimum Cohort Size (FERPA)
- **Filter Type**: `number/>=`
- **Purpose**: FERPA compliance - hide results for groups < N students
- **Connect to Cards**: Both cards (2 total)
- **Map to Field**: `cohort_size`
- **Default Value**: 10 (FERPA minimum)

**Important**: This filter ensures small groups (< 10 students) are not displayed, protecting student privacy.

### Verification
1. Save dashboard
2. Set "Minimum Cohort Size" to 10
3. Verify small demographic groups disappear
4. Select a demographic group → Verify charts update

---

## Dashboard 4: Class Effectiveness Comparison

**URL**: http://localhost:3000/dashboard/5

### Filters to Connect (4 filters)

#### Filter 1: School
- **Filter Type**: `string/=`
- **Connect to Cards**: "Class Section Performance" card (1 card)
- **Map to Field**: `school_name`

#### Filter 2: Teacher
- **Filter Type**: `string/=`
- **Purpose**: Filter by teacher (pseudonymized hash)
- **Connect to Cards**: "Class Section Performance" card (1 card)
- **Map to Field**: `teacher_id_hash`

**Note**: Teacher IDs are hashed for privacy. Values will look like `a3f5b9c2...`

#### Filter 3: Grade Level
- **Filter Type**: `string/=`
- **Connect to Cards**: "Class Section Performance" card (1 card)
- **Map to Field**: `grade_level`

#### Filter 4: Term
- **Filter Type**: `string/=`
- **Purpose**: Filter by school term (Fall, Spring, Q1, Q2, etc.)
- **Connect to Cards**: "Class Section Performance" card (1 card)
- **Map to Field**: `term`

### Verification
1. Save dashboard
2. Select a school → Verify table updates
3. Select a teacher → Verify only that teacher's classes show
4. Combine filters (School + Grade) → Verify results narrow

---

## Dashboard 5: Performance Correlations

**URL**: http://localhost:3000/dashboard/6

### Filters to Connect (2 filters)

#### Filter 1: School
- **Filter Type**: `string/=`
- **Connect to Cards**: "Performance Correlations" card (1 card)
- **Map to Field**: Look for school field (may not exist in this aggregated view)

**Note**: This view shows correlation statistics, which may be calculated across all schools. If no school field exists, skip this filter.

#### Filter 2: Date Range
- **Filter Type**: `date/range`
- **Purpose**: Filter correlations by date range
- **Connect to Cards**: "Performance Correlations" card (1 card)
- **Map to Field**: Look for date fields like:
  - `school_year`
  - `analysis_date`
  - `date_range_start` / `date_range_end`

**Note**: If no date fields exist in the query, this filter cannot be connected. Leave unconnected.

### Verification
1. Save dashboard
2. If school filter connected: Select a school → Verify correlations recalculate
3. If date range connected: Select a range → Verify results update

---

## Troubleshooting

### Issue: No Fields Available in Dropdown

**Symptom**: When trying to map a filter to a card, no fields appear in the dropdown.

**Causes**:
1. The card's query doesn't include that field
2. The query uses aggregations that remove individual fields
3. The card uses a custom SQL query without named columns

**Solutions**:
- **Option 1**: Edit the card's query to include the field
- **Option 2**: Skip connecting that filter to that specific card
- **Option 3**: Modify the underlying SQL query (advanced)

**Example**: Dashboard 3 (Equity Outcomes) aggregates by `demographic_group` and may not include `school_name`. In this case, the School filter cannot be connected.

---

### Issue: Filter Doesn't Affect Visualization

**Symptom**: After connecting filter, selecting a value doesn't update the card.

**Causes**:
1. Filter mapped to wrong field
2. Field name mismatch (e.g., `school` vs `school_name`)
3. Data type mismatch (e.g., string filter on numeric field)

**Solutions**:
1. Re-edit the filter mapping
2. Check the card's SQL query for exact field names
3. Try alternative field names from the dropdown
4. Verify data types match (string filter → string field)

**Verification Query**:
```sql
-- Check available fields in a view
SELECT * FROM main_main_analytics.v_chronic_absenteeism_risk LIMIT 1;
```

---

### Issue: Filter Shows No Values

**Symptom**: Filter dropdown is empty when clicked.

**Causes**:
1. Filter not connected to any cards
2. No data in the database for that field
3. Field contains only NULL values

**Solutions**:
1. Connect filter to at least one card
2. Verify data exists:
   ```sql
   SELECT DISTINCT primary_school 
   FROM main_main_analytics.v_chronic_absenteeism_risk 
   LIMIT 20;
   ```
3. If field is always NULL, edit the card query to populate it

---

### Issue: "This question can't be filtered by this parameter"

**Symptom**: Error message when trying to connect filter.

**Causes**:
1. Card uses native SQL query (not visual query builder)
2. Field referenced in filter doesn't exist in query
3. Parameter type mismatch

**Solutions**:
1. Edit the card to use visual query builder
2. Modify SQL query to include the field
3. Change filter type to match field type

---

## Field Mapping Quick Reference

Use this table to quickly find the correct field for each filter:

| Filter Name | Dashboard(s) | Map to Field | Notes |
|-------------|--------------|--------------|-------|
| School | 1, 2 | `primary_school` | Student's primary school |
| School | 3, 4, 5 | `school_name` | May not exist in aggregated views |
| Grade Level | 1, 2, 4 | `grade_level` | Format: "K", "1", "2", etc. |
| Risk Level | 1 | `wellbeing_risk_level` | Values: Low, Medium, High, Critical |
| Compound Risk Level | 2 | `compound_risk` | Combined risk score |
| Demographic Group | 3 | `demographic_group` | Race/ethnicity, ELL, SPED, FRL |
| Minimum Cohort Size | 3 | `cohort_size` | FERPA compliance threshold |
| Teacher | 4 | `teacher_id_hash` | Pseudonymized teacher ID |
| Term | 4 | `term` | School term/semester |
| Date Range | 5 | (varies) | Look for date fields in query |
| Number of Students | 1 | (row limit) | Special filter - limits result rows |

---

## Verifying Field Names in Database

If you're unsure which field name to use, run these SQL queries in Metabase:

### Query 1: List All Fields in a View
```sql
-- Replace view name with the one you're working with
SELECT * 
FROM main_main_analytics.v_chronic_absenteeism_risk 
LIMIT 1;
```

This shows all column names.

### Query 2: Get Distinct Values for a Field
```sql
-- Replace view and field name
SELECT DISTINCT primary_school 
FROM main_main_analytics.v_chronic_absenteeism_risk 
ORDER BY primary_school;
```

This shows what values exist in that field.

### Query 3: Verify Filter Field Exists
```sql
-- Check if 'primary_school' exists in the view
SELECT primary_school, grade_level, COUNT(*) as student_count
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY primary_school, grade_level
ORDER BY student_count DESC;
```

This confirms the field exists and has data.

---

## Testing Filters After Connection

### Test Plan for Each Dashboard

1. **Initial Load**:
   - Open dashboard
   - Verify all visualizations load without errors
   - Note the total record count

2. **Single Filter Test**:
   - Select a value from one filter (e.g., School = "Lincoln Elementary")
   - Verify all connected cards update
   - Verify record counts decrease appropriately

3. **Multiple Filter Test**:
   - Keep first filter active
   - Select a value from second filter (e.g., Grade Level = "5")
   - Verify visualizations narrow further
   - Verify results are logical (intersection of both filters)

4. **Clear Filter Test**:
   - Click "X" to clear one filter
   - Verify visualizations return to previous state
   - Clear all filters
   - Verify visualizations return to original state

5. **Edge Case Test**:
   - Select combination with NO results (e.g., School X + Risk Level that doesn't exist)
   - Verify dashboards show "No results" gracefully (not errors)

---

## Performance Tips

### Indexed Fields
These fields are indexed in DuckDB for fast filtering:
- `student_id_hash`
- `primary_school`
- `grade_level`
- `teacher_id_hash`

Filters on these fields will be fast (< 1 second).

### Non-Indexed Fields
These fields may be slower:
- `wellbeing_risk_level`
- `compound_risk`
- `demographic_group`

Expect 1-3 second response times.

### Optimization Tips
1. Apply narrowest filter first (School, then Grade)
2. Avoid selecting "All" for multiple filters simultaneously
3. Use FERPA minimum cohort size (10) to reduce result set

---

## Advanced: Editing Card Queries

If a filter cannot be connected because the field doesn't exist, you can edit the card's query:

### Step 1: Edit the Card
1. Go to the dashboard
2. Click on the card you want to edit
3. Click the three dots (...) → "Edit query"

### Step 2: Add the Missing Field
**Visual Query Builder**:
1. Click "Pick columns"
2. Check the missing field (e.g., `primary_school`)
3. Click "Done"

**Native SQL**:
1. Add field to SELECT clause:
   ```sql
   SELECT 
     existing_field,
     primary_school  -- Add this line
   FROM main_main_analytics.v_chronic_absenteeism_risk
   ```
2. Click "Save"

### Step 3: Return to Dashboard
1. Go back to the dashboard
2. Re-connect the filter to the updated card

---

## Summary Checklist

Use this checklist to track your progress:

### Dashboard 1: Chronic Absenteeism Risk
- [ ] School filter → All 5 cards → `primary_school`
- [ ] Grade Level filter → All 5 cards → `grade_level`
- [ ] Risk Level filter → 3-4 cards → `wellbeing_risk_level`
- [ ] Number of Students filter → 1 card → (row limit)
- [ ] Save dashboard
- [ ] Test filters

### Dashboard 2: Student Wellbeing Risk Profiles
- [ ] School filter → Both cards → `primary_school`
- [ ] Grade Level filter → Both cards → `grade_level`
- [ ] Compound Risk Level filter → Both cards → `compound_risk`
- [ ] Save dashboard
- [ ] Test filters

### Dashboard 3: Equity Outcomes Analysis
- [ ] School filter → Both cards → `school_name` (if exists)
- [ ] Demographic Group filter → Both cards → `demographic_group`
- [ ] Minimum Cohort Size filter → Both cards → `cohort_size`
- [ ] Save dashboard
- [ ] Test filters (especially FERPA threshold)

### Dashboard 4: Class Effectiveness Comparison
- [ ] School filter → 1 card → `school_name`
- [ ] Teacher filter → 1 card → `teacher_id_hash`
- [ ] Grade Level filter → 1 card → `grade_level`
- [ ] Term filter → 1 card → `term`
- [ ] Save dashboard
- [ ] Test filters

### Dashboard 5: Performance Correlations
- [ ] School filter → 1 card → (if field exists)
- [ ] Date Range filter → 1 card → (if field exists)
- [ ] Save dashboard
- [ ] Test filters

### Final Verification
- [ ] All 5 dashboards saved
- [ ] All filters tested and working
- [ ] No errors when selecting filter values
- [ ] Visualizations update correctly
- [ ] FERPA compliance verified (Dashboard 3)

---

## Expected Time Investment

| Dashboard | Filters | Estimated Time |
|-----------|---------|----------------|
| Dashboard 1 | 4 | 10 minutes |
| Dashboard 2 | 3 | 5 minutes |
| Dashboard 3 | 3 | 7 minutes (FERPA testing) |
| Dashboard 4 | 4 | 8 minutes |
| Dashboard 5 | 2 | 5 minutes |
| **Total** | **16** | **35 minutes** |

Add 10-15 minutes for testing and troubleshooting.

**Total estimated time**: 45-50 minutes

---

## Getting Help

If you encounter issues:

1. **Check this guide**: Most common issues are covered in Troubleshooting
2. **Verify field names**: Run SQL queries to confirm field names
3. **Check Metabase logs**: Look for errors in browser console (F12)
4. **Test with SQL**: Manually test queries in Metabase SQL editor

---

## Next Steps After Completion

Once all filters are connected:

1. **User Acceptance Testing (UAT)**:
   - Have end-users test each dashboard
   - Gather feedback on filter usefulness
   - Identify additional filters needed

2. **Documentation**:
   - Create user guides for each dashboard
   - Document common filter combinations
   - Record training videos

3. **Access Control**:
   - Set up user groups in Metabase
   - Restrict access to sensitive dashboards (e.g., teacher effectiveness)
   - Configure row-level security if needed

4. **Performance Monitoring**:
   - Monitor query times
   - Optimize slow queries
   - Add database indexes if needed

5. **Close Beads**:
   ```bash
   bd close openedDataEstate-3ih -m "Dashboard 1 filters complete"
   bd close openedDataEstate-z8v -m "Dashboard 2 filters complete"
   bd close openedDataEstate-65q -m "Dashboard 3 filters complete"
   bd close openedDataEstate-7qb -m "Dashboard 4 filters complete"
   bd close openedDataEstate-e6p -m "Dashboard 5 filters complete"
   ```

---

## Document Information

**Created**: January 29, 2026  
**Last Updated**: January 29, 2026  
**Author**: OSS Framework Team  
**Version**: 1.0  

**Related Files**:
- `create-dashboards-api.py` - Dashboard creation script
- `add-dashboard-filters.py` - Filter creation script
- `DASHBOARD-FILTERS-SPEC.md` - Technical filter specifications
- `HANDOFF.md` - Complete implementation handoff

**Support**: For questions or issues, contact the OSS Framework team.
