# Integrated Student Analytics Framework - DETAILED IMPLEMENTATION
## Chronic Absenteeism + Well-Being + Performance + Equity (SPECIFIC REQUIREMENTS)

**Status**: Ready for Approval (Detailed Specification)  
**Date**: January 27, 2026  
**Data Sources**: Aeries SIS (via API + direct tables)  
**Scope**: Full implementation plan with exact table mappings, API endpoints, and SQL specifications

---

## EXECUTIVE SUMMARY

This plan implements comprehensive integrated analytics leveraging:
- **Aeries API** for real-time data (reports endpoints)
- **OSS Framework** metadata system (6 core entities, 132 attributes)
- **District-specific Excel reports** (D&F with 504/SPED, Demographic, RFEP data)
- **Pseudonymization rules** (hash, mask, no-op per metadata_combined.csv)

Deliverable: **5 integrated dashboards + 12 risk scoring models + equity analysis views**

---

## Part 1: Data Integration & Architecture

### 1.1 Data Sources Mapped to Framework

| Source | Type | Primary Use | OSS Entity | Key Tables |
|--------|------|-------------|-----------|-----------|
| **Aeries SIS** | OLTP | Students, enrollment, attendance | students, enrollment, courses, academic_records | STU, ENR, CRS, SEC, ATT, CAT |
| **Aeries API** | REST | Real-time reports | engagement_events (derived) | /api/v5/reports/* |
| **D&F w_504 SE Report** | Excel/Extract | Special ed + at-risk tracking | students (SPED flag), academic_records | Custom: 504_IEP_Status |
| **Demographic Data by Course** | Excel/Extract | Race/ethnicity by section | students, enrollment | Custom: DEMOGRAPHIC_BREAKDOWNS |
| **RFEP Data** | Image/Manual | English learner tracking | students (ELL flags) | Custom: LANGUAGE_PROFICIENCY |

### 1.2 OSS Framework Metadata System (Applied)

**6 Core Entities with Pseudonymization Rules:**

```
ENTITY: students (26 attributes)
├─ Identifiers (hashed):
│  ├─ student_id → hash (enables linkage via lookup table)
│  ├─ date_of_birth → hash (sensitive)
│  └─ phone_number → mask (irreversible)
├─ Demographics (no-op):
│  ├─ grade_level, gender, ethnicity, cohort_year
│  ├─ special_education, english_learner, economically_disadvantaged
│  ├─ homeless_status, foster_care_status
│  └─ [KEY] New: 504_flag, IEP_status, disability_category
└─ Timestamps (no-op):
   ├─ _loaded_date, _updated_date
   └─ enrollment_start_date, enrollment_end_date

ENTITY: attendance (22 attributes)
├─ Link Fields (hashed):
│  ├─ student_id → hash
│  ├─ teacher_id → hash
│  └─ school_id → no-op
├─ Attendance Facts (no-op):
│  ├─ attendance_date, checkin_time, checkout_time
│  ├─ is_present, tardy_flag, early_departure_flag
│  ├─ absence_type (excused/unexcused/medical/OSS/ISS)
│  ├─ absence_reason, period_or_class
│  ├─ chronic_absence_flag (computed)
│  └─ attendance_pattern (improving/declining/stable/at_risk)
└─ Follow-up (no-op):
   ├─ parent_notification_sent, makeup_assignment_required
   └─ [NEW] discipline_incident_linked (links to discipline table)

ENTITY: academic_records (23 attributes)
├─ Link Fields (hashed):
│  ├─ student_id → hash
│  ├─ teacher_id → hash
│  └─ school_id, course_id, term → no-op
├─ Assignment Data (no-op):
│  ├─ assignment_id, assignment_name, assignment_type
│  ├─ assignment_due_date, assignment_submission_date
│  ├─ points_earned, points_possible, assignment_grade_percent
│  ├─ assignment_grade_letter, mastery_level
│  ├─ late_days, on_time_flag, submission_status
│  └─ [NEW] assignment_quality_flag (derived from rubric_score)
└─ Metadata (no-op):
   ├─ feedback_provided, feedback_date, rubric_score
   ├─ _loaded_date, _updated_date
   └─ [NEW] relative_grade (vs. class average)

ENTITY: enrollment (23 attributes)
├─ Link Fields (hashed):
│  ├─ student_id → hash
│  └─ course_id, term, school_id → no-op
├─ Enrollment State (no-op):
│  ├─ enrollment_date, completion_date
│  ├─ enrollment_status (active/completed/dropped/failed)
│  ├─ credits_attempted, credits_earned
│  ├─ final_grade_letter, final_grade_numeric
│  ├─ weighted_gpa_impact
│  └─ [NEW] section_teacher_id (hashed) - for class-level effectiveness
└─ Risk Flags (computed):
   ├─ academic_risk_flag, engagement_flag
   ├─ attendance_days, absence_count (period totals)
   └─ excused_absence_count, unexcused_absence_count

ENTITY: engagement_events (21 attributes)
├─ Link Fields (hashed):
│  ├─ student_id → hash, event_id → no-op
│  ├─ course_id, school_id → no-op
│  └─ [HASHED] ip_address_hash, user_agent_hash
├─ Event Data (no-op):
│  ├─ event_timestamp, event_type (page_view/assignment_submit/etc)
│  ├─ resource_id, resource_name, resource_type
│  ├─ duration_seconds, time_on_task (minutes)
│  ├─ interaction_depth, device_type, platform
│  └─ submission_quality_score (0-100)
└─ Derived Flags (no-op):
   ├─ content_interaction_flag, [NEW] effort_level_flag
   └─ _loaded_date, _updated_date

ENTITY: courses (18 attributes)
├─ Identifiers (no-op):
│  ├─ course_id, course_code, school_id
│  └─ [NEW] section_id (A, B, C for same course diff sections)
├─ Course Details (no-op):
│  ├─ course_name, course_description, subject_area
│  ├─ grade_level, course_type (regular/honors/AP/IB/CTE/SPED)
│  ├─ credit_value, term
│  └─ [NEW] class_size, days_per_week, instructional_minutes
└─ Instructor (hashed):
   ├─ teacher_id → hash
   └─ [NEW] section_teacher_id → hash (supports primary/secondary)
```

### 1.3 New Entities for Complete Picture

```sql
-- DISCIPLINE_INCIDENTS (NEW - 18 attributes)
CREATE TABLE stage2b_refined.fact_discipline_incidents (
    incident_key VARCHAR PRIMARY KEY,
    student_key VARCHAR (hashed student_id),
    incident_date DATE,
    incident_time TIME,
    
    -- Incident details
    incident_type VARCHAR,                      -- Class disruption, Fighting, Insubordination, etc.
    incident_code INT,                          -- Aeries discipline code
    severity_level VARCHAR,                     -- Minor, Moderate, Severe, Critical
    assertive_discipline_level INT,             -- 1=Warning, 2=Detention, 3=ISS, 4=OSS, 5=Expulsion
    
    -- Context
    location VARCHAR,                           -- Classroom, Hallway, Cafeteria
    involved_staff VARCHAR (hashed),
    witnessed_by_count INT,
    
    -- Consequence
    consequence_type VARCHAR,                   -- Warning, Detention, Suspension, Expulsion, Restorative
    consequence_date DATE,
    consequence_duration INT,                   -- Days (if suspension)
    follow_up_action VARCHAR,
    
    -- Link to attendance (if suspension)
    linked_to_absence_dates ARRAY<DATE>,
    
    _loaded_at TIMESTAMP,
    _rule_version VARCHAR
);

-- GRADUATION_PROGRESS (NEW - 15 attributes)
CREATE TABLE stage2b_refined.fact_graduation_progress (
    student_key VARCHAR,
    academic_year INT,
    
    credits_earned_to_date FLOAT,
    credits_required_for_graduation FLOAT,
    pct_credits_complete FLOAT,
    on_pace_status VARCHAR,                     -- On-Pace, Slightly Behind, At-Risk
    
    -- By subject (Math, ELA, Science, Social Studies, Electives)
    math_credits_needed INT,
    ell_credits_needed INT,
    science_credits_needed INT,
    social_studies_credits_needed INT,
    
    graduation_date_projected DATE,
    graduation_year_projected INT,
    
    _loaded_at TIMESTAMP
);

-- LANGUAGE_PROFICIENCY (NEW - 10 attributes) [from RFEP data]
CREATE TABLE stage2b_refined.dim_language_proficiency (
    student_key VARCHAR,
    
    english_learner BOOLEAN,
    ell_status VARCHAR,                         -- FEP, LTEL, Monitoring, RFEP
    primary_language VARCHAR,                   -- Spanish, Hmong, Somali, etc.
    years_in_ell_program INT,
    
    most_recent_language_assessment_date DATE,
    most_recent_language_level VARCHAR,        -- K, 1, 2, 3, 4 (proficiency levels)
    
    reclassification_eligible BOOLEAN,
    reclassification_recommended BOOLEAN,
    reclassification_date DATE,
    
    _loaded_at TIMESTAMP
);

-- SPECIAL_EDUCATION_STATUS (NEW - 12 attributes) [from D&F + 504/SPED reports]
CREATE TABLE stage2b_refined.dim_special_education (
    student_key VARCHAR,
    
    special_education_flag BOOLEAN,
    iep_flag BOOLEAN,
    section_504_flag BOOLEAN,
    
    disability_category VARCHAR,                -- Speech, Learning Disabled, Emotional, Autism, OHI, Visual, Deaf/Blind, etc.
    iep_start_date DATE,
    iep_meeting_date DATE,
    iep_review_date DATE,
    
    accommodations_documented BOOLEAN,
    accommodations_text VARCHAR,
    related_services_needed BOOLEAN,
    related_services_text VARCHAR,
    
    _loaded_at TIMESTAMP
);
```

### 1.4 Aeries API Endpoints (FROM REQUIREMENTS SPEC)

**All endpoints implemented via GET requests with parameters:**

```
BASE: http://aeries_server:8000/api/v5

REPORTS CATEGORY:
├─ GET /reports/categories
│  └─ Returns: {categories: [{name, report_routes}]}
│
├─ ATTENDANCE REPORTS:
│  ├─ GET /reports/daily-attendance-summary?schoolCode={code}&date={YYYY-MM-DD}
│  │  └─ Response: {school, date, by_period: [{period, present, absent, tardy}], by_teacher}
│  │
│  ├─ GET /reports/period-absence-summary?schoolCode={code}&startDate={YYYY-MM-DD}&endDate={YYYY-MM-DD}
│  │  └─ Response: {school, period_absences: [{period, teacher, absences_count}]}
│  │
│  ├─ GET /reports/attendance?schoolCode={code}&dateFrom={YYYY-MM-DD}&dateTo={YYYY-MM-DD}
│  │  └─ Response: {students: [{name, present, absent, tardy, excused, unexcused}]}
│  │
│  └─ GET /reports/chronic-absenteeism?schoolCode={code}&minEnrollmentDays={int}&chronicThresholdPct={float}
│     └─ Response: {chronic_absent: [{student, absences, rate, trend}]}
│
├─ GRADE REPORTS:
│  ├─ GET /reports/honor-roll?schoolCode={code}&term={term}&gpaType={weighted|unweighted}&honorRollThreshold={float}&highHonorRollThreshold={float}
│  │  └─ Response: {honor_roll: [{student, gpa, grade_level}], high_honor_roll: [...]}
│  │
│  ├─ GET /reports/d-and-f-report?schoolCode={code}&markingPeriod={period}
│  │  └─ Response: {at_risk: [{student, course, grade, current_gpa}]}
│  │
│  └─ GET /reports/grades?schoolCode={code}&studentId={id}&term={term}
│     └─ Response: {courses: [{name, grade_letter, grade_percent, teacher}]}
│
├─ STUDENT REPORTS:
│  ├─ GET /reports/student-demographics?schoolCode={code}
│  │  └─ Response: {students: [{id, name, grade, demographics...}]}
│  │
│  └─ GET /reports/emergency-cards?schoolCode={code}&gradeLevel={grade}
│     └─ Response: {emergency_cards: [{student, contacts, medical_alerts, special_instructions}]}
│
└─ SCHEDULING REPORTS:
   ├─ GET /reports/master-schedule?schoolCode={code}&term={term}
   │  └─ Response: {sections: [{course, section, teacher, room, enrollment_count}]}
   │
   └─ GET /reports/student-schedules?schoolCode={code}&gradeLevel={grade}
      └─ Response: {schedules: [{student, periods: [{period, course, teacher, room}]}]}
```

**Key Query Parameters:**
- `schoolCode`: School ID (from enrollment)
- `dateFrom`, `dateTo`: Date ranges (ISO 8601)
- `term`: Term identifier (e.g., "2025Q1", "2025S1")
- `studentId`: Specific student (optional)
- `gradeLevel`: Filter by grade (9, 10, 11, 12, K-8)
- `markingPeriod`: Grading period identifier

---

## Part 2: SQL Implementation (Specific Tables)

### 2.1 Stage 2B Refined Tables (Privacy-Aware)

**All tables include:**
- `_loaded_at TIMESTAMP` - When data entered Stage 2
- `_updated_at TIMESTAMP` - Last modification
- `_rule_version VARCHAR` - Metadata version applied for reproducibility

```sql
-- TABLE 1: dim_student_demographics (Enhanced with D&F + Demographic reports)
CREATE TABLE stage2b_refined.dim_student_demographics (
    student_key VARCHAR PRIMARY KEY,             -- Deterministic hash of student_id
    student_id_hash VARCHAR UNIQUE,              -- For lookup table
    
    -- Basic demographics (no-op - not sensitive for aggregation)
    grade_level INT,
    gender VARCHAR,
    ethnicity VARCHAR,                           -- From Demographic report
    race_ethnicity_rollup VARCHAR,               -- Simplified: White, Black, Hispanic, Asian, Other
    cohort_year INT,
    
    -- Language status (from RFEP + system flags)
    english_learner BOOLEAN,
    ell_status VARCHAR,                          -- FEP, LTEL, Monitoring, RFEP (from RFEP image/manual data)
    primary_language VARCHAR,                    -- Spanish, Hmong, Somali, Vietnamese, etc.
    years_in_ell_program INT,
    
    -- Special education status (from D&F report + system flags)
    special_education BOOLEAN,
    iep_flag BOOLEAN,                            -- Has IEP
    section_504_flag BOOLEAN,                    -- Has 504 plan
    disability_category VARCHAR,                 -- From D&F: Speech, LD, Emotional, Autism, OHI, etc.
    
    -- Socioeconomic status
    economically_disadvantaged BOOLEAN,
    free_reduced_lunch VARCHAR,                  -- Free, Reduced, Full-pay
    
    -- Housing/Family status
    homeless_flag BOOLEAN,
    foster_care_flag BOOLEAN,
    
    -- Program enrollment
    program_enrollment VARCHAR,                  -- AP, Honors, Remedial, STEM, Bilingual, etc.
    program_start_date DATE,
    program_end_date DATE,
    
    -- Entry/Exit
    entry_date DATE,
    exit_date DATE,
    withdrawal_reason VARCHAR,                   -- Graduated, Transferred, Moved, Dropout
    
    -- School/District context
    school_id VARCHAR,
    district_id VARCHAR,
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP,
    _rule_version VARCHAR
);

-- TABLE 2: fact_attendance_daily (Detailed daily records)
CREATE TABLE stage2b_refined.fact_attendance_daily (
    attendance_key VARCHAR PRIMARY KEY,          -- CONCAT(student_key, date, period)
    student_key VARCHAR,
    school_id VARCHAR,
    course_id VARCHAR,
    period_or_class VARCHAR,
    
    attendance_date DATE,
    
    -- Presence status
    is_present BOOLEAN,
    tardy_flag BOOLEAN,
    early_departure_flag BOOLEAN,
    
    -- Absence classification
    absence_type VARCHAR,                        -- excused, unexcused, medical, OSS, ISS, field_trip
    absence_reason VARCHAR,                      -- illness, appointment, family_emergency, truancy
    
    -- Timing details
    checkin_time TIME,
    checkout_time TIME,
    partial_absence_duration INT,                -- Minutes (if partial)
    
    -- Teacher tracking
    teacher_id_hash VARCHAR,
    
    -- Binary flags for aggregation
    is_excused_absence INT,                      -- 1 or 0
    is_unexcused_absence INT,
    is_tardy_incident INT,
    
    -- Computed flags
    chronic_absence_accumulating BOOLEAN,        -- Contributes to chronic definition
    attendance_pattern VARCHAR,                  -- improving, declining, stable, at_risk
    
    -- Linked discipline (if applicable)
    discipline_incident_same_day BOOLEAN,
    
    -- Follow-up
    parent_notification_sent BOOLEAN,
    makeup_assignment_required BOOLEAN,
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP,
    _rule_version VARCHAR
    
    -- UNIQUE INDEX on (student_key, attendance_date, period_or_class) for data quality
);

-- TABLE 3: agg_attendance_windows (Pre-aggregated for fast queries)
CREATE TABLE stage2b_refined.agg_attendance_windows (
    student_key VARCHAR,
    window_start_date DATE,
    window_end_date DATE,
    window_type VARCHAR,                         -- 30d, 60d, 90d, term
    
    -- Enrollment
    days_enrolled INT,
    school_days_count INT,                       -- Calendar school days
    
    -- Attendance counts
    days_present INT,
    days_absent_total INT,
    days_absent_excused INT,
    days_absent_unexcused INT,
    days_tardy INT,
    days_early_departure INT,
    
    -- Rates
    attendance_rate FLOAT,
    absence_rate FLOAT,
    unexcused_absence_rate FLOAT,
    excused_absence_rate FLOAT,
    tardy_rate FLOAT,
    
    -- Flags
    chronic_absence_flag BOOLEAN,                -- unexcused_absence_rate > 0.10
    perfect_attendance_flag BOOLEAN,
    
    -- Pattern analysis
    consecutive_absence_max INT,
    pattern_direction VARCHAR,                   -- improving, declining, stable
    
    -- Discipline correlation
    discipline_incidents_in_window INT,
    days_with_both_absence_and_incident INT,
    absence_discipline_correlation_score FLOAT,  -- 0-1
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP
    
    -- PRIMARY KEY (student_key, window_start_date, window_type)
);

-- TABLE 4: fact_discipline_incidents (Incident-level detail)
CREATE TABLE stage2b_refined.fact_discipline_incidents (
    incident_key VARCHAR PRIMARY KEY,
    student_key VARCHAR,
    school_id VARCHAR,
    incident_date DATE,
    incident_time TIME,
    
    -- Incident classification
    incident_type VARCHAR,                       -- Class disruption, Fighting, Insubordination, etc.
    incident_code INT,                           -- Aeries system code
    severity_level VARCHAR,                      -- Minor, Moderate, Severe, Critical
    
    -- Escalation progression
    assertive_discipline_level INT,              -- 1=Warning, 2=Detention, 3=ISS, 4=OSS, 5=Expulsion
    is_suspension BOOLEAN,
    is_expulsion BOOLEAN,
    
    -- Context
    location VARCHAR,                            -- Classroom, Hallway, Cafeteria, etc.
    involved_staff_id_hash VARCHAR,
    witnessed_by_count INT,
    
    -- Consequence
    consequence_type VARCHAR,                    -- Warning, Detention, Suspension, Expulsion, Restorative
    consequence_date DATE,
    consequence_duration INT,                    -- Days (if suspension)
    consequence_end_date DATE,
    
    -- Follow-up
    follow_up_action VARCHAR,                    -- Counselor referral, Parent contact, Restorative conference
    follow_up_completed BOOLEAN,
    follow_up_date DATE,
    
    -- Linked absence (if student suspended)
    linked_to_absence_dates ARRAY<DATE>,
    
    -- Pattern indicators
    indicates_trauma_signal BOOLEAN,
    indicates_peer_conflict BOOLEAN,
    indicates_adult_conflict BOOLEAN,
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP,
    _rule_version VARCHAR
);

-- TABLE 5: agg_discipline_windows (Pre-aggregated)
CREATE TABLE stage2b_refined.agg_discipline_windows (
    student_key VARCHAR,
    window_start_date DATE,
    window_end_date DATE,
    window_type VARCHAR,                         -- 30d, 60d, 90d, term
    
    -- Incident counts
    incident_count INT,
    incident_severity_min VARCHAR,               -- Most severe level observed
    incident_severity_max VARCHAR,
    
    -- Escalation tracking
    level_1_warnings INT,
    level_2_detentions INT,
    level_3_in_school_suspension INT,
    level_4_out_of_school_suspension INT,
    level_5_expulsion BOOLEAN,
    
    -- Indicators
    trauma_signal_flag BOOLEAN,
    peer_conflict_flag BOOLEAN,
    adult_conflict_flag BOOLEAN,
    escalating_pattern BOOLEAN,
    
    -- Trend
    incident_trend VARCHAR,                      -- increasing, stable, decreasing
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP
);

-- TABLE 6: fact_academic_performance (Grades + assessments)
CREATE TABLE stage2b_refined.fact_academic_performance (
    student_key VARCHAR,
    school_id VARCHAR,
    course_id VARCHAR,
    section_id VARCHAR,                          -- Links to specific class (A, B, C)
    term VARCHAR,
    
    -- Grade information
    grade_letter VARCHAR,                        -- A, B, C, D, F
    grade_numeric FLOAT,                         -- 4.0, 3.0, 2.0, 1.0, 0.0
    grade_percent FLOAT,
    
    -- Class context
    class_size INT,
    class_average_percent FLOAT,
    student_grade_vs_class_avg FLOAT,            -- Relative position
    
    -- Standards-based (if available)
    mastery_level VARCHAR,                       -- novice, developing, proficient, advanced
    standards_met_count INT,
    standards_total_count INT,
    
    -- Teacher info
    teacher_id_hash VARCHAR,
    
    -- On-pace analysis
    credits_earned_this_course FLOAT,
    on_pace_for_graduation BOOLEAN,
    graduation_impact INT,                       -- Years until graduation affected
    
    -- Flags
    at_risk_grade BOOLEAN,                       -- D or F
    grade_improved BOOLEAN,
    grade_declined BOOLEAN,
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP,
    _rule_version VARCHAR
);

-- TABLE 7: fact_class_effectiveness (Section-level aggregates)
CREATE TABLE stage2b_refined.fact_class_effectiveness (
    section_key VARCHAR PRIMARY KEY,
    school_id VARCHAR,
    course_id VARCHAR,
    section_id VARCHAR,                          -- A, B, C designator
    term VARCHAR,
    
    teacher_id_hash VARCHAR,
    class_size INT,
    
    -- Grade distribution
    avg_grade_numeric FLOAT,
    pct_passed FLOAT,                            -- % with C or better
    pct_a_b_grades FLOAT,
    median_grade_numeric FLOAT,
    grade_std_dev FLOAT,
    
    -- Subgroup effectiveness (from Demographic report)
    pct_passed_ell FLOAT,
    pct_passed_sped FLOAT,
    pct_passed_frl FLOAT,
    pct_passed_by_race JSONB,                    -- {'White': 85.0, 'Black': 72.0}
    
    -- Attendance impact
    avg_class_attendance_rate FLOAT,
    
    -- Engagement
    avg_assignment_completion_rate FLOAT,
    
    -- Section comparison
    rank_by_pass_rate INT,                       -- Within same course/term
    rank_by_avg_grade INT,
    grade_diff_from_section_avg FLOAT,           -- vs. other sections of same course
    
    _loaded_at TIMESTAMP,
    _updated_at TIMESTAMP
);
```

### 2.2 Stage 3 Published Views (Analytics-Ready)

```sql
-- VIEW 1: Chronic Absenteeism Risk Profile
CREATE OR REPLACE VIEW stage3_published.v_chronic_absenteeism_risk AS
SELECT
    d.student_key,
    d.grade_level,
    d.school_id,
    d.race_ethnicity,
    d.english_learner,
    d.special_education,
    d.free_reduced_lunch,
    d.homeless_flag,
    
    -- 30-day metrics
    a30.attendance_rate AS attendance_rate_30d,
    a30.unexcused_absence_rate AS unexcused_absence_rate_30d,
    a30.discipline_incidents_in_window AS discipline_incidents_30d,
    a30.absence_discipline_correlation_score,
    
    -- 90-day trend
    a90.attendance_rate AS attendance_rate_90d,
    a90.pattern_direction AS attendance_trend_90d,
    
    -- Risk scoring
    CASE 
        WHEN a30.unexcused_absence_rate > 0.10 THEN 1 ELSE 0
    END AS chronic_absence_flag,
    
    -- Composite risk score (0-100)
    ROUND(
        (1.0 - a30.attendance_rate) * 40.0 +
        (a30.unexcused_absence_rate / 0.15 * 20.0) +
        (LEAST(a30.discipline_incidents_in_window * 5, 30)) +
        (CASE WHEN a90.pattern_direction = 'declining' THEN 20 ELSE 0 END) +
        (LEAST(a30.absence_discipline_correlation_score * 10, 10)),
        1
    ) AS chronic_absenteeism_risk_score
    
FROM stage2b_refined.dim_student_demographics d
LEFT JOIN stage2b_refined.agg_attendance_windows a30 
    ON d.student_key = a30.student_key 
    AND a30.window_type = '30d'
    AND a30.window_start_date = CURRENT_DATE - 30
LEFT JOIN stage2b_refined.agg_attendance_windows a90 
    ON d.student_key = a90.student_key 
    AND a90.window_type = '90d'
    AND a90.window_start_date = CURRENT_DATE - 90
ORDER BY chronic_absenteeism_risk_score DESC;

-- VIEW 2: Student Well-Being Risk (Multi-domain)
CREATE OR REPLACE VIEW stage3_published.v_wellbeing_risk_profiles AS
WITH risk_domains AS (
    SELECT
        d.student_key,
        d.grade_level,
        d.school_id,
        
        -- Attendance risk (0-100)
        ROUND(
            (1.0 - COALESCE(a.attendance_rate, 0.95)) * 40.0,
            1
        ) AS attendance_risk_score,
        
        -- Discipline risk (0-100)
        ROUND(
            LEAST(COALESCE(dis.incident_count, 0) * 10, 100.0),
            1
        ) AS discipline_risk_score,
        
        -- Academic risk (0-100)
        ROUND(
            CASE 
                WHEN COALESCE(acad.grade_numeric, 2.0) < 2.0 THEN 100
                WHEN COALESCE(acad.grade_numeric, 2.0) < 2.5 THEN 70
                WHEN COALESCE(acad.grade_numeric, 2.0) < 3.0 THEN 40
                ELSE 10
            END,
            1
        ) AS academic_risk_score,
        
        -- Count domains at high risk
        SUM(
            CASE 
                WHEN (1.0 - COALESCE(a.attendance_rate, 0.95)) * 40.0 > 60 THEN 1 ELSE 0
            END +
            CASE 
                WHEN LEAST(COALESCE(dis.incident_count, 0) * 10, 100.0) > 60 THEN 1 ELSE 0
            END +
            CASE 
                WHEN COALESCE(acad.grade_numeric, 2.0) < 2.5 THEN 1 ELSE 0
            END
        ) AS high_risk_domain_count
        
    FROM stage2b_refined.dim_student_demographics d
    LEFT JOIN stage2b_refined.agg_attendance_windows a 
        ON d.student_key = a.student_key AND a.window_type = '30d'
    LEFT JOIN stage2b_refined.agg_discipline_windows dis 
        ON d.student_key = dis.student_key AND dis.window_type = '30d'
    LEFT JOIN stage2b_refined.fact_academic_performance acad 
        ON d.student_key = acad.student_key
)

SELECT
    student_key,
    grade_level,
    school_id,
    attendance_risk_score,
    discipline_risk_score,
    academic_risk_score,
    high_risk_domain_count,
    
    -- Composite well-being risk score
    ROUND(
        (attendance_risk_score + discipline_risk_score + academic_risk_score) / 3.0 *
        (1.0 + (high_risk_domain_count - 1) * 0.25),  -- Compound if multi-domain
        1
    ) AS wellbeing_risk_score,
    
    -- Risk level classification
    CASE 
        WHEN (attendance_risk_score + discipline_risk_score + academic_risk_score) / 3.0 * 
             (1.0 + (high_risk_domain_count - 1) * 0.25) <= 30 THEN 'Low'
        WHEN (attendance_risk_score + discipline_risk_score + academic_risk_score) / 3.0 * 
             (1.0 + (high_risk_domain_count - 1) * 0.25) <= 60 THEN 'Moderate'
        WHEN (attendance_risk_score + discipline_risk_score + academic_risk_score) / 3.0 * 
             (1.0 + (high_risk_domain_count - 1) * 0.25) <= 80 THEN 'High'
        ELSE 'Critical'
    END AS wellbeing_risk_level,
    
    -- Primary concern
    CASE 
        WHEN high_risk_domain_count >= 2 THEN 'Multi-factor'
        WHEN attendance_risk_score > discipline_risk_score AND attendance_risk_score > academic_risk_score THEN 'Attendance'
        WHEN discipline_risk_score > academic_risk_score THEN 'Behavior'
        ELSE 'Academic'
    END AS primary_concern

FROM risk_domains
ORDER BY wellbeing_risk_score DESC;

-- VIEW 3: Equity Analysis - Outcomes by Demographic
CREATE OR REPLACE VIEW stage3_published.v_equity_outcomes_by_demographics AS
SELECT
    d.race_ethnicity,
    d.english_learner,
    d.special_education,
    d.free_reduced_lunch,
    
    COUNT(*) AS cohort_size,
    
    -- Attendance outcomes
    ROUND(100.0 * SUM(CASE WHEN a.attendance_rate > 0.90 THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 1) AS pct_good_attendance,
    
    -- Discipline outcomes
    ROUND(100.0 * SUM(CASE WHEN dis.incident_count IS NULL OR dis.incident_count = 0 THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 1) AS pct_no_discipline,
    
    -- Academic outcomes
    ROUND(AVG(acad.grade_numeric), 2) AS avg_gpa,
    ROUND(100.0 * SUM(CASE WHEN acad.grade_numeric >= 2.5 THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 1) AS pct_gpa_2_5_plus,
    
    -- Graduation outcomes (on-pace)
    ROUND(100.0 * SUM(CASE WHEN grad.on_pace_for_graduation THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(*), 0), 1) AS pct_on_pace_graduation
    
FROM stage2b_refined.dim_student_demographics d
LEFT JOIN stage2b_refined.agg_attendance_windows a 
    ON d.student_key = a.student_key AND a.window_type = 'term'
LEFT JOIN stage2b_refined.agg_discipline_windows dis 
    ON d.student_key = dis.student_key AND dis.window_type = 'term'
LEFT JOIN stage2b_refined.fact_academic_performance acad 
    ON d.student_key = acad.student_key
LEFT JOIN stage2b_refined.fact_graduation_progress grad 
    ON d.student_key = grad.student_key AND grad.academic_year = EXTRACT(YEAR FROM CURRENT_DATE)

GROUP BY 1, 2, 3, 4
ORDER BY race_ethnicity, english_learner, special_education;

-- VIEW 4: Class Effectiveness Comparison (Same course, different sections)
CREATE OR REPLACE VIEW stage3_published.v_class_section_comparison AS
SELECT
    course_id,
    section_id,
    teacher_id_hash,
    
    -- Effectiveness metrics
    avg_grade_numeric,
    pct_passed,
    pct_a_b_grades,
    
    -- Comparison to same course
    ROUND(
        (SELECT AVG(avg_grade_numeric) 
        FROM stage2b_refined.fact_class_effectiveness ace2 
        WHERE ace2.course_id = ace.course_id AND ace2.term = ace.term),
        2
    ) AS course_avg_grade,
    
    ROUND(
        avg_grade_numeric - 
        (SELECT AVG(avg_grade_numeric) 
        FROM stage2b_refined.fact_class_effectiveness ace2 
        WHERE ace2.course_id = ace.course_id AND ace2.term = ace.term),
        2
    ) AS grade_diff_from_course_avg,
    
    -- Equity: Subgroup effectiveness
    pct_passed_ell,
    pct_passed_sped,
    pct_passed_frl,
    
    -- Ranking
    RANK() OVER (PARTITION BY course_id, term ORDER BY pct_passed DESC) AS pass_rate_rank,
    RANK() OVER (PARTITION BY course_id, term ORDER BY avg_grade_numeric DESC) AS grade_rank

FROM stage2b_refined.fact_class_effectiveness ace
WHERE term = DATE_FORMAT(CURRENT_DATE, '%YQ1')  -- Current term
ORDER BY course_id, pass_rate_rank;

-- VIEW 5: Performance Correlations
CREATE OR REPLACE VIEW stage3_published.v_performance_correlations AS
SELECT
    'Attendance ↔ GPA' AS correlation_pair,
    ROUND(
        CORR(a.attendance_rate, acad.grade_numeric),
        3
    ) AS correlation_coefficient,
    'Positive' AS expected_direction
FROM stage2b_refined.agg_attendance_windows a
JOIN stage2b_refined.fact_academic_performance acad 
    ON a.student_key = acad.student_key
WHERE a.window_type = 'term'

UNION ALL

SELECT
    'Discipline ↔ Grades',
    ROUND(
        CORR(
            CASE WHEN dis.incident_count > 0 THEN dis.incident_count ELSE 0 END * -1,
            acad.grade_numeric
        ),
        3
    ),
    'Negative'
FROM stage2b_refined.agg_discipline_windows dis
JOIN stage2b_refined.fact_academic_performance acad 
    ON dis.student_key = acad.student_key
WHERE dis.window_type = 'term'

UNION ALL

SELECT
    'Attendance ↔ Graduation',
    ROUND(
        CORR(
            a.attendance_rate,
            CASE WHEN grad.on_pace_for_graduation THEN 1.0 ELSE 0.0 END
        ),
        3
    ),
    'Positive'
FROM stage2b_refined.agg_attendance_windows a
LEFT JOIN stage2b_refined.fact_graduation_progress grad 
    ON a.student_key = grad.student_key
WHERE a.window_type = 'term';
```

---

## Part 3: Dashboard Specifications (5 Dashboards)

### Dashboard 1: Chronic Absenteeism Overview
**Source**: v_chronic_absenteeism_risk
**Segments**: School, Grade, Demographic (Race, ELL, SPED, SES)

| Component | Query | Interaction |
|-----------|-------|-------------|
| **KPI Cards** | Chronic absence rate (%), incident rate, avg risk score | Filter by demographic |
| **Trend Line** | Attendance rate 30/60/90d vs incident count | Date range selector |
| **Bar Chart** | Students at-risk by grade | Grade level drill-down |
| **Scatter Plot** | Attendance vs discipline incidents | Color: demographic, Size: risk score |
| **Risk Table** | Top 30 at-risk students | Sort: risk score, drill-down to detail |
| **Heatmap** | Absence rate by day-of-week + grade | Highlight patterns |

### Dashboard 2: Student Well-Being Risk Profiles
**Source**: v_wellbeing_risk_profiles
**Primary Users**: Counselors, administrators

| Component | Query | Purpose |
|-----------|-------|---------|
| **Risk Distribution** | Count by Low/Moderate/High/Critical | Quick snapshot |
| **Drill-down Table** | All students with risk level, score, drivers | Identify intervention candidates |
| **Multi-Domain Matrix** | Attendance risk vs Discipline vs Academic | Visualize interaction effects |
| **Intervention Tracking** | Pre/post scores after referral | Measure impact |
| **Automated Alerts** | New High/Critical risk students this week | Early notification |

### Dashboard 3: Equity & Demographic Analysis
**Source**: v_equity_outcomes_by_demographics
**Focus**: Identify outcome gaps

| Component | Source | Metric |
|-----------|--------|--------|
| **Comparison Table** | Demographic cohorts | Attendance, discipline, GPA, graduation rates |
| **Gap Visualization** | vs. district average | Show which groups underperforming |
| **Trend Over Time** | Historical by demographic | Improving or worsening? |
| **Drill-down** | By race, ELL, SPED, SES, housing | Combine multiple dimensions |
| **Disparity Flag** | > 10% gap detected | Requires investigation |

### Dashboard 4: Class Effectiveness Comparison
**Source**: v_class_section_comparison
**Focus**: Same course, different sections

| Component | Query | Shows |
|-----------|-------|-------|
| **Section Rankings** | Pass rate rank 1-N | Best/worst performing sections |
| **Side-by-Side Metrics** | Avg grade, pass rate, attendance | Direct section comparison |
| **Subgroup Breakdown** | ELL, SPED, FRL pass rates by section | Which sections support subgroups? |
| **Teacher Profile** | Aggregated across courses | Instructor effectiveness pattern |
| **Grade Distribution** | Histogram by section | Grading consistency |

### Dashboard 5: Performance Correlations
**Source**: v_performance_correlations
**Purpose**: Understand what drives outcomes

| Component | Visualization | Detail |
|-----------|---------------|--------|
| **Correlation Matrix** | Heatmap | All pairwise correlations |
| **By Demographic** | Separate correlation for each group | Does relationship differ? |
| **Scatter Plots** | Attendance vs GPA | Shows data distribution |
| **Statistical Significance** | p-values, confidence intervals | Is correlation real? |
| **Causal Notes** | Document non-causal correlations | Avoid misinterpretation |

---

## Part 4: Data Integration Pipeline (ETL/ELT)

### Stage 1 Ingest (from Aeries API + Excel imports)

```python
# Pipeline 1: Aeries API → Stage 1 (Daily)
from oss_framework import AeriesClient, DataPipeline

class AeriesIngestPipeline:
    def __init__(self, api_key, base_url):
        self.client = AeriesClient(api_key, base_url)
        self.pipeline = DataPipeline('sis_ingest', 'stage1_raw')
    
    def ingest_students(self):
        """GET /reports/student-demographics"""
        data = self.client.get('/reports/student-demographics')
        self.pipeline.load(data, 'raw_students', write_mode='merge')
    
    def ingest_attendance(self):
        """GET /reports/attendance (daily)"""
        data = self.client.get('/reports/attendance', 
            date_from=(today - 1).isoformat(),
            date_to=today.isoformat()
        )
        self.pipeline.load(data, 'raw_attendance', write_mode='append')
    
    def ingest_grades(self):
        """GET /reports/grades (by student + term)"""
        data = self.client.get('/reports/grades',
            term=current_term()
        )
        self.pipeline.load(data, 'raw_grades', write_mode='merge')
    
    def ingest_discipline(self):
        """GET /api/v5/discipline (if available)"""
        data = self.client.get('/discipline',
            date_from=(today - 1).isoformat(),
            date_to=today.isoformat()
        )
        self.pipeline.load(data, 'raw_discipline', write_mode='append')

# Pipeline 2: Excel imports (Weekly/Manual)
class ExcelImportPipeline:
    def import_d_and_f_report(self, file_path):
        """D and F w_504 SE.xlsx → enriched students table"""
        df = pd.read_excel(file_path)
        # Extract: student_id, 504_flag, IEP_status, disability_category
        enriched = df[['StudentID', '504Status', 'IEPStatus', 'DisabilityCategory']]
        self.pipeline.load(enriched, 'raw_d_and_f_import', write_mode='merge')
    
    def import_demographic_report(self, file_path):
        """Demographic Data by Course 24_25.xlsx → enriched enrollment"""
        df = pd.read_excel(file_path)
        # Extract: student_id, course_id, section, race_ethnicity
        enriched = df[['StudentID', 'CourseID', 'Section', 'RaceEthnicity']]
        self.pipeline.load(enriched, 'raw_demographic_import', write_mode='merge')
    
    def import_rfep_data(self, file_path_or_manual_entry):
        """RFEP.png → language proficiency tracking"""
        # Manual entry or OCR-extracted data
        data = {
            'StudentID': [...],
            'ELLStatus': [...],
            'LanguageLevel': [...]
        }
        self.pipeline.load(data, 'raw_ell_import', write_mode='merge')
```

### Stage 2 Transform (dbt models)

```yaml
# dbt/models/staging/stg_students.sql
{{ config(materialized='table') }}

WITH source AS (
    SELECT *
    FROM read_parquet('{{ var("stage1_path") }}/raw_students/**/*.parquet')
),

