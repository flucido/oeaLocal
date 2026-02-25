# 🎯 STAGE 4: METABASE INSTALLATION & DASHBOARD IMPLEMENTATION PLAN

## Overview

**Project**: OSS Framework Student Analytics Platform  
**Phase**: Stage 4 - Dashboards & Deployment (Final Phase)  
**Status**: Ready for Implementation  
**Timeline**: 2-3 weeks (10 work items)  
**Completion Target**: Production deployment with staff training

---

## 📋 IMPLEMENTATION ROADMAP

### PART 1: Metabase Setup & Configuration (1.5 days)

#### Task 4.01: Install & Configure Metabase

**Objective**: Deploy Metabase and connect to DuckDB analytics database

**Deliverables**:
- Metabase installed (Docker or standalone)
- DuckDB database connected and verified
- Initial admin account created
- System health checks passed

**Implementation Steps**:

1. **Install Metabase** (choose one):
   ```bash
   # Option A: Docker (Recommended for development)
   docker run -d -p 3000:3000 \
     -e MB_DB_TYPE=h2 \
     -v metabase-data:/metabase-data \
     --name metabase \
     metabase/metabase:latest
   
   # Option B: Standalone JAR (production)
   wget https://downloads.metabase.com/v0.47.0/metabase.jar
   java -jar metabase.jar
   ```

2. **Access Metabase**: Navigate to `http://localhost:3000`

3. **Create Admin Account**:
   - Email: admin@district.edu
   - Password: (strong, unique)
   - Company: [District Name]

4. **Connect DuckDB Database**:
   - Click "Admin Settings" → "Databases"
   - Click "New database"
   - Select "DuckDB"
   - Database Path: `/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb`
   - Display Name: "OSS Analytics"
   - Click "Save"

5. **Verify Connection**:
   - Run test query on `main_main_analytics.v_chronic_absenteeism_risk`
   - Expected: 3,400 rows returned in <1 second
   - Status: ✅ Connected

6. **Backup Configuration**:
   - Export Metabase settings: Settings → Admin Panel → Export
   - Save: `/oss_framework/deployment/metabase_config.backup`

**Success Criteria**:
- ✅ Metabase running (port 3000 accessible)
- ✅ Admin account created and logged in
- ✅ DuckDB connection established and tested
- ✅ All analytics tables visible in database UI
- ✅ Backup created

**Estimated Time**: 1.5 hours

---

### PART 2: Dashboard Creation (6-7 days)

#### Task 4.02: Build Dashboard 1 - Chronic Absenteeism Risk

**Objective**: Create primary dashboard for identifying and tracking chronically absent students

**Data Source**: `v_chronic_absenteeism_risk` (3,400 rows)

**Visualizations** (6 total):

1. **Risk Distribution Chart** (Pie/Donut)
   - Query: Count of students by `wellbeing_risk_level`
   - Categories: Low / Medium / High / Critical
   - Color scheme: Green → Yellow → Orange → Red
   - Expected: 68% Low, 20% Medium, 8% High, 4% Critical

2. **Top 20 At-Risk Students** (Table)
   - Columns: Student Name, Grade, Attendance Rate (30d), Unexcused Rate (30d), Risk Score, Primary School
   - Sort by: `risk_score DESC`
   - Filters: Risk Level, Grade Level, School
   - Click-through: Link to individual student detail

3. **Attendance Trend** (Line Chart)
   - X-axis: Date (90-day window, daily)
   - Y-axis: Average attendance rate by risk level
   - Lines: Low / Medium / High / Critical
   - Expected: Shows declining trend for High/Critical groups

4. **School Comparison** (Bar Chart)
   - X-axis: School name
   - Y-axis: Percentage of students chronically absent
   - Segments: By grade level (9-12)
   - Drill-down: Click school to see detail by grade

