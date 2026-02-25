# Metabase Analytics - Principal Guide

**Version**: 1.0  
**Last Updated**: January 2026  
**Audience**: School Principals, Assistant Principals  
**Access Level**: School-Filtered Access

---

## Overview

As a school principal, you have access to dashboards that help you:
- ✅ Monitor attendance patterns and chronic absenteeism risk at your school
- ✅ Identify students requiring intervention
- ✅ Compare class effectiveness and teacher performance
- ✅ Track trends over time to measure intervention impact

**Your Dashboard Access**:
- **Dashboard 1**: Chronic Absenteeism Risk (filtered to your school)
- **Dashboard 4**: Class Effectiveness Comparison (filtered to your school)

**Data Scope**: You see **only students and classes at your assigned school**. District-wide data is not visible.

---

## Section 1: Your Dashboards

### Dashboard 1: Chronic Absenteeism Risk

**Purpose**: Identify students at risk of chronic absenteeism (missing 10% or more of school days)

**What You'll See**:

1. **Risk Distribution Chart** (Pie Chart)
   - Shows breakdown of students by risk level: Low / Medium / High / Critical
   - **What to look for**: If >15% of students are High/Critical, immediate action needed

2. **Top 20 At-Risk Students** (Table)
   - Lists students with highest risk scores
   - Columns: Student name, grade, attendance rate, unexcused rate, risk score
   - **Action**: Contact counselor for students in "Critical" category

3. **Attendance Trend** (Line Chart)
   - Shows average attendance rate by risk level over last 90 days
   - **What to look for**: Declining trend = interventions not working

4. **Grade-Level Comparison** (Bar Chart)
   - Compares chronic absenteeism rate by grade (9-12)
   - **Action**: Target grade levels with highest rates

5. **Key Metrics** (4 Cards)
   - Total students monitored at your school
   - Overall chronic absenteeism rate
   - High/Critical risk count
   - Trend (improving or worsening)

**How to Use**:
- **Monday mornings**: Review dashboard to identify weekend absences
- **Weekly**: Check trend to see if interventions are working
- **Monthly**: Export data for staff meetings

**Filters Available**:
- **Grade Level**: Select specific grades (9, 10, 11, 12)
- **Risk Level**: Focus on High/Critical only
- **Date Range**: Last 30/60/90 days

---

### Dashboard 4: Class Effectiveness Comparison

**Purpose**: Compare class performance metrics to identify effective teaching practices and struggling classes

**What You'll See**:

1. **Class Pass Rate Comparison** (Bar Chart)
   - Shows percentage of students passing (C or better) by class section
   - **What to look for**: Classes with <70% pass rate need attention

2. **Teacher Effectiveness Ratings** (Table)
   - Lists teachers with their effectiveness rating: Highly Effective / Effective / Developing / Needs Improvement
   - Metrics: Pass rate, average attendance, average GPA, improvement trend
   - **Action**: Schedule observation for "Needs Improvement" ratings

3. **Course Performance by Department** (Grouped Bar Chart)
   - Compares pass rates across departments (Math, English, Science, etc.)
   - **What to look for**: Departments consistently below 75% need intervention

4. **Correlation: Attendance ↔ Pass Rate** (Scatter Plot)
   - Each dot = one class section
   - X-axis: Average student attendance, Y-axis: Pass rate
   - **What to look for**: Classes below trend line = attendance issues affecting performance

5. **Key Metrics** (4 Cards)
   - Total class sections at your school
   - School-wide pass rate
   - Number of "Highly Effective" classes
   - Average student attendance across classes

**How to Use**:
- **Before teacher observations**: Review effectiveness ratings to prioritize
- **Department meetings**: Share department-level performance data
- **PLC meetings**: Identify high-performing teachers to share best practices
- **End of term**: Track improvement trends, celebrate successes

**Filters Available**:
- **Department**: Math, English, Science, Social Studies, etc.
- **Grade Level**: 9-12
- **Teacher**: Select specific teacher (anonymous IDs)
- **Term**: Current term or historical comparison

