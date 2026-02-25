# Jupyter Analytics Guide

## Overview

Use JupyterLab for interactive data analysis, ad-hoc queries, and custom visualizations. This guide replaces the previous Hex notebook workflow with local Jupyter notebooks.

## Connecting Jupyter to DuckDB

### Launch JupyterLab

```bash
# Option 1: Direct launch
jupyter lab

# Option 2: Via Docker Compose
docker-compose up -d jupyter
# Access at http://localhost:8888
```

### Connect to DuckDB

```python
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to local DuckDB database
conn = duckdb.connect('./oss_framework/data/oea.duckdb', read_only=True)

# Install and load Delta extension
conn.execute("INSTALL delta")
conn.execute("LOAD delta")

# Test connection
conn.execute("SELECT COUNT(*) FROM core.dim_students").fetchdf()
```

## Common Analytics Queries

### Request 1: 7th Grade Math Pathways & 8th Grade Outcomes

#### Course Codes (Leading Zeros Stripped)

| Aeries Code | Our Code | Course |
|-------------|----------|--------|
| 000325 | 325 | Math 8 |
| 000329 | 329 | Apex Math 8 |
| 000308 | 308 | Algebra 1 |

#### Query 1A: 7th Grade Math Enrollment by Pathway

```python
query = """
SELECT 
    pathway,
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.math_pathways_7th_grade
GROUP BY pathway, primary_race, gender
ORDER BY pathway, students DESC
"""

df = conn.execute(query).fetchdf()
df
```

#### Query 1B: Math Pathway Summary by Race

```python
query = """
SELECT 
    pathway,
    primary_race,
    SUM(student_count) as total_students,
    ROUND(100.0 * SUM(student_count) / 
        SUM(SUM(student_count)) OVER (PARTITION BY pathway), 1) as pct
FROM analytics.math_pathways_7th_grade
GROUP BY pathway, primary_race
ORDER BY pathway, total_students DESC
"""

df = conn.execute(query).fetchdf()

# Visualize
plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='primary_race', y='total_students', hue='pathway')
plt.title('7th Grade Math Enrollment by Race and Pathway')
plt.xlabel('Race/Ethnicity')
plt.ylabel('Number of Students')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

#### Query 1C: 8th Grade Algebra 1 Grade Distribution

```python
query = """
SELECT 
    primary_race,
    grade,
    SUM(student_count) as students
FROM analytics.algebra_1_outcomes
GROUP BY primary_race, grade
ORDER BY primary_race, students DESC
"""

df = conn.execute(query).fetchdf()
df
```

#### Query 1D: Algebra 1 Pass Rate by Demographics

```python
query = """
SELECT 
    primary_race,
    gender,
    SUM(CASE WHEN is_passing THEN student_count ELSE 0 END) as passing,
    SUM(student_count) as total,
    ROUND(100.0 * SUM(CASE WHEN is_passing THEN student_count ELSE 0 END) 
        / SUM(student_count), 1) as pass_rate_pct
FROM analytics.algebra_1_outcomes
GROUP BY primary_race, gender
ORDER BY pass_rate_pct DESC
"""

df = conn.execute(query).fetchdf()

# Visualize
plt.figure(figsize=(10, 6))
df_pivot = df.pivot(index='primary_race', columns='gender', values='pass_rate_pct')
df_pivot.plot(kind='bar', figsize=(12, 6))
plt.title('Algebra 1 Pass Rates by Race and Gender')
plt.xlabel('Race/Ethnicity')
plt.ylabel('Pass Rate (%)')
plt.legend(title='Gender')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

---

### Request 2: LEAD Program Enrollment & Demographics

#### Query 2A: 5-Year Enrollment Trend

```python
query = """
SELECT 
    school_year,
    SUM(student_count) as total_students,
    SUM(CASE WHEN gender = 'M' THEN student_count ELSE 0 END) as male,
    SUM(CASE WHEN gender = 'F' THEN student_count ELSE 0 END) as female
FROM analytics.lead_program_enrollment
GROUP BY school_year
ORDER BY school_year
"""

df = conn.execute(query).fetchdf()

# Visualize trend
plt.figure(figsize=(12, 6))
plt.plot(df['school_year'], df['total_students'], marker='o', linewidth=2, label='Total')
plt.plot(df['school_year'], df['male'], marker='s', linewidth=2, label='Male')
plt.plot(df['school_year'], df['female'], marker='^', linewidth=2, label='Female')
plt.title('LEAD Program Enrollment Trend (5 Years)')
plt.xlabel('School Year')
plt.ylabel('Number of Students')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

#### Query 2B: LEAD Demographics by Race

```python
query = """
SELECT 
    primary_race,
    SUM(student_count) as total_students,
    ROUND(100.0 * SUM(student_count) / 
        (SELECT SUM(student_count) FROM analytics.lead_program_enrollment), 1) as pct
FROM analytics.lead_program_enrollment
GROUP BY primary_race
ORDER BY total_students DESC
"""

