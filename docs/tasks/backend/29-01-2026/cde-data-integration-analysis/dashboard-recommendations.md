# Dashboard Recommendations: CDE Data Integration

**Document Version**: 1.0  
**Date**: 2026-01-29  
**Status**: Draft for Approval

---

## Executive Summary

This document recommends **5 new Metabase dashboards** to visualize the California Department of Education (CDE) data integrated into the OSS Framework. These dashboards will provide district leaders with state benchmarking, comparative analytics, and accountability tracking capabilities not currently available with internal data alone.

**Key Dashboards**:
1. **Staff Insights Dashboard** - Workforce demographics, diversity, and retention
2. **Academic Performance & Benchmarking Dashboard** - State test scores with Dashboard colors
3. **Post-Secondary Outcomes Dashboard** - College-going rates and CTE completion
4. **State Benchmarking & Comparisons Dashboard** - Percentile rankings vs. similar schools
5. **Multi-Year Trends Dashboard** - 8-year historical analysis and growth trajectories

**Total Implementation**: ~150 hours across dashboard design, SQL development, and user training

---

## Current Dashboard Landscape

### Existing Dashboards (5)
1. **Chronic Absenteeism Risk** - Student-level attendance tracking
2. **Wellbeing Risk Profiles** - Multi-domain risk assessment
3. **Equity Outcomes by Demographics** - Achievement gap analysis
4. **Class Section Comparison** - Teacher effectiveness
5. **Performance Correlations** - Cross-domain relationships

### Gaps Addressed by CDE Data
- ❌ **No state-level benchmarking** (how do we compare to state/county?)
- ❌ **No standardized test scores** (SBAC/CAASPP)
- ❌ **No staff demographics** (workforce diversity)
- ❌ **No post-secondary outcomes** (college-going rates)
- ❌ **No Dashboard color tracking** (state accountability status)
- ❌ **No multi-year state trends** (8+ years historical data)

---

## Dashboard 1: Staff Insights Dashboard

### Purpose
Provide HR and district leadership with comprehensive workforce analytics: demographics, diversity, experience levels, education credentials, and student-to-staff ratios.

### Target Users
- **Primary**: Superintendent, HR Director, School Board
- **Secondary**: Principals (school-level metrics)

### Data Sources
- `mart_cde__staff_demographics` (race/ethnicity by role)
- `mart_cde__staff_education` (credential levels)
- `mart_cde__staff_experience` (years of service)
- `mart_cde__staff_ratios` (student-to-teacher, student-to-counselor)
- `dim_school_cds_mapping` (school names)

### Key Metrics

| Metric | Definition | SQL Source |
|--------|-----------|------------|
| **Teacher Diversity Index** | Percentage of teachers from underrepresented groups | `SUM(CASE WHEN ethnicity IN ('Hispanic', 'Black', 'Asian', 'Pacific Islander', 'Native American') THEN 1 END) / COUNT(*)` |
| **Average Years Experience** | Mean years of service by school/district | `AVG(years_experience)` |
| **Advanced Degree Rate** | % teachers with Master's or Doctorate | `SUM(CASE WHEN education_level IN ('Masters', 'Doctorate') THEN 1 END) / COUNT(*)` |
| **Student-to-Counselor Ratio** | Students per counselor | `total_students / total_counselors` |
| **Teacher Turnover Rate** | Year-over-year change in teacher count | `(teachers_current_year - teachers_prior_year) / teachers_prior_year` |

### Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Staff Insights Dashboard          [School Filter ▼] [Year ▼]  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Total      │  │  Teacher    │  │  Advanced   │            │
│  │  Teachers   │  │  Diversity  │  │  Degree     │            │
│  │     342     │  │    38.2%    │  │  Rate 62%   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Staff Demographics by Role (Bar Chart)                  │  │
│  │  - Teachers by ethnicity (stacked bar)                   │  │
│  │  - Administrators, Counselors, Support staff             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  Years of Experience    │  │  Student-to-Staff Ratios │    │
│  │  (Distribution Histogram)│  │  (Comparison Table)      │    │
│  │  0-5 yrs:  120 (35%)    │  │  Student-to-Teacher: 22  │    │
│  │  6-10 yrs:  98 (29%)    │  │  Student-to-Counselor: 450│   │
│  │  11-20 yrs: 84 (25%)    │  │  Student-to-Admin: 340   │    │
│  │  20+ yrs:   40 (12%)    │  │                          │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Teacher Turnover Trend (Line Chart - Multi-Year)       │  │
│  │  2017-18 to 2024-25 turnover rates by school            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### SQL Queries

#### Card 1: Total Teachers Count
```sql
SELECT 
    COUNT(*) as total_teachers
FROM {{ ref('mart_cde__staff_demographics') }}
WHERE school_year = '2024-25'
  AND job_classification = 'Teachers'
  AND school_cds_code = {{ school_filter }};
```

#### Card 2: Teacher Diversity Index
```sql
SELECT 
    ROUND(
        100.0 * SUM(
            CASE 
                WHEN ethnicity IN ('Hispanic or Latino', 'Black or African American', 
                                  'Asian', 'Pacific Islander', 'American Indian or Alaska Native')
                THEN teacher_count 
                ELSE 0 
            END
        ) / NULLIF(SUM(teacher_count), 0),
        1
    ) as diversity_percentage
FROM {{ ref('mart_cde__staff_demographics') }}
WHERE school_year = '2024-25'
  AND job_classification = 'Teachers'
  AND school_cds_code = {{ school_filter }};
```

#### Card 3: Advanced Degree Rate
```sql
SELECT 
    ROUND(
        100.0 * SUM(
            CASE 
                WHEN education_level IN ('Masters Degree', 'Doctorate Degree')
                THEN teacher_count 
                ELSE 0 
            END
        ) / NULLIF(SUM(teacher_count), 0),
        1
    ) as advanced_degree_rate
FROM {{ ref('mart_cde__staff_education') }}
WHERE school_year = '2024-25'
  AND job_classification = 'Teachers'
  AND school_cds_code = {{ school_filter }};
```

#### Card 4: Staff Demographics by Role (Bar Chart)
```sql
SELECT 
    job_classification,
    ethnicity,
    SUM(staff_count) as count
FROM {{ ref('mart_cde__staff_demographics') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
GROUP BY job_classification, ethnicity
ORDER BY job_classification, count DESC;
```

#### Card 5: Years of Experience Distribution
```sql
SELECT 
    CASE 
        WHEN avg_years_experience BETWEEN 0 AND 5 THEN '0-5 years'
        WHEN avg_years_experience BETWEEN 6 AND 10 THEN '6-10 years'
        WHEN avg_years_experience BETWEEN 11 AND 20 THEN '11-20 years'
        ELSE '20+ years'
    END as experience_bracket,
    COUNT(*) as teacher_count
FROM {{ ref('mart_cde__staff_experience') }}
WHERE school_year = '2024-25'
  AND job_classification = 'Teachers'
  AND school_cds_code = {{ school_filter }}
GROUP BY experience_bracket
ORDER BY MIN(avg_years_experience);
```