---

## Section 2: Common Tasks

### Task 1: Identify Students for SART/SARB

**Goal**: Create list of students for Student Attendance Review Team (SART) or Board (SARB) meetings

**Steps**:

1. Open **Dashboard 1: Chronic Absenteeism Risk**
2. Apply filters:
   - **Risk Level**: Check "High" and "Critical" only
   - **Date Range**: Last 90 days
3. Click on **"Top 20 At-Risk Students"** table
4. Click **⋯** (three dots) → **Download results** → **.csv**
5. Open CSV in Excel
6. Sort by `risk_score` (highest first)
7. Select top 10-15 students for review

**What to Include in SART/SARB Packet**:
- Student name, grade, attendance rate (from CSV)
- Risk score and risk level (from CSV)
- Intervention history (from your SIS - Aeries)
- Parent contact log (from your SIS)

**Best Practice**: Run this report **bi-weekly** to keep intervention pipeline full.

---

### Task 2: Prepare for Staff Meeting (Attendance Focus)

**Goal**: Create attendance report for monthly staff meeting

**Steps**:

1. Open **Dashboard 1: Chronic Absenteeism Risk**
2. Apply filter: **Date Range** = Last 30 days
3. Screenshot the following visualizations:
   - Risk Distribution Chart (show staff the breakdown)
   - Grade-Level Comparison (identify problem grades)
   - Attendance Trend (show if improving or worsening)
4. Click **⋯** (top right) → **Download as PDF**
5. Save as: `Attendance_Report_[School]_[Month].pdf`

**In Staff Meeting**:
- **Celebrate wins**: "9th grade attendance improved 5% this month!"
- **Identify challenges**: "12th grade has 20% chronic absenteeism rate"
- **Set goals**: "Goal: Reduce high-risk students from 12% to 8% by end of term"
- **Share strategies**: Ask teachers of low-risk classes what's working

**Frequency**: Monthly, typically first Monday of month

---

### Task 3: Teacher Observation Prioritization

**Goal**: Identify teachers who may benefit from coaching or support

**Steps**:

1. Open **Dashboard 4: Class Effectiveness Comparison**
2. Click on **"Teacher Effectiveness Ratings"** table
3. Look for teachers with:
   - Rating: "Needs Improvement" or "Developing"
   - Pass rate: <70%
   - Negative improvement trend
4. Export table as CSV
5. Cross-reference with your observation schedule

**Action Plan by Rating**:

| Rating | Action | Priority |
|--------|--------|----------|
| **Needs Improvement** | Schedule formal observation within 2 weeks, develop improvement plan | **HIGH** |
| **Developing** | Schedule informal walkthrough, offer peer mentoring | Medium |
| **Effective** | Continue regular observation cycle | Low |
| **Highly Effective** | Observe for best practices, ask to mentor others | Low |

**Important**: Use dashboard data as **one data point**, not sole evaluation criteria. Consider:
- Class composition (ELL, SPED, honors/AP)
- Course difficulty (Algebra 2 vs. Math Support)
- Teacher experience (1st year vs. veteran)

---

### Task 4: Share Data with Counselors

**Goal**: Provide counselor team with targeted list for intervention

**Steps**:

1. Open **Dashboard 1: Chronic Absenteeism Risk**
2. Apply filters:
   - **Grade Level**: Select one grade (e.g., 10th)
   - **Risk Level**: "Medium" and "High" (Critical students likely already known)
3. Export **"Top 20 At-Risk Students"** table as CSV
4. Email to grade-level counselor with subject: "10th Grade At-Risk Students - [Date]"
5. Include message:
   > "Attached are 10th grade students showing early warning signs of chronic absenteeism. Please review and prioritize for check-ins this week. Let me know if you need support."

**Frequency**: Weekly, Monday mornings

**Best Practice**: Rotate focus grade each week to ensure all students monitored.