df = conn.execute(query).fetchdf()

# Pie chart
plt.figure(figsize=(10, 8))
plt.pie(df['total_students'], labels=df['primary_race'], autopct='%1.1f%%', startangle=90)
plt.title('LEAD Program Demographics by Race')
plt.axis('equal')
plt.show()
```

#### Query 2C: LEAD by Race and Gender

```python
query = """
SELECT 
    primary_race,
    gender,
    SUM(student_count) as students
FROM analytics.lead_program_enrollment
GROUP BY primary_race, gender
ORDER BY students DESC
"""

df = conn.execute(query).fetchdf()

# Grouped bar chart
plt.figure(figsize=(12, 6))
df_pivot = df.pivot(index='primary_race', columns='gender', values='students')
df_pivot.plot(kind='bar', figsize=(12, 6))
plt.title('LEAD Program Enrollment by Race and Gender')
plt.xlabel('Race/Ethnicity')
plt.ylabel('Number of Students')
plt.legend(title='Gender')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## Available Tables in DuckDB

| Schema | Table | Description |
|--------|-------|-------------|
| analytics | math_pathways_7th_grade | 7th grade Math 8 vs Apex |
| analytics | algebra_1_outcomes | 8th grade Algebra 1 grades |
| analytics | lead_program_enrollment | LEAD program 5-year data |
| analytics | chronic_absenteeism_risk | Students at risk |
| analytics | equity_outcomes_by_demographics | Equity metrics |
| core | dim_students | Student demographics |
| core | fact_academic_records | Grades and courses |
| core | fact_attendance | Daily attendance |
| core | fact_enrollment | Enrollment history |

## Advanced Analysis

### Custom Aggregations

```python
# Calculate custom metrics
query = """
WITH student_metrics AS (
    SELECT 
        s.student_id,
        s.primary_race,
        s.gender,
        AVG(a.attendance_rate) as avg_attendance,
        AVG(g.gpa) as avg_gpa
    FROM core.dim_students s
    LEFT JOIN core.fact_attendance a ON s.student_id = a.student_id
    LEFT JOIN core.fact_academic_records g ON s.student_id = g.student_id
    GROUP BY s.student_id, s.primary_race, s.gender
)
SELECT 
    primary_race,
    gender,
    COUNT(*) as student_count,
    ROUND(AVG(avg_attendance), 2) as avg_attendance_rate,
    ROUND(AVG(avg_gpa), 2) as avg_gpa
FROM student_metrics
WHERE avg_attendance IS NOT NULL AND avg_gpa IS NOT NULL
GROUP BY primary_race, gender
ORDER BY avg_gpa DESC
"""

df = conn.execute(query).fetchdf()
df
```

### Export Results

```python
# Export to CSV
df.to_csv('./reports/equity_analysis.csv', index=False)

# Export to Excel
df.to_excel('./reports/equity_analysis.xlsx', index=False)

# Export to Parquet
df.to_parquet('./reports/equity_analysis.parquet', index=False)
```

### Save Notebook Results to DuckDB

```python
# Write analysis results back to DuckDB
conn.execute("""
    CREATE TABLE IF NOT EXISTS analytics.custom_analysis AS
    SELECT * FROM df
""")

conn.commit()
```

## Tips & Best Practices

1. **Use read_only connections** for analysis to prevent accidental modifications
2. **Close connections** when done: `conn.close()`
3. **Cache intermediate results** in DataFrames for faster iteration
4. **Use DuckDB's parallel execution** - it's fast even on large datasets
5. **Leverage pandas integration** - seamlessly convert between DuckDB and pandas

## Resources

- **JupyterLab Docs**: https://jupyterlab.readthedocs.io/
- **DuckDB Python API**: https://duckdb.org/docs/api/python/overview.html
- **Pandas Integration**: https://duckdb.org/docs/guides/python/pandas.html
- **Sample Notebooks**: See `notebooks/` directory in this repository

---

*Last updated: 2026-02-25*