#### Card 6: Student-to-Staff Ratios
```sql
SELECT 
    ratio_type,
    ratio_value
FROM {{ ref('mart_cde__staff_ratios') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND ratio_type IN ('Student-to-Teacher', 'Student-to-Counselor', 'Student-to-Administrator')
ORDER BY ratio_type;
```

#### Card 7: Teacher Turnover Trend (Multi-Year)
```sql
WITH year_counts AS (
    SELECT 
        school_year,
        school_cds_code,
        SUM(teacher_count) as total_teachers
    FROM {{ ref('mart_cde__staff_demographics') }}
    WHERE job_classification = 'Teachers'
      AND school_cds_code = {{ school_filter }}
      AND school_year BETWEEN '2017-18' AND '2024-25'
    GROUP BY school_year, school_cds_code
),
turnover AS (
    SELECT 
        curr.school_year,
        curr.school_cds_code,
        curr.total_teachers,
        prev.total_teachers as prior_year_teachers,
        ROUND(
            100.0 * (curr.total_teachers - COALESCE(prev.total_teachers, curr.total_teachers)) 
            / NULLIF(COALESCE(prev.total_teachers, curr.total_teachers), 0),
            1
        ) as turnover_rate
    FROM year_counts curr
    LEFT JOIN year_counts prev
        ON curr.school_cds_code = prev.school_cds_code
        AND CAST(SUBSTR(curr.school_year, 1, 4) AS INTEGER) - 1 = CAST(SUBSTR(prev.school_year, 1, 4) AS INTEGER)
)
SELECT 
    school_year,
    total_teachers,
    turnover_rate
FROM turnover
ORDER BY school_year;
```

### Filters
- **School**: Dropdown (district-wide, individual schools)
- **School Year**: Dropdown (2017-18 through 2024-25)
- **Job Classification**: Multi-select (Teachers, Administrators, Counselors, Support Staff)

---

## Dashboard 2: Academic Performance & Benchmarking

### Purpose
Display standardized test performance (SBAC ELA/Math, CAST Science, ELPAC) with California Dashboard color status levels, performance bands, and Distance From Standard (DFS) metrics.

### Target Users
- **Primary**: Principals, Curriculum Directors, Instructional Coaches
- **Secondary**: School Board, Superintendent

### Data Sources
- `mart_cde__standardized_assessments` (SBAC, CAST, CAA, ELPAC)
- `mart_cde__dashboard_colors` (accountability status levels)
- `dim_school_cds_mapping` (school names)
- `dim_reporting_category` (student groups)

### Key Metrics

| Metric | Definition | SQL Source |
|--------|-----------|------------|
| **Dashboard Color** | State accountability status (Blue, Green, Yellow, Orange, Red) | From `status_level` field |
| **Distance From Standard (DFS)** | Points above/below proficiency standard | `dfs_value` (positive = above, negative = below) |
| **Percentage Standard Met/Exceeded** | % students proficient or advanced | `pct_standard_met_exceeded` |
| **Change Level** | Year-over-year performance change (Increased, Maintained, Declined) | From `change_level` field |
| **Performance Band** | Relative performance (Very High, High, Medium, Low, Very Low) | Calculated from DFS |

### Dashboard Color Calculation

**Formula** (from CDE accountability documentation):
```sql
CASE 
    -- Blue: Very High status + Increased/Maintained
    WHEN dfs_value >= 95 AND change_level IN ('Increased Significantly', 'Increased', 'Maintained') THEN 'Blue'
    
    -- Green: High status + positive/neutral change
    WHEN dfs_value >= 30 AND dfs_value < 95 AND change_level != 'Declined Significantly' THEN 'Green'
    
    -- Yellow: Medium status OR neutral change
    WHEN (dfs_value >= -35 AND dfs_value < 30) OR change_level = 'Maintained' THEN 'Yellow'
    
    -- Orange: Low status + some decline
    WHEN dfs_value >= -95 AND dfs_value < -35 AND change_level = 'Declined' THEN 'Orange'
    
    -- Red: Very Low status OR significant decline
    WHEN dfs_value < -95 OR change_level = 'Declined Significantly' THEN 'Red'
    
    ELSE 'No Color'  -- Insufficient data
END as dashboard_color
```

### Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Academic Performance & Benchmarking    [School ▼] [Year ▼]    │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  ELA        │  │  Math       │  │  Science    │            │
│  │  Dashboard  │  │  Dashboard  │  │  Dashboard  │            │
│  │  🟢 Green   │  │  🟡 Yellow  │  │  🟢 Green   │            │
│  │  DFS: +42.3 │  │  DFS: -12.5 │  │  DFS: +28.1 │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Performance by Student Group (Table)                    │  │
│  │  Group          │ ELA Color │ Math Color │ DFS ELA │ DFS Math│
│  │  All Students   │ 🟢 Green │ 🟡 Yellow │  +42.3  │  -12.5 │
│  │  Hispanic       │ 🟡 Yellow│ 🟡 Yellow │  +15.2  │  -28.4 │
│  │  Econ Disadv    │ 🟡 Yellow│ 🟠 Orange │  +8.7   │  -52.1 │
│  │  English Learn  │ 🟢 Green │ 🟡 Yellow │  +35.4  │  -18.9 │
│  │  Students w/Dis │ 🟠 Orange│ 🟠 Orange │  -42.8  │  -68.3 │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  Proficiency Rates      │  │  Multi-Year DFS Trend    │    │
│  │  (Stacked Bar Chart)    │  │  (Line Chart)            │    │
│  │  Standard Exceeded: 28% │  │  2017 → 2025 trend       │    │
│  │  Standard Met:      34% │  │  ELA: ↗ +15.3 pts        │    │
│  │  Standard Not Met:  38% │  │  Math: ↘ -8.2 pts        │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ELPAC (English Proficiency) Results (Gauge Chart)      │  │
│  │  Level 4 (Well Developed):  42% │ Level 3: 31%          │  │
│  │  Level 2 (Somewhat Dev):    18% │ Level 1:  9%          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### SQL Queries

#### Card 1-3: Subject Dashboard Colors
```sql
SELECT 
    subject,
    dashboard_color,
    dfs_value,
    change_level,
    pct_standard_met_exceeded
FROM {{ ref('mart_cde__dashboard_colors') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND subject IN ('English Language Arts/Literacy', 'Mathematics', 'Science')
ORDER BY subject;
```

