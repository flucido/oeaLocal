# Integrated Student Analytics Framework
## Chronic Absenteeism + Well-Being + Performance + Equity

**Status**: Framework Design  
**Date**: January 27, 2026  
**Scope**: Complete analytical architecture for integrated student analysis  
**Audience**: Data analysts, data scientists, district leaders

---

## Executive Summary

This framework enables integrated analysis across **four interconnected domains**:

1. **Chronic Absenteeism** (attendance + discipline integration)
2. **Student Well-Being Risk** (discipline, behavioral, health signals)
3. **Academic Performance** (grades, assessments, graduation outcomes)
4. **Demographic Equity** (across ELL, special education, race, SES, housing status, class-level effectiveness)

The framework is built on a **unified data model** that allows you to:
- Segment students by demographic characteristics AND programs
- Correlate attendance/behavior with academic outcomes
- Compare class-level teaching effectiveness
- Identify equity gaps across demographic groups
- Understand how discipline, well-being, and attendance interact with performance

---

## Part 1: Analytical Framework Architecture

### 1.1 Core Analytical Questions

**Question Set A: Chronic Absenteeism**
- Which students are chronically absent (>10% absences)?
- What's the relationship between unexcused vs. excused absences?
- How do discipline incidents correlate with absence patterns?
- Which demographic groups have highest chronic absenteeism rates?
- What's the impact on academic performance?

**Question Set B: Student Well-Being Risk**
- Which students show signals of wellness concerns (attendance drop, behavior change, engagement decline)?
- How do discipline incidents indicate well-being issues?
- What's the relationship between assertive discipline data and student outcomes?
- Which students need proactive support?
- How does well-being vary by demographics?

**Question Set C: Performance Analysis**
- How does attendance relate to GPA, test scores, graduation?
- Which students are at risk of poor outcomes (poor grades, failing classes, off-pace for graduation)?
- What's the impact of behavioral incidents on performance?
- How do different teaching approaches affect outcomes (class-level effectiveness)?
- Which demographic groups are underperforming?

**Question Set D: Equity & Class-Level Effectiveness**
- How do outcomes vary by demographic group?
- Are certain subgroups systematically underperforming?
- Is one section of Algebra I performing better than another? Why?
- Which teachers/sections have best outcomes for at-risk students?
- Are discipline disparities present across groups?

### 1.2 Data Integration Model

```
STUDENT DEMOGRAPHICS              ATTENDANCE/ABSENCE          DISCIPLINE/BEHAVIOR
├─ Student ID (hashed)            ├─ Daily attendance status    ├─ Incident records
├─ Grade level                     ├─ Absence reason            ├─ Incident type/code
├─ School, District               ├─ Tardiness                 ├─ Severity level
├─ Race/Ethnicity                 ├─ Excused vs unexcused      ├─ Assertive discipline level
├─ English Language Learner (ELL)  ├─ Trends (30/60/90 day)     ├─ Suspension/expulsion
├─ Special Education (IEP/504)     └─ School year metrics       └─ Restorative practices
├─ Economically Disadvantaged
├─ Homeless/Foster
├─ Program enrollment (AP, honors, remedial)
└─ Entry/exit dates
                                        ↓
                        ┌─────────────────────────────┐
                        │   INTEGRATED STUDENT VIEW   │
                        │                             │
                        │ - Risk profiles             │
                        │ - Outcome predictions       │
                        │ - Equity analysis           │
                        │ - Intervention targets      │
                        │ - Effectiveness evaluation  │
                        └─────────────────────────────┘
                                        ↑
                    ACADEMIC PERFORMANCE         SYSTEM CONTEXT
                    ├─ Grades by course          ├─ Class section
                    ├─ Grade trends              ├─ Instructor ID
                    ├─ Assessment scores         ├─ Classroom size
                    ├─ Credit completion         ├─ Course difficulty
                    ├─ On-pace for graduation    └─ Program track
                    └─ Graduation status
```

### 1.3 Analysis Workflow

```
STAGE 1: DATA INGESTION & VALIDATION
└─ Ingest: Students, Attendance, Discipline, Grades, Assessments
   └─ Validate: Schema, domain rules, cross-system coherence

STAGE 2: DEMOGRAPHIC SEGMENTATION
└─ Create demographic cohorts (ELL, SPED, Race, SES, Housing, Programs)
   └─ Pseudonymize student identifiers
   └─ Flag special populations

STAGE 3: FEATURE ENGINEERING
├─ Attendance features (rate, trend, unexcused %, incident correlation)
├─ Behavioral features (incident count, severity trend, pattern)
├─ Performance features (GPA, grade trend, assessment z-score)
├─ Engagement features (class participation, assignment submission)
└─ Temporal features (30/60/90-day windows, seasonality)

STAGE 4: INTEGRATED ANALYSIS
├─ Correlation analysis (attendance ↔ behavior ↔ performance)
├─ Clustering (identify risk profiles)
├─ Class-level effectiveness (compare sections of same course)
├─ Equity analysis (outcome gaps by demographic)
└─ Predictive modeling (risk scores for intervention)

STAGE 5: DASHBOARD & REPORTING
├─ Executive summary (key metrics by demographic)
├─ Class-level comparison (same course, different sections)
├─ Student-level risk profiles (drill-down to individuals)
├─ Equity analysis (demographic outcome gaps)
└─ Intervention tracking (pre/post outcomes)
```

