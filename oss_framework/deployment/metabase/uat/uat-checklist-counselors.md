# UAT Checklist - School Counselors

**Role**: School Counselor, Social Worker, Case Manager  
**Duration**: 1.5 hours  
**Dashboards**: 2 (Wellbeing Risk), 3 (Equity Outcomes)  
**Date**: ___________ **Time**: ___________  **Tester Name**: ___________

---

## Pre-Test Setup

- [ ] Logged into Metabase
- [ ] Verified access to Dashboards 2 and 3 only
- [ ] Training guide available (counselor-guide.md)
- [ ] Facilitator present

---

## Test Scenario 1: Multi-Domain Risk Assessment (25 min)

### Objective
Identify students with multiple risk factors for prioritized case management.

### Steps

1. [ ] **Open Dashboard 2: Student Wellbeing Profiles**
   - Dashboard loads successfully
   - Check "School" filter - should be pre-set to YOUR school only
   - Check "Grade Level" filter - should show your assigned grades

2. [ ] **Review Risk Domain Matrix (Bubble Chart)**
   - X-axis: Attendance risk (0-100)
   - Y-axis: Discipline risk (0-100)
   - Bubble size: Academic risk
   - Identify students in upper-right quadrant (high attendance + discipline risk)
   - How many students are in the "Critical" zone? __________

3. [ ] **Filter to High-Risk Students**
   - Click "Wellbeing Level" filter
   - Select ONLY "High" and "Critical"
   - Click "Apply"
   - How many high-risk students in your grade(s)? __________

4. [ ] **Review "Students by Wellbeing Level" Table**
   - Find 3 students you recognize:
     - Student 1: __________________ (Primary Concern: _________)
     - Student 2: __________________ (Primary Concern: _________)
     - Student 3: __________________ (Primary Concern: _________)
   - Check one student's details:
     - Attendance risk: __________
     - Discipline risk: __________
     - Academic risk: __________
     - Does this match what you know about this student? [ ] Yes  [ ] No

5. [ ] **Check Recommended Actions**
   - Table shows "Recommended Action" column
   - Read recommendation for one student: ________________________________
   - Is this recommendation appropriate/helpful? [ ] Yes  [ ] No
   - If No, explain: _____________________________________________

### Success Criteria
✅ Can identify multi-factor risk students in <10 minutes  
✅ Data matches your knowledge of students  
✅ Recommended actions are actionable and relevant

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 2: Create Case Management List (20 min)

### Objective
Export prioritized student list for weekly case management meetings.

### Steps

1. [ ] **Filter Dashboard 2 for Your Target Population**
   - Example: 10th grade students with "Multi-factor" primary concern
   - Set filters:
     - Grade Level: __________
     - Primary Concern: Multi-factor
     - Wellbeing Level: High, Critical
   - How many students meet criteria? __________

2. [ ] **Prioritize by Compound Risk Score**
   - "Students by Wellbeing Level" table should be sorted by compound risk (highest first)
   - Top 5 students by risk score:
     1. __________________ (Risk Score: ______)
     2. __________________ (Risk Score: ______)
     3. __________________ (Risk Score: ______)
     4. __________________ (Risk Score: ______)
     5. __________________ (Risk Score: ______)

3. [ ] **Export for Case Management System**
   - Hover over "Students by Wellbeing Level" table
   - Click "⋯" → "Download results" → ".csv"
   - Open CSV in Excel/Google Sheets
   - Verify columns include:
     - Student name
     - Grade level
     - Attendance risk, discipline risk, academic risk
     - Compound risk score
     - Primary concern
     - Recommended action

4. [ ] **Verify Usefulness**
   - Can you import this CSV into your case management system? [ ] Yes  [ ] No
   - Does this list help you prioritize your week? [ ] Yes  [ ] No
   - What additional data would be helpful? _______________________________

### Success Criteria
✅ Can create targeted student list in <15 minutes  
✅ Export format is compatible with case management workflow  
✅ List provides actionable prioritization

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 3: Identify Equity Gaps (20 min)

### Objective
Use Dashboard 3 to identify students from underserved groups needing support.

### Steps

1. [ ] **Open Dashboard 3: Equity Outcomes Analysis**
   - Dashboard loads successfully
   - Data is filtered to your school

2. [ ] **Review Attendance by Demographic Subgroup**
   - Look at "Attendance Rate by Subgroup" bar chart
   - Which demographic group has **lowest** attendance rate? __________
   - What is their attendance rate? __________%
   - What is the **highest** group's rate? __________%
   - Gap between highest and lowest: __________percentage points