#### Card 4: Performance by Student Group
```sql
SELECT 
    rc.reporting_category_name,
    MAX(CASE WHEN subject = 'English Language Arts/Literacy' THEN dashboard_color END) as ela_color,
    MAX(CASE WHEN subject = 'Mathematics' THEN dashboard_color END) as math_color,
    MAX(CASE WHEN subject = 'English Language Arts/Literacy' THEN dfs_value END) as dfs_ela,
    MAX(CASE WHEN subject = 'Mathematics' THEN dfs_value END) as dfs_math
FROM {{ ref('mart_cde__dashboard_colors') }} dc
JOIN {{ ref('dim_reporting_category') }} rc ON dc.reporting_category = rc.reporting_category_code
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND subject IN ('English Language Arts/Literacy', 'Mathematics')
GROUP BY rc.reporting_category_name
ORDER BY rc.sort_order;
```

#### Card 5: Proficiency Rates
```sql
SELECT 
    'Standard Exceeded' as performance_level,
    SUM(students_tested_standard_exceeded) as student_count
FROM {{ ref('mart_cde__standardized_assessments') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND subject = 'English Language Arts/Literacy'
  AND reporting_category = 'All Students'

UNION ALL

SELECT 
    'Standard Met',
    SUM(students_tested_standard_met)
FROM {{ ref('mart_cde__standardized_assessments') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND subject = 'English Language Arts/Literacy'
  AND reporting_category = 'All Students'

UNION ALL

SELECT 
    'Standard Not Met',
    SUM(students_tested_standard_not_met)
FROM {{ ref('mart_cde__standardized_assessments') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND subject = 'English Language Arts/Literacy'
  AND reporting_category = 'All Students';
```

#### Card 6: Multi-Year DFS Trend
```sql
SELECT 
    school_year,
    subject,
    dfs_value
FROM {{ ref('mart_cde__dashboard_colors') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND subject IN ('English Language Arts/Literacy', 'Mathematics')
  AND school_year BETWEEN '2017-18' AND '2024-25'
ORDER BY school_year, subject;
```

#### Card 7: ELPAC Results
```sql
SELECT 
    performance_level,
    student_count,
    ROUND(100.0 * student_count / SUM(student_count) OVER (), 1) as percentage
FROM {{ ref('mart_cde__standardized_assessments') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
  AND assessment_type = 'ELPAC'
  AND reporting_category = 'English Learners'
GROUP BY performance_level, student_count
ORDER BY 
    CASE performance_level
        WHEN 'Level 4 - Well Developed' THEN 1
        WHEN 'Level 3 - Moderately Developed' THEN 2
        WHEN 'Level 2 - Somewhat Developed' THEN 3
        WHEN 'Level 1 - Minimally Developed' THEN 4
    END;
```

### Filters
- **School**: Dropdown
- **School Year**: Dropdown (2017-18 through 2024-25)
- **Subject**: Multi-select (ELA, Math, Science, ELPAC)
- **Student Group**: Multi-select (All Students, Hispanic, Economically Disadvantaged, EL, etc.)

---

## Dashboard 3: Post-Secondary Outcomes

### Purpose
Track college-going rates, Career Technical Education (CTE) pathway completion, A-G course requirements, and UC/CSU eligibility.

### Target Users
- **Primary**: Counselors, College & Career Readiness Coordinators
- **Secondary**: Principals, School Board

### Data Sources
- `mart_cde__post_secondary` (college enrollment, A-G completion)
- `mart_cde__cte_completion` (CTE pathway completers)
- `dim_school_cds_mapping` (school names)
- `dim_reporting_category` (student groups)

### Key Metrics

| Metric | Definition | SQL Source |
|--------|-----------|------------|
| **College-Going Rate (12 Months)** | % graduates enrolled in college within 12 months | `college_going_rate_12mo` |
| **A-G Completion Rate** | % graduates completing UC/CSU A-G requirements | `ag_completion_rate` |
| **CTE Pathway Completers** | Students completing CTE sequence (3+ courses) | `cte_completers` |
| **UC/CSU Eligibility Rate** | % graduates eligible for UC or CSU admission | `uc_csu_eligibility_rate` |
| **4-Year College Enrollment** | % attending 4-year institution (vs. 2-year) | `four_year_enrollment_rate` |

### Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Post-Secondary Outcomes Dashboard     [School ▼] [Cohort ▼]  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  College    │  │  A-G        │  │  CTE        │            │
│  │  Going Rate │  │  Completion │  │  Completers │            │
│  │    72.4%    │  │    58.1%    │  │    124      │            │
│  │  📈 +3.2%   │  │  📈 +5.4%   │  │  📈 +18     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  College Enrollment by Type (Donut Chart)                │  │
│  │  4-Year Public:   42% │ 4-Year Private: 18%              │  │
│  │  2-Year CC:       32% │ Out-of-State:    8%              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  College-Going Rates    │  │  A-G Completion by       │    │
│  │  by Student Group       │  │  Subject Area (Bar)      │    │
│  │  (Horizontal Bar Chart) │  │  Math (4 yrs):      89%  │    │
│  │  All Students:    72.4% │  │  English (4 yrs):   91%  │    │
│  │  Hispanic:        68.3% │  │  Science (2 yrs):   76%  │    │
│  │  Econ Disadv:     61.2% │  │  History (2 yrs):   82%  │    │
│  │  English Learn:   58.9% │  │  Foreign Lang:      65%  │    │
│  │  Students w/Dis:  42.1% │  │  Arts:              58%  │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CTE Pathway Completers by Sector (Stacked Bar)         │  │
│  │  Health Science: 42 │ Engineering: 28 │ IT: 24           │  │
│  │  Business: 18 │ Arts/Media: 12 │ Other: 0               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5-Year Trend: College-Going & A-G Rates (Line Chart)   │  │
│  │  2020-21 through 2024-25 cohorts                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### SQL Queries

#### Card 1: College-Going Rate (12 Months)
```sql
SELECT 
    ROUND(100.0 * college_going_count_12mo / NULLIF(cohort_size, 0), 1) as college_going_rate
FROM {{ ref('mart_cde__post_secondary') }}
WHERE cohort_year = '2023-24'  -- Most recent complete cohort
  AND school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students';
```

#### Card 2: A-G Completion Rate
```sql
SELECT 
    ROUND(100.0 * ag_completers / NULLIF(cohort_size, 0), 1) as ag_completion_rate
FROM {{ ref('mart_cde__post_secondary') }}
WHERE cohort_year = '2023-24'
  AND school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students';
```

#### Card 3: CTE Pathway Completers
```sql
SELECT 
    SUM(cte_completers) as total_cte_completers
FROM {{ ref('mart_cde__cte_completion') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }};
```

#### Card 4: College Enrollment by Type
```sql
SELECT 
    college_type,
    enrolled_count,
    ROUND(100.0 * enrolled_count / SUM(enrolled_count) OVER (), 1) as percentage
FROM {{ ref('mart_cde__post_secondary') }}
WHERE cohort_year = '2023-24'
  AND school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND college_type IN ('4-Year Public', '4-Year Private', '2-Year Community College', 'Out-of-State')
ORDER BY enrolled_count DESC;
```

