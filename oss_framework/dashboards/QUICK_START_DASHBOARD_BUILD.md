# Quick Start: Build Chronic Absenteeism Dashboard in Metabase

**Status**: Ready to implement  
**Time Required**: 2-3 hours  
**Difficulty**: Intermediate

---

## Prerequisites

- Metabase running at `http://localhost:3001`
- Admin account with credentials
- DuckDB analytics database connected
- Database schema synced in Metabase

---

##Step 1: Access Metabase & Login

1. Open browser: `http://localhost:3001`
2. Login with admin credentials:
   - Email: `admin@metabase.local` (or default)
   - Password: (your admin password)

**Expected Result**: You see the Metabase home dashboard

---

## Step 2: Verify DuckDB Connection

### If database is NOT yet connected:

1. Click **⚙ Settings** (top right)
2. Go to **Admin Panel → Databases**
3. Click **+ New database**
4. Select **DuckDB**
5. Configure:
   - **Name**: `OEA Analytics`
   - **Database file**: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
   - **Auto-run queries**: Toggle ON
   - **Query caching TTL**: `10` minutes
6. Click **Save**
7. Wait for "Sync database schema" to complete

**Expected Result**: Database appears in the list with green checkmark

### If database IS already connected:

Click **⚙ Settings → Admin Panel → Databases** and verify you see `OEA Analytics` with a green status.

---

## Step 3: Create New Dashboard

1. Click **+ New** (top left)
2. Select **Dashboard**
3. Name it: `Chronic Absenteeism Risk`
4. Description: `Real-time monitoring of students at risk of chronic absenteeism`
5. Click **Create**

**Expected Result**: Empty dashboard opens with edit mode active

---

## Step 4: Add Dashboard Filters

These filters will apply to all cards on the dashboard.

### Add Filter 1: School

1. Click **Filter** button (left side)
2. Click **+ Add filter**
3. Select **School** from column list (or select table first)
4. Choose **Specific values** or **Dropdown**
5. Label: `School`
6. Click **Add filter**

### Add Filter 2: Grade

1. Click **+ Add filter**
2. Select **Grade Level** column
3. Label: `Grade`
4. Click **Add filter**

### Add Filter 3: Risk Threshold

1. Click **+ Add filter**
2. Select **Numeric** type
3. Column: `chronic_absenteeism_risk_score`
4. Operator: `>=`
5. Label: `Risk Threshold`
6. Click **Add filter**

### Add Filter 4: Date Range

1. Click **+ Add filter**
2. Select **Date** type
3. Column: (check database for date column)
4. Label: `Date Range`
5. Click **Add filter**

**Expected Result**: 4 filter widgets appear above the dashboard

---

## Step 5: Create Tabs

1. Click the **+** icon next to "Tab 1" at the top
2. Rename tabs:
   - Tab 1 → "Overview"
   - Tab 2 → "Risk Distribution"
   - Tab 3 → "At-Risk Students"
   - Tab 4 → "Trends & Analysis"

**Expected Result**: 4 tabs visible at the top of the dashboard

---

## Step 6: Build Tab 1 - Overview (4 Cards)

### Card 1: Students at Risk

1. Go to **Overview** tab
2. Click **+ Add → Question**
3. Select **DuckDB / OEA Analytics**
4. Click **Native query**
5. Paste this SQL:

```sql
SELECT COUNT(*) as count 
FROM main_main_analytics.v_chronic_absenteeism_risk 
WHERE risk_classification IN ('Critical', 'High')
```

