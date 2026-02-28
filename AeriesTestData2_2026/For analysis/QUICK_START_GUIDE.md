# QUICK START GUIDE
**Data Normalization & Analysis - 5-Year Student Enrollment Study**

---

## 📋 WHAT YOU HAVE

### Current Files:
- ✅ `Algebra 1A 23-26.xlsx` - Algebra enrollment (2023-2026)
- ✅ `Lead 21-26.xlsx` - LEAD program enrollment (2021-2026)
- ✅ `MATH 8 and Apex Data 21-26.xlsx` - 7th grade math enrollment (2021-2026)
- ✅ `academicrecords .csv` - Performance data (limited scope)

### Generated Analysis Files:
- 📄 `DATA_NORMALIZATION_REPORT.md` - Comprehensive data analysis
- 🐍 `normalize_and_analyze.py` - Python script to run analysis

---

## ⚠️ BEFORE YOU CAN RUN THE ANALYSIS

You need to answer **3 clarification questions** (see below). These answers will be configured in the Python script.

---

## ❓ CLARIFICATION QUESTIONS

### Question 1: Course ID Format
**Is Course ID 308 the same as "000308" mentioned in your requirements?**

- [ ] **Yes** - They're the same course (Algebra 1)
- [ ] **No** - Need to find data for course "000308"
- [ ] **Unsure** - Proceed with 308 and note the assumption

**Impact:** This determines which records to analyze for 8th grade Algebra outcomes.

---

### Question 2: Apex Math 8 Identification
**Which Course ID represents "Apex Math 8" (the accelerated pathway)?**

Your data shows two Math 8 courses:
- **Course 329:** 134 students, spans 2021-2026 (5 years)
- **Course 325:** 99 students, spans 2022-2026 (4 years)

Which one is Apex Math 8?

- [ ] **Course 329** is Apex Math 8 (accelerated pathway)
- [ ] **Course 325** is Apex Math 8 (accelerated pathway)
- [ ] **Need to check** course catalog/documentation
- [ ] **Both are valid** pathways (track separately)

**Impact:** This determines which students are on the "accelerated" vs "regular" track for the pipeline analysis.

**Hints:**
- Course 329 started earlier (2021) - might indicate standard track
- Course 325 has slightly fewer students - might indicate honors/accelerated
- Check your school's course catalog or consult curriculum coordinator

---

### Question 3: Include CSV File?
**Should we include `academicrecords.csv` in the analysis?**

**CSV File Limitations:**
- Only 3 students (vs 233 in Excel files)
- Only covers 2022-23 school year
- Missing demographic data (Sex, Race, Ethnicity)
- No overlap with Excel student populations
- Contains letter grades (A, B, C) but for different students

**Recommendation:** ❌ **EXCLUDE** the CSV file

- [ ] **Exclude CSV** (recommended)
- [ ] **Include CSV** (explain why)

**Impact:** Including CSV adds minimal value and may confuse results.

---

## 🚀 HOW TO RUN THE ANALYSIS

### Step 1: Answer the Questions Above

Based on your answers, update lines 26-34 in `normalize_and_analyze.py`:

```python
# Question 1: Is Course ID 308 the same as "000308"?
COURSE_308_IS_000308 = True  # Change to False if different

# Question 2: Which Course ID represents "Apex Math 8"?
APEX_COURSE_ID = 325  # Change to 329 if that's the accelerated pathway

# Question 3: Include CSV file?
INCLUDE_CSV = False  # Change to True if you want to include it
```

### Step 2: Run the Script

```bash
python3 normalize_and_analyze.py
```

### Step 3: Review Generated Files

The script will create 5 Excel files:

1. **unified_enrollments.xlsx** - All enrollment data (normalized)
2. **student_demographics.xlsx** - Master demographic table
3. **task_a_pipeline_analysis.xlsx** - 7th → 8th grade progression
4. **task_b_enrollment_trends.xlsx** - LEAD enrollment by year
5. **task_b_representation_analysis.xlsx** - LEAD representation details

---

## 📊 WHAT THE ANALYSIS WILL SHOW

### Task A: 7th to 8th Grade Math Success Pipeline

**Analysis includes:**
- Total 7th graders tracked
- How many took Algebra in 8th grade
- Progression rate by math pathway (Apex vs Regular)
- Demographic breakdown (Sex, Race, Ethnicity)
- Cross-tabulation: Pathway × Demographics

**Expected output:**
```
7th to 8th Grade Pipeline Analysis:
  Total 7th graders tracked: 233
  Students who took 8th grade Algebra: 106
  Progression rate: 45.5%

By Math Pathway:
                    Total Students  Took Algebra  Progression Rate
Apex Math 8                     99            58              58.6
Regular Math 8                 134            48              35.8

By Sex:
    Total Students  Took Algebra  Progression Rate
F              110            52              47.3
M              123            54              43.9
```

---

### Task B: LEAD Program Longitudinal Trends

**Analysis includes:**
- Year-over-year enrollment volume
- Gender representation trends
- Race/Ethnicity representation trends
- Detailed demographic breakdowns per year

**Expected output:**
```
LEAD Program Enrollment Trends (2021-2026):
Academic Year  Total Enrollment  Female Count  Male Count  Female %  Male %
21-22                        32            18          14      56.3    43.8
22-23                        28            14          14      50.0    50.0
23-24                        33            19          14      57.6    42.4
24-25                        59            34          25      57.6    42.4
25-26                        66            38          28      57.6    42.4
```

---

## 📈 KEY FINDINGS (Preview)

Based on preliminary analysis:

### 7th → 8th Grade Pipeline:
- **106 students** tracked from 7th grade Math to 8th grade Algebra
- **45.5% progression rate** overall
- Significant variation by pathway (pending Course ID clarification)

### LEAD Program Growth:
- **106% growth** in enrollment (32 → 66 students)
- Steady gender balance (~57% Female, ~43% Male)
- Increasing racial/ethnic diversity

---

## 🔍 DATA QUALITY NOTES

### ✅ Strengths:
- Complete demographic data across all Excel files
- 5-year historical coverage (2021-2026)
- Trackable student IDs for longitudinal analysis
- Sufficient sample sizes for statistical analysis

### ⚠️ Known Limitations:
- **No performance data** (letter grades) in Excel files
  - Cannot analyze "final marks/grades" as originally requested
  - CSV has grades but only for 3 students (insufficient)
- **Incomplete Algebra data** (starts 2023, no 2021-2022 data)
  - Limits tracking for early cohorts
- **Course ID ambiguity** (pending your clarification)

---

## 💬 NEXT STEPS

1. **Answer the 3 clarification questions** above
2. **Update the configuration** in `normalize_and_analyze.py` (lines 26-34)
3. **Run the script:** `python3 normalize_and_analyze.py`
4. **Review the output files** in Excel
5. **Interpret findings** in context of your research questions

---

## 📞 QUESTIONS?

If you need help with:
- **Course identification** → Check school course catalog or ask curriculum coordinator
- **Data interpretation** → Review `DATA_NORMALIZATION_REPORT.md` for detailed analysis
- **Technical issues** → Ensure Python 3 and required libraries are installed

---

## 📚 DOCUMENTATION

- **Detailed Report:** `DATA_NORMALIZATION_REPORT.md`
- **Analysis Script:** `normalize_and_analyze.py`
- **This Guide:** `QUICK_START_GUIDE.md`

---

**Ready to proceed?** Answer the 3 questions above, update the script configuration, and run the analysis!