#### Card 5: College-Going Rates by Student Group
```sql
SELECT 
    rc.reporting_category_name,
    ROUND(100.0 * ps.college_going_count_12mo / NULLIF(ps.cohort_size, 0), 1) as college_going_rate
FROM {{ ref('mart_cde__post_secondary') }} ps
JOIN {{ ref('dim_reporting_category') }} rc ON ps.reporting_category = rc.reporting_category_code
WHERE cohort_year = '2023-24'
  AND school_cds_code = {{ school_filter }}
GROUP BY rc.reporting_category_name, ps.college_going_count_12mo, ps.cohort_size
ORDER BY rc.sort_order;
```

#### Card 6: A-G Completion by Subject Area
```sql
SELECT 
    subject_area,
    ROUND(100.0 * completers / NULLIF(cohort_size, 0), 1) as completion_rate
FROM {{ ref('mart_cde__ag_requirements') }}
WHERE cohort_year = '2023-24'
  AND school_cds_code = {{ school_filter }}
  AND subject_area IN ('History/Social Science', 'English', 'Mathematics', 
                       'Laboratory Science', 'Language Other Than English', 
                       'Visual and Performing Arts', 'College-Prep Elective')
ORDER BY 
    CASE subject_area
        WHEN 'History/Social Science' THEN 1
        WHEN 'English' THEN 2
        WHEN 'Mathematics' THEN 3
        WHEN 'Laboratory Science' THEN 4
        WHEN 'Language Other Than English' THEN 5
        WHEN 'Visual and Performing Arts' THEN 6
        WHEN 'College-Prep Elective' THEN 7
    END;
```

#### Card 7: CTE Completers by Sector
```sql
SELECT 
    cte_sector,
    SUM(cte_completers) as completers
FROM {{ ref('mart_cde__cte_completion') }}
WHERE school_year = '2024-25'
  AND school_cds_code = {{ school_filter }}
GROUP BY cte_sector
ORDER BY completers DESC;
```

#### Card 8: 5-Year Trend
```sql
SELECT 
    cohort_year,
    ROUND(100.0 * college_going_count_12mo / NULLIF(cohort_size, 0), 1) as college_going_rate,
    ROUND(100.0 * ag_completers / NULLIF(cohort_size, 0), 1) as ag_completion_rate
FROM {{ ref('mart_cde__post_secondary') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND cohort_year BETWEEN '2019-20' AND '2023-24'
ORDER BY cohort_year;
```

### Filters
- **School**: Dropdown
- **Cohort Year**: Dropdown (2019-20 through 2023-24)
- **Student Group**: Multi-select
- **CTE Sector**: Multi-select (Health, Engineering, IT, Business, etc.)

---

## Dashboard 4: State Benchmarking & Comparisons

### Purpose
Compare school/district performance against state, county, and "similar schools" percentile rankings. Enable leaders to answer "How do we compare?"

### Target Users
- **Primary**: Superintendent, School Board, Principals
- **Secondary**: Curriculum Directors

### Data Sources
- `mart_cde__comparative_benchmarks` (percentile rankings)
- `mart_cde__similar_schools` (matched peer schools)
- `mart_cde__dashboard_colors` (accountability status)
- `dim_school_cds_mapping` (school names)

### Key Metrics

| Metric | Definition | SQL Source |
|--------|-----------|------------|
| **State Percentile Rank** | School's position relative to all CA schools (0-100) | Calculated from statewide data |
| **County Percentile Rank** | Position relative to county schools | Calculated from county data |
| **Similar Schools Rank** | Rank among demographically similar schools | From CDE "Similar Schools" algorithm |
| **Performance Gap** | Points above/below state average | `school_dfs - state_avg_dfs` |

### Similar Schools Algorithm

**Matching Criteria** (CDE methodology):
1. **School Type**: Elementary, Middle, High (same type only)
2. **Enrollment Size**: ±30% of school enrollment
3. **% Free/Reduced Lunch**: ±10 percentage points
4. **% English Learners**: ±10 percentage points
5. **% Students with Disabilities**: ±5 percentage points

**Pool Size**: Top 100 most similar schools in California

### Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  State Benchmarking & Comparisons      [School ▼] [Metric ▼]  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  State      │  │  County     │  │  Similar    │            │
│  │  Percentile │  │  Percentile │  │  Schools    │            │
│  │    68th     │  │    42nd     │  │  Rank 23/100│            │
│  │  📈 Above   │  │  📊 Middle  │  │  📉 Below   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Performance vs. State Average (Gauge Chart)             │  │
│  │  Our DFS: +42.3 │ State Avg: +12.8 │ Gap: +29.5 pts    │  │
│  │  ░░░░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ◉               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  Similar Schools        │  │  Performance by Metric   │    │
│  │  Comparison (Scatter)   │  │  (Horizontal Bar Chart)  │    │
│  │  X-axis: % FRPM         │  │  ELA:    68th ▓▓▓▓▓░░    │    │
│  │  Y-axis: DFS            │  │  Math:   52nd ▓▓▓▓░░░    │    │
│  │  Our School: ◉          │  │  Science:71st ▓▓▓▓▓▓░    │    │
│  │  Similar: ● (100 dots)  │  │  College:58th ▓▓▓▓░░░    │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Top 10 Similar Schools (Table)                          │  │
│  │  Rank│School Name         │County  │DFS ELA│DFS Math│Enr│
│  │  1   │Lincoln High (LA)   │Los Ang │ +58.3 │ +42.1  │1820│
│  │  2   │Roosevelt HS (SD)   │San Diego│ +55.2 │ +38.4  │1650│
│  │  3   │Kennedy HS (Fresno) │Fresno  │ +52.1 │ +35.8  │1580│
│  │  ... │...                 │...     │ ...   │ ...    │...│
│  │  23  │OUR SCHOOL →        │Alameda │ +42.3 │ -12.5  │1700│
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### SQL Queries

#### Card 1: State Percentile Rank
```sql
WITH ranked_schools AS (
    SELECT 
        school_cds_code,
        dfs_value,
        PERCENT_RANK() OVER (ORDER BY dfs_value) * 100 as percentile_rank
    FROM {{ ref('mart_cde__dashboard_colors') }}
    WHERE school_year = '2024-25'
      AND subject = 'English Language Arts/Literacy'
      AND reporting_category = 'All Students'
      AND aggregation_level = 'School'
)
SELECT 
    ROUND(percentile_rank, 0) as state_percentile
FROM ranked_schools
WHERE school_cds_code = {{ school_filter }};
```

#### Card 2: County Percentile Rank
```sql
WITH county_schools AS (
    SELECT 
        dc.school_cds_code,
        dc.dfs_value,
        sm.county_code,
        PERCENT_RANK() OVER (
            PARTITION BY sm.county_code 
            ORDER BY dc.dfs_value
        ) * 100 as county_percentile
    FROM {{ ref('mart_cde__dashboard_colors') }} dc
    JOIN {{ ref('dim_school_cds_mapping') }} sm ON dc.school_cds_code = sm.cds_code
    WHERE dc.school_year = '2024-25'
      AND dc.subject = 'English Language Arts/Literacy'
      AND dc.reporting_category = 'All Students'
      AND dc.aggregation_level = 'School'
)
SELECT 
    ROUND(county_percentile, 0) as county_percentile
FROM county_schools
WHERE school_cds_code = {{ school_filter }};
```