joined_enrichments AS (
    SELECT
        s.*,
        -- Join D&F import
        daf.504_flag,
        daf.iep_status,
        daf.disability_category,
        -- Join demographic import
        dem.race_ethnicity,
        dem.primary_language,
        -- Join RFEP import
        ell.ell_status,
        ell.language_level,
        ell.years_in_program
    FROM source s
    LEFT JOIN read_parquet('{{ var("stage1_path") }}/raw_d_and_f_import/**/*.parquet') daf
        ON s.student_id = daf.student_id
    LEFT JOIN read_parquet('{{ var("stage1_path") }}/raw_demographic_import/**/*.parquet') dem
        ON s.student_id = dem.student_id
    LEFT JOIN read_parquet('{{ var("stage1_path") }}/raw_ell_import/**/*.parquet') ell
        ON s.student_id = ell.student_id
),

validated AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['student_id']) }} AS student_key,
        student_id,
        grade_level,
        gender,
        COALESCE(race_ethnicity, 'Unknown') AS race_ethnicity,
        english_learner,
        COALESCE(ell_status, 'Unknown') AS ell_status,
        special_education,
        COALESCE(504_flag, FALSE) AS 504_flag,
        COALESCE(iep_status, FALSE) AS iep_flag,
        COALESCE(disability_category, 'None') AS disability_category,
        enrollment_status,
        CURRENT_TIMESTAMP AS _loaded_at
    FROM joined_enrichments
    WHERE student_id IS NOT NULL
        AND enrollment_status = 'Active'
)