---

## Part 2: Chronic Absenteeism + Discipline Integration

### 2.1 Core Data Model

```sql
-- Core fact table: Daily Student State
CREATE TABLE stage3_published.fact_student_daily_state (
    student_key VARCHAR,                        -- Hashed student ID
    date_key DATE,
    
    -- Attendance facts
    attendance_status VARCHAR,                  -- Present, Absent_Excused, Absent_Unexcused, Tardy
    days_tardy INT,
    minutes_late INT,
    
    -- Discipline facts (if occurred this day)
    discipline_incident_occurred BOOLEAN,
    incident_count INT,
    incident_severity_max VARCHAR,              -- Minor, Moderate, Severe
    assertive_discipline_level INT,             -- 1-5 escalation level
    
    -- Derived indicators
    is_chronically_absent_flag BOOLEAN,         -- >10% unexcused absences in window
    attendance_risk_score FLOAT,                -- 0-100 (0=no risk, 100=highest risk)
    
    _loaded_at TIMESTAMP
);

-- Aggregated view: 30/60/90 day windows
CREATE TABLE stage3_published.agg_student_attendance_windows (
    student_key VARCHAR,
    analysis_date DATE,
    
    -- 30-day window
    days_30_enrolled INT,
    days_30_present INT,
    days_30_absent_unexcused INT,
    days_30_absent_excused INT,
    days_30_tardy INT,
    attendance_rate_30 FLOAT,
    discipline_incidents_30 INT,
    
    -- 60-day window
    days_60_enrolled INT,
    days_60_present INT,
    attendance_rate_60 FLOAT,
    discipline_incidents_60 INT,
    
    -- 90-day window
    days_90_enrolled INT,
    days_90_present INT,
    attendance_rate_90 FLOAT,
    discipline_incidents_90 INT,
    
    -- Correlation indicators
    absence_discipline_correlation VARCHAR,    -- None, Weak, Strong, VeryStrong
    trend_direction VARCHAR,                    -- Improving, Stable, Declining
    
    _loaded_at TIMESTAMP
);

-- Discipline detail
CREATE TABLE stage2b_refined.fact_discipline_incidents (
    incident_key VARCHAR PRIMARY KEY,
    student_key VARCHAR,
    incident_date DATE,
    incident_time TIME,
    
    incident_type VARCHAR,                      -- Class disruption, Fighting, Insubordination, etc.
    incident_code INT,                          -- System code
    severity_level VARCHAR,                     -- Minor, Moderate, Severe, Critical
    assertive_discipline_level INT,             -- 1=Warning, 2=Detention, 3=In-school suspension, etc.
    
    location VARCHAR,                           -- Classroom, Hallway, Cafeteria, etc.
    involved_staff VARCHAR,                     -- Staff member (hashed)
    witnessed_by_count INT,
    
    consequence_type VARCHAR,                   -- Warning, Detention, Suspension, Expulsion, Restorative
    consequence_date DATE,
    consequence_duration INT,                   -- Days (if suspension)
    
    follow_up_action VARCHAR,                   -- Parent contact, counselor referral, etc.
    
    _loaded_at TIMESTAMP
);
```

### 2.2 Feature Engineering for Chronic Absenteeism

```python
# Chronic Absenteeism Risk Features

features = {
    # Basic attendance metrics
    'attendance_rate_30d': 'days_present_30 / days_enrolled_30',
    'unexcused_absence_rate_30d': 'days_unexcused_absent_30 / days_enrolled_30',
    'excused_absence_rate_30d': 'days_excused_absent_30 / days_enrolled_30',
    'tardy_rate_30d': 'days_tardy_30 / days_enrolled_30',
    
    # Temporal trends
    'attendance_trend_90d': 'slope(attendance_rate over 90 days)',
    'attendance_volatility_30d': 'std_dev(daily attendance over 30 days)',
    'absence_acceleration': 'change(absence_rate_30d) vs change(absence_rate_60d)',
    
    # Discipline correlation
    'discipline_incident_count_30d': 'count(incidents in 30 days)',
    'discipline_severity_avg_30d': 'severity_score(1=minor...5=critical) avg over 30d',
    'discipline_trend_30d': 'increasing/stable/decreasing',
    
    # Absence-Discipline correlation
    'days_with_incident_and_absence_30d': 'count(days with both)',
    'incident_discipline_ratio': 'incidents / unexcused_absences',
    'correlation_absence_discipline': 'pearson_correlation(absence ↔ incident)',
    
    # Pattern indicators
    'monday_absence_rate': 'absence_rate(Mondays only)',
    'friday_absence_rate': 'absence_rate(Fridays only)',
    'post_incident_absence_rate': 'absence_rate(days after incident vs baseline)',
    'chronic_unexcused_flag': 'unexcused_absence_rate > 0.10',
    
    # Demographic breakdowns (for all above)
    'by_race_ethnicity': 'separate rates by demographic',
    'by_ell_status': 'compare ELL vs non-ELL',
    'by_sped_status': 'compare SPED vs general ed',
    'by_ses': 'compare free/reduced lunch vs full pay',
    'by_grade_level': 'compare by grade',
}

# Risk scoring
def chronic_absence_risk_score(student_features):
    """
    Combines multiple signals into 0-100 risk score
    Higher = more at-risk
    """
    score = 0
    
    # Attendance base (0-40 points)
    if attendance_rate_30d < 0.95:
        score += 10 * (0.95 - attendance_rate_30d) / 0.95
    if unexcused_absence_rate_30d > 0.05:
        score += 20 * min(unexcused_absence_rate_30d / 0.15, 1.0)
    
    # Discipline multiplier (0-30 points)
    if discipline_incident_count_30d > 0:
        score += min(discipline_incident_count_30d * 5, 30)
    
    # Trend acceleration (0-20 points)
    if attendance_trend_90d < 0:  # Getting worse
        score += 20
    elif attendance_trend_90d > 0:  # Getting better
        score -= min(abs(attendance_trend_90d) * 5, 10)
    
    # Absence-discipline correlation (0-10 points)
    if correlation_absence_discipline > 0.5:
        score += correlation_absence_discipline * 10
    
    return min(max(score, 0), 100)
```