#### Card 3: Similar Schools Rank
```sql
WITH similar_schools_pool AS (
    SELECT 
        ss.target_school_cds_code,
        ss.similar_school_cds_code,
        ss.similarity_score,
        dc.dfs_value
    FROM {{ ref('mart_cde__similar_schools') }} ss
    JOIN {{ ref('mart_cde__dashboard_colors') }} dc 
        ON ss.similar_school_cds_code = dc.school_cds_code
    WHERE ss.target_school_cds_code = {{ school_filter }}
      AND dc.school_year = '2024-25'
      AND dc.subject = 'English Language Arts/Literacy'
      AND dc.reporting_category = 'All Students'
),
target_school_dfs AS (
    SELECT dfs_value
    FROM {{ ref('mart_cde__dashboard_colors') }}
    WHERE school_cds_code = {{ school_filter }}
      AND school_year = '2024-25'
      AND subject = 'English Language Arts/Literacy'
      AND reporting_category = 'All Students'
)
SELECT 
    (SELECT COUNT(*) + 1 
     FROM similar_schools_pool 
     WHERE dfs_value > (SELECT dfs_value FROM target_school_dfs)) as rank,
    (SELECT COUNT(*) FROM similar_schools_pool) + 1 as total_schools
FROM target_school_dfs;
```

#### Card 4: Performance vs. State Average
```sql
WITH state_avg AS (
    SELECT AVG(dfs_value) as avg_dfs
    FROM {{ ref('mart_cde__dashboard_colors') }}
    WHERE school_year = '2024-25'
      AND subject = 'English Language Arts/Literacy'
      AND reporting_category = 'All Students'
      AND aggregation_level = 'School'
),
school_dfs AS (
    SELECT dfs_value
    FROM {{ ref('mart_cde__dashboard_colors') }}
    WHERE school_cds_code = {{ school_filter }}
      AND school_year = '2024-25'
      AND subject = 'English Language Arts/Literacy'
      AND reporting_category = 'All Students'
)
SELECT 
    s.dfs_value as school_dfs,
    sa.avg_dfs as state_avg_dfs,
    s.dfs_value - sa.avg_dfs as gap
FROM school_dfs s
CROSS JOIN state_avg sa;
```

#### Card 5: Similar Schools Comparison Scatter
```sql
SELECT 
    sm.school_name,
    sm.free_reduced_lunch_pct,
    dc.dfs_value,
    CASE WHEN sm.cds_code = {{ school_filter }} THEN 'Our School' ELSE 'Similar School' END as school_type
FROM {{ ref('mart_cde__similar_schools') }} ss
JOIN {{ ref('dim_school_cds_mapping') }} sm ON ss.similar_school_cds_code = sm.cds_code
JOIN {{ ref('mart_cde__dashboard_colors') }} dc ON ss.similar_school_cds_code = dc.school_cds_code
WHERE ss.target_school_cds_code = {{ school_filter }}
  AND dc.school_year = '2024-25'
  AND dc.subject = 'English Language Arts/Literacy'
  AND dc.reporting_category = 'All Students'

UNION ALL

-- Add our school
SELECT 
    sm.school_name,
    sm.free_reduced_lunch_pct,
    dc.dfs_value,
    'Our School'
FROM {{ ref('dim_school_cds_mapping') }} sm
JOIN {{ ref('mart_cde__dashboard_colors') }} dc ON sm.cds_code = dc.school_cds_code
WHERE sm.cds_code = {{ school_filter }}
  AND dc.school_year = '2024-25'
  AND dc.subject = 'English Language Arts/Literacy'
  AND dc.reporting_category = 'All Students';
```

#### Card 6: Performance by Metric (Percentile Ranks)
```sql
WITH ranked AS (
    SELECT 
        school_cds_code,
        subject,
        PERCENT_RANK() OVER (PARTITION BY subject ORDER BY dfs_value) * 100 as percentile
    FROM {{ ref('mart_cde__dashboard_colors') }}
    WHERE school_year = '2024-25'
      AND reporting_category = 'All Students'
      AND aggregation_level = 'School'
)
SELECT 
    subject,
    ROUND(percentile, 0) as percentile_rank
FROM ranked
WHERE school_cds_code = {{ school_filter }}
  AND subject IN ('English Language Arts/Literacy', 'Mathematics', 'Science')
ORDER BY subject;
```

#### Card 7: Top Similar Schools Table
```sql
WITH ranked_similar AS (
    SELECT 
        sm.school_name,
        sm.county_name,
        sm.enrollment,
        dc_ela.dfs_value as dfs_ela,
        dc_math.dfs_value as dfs_math,
        ss.similarity_score,
        ROW_NUMBER() OVER (ORDER BY ss.similarity_score DESC) as similarity_rank
    FROM {{ ref('mart_cde__similar_schools') }} ss
    JOIN {{ ref('dim_school_cds_mapping') }} sm ON ss.similar_school_cds_code = sm.cds_code
    JOIN {{ ref('mart_cde__dashboard_colors') }} dc_ela 
        ON ss.similar_school_cds_code = dc_ela.school_cds_code
        AND dc_ela.subject = 'English Language Arts/Literacy'
    JOIN {{ ref('mart_cde__dashboard_colors') }} dc_math 
        ON ss.similar_school_cds_code = dc_math.school_cds_code
        AND dc_math.subject = 'Mathematics'
    WHERE ss.target_school_cds_code = {{ school_filter }}
      AND dc_ela.school_year = '2024-25'
      AND dc_math.school_year = '2024-25'
      AND dc_ela.reporting_category = 'All Students'
      AND dc_math.reporting_category = 'All Students'
)
SELECT 
    similarity_rank,
    school_name,
    county_name,
    ROUND(dfs_ela, 1) as dfs_ela,
    ROUND(dfs_math, 1) as dfs_math,
    enrollment
FROM ranked_similar
WHERE similarity_rank <= 25  -- Top 25 for display
ORDER BY similarity_rank;
```

### Filters
- **School**: Dropdown
- **Subject/Metric**: Multi-select (ELA, Math, Science, College-Going, etc.)
- **Comparison Group**: Radio (State, County, Similar Schools)

---

## Dashboard 5: Multi-Year Trends Dashboard

### Purpose
Visualize 8+ years of historical CDE data to identify growth trajectories, persistent gaps, and long-term trends across key metrics.

### Target Users
- **Primary**: School Board, Superintendent, Planning Directors
- **Secondary**: Principals (for school-level trends)

### Data Sources
- All CDE marts (chronic absenteeism, assessments, staff, post-secondary)
- Available years: 2016-17 through 2024-25 (8 years)
- `dim_school_cds_mapping` (school names)