SELECT * FROM validated
```

---

## Part 5: Risk Scoring Implementation

### Algorithm 1: Chronic Absenteeism Risk Score

```python
def calculate_chronic_absence_risk(student_data):
    """
    Components (0-100 scale):
    - Attendance rate: 0-40 points
    - Unexcused %: 0-20 points
    - Discipline count: 0-30 points
    - Trend: 0-20 points
    - Correlation: 0-10 points
    """
    score = 0
    
    # Attendance penalty
    if student_data['attendance_rate_30d'] < 0.95:
        score += (0.95 - student_data['attendance_rate_30d']) / 0.95 * 40
    
    # Unexcused absence penalty
    if student_data['unexcused_absence_rate_30d'] > 0.05:
        score += min(student_data['unexcused_absence_rate_30d'] / 0.15 * 20, 20)
    
    # Discipline multiplier
    score += min(student_data['discipline_incidents_30d'] * 5, 30)
    
    # Trend acceleration
    if student_data['attendance_trend_90d'] < 0:  # Declining
        score += 20
    
    # Absence-discipline correlation
    if student_data['absence_discipline_correlation_score'] > 0.5:
        score += student_data['absence_discipline_correlation_score'] * 10
    
    return min(max(score, 0), 100)
```

### Algorithm 2: Well-Being Risk Score

```python
def calculate_wellbeing_risk(student_data):
    """
    Multi-domain composite with interaction effects
    """
    # Individual domain scores (0-100)
    attendance_score = calculate_attendance_risk(student_data)
    discipline_score = calculate_discipline_risk(student_data)
    academic_score = calculate_academic_risk(student_data)
    
    # Count high-risk domains
    high_risk_domains = sum([
        attendance_score > 60,
        discipline_score > 60,
        academic_score > 60
    ])
    
    # Composite with interaction multiplier
    base_score = (attendance_score + discipline_score + academic_score) / 3
    if high_risk_domains >= 2:
        # Compound effect: each additional domain = 25% increase
        multiplier = 1 + (high_risk_domains - 1) * 0.25
        composite_score = base_score * multiplier
    else:
        composite_score = base_score
    
    # Trend acceleration
    if any([
        student_data.get('attendance_declining'),
        student_data.get('discipline_increasing'),
        student_data.get('grade_declining')
    ]):
        composite_score *= 1.2  # 20% boost
    
    # Recent critical incident
    if student_data.get('days_since_critical_incident', 31) < 30:
        composite_score = min(composite_score * 1.3, 100)
    
    return min(max(composite_score, 0), 100)