### 2.3 Chronic Absenteeism Dashboard Specifications

**Dashboard 1: Chronic Absenteeism Overview**

| Visualization | Query | Segment By |
|---|---|---|
| **Metric Cards** | Chronic absence rate, incident rate, avg score | Total, by school, by grade |
| **Trend Line** | Attendance rate (30/60/90 day) vs incident count | All students, flagged students |
| **Bar Chart** | Students at-risk by grade level | Grade 9, 10, 11, 12 |
| **Scatter Plot** | Attendance rate vs discipline incidents | Color: demographic group |
| **Table** | Top 25 at-risk students | Name (hashed), score, drivers |
| **Heatmap** | Absence rate by day-of-week & grade | Shows Monday/Friday patterns |

**Segment Controls**: 
- Filter by: School, Grade, Demographic (Race, ELL, SPED, SES, Housing)
- Compare: This year vs last year, this month vs last month

---

## Part 3: Student Well-Being Risk Model

### 3.1 Well-Being Data Integration

```sql
-- Multi-dimensional well-being risk model
CREATE TABLE stage3_published.fact_student_wellbeing_risk (
    student_key VARCHAR,
    analysis_date DATE,
    
    -- Attendance signals
    attendance_risk_score FLOAT,        -- 0-100 (from chronic absenteeism model)
    attendance_change_30d FLOAT,        -- % change from 30-60 days ago
    
    -- Behavioral/Discipline signals
    discipline_risk_score FLOAT,        -- 0-100 based on frequency/severity
    incident_frequency_trend VARCHAR,   -- Increasing/Stable/Decreasing
    incident_severity_escalation BOOLEAN, -- Recently escalating?
    
    -- Academic engagement signals
    engagement_risk_score FLOAT,        -- 0-100 based on LMS activity
    assignment_completion_rate FLOAT,   -- % assignments turned in on time
    grade_trend VARCHAR,                -- Improving/Stable/Declining
    
    -- Cross-signal indicators
    multi_domain_risk BOOLEAN,          -- At-risk in 2+ domains?
    risk_escalation BOOLEAN,            -- Risk worsening over time?
    
    -- Integrated well-being risk score
    wellbeing_risk_score FLOAT,         -- 0-100 composite score
    wellbeing_risk_level VARCHAR,       -- Low, Moderate, High, Critical
    
    -- Recommended interventions
    primary_concern VARCHAR,            -- Attendance, Behavior, Academic, Multi-factor
    recommended_actions VARCHAR,        -- Counselor referral, Parent contact, etc.
    
    _loaded_at TIMESTAMP
);

-- Assertive Discipline detail (linked to well-being)
CREATE TABLE stage2b_refined.fact_assertive_discipline_escalation (
    student_key VARCHAR,
    academic_year INT,
    
    -- Escalation progression
    level_1_warnings INT,               -- Warnings issued
    level_2_detentions INT,             -- After-school/lunch detention
    level_3_in_school_suspension INT,   -- ISS days
    level_4_out_of_school_suspension INT, -- OSS days
    level_5_expulsion BOOLEAN,          -- Recommended for expulsion?
    
    -- Restorative practices
    restorative_conference_completed BOOLEAN,
    restorative_plan_created BOOLEAN,
    behavior_improved_after_intervention BOOLEAN,
    
    -- Well-being flags
    indicates_trauma_signal BOOLEAN,    -- Pattern suggests trauma/crisis
    indicates_peer_conflict BOOLEAN,    -- Pattern suggests bullying/conflict
    indicates_adult_conflict BOOLEAN,   -- Pattern suggests authority issues
    
    _loaded_at TIMESTAMP
);
```