### Key Metrics

| Metric | Definition | Years Available |
|--------|-----------|----------------|
| **Chronic Absenteeism Rate** | % students absent ≥10% of enrolled days | 2016-17 to 2024-25 (8 years) |
| **ELA/Math DFS Trend** | Distance From Standard over time | 2017-18 to 2024-25 (7 years) |
| **College-Going Rate Trend** | % graduates enrolling in college | 2016-17 to 2023-24 (7 cohorts) |
| **Teacher Turnover Trend** | Year-over-year teacher retention | 2021-22 to 2024-25 (4 years) |
| **Graduation Rate (ACGR)** | Adjusted Cohort Graduation Rate | 2017-18 to 2023-24 (6 cohorts) |

### Dashboard Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Multi-Year Trends Dashboard          [School ▼] [Group ▼]    │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  8-Year Chronic Absenteeism Trend (Line Chart)           │  │
│  │  2016-17: 8.2% → 2019-20: 6.1% → 2020-21: 31.5% (COVID)  │  │
│  │  → 2021-22: 28.3% → 2024-25: 14.2% (current)             │  │
│  │  Pre-COVID baseline: 6.1% │ Current: 14.2% (+8.1 pts)    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  7-Year ELA/Math DFS    │  │  College-Going Rate      │    │
│  │  Trend (Dual-Axis Line) │  │  7-Cohort Trend (Line)   │    │
│  │  ELA: -5.2 → +42.3      │  │  2016-17: 68% → 72.4%    │    │
│  │  Math: -22.8 → -12.5    │  │  Growth: +4.4 pts        │    │
│  │  Growth: ELA +47.5 pts  │  │  Target 2026: 75%        │    │
│  │          Math +10.3 pts │  │                          │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Performance Gaps by Student Group (Multi-Line Trend)    │  │
│  │  Lines: All Students, Hispanic, Econ Disadv, EL, SWD     │  │
│  │  Y-axis: ELA DFS │ X-axis: Years (2017-18 to 2024-25)   │  │
│  │  Gap Analysis: Econ Disadv gap narrowed from 42 pts      │  │
│  │                to 28 pts (improvement)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────┐    │
│  │  Graduation Rate Trend  │  │  Teacher Diversity Trend │    │
│  │  (Area Chart)           │  │  (Stacked Area Chart)    │    │
│  │  2017-18: 87.2%         │  │  2021-22 → 2024-25       │    │
│  │  2023-24: 92.1%         │  │  % Teachers of Color     │    │
│  │  Growth: +4.9 pts       │  │  32.1% → 38.2% (+6.1)    │    │
│  └─────────────────────────┘  └──────────────────────────┘    │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### SQL Queries

#### Card 1: 8-Year Chronic Absenteeism Trend
```sql
SELECT 
    school_year,
    ROUND(100.0 * chronic_absenteeism_count / NULLIF(cumulative_enrollment, 0), 1) as chronic_absence_rate,
    -- Flag COVID years for annotation
    CASE 
        WHEN school_year IN ('2019-20', '2020-21', '2021-22') THEN 'COVID Impact'
        ELSE 'Normal'
    END as period_type
FROM {{ ref('mart_cde__chronic_absenteeism') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND school_year BETWEEN '2016-17' AND '2024-25'
ORDER BY school_year;
```

#### Card 2: 7-Year ELA/Math DFS Trend
```sql
SELECT 
    school_year,
    MAX(CASE WHEN subject = 'English Language Arts/Literacy' THEN dfs_value END) as dfs_ela,
    MAX(CASE WHEN subject = 'Mathematics' THEN dfs_value END) as dfs_math
FROM {{ ref('mart_cde__dashboard_colors') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND subject IN ('English Language Arts/Literacy', 'Mathematics')
  AND school_year BETWEEN '2017-18' AND '2024-25'
GROUP BY school_year
ORDER BY school_year;
```

#### Card 3: College-Going Rate 7-Cohort Trend
```sql
SELECT 
    cohort_year,
    ROUND(100.0 * college_going_count_12mo / NULLIF(cohort_size, 0), 1) as college_going_rate
FROM {{ ref('mart_cde__post_secondary') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND cohort_year BETWEEN '2016-17' AND '2023-24'
ORDER BY cohort_year;
```

#### Card 4: Performance Gaps by Student Group (Multi-Line)
```sql
SELECT 
    dc.school_year,
    rc.reporting_category_name,
    dc.dfs_value
FROM {{ ref('mart_cde__dashboard_colors') }} dc
JOIN {{ ref('dim_reporting_category') }} rc ON dc.reporting_category = rc.reporting_category_code
WHERE dc.school_cds_code = {{ school_filter }}
  AND dc.subject = 'English Language Arts/Literacy'
  AND dc.school_year BETWEEN '2017-18' AND '2024-25'
  AND rc.reporting_category_code IN ('TA', 'RH', 'SE', 'EL', 'SD')  -- All, Hispanic, Econ Disadv, EL, SWD
ORDER BY dc.school_year, rc.sort_order;
```

#### Card 5: Graduation Rate Trend (ACGR)
```sql
SELECT 
    cohort_year,
    ROUND(100.0 * regular_hs_diploma_graduates / NULLIF(cohort_size, 0), 1) as graduation_rate
FROM {{ ref('mart_cde__graduation_rates') }}
WHERE school_cds_code = {{ school_filter }}
  AND reporting_category = 'All Students'
  AND cohort_year BETWEEN '2017-18' AND '2023-24'
ORDER BY cohort_year;
```

#### Card 6: Teacher Diversity Trend
```sql
WITH diversity_by_year AS (
    SELECT 
        school_year,
        ethnicity,
        SUM(teacher_count) as teacher_count
    FROM {{ ref('mart_cde__staff_demographics') }}
    WHERE school_cds_code = {{ school_filter }}
      AND job_classification = 'Teachers'
      AND school_year BETWEEN '2021-22' AND '2024-25'
    GROUP BY school_year, ethnicity
)
SELECT 
    school_year,
    ethnicity,
    teacher_count,
    ROUND(100.0 * teacher_count / SUM(teacher_count) OVER (PARTITION BY school_year), 1) as percentage
FROM diversity_by_year
ORDER BY school_year, 
    CASE ethnicity
        WHEN 'White' THEN 1
        WHEN 'Hispanic or Latino' THEN 2
        WHEN 'Asian' THEN 3
        WHEN 'Black or African American' THEN 4
        ELSE 5
    END;
```

### Filters
- **School**: Dropdown (district-wide, individual schools)
- **Student Group**: Multi-select (All Students, Hispanic, Econ Disadv, EL, SWD)
- **Metric**: Multi-select (Chronic Absence, ELA DFS, Math DFS, College-Going, Graduation)
- **Year Range**: Slider (2016-17 to 2024-25)

---

## Technical Implementation

### Metabase Configuration

