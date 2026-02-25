# UAT Checklist - School Principals

**Role**: Principal, Assistant Principal  
**Duration**: 1.5 hours  
**Dashboards**: 1 (Chronic Absenteeism), 4 (Class Effectiveness)  
**Date**: ___________ **Time**: ___________  **Tester Name**: ___________

---

## Pre-Test Setup

- [ ] Logged into Metabase
- [ ] Verified access to Dashboards 1 and 4 only
- [ ] Training guide available (principal-guide.md)
- [ ] Facilitator present

---

## Test Scenario 1: School-Filtered Access (15 min)

###Objective
Verify you see ONLY your school's data (not other schools).

### Steps

1. [ ] **Open Dashboard 1**
   - Dashboard loads successfully
   - Check "School" filter - should be pre-set to YOUR school only
   - Student count shows only your school (~450 students for typical HS)

2. [ ] **Try to View Other Schools (Security Test)**
   - Click "School" filter dropdown
   - **Expected**: Only YOUR school appears in list (or other schools are greyed out)
   - **If you can see/select other schools → REPORT SECURITY ISSUE**

3. [ ] **Verify Student Names**
   - Look at "Top 20 At-Risk Students" table
   - All students should be from YOUR school (verify by familiar names)
   - If you see unfamiliar students → May be from wrong school (report)

### Success Criteria
✅ See only your school's data  
✅ Cannot access other schools' data  
✅ Student names are familiar (your school's students)

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 2: Identify Students for SART/SARB (20 min)

### Objective
Use Dashboard 1 to create list for Student Attendance Review Team.

### Steps

1. [ ] **Filter for High-Risk Students**
   - Dashboard 1: Click "Risk Level" filter
   - Check ONLY "High" and "Critical"
   - Click "Apply"
   - How many high-risk students at your school? __________

2. [ ] **Review Top At-Risk Students**
   - Look at "Top 20 At-Risk Students" table
   - Identify 3 students you know need intervention:
     - Student 1: ____________________ (Risk Score: ______)
     - Student 2: ____________________ (Risk Score: ______)
     - Student 3: ____________________ (Risk Score: ______)

3. [ ] **Check Attendance Details**
   - For one student, note:
     - Attendance rate (30 days): ___________%
     - Unexcused absences: __________
     - Does this match what you know about this student? [ ] Yes  [ ] No

4. [ ] **Export SART List**
   - Hover over "Top 20 At-Risk Students" table
   - Click "⋯" → "Download results" → ".csv"
   - Open CSV in Excel
   - Verify columns: Student Name, Grade, Attendance Rate, Risk Score

### Success Criteria
✅ Can identify high-risk students in <5 minutes  
✅ Data matches your knowledge of students  
✅ CSV export works for SART meetings

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 3: Prepare for Staff Meeting (15 min)

### Objective
Create attendance report for monthly staff meeting.

### Steps

1. [ ] **Capture Key Metrics**
   - Dashboard 1: Note the 4 metric cards at top
     - Total Students: __________
     - Chronic Absence Rate: __________%
     - High/Critical Risk Count: __________
     - Trend (30d vs 90d): __________ (improving/worsening)

2. [ ] **Identify Problem Grades**
   - Look at "Grade-Level Comparison" bar chart
   - Which grade has highest chronic absenteeism? __________
   - Rate for that grade: __________%

3. [ ] **Export Dashboard for Staff**
   - Click "⋯" (top right) → "Download as PDF"
   - Select Landscape orientation
   - PDF downloads successfully
   - Open PDF → All charts visible and print-ready?  [ ] Yes  [ ] No

### Success Criteria
✅ Can extract key talking points in <10 minutes  
✅ PDF is presentation-ready for staff meeting

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 4: Teacher Observation Prioritization (20 min)

### Objective
Use Dashboard 4 to identify teachers for observation and support.

### Steps

1. [ ] **Open Dashboard 4: Class Effectiveness**
   - Dashboard loads successfully
   - Shows classes ONLY from your school

2. [ ] **Review Teacher Effectiveness Table**
   - Table shows: Course, Teacher ID, Pass Rate, Effectiveness Rating
   - How many teachers at your school? __________
   - How many rated "Needs Improvement"? __________
   - How many rated "Highly Effective"? __________

3. [ ] **Identify Teacher for Support**
   - Find a teacher with "Needs Improvement" or "Developing" rating
   - **Teacher ID**: __________ (e.g., T_12345)
   - **Course**: __________
   - **Pass Rate**: __________%
   - **Avg Attendance in class**: __________%
   - Do you recognize this teacher (by course/schedule)? [ ] Yes  [ ] No

4. [ ] **Identify High-Performing Teacher**
   - Find a teacher with "Highly Effective" rating
   - **Teacher ID**: __________
   - **Course**: __________
   - **Pass Rate**: __________%
   - Plan to observe for best practices sharing

5. [ ] **Check for Context**
   - Look at "Attendance Impact on Pass Rate" scatter plot
   - Find the "Needs Improvement" teacher's dot
   - Is their class below trend line? (low pass rate despite decent attendance)
     - [ ] Yes → May indicate instructional issue
     - [ ] No → May be attendance-driven issue

### Success Criteria
✅ Can identify teachers needing support in <15 minutes  
✅ Can identify high-performers for best practice sharing  
✅ Dashboard provides context (attendance vs. instruction)

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 5: Share Data with Counselor (10 min)

### Objective
Export student list for counselor follow-up.

### Steps

1. [ ] **Filter to One Grade Level**
   - Dashboard 1: Click "Grade Level" filter
   - Select "10th grade" only
   - Click "Apply"
   - How many 10th graders at High/Critical risk? __________

2. [ ] **Export for Counselor**
   - Export "Top 20 At-Risk Students" table as CSV
   - Open CSV
   - **Email this to your counselor with subject**: "10th Grade At-Risk Students - [Date]"
   - Include message: "Please review and prioritize for check-ins this week"

3. [ ] **Check Privacy**
   - CSV contains: Student names, attendance data, risk scores
   - This is appropriate to share with counselor? [ ] Yes (legitimate educational interest)

### Success Criteria
✅ Can create grade-specific lists for counselor  
✅ Export process is quick (<2 minutes)

### Issues Encountered
_______________________________________________________________________

---

## Post-Test Feedback

### Overall Impression

1. **Usefulness**: How useful is this for identifying struggling students? (1-5)
   - [ ] 1 - Not useful  [ ] 2  [ ] 3  [ ] 4  [ ] 5 - Extremely useful

2. **Will you use this regularly?**
   - [ ] Yes, weekly (Monday mornings)
   - [ ] Yes, monthly (staff meetings)
   - [ ] No (why not?): ___________

3. **Dashboard 1 vs. Dashboard 4 - which is more useful?**
   - [ ] Dashboard 1 (Attendance)
   - [ ] Dashboard 4 (Teacher Effectiveness)
   - [ ] Both equally useful

### What Worked Well
_______________________________________________________________________

### What Needs Improvement
_______________________________________________________________________

### Suggested Enhancements
_______________________________________________________________________

---

## Sign-Off

**Tester Name**: _______________________________________  
**School**: _______________________________________  
**Date**: _______________________________________  
**Signature**: _______________________________________

**UAT Facilitator**: _______________________________________

---

**End of Principal UAT Checklist**