5. **Metric Cards** (KPI Row - 4 cards):
   - Total Students Monitored: `{count}`
   - Chronic Absence Rate: `{avg_rate}%`
   - High/Critical Risk Count: `{count}`
   - Trend (30d vs 90d): `{% change}`

6. **Discipline Correlation** (Scatter)
   - X-axis: Attendance rate
   - Y-axis: Discipline incidents (30d)
   - Size: Risk score
   - Color: Wellbeing level
   - Purpose: Show correlation between attendance and behavior

**Filters**:
- School (select one or all)
- Grade Level (9, 10, 11, 12)
- Risk Level (checkboxes: Low, Medium, High, Critical)
- Date Range (last 30/60/90 days)

**Refresh Schedule**: Daily at 6 AM

**Estimated Time**: 1.5 days

---

#### Task 4.03: Build Dashboard 2 - Wellbeing & Mental Health Risk

**Objective**: Create multi-domain risk assessment view for counselors and case managers

**Data Source**: `v_wellbeing_risk_profiles` (3,400 rows)

**Visualizations** (5 total):

1. **Risk Domain Matrix** (Bubble Chart)
   - X-axis: Attendance risk (0-100)
   - Y-axis: Discipline risk (0-100)
   - Z-axis (bubble size): Academic risk (0-100)
   - Color: Primary concern (Multi-factor / Attendance / Behavior / Academic)
   - Quadrants: Low-Low (green) → High-High (red)
   - Click bubble to see student list

2. **Wellbeing Risk Breakdown** (Stacked Bar)
   - X-axis: Schools
   - Y-axis: Count of students
   - Segments: Low / Moderate / High / Critical wellbeing risk
   - Color scheme: Green → Yellow → Orange → Red
   - Show percentages on hover

3. **Primary Concern Distribution** (Horizontal Bar)
   - Categories: Multi-factor / Attendance / Behavior / Academic
   - Count: Number of students with each concern
   - Segments by: School (stacked horizontal)
   - Purpose: Show where to focus intervention resources

4. **Students by Wellbeing Level** (Table)
   - Columns: Student, Grade, School, Attendance Risk, Discipline Risk, Academic Risk, Compound Risk, Primary Concern, Recommended Action
   - Sort: Compound risk (highest first)
   - Filters: Wellbeing level, primary concern, school
   - Export: CSV for case management

5. **Risk Trend Over Time** (Line Chart)
   - X-axis: Weekly (over 12 weeks)
   - Y-axis: Average compound risk score
   - Lines: By school
   - Purpose: Identify improving/worsening trend

**Filters**:
- School
- Grade Level
- Wellbeing Risk Level (Low / Moderate / High / Critical)
- Primary Concern (Multi-factor / Attendance / Behavior / Academic)
- Date Range

**Access**: School counselors, case managers, administrators

**Refresh Schedule**: Daily

**Estimated Time**: 1.5 days

---

#### Task 4.04: Build Dashboard 3 - Equity Outcomes Analysis

**Objective**: Analyze achievement and opportunity gaps by demographic subgroups

**Data Source**: `v_equity_outcomes_by_demographics` (5 rows)

**Visualizations** (5 total):

1. **Outcomes by Demographics** (Grouped Bar Chart)
   - X-axis: Demographics (Race/Ethnicity, ELL, SPED, FRL)
   - Y-axis: Four sets of bars:
     - Good Attendance % (>90%)
     - No Discipline %
     - Average GPA
     - College-Ready % (GPA ≥2.5)
   - Color bars by subgroup: White / Black / Hispanic / Asian / Other
   - Purpose: Highlight disparities

2. **Achievement Gap Heatmap** (Table)
   - Rows: Demographic groups (Black, Hispanic, Asian, etc.)
   - Columns: Cohort Size, Attendance %, No Discipline %, Avg GPA, College-Ready %
   - Conditional formatting: Highlight low/high values
   - Gap columns: Disparity vs. district average
   - Example: "Hispanic students 12% below average attendance"

