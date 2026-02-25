# UAT Checklist - Administrators

**Role**: Superintendent, Assistant Superintendent, Data Director  
**Duration**: 2 hours  
**Dashboards**: All 5 (full system access)  
**Date**: ___________ **Time**: ___________ **Tester Name**: ___________

---

## Pre-Test Setup

- [ ] Logged into Metabase at http://localhost:3000
- [ ] Verified access to all 5 dashboards
- [ ] Training guide available for reference
- [ ] Facilitator present and ready

---

## Test Scenario 1: Dashboard Access & Navigation (15 min)

### Objective
Verify you can access all dashboards and navigate the system.

### Steps

1. [ ] **Access Home Page**
   - Navigate to http://localhost:3000
   - Home page loads successfully
   - You see "Pick up where you left off" section

2. [ ] **View Collections**
   - Click "Collections" in left sidebar
   - You see "OSS Analytics" collection
   - Click into collection

3. [ ] **See All 5 Dashboards**
   - [ ] Dashboard 1: Chronic Absenteeism Risk
   - [ ] Dashboard 2: Student Wellbeing Profiles
   - [ ] Dashboard 3: Equity Outcomes Analysis
   - [ ] Dashboard 4: Class Effectiveness Comparison
   - [ ] Dashboard 5: Performance Correlations

4. [ ] **Open Dashboard 1**
   - Click "Chronic Absenteeism Risk"
   - Dashboard loads in <5 seconds
   - All visualizations appear (6 total)

### Success Criteria
✅ All 5 dashboards visible and accessible  
✅ Load time <5 seconds  
✅ No errors or broken visualizations

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 2: District-Wide Data View (20 min)

### Objective
Verify you see data from ALL schools (not filtered).

### Steps

1. [ ] **Dashboard 1: Check School Filter**
   - Look at "School" filter dropdown at top
   - Default should be "All Schools" selected
   - Total student count should match district enrollment (~3,400)

2. [ ] **View Risk Distribution Chart**
   - Pie chart shows: Low / Medium / High / Critical
   - Percentages add up to 100%
   - Numbers match expected distribution (ask: ~68% Low, 20% Medium, 8% High, 4% Critical)

3. [ ] **View School Comparison Bar Chart**
   - All district schools visible on chart (not just one school)
   - Can see which schools have highest chronic absenteeism rates
   - Click on a school bar → should drill down or show detail

4. [ ] **Dashboard 4: View All Teachers**
   - Open Dashboard 4: Class Effectiveness
   - Table shows ALL teachers in district (not filtered to one school)
   - Can see effectiveness ratings across schools

### Success Criteria
✅ Data shows ALL schools (district-wide view)  
✅ Student count matches enrollment  
✅ No single-school filter applied by default

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 3: Filtering & Drill-Down (20 min)

### Objective
Test filtering by school, grade, risk level, and date range.

### Steps

1. [ ] **Filter by School**
   - Dashboard 1: Click "School" filter dropdown
   - Select "Lincoln High School" (or any one school)
   - Click "Apply"
   - Student count should decrease (now showing only Lincoln students)
   - Charts update to show Lincoln data only

2. [ ] **Filter by Grade Level**
   - Check boxes for "9th" and "10th" only (uncheck 11th, 12th)
   - Click "Apply"
   - Student count decreases further (now 9th + 10th only)
   - Charts update

3. [ ] **Filter by Risk Level**
   - Check only "High" and "Critical" risk levels
   - Click "Apply"
   - Student count shows only high-risk students
   - Top 20 table shows only High/Critical students

4. [ ] **Change Date Range**
   - Click "Date Range" filter
   - Select "Last 90 days" (instead of default 30)
   - Click "Apply"
   - Attendance trend line chart should extend to 90 days

5. [ ] **Reset Filters**
   - Click "Reset" button at top
   - All filters return to defaults
   - Student count returns to full district count

### Success Criteria
✅ Filters work correctly and update visualizations  
✅ Multiple filters can be applied together  
✅ Reset button clears all filters  
✅ Response time <2 seconds per filter apply

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 4: Data Accuracy Validation (30 min)

### Objective
Verify dashboard numbers match source data (Aeries SIS).

### Steps

1. [ ] **Verify Total Student Count**
   - Dashboard 1: Note "Total Students Monitored" card
   - Open Aeries → Reports → Enrollment Count
   - **Dashboard shows**: __________ students
   - **Aeries shows**: __________ students
   - **Match?** [ ] Yes  [ ] No (if no, document discrepancy below)

2. [ ] **Spot-Check Individual Student (Student A)**
   - Dashboard 1: Find student in "Top 20 At-Risk Students" table
   - **Student Name**: ___________
   - **Dashboard Attendance Rate**: ___________%
   - Open Aeries → Student Profile → Attendance
   - **Aeries Attendance Rate**: ___________%
   - **Match?** [ ] Yes  [ ] No

3. [ ] **Spot-Check Individual Student (Student B)**
   - Pick a different student from table
   - **Student Name**: ___________
   - **Dashboard Risk Score**: __________
   - Manually calculate: (absences × weight) + (tardies × weight) + (discipline × weight)
   - **Manual Calculation**: __________
   - **Match (within ±2 points)?** [ ] Yes  [ ] No

4. [ ] **Verify School-Level Aggregates**
   - Dashboard 1: Note chronic absenteeism rate for "Lincoln HS"
   - **Dashboard**: __________% chronic absenteeism
   - Calculate manually: (Students with ≥10% absences) / (Total students) × 100
   - **Manual Calculation**: __________%
   - **Match (within ±1%)?** [ ] Yes  [ ] No