#### 1. Database Connection
Use existing DuckDB connection:
- **Database**: `main` schema
- **Tables**: All `mart_cde__*` tables from Stage 3

#### 2. Dashboard Creation Process

**Step 1: Create Dashboard Shell**
```
Dashboard Settings:
- Name: "[Dashboard Name]"
- Description: "[Purpose statement]"
- Auto-refresh: 15 minutes (optional)
- Width: Full-width (1200px)
```

**Step 2: Add Cards (SQL Questions)**
For each card:
1. Create new SQL question
2. Paste SQL query from this document
3. Configure parameters (school filter, year filter)
4. Set visualization type (Number, Bar, Line, Table, etc.)
5. Add to dashboard

**Step 3: Configure Filters**
```
Filter Configuration:
- School Filter:
  - Type: Dropdown
  - Source: SELECT cds_code, school_name FROM dim_school_cds_mapping
  - Default: First school
  
- Year Filter:
  - Type: Dropdown
  - Source: SELECT DISTINCT school_year FROM [relevant mart]
  - Default: Latest year (2024-25)
  
- Student Group Filter:
  - Type: Multi-select
  - Source: SELECT reporting_category_code, reporting_category_name 
            FROM dim_reporting_category
  - Default: All Students
```

**Step 4: Layout & Styling**
- Use grid layout (12 columns)
- KPI cards: 3-4 columns each
- Charts: 6-12 columns (half or full width)
- Tables: Full width (12 columns)
- Add section dividers between card groups

#### 3. Performance Optimization

**Materialization Strategy**:
All CDE marts should be materialized as **tables** (not views):
```sql
{{ config(
    materialized='table',
    schema='cde_analytics'
) }}
```

**Why tables over views**:
- CDE data is updated quarterly (not real-time)
- Complex aggregations (staff, assessments) are expensive
- Dashboard queries will be faster (no re-computation)
- Can add indexes on frequently filtered columns

**Recommended Indexes**:
```sql
-- Add indexes after table creation
CREATE INDEX idx_cde_staff_cds ON mart_cde__staff_demographics(school_cds_code);
CREATE INDEX idx_cde_staff_year ON mart_cde__staff_demographics(school_year);
CREATE INDEX idx_cde_assess_cds ON mart_cde__standardized_assessments(school_cds_code);
CREATE INDEX idx_cde_assess_year ON mart_cde__standardized_assessments(school_year);
CREATE INDEX idx_cde_dashclr_cds ON mart_cde__dashboard_colors(school_cds_code);
CREATE INDEX idx_cde_dashclr_subj ON mart_cde__dashboard_colors(subject);
```

**Expected Query Performance**:
- Single-school queries: <500ms
- District-wide aggregations: <2s
- Multi-year trends: <3s
- Similar schools comparisons: <5s (100 schools)

#### 4. Data Refresh Strategy

**CDE Data Update Frequency**:
| Data Category | Update Schedule | Lag Time |
|---------------|----------------|----------|
| Chronic Absenteeism | Annual (October) | ~3 months |
| Staff Data | Annual (November) | ~4 months |
| Assessments (SBAC) | Annual (September) | ~2 months |
| Post-Secondary | Annual (March) | ~9 months |
| Dashboard Colors | Annual (December) | ~4 months |

**Recommended Refresh Schedule**:
```bash
# Monthly dbt run (1st of each month)
0 2 1 * * cd /path/to/oss_framework && dbt run --select mart_cde

# After each CDE data file update (manual trigger):
dbt run --select mart_cde__[specific_model]
```