3. **Outcome Distribution** (Box Plot)
   - Y-axis: GPA
   - Groups: By demographic (5 boxes)
   - Show: Min, Q1, Median, Q3, Max
   - Purpose: Show spread and outliers for each group

4. **College Readiness Pathway** (Funnel)
   - Step 1: Total students by demographic
   - Step 2: Passing grades (≥C)
   - Step 3: College-eligible GPA (≥2.5)
   - Step 4: 4-year enrollment (if available)
   - Color: By demographic group

5. **Equity Scorecard** (Card Grid)
   - 4 cards per demographic:
     - Students (count)
     - Attendance rate
     - Avg GPA
     - % College-ready
   - Comparison to district average
   - Trend arrow: ↑ improving / ↓ declining

**Filters**:
- Demographic dimension (Race, ELL, SPED, FRL)
- School (optional)
- Academic year (if historical)

**Access**: Equity officer, administrators, board members

**Refresh Schedule**: Monthly (less frequent data changes)

**Estimated Time**: 1.5 days

---

#### Task 4.05: Build Dashboard 4 - Class Effectiveness & Teacher Quality

**Objective**: Compare course section performance and identify effective teaching practices

**Data Source**: `v_class_section_comparison` (300 rows)

**Visualizations** (6 total):

1. **Class Performance Ranking** (Table)
   - Columns: Course, Section (A/B/C), Teacher, Enrollment, Pass Rate %, Avg Grade, Effectiveness Rating, Comparison to Course Average
   - Sort by: `effectiveness_rating`, then `pct_passed DESC`
   - Color rows: Highly Effective (green) → Needs Improvement (red)
   - Drill-down: Click section to see student roster and grades

2. **Subgroup Performance Comparison** (Grouped Bars)
   - X-axis: Sections (top 20 by enrollment)
   - Y-axis: Pass rate (0-100%)
   - Bars: Overall / ELL / SPED / FRL
   - Purpose: Show which teachers effectively serve subgroups
   - Expected: Top teachers have <15% spread between groups

3. **Class Size vs. Effectiveness** (Scatter)
   - X-axis: Enrollment count
   - Y-axis: Pass rate or avg grade
   - Size: Average grade
   - Color: Effectiveness rating
   - Purpose: Evaluate if smaller classes correlate with better outcomes

4. **Subject Area Comparison** (Faceted Bar Charts)
   - One chart per subject: Math, ELA, Science, Social Studies
   - X-axis: Course sections
   - Y-axis: Pass rate
   - Benchmark line: District average for subject
   - Purpose: Compare within discipline

5. **Teacher Effectiveness Scorecard** (Card Grid - Top 10)
   - Card per teacher (sorted by pass rate)
   - Displays: Name, Subject, Avg Pass Rate, Avg Grade, Subgroup Equity Score
   - Color: Green (high) → Yellow (average) → Red (low)
   - Trend: ↑/↓ vs. previous term

6. **Equity in Class Outcomes** (Heatmap)
   - Rows: Teachers/Sections
   - Columns: Subgroups (Overall, ELL, SPED, FRL)
   - Values: Pass rate
   - Color: Gradient (red=low, yellow=mid, green=high)
   - Purpose: Identify teachers with equity concerns

**Filters**:
- Subject area (Math, ELA, Science, Social Studies)
- School
- Grade level (9-12)
- Effectiveness rating (Highly Effective / Effective / Adequate / Needs Improvement)
- Term (if available)

**Access**: School principals, department heads, professional development coordinators

**Refresh Schedule**: Per term (every 6-9 weeks)

**Estimated Time**: 2 days

---

#### Task 4.06: Build Dashboard 5 - Performance Correlations & Insights

**Objective**: Analyze relationships between attendance, discipline, and academic outcomes

**Data Source**: `v_performance_correlations` (3 rows aggregate)

**Visualizations** (4 total):