5. [ ] **Check Data Freshness**
   - Look for "Last updated" timestamp on dashboard
   - **Last updated**: ___________
   - Should be yesterday's date (data refreshes nightly at 2 AM)
   - **Is data fresh?** [ ] Yes  [ ] No

### Success Criteria
✅ 100% match on total student count  
✅ 100% match on individual student data (within rounding)  
✅ Data is from yesterday (not stale)

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 5: Export for Board Presentation (15 min)

### Objective
Export dashboards as PDF and CSV for board meetings.

### Steps

1. [ ] **Export Dashboard as PDF**
   - Dashboard 1: Click "⋯" button (top right)
   - Select "Download as PDF"
   - Configure: Page size = Letter, Orientation = Landscape
   - Click "Download"
   - File downloads in <15 seconds
   - Open PDF → Verify all charts are visible and legible

2. [ ] **Export Table as CSV**
   - Dashboard 1: Hover over "Top 20 At-Risk Students" table
   - Click "⋯" (three dots) in top-right corner of table
   - Select "Download results" → ".csv"
   - File downloads in <10 seconds
   - Open CSV in Excel → Verify all columns present (Student, Grade, Attendance, Risk Score, etc.)

3. [ ] **Export Aggregated Data**
   - Dashboard 3: Equity Outcomes Analysis
   - Hover over "Opportunity Gap Table"
   - Click "⋯" → "Download results" → ".csv"
   - Open CSV → Verify data is aggregated (no individual student names)

### Success Criteria
✅ PDF export works and is print-ready  
✅ CSV export works and opens in Excel  
✅ Export times <15 seconds for PDF, <10 seconds for CSV  
✅ Aggregated data exports contain no student names (FERPA compliant)

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 6: Performance Under Load (10 min)

### Objective
Test system responsiveness with realistic usage.

### Steps

1. [ ] **Open Multiple Dashboards**
   - Open Dashboard 1 in new tab
   - Open Dashboard 2 in new tab
   - Open Dashboard 3 in new tab
   - All dashboards load without crashing
   - No significant slowdown

2. [ ] **Apply Complex Filters**
   - Dashboard 1: Apply 4 filters simultaneously:
     - School = "Lincoln HS"
     - Grade = "9th, 10th"
     - Risk Level = "High, Critical"
     - Date Range = "Last 90 days"
   - Click "Apply"
   - Dashboard updates in <2 seconds

3. [ ] **Rapid Filter Changes**
   - Change school filter 5 times rapidly
   - System responds to each change
   - No lag or freezing

### Success Criteria
✅ Multiple dashboards can be open simultaneously  
✅ Filter response time <2 seconds  
✅ No crashes or freezing

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Test Scenario 7: Board Member Scenario (10 min)

### Objective
Simulate preparing data for board meeting.

### Steps

1. [ ] **Dashboard 1: Chronic Absenteeism Trends**
   - Note district-wide chronic absenteeism rate: ___________%
   - Note trend (improving or worsening): __________
   - Screenshot the "Trend Over Time" chart

2. [ ] **Dashboard 3: Equity Gaps**
   - Note largest attendance gap: __________ (between which groups?)
   - Note largest GPA gap: __________ (between which groups?)
   - Export "Opportunity Gap Table" as CSV

3. [ ] **Dashboard 5: Key Insights**
   - Note strongest correlation: Attendance ↔ GPA = __________
   - Interpretation: "For every 10% increase in attendance, GPA increases by __________ points"

4. [ ] **Prepare Board Packet**
   - Export Dashboard 1 as PDF
   - Export Dashboard 3 as PDF
   - Include CSV from Equity table
   - Estimated time to prepare full packet: __________ minutes

### Success Criteria
✅ Can extract key metrics in <10 minutes  
✅ Exports are board-presentation ready  
✅ Data tells a clear story for board

### Issues Encountered
_______________________________________________________________________
_______________________________________________________________________

---

## Post-Test Feedback

### Overall Impression

1. **Clarity**: How clear are the visualizations? (1-5, 5=very clear)
   - [ ] 1 - Very confusing
   - [ ] 2 - Somewhat confusing
   - [ ] 3 - Neutral
   - [ ] 4 - Mostly clear
   - [ ] 5 - Very clear

2. **Usefulness**: How useful is this for your role? (1-5, 5=very useful)
   - [ ] 1 - Not useful at all
   - [ ] 2 - Slightly useful
   - [ ] 3 - Moderately useful
   - [ ] 4 - Very useful
   - [ ] 5 - Extremely useful

3. **Performance**: Is the dashboard fast enough?
   - [ ] Yes, very responsive
   - [ ] Yes, acceptable
   - [ ] No, too slow (specify where): ___________

4. **Accuracy**: Do the numbers match your expectations?
   - [ ] Yes, 100% accurate
   - [ ] Mostly accurate (a few discrepancies)
   - [ ] No, significant issues (describe below)

### What Worked Well
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

### What Needs Improvement
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

### Suggested Enhancements
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

### Would you use this regularly?
- [ ] Yes, daily
- [ ] Yes, weekly
- [ ] Yes, monthly
- [ ] No (why not?): ___________

---

## Sign-Off

**Tester Name**: _______________________________________  
**Role**: _______________________________________  
**Date**: _______________________________________  
**Signature**: _______________________________________  

**UAT Facilitator**: _______________________________________  
**Date**: _______________________________________

---

**End of Administrator UAT Checklist**

Return completed checklist to: analytics@district.edu