### 3.2 Well-Being Risk Scoring Algorithm

```python
def wellbeing_risk_score(student):
    """
    Integrates attendance, discipline, academic, and engagement signals
    Returns 0-100 score where:
    - 0-30 = Low risk (monitor)
    - 31-60 = Moderate risk (intervene)
    - 61-80 = High risk (urgent support)
    - 81-100 = Critical risk (immediate action)
    """
    
    # Domain scores (each 0-100)
    attendance_score = calculate_attendance_risk()      # Based on absence trend, pattern
    discipline_score = calculate_discipline_risk()      # Based on frequency, severity, trend
    academic_score = calculate_academic_risk()          # Based on grades, trend
    engagement_score = calculate_engagement_risk()      # Based on LMS activity, participation
    
    # Interaction weights (if at-risk in multiple domains, higher weight)
    risk_domains = sum([
        attendance_score > 60,
        discipline_score > 60,
        academic_score > 60,
        engagement_score > 60
    ])
    
    if risk_domains == 0:
        # No high-risk signals
        composite = (attendance_score + discipline_score + academic_score + engagement_score) / 4
        
    elif risk_domains == 1:
        # At-risk in one domain: weight heavily
        weights = [
            attendance_score > 60 * 0.4,
            discipline_score > 60 * 0.35,
            academic_score > 60 * 0.35,
            engagement_score > 60 * 0.3
        ]
        composite = weighted_average(
            [attendance_score, discipline_score, academic_score, engagement_score],
            weights
        )
        
    else:
        # At-risk in 2+ domains: multiplicative effect
        # Each additional domain multiplies risk
        composite = (attendance_score + discipline_score + academic_score + engagement_score) / 4
        composite = composite * (1 + (risk_domains - 1) * 0.25)  # Compound risk
    
    # Trend acceleration: if worsening, increase score
    if any([
        attendance_trend < 0,  # Attendance declining
        discipline_trend > 0,  # Incidents increasing
        grade_trend < 0,       # Grades declining
        engagement_trend < 0   # Engagement declining
    ]):
        composite *= 1.2  # 20% boost for accelerating risk
    
    # Recently had major incident? Add weight
    if last_critical_incident_days_ago < 30:
        composite = min(composite * 1.3, 100)  # Boost to 130% but cap at 100
    
    return min(max(composite, 0), 100)

# Recommended interventions
def recommend_interventions(student, wellbeing_score):
    """
    Based on score and domain patterns, recommend specific actions
    """
    interventions = []
    
    if wellbeing_score < 30:
        interventions.append("Monitor: Regular check-ins")
        
    elif wellbeing_score < 60:
        # Moderate risk
        if attendance_score > 60:
            interventions.append("Contact parent: Attendance concerns")
            interventions.append("Counselor: Attendance barriers assessment")
        if discipline_score > 60:
            interventions.append("Counselor: Behavior support plan")
            interventions.append("Consider restorative practices")
        if academic_score > 60:
            interventions.append("Tutor: Academic support")
            interventions.append("Monitor grades weekly")
        if engagement_score > 60:
            interventions.append("LMS monitoring: Increase check-ins")
            
    else:
        # High/Critical risk
        interventions.append("URGENT: Family/Student meeting")
        interventions.append("Assess: Trauma-informed screening")
        interventions.append("Coordinate: Multi-disciplinary team")
        if discipline_score > 80:
            interventions.append("Safety assessment")
            interventions.append("Consider restorative practices vs suspension")
    
    return interventions
```

---

## Part 4: Demographic Segmentation & Equity Analysis

### 4.1 Demographic Segmentation Schema