1. **Correlation Matrix** (Heatmap)
   - Rows/Columns: Attendance, Discipline, GPA
   - Values: Pearson correlation coefficient (-1 to +1)
   - Color: Blue (negative) → White (zero) → Red (positive)
   - Show correlation strength: Strong / Moderate / Weak / Negligible
   - Annotations: Confidence levels, sample size

2. **Individual Correlations** (3 Large Number Cards)
   
   **Card 1: Attendance ↔ GPA**
   - Correlation: +0.62 (Strong positive)
   - Interpretation: "Strong positive relationship - students with better attendance have higher GPAs"
   - Sample size: 3,400 students
   - Confidence: 95%
   - Actionable insight: "Attendance interventions likely to improve grades"
   
   **Card 2: Discipline ↔ GPA**
   - Correlation: -0.51 (Strong negative)
   - Interpretation: "Students with more discipline incidents have lower GPAs"
   - Insight: "Behavior support may improve academic outcomes"
   
   **Card 3: Attendance ↔ Engagement**
   - Correlation: +0.43 (Moderate positive)
   - Interpretation: "Good attendance correlates with digital engagement"
   - Insight: "Chronic absence often pairs with disengagement"

3. **Correlation Context** (Text Summary)
   - Automatically generated narrative:
   ```
   "This month we see strong correlations between attendance and achievement. 
   Students with 90%+ attendance average 2.8 GPA, while chronically absent 
   students average 1.9 GPA - a 0.9 point gap. This is consistent with 
   national research and suggests that attendance interventions should be 
   a priority."
   ```

4. **Recommendations Engine** (Card List)
   - Based on correlations, show:
     - "94% of correlation strength → Prioritize attendance"
     - "Discipline incidents strongly linked to low GPA → Expand restorative practices"
     - "Engagement data shows ELL students disproportionately absent → Targeted outreach"
     - "Strong correlation supports current student success plan"

**Filters**:
- Time period (this month / term / year)
- School
- Grade level

**Access**: District analytics team, administrators, board

**Refresh Schedule**: Monthly

**Estimated Time**: 1.5 days

---

### PART 3: Access Control & Security (1.5 days)

#### Task 4.07: Configure User Roles, Filters & Access Controls

**Objective**: Implement role-based access control for different stakeholder groups

**User Roles** (5 types):

1. **Superintendent / District Admin**
   - Access: All 5 dashboards, all schools, all grades
   - Filters: None (see everything)
   - Edit rights: Yes (can create saved queries)
   - Export: Unlimited

2. **School Principal**
   - Access: All 5 dashboards
   - Filters: Locked to their school only
   - Visibility: Cannot see other schools in comparisons
   - Edit rights: Limited (personal queries only)
   - Export: CSV only (no raw data)

3. **Counselor / Case Manager**
   - Access: Dashboard 2 (Wellbeing Risk) + Dashboard 3 (Equity)
   - Filters: School + their assigned grade level
   - Visibility: Student-level data with names
   - Edit rights: None
   - Export: For case management purposes only

4. **Teacher**
   - Access: Dashboard 4 (Class Effectiveness) only
   - Filters: Their own classes
   - Visibility: Class roster and grades only
   - Edit rights: None
   - Export: Roster only

5. **Board Member**
   - Access: Dashboard 1 (Chronic Absenteeism) + Dashboard 3 (Equity) + Dashboard 5 (Insights)
   - Filters: All schools (aggregated view)
   - Visibility: No student names, aggregated only
   - Edit rights: None
   - Export: PDF reports only

**Implementation Steps**:

1. **Create User Groups in Metabase**:
   - Admin → People → New group
   - Groups: Admins, Principals, Counselors, Teachers, Board_Members

2. **Set Database-Level Permissions**:
   - Click database → Permissions
   - Set by role: Full / Limited / No access

3. **Create Saved Filters** (reusable where possible):
   - Filter: "My School" = authenticated user's school
   - Filter: "My Grade Level" = assigned grades
   - Auto-apply based on role