---

### Task 5: Parent Communication

**Goal**: Contact parents of students with declining attendance

**Steps**:

1. Open **Dashboard 1: Chronic Absenteeism Risk**
2. Filter to **Risk Level**: "High" or "Critical"
3. Click on student name in table to see detail view
4. Note:
   - Current attendance rate (e.g., 82%)
   - Number of unexcused absences last 30 days
   - Risk score (0-100)
5. Call parent or send letter with:
   - Specific data: "Your student has missed 8 days in the last 30, bringing attendance to 82%"
   - Concern: "At this rate, [student] is at risk of chronic absenteeism"
   - Action: "Let's meet to discuss barriers and create an action plan"
   - Support: "We have resources available: transportation, counseling, mentoring"

**Script Template**:
> "Hello [Parent Name], this is Principal [Your Name] from [School]. I'm calling about [Student Name]'s attendance. According to our records, [Student] has missed [X] days in the last 30 days, and their attendance rate is currently [X]%. I'm concerned because consistent attendance is critical for academic success. Can we schedule a time to meet and discuss how we can support [Student] in improving attendance?"

**Frequency**: Contact parents of all "Critical" students within 3 days of appearing on dashboard.

---

## Section 3: Interpreting the Data

### Understanding Risk Levels

| Risk Level | Attendance Rate | What It Means | Action Required |
|------------|-----------------|---------------|-----------------|
| **Low** | >95% | Student attending regularly | No action, continue monitoring |
| **Medium** | 90-95% | Early warning signs | Counselor check-in, monitor |
| **High** | 85-90% | At risk of chronic absenteeism | Parent contact, intervention plan |
| **Critical** | <85% | Chronic absenteeism or imminent | Immediate intervention, SART/SARB |

**Important**: 90% attendance = missing 1 day per 10 days = 18 days per year = **Chronic Absenteeism**

---

### Understanding Teacher Effectiveness Ratings

| Rating | Pass Rate | Attendance | What It Means |
|--------|-----------|------------|---------------|
| **Highly Effective** | >85% | >92% | Students succeeding, strong engagement |
| **Effective** | 75-85% | 88-92% | Solid performance, meeting expectations |
| **Developing** | 65-75% | 85-88% | Room for improvement, coaching needed |
| **Needs Improvement** | <65% | <85% | Significant concerns, support required |

**Important**: Ratings are **relative to school average**, not absolute thresholds.

---

### Common Data Questions

**Q: Why does my school have higher chronic absenteeism than the district average?**

**A**: Possible factors:
- Demographic differences (higher FRL, ELL, special populations)
- Transportation barriers
- School climate or safety concerns
- Community patterns (e.g., agricultural area with seasonal migration)

**Action**: Use **Dashboard 3: Equity Outcomes** (request admin access) to see breakdown by subgroup.

---

**Q: Why does a teacher with low pass rates have "Effective" rating?**

**A**: Effectiveness rating considers **multiple factors**:
- **Context**: Teaching AP Calculus vs. Algebra 1
- **Improvement trend**: Pass rate increasing over time
- **Relative performance**: Compared to similar courses
- **Attendance**: Students attending but still struggling (teaching issue vs. attendance issue)

**Action**: Use dashboard as **starting point for conversation**, not evaluation.

---

**Q: How often is data updated?**

**A**: 
- **Source data**: Exported from Aeries SIS nightly at 2 AM
- **Dashboard refresh**: Daily at 6 AM
- **Lag**: Yesterday's attendance appears this morning

**Best Practice**: Check dashboards **Monday mornings** for fresh weekend data.

---

## Section 4: Best Practices

### Data-Driven Decision Making

**DO**:
- ✅ Use dashboards **weekly** to monitor trends
- ✅ Combine dashboard data with qualitative observations
- ✅ Share data transparently with staff (aggregate, not individual student data)
- ✅ Set measurable goals: "Reduce chronic absenteeism from 15% to 10% by May"
- ✅ Celebrate improvements with staff and students

