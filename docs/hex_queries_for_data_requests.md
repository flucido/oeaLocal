# Hex Queries for Data Requests

## Connecting Hex to MotherDuck

1. Open Hex: https://app.hex.tech
2. Create a new project
3. Add data connection → Select "MotherDuck"
4. Paste your MotherDuck token (from https://app.motherduck.com → Settings → Access Tokens)
5. Database: `aeries_data_mart`

---

## Request 1: 7th Grade Math Pathways & 8th Grade Outcomes

### Course Codes (Leading Zeros Stripped)

| Aeries Code | Our Code | Course |
|-------------|----------|--------|
| 000325 | 325 | Math 8 |
| 000329 | 329 | Apex Math 8 |
| 000308 | 308 | Algebra 1 |

### Query 1A: 7th Grade Math Enrollment by Pathway

```sql
-- 7th Grade Math 8 vs Apex Math 8 by Race and Gender
SELECT 
    pathway,
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.math_pathways_7th_grade
GROUP BY pathway, primary_race, gender
ORDER BY pathway, students DESC;
```

### Query 1B: Math Pathway Summary by Race

```sql
-- Total enrollment by pathway and race
SELECT 
    pathway,
    primary_race,
    SUM(student_count) as total_students,
    ROUND(100.0 * SUM(student_count) / 
        SUM(SUM(student_count)) OVER (PARTITION BY pathway), 1) as pct
FROM analytics.math_pathways_7th_grade
GROUP BY pathway, primary_race
ORDER BY pathway, total_students DESC;
```

### Query 1C: 8th Grade Algebra 1 Grade Distribution

```sql
-- Algebra 1 grades by race
SELECT 
    primary_race,
    grade,
    SUM(student_count) as students
FROM analytics.algebra_1_outcomes
GROUP BY primary_race, grade
ORDER BY primary_race, students DESC;
```

### Query 1D: Algebra 1 Pass Rate by Demographics

```sql
-- Pass rate by race and gender
SELECT 
    primary_race,
    gender,
    SUM(CASE WHEN is_passing THEN student_count ELSE 0 END) as passing,
    SUM(student_count) as total,
    ROUND(100.0 * SUM(CASE WHEN is_passing THEN student_count ELSE 0 END) 
        / SUM(student_count), 1) as pass_rate_pct
FROM analytics.algebra_1_outcomes
GROUP BY primary_race, gender
ORDER BY pass_rate_pct DESC;
```

---

## Request 2: LEAD Program Enrollment & Demographics

### Query 2A: 5-Year Enrollment Trend

```sql
-- LEAD enrollment by year
SELECT 
    school_year,
    SUM(student_count) as total_students,
    SUM(CASE WHEN gender = 'M' THEN student_count ELSE 0 END) as male,
    SUM(CASE WHEN gender = 'F' THEN student_count ELSE 0 END) as female
FROM analytics.lead_program_enrollment
GROUP BY school_year
ORDER BY school_year;
```

### Query 2B: LEAD Demographics by Race

```sql
-- LEAD students by race
SELECT 
    primary_race,
    SUM(student_count) as total_students,
    ROUND(100.0 * SUM(student_count) / 
        (SELECT SUM(student_count) FROM analytics.lead_program_enrollment), 1) as pct
FROM analytics.lead_program_enrollment
GROUP BY primary_race
ORDER BY total_students DESC;
```

### Query 2C: LEAD by Race and Gender

```sql
-- LEAD students by race and gender
SELECT 
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.lead_program_enrollment
GROUP BY primary_race, gender
ORDER BY students DESC;
```

### Query 2D: LEAD by Grade Level

```sql
-- LEAD students by grade level
SELECT 
    grade_level,
    SUM(student_count) as students
FROM analytics.lead_program_enrollment
GROUP BY grade_level
ORDER BY grade_level;
```

---

## Quick Summary Results

### 7th Grade Math Pathways

| Pathway | Students | Key Demographics |
|---------|----------|------------------|
| Math 8 | 809 | White 78%, Asian 8% |
| Apex Math 8 | 132 | White 79%, Asian 18% |

### 8th Grade Algebra 1

- **153 students** total
- Grades: A through D distributed
- Pass rates vary by demographic group

### LEAD Program (5-Year)

| Year | Students |
|------|----------|
| 2021-2022 | 32 |
| 2022-2023 | 29 |
| 2023-2024 | 33 |
| 2024-2025 | 59 |
| 2025-2026 | 66 |

**Demographics:** White 78.5%, Asian 8.6%, Hispanic 2.7%

---

## Available Tables in MotherDuck

| Schema | Table | Description |
|--------|-------|-------------|
| analytics | math_pathways_7th_grade | 7th grade Math 8 vs Apex |
| analytics | algebra_1_outcomes | 8th grade Algebra 1 grades |
| analytics | lead_program_enrollment | LEAD program 5-year data |
| analytics | analytics_for_hex | Student-level analytics |
| analytics | equity_by_race | Equity outcomes by race |
| core | dim_students | Student demographics |

---

*Last updated: 2026-02-23*