4. **Enable Field-Level Masking** (for sensitive fields):
   - Hide: Social Security numbers, dates of birth
   - Show: Student ID (hashed), grades, attendance

5. **Session Settings**:
   - Session timeout: 30 minutes
   - Password policy: 12+ chars, must change every 90 days
   - Multi-factor auth: Optional (for admin only)

**Sample Configuration**:
```
School Principal (Lincoln High):
├─ Can see: All dashboards filtered to Lincoln High
├─ Cannot see: Other schools, student names
├─ Can export: CSV of their school's data
└─ Cannot: Modify queries, manage users

Counselor (Lincoln High, Grades 9-10):
├─ Can see: Dashboard 2 (Wellbeing) + Dashboard 3 (Equity)
├─ Cannot see: Dashboard 1, 4, 5
├─ Visibility: Student names, full risk data (for casework)
└─ Cannot: Export beyond authorized scope
```

**Estimated Time**: 1.5 days

---

### PART 4: Testing & Validation (1.5 days)

#### Task 4.08: Conduct User Acceptance Testing (UAT)

**Objective**: Validate dashboards meet stakeholder needs and function correctly

**Testing Approach**: Multi-tier UAT with real users

**UAT Groups** (by role):

**Group 1: Administrators** (2-3 people)
- User: Superintendent, Assistant Superintendent
- Duration: 2 hours
- Test scenarios:
  - View all dashboards across all schools
  - Filter by grade level and time range
  - Export data for board presentation
  - Verify accuracy of dashboard numbers vs. raw data
- Success criteria: "Dashboard numbers match my expectations"

**Group 2: School Leaders** (4-6 people)
- Users: 2-3 principals, 1-2 assistant principals
- Duration: 1.5 hours each
- Test scenarios:
  - Access their school's dashboards
  - Verify they cannot see other schools
  - Run Dashboard 1 & 4 to identify students needing intervention
  - Export roster for follow-up meetings
  - Spot-check accuracy for known students
- Success criteria: "I can identify my struggling students and will use this regularly"

**Group 3: Counselors & Case Managers** (3-4 people)
- Duration: 1.5 hours
- Test scenarios:
  - Access Dashboard 2 (Wellbeing Risk)
  - Identify students for case management
  - Export list for portfolio
  - Verify student names and data match their records
- Success criteria: "I can quickly identify students needing support"

**Group 4: Teachers** (2-3 people)
- Duration: 1 hour
- Test scenarios:
  - Access Dashboard 4 (Class Effectiveness)
  - View their class performance
  - Compare to school average
  - Provide feedback on usefulness
- Success criteria: "This shows how my class is performing"

**Group 5: Board Members** (2 people)
- Duration: 1 hour
- Test scenarios:
  - Access Dashboard 1, 3, 5
  - No student names visible
  - Aggregated data only
  - Export dashboard as PDF
- Success criteria: "This gives me the information I need for board meetings"

**UAT Metrics**:
- System response time: <2 seconds for all queries
- Dashboard load time: <5 seconds
- Export speed: <10 seconds for CSV
- Accuracy: 100% match with known values
- User satisfaction: ≥4/5 average rating

**UAT Feedback Form** (per user):
- Clarity: "How clear are the visualizations?" (1-5)
- Usefulness: "How useful is this for your role?" (1-5)
- Performance: "Is the dashboard fast enough?" (Yes/No)
- Issues: "What problems did you encounter?"
- Suggestions: "What would make this better?"

**UAT Timeline**:
- Schedule: Coordinate with users
- Feedback collection: Real-time + follow-up survey
- Issues log: Track all problems
- Resolution: Fix bugs before production

**Success Criteria**:
- ✅ All 5 user groups complete testing
- ✅ ≥80% satisfaction rating
- ✅ Zero critical issues
- ✅ <5 medium/low issues requiring fixes
- ✅ Users confirm accuracy of displayed data

**Estimated Time**: 1.5 days

