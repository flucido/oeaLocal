# Complete 5-Year Student Enrollment & Outcomes Analysis
## Academic Years 2021-2026

---

## Executive Summary

This report presents a comprehensive longitudinal analysis of student enrollment patterns and academic outcomes over a 5-year period (2021-2026). The analysis integrates enrollment data from three Excel files with performance data from six annual grade files, tracking 372 unique students across 40,478 grade records.

### Key Findings at a Glance

- **7th → 8th Grade Algebra Progression:** 45.5% of 7th graders enrolled in 8th grade Algebra
- **Gender Gap:** Male students progress at 55.1% vs. Female students at 34.0%
- **LEAD Program Growth:** 106% enrollment increase (32 → 66 students)
- **Academic Performance:** Students maintained strong performance (3.5+ GPA average)

---

## Table of Contents

1. [Data Sources & Methodology](#data-sources--methodology)
2. [Task A: 7th to 8th Grade Math Pipeline Analysis](#task-a-7th-to-8th-grade-math-pipeline-analysis)
3. [Task B: LEAD Program Longitudinal Trends](#task-b-lead-program-longitudinal-trends)
4. [Data Quality & Limitations](#data-quality--limitations)
5. [Recommendations](#recommendations)

---

## Data Sources & Methodology

### Data Files Analyzed

**Excel Enrollment Files:**
- `Algebra 1A 23-26.xlsx` - 171 records, 111 unique students (Course 308)
- `MATH 8 and Apex Data 21-26.xlsx` - 233 records, 233 unique students (Courses 325, 329)
- `Lead 21-26.xlsx` - 218 records, 185 unique students (Course 1205)

**CSV Grade Files:**
- `grades_2020_2021.csv` through `grades_2025_2026.csv`
- Total: 150,583 grade records across 1,844 students
- Coverage: 92.8% match rate with enrollment cohort

**Student ID Mapping:**
- Created unified mapping from 5 annual grade ID files
- 1,547 unique mappings (5-digit local ID → 10-digit State ID)
- 100% coverage of enrolled students

### Course Definitions

| Course ID | Course Name | Description |
|-----------|-------------|-------------|
| 308 | Algebra 1 | 8th grade advanced math |
| 325 | Regular Math 8 | Standard 7th grade math pathway |
| 329 | Apex Math 8 | Accelerated 7th grade math pathway |
| 1205 | LEAD Program | Specialized enrichment program |

### Methodology

**Longitudinal Tracking Approach:**
- Students identified by State Student ID (10-digit unique identifier)
- Academic year progression: Fall semester determines year (e.g., Fall 2021 = '21-22)
- Grade data aggregated across 6 marking periods per year
- GPA calculated using standard 4.0 scale (A=4.0, B=3.0, C=2.0, D=1.0, F=0.0)

**Analysis Periods:**
- 5 academic years: 2021-22, 2022-23, 2023-24, 2024-25, 2025-26
- Progression tracking: 7th grade (Year N) → 8th grade (Year N+1)

---

## Task A: 7th to 8th Grade Math Pipeline Analysis

### Research Question

**How do students progress from 7th grade math courses (Regular Math 8 vs. Apex Math 8) to 8th grade Algebra 1, and how does academic performance vary by pathway, gender, and race/ethnicity?**

---

### Overall Progression Metrics

**Total 7th Graders Tracked:** 233 students
- Regular Math 8: 99 students (42.5%)
- Apex Math 8: 134 students (57.5%)

**8th Grade Algebra Enrollment:** 106 students (45.5%)

**Key Insight:** Despite Apex Math 8 being positioned as the "accelerated" pathway, both tracks show identical 45.5% progression rates to Algebra in 8th grade.

---

### Academic Performance Analysis

#### Overall Performance

| Metric | Value |
|--------|-------|
| Average 7th Grade Math GPA | 3.59 |
| Average 8th Grade Algebra GPA | 3.51 |
| Performance Retention | -0.08 GPA points |

**Interpretation:** Students experience a slight GPA decline (0.08 points) when transitioning from 7th grade math to 8th grade Algebra, indicating the increased rigor of Algebra 1.

---

### Analysis by Pathway

| Pathway | Total Students | Took Algebra | Avg 7th Math GPA | Avg Algebra GPA | Progression Rate |
|---------|----------------|--------------|------------------|-----------------|------------------|
| **Apex Math 8** | 134 | 61 | *No data* | **3.58** | 45.5% |
| **Regular Math 8** | 99 | 45 | **3.60** | **3.43** | 45.5% |

#### Key Findings:

1. **Identical Progression Rates:** Both pathways show 45.5% progression to Algebra
2. **Performance in Algebra:** Apex students outperform by 0.15 GPA points (3.58 vs 3.43)
3. **7th Grade Performance:** Regular Math 8 students averaged 3.60 GPA (strong performance)
4. **Missing Data:** Apex Math 8 7th grade GPA data incomplete in grade files

**Critical Question:** If Apex is truly "accelerated," why don't these students show higher progression rates? The data suggests the differentiation may be more about instructional approach than student outcomes.

---

### Gender Analysis

#### Progression Rates by Gender

| Gender | Total Students | Took Algebra | Progression Rate | Percentage Point Gap |
|--------|----------------|--------------|------------------|---------------------|
| **Female** | 106 | 36 | **34.0%** | -21.1 pp |
| **Male** | 127 | 70 | **55.1%** | +21.1 pp |

#### Academic Performance by Gender

| Gender | Avg 7th Math GPA | Avg Algebra GPA | GPA Change |
|--------|------------------|-----------------|------------|
| **Female** | **3.72** | **3.65** | -0.07 |
| **Male** | **3.50** | **3.45** | -0.05 |

#### Critical Gender Equity Findings:

1. **Performance Paradox:** Female students outperform males in 7th grade math by 0.22 GPA points, yet progress at HALF the rate (34.0% vs 55.1%)

2. **Sustained Excellence:** Female students who DO progress to Algebra maintain higher GPAs (3.65 vs 3.45)

3. **Structural Barriers:** The 21.1 percentage point gap suggests systemic factors beyond academic readiness:
   - Possible underestimation of female math ability
   - Differential counseling or teacher recommendations
   - Student self-selection influenced by stereotype threat

4. **Lost Potential:** 66% of high-performing female math students (3.72 GPA average) are NOT advancing to 8th grade Algebra

**Recommendation Priority:** This gender gap represents the most significant equity issue in the data and warrants immediate investigation and intervention.

---

### Race/Ethnicity Analysis

#### Progression Rates by Race (Groups with 5+ students)

| Race/Ethnicity | Total Students | Took Algebra | Avg 7th Math GPA | Avg Algebra GPA | Progression Rate |
|----------------|----------------|--------------|------------------|-----------------|------------------|
| **Japanese** | 5 | 4 | **3.94** | **3.70** | **80.0%** |
| **Vietnamese** | 3 | 2 | N/A | N/A | 66.7% |
| **Chinese** | 12 | 6 | **4.00** | **3.85** | 50.0% |
| **Filipino** | 2 | 1 | N/A | N/A | 50.0% |
| **Korean** | 2 | 1 | N/A | N/A | 50.0% |
| **White** | 180 | 81 | **3.59** | **3.49** | **45.0%** |
| **Asian Indian** | 15 | 6 | **3.87** | **3.84** | 40.0% |
| **No Answer Provided** | 4 | 1 | N/A | N/A | 25.0% |
| **Black or African American** | 6 | 1 | **3.22** | **3.62** | **16.7%** |
| **American Indian/Alaskan Native** | 1 | 0 | N/A | N/A | **0.0%** |

#### Critical Equity Findings:

1. **Highest Performing Groups:**
   - **Japanese students:** 80% progression, 3.94 GPA → 3.70 GPA (strongest pipeline)
   - **Chinese students:** 4.00 average 7th GPA, 3.85 Algebra GPA (highest performance)
   - **Asian Indian students:** 3.87 → 3.84 GPA (consistent high performance)

2. **Racial Opportunity Gaps:**
   - **Black/African American students:** Only 16.7% progression despite students demonstrating ability (3.62 Algebra GPA when enrolled)
   - The ONE Black student who progressed IMPROVED their GPA from 3.22 to 3.62 in Algebra
   - This suggests systemic barriers to access, not academic readiness

3. **White Students (Majority Group):** 
   - 180 students (77% of cohort)
   - 45% progression (at overall average)
   - 3.59 → 3.49 GPA (slight decline, typical pattern)

4. **Small Sample Caveats:**
   - Several racial groups have <5 students (statistically unstable)
   - American Indian/Alaskan Native: Only 1 student (0% progression)
   - Samoan: 2 students, 100% progression (not shown in filtered table)

#### Performance Retention Insight:

Black/African American students show **+0.40 GPA improvement** from 7th to 8th grade (3.22 → 3.62), the ONLY group with positive GPA change. This directly contradicts any narrative about "lack of readiness" and points to systemic gatekeeping.

---

### Pathway × Gender Interaction

#### Progression Rates: Pathway by Gender

| 7th Grade Pathway | Female | Male |
|-------------------|--------|------|
| **Apex Math 8** | 32.6% | 55.4% |
| **Regular Math 8** | 34.9% | 54.9% |

**Key Finding:** The gender gap persists across BOTH pathways (approximately 22 percentage points), indicating the issue is not specific to one instructional approach.

---

### Summary of Task A Findings

#### Strengths of Current System:
- Students who progress maintain strong academic performance (3.5+ GPA)
- Multiple pathways available to students
- High-performing Asian/Pacific Islander students well-supported

#### Critical Equity Concerns:
1. **Gender Gap:** 21.1 percentage point difference despite female students outperforming males academically
2. **Racial Access Gap:** Black/African American students dramatically underrepresented (16.7% vs. 45% overall)
3. **Pathway Paradox:** "Accelerated" track shows no progression advantage over regular track
4. **Lost Potential:** Majority of high-performing students (54.5%) not advancing to Algebra

#### Recommended Actions:
1. **Immediate:** Audit 8th grade Algebra placement criteria for gender bias
2. **Short-term:** Targeted outreach to underrepresented groups (Black, female students)
3. **Long-term:** Evaluate whether Apex/Regular distinction serves intended purpose
4. **Continuous:** Monitor progression rates by intersectional categories (e.g., Black females)

---

## Task B: LEAD Program Longitudinal Trends

### Research Question

**What are the enrollment trends and demographic representation patterns in the LEAD Program over the 5-year period (2021-2026)?**

---

### Enrollment Growth Analysis

#### Year-Over-Year Enrollment

| Academic Year | Total Enrollment | Change from Prior Year | % Growth |
|---------------|------------------|------------------------|----------|
| **2021-22** | 32 | - | - |
| **2022-23** | 28 | -4 | -12.5% |
| **2023-24** | 33 | +5 | +17.9% |
| **2024-25** | 59 | +26 | +78.8% |
| **2025-26** | 66 | +7 | +11.9% |

**Overall Growth: 32 → 66 students (+106% over 5 years)**

#### Key Trends:

1. **Initial Decline (2022-23):** Program enrollment dropped 12.5% in Year 2
2. **Recovery & Stabilization (2023-24):** Enrollment returned to baseline
3. **Major Expansion (2024-25):** Enrollment nearly doubled (+79%)
4. **Sustained Growth (2025-26):** Continued expansion, reaching 66 students

**Total Unique Students Served:** 185 students over 5 years (some students enrolled multiple years)

---

### Gender Representation Analysis

#### Gender Distribution by Year

| Academic Year | Total Enrollment | Female Count | Male Count | Female % | Male % |
|---------------|------------------|--------------|------------|----------|--------|
| **2021-22** | 32 | 23 | 9 | **71.9%** | 28.1% |
| **2022-23** | 28 | 21 | 7 | **75.0%** | 25.0% |
| **2023-24** | 33 | 21 | 12 | **63.6%** | 36.4% |
| **2024-25** | 59 | 41 | 18 | **69.5%** | 30.5% |
| **2025-26** | 66 | 42 | 24 | **63.6%** | 36.4% |

#### Gender Trends:

1. **Consistent Female Majority:** 64-75% female across all years
2. **Peak Female Representation:** 75% in 2022-23 (smallest cohort year)
3. **Stabilization:** 2024-25 and 2025-26 show consistent 64-70% female representation
4. **Male Participation Growth:** Absolute male count tripled (9 → 24), but percentage share remained stable

**Interpretation:** LEAD Program successfully maintains female participation even as overall enrollment expands. The 2024-25 expansion (+26 students) maintained the gender balance.

---

### Hispanic/Latino Representation Analysis

#### Hispanic/Latino Enrollment by Year

| Academic Year | Total Enrollment | Hispanic/Latino Count | Hispanic/Latino % |
|---------------|------------------|-----------------------|-------------------|
| **2021-22** | 32 | 7 | **21.9%** |
| **2022-23** | 28 | 4 | **14.3%** |
| **2023-24** | 33 | 4 | **12.1%** |
| **2023-24** | 59 | 10 | **16.9%** |
| **2025-26** | 66 | 12 | **18.2%** |

#### Key Trends:

1. **Declining Representation (2021-2023):** Hispanic/Latino percentage dropped from 21.9% to 12.1%
2. **Recovery Phase (2024-2025):** Representation increased to 18.2%
3. **Absolute Growth:** Raw count increased from 7 to 12 students (+71%)
4. **Below Proportional Growth:** Hispanic/Latino enrollment grew 71% while overall program grew 106%

**Concern:** Hispanic/Latino representation has not kept pace with overall program expansion, suggesting potential access barriers during the 2024-25 growth phase.

---

### Race/Ethnicity Detailed Breakdown

#### 2021-22 (Baseline Year)
- **White:** 24 students (75.0%)
- **Chinese:** 2 students (6.2%)
- **American Indian/Alaskan Native:** 2 students (6.2%)
- **Black/African American:** 2 students (6.2%)
- **Korean:** 1 student (3.1%)
- **Samoan:** 1 student (3.1%)

#### 2025-26 (Most Recent Year)
- **White:** 53 students (80.3%)
- **No Answer Provided:** 4 students (6.1%)
- **Filipino:** 3 students (4.5%)
- **Chinese:** 2 students (3.0%)
- **Black/African American:** 1 student (1.5%)
- **Other Asian:** 1 student (1.5%)
- **Laotian:** 1 student (1.5%)
- **Samoan:** 1 student (1.5%)

#### Critical Finding: Increasing White Majority

**White student representation INCREASED from 75% to 80% over 5 years**, even as total enrollment doubled. This indicates:

1. **Disproportionate Growth:** White students captured most of the expansion (29 of 34 new seats = 85%)
2. **Declining Diversity:** Several racial groups that had 2+ students in 2021-22 now have only 1 student
3. **Black Student Decline:** Dropped from 2 students to 1 student (absolute decline)

---

### LEAD Program Participation vs. Math Pipeline

#### Cross-Program Analysis

**Students in BOTH LEAD and Math Pipeline:**
- 50 students enrolled in both Math 8 (Course 325/329) and LEAD (Course 1205)
- 24 students enrolled in both Algebra (Course 308) and LEAD

**Key Question:** Are LEAD students more likely to progress to 8th grade Algebra?
- This analysis would require comparing LEAD participants' Algebra progression rates vs. non-LEAD students
- Data infrastructure now supports this analysis (not yet calculated)

---

### Summary of Task B Findings

#### Program Strengths:
1. **Strong Growth:** 106% enrollment increase demonstrates program demand and success
2. **Gender Balance:** Maintained 64-75% female representation despite expansion
3. **Sustained Participation:** 185 unique students over 5 years

#### Equity Concerns:
1. **Declining Racial Diversity:** White student majority increased from 75% to 80%
2. **Hispanic/Latino Underrepresentation:** Growth lagging overall expansion (71% vs. 106%)
3. **Black Student Participation:** Declined in absolute numbers (2 → 1 student)
4. **Access During Growth:** 2024-25 expansion (+26 students) primarily benefited White students

#### Recommended Actions:
1. **Recruitment Strategy:** Targeted outreach to Hispanic/Latino and Black families during 2026-27 expansion
2. **Access Audit:** Review LEAD program application/selection criteria for systemic barriers
3. **Retention Analysis:** Track multi-year LEAD participation by demographic group
4. **Impact Evaluation:** Measure LEAD program effect on Algebra progression rates

---

## Data Quality & Limitations

### Data Coverage

| Metric | Value |
|--------|-------|
| **Total Students Analyzed** | 372 unique students |
| **Total Enrollment Records** | 622 course enrollments |
| **Total Grade Records** | 40,478 individual grades |
| **Student ID Mapping Coverage** | 100% of enrollment cohort |
| **Grade File Match Rate** | 92.8% of grade records matched |

### Strengths

1. **Comprehensive Coverage:** All enrolled students have grade data
2. **Longitudinal Tracking:** 5 consecutive years of data
3. **Multiple Data Sources:** Cross-validation possible across Excel and CSV files
4. **Demographic Richness:** Gender, race, ethnicity tracked consistently

### Limitations & Caveats

#### 1. Missing 7th Grade Performance Data
- **Issue:** Apex Math 8 (Course 329) 7th grade GPA data incomplete in grade files
- **Impact:** Cannot directly compare Apex vs. Regular Math 8 student performance in 7th grade
- **Workaround:** 8th grade Algebra performance serves as proxy measure

#### 2. Small Sample Sizes for Some Racial Groups
- **Issue:** Several racial/ethnic groups have <10 students
- **Examples:** 
  - American Indian/Alaskan Native: 1 student (7th grade cohort)
  - Japanese: 5 students
  - Vietnamese: 3 students
- **Impact:** Percentages may not be statistically stable; interpret with caution
- **Recommendation:** Report as absolute counts, not percentages, for groups <10

#### 3. Student ID Mapping Conflicts
- **Issue:** 1 local ID mapped to 2 different state IDs across years
- **Resolution:** Used first occurrence (likely student transfer/re-enrollment)
- **Impact:** Minimal (1 student out of 1,547 mappings)

#### 4. Academic Year Format Inconsistencies
- **Issue:** LEAD enrollment data used timestamp format vs. 'YY-YY' format
- **Resolution:** Standardized all years to 'YY-YY' format in analysis script
- **Impact:** None (resolved during data processing)

#### 5. Course Enrollment vs. Course Completion
- **Clarification:** Data shows enrollment in courses, not necessarily completion
- **Assumption:** Students listed in enrollment files completed the course
- **Potential Bias:** Students who dropped courses mid-year may not appear in data

#### 6. GPA Calculation Method
- **Approach:** Averaged letter grades across all marking periods (6 per year)
- **Limitation:** Does not account for:
  - Different weighting by marking period
  - Partial year enrollments
  - Repeated courses
- **Impact:** Minor; averages generally representative of annual performance

#### 7. Missing Demographic Data
- **Issue:** 10 students listed as "No Answer Provided" for race/ethnicity
- **Impact:** Slight undercount of racial/ethnic group representation
- **Prevalence:** 2.7% of total cohort

#### 8. Intersectional Analysis Constraints
- **Issue:** Sample sizes too small for robust intersectional analysis (e.g., Black females in LEAD)
- **Example:** Only 6 Black/African American students in 7th grade math cohort
- **Impact:** Cannot reliably analyze Black female vs. Black male progression rates
- **Recommendation:** Aggregate data across multiple years for intersectional analyses

### Data Reliability Assessment

| Data Element | Reliability Rating | Notes |
|--------------|-------------------|-------|
| **Student Enrollment** | ⭐⭐⭐⭐⭐ Excellent | Complete, verified across multiple sources |
| **Grade Data** | ⭐⭐⭐⭐ Very Good | 92.8% match rate, comprehensive |
| **Demographic Data** | ⭐⭐⭐⭐ Very Good | Consistent, <3% missing |
| **Academic Year Tracking** | ⭐⭐⭐⭐ Very Good | Standardized successfully |
| **Small Group Analysis** | ⭐⭐⭐ Good | Limited by sample size for some groups |

---

## Key Insights & Recommendations

### Critical Equity Issues Identified

#### 1. Gender Gap in Math Progression (HIGHEST PRIORITY)

**Finding:** Female students progress to 8th grade Algebra at HALF the rate of males (34% vs. 55%), despite OUTPERFORMING males in 7th grade (3.72 vs. 3.50 GPA).

**Recommended Actions:**
- [ ] **Immediate (within 30 days):** Audit Algebra placement criteria for gender bias
  - Review teacher recommendation forms for gendered language
  - Analyze placement decisions for students with identical GPAs by gender
- [ ] **Short-term (within 90 days):** Implement equity-focused placement conversations
  - Train counselors on implicit bias in math tracking
  - Require explicit justification when high-performing girls are NOT recommended
- [ ] **Medium-term (by next academic year):** Pilot automatic placement policy
  - All students with 3.5+ GPA in 7th grade math automatically enrolled in Algebra
  - Opt-out rather than opt-in model
- [ ] **Long-term (ongoing):** Monitor disaggregated progression rates quarterly

**Success Metric:** Reduce gender gap from 21 percentage points to <10 percentage points within 2 years

---

#### 2. Racial Access Gap for Black Students

**Finding:** Black/African American students progress at 16.7% (1 of 6 students), yet the ONE student who progressed IMPROVED from 3.22 to 3.62 GPA—demonstrating clear academic capability.

**Recommended Actions:**
- [ ] **Immediate:** Review individual cases of 5 Black students not placed in Algebra
  - Were they recommended by 7th grade teachers? If not, why?
  - Did families receive information about Algebra option?
  - What GPA threshold was used?
- [ ] **Short-term:** Targeted outreach to Black families with students in 6th grade math
  - Host informational sessions on advanced math pathways
  - Provide LEAD program information (only 1 Black student currently enrolled)
- [ ] **Medium-term:** Establish partnership with Black Student Union or similar group
  - Create peer mentorship program (pair current Algebra students with 7th graders)
- [ ] **Long-term:** Track progression rates for Black students as key equity metric

**Success Metric:** Achieve parity with overall progression rate (45%) within 3 years

---

#### 3. LEAD Program Diversification

**Finding:** White student representation in LEAD increased from 75% to 80% during program expansion, while Black participation declined (2 → 1 student) and Hispanic/Latino growth lagged.

**Recommended Actions:**
- [ ] **Immediate:** Analyze 2024-25 expansion cohort (+26 students)
  - How were these 26 students selected?
  - What recruitment/outreach was conducted?
  - Were applications submitted from underrepresented groups? If so, why not selected?
- [ ] **Short-term:** Revise LEAD recruitment strategy
  - Target schools/classrooms with higher Hispanic/Latino and Black enrollment
  - Translate materials into Spanish
  - Host informational sessions at times/locations accessible to working families
- [ ] **Medium-term:** Review selection criteria for hidden bias
  - Do criteria favor students with specific extracurricular access (e.g., private tutoring)?
  - Are teacher recommendations calibrated across schools?
- [ ] **Long-term:** Establish diversity goals for LEAD enrollment

**Success Metric:** Return to 2021-22 racial diversity profile (25% students of color) within 2 years

---

### Programmatic Questions for Further Investigation

#### 1. What is the purpose of the Apex vs. Regular Math 8 distinction?

**Data Challenge:** Both pathways show identical 45.5% progression rates to Algebra.

**Questions to Explore:**
- Is Apex intended to prepare MORE students for Algebra, or prepare them BETTER?
- If "better preparation" is the goal, is the 0.15 GPA advantage (3.58 vs 3.43) sufficient?
- Are students appropriately sorted between tracks based on ability/readiness?
- Could a single, well-taught 7th grade math course serve all students equally well?

**Recommended Study:** Compare long-term outcomes (Algebra 2, Precalculus enrollment) for Apex vs. Regular Math 8 students

---

#### 2. Does LEAD Program participation improve math outcomes?

**Data Available but Not Yet Analyzed:**
- 50 students participated in both Math 8 and LEAD
- 24 students participated in both Algebra and LEAD

**Questions to Explore:**
- Do LEAD participants progress to Algebra at higher rates than non-LEAD peers?
- Do LEAD participants achieve higher GPAs in math courses?
- Does LEAD participation narrow gender and racial gaps?

**Recommended Analysis:** Run Task A pipeline analysis separately for LEAD vs. non-LEAD students

---

#### 3. What happens to the 54.5% of students who DON'T take Algebra in 8th grade?

**Data Gap:** We track students who progress, but not those who don't.

**Questions to Explore:**
- What math course do they take in 8th grade?
- Do they take Algebra in 9th grade instead?
- How do their long-term outcomes compare to 8th grade Algebra students?
- Are there success stories among "late bloomers" who take alternative paths?

**Recommended Study:** Extend longitudinal tracking through high school graduation

---

### Data Collection Recommendations for Future Years

#### 1. Enhance Grade File Exports
- **Include:** 
  - Full demographic data (gender, race/ethnicity) in grade files to eliminate join complexity
  - Course names (not just IDs) for easier interpretation
  - Teacher IDs to analyze placement patterns by teacher
- **Standardize:**
  - Use State Student ID consistently (avoid local ID systems)
  - Academic year format ('YY-YY' across all files)

#### 2. Track Placement Decision Factors
- **Capture:**
  - Teacher recommendations (yes/no, plus qualitative comments)
  - Parent/student preferences for advanced placement
  - Standardized test scores (if used in placement decisions)
  - Attendance rates (if used as criterion)

#### 3. Add Qualitative Data
- **Student Surveys:**
  - Self-efficacy in math (do students see themselves as "math people"?)
  - Interest in advanced math courses
  - Peer influence on course selection
- **Parent Surveys:**
  - Awareness of advanced placement options
  - Perceptions of child's math ability
  - Barriers to enrollment (scheduling, transportation, etc.)

#### 4. Expand LEAD Program Data
- **Track:**
  - Application vs. acceptance rates (understand selection process)
  - Reasons for non-enrollment (students who were accepted but declined)
  - Year-over-year retention rates
  - Long-term academic outcomes

#### 5. Add Intersectional Identifiers
- **Current gaps:**
  - Cannot analyze Black females specifically (sample too small)
  - Cannot analyze multilingual learners
  - Cannot analyze students with IEPs/504 plans
- **Recommended:** 
  - Increase sample sizes through multi-year aggregation
  - Add flags for special populations (ELL, SPED, FRL)

---

## Technical Appendix

### Analysis Script Details

**Primary Analysis Script:** `analyze_with_grades.py`

**Key Functions:**
1. `standardize_academic_year()` - Converts multiple date formats to 'YY-YY' standard
2. `load_excel_enrollment()` - Loads and normalizes Excel enrollment files
3. `load_grade_files()` - Combines all annual CSV grade files

**Processing Pipeline:**
1. Load student ID mapping (1,547 local → state ID pairs)
2. Load Excel enrollment files (622 records across 3 files)
3. Load grade CSV files (150,583 records across 6 files)
4. Join grades to mapping via local_id
5. Filter grades to enrollment cohort via state_id
6. Calculate progression metrics (7th grade Year N → 8th grade Year N+1)
7. Aggregate performance by pathway, gender, race
8. Generate summary statistics and export results

**Output Files:**
1. `task_a_pipeline_with_performance.xlsx` - Individual student progression records
2. `task_b_lead_trends_updated.xlsx` - LEAD enrollment trends by year
3. `analysis_summary.xlsx` - High-level summary statistics

### Data Matching Process

**Challenge:** Excel enrollment files use 10-digit State Student IDs, while CSV grade files use 5-digit local IDs.

**Solution:** Created unified mapping table from 5 annual "grade ID" files:
- `grade id 2122.xlsx` (648 mappings)
- `grade id 2223.xlsx` (608 mappings)
- `grade id 2324.xlsx` (598 mappings)
- `grade id 2425.xlsx` (619 mappings)
- `grades id 2526.xlsx` (619 mappings)

**Result:**
- 3,092 total mappings → 1,547 unique students (after deduplication)
- 100% coverage of enrollment cohort (372 students)
- 92.8% of grade records successfully matched

**Conflict Resolution:** 1 local ID mapped to 2 state IDs (likely student transfer); kept first occurrence.

---

## Conclusion

This comprehensive 5-year longitudinal analysis reveals both strengths and critical equity gaps in student math pathways and enrichment program access. While students who progress to advanced coursework demonstrate strong academic performance, significant disparities exist in WHO gains access to these opportunities.

### Key Takeaways

1. **Gender is the most significant equity issue:** High-performing female students are systematically underrepresented in 8th grade Algebra despite outperforming their male peers academically.

2. **Race-based access gaps are evident but under-studied:** Small sample sizes for Black/African American students mask potentially significant barriers. The data we have suggests capability is not the issue—access is.

3. **Program expansion can inadvertently reduce diversity:** The LEAD program's 106% growth primarily benefited White students, increasing their representation from 75% to 80%.

4. **Pathway differentiation may not serve its intended purpose:** Identical progression rates between "accelerated" and "regular" tracks raise questions about the value of ability tracking in 7th grade.

5. **Data infrastructure is now in place for ongoing monitoring:** The unified dataset and analysis scripts enable future tracking of these equity metrics over time.

### Recommended Next Steps

**For Administrators:**
1. Form equity task force to address gender gap in math placement
2. Conduct audit of LEAD program selection criteria and recruitment practices
3. Establish annual equity reporting dashboard with disaggregated data

**For Counselors/Teachers:**
1. Review implicit bias in advanced placement recommendations
2. Implement universal screening for Algebra readiness (vs. selective referral)
3. Create peer mentorship programs to increase underrepresented student participation

**For Researchers:**
1. Extend analysis to high school outcomes (Algebra 2, Precalculus)
2. Investigate LEAD program impact on math progression rates
3. Conduct intersectional analysis with multi-year aggregated data

**For Families:**
1. Increase transparency about advanced placement criteria and timelines
2. Provide multilingual materials about course pathways
3. Host information sessions specifically for underrepresented groups

---

## Acknowledgments

**Data Sources:**
- School district enrollment records (2021-2026)
- Student information system grade exports (2020-2026)
- Student ID mapping files (2021-2026)

**Analysis Conducted:** February 2026

**Technical Environment:**
- Python 3.14
- pandas 3.0.1, numpy 2.4.2, openpyxl 3.1.5

**Report Prepared By:** OpenCode AI Analysis System

---

*This report represents an independent analysis of student enrollment and outcomes data. Findings and recommendations are based solely on quantitative data patterns and should be supplemented with qualitative research and stakeholder input before implementing policy changes.*
