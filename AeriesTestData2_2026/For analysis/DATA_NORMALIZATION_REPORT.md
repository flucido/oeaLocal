# DATA NORMALIZATION & INTEGRATION REPORT
**Analysis Date:** February 23, 2026  
**Analyst:** Senior Data Analyst  
**Objective:** Prepare 5-year enrollment and outcomes data for longitudinal analysis

---

## EXECUTIVE SUMMARY

This report analyzes four data sources covering student enrollment and outcomes from 2021-2026. **The data requires significant normalization before cross-dataset analysis can proceed.** Key findings:

- ✅ **Core data is present:** Student demographics, course enrollment, 5-year history
- ⚠️ **Column naming inconsistencies** across datasets prevent direct joins
- ⚠️ **Academic year format varies** (3 different formats identified)
- ⚠️ **CSV file has limited value** for the required analysis (3 students only, missing demographics)
- ✅ **Longitudinal tracking is feasible:** 106 students tracked from 7th to 8th grade

---

## DATA INVENTORY

### 1. Algebra 1A 23-26.xlsx
- **Records:** 171 enrollment records
- **Students:** 111 unique students
- **Coverage:** Academic years 2023-24, 2024-25, 2025-26
- **Course:** Algebra 1 (Course ID: 308)
- **Grades:** 7th and 8th grade students
- **Demographics:** ✓ Complete (Sex, Ethnicity, Race)

### 2. Lead 21-26.xlsx
- **Records:** 218 enrollment records
- **Students:** 185 unique students
- **Coverage:** Academic years 2021-22 through 2025-26
- **Course:** LEAD Program (Course ID: 1205)
- **Grades:** 7th and 8th grade students
- **Demographics:** ✓ Complete (Sex, Ethnicity, Race)

### 3. MATH 8 and Apex Data 21-26.xlsx
- **Records:** 233 enrollment records
- **Students:** 233 unique students
- **Coverage:** Academic years 2021-22 through 2025-26
- **Courses:** Two course IDs present (329 and 325)
- **Grades:** 7th grade students only
- **Demographics:** ✓ Complete (Sex, Ethnicity, Race)

### 4. academicrecords.csv
- **Records:** 100 records
- **Students:** 3 unique students
- **Coverage:** Academic year 2022-23 only
- **Courses:** 9 different courses
- **Demographics:** ✗ Missing (no Sex, Ethnicity, Race, or Grade Level)
- **Note:** Contains performance data (letter grades) but limited scope

---

## CRITICAL NORMALIZATION ISSUES

### Issue #1: Column Name Inconsistencies

| Standard Column | Algebra 1A | LEAD | MATH 8 | CSV |
|----------------|-----------|------|--------|-----|
| **Student ID** | State Student ID | State Student ID | State Student ID | student_id_raw ❌ |
| **Academic Year** | Academic Year | Academic Year | Academic year ❌ | school_year ❌ |
| **Course ID** | Course ID | Course ID | Course ID | course_id ❌ |
| **Grade Level** | Grade | Grade | Grade | ❌ MISSING |
| **Letter Grade** | ❌ N/A | ❌ N/A | ❌ N/A | grade ⚠️ |

**⚠️ CRITICAL:** CSV's "grade" column contains **LETTER GRADES (A, B, C)**, not grade level (7, 8). These are semantically different and cannot be merged.

### Issue #2: Academic Year Format Inconsistencies

Three different formats identified:

| Format | Example | Source |
|--------|---------|--------|
| **YY-YY** (Recommended) | '23-24' | Algebra 1A, MATH 8 |
| **YYYY-MM-DD** (Timestamp) | '2021-08-20' | LEAD |
| **YYYY-YYYY** | '2022-2023' | CSV |

**Recommendation:** Standardize to **'YY-YY'** format (e.g., '21-22', '22-23').

### Issue #3: Course ID Ambiguity

Two unresolved questions:

1. **Course ID 308 vs 000308**
   - Requirements mention Course ID "000308" for Algebra 1
   - Data files contain Course ID **308** (integer, no leading zeros)
   - **ACTION REQUIRED:** Confirm these refer to the same course

2. **Course ID 329 vs 325 - Which is "Apex Math 8"?**
   - Course 329: 134 students, data from 2021-2026
   - Course 325: 99 students, data from 2022-2026
   - Both are labeled "Math 8" type courses
   - **ACTION REQUIRED:** Identify which represents the "accelerated pathway" (Apex Math 8)

---

## STUDENT OVERLAP ANALYSIS