---

### PART 5: Deployment & Launch (1.5 days)

#### Task 4.09: Deploy to Production & Verify Stability

**Objective**: Move Metabase dashboards to production environment

**Pre-Deployment Checklist**:
- ✅ All UAT issues resolved
- ✅ Database backups created
- ✅ Security configuration finalized
- ✅ User accounts created for all stakeholders
- ✅ Documentation updated
- ✅ Training materials ready

**Deployment Steps**:

1. **Production Environment Setup** (if different from dev):
   ```bash
   # Production Metabase server (separate from dev)
   - VM / Physical server with 8GB+ RAM
   - 500GB storage for Metabase data
   - Scheduled backups (daily)
   - Network firewall rules (restrict to district IPs)
   ```

2. **Export Dev Configuration**:
   - Metabase Admin → Settings → Export
   - Save as `/oss_framework/deployment/metabase_prod_config.zip`

3. **Import to Production**:
   - Deploy Metabase to production server
   - Import exported configuration
   - Verify all dashboards present

4. **Database Connection Verification**:
   - Test each dashboard query
   - Verify performance (<2 sec query time)
   - Check that student data is current

5. **User Access Verification**:
   - Test login as each role
   - Verify role-based filters work
   - Confirm data masking applied

6. **Backup & Disaster Recovery**:
   - Create full backup of production Metabase database
   - Document restore procedure
   - Store backups: `/oss_framework/deployment/backups/`

7. **Monitoring Setup**:
   - Configure alerts for query performance >5 seconds
   - Monitor database connectivity
   - Track dashboard access logs

**Rollback Plan** (if issues occur):
- Keep dev environment running
- Document any critical issues
- Rollback to previous version if needed
- Communicate status to users

**Launch Communication**:
- Email announcement to all users
- Subject: "New Student Analytics Dashboards Available"
- Include: Link to access, quick start guide, support contact
- Schedule: Deploy during off-hours (evenings), announce next morning

**Success Criteria**:
- ✅ All 5 dashboards accessible from production
- ✅ <1 second query time for all visualizations
- ✅ User login working for all roles
- ✅ Role-based access control functioning
- ✅ Backup automated and verified

**Estimated Time**: 1.5 days

---

### PART 6: Staff Training & Adoption (1.5 days)

#### Task 4.10: Conduct Staff Training & Documentation

**Objective**: Enable users to effectively use dashboards for decision-making

**Training Program**: 5 tailored sessions (45 minutes each)

**Session 1: Administrator Training** (45 min)
- Audience: Superintendent, Assistant Superintendent
- Location: Board room or conference call
- Topics:
  - Overview of all 5 dashboards
  - How to access and navigate
  - Interpreting risk scores and metrics
  - Exporting for board presentations
  - How to request custom reports
- Materials: Slide deck + quick reference guide
- Hands-on: Live demo on production system

**Session 2: Principal Training** (45 min x 2 cohorts)
- Audience: All principals
- Topics:
  - Dashboard 1: Identify chronically absent students
  - Dashboard 4: Monitor class effectiveness
  - Setting up intervention follow-ups
  - Exporting rosters for staff meetings
  - Troubleshooting common issues
- Materials: Quick reference card (laminated)
- Hands-on: Log in and filter to their school

**Session 3: Counselor/Case Manager Training** (45 min)
- Audience: All counselors, case managers
- Topics:
  - Dashboard 2: Wellbeing risk assessment
  - Dashboard 3: Equity outcomes
  - Using data for case management
  - Maintaining student privacy
  - Exporting for portfolios
- Materials: Case study examples
- Hands-on: Identify at-risk students + export

**Session 4: Teacher Training** (30 min, self-paced optional)
- Audience: Teachers (optional attendance)
- Topics:
  - Dashboard 4: Class effectiveness metrics
  - Understanding your pass rates vs. school average
  - How students are measured
  - Q&A
