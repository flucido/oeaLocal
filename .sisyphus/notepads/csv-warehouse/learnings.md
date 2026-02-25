
## AeRIES Naming Research (2026-02-22)

### AeRIES Official Terminology

**Key Tables in AeRIES:**
- **GRD** (Grade Reporting) - Current period grades, report card marks
- **HIS** (Course History) - Historical transcript data, completed courses
- **GRC** (Grade Report Marks) - Grade code definitions (A, B, C, etc.)
- **GRD table purpose**: "Contains Grades given to Students for Grade Reporting"
- **HIS table purpose**: "History of Grades given to a student, including those from other schools – Transcript Data"

**AeRIES Distinction:**
- **Grades (GRD)**: Current grading period marks, in-progress semester grades
- **Course History (HIS)**: Final grades, transcript records, historical data
- Both are part of the broader "academic record" concept

### Ed-Fi Data Standard

**Domain: "Student Academic Record Domain"**
- Official Ed-Fi domain name: "Student Academic Record"
- Contains THREE subdomains:
  1. **Gradebook** - Assignment-level scores (GradebookEntry, StudentGradebookEntry)
  2. **Grades and Report Card** - Period grades (Grade, ReportCard, GradingPeriod)
  3. **Student Transcript** - Historical academic record (StudentAcademicRecord, CourseTranscript)

**Ed-Fi Entity Mapping:**
- Entity: `StudentAcademicRecord` - Cumulative academic record for session
- Entity: `CourseTranscript` - Individual course outcomes (part of StudentAcademicRecord)
- Entity: `Grade` - Grading period grade for a section
- Entity: `ReportCard` - Report card containing grades for grading period

**Key Quote from Ed-Fi:**
> "The Student Academic Record domain captures the most common outputs of student 
> performance reporting found in K–12 education, ranging from grades received in a 
> student information system, to elements on a report card, to a student transcript."

**Ed-Fi's Distinction:**
- "Grades" = grading period marks
- "Student Academic Record" = holistic transcript/academic history
- These are NOT synonyms - they're different granularities

### Industry Standard Usage

**Common Patterns:**
- Data warehouses typically use **fact_grades** for grading period data
- **academic_records** or **transcript** for final course outcomes
- Separation reflects temporal distinction: in-progress vs. historical

**Search Results:**
- Very few GitHub repos use "CREATE TABLE academic_records"
- More common: "CREATE TABLE grades" (for grading period data)
- Educational platforms (OpenEdX) use: `dim_student_status` (not grades/academic_records)

### Our Current Implementation

**What we have:**
- Table: `fact_academic_records`
- Source: Aeries HIS table (Course History)
- Contents: Final course grades, credit earned, GPA points
- Grain: One row per student per course per term

**Semantic Match:**
- Our data = Final grades / transcript data (HIS equivalent)
- NOT = Current grading period marks (GRD equivalent)

### Recommendation: KEEP "academic_records"

**Reasons to KEEP current naming:**

1. **Semantic Accuracy**: Our data represents final academic records (transcripts), not in-progress grading period marks
2. **Ed-Fi Alignment**: Ed-Fi uses "StudentAcademicRecord" as the domain name and entity for transcript-level data
3. **AeRIES Mapping**: We're pulling from HIS (Course History), not GRD (Grade Reporting)
4. **Scope Clarity**: "academic_records" signals holistic view (grades + credits + GPA)
5. **Future Flexibility**: Leaves room to add `fact_grades` later if we ingest GRD table

**If we renamed to "grades":**
- ❌ Would imply grading period marks (GRD table)
- ❌ Conflicts with Ed-Fi's distinction (Grade vs. StudentAcademicRecord)
- ❌ Less descriptive (grades alone doesn't convey credits, transcripts)

**Potential Confusion:**
- Some users might expect "grades" to be more intuitive
- Industry has mixed usage (not standardized)

### Missing Standard Fields

**Fields we SHOULD consider adding:**
1. **Marking Period / Term Type** - Semester vs. Quarter vs. Trimester
2. **Cumulative GPA** - Running GPA calculation
3. **Credit Type** - Elective vs. Required vs. Honors
4. **Course Sequence** - Prerequisites, course ordering
5. **Repeat Indicator** - Course retaken flag
6. **Grade Type** - Final vs. Mid-term vs. Progress report

**From Ed-Fi CourseTranscript entity:**
- CourseAttemptResult (Pass/Fail status) - ✅ We have `is_passing`
- EarnedCredits - ✅ We have `credit_earned`
- NumericGradeEarned - ⚠️ Missing (we have letter grades only)
- LetterGradeEarned - ✅ We have `grade`

**From AeRIES HIS table (that we might not be capturing):**
- HIS.PF - Pass/Fail Credit Status
- HIS.CH - College Credit Hours
- HIS.SDE - Dual Enrollment indicator
- HIS.TE - Term (semester/quarter indicator)

### Action Items

**KEEP naming as-is:**
- ✅ `fact_academic_records` is semantically correct
- ✅ Aligns with Ed-Fi standard terminology
- ✅ Reflects data source (HIS/transcript, not GRD/period grades)

**Consider enhancements:**
1. Add term_type field (Semester/Quarter/Trimester)
2. Add numeric_grade field (if available in source)
3. Add course_repeat_flag
4. Add dual_enrollment_flag
5. Document distinction from "grades" in README