3. [ ] **Review GPA Distribution by Subgroup**
   - Look at "GPA Distribution by Subgroup" box plot
   - Which group has lowest **median** GPA? __________
   - What is their median GPA? __________
   - Which group has highest median GPA? __________

4. [ ] **Check Discipline Disparities**
   - Look at "Discipline Disparities" stacked bar chart
   - Which racial/ethnic group has most discipline incidents? __________
   - Count: __________ incidents
   - Does this seem proportional to their enrollment? [ ] Yes  [ ] No

5. [ ] **Review Opportunity Gap Table**
   - Identify the subgroup with "Equity Flag" marked
   - Subgroup: __________
   - Why flagged (large gap in what metric)? __________________________
   - How many students in this subgroup at your school? __________

### Success Criteria
✅ Can identify equity gaps in <15 minutes  
✅ Dashboard highlights disproportionality clearly  
✅ Data informs culturally responsive support strategies

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 4: Track Intervention Effectiveness (15 min)

### Objective
Monitor whether risk levels are improving over time for students you're supporting.

### Steps

1. [ ] **Return to Dashboard 2: Student Wellbeing Profiles**
   - Look at "Risk Trend Over Time" line chart
   - Shows average compound risk score by grade over 12 weeks

2. [ ] **Analyze Trend for Your Grade Level**
   - Select your grade level in the chart (or legend)
   - Current week risk score: __________
   - 12 weeks ago risk score: __________
   - Trend direction: [ ] Improving (decreasing)  [ ] Worsening (increasing)  [ ] Stable

3. [ ] **Interpret Results**
   - If improving → Interventions may be working
   - If worsening → Need to adjust approach or increase support
   - Does this match your perception? [ ] Yes  [ ] No

4. [ ] **Identify Specific Students to Monitor**
   - Filter to students you're actively supporting (if possible by name/ID)
   - Note their current compound risk scores
   - Can you track these students week-over-week? [ ] Yes  [ ] No
   - If No, what's missing? __________________________________________

### Success Criteria
✅ Can see longitudinal trends  
✅ Dashboard supports intervention monitoring  
✅ Can measure impact of counseling services

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 5: Collaboration with Teachers (10 min)

### Objective
Share relevant data with classroom teachers for coordinated student support.

### Steps

1. [ ] **Create Teacher-Friendly Report**
   - Dashboard 2: Filter to one teacher's class (if available)
   - If not available, filter to one course (e.g., "Algebra 1")
   - How many students in this class are High/Critical risk? __________

2. [ ] **Export for Teacher**
   - Export student list as CSV
   - Open CSV and review
   - Remove sensitive columns if needed (discipline details?)
   - This report is appropriate to share with teacher? [ ] Yes  [ ] No

3. [ ] **Check Privacy Compliance**
   - CSV contains: Student names, risk scores, attendance data
   - Is sharing this with teacher a legitimate educational interest (FERPA)? [ ] Yes
   - Would you feel comfortable sharing this? [ ] Yes  [ ] No
   - What concerns do you have? _____________________________________

### Success Criteria
✅ Can create teacher-shareable reports  
✅ Privacy protections are clear  
✅ Supports cross-functional collaboration

### Issues Encountered
_______________________________________________________________________

---

## Post-Test Feedback

### Overall Impression

1. **Usefulness**: How useful are these dashboards for your counseling work? (1-5)
   - [ ] 1 - Not useful  [ ] 2  [ ] 3  [ ] 4  [ ] 5 - Extremely useful

2. **Will you use this regularly?**
   - [ ] Yes, daily (morning check-ins)
   - [ ] Yes, weekly (case management meetings)
   - [ ] Yes, monthly (progress monitoring)
   - [ ] No (why not?): ___________

3. **Dashboard 2 vs. Dashboard 3 - which is more useful for your role?**
   - [ ] Dashboard 2 (Wellbeing Risk) - more useful for direct student support
   - [ ] Dashboard 3 (Equity) - more useful for systemic advocacy
   - [ ] Both equally useful

4. **Recommended Action column - is it helpful?**
   - [ ] Yes, very actionable
   - [ ] Somewhat helpful, needs refinement
   - [ ] No, not useful (explain): ____________________________________

### What Worked Well
_______________________________________________________________________

### What Needs Improvement
_______________________________________________________________________

### Suggested Enhancements
_______________________________________________________________________

### Missing Features/Data
_______________________________________________________________________

---

## Sign-Off

**Tester Name**: _______________________________________  
**School**: _______________________________________  
**Grade Levels Assigned**: _______________________________________  
**Date**: _______________________________________  
**Signature**: _______________________________________

**UAT Facilitator**: _______________________________________

---

**End of Counselor UAT Checklist**