```sql
-- Master demographic attributes (pseudonymized)
CREATE TABLE stage2b_refined.dim_student_demographics (
    student_key VARCHAR PRIMARY KEY,
    student_id_hash VARCHAR,                    -- For lookup tables if needed
    
    -- Core demographics (no-op, not sensitive for aggregation)
    grade_level INT,
    school_id VARCHAR,
    district_id VARCHAR,
    
    -- Race/Ethnicity segmentation
    race_ethnicity VARCHAR,                     -- White, Black, Hispanic, Asian, Native American, Multiracial, Other
    race_ethnicity_rollup VARCHAR,              -- White, Black, Hispanic, Asian, Other
    
    -- Language status
    english_learner BOOLEAN,
    ell_status VARCHAR,                         -- Fluent English Proficient, Limited English Proficient, Bilingual
    primary_language VARCHAR,                   -- Spanish, Hmong, Somali, etc.
    years_in_ell_program INT,
    
    -- Special Education & Disability
    special_education BOOLEAN,
    iep_flag BOOLEAN,                           -- Has Individualized Education Plan
    section_504_flag BOOLEAN,                   -- Has 504 plan
    disability_category VARCHAR,                -- Speech, Learning Disabled, Emotional, Autism, etc.
    
    -- Socioeconomic status
    free_reduced_lunch BOOLEAN,
    economically_disadvantaged VARCHAR,         -- Free, Reduced, Full-pay
    
    -- Housing/Family status
    homeless_flag BOOLEAN,
    foster_care_flag BOOLEAN,
    parent_education_level VARCHAR,             -- HS, Some College, College, Graduate
    household_income_bracket VARCHAR,           -- <25k, 25-50k, 50-75k, 75-100k, >100k
    
    -- Program enrollment
    program_enrollment VARCHAR,                 -- Advanced, Honors, General, Remedial, AP, IB, STEM, etc.
    program_start_date DATE,
    program_end_date DATE,
    
    -- Entry/Exit tracking
    entry_date DATE,
    exit_date DATE,
    withdrawal_reason VARCHAR,                  -- Graduated, Transferred, Moved, Dropout, etc.
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP
);

-- Cohort definitions for easy filtering
CREATE TABLE stage3_published.v_student_demographic_cohorts AS
SELECT
    student_key,
    
    -- Binary flags for filtering
    CASE WHEN english_learner THEN 'ELL' ELSE 'Non-ELL' END AS ell_group,
    CASE WHEN special_education THEN 'SPED' ELSE 'General Ed' END AS sped_group,
    CASE WHEN free_reduced_lunch THEN 'FRL' ELSE 'Full-Pay' END AS ses_group,
    CASE WHEN homeless_flag THEN 'Homeless' ELSE 'Housed' END AS housing_group,
    CASE WHEN foster_care_flag THEN 'Foster' ELSE 'Non-Foster' END AS foster_group,
    
    race_ethnicity,
    race_ethnicity_rollup,
    
    -- Multi-group indicators
    (special_education::INT + english_learner::INT + free_reduced_lunch::INT) AS risk_factor_count,
    (homeless_flag::INT + foster_care_flag::INT) AS unstable_housing_indicator,
    
FROM stage2b_refined.dim_student_demographics;
```

### 4.2 Equity Analysis Queries

```sql
-- Equity Gap Analysis: Outcomes by Demographic Group
CREATE VIEW v_equity_outcomes_by_demographics AS
WITH student_outcomes AS (
    SELECT
        d.race_ethnicity,
        d.english_learner,
        d.special_education,
        d.free_reduced_lunch,
        d.homeless_flag,
        
        -- Attendance outcomes
        ROUND(100.0 * SUM(CASE WHEN a.attendance_rate > 0.90 THEN 1 ELSE 0 END) 
            / COUNT(*), 1) AS pct_good_attendance,
        
        -- Discipline outcomes
        ROUND(100.0 * SUM(CASE WHEN di.incident_count_year = 0 THEN 1 ELSE 0 END) 
            / COUNT(*), 1) AS pct_no_discipline,
        
        -- Academic outcomes
        ROUND(AVG(g.gpa), 2) AS avg_gpa,
        ROUND(100.0 * SUM(CASE WHEN g.gpa >= 2.5 THEN 1 ELSE 0 END) 
            / COUNT(*), 1) AS pct_gpa_2_5_plus,
        
        -- Graduation outcomes
        ROUND(100.0 * SUM(CASE WHEN grad.graduated THEN 1 ELSE 0 END) 
            / COUNT(*), 1) AS graduation_rate,
        
        COUNT(*) AS cohort_size
        
    FROM stage2b_refined.dim_student_demographics d
    LEFT JOIN agg_student_attendance_30d a ON d.student_key = a.student_key
    LEFT JOIN agg_discipline_incidents di ON d.student_key = di.student_key
    LEFT JOIN agg_student_grades_year g ON d.student_key = g.student_key
    LEFT JOIN agg_graduation grad ON d.student_key = grad.student_key
    
    GROUP BY 1, 2, 3, 4, 5
)

SELECT
    race_ethnicity,
    english_learner,
    special_education,
    free_reduced_lunch,
    homeless_flag,
    pct_good_attendance,
    pct_no_discipline,
    avg_gpa,
    pct_gpa_2_5_plus,
    graduation_rate,
    cohort_size
FROM student_outcomes
ORDER BY race_ethnicity, english_learner, special_education;

-- Equity Gap Calculation: Compare underrepresented groups to district average
CREATE VIEW v_equity_gaps AS
WITH outcomes_by_group AS (
    SELECT
        'All Students' AS demographic_group,
        COUNT(*) AS cohort_size,
        ROUND(100.0 * SUM(CASE WHEN a.attendance_rate > 0.90 THEN 1 ELSE 0 END) / COUNT(*), 1) AS attendance_rate,
        ROUND(AVG(g.gpa), 2) AS avg_gpa,
        ROUND(100.0 * SUM(CASE WHEN grad.graduated THEN 1 ELSE 0 END) / COUNT(*), 1) AS graduation_rate
    FROM stage2b_refined.dim_student_demographics d
    ...
    
    UNION ALL
    
    SELECT
        'Race: ' || d.race_ethnicity,
        COUNT(*),
        ... (same metrics)
    FROM stage2b_refined.dim_student_demographics d
    WHERE d.race_ethnicity IS NOT NULL
    GROUP BY 1
    
    UNION ALL
    
    SELECT
        CASE WHEN english_learner THEN 'English Language Learners' ELSE 'Non-ELL' END,
        COUNT(*),
        ... (same metrics)
    FROM stage2b_refined.dim_student_demographics d
    GROUP BY 1
    
    UNION ALL
    
    SELECT
        CASE WHEN special_education THEN 'Special Education' ELSE 'General Education' END,
        COUNT(*),
        ... (same metrics)
    FROM stage2b_refined.dim_student_demographics d
    GROUP BY 1
)

SELECT
    demographic_group,
    cohort_size,
    attendance_rate,
    (attendance_rate - (SELECT attendance_rate FROM outcomes_by_group WHERE demographic_group = 'All Students')) AS attendance_gap,
    avg_gpa,
    (avg_gpa - (SELECT avg_gpa FROM outcomes_by_group WHERE demographic_group = 'All Students')) AS gpa_gap,
    graduation_rate,
    (graduation_rate - (SELECT graduation_rate FROM outcomes_by_group WHERE demographic_group = 'All Students')) AS graduation_gap
FROM outcomes_by_group
WHERE demographic_group != 'All Students'
ORDER BY ABS(graduation_gap) DESC;
```

