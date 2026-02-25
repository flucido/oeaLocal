# UAT Checklist - School Board Members

**Role**: School Board Member, Trustee  
**Duration**: 1 hour  
**Dashboards**: 1 (Chronic Absenteeism), 3 (Equity), 5 (Correlations)  
**Date**: ___________ **Time**: ___________  **Tester Name**: ___________

---

## Pre-Test Setup

- [ ] Logged into Metabase
- [ ] Verified access to Dashboards 1, 3, and 5 (district-wide, aggregated)
- [ ] Training guide available (board-member-guide.md)
- [ ] Facilitator present
- [ ] **Privacy Check**: Confirmed NO student names visible

---

## Test Scenario 1: Privacy & Aggregation Verification (10 min)

### Objective
Verify that dashboards show ONLY aggregated data with no personally identifiable information.

### Steps

1. [ ] **Open Dashboard 1: Chronic Absenteeism Risk**
   - Dashboard loads successfully
   - Data shows district-wide view (all schools)

2. [ ] **Privacy Check: Search for Student Names**
   - Scan all charts and tables
   - Look for any student names, IDs, or identifiable information
   - **Expected**: Only aggregated counts, percentages, school names
   - Do you see ANY student names? [ ] Yes (REPORT ISSUE)  [ ] No (GOOD)

3. [ ] **Open Dashboard 3: Equity Outcomes**
   - Scan for student names or IDs
   - Do you see ANY student names? [ ] Yes (REPORT ISSUE)  [ ] No (GOOD)

4. [ ] **Open Dashboard 5: Performance Correlations**
   - Scan for student names or IDs
   - Do you see ANY student names? [ ] Yes (REPORT ISSUE)  [ ] No (GOOD)

5. [ ] **FERPA Compliance Confirmation**
   - All data is aggregated at school/district level? [ ] Yes
   - No individual student records visible? [ ] Confirmed
   - Appropriate for board governance role? [ ] Yes

### Success Criteria
✅ Zero student names or IDs visible  
✅ All data is appropriately aggregated  
✅ Meets FERPA privacy requirements for board access

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 2: Monitor Strategic Goal Progress (15 min)

### Objective
Use Dashboard 1 to assess progress toward board's attendance improvement goals.

### Steps

1. [ ] **Review District-Wide Chronic Absenteeism Rate**
   - Look at "Key Metrics" cards at top
   - **Overall Chronic Absenteeism Rate**: __________%
   - Board's strategic goal (example: "Reduce to 12% by 2027"): __________%
   - Are we on track? [ ] Yes  [ ] No  [ ] Need more time to assess

2. [ ] **Analyze "Trend Over Time" Line Chart**
   - Shows district rate over past 3 years
   - 3 years ago: __________%
   - 2 years ago: __________%
   - 1 year ago: __________%
   - Current: __________%
   - **Trend direction**: [ ] Improving  [ ] Worsening  [ ] Stable

3. [ ] **Identify Schools Needing Support**
   - Look at "Chronic Absenteeism Rate by School" bar chart
   - Which school has **highest** rate? __________ (_________%)
   - Which school has **lowest** rate? __________ (_________%)
   - Gap between highest and lowest: __________percentage points

