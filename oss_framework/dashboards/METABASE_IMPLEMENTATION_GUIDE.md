# Metabase Dashboard Implementation Guide

**Phase 4: Dashboard Development & Deployment**  
**Last Updated**: January 26, 2026  
**Status**: Implementation Ready

---

## Overview

This guide provides step-by-step instructions for building and deploying 5 production-ready Metabase dashboards connecting to DuckDB analytics data warehouse. All dashboard definitions have been generated from templates and are ready for implementation.

---

## Dashboard Definitions

All 5 dashboards have been generated with specifications, queries, and visualizations:

### 1. Chronic Absenteeism Risk Dashboard
- **File**: `chronic_absenteeism_definition.json`
- **Target**: School Administrators, Counselors
- **Tabs**: 4 (Overview, Risk Distribution, At-Risk Students, Trends & Analysis)
- **Security**: Row-level by school_id

### 2. Wellbeing & Mental Health Risk Dashboard
- **File**: `wellbeing_risk_definition.json`
- **Target**: Counselors, Social Workers
- **Tabs**: 2 (Risk Dashboard, Support Resources)
- **Security**: Row-level by assigned_counselor_id

### 3. Equity Outcomes Analysis Dashboard
- **File**: `equity_outcomes_definition.json`
- **Target**: District Leadership, Equity Officers
- **Tabs**: 3 (Achievement Gap, Disparity Index, Intervention Effectiveness)
- **Security**: No row-level security (district-level)

### 4. Class Effectiveness & Teacher Quality Dashboard
- **File**: `class_effectiveness_definition.json`
- **Target**: Teachers, Instructional Coaches
- **Tabs**: 2 (My Classes, Peer Comparison)
- **Security**: Row-level by teacher_id

### 5. Performance Correlations & Interventions Dashboard
- **File**: `performance_correlations_definition.json`
- **Target**: Data Analysts, Researchers
- **Tabs**: 3 (Root Cause Analysis, Intervention Funnel, ROI Analysis)
- **Security**: No row-level security (analysis only)

---

## Technical Stack

```
Metabase (v0.48.0+)
    ↓ JDBC Connection
DuckDB Analytics Database
    ↓ Analytics Views
Stage 3 Mart (main_main_analytics schema)
    ↓ 500K+ student records
Student Data Warehouse
```

### Database Connection Details