---

## Part 5: Class-Level Effectiveness Analysis

### 5.1 Class Section Comparison Model

```sql
-- Class/Section fact table with instructor and context
CREATE TABLE stage2b_refined.fact_class_enrollment (
    enrollment_key VARCHAR PRIMARY KEY,
    student_key VARCHAR,
    school_id VARCHAR,
    course_id VARCHAR,
    section_id VARCHAR,                         -- Unique section (not just course)
    section_number INT,                         -- Section A, B, C, etc.
    term_id VARCHAR,
    academic_year INT,
    
    instructor_id_hash VARCHAR,                 -- Pseudonymized instructor
    class_size INT,
    
    start_date DATE,
    end_date DATE,
    
    -- Student demographics (for subgroup analysis)
    student_race_ethnicity VARCHAR,
    student_ell_status BOOLEAN,
    student_sped_status BOOLEAN,
    student_ses_status VARCHAR,
    
    -- Enrollment outcomes
    grade_earned VARCHAR,                       -- A, B, C, D, F
    grade_numeric FLOAT,                        -- 4.0, 3.0, 2.0, 1.0, 0.0
    credit_earned BOOLEAN,
    passed BOOLEAN,                             -- Grade >= C
    
    -- Attendance in this class
    attendance_rate FLOAT,
    class_absences INT,
    class_tardies INT,
    
    _loaded_at TIMESTAMP
);

-- Aggregated class effectiveness metrics
CREATE TABLE stage3_published.agg_class_effectiveness (
    section_key VARCHAR PRIMARY KEY,
    school_id VARCHAR,
    course_id VARCHAR,
    section_id VARCHAR,
    term_id VARCHAR,
    academic_year INT,
    
    instructor_id_hash VARCHAR,
    class_size INT,
    
    -- Overall effectiveness
    avg_grade_numeric FLOAT,                    -- Average grade in course
    pct_passed FLOAT,                           -- % students earned credit (C or better)
    pct_A_B_grades FLOAT,                       -- % A or B grades
    median_grade_numeric FLOAT,
    
    -- Attendance effectiveness
    avg_class_attendance_rate FLOAT,
    avg_absences_per_student INT,
    
    -- Equity analysis: How does class perform for underrepresented groups?
    pct_passed_ell FLOAT,
    pct_passed_sped FLOAT,
    pct_passed_frl FLOAT,
    pct_passed_by_race JSONB,                   -- {'White': 85.0, 'Black': 72.0, ...}
    
    -- Grade distribution
    pct_A_grades FLOAT,
    pct_B_grades FLOAT,
    pct_C_grades FLOAT,
    pct_D_grades FLOAT,
    pct_F_grades FLOAT,
    
    -- Grade variance (how consistent is grading?)
    grade_std_dev FLOAT,
    
    -- Engagement
    avg_assignment_completion_rate FLOAT,
    avg_online_activity_score FLOAT,
    
    _loaded_at TIMESTAMP
);

-- Section comparison view (same course, different sections)
CREATE VIEW v_class_section_comparison AS
SELECT
    course_id,
    section_id,
    section_number,
    term_id,
    academic_year,
    
    instructor_id_hash,
    class_size,
    
    avg_grade_numeric,
    pct_passed,
    pct_A_B_grades,
    
    -- Compare to other sections of same course
    (
        SELECT AVG(avg_grade_numeric) 
        FROM agg_class_effectiveness ace2 
        WHERE ace2.course_id = ace.course_id 
        AND ace2.term_id = ace.term_id
    ) AS same_course_avg_grade,
    
    (avg_grade_numeric - 
        (SELECT AVG(avg_grade_numeric) 
        FROM agg_class_effectiveness ace2 
        WHERE ace2.course_id = ace.course_id 
        AND ace2.term_id = ace.term_id)
    ) AS grade_diff_from_section_avg,
    
    pct_passed_ell,
    pct_passed_sped,
    pct_passed_frl,
    
    -- Effectiveness ranking (within same course/term)
    RANK() OVER (
        PARTITION BY course_id, term_id 
        ORDER BY pct_passed DESC
    ) AS section_rank_by_pass_rate,
    
    RANK() OVER (
        PARTITION BY course_id, term_id 
        ORDER BY avg_grade_numeric DESC
    ) AS section_rank_by_avg_grade
    
FROM stage3_published.agg_class_effectiveness ace
WHERE academic_year = EXTRACT(YEAR FROM CURRENT_DATE)
ORDER BY course_id, section_number;
```