4. [ ] **Board Accountability Questions** (write questions you'd ask superintendent)
   - Question 1: _____________________________________________________
   - Question 2: _____________________________________________________
   - Question 3: _____________________________________________________

### Success Criteria
✅ Can assess progress toward strategic goals  
✅ Can identify schools needing additional resources  
✅ Dashboard supports accountability conversations

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 3: Equity Gap Analysis (20 min)

### Objective
Use Dashboard 3 to identify and discuss equity issues requiring board action.

### Steps

1. [ ] **Open Dashboard 3: Equity Outcomes Analysis**
   - Dashboard loads with district-wide data

2. [ ] **Review Attendance Rate by Demographic Subgroup**
   - Look at "Attendance Rate by Subgroup" bar chart
   - Identify groups with rates **below 90%** (chronic absenteeism threshold):
     1. Group: ______________ (Rate: ______%)
     2. Group: ______________ (Rate: ______%)
   - Largest gap between highest and lowest group: __________percentage points

3. [ ] **Review GPA Distribution by Subgroup**
   - Look at "GPA Distribution by Subgroup" box plot
   - Which group has lowest median GPA? __________
   - Median GPA: __________
   - Which group has highest median GPA? __________
   - Median GPA: __________
   - Achievement gap: __________GPA points

4. [ ] **Analyze Discipline Disparities**
   - Look at "Discipline Disparities" stacked bar chart
   - Which racial/ethnic group has most suspensions? __________
   - What % of total suspensions? ______%
   - What % of total enrollment is this group? ______%
   - Is discipline disproportionate? [ ] Yes (% suspensions > % enrollment)  [ ] No

5. [ ] **Review "Key Equity Metrics" Cards**
   - **Largest Attendance Gap**: ______________________________
   - **Largest GPA Gap**: ______________________________
   - **Disproportionate Discipline Group**: ______________________________
   - **% Students in Underperforming Subgroups**: ______%

6. [ ] **Board Policy Questions**
   - Based on this data, should the board:
     - [ ] Adopt an equity policy or resolution
     - [ ] Allocate budget for targeted interventions
     - [ ] Request equity action plan from superintendent
     - [ ] Provide additional support to specific schools
     - [ ] Review discipline policies for bias
   - What specific board action would you propose? _________________________
     ________________________________________________________________

### Success Criteria
✅ Can identify achievement and opportunity gaps  
✅ Can see disproportionality in discipline  
✅ Dashboard informs equity-focused policy decisions

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 4: Understand Data Relationships (10 min)

### Objective
Use Dashboard 5 to understand research-backed correlations between metrics.

### Steps

1. [ ] **Open Dashboard 5: Performance Correlations**
   - Dashboard loads with statistical correlation data

2. [ ] **Review "Key Correlations" Cards**
   - **Attendance ↔ GPA Correlation**: __________ (strength: _________)
   - **Discipline ↔ GPA Correlation**: __________ (strength: _________)
   - **Attendance ↔ Discipline Correlation**: __________ (strength: _________)

3. [ ] **Interpret Attendance ↔ GPA Correlation**
   - Is correlation positive (higher attendance = higher GPA)? [ ] Yes  [ ] No
   - Strength: [ ] Strong (0.7-1.0)  [ ] Moderate (0.4-0.7)  [ ] Weak (0.0-0.4)
   - **Board insight**: Investing in attendance programs should improve academic outcomes

4. [ ] **Interpret Discipline ↔ GPA Correlation**
   - Is correlation negative (more discipline = lower GPA)? [ ] Yes  [ ] No
   - **Board insight**: Excessive discipline may harm academic performance

5. [ ] **Policy Implications**
   - Which area should board prioritize for investment?
     - [ ] Attendance interventions (transportation, truancy, engagement)
     - [ ] Discipline reform (restorative practices, positive behavior supports)
     - [ ] Academic support (tutoring, extended learning)
   - Why? _____________________________________________________________

### Success Criteria
✅ Correlations are presented clearly for non-technical audience  
✅ Dashboard supports evidence-based decision making  
✅ Insights inform resource allocation priorities

### Issues Encountered
_______________________________________________________________________

---

## Test Scenario 5: Export for Board Meeting (5 min)

### Objective
Export dashboard data for inclusion in board meeting packet.

### Steps

1. [ ] **Export Dashboard 1 as PDF**
   - Click "⋯" (top right of Dashboard 1) → "Download as PDF"
   - Select **Landscape** orientation
   - PDF downloads successfully? [ ] Yes  [ ] No

2. [ ] **Open PDF and Review**
   - All charts are visible and legible? [ ] Yes  [ ] No
   - Text is readable (not cut off)? [ ] Yes  [ ] No
   - Suitable for printing and including in board packet? [ ] Yes  [ ] No

3. [ ] **Export Table Data as CSV**
   - Return to Dashboard 3
   - Hover over "Opportunity Gap Table"
   - Click "⋯" → "Download results" → ".csv"
   - Open CSV in Excel
   - Data is complete and readable? [ ] Yes  [ ] No

4. [ ] **Use Case Check**
   - Could you use these exports for:
     - [ ] Board meeting agenda packet
     - [ ] Public presentation at board meeting
     - [ ] Strategic planning session
     - [ ] Budget justification documentation

### Success Criteria
✅ PDF export is presentation-quality  
✅ CSV export provides detailed data for analysis  
✅ Supports board's transparency and communication needs

### Issues Encountered
_______________________________________________________________________

---

## Post-Test Feedback

### Overall Impression

1. **Usefulness**: How useful are these dashboards for board governance? (1-5)
   - [ ] 1 - Not useful  [ ] 2  [ ] 3  [ ] 4  [ ] 5 - Extremely useful

2. **Clarity**: Are the visualizations clear and easy to understand for non-technical board members?
   - [ ] Yes, very clear
   - [ ] Mostly clear, some charts confusing
   - [ ] No, too technical (explain): ___________________________________

3. **Will you use this regularly?**
   - [ ] Yes, monthly (review before board meetings)
   - [ ] Yes, quarterly (for strategic planning)
   - [ ] Yes, annually (for goal-setting)
   - [ ] No (why not?): ___________

4. **Strategic Value**: Does this help the board fulfill its governance role?
   - [ ] Yes - provides data for accountability, policy, and resource decisions
   - [ ] Somewhat - useful but missing key information
   - [ ] No - not relevant to board-level decisions

### What Worked Well
_______________________________________________________________________

### What Needs Improvement
_______________________________________________________________________

### Suggested Enhancements
_______________________________________________________________________

### Additional Data Needed for Board Decisions
_______________________________________________________________________

### Concerns About Data Interpretation
_______________________________________________________________________

---

## Sign-Off

**Tester Name**: _______________________________________  
**Board Position**: _______________________________________  
**Years on Board**: _______________________________________  
**Date**: _______________________________________  
**Signature**: _______________________________________

**UAT Facilitator**: _______________________________________

---

**End of Board Member UAT Checklist**