Understanding data relationships:

```
MATH 8/Apex (7th Grade)      →      Algebra 1A (8th Grade)
233 unique students                 111 unique students
                              ↓
                         106 students tracked (45.5% progression rate)
```

### Cross-Dataset Student Counts:

| Overlap | Count | Significance |
|---------|-------|-------------|
| Math 8 → Algebra 1A | 106 | Core pipeline for Task A |
| Math 8 → LEAD | 50 | Students in both programs |
| Algebra 1A → LEAD | 24 | Students in both programs |
| CSV → Excel files | 0 | No overlap; CSV has different student population |

**✓ FEASIBILITY:** Longitudinal tracking (7th → 8th grade) is **viable** with 106 students.

---

## COURSE ENROLLMENT BREAKDOWN

### MATH 8 / Apex Courses (7th Grade)

| Course ID | Total Students | Coverage Years | Students per Year (Avg) |
|-----------|---------------|----------------|------------------------|
| **329** | 134 | 2021-2026 (5 years) | 27 students/year |
| **325** | 99 | 2022-2026 (4 years) | 25 students/year |

**Note:** Course 329 has earlier start date (2021), suggesting it may be the standard track.

### Algebra 1 (8th Grade)

| Course ID | Total Students | Coverage Years |
|-----------|---------------|----------------|
| **308** | 111 | 2023-2026 (3 years) |

### LEAD Program

| Course ID | Total Students | Coverage Years | Trend |
|-----------|---------------|----------------|-------|
| **1205** | 185 | 2021-2026 (5 years) | Growing (32 → 66 students) |

---

## DATA QUALITY ASSESSMENT

### ✓ STRENGTHS

1. **Complete demographics** in all Excel files (Sex, Description_STU_ETH, Description_STU_RC1)
2. **5-year historical coverage** (2021-2026)
3. **Consistent structure** across three Excel files
4. **Sufficient sample size** for statistical analysis (233 Math 8, 111 Algebra)
5. **Trackable student IDs** (State Student ID is unique identifier)

### ⚠️ LIMITATIONS

1. **CSV file has minimal utility:**
   - Only 3 students (insufficient for analysis)
   - Missing demographic data required for Task A & B
   - No overlap with Excel student populations
   - Covers only 1 academic year (2022-23)

2. **Missing performance data:**
   - No letter grades in Excel files
   - Cannot analyze "final marks/grades" as requested in Task A
   - CSV grades cover different students

3. **Incomplete Algebra 1A coverage:**
   - Starts in 2023-24 (no data for 2021-23)
   - Limits longitudinal tracking for early cohorts

4. **Course ID ambiguity:**
   - Cannot differentiate Apex vs regular Math 8 without clarification

---

## NORMALIZATION ACTION PLAN

### Phase 1: Column Standardization ✅ READY TO EXECUTE

**Rename columns to match standard schema:**

```python
# MATH 8 file
'Academic year' → 'Academic Year'

# CSV file (if included)
'student_id_raw' → 'State Student ID'
'course_id' → 'Course ID'
'school_year' → 'Academic Year'
```

### Phase 2: Academic Year Format Conversion ✅ READY TO EXECUTE

**Standardize all to 'YY-YY' format:**

```python
# LEAD file: Convert timestamps
'2021-08-20' → '21-22'
'2022-08-19' → '22-23'
etc.

# CSV file: Convert full format
'2022-2023' → '22-23'
```

### Phase 3: Course ID Verification ⏸️ REQUIRES USER INPUT

**Questions for user:**

1. **Is Course ID 308 the same as "000308" mentioned in requirements?**
   - [ ] Yes, they're the same (proceed with 308)
   - [ ] No, need to find 000308 data
   - [ ] Unsure, use 308 and note assumption

2. **Which Course ID represents "Apex Math 8"?**
   - [ ] Course 329 is Apex Math 8 (accelerated)
   - [ ] Course 325 is Apex Math 8 (accelerated)
   - [ ] Course title lookup needed
   - [ ] Both are valid pathways (track separately)

### Phase 4: Data Integration ⏸️ PENDING CLARIFICATIONS

Once Phase 3 is complete:

1. **Create unified enrollment table** with standardized columns
2. **Build demographic master table** (one row per student)
3. **Generate longitudinal tracking table** (7th grade → 8th grade outcomes)
4. **Prepare LEAD trend analysis table** (year-over-year representation)

---

## ANSWERS TO REQUIREMENTS

### Task A: 7th to 8th Grade Math Success Pipeline