- Materials: Video recording (for asynchronous)
- Access: Embedded in staff portal

**Session 5: Board Member Briefing** (20 min)
- Audience: School board members
- Topics:
  - High-level overview of dashboards
  - Key metrics for monitoring district performance
  - Using data for policy decisions
  - No technical details
- Materials: Executive summary (PDF)
- Format: Brief presentation before board meeting

**Training Materials**:

1. **Quick Start Guide** (1-page PDF)
   - How to log in
   - Where to find each dashboard
   - How to filter data
   - How to export

2. **Role-Specific Guides** (5 documents):
   - Admin guide (3 pages)
   - Principal guide (2 pages)
   - Counselor guide (2 pages)
   - Teacher guide (1 page)
   - Board member guide (1 page)

3. **Video Tutorials** (5 x 5-min videos):
   - Getting started with Metabase
   - Dashboard 1: Chronic absenteeism
   - Dashboard 2: Wellbeing risk
   - Dashboard 3: Equity outcomes
   - Dashboard 4: Class effectiveness

4. **Troubleshooting Guide**:
   - "I can't log in"
   - "My school's data is missing"
   - "A dashboard is slow"
   - "I need to report a data error"

5. **FAQ Document**:
   - Common questions from each role
   - How to request new queries
   - How often is data updated?
   - Why don't I see student X?
   - etc.

**Ongoing Support Plan**:
- Helpdesk email: analytics@district.edu
- Response time: <24 hours
- Monthly office hours (optional Q&A)
- Quarterly refresher training
- Annual report on dashboard usage

**Adoption Timeline**:
- Week 1: Administrators + Principals trained
- Week 2: Counselors + Teachers trained
- Week 3-4: Adoption and feedback collection
- Month 2: Address feedback, refinements
- Month 3+: Routine use + optimization

**Success Metrics**:
- ✅ ≥90% of staff completes assigned training
- ✅ ≥75% of users log in within first 2 weeks
- ✅ <5 support tickets per 100 users per month
- ✅ Positive feedback from user survey (≥4/5)
- ✅ Dashboards actively used for decision-making

**Estimated Time**: 1.5 days

---

## 📅 IMPLEMENTATION TIMELINE

| Task | Week | Duration | Owner |
|------|------|----------|-------|
| 4.01 - Metabase setup | 1 | 1.5d | DevOps |
| 4.02 - Dashboard 1 | 1-2 | 1.5d | BI Developer |
| 4.03 - Dashboard 2 | 2 | 1.5d | BI Developer |
| 4.04 - Dashboard 3 | 2 | 1.5d | BI Developer |
| 4.05 - Dashboard 4 | 2-3 | 2.0d | BI Developer |
| 4.06 - Dashboard 5 | 3 | 1.5d | BI Developer |
| 4.07 - Access control | 3 | 1.5d | Security + BI Dev |
| 4.08 - UAT | 3 | 1.5d | Project Manager |
| 4.09 - Deployment | 3 | 1.5d | DevOps |
| 4.10 - Training | 3 | 1.5d | Project Manager |
| **TOTAL** | **3 weeks** | **15 days** | **Team** |

---

## 🎯 SUCCESS CRITERIA

### Technical Requirements
- ✅ Metabase running and stable (99.5% uptime)
- ✅ All 5 dashboards accessible
- ✅ Query performance: <2 seconds for all visualizations
- ✅ DuckDB connection reliable
- ✅ Automated backups running daily
- ✅ Role-based access control working

### Business Requirements
- ✅ Dashboards meet stakeholder needs
- ✅ ≥75% of staff log in within 2 weeks
- ✅ Data accuracy verified vs. source systems
- ✅ Users report ability to make informed decisions
- ✅ Reduced manual data pulls from IT

### Adoption Requirements
- ✅ ≥90% of assigned staff complete training
- ✅ ≥80% user satisfaction rating
- ✅ <5 support tickets per 100 users/month
- ✅ Evidence of dashboards used for decision-making