**Metabase Cache Settings**:
- Dashboard cache: 4 hours (data doesn't change intraday)
- Question cache: 1 hour
- Clear cache after dbt runs

---

## User Access & Permissions

### Role-Based Access Control (RBAC)

| Role | Dashboards Accessible | Data Scope | Restrictions |
|------|----------------------|------------|--------------|
| **Superintendent** | All 5 dashboards | District-wide | None |
| **School Board** | All 5 dashboards | District-wide | None |
| **Principals** | Dashboards 1-3, 5 | Own school only | No similar schools comparison |
| **Teachers** | Dashboard 2 only (Academic Performance) | Own school | No staff data |
| **Counselors** | Dashboard 3 only (Post-Secondary) | Own school | No staff data |
| **Public** | None | None | No access |

### Row-Level Security (RLS)

**Implementation**:
```sql
-- Create view with RLS for principals
CREATE VIEW v_cde_data_principal_rls AS
SELECT *
FROM [mart_table]
WHERE school_cds_code IN (
    SELECT school_cds_code 
    FROM user_school_assignments 
    WHERE user_email = current_user()
);
```

**Metabase Groups**:
1. **District Leadership** - Full access, no filters
2. **School Principals** - Filtered by assigned school
3. **Teachers/Counselors** - Limited dashboards + school filter

---

## Training & Rollout

### Phase 1: Leadership Training (Week 1)
**Duration**: 2 hours  
**Audience**: Superintendent, Asst. Superintendents, Directors  
**Format**: In-person workshop

**Agenda**:
1. **Introduction to CDE Data Integration** (20 min)
   - What's new vs. existing dashboards
   - Data sources and update schedules
   - Limitations (aggregated data, no student-level)

2. **Dashboard Walkthroughs** (60 min)
   - Live demo of all 5 dashboards
   - Key metrics definitions (DFS, Dashboard colors, etc.)
   - Filter usage and navigation

3. **Strategic Use Cases** (30 min)
   - Benchmarking for board reports
   - Staff planning and diversity initiatives
   - Multi-year trend analysis for goal setting

4. **Q&A and Hands-On Practice** (10 min)

**Materials**:
- Printed dashboard quick reference guides
- Metric glossary (DFS, ACGR, etc.)
- FAQ handout

### Phase 2: Principal Training (Week 2)
**Duration**: 1.5 hours  
**Audience**: All school principals  
**Format**: Virtual workshop (recorded)

**Agenda**:
1. **Dashboard Tour** (45 min)
   - Staff Insights: workforce planning
   - Academic Performance: state benchmarking
   - Post-Secondary: college readiness tracking
   - Multi-Year Trends: progress monitoring

2. **Comparison to Internal Data** (20 min)
   - When to use CDE data vs. Aeries data
   - Understanding aggregation levels
   - Interpreting Dashboard colors

3. **Action Planning** (25 min)
   - Using benchmarking for improvement planning
   - Identifying gaps and priority areas
   - Setting SMART goals using trends

**Materials**:
- Video recording (for future reference)
- Principal-specific use case examples
- Dashboard access instructions

### Phase 3: Self-Service Rollout (Week 3)
**Audience**: Teachers, Counselors, Other Staff (as assigned)  
**Format**: Self-paced video tutorials + documentation

**Resources**:
- 5-minute video walkthrough per dashboard
- PDF user guides (one per dashboard)
- Troubleshooting FAQ
- Help desk contact information

---

## Success Metrics

### Dashboard Usage Targets (90 days post-launch)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Active Users (Monthly)** | 30+ | Metabase analytics |
| **Dashboard Views (Monthly)** | 500+ | Metabase analytics |
| **Average Session Duration** | 5+ minutes | Metabase analytics |
| **User Satisfaction** | 80%+ positive | Post-launch survey |
| **Data Quality Issues Reported** | <5 per month | Help desk tickets |

### Business Impact Targets (1 year post-launch)

| Outcome | Target | Measurement |
|---------|--------|-------------|
| **Board Reports Using CDE Data** | 100% | Count of board presentations |
| **Staff Planning Informed by Diversity Data** | 100% | HR director confirmation |
| **Schools Meeting A-G Targets** | +10% | Post-secondary outcomes |
| **Chronic Absenteeism Reduction** | -5 percentage points | Comparing internal + CDE data |

---

## Maintenance & Support

### Ongoing Maintenance Tasks

| Task | Frequency | Owner | Estimated Time |
|------|-----------|-------|----------------|
| **Monitor dashboard performance** | Weekly | Data Engineer | 30 min |
| **Update CDE data files** | Quarterly (as CDE releases) | Data Engineer | 2 hours |
| **Refresh dbt models** | Monthly (1st of month) | Data Engineer | 1 hour (automated) |
| **Review user feedback** | Monthly | Product Owner | 1 hour |
| **Update documentation** | As needed | Data Engineer | Variable |
| **Train new users** | As needed | Product Owner | 1.5 hours per session |

### Common Issues & Troubleshooting

| Issue | Likely Cause | Resolution |
|-------|-------------|------------|
| **Dashboard slow to load** | Stale cache or missing indexes | Clear cache, verify indexes exist |
| **"No data" for recent year** | CDE hasn't released yet | Document expected lag times |
| **School missing from filter** | Not in Public Schools Directory | Verify school is active in CDE data |
| **Dashboard color incorrect** | Calculation bug or data quality | Review DFS + Change Level logic |
| **Staff counts don't match HR** | Different reporting periods | Explain CDE uses October snapshot |

---

## Appendices

### Appendix A: Dashboard Color Status Level Definitions

**From CDE Dashboard Documentation**:

| Color | Status | DFS Range | Change Level | Description |
|-------|--------|-----------|--------------|-------------|
| 🔵 **Blue** | Very High | ≥ +95 | Increased/Maintained | Very high performance, sustained or improving |
| 🟢 **Green** | High | +30 to +94.9 | Not Declined Significantly | High performance, not declining |
| 🟡 **Yellow** | Medium | -35 to +29.9 | Any | Middle performance |
| 🟠 **Orange** | Low | -95 to -35.1 | Declined | Low performance, declining |
| 🔴 **Red** | Very Low | < -95 OR any | Declined Significantly | Very low performance or significant decline |

**Change Level Definitions**:
- **Increased Significantly**: +3+ points DFS change
- **Increased**: +0.5 to +2.9 points
- **Maintained**: -0.4 to +0.4 points
- **Declined**: -0.5 to -2.9 points
- **Declined Significantly**: -3+ points

### Appendix B: Reporting Category Codes

| Code | Name | Description |
|------|------|-------------|
| **TA** | All Students | Total, all students (unduplicated) |
| **RH** | Hispanic or Latino | Hispanic/Latino ethnicity |
| **RA** | Asian | Asian ethnicity |
| **RB** | Black or African American | Black/African American ethnicity |
| **RW** | White | White ethnicity |
| **SE** | Socioeconomically Disadvantaged | Free/Reduced-Price Meal eligible |
| **EL** | English Learners | Currently designated EL |
| **SD** | Students with Disabilities | Receiving special education services |
| **HM** | Homeless | Experiencing homelessness |
| **FY** | Foster Youth | In foster care system |

### Appendix C: Metric Glossary

**ACGR (Adjusted Cohort Graduation Rate)**  
Percentage of students in a cohort who graduate with a regular high school diploma within 4 years.

**A-G Requirements**  
University of California/California State University minimum admission requirements (7 subject areas).

**CAASPP**  
California Assessment of Student Performance and Progress (umbrella term for SBAC, CAST, CAA, ELPAC).

**CDS Code**  
County-District-School code (14-digit identifier): `19-64733-0000000`

**CTE (Career Technical Education)**  
Vocational programs organized into 15 industry sectors (Health, Engineering, IT, etc.).

**Dashboard Color**  
California School Dashboard accountability status level (Blue, Green, Yellow, Orange, Red).

**DFS (Distance From Standard)**  
Points above (+) or below (-) the proficiency threshold on SBAC assessments.

**ELPAC**  
English Language Proficiency Assessments for California (English proficiency test for EL students).

**FRPM**  
Free or Reduced-Price Meal eligibility (proxy for socioeconomic disadvantage).

**SBAC (Smarter Balanced Assessment)**  
Standardized tests for ELA and Math (grades 3-8, 11).

**UPC (Unduplicated Pupil Count)**  
Count of students who are EL, FRPM-eligible, or Foster Youth (used for LCFF funding).

---

## Implementation Timeline

| Week | Milestone | Owner | Hours |
|------|-----------|-------|-------|
| **Week 1** | Create dashboard shells in Metabase | Data Engineer | 8 |
| **Week 2** | Implement SQL queries for Dashboard 1 (Staff) | Data Engineer | 16 |
| **Week 3** | Implement SQL queries for Dashboard 2 (Academic) | Data Engineer | 20 |
| **Week 4** | Implement SQL queries for Dashboard 3 (Post-Secondary) | Data Engineer | 12 |
| **Week 5** | Implement SQL queries for Dashboard 4 (Benchmarking) | Data Engineer | 18 |
| **Week 6** | Implement SQL queries for Dashboard 5 (Trends) | Data Engineer | 14 |
| **Week 7** | Configure filters, RBAC, and performance tuning | Data Engineer | 12 |
| **Week 8** | User testing and bug fixes | Data Engineer + Product Owner | 16 |
| **Week 9** | Leadership training (Phase 1) | Product Owner | 4 |
| **Week 10** | Principal training (Phase 2) | Product Owner | 3 |
| **Week 11** | Self-service rollout (Phase 3) | Product Owner | 8 |
| **Week 12** | Post-launch monitoring and support | Data Engineer + Product Owner | 8 |
| **Total** | | | **139 hours** |

---

## Approval & Sign-Off

| Stakeholder | Role | Approval Date | Signature |
|-------------|------|---------------|-----------|
| [Name] | Superintendent | __________ | __________ |
| [Name] | Director of Technology | __________ | __________ |
| [Name] | Director of Curriculum & Instruction | __________ | __________ |
| [Name] | Data Engineer | __________ | __________ |

---

**Document Status**: Draft for Approval  
**Next Steps**: Review with stakeholders, incorporate feedback, obtain sign-off before implementation

**Questions or Feedback**: Contact [Data Team Email] or [Product Owner Name]