**✓ DATA AVAILABLE:**
- [x] 7th grade cohorts identified (233 students in Math 8/Apex)
- [x] Demographic segmentation possible (Sex, Description_STU_RC1)
- [x] 8th grade Algebra 1 enrollment trackable (106 students followed)
- [x] Course pathway differentiation possible (Course 329 vs 325)

**⚠️ DATA GAPS:**
- [ ] Performance data (final marks/grades) **NOT AVAILABLE** in Excel files
- [ ] Need to determine which course is "Apex Math 8"

**Recommendation:** Proceed with enrollment/retention analysis. Note that performance analysis requires additional data source.

### Task B: LEAD Program Longitudinal Trends

**✓ DATA AVAILABLE:**
- [x] 5-year enrollment data (2021-2026)
- [x] Complete demographic breakdown (Description_STU_ETH, Sex)
- [x] Year-over-year tracking possible
- [x] Growing trend visible (32 → 66 students)

**No data gaps for this task.**

---

## CSV FILE RECOMMENDATION

**Recommendation: EXCLUDE CSV from primary analysis**

**Rationale:**
1. Only 3 students (0.5% of dataset)
2. No overlap with Excel student populations
3. Missing demographic variables required for Tasks A & B
4. Single-year coverage (2022-23 only)
5. Grade-level information absent

**Alternative use:** If needed, CSV could supplement performance analysis for the 3 students it covers, but this would not impact the core analysis.

---

## IMMEDIATE NEXT STEPS

### Step 1: User Clarifications Needed ⏸️

Before proceeding, please confirm:

1. **Course ID 308 = "000308"?** (Yes/No/Clarify)
2. **Which is Apex Math 8?** Course 329 or 325?
3. **Performance data source?** Excel files lack letter grades needed for "final marks" analysis
4. **Include CSV file?** Recommend excluding due to limited scope

### Step 2: Execute Normalization ⏳ READY

Once clarifications received:
- Standardize all column names
- Convert Academic Year formats
- Create unified dataset
- Generate analysis-ready tables

### Step 3: Run Analysis ⏳ PENDING

After normalization:
- Task A: 7th → 8th pipeline analysis (enrollment/retention)
- Task B: LEAD program trends (representation analysis)

---

## TECHNICAL NOTES

### Data Quality Metrics

| Metric | Status | Details |
|--------|--------|---------|
| Completeness | 90% | Missing: performance data |
| Consistency | 70% | Issues: column names, date formats |
| Accuracy | ✓ | No duplicates or invalid IDs detected |
| Timeliness | ✓ | Current through 2025-26 |
| Validity | ✓ | All IDs and codes within expected ranges |

### Assumptions Made

1. State Student ID is the unique, permanent student identifier
2. Course ID 308 refers to the same course as "000308" in requirements
3. Grade levels (7, 8) are accurate and represent academic progression
4. Academic year indicates the **start** of the school year (e.g., '23-24' = Fall 2023)

---

## APPENDIX: Schema Comparison

### Standardized Schema (Target)

```
State Student ID      (int)      - Unique student identifier
Last Name             (string)   - Student surname
First Name            (string)   - Student given name
Grade                 (int)      - Grade level (7 or 8)
Sex                   (string)   - Gender (M/F)
Description_STU_ETH   (string)   - Ethnicity classification
Description_STU_RC1   (string)   - Race classification
Section#              (int)      - Course section identifier
Course ID             (int)      - Course identifier
Academic Year         (string)   - Format: 'YY-YY' (e.g., '21-22')
```

### Current File Schemas

**Algebra 1A 23-26.xlsx** - ✓ Matches standard (10/10 columns)  
**Lead 21-26.xlsx** - ⚠️ Academic Year needs conversion (9/10 match)  
**MATH 8 and Apex.xlsx** - ⚠️ 'Academic year' capitalization (9/10 match)  
**academicrecords.csv** - ❌ Different schema (0/10 match)

---

## CONCLUSION

The Excel files contain **sufficient, high-quality data** for the required longitudinal analysis. After addressing column naming and date format inconsistencies, the dataset will support:

1. ✅ 7th → 8th grade progression tracking (106 students)
2. ✅ Demographic segmentation and equity analysis
3. ✅ LEAD program trend analysis (5-year history)
4. ⚠️ Enrollment outcomes (available)
5. ⚠️ Performance outcomes (requires additional data)

**Recommendation:** Proceed with normalization upon receiving user clarifications on Course ID mapping.
