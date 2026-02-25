# Dashboard Verification Checklist

## After running create-dashboards-api.py, verify each dashboard:

### Dashboard 1: Chronic Absenteeism Risk
- [ ] Pie chart shows risk distribution (Critical/High/Medium/Low) with colors
- [ ] "Total Students Monitored" shows 3,400
- [ ] "Chronic Absenteeism Rate" shows percentage (should be ~10-15%)
- [ ] Table shows top 20 at-risk students with attendance rates
- [ ] Bar chart shows chronic rate by grade level
- [ ] Trend chart shows attendance over time

**Expected data**: 3,400 students with varying risk levels

### Dashboard 2: Student Wellbeing & Mental Health
- [ ] Compound risk chart shows distribution across risk quadrants
- [ ] Multi-domain table shows students with breakdown by domain
- [ ] Risk score distribution histogram displays
- [ ] Key metrics cards show numbers

**Expected data**: 3,400 students with attendance/discipline/academic risk scores

### Dashboard 3: Equity Outcomes Analysis
- [ ] Table shows 5 demographic groups (White, Hispanic, Black, Asian, Multiple)
- [ ] Bar charts compare GPA and attendance by demographics
- [ ] ELL/SPED/FRL comparison charts display
- [ ] Each group shows: cohort size, GPA, attendance rate

**Expected data**: 5 demographic groups with aggregated metrics

### Dashboard 4: Class Effectiveness Comparison
- [ ] Table shows ~300 class sections
- [ ] Scatter plot shows enrollment vs pass rate
- [ ] Top/bottom performers lists display
- [ ] GPA distribution by effectiveness rating shows

**Expected data**: 300 class sections with effectiveness ratings

### Dashboard 5: Performance Correlations
- [ ] Table shows 3 correlation pairs:
  - Attendance ↔ GPA (strong positive, ~0.65)
  - Discipline ↔ GPA (moderate negative, ~-0.35)
  - Attendance ↔ Discipline (weak negative, ~-0.25)
- [ ] Each shows correlation value, strength, direction

**Expected data**: 3 statistical correlations with interpretation

---

## Common Issues and Solutions

### Issue: "No results found"
**Cause**: Query failed or returned empty
**Solution**: 
1. Click "Show Editor" on the visualization
2. Check if SQL query runs successfully
3. Verify schema name is `main_main_analytics.v_...`
4. Try running query manually in SQL editor

### Issue: "Unknown table"
**Cause**: Schema prefix missing or incorrect
**Solution**:
1. Go to Metabase → SQL Editor
2. Run: `SELECT schema_name, table_name FROM information_schema.tables WHERE table_type = 'VIEW';`
3. Verify views exist in `main_main_analytics` schema
4. If schema name is different, report to developer

### Issue: Numbers seem wrong
**Cause**: Data may be test data or need refresh
**Solution**:
1. Verify this is expected: 3,400 students is synthetic data
2. Check data freshness: when was oea.duckdb last updated?
3. Re-run dbt if needed: `cd oss_framework && dbt build --select stage3`

---

## Verification Complete ✅

Once all checkboxes above are checked, dashboards are verified working.

Report any issues with:
- Dashboard name
- Specific visualization that failed
- Error message (if any)
- Screenshot (if helpful)
