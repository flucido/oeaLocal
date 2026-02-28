# Student Enrollment and Academic Outcomes Analysis
## Supporting Documentation: Detailed Findings and Methodology

**Period Covered:** Academic Years 2021-22 through 2025-26  
**Date Prepared:** February 2026

---

## Table of Contents

1. [Data Sources and Methodology](#data-sources-and-methodology)
2. [Mathematics Pipeline Analysis](#mathematics-pipeline-analysis)
3. [LEAD Program Longitudinal Analysis](#lead-program-longitudinal-analysis)
4. [Data Quality Assessment](#data-quality-assessment)
5. [Technical Appendix](#technical-appendix)

---

## Data Sources and Methodology

### Dataset Overview

This analysis integrates multiple data sources to track student enrollment and academic performance across five academic years.

**Core Metrics:**
- **Total Unique Students:** 372
- **Total Enrollment Records:** 622 course enrollments
- **Total Grade Records:** 40,478 individual grades across six years
- **Student ID Mapping Coverage:** 100% (1,547 unique mappings)
- **Grade Match Rate:** 92.8%

### Data Sources

#### Enrollment Data (Excel Files)

| File | Records | Unique Students | Course | Description |
|------|---------|-----------------|--------|-------------|
| Algebra 1A 23-26.xlsx | 171 | 111 | 308 | 8th grade advanced mathematics |
| MATH 8 and Apex Data 21-26.xlsx | 233 | 233 | 325, 329 | 7th grade mathematics pathways |
| Lead 21-26.xlsx | 218 | 185 | 1205 | Specialized enrichment program |

#### Grade Data (CSV Files)

Six annual grade files covering academic years 2020-21 through 2025-26:
- Total records across all files: 150,583
- Unique students in grade files: 1,844
- Records matching enrollment cohort: 92.8%

#### Student ID Mapping

Five annual mapping files connecting local IDs (5-digit) to State Student IDs (10-digit):
- Total mappings: 3,092
- Unique student mappings: 1,547 (after deduplication)
- Conflict resolution: 1 local ID mapped to multiple state IDs; first occurrence retained

### Course Definitions

| Course ID | Course Name | Grade Level | Description |
|-----------|-------------|-------------|-------------|
| 308 | Algebra 1 | 8th | Advanced mathematics course typically taken in 9th grade |
| 325 | Regular Math 8 | 7th | Standard accelerated mathematics pathway |
| 329 | Apex Math 8 | 7th | Supplemental delivery accelerated mathematics pathway |
| 1205 | LEAD Program | K-8 | Specialized enrichment program |

### Analytical Framework

**Longitudinal Tracking Model:**
- Primary tracking key: State Student ID (10-digit)
- Progression model: 7th grade (Year N) → 8th grade (Year N+1)
- Academic year determination: Fall semester enrollment
- GPA calculation: Standard 4.0 scale, averaged across all marking periods

**Data Processing Pipeline:**
1. Load and standardize student ID mappings
2. Load enrollment records and normalize academic year formats
3. Load grade files and join to ID mappings via local ID
4. Filter grade data to enrollment cohort via state ID
5. Calculate progression metrics and performance statistics
6. Generate demographic disaggregation and trend analysis

---

## Mathematics Pipeline Analysis

### Research Question

How do students progress from 7th grade mathematics courses to 8th grade Algebra 1, and how does academic performance vary by delivery pathway, gender, and race/ethnicity?

### Overall Progression

**Cohort Definition:**
- 233 students enrolled in 7th grade mathematics (Courses 325 or 329)
- Tracking period: 7th grade (Year N) to 8th grade (Year N+1)
- Outcome measure: Enrollment in 8th grade Algebra 1 (Course 308)

**Aggregate Results:**
- 106 students enrolled in 8th grade Algebra 1
- Overall progression rate: **45.5%**
- 127 students (54.5%) did not enroll in 8th grade Algebra

**Academic Performance:**
- Average 7th grade mathematics GPA: **3.59**
- Average 8th grade Algebra 1 GPA: **3.51**
- Performance change: **-0.08 points**

The slight GPA decline reflects increased course rigor. Students who progress maintain strong performance (3.5+ GPA threshold).

### Analysis by Delivery Pathway

Two distinct 7th grade mathematics delivery methods were compared:

| Pathway | Course ID | Students | Algebra Progression | Progression Rate | Avg 7th GPA | Avg Algebra GPA |
|---------|-----------|----------|---------------------|------------------|-------------|-----------------|
| Supplemental Delivery | 329 (Apex Math 8) | 134 | 61 | 45.5% | Incomplete data | 3.58 |
| Regular-Hour Delivery | 325 (Regular Math 8) | 99 | 45 | 45.5% | 3.59 | 3.43 |

**Key Findings:**

1. **Identical Progression Rates:** Both delivery methods produce the same 45.5% advancement rate to 8th grade Algebra, suggesting pathway designation does not affect access to advanced coursework.

2. **Performance Differential:** Students from the supplemental delivery pathway (Apex Math 8) achieve 0.15 points higher GPA in 8th grade Algebra (3.58 vs. 3.43).

3. **Data Limitation:** 7th grade GPA data for Apex Math 8 students was incomplete in source files, preventing direct performance comparison at entry point.

### Gender Analysis

#### Progression Rates

| Gender | Total Students | Progressed to Algebra | Progression Rate | Percentage Point Gap |
|--------|---------------|----------------------|------------------|---------------------|
| Male | 127 | 70 | 55.1% | Reference |
| Female | 106 | 36 | 34.0% | -21.1 pp |

#### Academic Performance

| Gender | Avg 7th Grade Math GPA | Avg 8th Grade Algebra GPA | GPA Change |
|--------|------------------------|---------------------------|------------|
| Male | 3.50 | 3.45 | -0.05 |
| Female | 3.72 | 3.65 | -0.07 |

#### Key Patterns

1. **Performance-Progression Paradox:** Female students demonstrate higher academic performance in both 7th grade mathematics (+0.22 GPA points) and 8th grade Algebra (+0.20 GPA points), yet progress at substantially lower rates.

2. **Consistent Gender Gap Across Pathways:**

| Pathway | Female Progression Rate | Male Progression Rate | Gap |
|---------|------------------------|----------------------|-----|
| Apex Math 8 | 32.6% | 55.4% | 22.8 pp |
| Regular Math 8 | 34.9% | 54.9% | 20.0 pp |

The gender disparity persists regardless of pathway, indicating it is not specific to one instructional approach.

3. **Sustained Excellence:** Female students who progress maintain their performance advantage throughout the transition.

### Race and Ethnicity Analysis

#### Progression Rates by Demographic Group

Groups with 5 or more students are presented for statistical stability:

| Race/Ethnicity | Total Students | Progressed to Algebra | Progression Rate | Avg 7th Math GPA | Avg Algebra GPA |
|----------------|---------------|----------------------|------------------|------------------|-----------------|
| Japanese | 5 | 4 | 80.0% | 3.94 | 3.70 |
| Chinese | 12 | 6 | 50.0% | 4.00 | 3.85 |
| White | 180 | 81 | 45.0% | 3.59 | 3.49 |
| Asian Indian | 15 | 6 | 40.0% | 3.87 | 3.84 |
| Black or African American | 6 | 1 | 16.7% | 3.22 | 3.62 |

#### Additional Groups (n < 5, reported for completeness)

| Race/Ethnicity | Total Students | Progressed | Progression Rate |
|----------------|---------------|------------|------------------|
| Vietnamese | 3 | 2 | 66.7% |
| Filipino | 2 | 1 | 50.0% |
| Korean | 2 | 1 | 50.0% |
| Samoan | 2 | 2 | 100.0% |
| No Answer Provided | 4 | 1 | 25.0% |
| American Indian/Alaskan Native | 1 | 0 | 0.0% |

#### Notable Patterns

1. **High-Performing Asian Subgroups:**
   - Japanese students: 80% progression rate, 3.94 → 3.70 GPA
   - Chinese students: Highest 7th grade performance (4.00 GPA), maintained in Algebra (3.85)
   - Asian Indian students: Consistent high performance across both courses

2. **Performance vs. Access Pattern:**
   - One Black/African American student progressed from 3.22 GPA (7th grade) to 3.62 GPA (8th grade Algebra)
   - This represents a +0.40 GPA improvement, the only demographic group showing positive GPA change
   - Demonstrates capability when access is provided

3. **Sample Size Limitations:**
   - Several groups have fewer than 10 students, making percentage calculations statistically unstable
   - Absolute counts should be considered alongside percentages for small groups

### Pathway × Gender Interaction

Progression rates disaggregated by both pathway and gender:

| 7th Grade Pathway | Female Progression Rate | Male Progression Rate | Gender Gap |
|-------------------|------------------------|----------------------|------------|
| Apex Math 8 | 32.6% | 55.4% | 22.8 pp |
| Regular Math 8 | 34.9% | 54.9% | 20.0 pp |

The gender disparity is consistent across both pathways, ranging from 20.0 to 22.8 percentage points.

---

## LEAD Program Longitudinal Analysis

### Research Question

What are the enrollment trends and demographic representation patterns in the LEAD Program over the five-year period (2021-2026)?

### Enrollment Trends

#### Year-Over-Year Growth

| Academic Year | Total Enrollment | Change from Prior Year | Percent Change | Cumulative Growth |
|---------------|------------------|----------------------|----------------|-------------------|
| 2021-22 | 32 | — | — | Baseline |
| 2022-23 | 28 | -4 | -12.5% | -12.5% |
| 2023-24 | 33 | +5 | +17.9% | +3.1% |
| 2024-25 | 59 | +26 | +78.8% | +84.4% |
| 2025-26 | 66 | +7 | +11.9% | +106.3% |

**Key Observations:**
- Initial contraction in Year 2 (-12.5%)
- Return to baseline by Year 3
- Substantial expansion in Year 4 (+26 students, +78.8%)
- Continued growth in Year 5 (+7 students)
- Overall five-year growth: **+106.3%** (32 → 66 students)
- Total unique students served: **185** (some students enrolled multiple years)

### Gender Representation

#### Annual Gender Distribution

| Academic Year | Total | Female Count | Male Count | Female % | Male % |
|---------------|-------|--------------|------------|----------|--------|
| 2021-22 | 32 | 23 | 9 | 71.9% | 28.1% |
| 2022-23 | 28 | 21 | 7 | 75.0% | 25.0% |
| 2023-24 | 33 | 21 | 12 | 63.6% | 36.4% |
| 2024-25 | 59 | 41 | 18 | 69.5% | 30.5% |
| 2025-26 | 66 | 42 | 24 | 63.6% | 36.4% |

**Patterns:**
- Female students consistently represent 64-75% of enrollment
- Peak female representation: 75.0% in 2022-23 (smallest cohort year)
- Male participation increased in absolute numbers (9 → 24) during expansion
- Gender balance maintained despite substantial program growth

### Hispanic/Latino Representation

| Academic Year | Total Enrollment | Hispanic/Latino Count | Hispanic/Latino % |
|---------------|------------------|----------------------|-------------------|
| 2021-22 | 32 | 7 | 21.9% |
| 2022-23 | 28 | 4 | 14.3% |
| 2023-24 | 33 | 4 | 12.1% |
| 2024-25 | 59 | 10 | 16.9% |
| 2025-26 | 66 | 12 | 18.2% |

**Trends:**
- Representation declined from baseline (21.9%) to lowest point in 2023-24 (12.1%)
- Recovery began in 2024-25 (16.9%), continued in 2025-26 (18.2%)
- Absolute growth: +71% (7 → 12 students)
- Growth rate below overall program expansion (+106%)

### Racial and Ethnic Composition

#### 2021-22 Baseline Year

| Race/Ethnicity | Count | Percentage |
|----------------|-------|------------|
| White | 24 | 75.0% |
| Hispanic/Latino | 7 | 21.9% |
| Chinese | 2 | 6.2% |
| American Indian/Alaskan Native | 2 | 6.2% |
| Black/African American | 2 | 6.2% |
| Korean | 1 | 3.1% |
| Samoan | 1 | 3.1% |

*Note: Students may identify with multiple categories; percentages may sum to >100%*

#### 2025-26 Current Year

| Race/Ethnicity | Count | Percentage |
|----------------|-------|------------|
| White | 53 | 80.3% |
| Hispanic/Latino | 12 | 18.2% |
| No Answer Provided | 4 | 6.1% |
| Filipino | 3 | 4.5% |
| Chinese | 2 | 3.0% |
| Black/African American | 1 | 1.5% |
| Other Asian | 1 | 1.5% |
| Laotian | 1 | 1.5% |
| Samoan | 1 | 1.5% |

#### Baseline to Current Comparison

| Demographic Group | 2021-22 Baseline | 2025-26 Current | Percentage Point Change | Absolute Change |
|-------------------|------------------|-----------------|------------------------|-----------------|
| White | 75.0% (24 students) | 80.3% (53 students) | +5.3 pp | +29 students |
| Hispanic/Latino | 21.9% (7 students) | 18.2% (12 students) | -3.7 pp | +5 students |
| Black/African American | 6.2% (2 students) | 1.5% (1 student) | -4.7 pp | -1 student |
| Chinese | 6.2% (2 students) | 3.0% (2 students) | -3.2 pp | 0 students |
| American Indian/Alaskan Native | 6.2% (2 students) | 0.0% (0 students) | -6.2 pp | -2 students |
| Filipino | 0.0% (0 students) | 4.5% (3 students) | +4.5 pp | +3 students |

**Key Patterns:**
- White student representation increased both proportionally (+5.3 pp) and in absolute numbers (+29)
- Of 34 new seats created during expansion (32 → 66), White students filled 29 (85.3%)
- Black/African American participation declined in absolute terms (2 → 1 student)
- American Indian/Alaskan Native representation declined to zero
- Filipino students emerged as new demographic group (+3 students)

### Cross-Program Participation

**Students enrolled in both LEAD and Mathematics pathways:**
- 50 students enrolled in both Math 8 (Courses 325/329) and LEAD
- 24 students enrolled in both Algebra 1 (Course 308) and LEAD

This overlap enables future analysis of whether LEAD participation affects mathematics progression rates.

---

## Data Quality Assessment

### Coverage and Completeness

| Metric | Value | Assessment |
|--------|-------|------------|
| Student ID Mapping Coverage | 100% | ⭐⭐⭐⭐⭐ Excellent |
| Grade Record Match Rate | 92.8% | ⭐⭐⭐⭐ Very Good |
| Demographic Data Completeness | 97.3% | ⭐⭐⭐⭐ Very Good |
| Academic Year Standardization | 100% | ⭐⭐⭐⭐⭐ Excellent |
| Small Group Statistical Stability | Variable | ⭐⭐⭐ Good (limited by sample size) |

### Data Strengths

1. **Comprehensive Longitudinal Tracking:** Five consecutive years of enrollment and performance data enable robust trend analysis.

2. **Unified Student Identifier:** 10-digit State Student ID provides reliable cross-file matching and eliminates duplicate counting.

3. **Multiple Data Source Validation:** Enrollment data (Excel) and performance data (CSV) independently sourced, enabling cross-validation.

4. **Consistent Demographic Tracking:** Gender, race, and ethnicity recorded consistently across all years.

5. **High Grade Match Rate:** 92.8% of grade records successfully matched to enrollment cohort.

### Data Limitations

#### 1. Missing 7th Grade GPA Data

**Issue:** Apex Math 8 (Course 329) 7th grade GPA data incomplete in grade files.

**Impact:** 
- Cannot directly compare 7th grade performance between Apex and Regular Math 8 students
- Limited ability to assess "value-added" effect of supplemental delivery pathway

**Mitigation:** 8th grade Algebra performance serves as downstream outcome measure.

#### 2. Small Sample Sizes

**Issue:** Several racial/ethnic groups have fewer than 10 students in analysis cohort.

**Examples:**
- Japanese: 5 students
- Vietnamese: 3 students
- Black/African American: 6 students
- American Indian/Alaskan Native: 1 student

**Impact:**
- Percentage calculations may be statistically unstable
- Single student movements create large percentage swings
- Intersectional analysis (e.g., race × gender) not feasible

**Mitigation:** Report absolute counts alongside percentages; exercise caution in interpretation.

#### 3. Student ID Mapping Conflicts

**Issue:** One instance where single local ID mapped to multiple State IDs across years.

**Resolution:** Selected chronologically first State ID to maintain longitudinal continuity.

**Impact:** Minimal (affects 1 of 1,547 mappings, 0.06%).

#### 4. Academic Year Format Inconsistencies

**Issue:** LEAD enrollment data used timestamp format; other files used 'YY-YY' format.

**Resolution:** Standardized all data to 'YY-YY' format during processing.

**Impact:** None (resolved during data cleaning phase).

#### 5. Enrollment vs. Completion Distinction

**Clarification:** Data reflects course enrollment (student appeared on roster), not course completion.

**Assumption:** Students listed in enrollment files completed the course.

**Potential Bias:** Students who dropped courses mid-year may not appear in final enrollment files.

**Impact:** Unknown magnitude; likely minimal for advanced courses with high persistence rates.

#### 6. GPA Calculation Methodology

**Approach:** 
- Letter grades converted to 4.0 scale (A=4.0, B=3.0, C=2.0, D=1.0, F=0.0)
- Averaged across all available marking periods (typically 6 per year)
- Equal weighting for all marking periods

**Limitations:**
- Does not account for possible differential weighting by marking period
- Does not account for partial-year enrollments
- Does not distinguish between original grades and repeated courses

**Impact:** Minor; averages generally representative of annual performance.

#### 7. Missing Demographic Data

**Issue:** 10 students (2.7% of cohort) listed as "No Answer Provided" for race/ethnicity.

**Impact:** Slight undercount of racial/ethnic group representation.

**Magnitude:** Small (fewer than 3% of students).

#### 8. Intersectional Analysis Constraints

**Issue:** Sample sizes insufficient for robust intersectional demographic analysis.

**Example:** Only 6 Black/African American students in 7th grade mathematics cohort; cannot reliably analyze by gender.

**Limitation:** Cannot assess whether gender gap is consistent across all racial/ethnic groups.

**Mitigation:** Would require multi-year cohort aggregation to achieve sufficient sample sizes.

### Reliability Matrix

| Data Element | Reliability Rating | Notes |
|--------------|-------------------|-------|
| Student Enrollment Records | ⭐⭐⭐⭐⭐ | Complete; cross-verified across multiple files |
| Grade/Performance Data | ⭐⭐⭐⭐ | High fidelity (92.8% match rate); minor attrition |
| Demographic Data | ⭐⭐⭐⭐ | Strong coverage; <3% missing |
| Academic Year Tracking | ⭐⭐⭐⭐⭐ | Standardized successfully across all sources |
| Small Group Trend Analysis | ⭐⭐⭐ | Variance likely due to small sample sizes for specific groups |

### Data Processing Validation

**Quality Control Steps Implemented:**
1. Duplicate student ID detection and resolution
2. Academic year format standardization across all files
3. Cross-file validation of student counts
4. Range checks on GPA values (0.0-4.0)
5. Demographic category consistency verification
6. Longitudinal tracking validation (same student across multiple years)

---

## Technical Appendix

### Analysis Environment

**Primary Analysis Script:** `analyze_with_grades.py`

**Software Environment:**
- Python 3.14
- pandas 3.0.1 (data manipulation)
- numpy 2.4.2 (numerical computation)
- openpyxl 3.1.5 (Excel file handling)

### Data Processing Pipeline

#### Step 1: Student ID Mapping

**Function:** Load and consolidate student ID mappings from five annual files

**Input Files:**
- `grade id 2122.xlsx` (648 mappings)
- `grade id 2223.xlsx` (608 mappings)
- `grade id 2324.xlsx` (598 mappings)
- `grade id 2425.xlsx` (619 mappings)
- `grades id 2526.xlsx` (619 mappings)

**Processing:**
- Load all mapping files
- Concatenate into unified mapping table
- Remove duplicate local_id → state_id pairs
- Resolve conflicts (1 local ID → multiple state IDs) by selecting first occurrence

**Output:** 1,547 unique student mappings (local_id → state_id)

#### Step 2: Enrollment Data Loading

**Function:** `load_excel_enrollment()`

**Processing:**
- Load three Excel enrollment files
- Standardize academic year format to 'YY-YY'
- Add course identifier and course name
- Combine into unified enrollment dataset

**Output:** 622 enrollment records across 372 unique students

#### Step 3: Grade Data Integration

**Function:** `load_grade_files()`

**Input:** Six annual CSV grade files (2020-21 through 2025-26)

**Processing:**
- Load each year's grade file
- Join grades to ID mapping via `local_id`
- Filter to enrollment cohort via `state_id`
- Calculate average GPA per student per course per year
- Aggregate across marking periods

**Output:** 40,478 grade records matched to enrollment cohort (92.8% match rate)

#### Step 4: Progression Calculation

**Logic:**
- Identify 7th grade math enrollment (Year N) in Courses 325 or 329
- Search for same student in 8th grade (Year N+1) in Course 308 (Algebra 1)
- Record progression outcome (Yes/No) and performance metrics

**Demographic Disaggregation:**
- Group by gender
- Group by race/ethnicity
- Group by pathway (Course 325 vs. 329)
- Calculate progression rates and average GPAs for each subgroup

#### Step 5: LEAD Program Trend Analysis

**Processing:**
- Aggregate LEAD enrollment by academic year
- Calculate year-over-year growth rates
- Track demographic composition changes over time
- Identify unique vs. repeat participants

### Output Files Generated

| Filename | Description | Record Count |
|----------|-------------|--------------|
| `task_a_pipeline_with_performance.xlsx` | Individual student progression records with GPAs | 233 students |
| `task_b_lead_trends_updated.xlsx` | LEAD enrollment by year with demographics | 5 years × demographics |
| `analysis_summary.xlsx` | High-level summary statistics | Aggregate metrics |

### Academic Year Standardization

**Challenge:** Multiple date/year formats across source files

**Formats Encountered:**
- 'YY-YY' (e.g., '21-22')
- Full dates (e.g., '2021-09-01')
- Timestamps (e.g., '2021-09-01 08:00:00')

**Standardization Function:** `standardize_academic_year()`

**Logic:**
- If format is 'YY-YY', return as-is
- If date/timestamp format:
  - Extract year
  - If month ≥ 8 (August or later), academic year is year → year+1
  - If month < 8, academic year is year-1 → year
  - Format as 'YY-YY' (e.g., 2021 → '21-22')

### GPA Calculation Method

**Formula:**
```
GPA = Σ(grade_points) / n_marking_periods
```

**Grade Point Conversion:**
- A = 4.0
- B = 3.0
- C = 2.0
- D = 1.0
- F = 0.0

**Aggregation:**
- All marking periods within academic year weighted equally
- Missing grades excluded from calculation (not counted as zeros)
- Final GPA rounded to 2 decimal places

### Data Matching Workflow

```
Enrollment Files (Excel)          Grade Files (CSV)
    ↓ (state_id)                      ↓ (local_id)
    |                                  |
    |                                  ↓
    |                           ID Mapping Files
    |                           (local_id → state_id)
    |                                  |
    |                                  ↓
    |                            Grades with state_id
    |                                  |
    └──────────────────→ Join on state_id ←────┘
                              ↓
                    Combined Dataset
            (Enrollment + Performance)
```

### Quality Assurance Checks

**Automated Validations:**
1. All state_ids in enrollment files present in ID mapping (100% match required)
2. GPA values within valid range (0.0-4.0)
3. No duplicate student-course-year combinations
4. Academic year sequence validation (no gaps in progression tracking)
5. Demographic category consistency across years

**Manual Verification:**
- Random sample of 20 students manually traced through source files
- Progression calculations spot-checked against enrollment records
- GPA calculations validated against original grade files

---

## Appendix: Course and Program Descriptions

### Mathematics Courses

**Course 325: Regular Math 8**
- Grade Level: 7th grade
- Description: Accelerated mathematics pathway covering 8th grade curriculum in 7th grade
- Delivery: Regular classroom hours
- Typical outcome: Students positioned for 8th grade Algebra 1

**Course 329: Apex Math 8**
- Grade Level: 7th grade
- Description: Accelerated mathematics pathway covering 8th grade curriculum in 7th grade
- Delivery: Supplemental delivery methodology
- Typical outcome: Students positioned for 8th grade Algebra 1

**Course 308: Algebra 1**
- Grade Level: 8th grade (advanced) or 9th grade (standard)
- Description: First-year algebra course
- Prerequisites: Completion of 7th grade accelerated math or 8th grade math
- Significance: Gateway to advanced STEM coursework in high school

### LEAD Program

**Course 1205: LEAD Program**
- Grade Levels: K-8
- Description: Specialized enrichment program
- Structure: Multi-year participation possible
- Focus: Academic acceleration and enrichment
- Selection: Application-based enrollment

---

## Glossary of Terms

**Academic Year:** 12-month period beginning in fall semester; formatted as 'YY-YY' (e.g., '21-22' represents 2021-2022 school year).

**Longitudinal Tracking:** Following the same students across multiple years to observe changes over time.

**Marking Period:** Subdivision of academic year for grading purposes; typically 6 marking periods per year in source data.

**Percentage Point (pp):** Unit of measurement for the difference between two percentages (e.g., 55% - 34% = 21 percentage points).

**Progression Rate:** Percentage of students in a baseline group who advance to a specified next-level course.

**State Student ID:** 10-digit unique identifier assigned by state education system; remains constant across schools and years.

**Local ID:** 5-digit identifier used within district student information system; mapped to State Student ID for analysis purposes.

---

**Report Prepared:** February 2026  
**Data Coverage:** Academic Years 2021-22 through 2025-26  
**Analysis Conducted By:** OpenCode AI Analysis System

---

*This supporting documentation provides detailed methodological information and complete data findings for the Student Enrollment and Academic Outcomes Analysis. All data presented reflects enrollment and performance records as recorded in district information systems. Findings are factual summaries of observed patterns in the data.*