```

---

## Part 6: Data Quality & Validation

**Tier 1: Schema Validation** (dbt tests)
```yaml
- unique: [student_id, attendance_date]
- not_null: [student_id, school_id, attendance_date]
- relationships: [student_id → students.student_id]
```

**Tier 2: Domain Validation**
```
- attendance_rate: 0-1
- unexcused_absence_count: 0-max_school_days
- discipline_incident_code: valid codes only
```

**Tier 3: Cross-System Coherence**
```
- If absent (ATT), should not have LMS login
- If ISS/OSS (discipline), attendance should show suspension
- If grade D/F, should flag academic_risk_flag
```

---

## Part 7: Implementation Timeline

### Week 1-2: Data Foundation
- [ ] Set up Aeries API integration (authentication, rate limiting)
- [ ] Configure Stage 1 landing zone
- [ ] Create raw_students, raw_attendance, raw_grades tables
- [ ] Import D&F, Demographic, RFEP Excel data

### Week 3-4: Feature Engineering
- [ ] Build dbt models for Stage 2 (stg_students, stg_attendance, stg_academic_records)
- [ ] Implement attendance windows (30/60/90d)
- [ ] Create discipline_incidents table
- [ ] Calculate risk scores (chronic absence, discipline)

### Week 5-6: Integrated Models
- [ ] Build wellbeing_risk_profiles view
- [ ] Create equity_outcomes_by_demographics view
- [ ] Implement class_effectiveness analysis
- [ ] Calculate correlations

### Week 7-8: Dashboards
- [ ] Build 5 Metabase/BI dashboards
- [ ] User testing with counselors
- [ ] Superintendent demo
- [ ] Documentation

---

## Part 8: Success Criteria

✅ **Data Quality**
- 100% student records have demographic data
- Attendance completeness > 99%
- Discipline linkage > 95%
- Cross-system coherence > 90%

✅ **Analytical Rigor**
- All correlations with p-value significance
- Fairness: No demographic disparity > 10% without explanation
- Risk models cross-validated

✅ **Adoption**
- Used by >80% of counselors weekly
- Superintendent presentations monthly
- Documented interventions with outcomes tracking

---

## QUESTIONS FOR YOU (CLARIFICATION)

1. **Aeries Access**: Do you have API key + endpoint? Or database-level access?
2. **Excel Frequency**: Are D&F, Demographic, RFEP updated weekly/monthly/on-demand?
3. **Priority Reports**: Which report matters most first? (Chronic absenteeism, well-being, equity?)
4. **Dashboard Users**: Who accesses? (Counselors, teachers, principals, superintendent?)
5. **Data Retention**: How long retain student records? (FERPA compliance question)

---

**READY TO BUILD**: All specifications complete. Awaiting approval + clarification on 5 questions above.