### 5.2 Class Effectiveness Analysis Queries

```sql
-- What makes the highest-performing section different?
SELECT
    'Course: ' || c1.course_id || ' Section: ' || c1.section_number AS highest_section,
    'Course: ' || c2.course_id || ' Section: ' || c2.section_number AS comparison_section,
    
    c1.avg_grade_numeric AS highest_avg_grade,
    c2.avg_grade_numeric AS comparison_avg_grade,
    (c1.avg_grade_numeric - c2.avg_grade_numeric) AS grade_difference,
    
    c1.pct_passed AS highest_pass_rate,
    c2.pct_passed AS comparison_pass_rate,
    
    c1.class_size,
    c2.class_size,
    
    c1.avg_class_attendance_rate AS highest_attendance,
    c2.avg_class_attendance_rate AS comparison_attendance,
    
    c1.avg_assignment_completion_rate AS highest_completion,
    c2.avg_assignment_completion_rate AS comparison_completion,
    
    -- Equity: How well does each section support vulnerable students?
    c1.pct_passed_ell AS highest_ell_pass,
    c2.pct_passed_ell AS comparison_ell_pass,
    (c1.pct_passed_ell - c2.pct_passed_ell) AS ell_gap
    
FROM agg_class_effectiveness c1
JOIN agg_class_effectiveness c2 ON c1.course_id = c2.course_id 
    AND c1.term_id = c2.term_id
    AND c1.section_id != c2.section_id
    
WHERE c1.avg_grade_numeric = (
    SELECT MAX(avg_grade_numeric)
    FROM agg_class_effectiveness
    WHERE course_id = c1.course_id AND term_id = c1.term_id
)
AND c2.avg_grade_numeric = (
    SELECT MIN(avg_grade_numeric)
    FROM agg_class_effectiveness
    WHERE course_id = c2.course_id AND term_id = c2.term_id
);
```

---

## Part 6: Performance Correlation Analysis

### 6.1 Correlation Framework

```python
# Correlation Analysis: How do attendance/behavior/well-being relate to performance?

correlations = {
    # Attendance ↔ Performance
    'attendance_rate_vs_gpa': {
        'description': 'Does attendance predict GPA?',
        'method': 'Pearson correlation',
        'expected': 'Strong positive (r > 0.6)',
        'calculation': 'correlation(attendance_rate, cumulative_gpa)',
        'significance_level': 'p < 0.05'
    },
    
    # Discipline ↔ Performance
    'discipline_incidents_vs_grades': {
        'description': 'Does behavioral issues predict lower grades?',
        'method': 'Spearman correlation',
        'expected': 'Negative (r < -0.4)',
        'calculation': 'correlation(incidents_per_term, grades)',
        'significance_level': 'p < 0.05'
    },
    
    # Engagement ↔ Performance
    'lms_engagement_vs_performance': {
        'description': 'Does LMS activity predict assignment completion & grades?',
        'method': 'Pearson correlation',
        'expected': 'Positive (r > 0.5)',
        'calculation': 'correlation(engagement_score, assignment_completion)'
    },
    
    # Combined risk ↔ Performance
    'multi_factor_risk_vs_graduation': {
        'description': 'Does combination of attendance+behavior+engagement predict graduation?',
        'method': 'Logistic regression',
        'expected': 'Significant negative relationship',
        'calculation': 'logit(graduation) ~ attendance + discipline + engagement'
    }
}

# By demographic
def correlations_by_demographic(demographic_group):
    """
    Calculate all correlations separately by demographic
    to identify equity gaps in how factors affect outcomes
    """
    results = {}
    
    for demographic in ['race_ethnicity', 'ell_status', 'sped_status', 'ses_status']:
        for group_value in distinct_values(demographic):
            # Filter data to this group
            subset = students[students[demographic] == group_value]
            
            # Calculate correlations within group
            results[f'{demographic}_{group_value}'] = {
                'attendance_gpa_correlation': correlation(subset.attendance_rate, subset.gpa),
                'discipline_grades_correlation': correlation(subset.incidents, subset.grades),
                'cohort_size': len(subset)
            }
    
    return results
```

### 6.2 Performance Analysis Tables