**DON'T**:
- ❌ Use dashboard data as **sole** evaluation tool for teachers
- ❌ Share individual student data in public forums (FERPA violation)
- ❌ Ignore context (e.g., flu outbreak week, state testing week)
- ❌ Make decisions on one data point (check trends over time)
- ❌ "Gotcha" culture - use data for support, not punishment

---

### Privacy and FERPA Compliance

**Your Responsibilities**:
- 🔒 Only access data for students at your school
- 🔒 Do not share student names/IDs outside of appropriate staff
- 🔒 Export data only for approved educational purposes
- 🔒 Store exported data on secure, password-protected devices
- 🔒 Delete exported data after use (e.g., after SART meeting)

**Approved Uses**:
- Staff meetings (aggregate data, no names)
- SART/SARB packets (confidential, stored securely)
- Counselor referrals (secure email or in-person)
- Parent conferences (student's own data only)

**Prohibited Uses**:
- Sharing on social media or public forums
- Discussing individual students in public spaces
- Emailing student data to unsecured personal email
- Printing and leaving data in unsecured locations

---

### Working with Your Counselor Team

**Weekly Routine**:
1. **Monday AM**: Review Dashboard 1, identify 5-10 new at-risk students
2. **Monday PM**: Email list to counselors with priorities
3. **Wednesday**: Check in with counselors on outreach progress
4. **Friday**: Review any escalations, decide on SART referrals

**Communication Tips**:
- Be specific: "10th grade has 15 students at High risk this week"
- Prioritize: "Focus on these 5 Critical students first"
- Follow up: "Did you reach the Johnson family? How can I support?"

---

## Section 5: Troubleshooting

### Issue: I can't see data for my school

**Cause**: Filter may be applied to different school, or permissions issue

**Solution**:
1. Check **School filter** at top of dashboard
2. Click filter → Select your school → Apply
3. If your school isn't listed, contact admin: analytics@district.edu

---

### Issue: Data looks wrong (numbers don't match SIS)

**Diagnostic Steps**:
1. Check **date range filter** - ensure comparing same time period
2. Check **risk level filter** - ensure not filtering out students
3. Verify data refresh date: Should be today's date

**If still wrong**:
- Export dashboard data as CSV
- Export same data from Aeries
- Email both to: analytics@district.edu with subject "Data Discrepancy - [School]"

---

### Issue: Dashboard is slow or won't load

**Solutions**:
1. **Clear browser cache**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Try different browser**: Chrome, Firefox, or Safari
3. **Check internet connection**: Run speed test
4. **Reduce date range**: Use 30 days instead of 90 days

**If still slow**: Contact helpdesk: support@district.edu

---

## Quick Reference

| Task | Dashboard | Action |
|------|-----------|--------|
| **Find at-risk students** | Dashboard 1 | Filter: High/Critical → Export table |
| **Prepare staff meeting** | Dashboard 1 | Screenshot charts → Download PDF |
| **Prioritize observations** | Dashboard 4 | Review effectiveness table → Export CSV |
| **Share with counselors** | Dashboard 1 | Filter by grade → Export → Email |
| **Contact parents** | Dashboard 1 | Click student name → Note attendance rate |

---

## Getting Help

| Issue | Contact | Response Time |
|-------|---------|---------------|
| **Login problems** | IT Helpdesk: support@district.edu | 1 hour |
| **Data questions** | Analytics Team: analytics@district.edu | 24 hours |
| **Training request** | Professional Development: pd@district.edu | 1 week |

---

## Additional Resources

- **Quick Start Guide**: `quick-start-guide.md` (basic navigation)
- **Troubleshooting Guide**: `troubleshooting-guide.md` (technical issues)
- **FAQ**: `faq.md` (common questions)
- **Video Tutorials**: *(coming soon)*

---

**Last Updated**: January 2026  
**Your Feedback**: Email analytics@district.edu with suggestions for improving this guide

