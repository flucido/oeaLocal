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

---

### Question 1A: How many 7th graders were enrolled in Math 8 by year?

```sql
-- 7th Grade Math 8 Enrollment by Year
SELECT 
    school_year,
    SUM(student_count) as total_students
FROM analytics.math_8_enrollment_by_year
GROUP BY school_year
ORDER BY school_year;
```

**With demographics breakdown:**
```sql
-- Math 8 Enrollment by Year, Race, and Gender
SELECT 
    school_year,
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.math_8_enrollment_by_year
GROUP BY school_year, primary_race, gender
ORDER BY school_year, students DESC;
```

---

### Question 1B: How many 7th graders were enrolled in Apex Math 8 by year?

```sql
-- 7th Grade Apex Math 8 Enrollment by Year
SELECT 
    school_year,
    SUM(student_count) as total_students
FROM analytics.apex_math_8_enrollment_by_year
GROUP BY school_year
ORDER BY school_year;
```

**With demographics breakdown:**
```sql
-- Apex Math 8 Enrollment by Year, Race, and Gender
SELECT 
    school_year,
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.apex_math_8_enrollment_by_year
GROUP BY school_year, primary_race, gender
ORDER BY school_year, students DESC;
```

---

### Question 1C: How many 7th grade Math 8 students went on to Algebra 1 in 8th grade?

```sql
-- Cohort Tracking: Math 8 → Algebra 1
-- Shows how many 7th graders took Algebra 1 in their 8th grade year
SELECT 
    year_7th_grade,
    took_algebra_1_in_8th,
    SUM(student_count) as students
FROM analytics.math_8_cohort_tracking
GROUP BY year_7th_grade, took_algebra_1_in_8th
ORDER BY year_7th_grade, took_algebra_1_in_8th;
```

**By demographics:**
```sql
-- Math 8 Cohort by Race and Gender
SELECT 
    year_7th_grade,
    primary_race,
    gender,
    took_algebra_1_in_8th,
    SUM(student_count) as students
FROM analytics.math_8_cohort_tracking
GROUP BY year_7th_grade, primary_race, gender, took_algebra_1_in_8th
ORDER BY year_7th_grade, took_algebra_1_in_8th DESC, students DESC;
```

---

### Question 1D: Grade distribution for Algebra 1 students (final term)

```sql
-- Algebra 1 Grade Distribution for Math 8 Cohort
SELECT 
    year_7th_grade,
    algebra_1_grade,
    SUM(student_count) as students
FROM analytics.math_8_cohort_tracking
WHERE took_algebra_1_in_8th = true
GROUP BY year_7th_grade, algebra_1_grade
ORDER BY year_7th_grade, students DESC;
```

**By race and gender:**
```sql
-- Algebra 1 Grades by Race and Gender
SELECT 
    primary_race,
    gender,
    algebra_1_grade,
    SUM(student_count) as students
FROM analytics.math_8_cohort_tracking
WHERE took_algebra_1_in_8th = true
GROUP BY primary_race, gender, algebra_1_grade
ORDER BY primary_race, students DESC;
```

**Pass rate by demographics:**
```sql
-- Algebra 1 Pass Rate by Race and Gender
SELECT 
    primary_race,
    gender,
    SUM(CASE WHEN algebra_1_passing = true THEN student_count ELSE 0 END) as passing,
    SUM(student_count) as total,
    ROUND(100.0 * SUM(CASE WHEN algebra_1_passing = true THEN student_count ELSE 0 END) 
        / SUM(student_count), 1) as pass_rate_pct
FROM analytics.math_8_cohort_tracking
WHERE took_algebra_1_in_8th = true
GROUP BY primary_race, gender
ORDER BY pass_rate_pct DESC;
```

---

## Request 2: LEAD Program Enrollment & Demographics (5-Year)

### Question 2A: LEAD Enrollment by Year

```sql
-- LEAD Program 5-Year Enrollment Trend
SELECT 
    school_year,
    SUM(student_count) as total_students
FROM analytics.lead_enrollment_by_year
GROUP BY school_year
ORDER BY school_year;
```

### Question 2B: LEAD Demographics by Race

```sql
-- LEAD Students by Race
SELECT 
    primary_race,
    SUM(student_count) as total_students,
    ROUND(100.0 * SUM(student_count) / 
        (SELECT SUM(student_count) FROM analytics.lead_enrollment_by_year), 1) as pct
FROM analytics.lead_enrollment_by_year
GROUP BY primary_race
ORDER BY total_students DESC;
```

### Question 2C: LEAD by Race and Gender

```sql
-- LEAD Students by Race and Gender
SELECT 
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.lead_enrollment_by_year
GROUP BY primary_race, gender
ORDER BY students DESC;
```

### Question 2D: LEAD by Year and Gender

```sql
-- LEAD Enrollment by Year and Gender
SELECT 
    school_year,
    gender,
    SUM(student_count) as students
FROM analytics.lead_enrollment_by_year
GROUP BY school_year, gender
ORDER BY school_year, gender;
```

---

## Available Tables in MotherDuck

| Schema | Table | Rows | Description |
|--------|-------|------|-------------|
| analytics | math_8_enrollment_by_year | 87 | Math 8 enrollment by year/race/gender |
| analytics | apex_math_8_enrollment_by_year | 25 | Apex Math 8 enrollment by year/race/gender |
| analytics | math_8_cohort_tracking | 495 | Cohort: 7th Math 8 → 8th Algebra 1 |
| analytics | lead_enrollment_by_year | 180 | LEAD program by year/race/gender |
| analytics | analytics_for_hex | 5,232 | Student-level analytics |
| analytics | equity_by_race | 14 | Equity outcomes by race |
| core | dim_students | 5,232 | Student demographics |
| core | fact_academic_records | 150,583 | Grades and courses |

---

## Quick Summary Results

### 7th Grade Math 8 Enrollment by Year

| Year | Students |
|------|----------|
| 2021-2022 | 152 |
| 2022-2023 | 176 |
| 2023-2024 | 161 |
| 2024-2025 | 150 |
| 2025-2026 | 175 |

### 7th Grade Apex Math 8 Enrollment by Year

| Year | Students |
|------|----------|
| 2022-2023 | 36 |
| 2023-2024 | 25 |
| 2024-2025 | 33 |
| 2025-2026 | 38 |

### Math 8 Cohort → Algebra 1

| 7th Grade Year | Took Algebra 1 | Did Not Take |
|----------------|----------------|--------------|
| 2021-2022 | - | 18 |
| 2022-2023 | 189 | 18 |
| 2023-2024 | 134 | 19 |
| 2024-2025 | 77 | 16 |
| 2025-2026 | - | 24 |

### LEAD Program 5-Year Trend

| Year | Students |
|------|----------|
| 2021-2022 | 73 |
| 2022-2023 | 92 |
| 2023-2024 | 129 |
| 2024-2025 | 235 |
| 2025-2026 | 232 |

---

*Last updated: 2026-02-23*