```sql
-- Integrated student performance view (combines all domains)
CREATE TABLE stage3_published.v_student_performance_integrated AS
SELECT
    d.student_key,
    d.grade_level,
    d.school_id,
    d.race_ethnicity,
    d.english_learner,
    d.special_education,
    d.free_reduced_lunch,
    
    -- Attendance
    ROUND(a.attendance_rate_90d, 2) AS attendance_rate_90d,
    a.chronic_absence_flag,
    
    -- Discipline
    di.incident_count_90d,
    di.incident_severity_avg,
    
    -- Academic performance
    g.cumulative_gpa,
    g.current_term_gpa,
    g.gpa_trend_direction,
    ROUND((g.current_term_gpa - g.prior_term_gpa) / 4.0 * 100, 1) AS gpa_trend_pct,
    
    -- Assessment performance
    ast.most_recent_assessment_score,
    ast.assessment_percentile,
    
    -- On-pace analysis
    grad.credits_earned_to_date,
    grad.credits_required_for_graduation,
    ROUND(100.0 * grad.credits_earned_to_date / grad.credits_required_for_graduation, 1) AS pct_credits_complete,
    CASE 
        WHEN grad.credits_earned_to_date / (4 - d.grade_level) >= grad.credits_required_for_graduation / (13 - 9) THEN 'On-Pace'
        WHEN grad.credits_earned_to_date / (4 - d.grade_level) >= grad.credits_required_for_graduation / (13 - 9) * 0.8 THEN 'Slightly Behind'
        ELSE 'At-Risk'
    END AS graduation_pacing,
    
    -- Risk scoring
    a.attendance_risk_score,
    di.discipline_risk_score,
    g.academic_risk_score,
    ROUND((a.attendance_risk_score + di.discipline_risk_score + g.academic_risk_score) / 3, 1) AS integrated_risk_score
    
FROM stage2b_refined.dim_student_demographics d
LEFT JOIN agg_attendance_windows a ON d.student_key = a.student_key
LEFT JOIN agg_discipline_incidents di ON d.student_key = di.student_key
LEFT JOIN agg_student_grades g ON d.student_key = g.student_key
LEFT JOIN agg_assessment_performance ast ON d.student_key = ast.student_key
LEFT JOIN agg_graduation_progress grad ON d.student_key = grad.student_key;
```

---

## Part 7: Implementation Roadmap

### Phase 1: Data Foundation (Weeks 1-4)
- [ ] Ingest: Students, Attendance, Discipline, Grades, Assessments
- [ ] Validate: Schema, domain rules, cross-system coherence
- [ ] Pseudonymize: Student identifiers, staff identifiers
- [ ] Create: Stage 2 refined tables

### Phase 2: Feature Engineering (Weeks 5-8)
- [ ] Build: Attendance feature tables (30/60/90 day windows)
- [ ] Build: Discipline feature tables and risk scoring
- [ ] Build: Academic performance aggregations
- [ ] Build: Demographic cohort views

### Phase 3: Integrated Analysis (Weeks 9-12)
- [ ] Create: Chronic absenteeism risk model
- [ ] Create: Well-being risk model (multi-domain)
- [ ] Create: Equity analysis views
- [ ] Create: Class effectiveness analysis
- [ ] Calculate: Correlations (attendance ↔ performance, etc.)

### Phase 4: Dashboards & Deployment (Weeks 13-16)
- [ ] Dashboard: Chronic Absenteeism Overview
- [ ] Dashboard: Student Well-Being Risk Profiles
- [ ] Dashboard: Equity & Demographic Analysis
- [ ] Dashboard: Class Effectiveness Comparison
- [ ] Dashboard: Performance Correlations
- [ ] User Training & Launch

---

## Part 8: Key Success Criteria

**Data Quality**
- [ ] 100% of students have valid demographic data
- [ ] Attendance data completeness > 99%
- [ ] Discipline data linkage > 95%
- [ ] Attendance-discipline correlation identified for >50% of students

**Analytical Rigor**
- [ ] All features documented with business logic
- [ ] All correlations with p-value significance testing
- [ ] Fairness assessment: No demographic disparity > 10% without explanation
- [ ] Risk models cross-validated (holdout test set performance > 75% accuracy)

**Equity Focus**
- [ ] Outcome gaps identified for all demographic groups
- [ ] Class-level effectiveness variation explained
- [ ] Intervention targeting validated with post-hoc outcome analysis

**User Adoption**
- [ ] Superintendent sees value in data
- [ ] Teachers can understand class-level comparisons
- [ ] Counselors can identify students for intervention
- [ ] Dashboard used by >80% of relevant staff weekly

---

## Next Steps

1. **Approve Framework**: Get stakeholder buy-in on this comprehensive model
2. **Finalize Data Sources**: Confirm all data sources available (especially discipline, grades)
3. **Build Stage 2 Tables**: Implement all schema above
4. **Develop Risk Models**: Build Python/SQL models for scoring
5. **Create Initial Dashboards**: Prioritize chronic absenteeism first
6. **Pilot with Counselors**: Get feedback from end users
7. **Refine & Iterate**: Adjust based on feedback

---

**Questions for You:**

1. Is the discipline data granular enough for incident-level analysis?
2. Do you have assertive discipline level data (1-5 escalation)?
3. Are grades available real-time or batch-loaded?
4. What is your data retention policy for sensitive information?
5. Which demographic segmentations are most important to your district?