6. Click **Visualize**
7. Change visualization to **Number**
8. Format options:
   - Font size: **Large**
   - Color: **Red** (#E53935)
9. Click **Save**
10. Add to dashboard: "Chronic Absenteeism Risk"
11. Position: top-left, size: 4 columns × 2 rows
12. Save dashboard

**Expected Result**: Red number showing count of at-risk students

### Card 2: Chronic Absence Rate (%)

1. Click **+ Add → Question**
2. Select **DuckDB / OEA Analytics**
3. Click **Native query**
4. Paste this SQL:

```sql
SELECT ROUND(
  AVG(CASE WHEN chronic_absence_flag = true THEN 100 ELSE 0 END), 
  1
) as rate
FROM main_main_analytics.v_chronic_absenteeism_risk
```

5. Click **Visualize**
6. Change visualization to **Gauge**
7. Settings:
   - Min: 0
   - Max: 30
   - Thresholds: Green <15, Yellow 15-20, Red >20
8. Click **Save**
9. Add to dashboard: Position next to Card 1

**Expected Result**: Gauge visualization showing percentage

### Card 3: Declining Attendance (30 days)

1. Click **+ Add → Question**
2. Select **DuckDB / OEA Analytics**
3. Click **Native query**
4. Paste this SQL:

```sql
SELECT COUNT(*) as count
FROM main_main_analytics.v_chronic_absenteeism_risk
WHERE attendance_trend_30d = 'declining' 
   OR attendance_rate_30d < 85
```

5. Click **Visualize**
6. Change visualization to **Number**
7. Format: Orange color (#FB8C00)
8. Click **Save**
9. Add to dashboard below Card 1

**Expected Result**: Orange number showing declining attendance count

---

## Step 7: Build Tab 2 - Risk Distribution (2 Charts)

### Card 1: Risk Score Distribution (Bar Chart)

1. Go to **Risk Distribution** tab
2. Click **+ Add → Question**
3. Select **DuckDB / OEA Analytics**
4. Click **Native query**
5. Paste this SQL:

```sql
SELECT 
  ROUND(chronic_absenteeism_risk_score * 10) / 10 as risk_score,
  COUNT(*) as student_count
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY ROUND(chronic_absenteeism_risk_score * 10) / 10
ORDER BY risk_score
```

6. Click **Visualize**
7. Select visualization **Bar chart**
8. X-axis: `risk_score`
9. Y-axis: `student_count`
10. Click **Save**
11. Add to dashboard, position: top-left, size 6×4

**Expected Result**: Bar chart showing risk score distribution

### Card 2: Risk Classification Breakdown (Pie Chart)

1. Click **+ Add → Question**
2. Select **DuckDB / OEA Analytics**
3. Click **Native query**
4. Paste this SQL:

```sql
SELECT 
  risk_classification,
  COUNT(*) as count
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY risk_classification
ORDER BY risk_classification
```

5. Click **Visualize**
6. Select visualization **Pie chart**
7. Category: `risk_classification`
8. Value: `count`
9. Click **Save**
10. Add to dashboard next to Card 1

**Expected Result**: Pie chart showing classification breakdown

---

## Step 8: Build Tab 3 - At-Risk Students (Table)

1. Go to **At-Risk Students** tab
2. Click **+ Add → Question**
3. Select **DuckDB / OEA Analytics**
4. Click **Native query**
5. Paste this SQL:

```sql
SELECT 
  student_key as "Student ID",
  grade_level as "Grade",
  school_id as "School",
  ROUND(chronic_absenteeism_risk_score, 2) as "Risk Score",
  risk_classification as "Risk Level",
  ROUND(attendance_rate_30d, 1) as "Attend Rate (30d) %",
  discipline_incidents_30d as "Incidents (30d)"
FROM main_main_analytics.v_chronic_absenteeism_risk
WHERE risk_classification IN ('Critical', 'High')
ORDER BY chronic_absenteeism_risk_score DESC
LIMIT 50
```

6. Click **Visualize**
7. Visualization is **Table** (default)
8. Enable columns you want to display (all above are good)
9. Click **Save**
10. Add to dashboard, size: full width (12 columns) × 6 rows

**Expected Result**: Table with 50 at-risk students, sortable columns

---

## Step 9: Build Tab 4 - Trends & Analysis (Table)

1. Go to **Trends & Analysis** tab
2. Click **+ Add → Question**
3. Select **DuckDB / OEA Analytics**
4. Click **Native query**
5. Paste this SQL:

```sql
SELECT 
  grade_level as "Grade",
  ROUND(AVG(attendance_rate_30d), 1) as "30d Average",
  ROUND(AVG(attendance_rate_60d), 1) as "60d Average",
  ROUND(AVG(attendance_rate_90d), 1) as "90d Average"
FROM main_main_analytics.v_chronic_absenteeism_risk
GROUP BY grade_level
ORDER BY grade_level
```

6. Click **Visualize**
7. Visualization: **Table**
8. Click **Save**
9. Add to dashboard, size: full width × 4 rows

**Expected Result**: Table showing attendance trends by grade

---

## Step 10: Connect Filters to Dashboard Cards

1. For each card on the dashboard:
   - Click **⚙ (card options)**
   - Select **Filter**
   - Connect filters:
     - School filter → `school_id` column
     - Grade filter → `grade_level` column
     - Risk filter → `chronic_absenteeism_risk_score` column
     - Date filter → date column in data

2. Test filters:
   - Select a specific school
   - Select a grade level
   - Verify all cards update

**Expected Result**: Filters work and cards update dynamically

---

## Step 11: Customize Appearance

1. Click **Edit** on dashboard
2. Set refresh rate:
   - Click dashboard settings
   - Auto-refresh: Every 5 minutes
3. Customize colors:
   - For each number card, set color code
   - Overview cards should be red/orange for urgency
4. Resize cards as needed for better layout

**Expected Result**: Professional-looking dashboard with proper colors and layout

---

## Step 12: Save & Test

1. Click **Save** (top right)
2. Give dashboard a description
3. Click **Save changes**
4. Test functionality:
   - Refresh the page
   - Try applying filters
   - Verify performance (<2 seconds per query)

**Expected Result**: Dashboard is saved and functional

---

## SQL Queries Reference

All queries use tables in the `main_main_analytics` schema:

- `v_chronic_absenteeism_risk` (3,400 rows) - main analytics view
  - Columns: `student_key`, `grade_level`, `school_id`, `chronic_absenteeism_risk_score`, `risk_classification`, `chronic_absence_flag`, `attendance_rate_30d`, `attendance_rate_60d`, `attendance_rate_90d`, `attendance_trend_30d`, `discipline_incidents_30d`

---

## Troubleshooting

### Query returns no results
- Check table name spelling
- Verify schema is `main_main_analytics`
- Check column names against database

### Filters not working
- Ensure column name matches exactly
- Use lowercase column names in filter connections
- Test with simpler filter first

### Slow performance
- Check if queries have LIMIT clause
- Enable query caching
- Use aggregated tables instead of views if available

### Connection errors
- Verify DuckDB file path is correct
- Check database is properly synced
- Restart Metabase container if needed

---

## Next Steps

Once this dashboard is complete:
1. Build Wellbeing Risk dashboard (similar process)
2. Build Equity Outcomes dashboard
3. Build Class Effectiveness dashboard
4. Build Performance Correlations dashboard
5. Configure row-level security
6. Run performance tests
7. Deploy to Kubernetes

---

**Estimated Time**: 2-3 hours for this dashboard  
**Estimated Time for All 5**: 12-15 hours  
**Total Phase 2-3 Time**: 50-60 hours  