**Connection Type**: DuckDB (file-based)  
**Host**: Local file system  
**Path**: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`  
**Schema**: `main_main_analytics`

**Analytics Views Available**:
- `v_chronic_absenteeism_risk` (3,400 rows)
- `v_wellbeing_risk_profiles` (3,400 rows)
- `v_equity_outcomes_by_demographics` (5 rows aggregated)
- `v_class_section_comparison` (300 rows)
- `v_performance_correlations` (3 rows)

**Aggregation Tables** (for performance):
- `agg_attendance_windows` (90,000 rows)
- `agg_discipline_windows` (4,000 rows)
- `fact_academic_performance` (400,000 rows)
- `fact_class_effectiveness` (300 rows)

---

## Implementation Steps

### Phase 1: Database Connection Setup (15 min)

#### Step 1.1: Access Metabase Admin Panel

```
URL: http://localhost:3001/admin
Username: admin@metabase.com
Password: metabasepassword
```

#### Step 1.2: Add DuckDB Connection

1. Go to **Settings → Admin Panel → Databases**
2. Click **+ New database**
3. Select **DuckDB** from the list
4. Configure:
   - **Name**: `DuckDB Analytics`
   - **Database file path**: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
   - **Auto run queries**: Enabled (for performance)
   - **Database caching**: 10 minutes
   - **Read-only**: Yes (recommended for production)

5. Click **Save**
6. Run **Sync database schema** to load tables and views

---

### Phase 2: Dashboard Creation (4-5 hours)

#### Step 2.1: Create Chronic Absenteeism Risk Dashboard

**Instructions**:

1. Go to **+ New → Dashboard**
   - **Name**: `Chronic Absenteeism Risk`
   - **Description**: `Real-time identification and monitoring of students at chronic absenteeism risk`

2. **Add filters** (dashboard level):
   - Filter 1: `School` (dropdown, connects to `school_id` column)
   - Filter 2: `Grade` (dropdown, connects to `grade_level` column)
   - Filter 3: `Risk Threshold` (slider, 0-100)
   - Filter 4: `Date Range` (date picker)

3. **Tab 1: Overview** (4 metric cards)

   **Card 1: Students at Risk**
   ```sql
   SELECT COUNT(*) as count 
   FROM main_main_analytics.v_chronic_absenteeism_risk 
   WHERE risk_classification IN ('Critical', 'High')
   ```
   - Visualization: **Number**
   - Color: **Red** (#E53935)
   - Format: Large font

   **Card 2: Chronic Absence Rate (%)**
   ```sql
   SELECT ROUND(AVG(CASE WHEN chronic_absence_flag = true THEN 100 ELSE 0 END), 1) as rate
   FROM main_main_analytics.v_chronic_absenteeism_risk
   ```
   - Visualization: **Gauge**
   - Min: 0, Max: 30
   - Green threshold: <15%, Yellow: 15-20%, Red: >20%

   **Card 3: Declining Attendance (30d)**
   ```sql
   SELECT COUNT(*) as count
   FROM main_main_analytics.v_chronic_absenteeism_risk
   WHERE attendance_trend_30d = 'declining' OR attendance_rate_30d < 85
   ```
   - Visualization: **Number**
   - Color: **Orange** (#FB8C00)

4. **Tab 2: Risk Distribution** (2 charts)

   **Card 1: Risk Score Distribution**
   ```sql
   SELECT 
       ROUND(chronic_absenteeism_risk_score * 10) / 10 as risk_score,
       COUNT(*) as student_count
   FROM main_main_analytics.v_chronic_absenteeism_risk
   GROUP BY ROUND(chronic_absenteeism_risk_score * 10) / 10
   ORDER BY risk_score
   ```
   - Visualization: **Bar Chart**
   - X-axis: Risk Score
   - Y-axis: Student Count

   **Card 2: Risk Classification Breakdown**
   ```sql
   SELECT 
       risk_classification,
       COUNT(*) as count
   FROM main_main_analytics.v_chronic_absenteeism_risk
   GROUP BY risk_classification
   ORDER BY risk_classification
   ```
   - Visualization: **Pie Chart**

5. **Tab 3: At-Risk Students** (1 table)

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
   - Visualization: **Table**
   - Enable: Click-through drills on Student ID
   - Sort by: Risk Score (descending)

6. **Tab 4: Trends & Analysis** (1 table)

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
   - Visualization: **Table**

7. **Configuration**:
   - **Refresh**: Every 5 minutes
   - **Cache**: 10 minutes
   - **Share**: Enable (for read-only access)

---

#### Step 2.2: Create Wellbeing & Mental Health Risk Dashboard

1. Create new dashboard: `Wellbeing & Mental Health Risk`
2. Add filters:
   - **School** (dropdown)
   - **Assigned Counselor** (dropdown, for RBAC)
   - **Risk Level** (checkboxes: Critical, High, Medium, Low)
   - **Date Range** (date picker)

3. **Tab 1: Risk Dashboard** (6 cards)

   **Cards 1-4: Metric Cards**
   - High Risk Count: `SELECT COUNT(*) FROM ... WHERE overall_risk_level = 'High'`
   - Medium Risk Count: `SELECT COUNT(*) FROM ... WHERE overall_risk_level = 'Medium'`
   - Active Cases: `SELECT COUNT(*) FROM ... WHERE has_active_case_plan = true`
   - Follow-ups Due: `SELECT COUNT(*) FROM ... WHERE days_since_last_contact > 14 AND has_active_case_plan = true`

   **Card 5: Risk Domain Breakdown** (Bar chart)
   - Shows: Academic, Behavioral, Social-Emotional, Family Engagement risks

   **Card 6: My Caseload** (Pie chart)
   - Breakdown by risk level

4. **Tab 2: Support Resources** (1 table)

   Resource allocation metrics by risk level

---

#### Step 2.3: Create Equity Outcomes Analysis Dashboard

1. Create new dashboard: `Equity Outcomes Analysis`
2. Add filters:
   - **Demographic Category** (dropdown)
   - **Year** (dropdown)
   - **School** (dropdown)

3. **Tab 1: Achievement Gap Analysis** (1 large table)
   - Shows: Demographic groups, graduation rates, performance gaps

4. **Tab 2: Disparity Index** (2 charts)
   - Performance Gap Index by demographic
   - Graduation Rate by Race/Ethnicity

5. **Tab 3: Intervention Effectiveness** (1 table)
   - Intervention ROI by demographic group

---

#### Step 2.4: Create Class Effectiveness Dashboard

1. Create new dashboard: `Class Effectiveness & Teacher Quality`
2. Add filters:
   - **School** (dropdown)
   - **Subject** (dropdown)
   - **Grade** (dropdown)

3. **Tab 1: My Classes** (1 table)
   - Performance metrics vs peer average

4. **Tab 2: Peer Comparison** (2 charts)
   - Top 10 performing classes (bar)
   - Student growth trajectory distribution

---

#### Step 2.5: Create Performance Correlations Dashboard

1. Create new dashboard: `Performance Correlations & Interventions`
2. No special filters required (analysis dashboard)

3. **Tab 1: Root Cause Analysis** (1 table)
   - Key correlations with statistical significance

4. **Tab 2: Intervention Funnel** (2 charts)
   - Intervention status distribution (pie)
   - Completion rate by type (bar)

5. **Tab 3: ROI Analysis** (1 table)
   - Intervention effectiveness metrics

---

### Phase 3: Row-Level Security (RBAC) Configuration (1-2 hours)

#### Step 3.1: Create User Groups

1. Go to **Settings → Admin Panel → People → Groups**
2. Create groups:
   - `Administrators` (all data access)
   - `School Administrators` (filtered by school)
   - `Counselors` (filtered by assigned counselor)
   - `Teachers` (filtered by teacher ID)
   - `District Leadership` (full access)
   - `Analysts` (full access)

#### Step 3.2: Configure Dashboard-Level Permissions

For each dashboard with RBAC:

1. Open dashboard
2. Click **Sharing & Embedding**
3. Set permissions by group:
   - `Administrators`: Full access
   - `School Administrators`: Can view, can't edit
   - `Counselors`: Can view (filtered data), can't edit
   - `Teachers`: Can view (own classes only), can't edit
   - Others: No access

#### Step 3.3: Configure Row-Level Security

For **Chronic Absenteeism Risk** dashboard:

1. Settings → Databases → DuckDB Analytics
2. Click on `v_chronic_absenteeism_risk` table
3. **Row-Level Security**:
   - **Column**: `school_id`
   - **Group**: `School Administrators`
   - **Value mapping**: Map user to school ID
   - Apply to `School Administrators` group

4. Set filter for `School Administrators` group:
   - `school_id` = `{{current_user.school_id}}`

#### Step 3.4: User-Specific Data Access

For **Wellbeing & Mental Health Risk** dashboard:

1. Configure RLS for `assigned_counselor_id` column
2. Map counselor users to their ID
3. Filter: `assigned_counselor_id` = `{{current_user.id}}`

For **Class Effectiveness** dashboard:

1. Configure RLS for `teacher_id` column
2. Map teacher users to their ID
3. Filter: `teacher_id` = `{{current_user.id}}`

---

### Phase 4: Performance Testing & Optimization (1-2 hours)

#### Step 4.1: Test Dashboard Load Times

For each dashboard:

1. Open dashboard in Chrome DevTools (F12 → Network tab)
2. Clear cache and reload
3. Measure:
   - Dashboard load time (target: <2 seconds)
   - Individual card query time (target: <1 second)
   - Total time to interaction (target: <3 seconds)

#### Step 4.2: Performance Optimization

If queries are slow:

1. **Add database indexes** (DuckDB):
   ```sql
   CREATE INDEX idx_chronic_school ON main_main_analytics.v_chronic_absenteeism_risk(school_id);
   CREATE INDEX idx_chronic_risk ON main_main_analytics.v_chronic_absenteeism_risk(risk_classification);
   CREATE INDEX idx_wellbeing_counselor ON main_main_analytics.v_wellbeing_risk_profiles(assigned_counselor_id);
   ```

2. **Enable Metabase query caching**:
   - Dashboard cache: 10 minutes
   - Query cache: 1 minute (for frequent queries)

3. **Use materialized views** instead of regular views:
   - Create `agg_chronic_absenteeism` from `v_chronic_absenteeism_risk`
   - Update query to use aggregation table

4. **Analyze slow queries**:
   - Open query in Metabase editor
   - Click "Explain" to see query plan
   - Look for missing indexes or inefficient joins

#### Step 4.3: Load Testing

Use Apache JMeter or similar to test:

1. 10 concurrent users
2. Each dashboard loaded 5 times
3. All cards load simultaneously
4. Record response times and error rates

Target:
- p95 response time: <2 seconds
- p99 response time: <3 seconds
- Error rate: <0.1%

---

## Configuration Files

### Dashboard Definition Format

Each dashboard has a JSON definition file:

```json
{
  "name": "Chronic Absenteeism Risk",
  "description": "...",
  "type": "chronic_absenteeism",
  "target_audience": ["School Administrators", "Counselors"],
  "refresh_interval_minutes": 5,
  "row_level_security": true,
  "rbac_column": "school_id",
  "tabs": [
    {
      "name": "Overview",
      "cards": [
        {
          "position": [0, 0],
          "size": [4, 2],
          "title": "Students at Risk",
          "query": "SELECT ...",
          "visualization_type": "number",
          "settings": {
            "color": "#E53935",
            "fontSize": 32
          }
        }
      ]
    }
  ]
}
```

---

## Metabase Configuration Details

### Database Connection

**Name**: DuckDB Analytics  
**Type**: DuckDB  
**Path**: Local file path to oea.duckdb  
**Options**:
- Auto run queries: ✓ Enabled
- Database caching: 10 minutes
- Read-only: ✓ Yes
- Timezone: UTC

### Dashboard Settings

```yaml
Refresh Interval: 5 minutes
Cache TTL: 10 minutes
Caching Strategy: All results
Auto-refresh: Enabled
Sharing: Public (read-only) for authorized groups
Embedding: Enabled for secure embedding
```

### Query Optimization

```
Materialized View: agg_* tables (for large queries)
Index Strategy: Create indexes on filter columns
Cache Strategy: 10-min dashboard, 1-min query cache
Maximum result rows: 50,000 (for performance)
```

---

## Validation Checklist

- [ ] DuckDB database connected and synced
- [ ] 5 dashboards created with all tabs
- [ ] All queries return correct data
- [ ] Filters work correctly (school, grade, date, etc.)
- [ ] Dashboard load time < 2 seconds (p95)
- [ ] Individual card queries < 1 second
- [ ] Row-level security configured for RBAC dashboards
- [ ] User access controls tested for each role
- [ ] Cache settings configured (10 min dashboard, 1 min query)
- [ ] All visualizations render correctly
- [ ] Data drill-down/click-through works on tables
- [ ] Export functionality tested (CSV, PDF)
- [ ] Mobile responsiveness verified

---

## Troubleshooting

### Dashboard Not Loading

**Problem**: Dashboard shows loading spinner indefinitely  
**Solution**:
1. Check DuckDB connection in admin panel
2. Verify database file path is correct
3. Check database file permissions
4. Run "Sync database schema" again
5. Check Metabase logs for errors

### Slow Query Performance

**Problem**: Dashboard cards take >2 seconds to load  
**Solution**:
1. Add indexes on filter columns (school_id, grade_level, etc.)
2. Enable query result caching (1 minute)
3. Use materialized views instead of regular views
4. Limit result rows with TOP/LIMIT clause
5. Check for missing indexes: `PRAGMA query_plan_only`

### Row-Level Security Not Working

**Problem**: Users see all data despite RLS configuration  
**Solution**:
1. Verify user group assignment
2. Check RLS column mapping
3. Verify user attribute exists and is correct
4. Test filter with hardcoded value first
5. Check Metabase logs for permission errors

### Data Not Refreshing

**Problem**: Dashboard shows stale data  
**Solution**:
1. Check dbt refresh schedule (2 AM UTC daily)
2. Verify dbt job completed successfully
3. Clear Metabase cache manually: **Settings → Caching → Clear entire cache**
4. Force dashboard refresh (Ctrl+Shift+R)
5. Check database for data freshness: `SELECT MAX(updated_at) FROM ...`

---

## Next Steps

1. **Implement dashboards** following Phase 2 above (4-5 hours)
2. **Test row-level security** with sample users (1-2 hours)
3. **Conduct performance testing** against target metrics (1-2 hours)
4. **Deploy to production** Kubernetes cluster (Week 7)
5. **Execute UAT** with stakeholders (Days 7-10)
6. **Train users** on dashboard usage (Week 8)

---

## Support & Documentation

- **Metabase Docs**: https://www.metabase.com/docs/
- **DuckDB Integration**: https://duckdb.org/
- **Dashboard Examples**: See METABASE_TEMPLATES.md
- **UAT Plan**: See UAT_PLAN.md
- **Training Materials**: See STAFF_TRAINING.md

---

**Dashboard Implementation Status**: READY  
**Target Completion**: Week 6 (4-5 days of development)  
**Production Deployment**: Week 7  
**UAT Window**: Days 7-10  
**Go-Live**: Week 8