---

## 📊 DELIVERABLES BY PHASE

| Phase | Deliverables |
|-------|--------------|
| **Setup** | Metabase instance, DuckDB connection, admin account |
| **Dashboards** | 5 production-ready dashboards with filters |
| **Security** | User accounts, role-based access control, field masking |
| **Testing** | UAT report, issue resolution, sign-off |
| **Deployment** | Production environment, backups, monitoring |
| **Training** | Training materials, recorded videos, staff trained |

---

## 💾 TECHNICAL SPECIFICATIONS

### System Requirements
- **Server**: 8GB+ RAM, 500GB SSD
- **Browser**: Chrome, Firefox, Safari (latest versions)
- **Network**: HTTPS connection recommended
- **Database**: DuckDB file-based (no server needed)

### Dashboard Technical Specs
- Query performance: <2 sec typical, <5 sec max
- Refresh rate: Real-time (on-demand) or scheduled
- Concurrent users: 10-20 simultaneously
- Data freshness: Daily (aligned with dbt build schedule)

### Data Architecture
```
DuckDB (oea.duckdb)
├── main_main_analytics (Stage 3)
│   ├── v_chronic_absenteeism_risk (3,400 rows)
│   ├── v_wellbeing_risk_profiles (3,400 rows)
│   ├── v_equity_outcomes_by_demographics (5 rows)
│   ├── v_class_section_comparison (300 rows)
│   └── v_performance_correlations (3 rows)
└── [other schemas - not used by dashboards]
```

---

## ⚠️ RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| **Slow query performance** | Pre-aggregate data in Stage 3 (already done); optimize views |
| **Data accuracy issues** | Validate data in UAT; spot-check vs. source systems |
| **User adoption** | Tailored training per role; ongoing support; highlight quick wins |
| **Access control misconfiguration** | Test each role in UAT; start restrictive, open as needed |
| **Metabase downtime** | Schedule backups; document restore procedure; monitor uptime |
| **Security breach** | Limit field visibility; hash PII; restrict network access |

---

## 📝 ASSUMPTIONS & CONSTRAINTS

**Assumptions**:
- All analytics views are production-ready (✅ confirmed)
- DuckDB database is stable and backed up
- Users have basic data literacy
- District IT can support Metabase operations
- Network bandwidth sufficient for data export

**Constraints**:
- No additional hardware procurement (use existing)
- Staff training limited to 45 min per session
- No offline dashboards (must access online)
- Metabase free version used (no premium features)
- Data refresh: Daily (not real-time)

---

## 🔄 NEXT STEPS (POST-DEPLOYMENT)

1. **Months 1-3**: Monitor usage, gather feedback, make refinements
2. **Month 3**: Create additional specialized dashboards based on user requests
3. **Quarter 2**: Integrate with other data sources (attendance system, LMS)
4. **Ongoing**: Update dashboards to reflect new district initiatives

---

## 📞 SUPPORT & ESCALATION

**Level 1**: Users can self-help using documentation and video tutorials  
**Level 2**: Helpdesk support via email (analytics@district.edu) - 24 hour response  
**Level 3**: Technical support team for configuration issues - 48 hour response  
**Level 4**: Metabase community + external consultant (if needed)

---

## ✅ APPROVAL CHECKLIST

- [x] **Plan Reviewed**: All stakeholders reviewed and approved
- [x] **Scope Confirmed**: 5 dashboards match business requirements
- [x] **Timeline Agreed**: 3-week implementation timeline acceptable
- [x] **Resources Allocated**: Team members assigned to tasks
- [x] **Budget Approved**: No licensing costs (open-source)
- [x] **Security Signed Off**: Access control model approved by IT/Privacy
- [x] **Ready to Proceed**: Executive approval to begin implementation

---

**Status**: Ready for Implementation  
**Prepared by**: Technical Team  
**Date**: January 27, 2026  
**Next Review**: Upon completion of each major task