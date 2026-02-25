# Metabase Analytics - Counselor Guide

**Version**: 1.0  
**Last Updated**: January 2026  
**Audience**: School Counselors, Social Workers, Case Managers  
**Access Level**: School/Grade-Filtered Access

---

## Overview

As a school counselor, you have access to dashboards that help you:
- ✅ Identify students with multi-domain risk factors (attendance, behavior, academic)
- ✅ Prioritize students for intervention and case management
- ✅ Monitor equity gaps and support underserved populations
- ✅ Track intervention effectiveness over time

**Your Dashboard Access**:
- **Dashboard 2**: Student Wellbeing Profiles (filtered to your school/grade level)
- **Dashboard 3**: Equity Outcomes Analysis (filtered to your school)

**Data Scope**: You see **only students assigned to your school and grade level(s)**. Other schools' data is not visible.

---

## Section 1: Your Dashboards

### Dashboard 2: Student Wellbeing Profiles

**Purpose**: Assess students across multiple risk domains to prioritize intervention

**What You'll See**:

1. **Risk Domain Matrix** (Bubble Chart)
   - X-axis: Attendance risk (0-100)
   - Y-axis: Discipline risk (0-100)
   - Bubble size: Academic risk (0-100)
   - Color: Primary concern (Multi-factor / Attendance / Behavior / Academic)
   - **How to use**: Click quadrants to identify students with multiple risk factors

2. **Wellbeing Risk Breakdown** (Stacked Bar)
   - Shows count of students by wellbeing level: Low / Moderate / High / Critical
   - Broken down by grade level (9-12)
   - **What to look for**: Grades with highest "Critical" count need immediate attention

3. **Primary Concern Distribution** (Horizontal Bar)
   - Categories: Multi-factor / Attendance / Behavior / Academic
   - **Action**: Allocate your time based on largest category (e.g., if "Attendance" is highest, partner with attendance team)

4. **Students by Wellbeing Level** (Table)
   - Columns: Student name, grade, attendance risk, discipline risk, academic risk, compound risk, primary concern, recommended action
   - Sorted by compound risk (highest first)
   - **Action**: Export for your case management system

5. **Risk Trend Over Time** (Line Chart)
   - Shows average compound risk score by grade level over 12 weeks
   - **What to look for**: Increasing trend = interventions not effective, need new approach

**Filters Available**:
- **Grade Level**: Select your assigned grades
- **Wellbeing Level**: Focus on High/Critical
- **Primary Concern**: Filter by domain (Attendance, Behavior, Academic)

---

### Dashboard 3: Equity Outcomes Analysis

**Purpose**: Identify achievement and opportunity gaps across demographic groups

**What You'll See**:

1. **Attendance Rate by Subgroup** (Bar Chart)
   - Compares attendance rates across: Race/Ethnicity, ELL status, SPED status, FRL status
   - **What to look for**: Gaps >5 percentage points = equity concern

2. **GPA Distribution by Subgroup** (Box Plot)
   - Shows GPA range (min, median, max) for each demographic group
   - **Action**: Identify groups with lower median GPA for targeted academic support

3. **Discipline Disparities** (Stacked Bar)
   - Count of discipline incidents by race/ethnicity
   - Segments: Minor / Major / Suspensions
   - **What to look for**: Disproportionality (e.g., one group has 15% of students but 30% of suspensions)

4. **Opportunity Gap Table** (Table)
   - Columns: Subgroup, cohort size, % good attendance, avg GPA, % passed core classes, equity flag
   - Sorted by largest gaps
   - **Action**: Use for equity conversations with admin and staff

5. **Key Equity Metrics** (4 Cards)
   - Largest attendance gap (e.g., "12 percentage points between Hispanic and White students")
   - Largest GPA gap
   - Most disproportionate discipline group
   - % of students in underperforming subgroups

**Filters Available**:
- **Demographic Group**: Select specific subgroup for deep dive
- **Outcome Type**: Attendance / Academic / Discipline
- **Grade Level**: 9-12

---

## Section 2: Common Tasks

### Task 1: Weekly Case Management Review

**Goal**: Update your caseload with new high-risk students

**Steps**:

1. Open **Dashboard 2: Student Wellbeing Profiles**
2. Apply filters:
   - **Grade Level**: Your assigned grades (e.g., 9th and 10th)
   - **Wellbeing Level**: "High" and "Critical"
3. Review **"Students by Wellbeing Level"** table
4. Identify students **not already on your caseload**:
   - Look for compound risk >70 (scale 0-100)
   - Prioritize "Critical" wellbeing level
   - Check "Primary Concern" column to understand intervention needs
5. Export table as CSV
6. Add new students to your case management system (Aeries, Google Sheets, etc.)

**Recommended Workflow**:
- **Monday AM**: Review dashboard, identify new students (5-10 per week)
- **Monday PM**: Attempt first contact (pull from class, send pass, call home)
- **By Friday**: Complete initial check-in with all new Critical students

**Documentation Tip**: In your case notes, record:
- Risk score from dashboard (e.g., "Compound risk: 78")
- Primary concern (Attendance / Behavior / Academic)
- Date added to caseload
- Initial contact outcome

---

### Task 2: Prioritize Daily Check-Ins

**Goal**: Decide which students to check in with today

**Steps**:

1. Open **Dashboard 2: Student Wellbeing Profiles**
2. Click on **Risk Domain Matrix** (bubble chart)
3. Focus on **top-right quadrant** (high attendance risk + high discipline risk)
4. Click bubbles in this quadrant to see student names
5. Cross-reference with:
   - Students you haven't contacted this week
   - Students with recent discipline referrals (check Aeries)
   - Students with parent concerns flagged
6. Create daily check-in list (3-5 students)

**Check-In Script**:
> "Hi [Student Name], I wanted to check in with you. I've noticed you've missed a few days recently and had a couple of tough situations. How are you doing? What's going on? How can I support you?"

**Red Flags to Watch For**:
- Changes in appearance or hygiene
- Social withdrawal or isolation
- Emotional dysregulation (crying, anger outbursts)
- Substance use indicators
- Suicidal ideation (follow district protocol immediately)

**Frequency**: Daily check-ins for Critical students, weekly for High students

---

### Task 3: Equity Review for School Improvement Plan

**Goal**: Provide data for school equity goals and action plans

**Steps**:

1. Open **Dashboard 3: Equity Outcomes Analysis**
2. Screenshot the following:
   - **Attendance Rate by Subgroup** bar chart
   - **GPA Distribution by Subgroup** box plot
   - **Opportunity Gap Table**
3. Export **Opportunity Gap Table** as CSV
4. Identify top 3 equity concerns, e.g.:
   - "African American students have 12% lower attendance rate than district average"
   - "ELL students have average GPA of 1.8 vs. 2.5 for non-ELL"
   - "Hispanic students are 2x more likely to receive suspension"
5. Draft equity goal for each gap:
   - "Increase African American student attendance from 82% to 90% by end of year"
   - "Increase ELL average GPA from 1.8 to 2.2 through targeted tutoring"
   - "Reduce suspension disproportionality by 50% via restorative practices"

**Present to**:
- School Site Council
- Principal (for School Improvement Plan)
- Staff (professional development day)

**Frequency**: Quarterly review (Sept, Nov, Feb, May)

---

### Task 4: Prepare for Student Support Team (SST) Meeting

**Goal**: Bring data to SST meeting for holistic student review

**Steps**:

1. Identify student for SST (e.g., "Maria Garcia, 10th grade")
2. Open **Dashboard 2: Student Wellbeing Profiles**
3. Apply filter: **Student Name** (if available) or manually find in table
4. Record student's data:
   - **Attendance risk**: 85 (High)
   - **Discipline risk**: 60 (Moderate)
   - **Academic risk**: 90 (Critical)
   - **Compound risk**: 78 (High)
   - **Primary concern**: Academic
   - **Recommended action**: "Intensive academic intervention + counseling support"
5. Click on student row to see detail view (if available)
6. Take screenshot or print PDF of student's profile
7. Bring to SST meeting along with:
   - Transcript (from Aeries)
   - Discipline history (from Aeries)
   - Teacher input forms
   - Parent communication log

**In SST Meeting**:
- Present dashboard data as **objective starting point**
- Ask team: "Given these risk factors, what interventions do you recommend?"
- Document action plan in SST notes
- Schedule follow-up SST in 6-8 weeks to review progress

**Frequency**: As needed (typically 1-3 SST meetings per week)

---

### Task 5: Monthly Equity Conversation with Staff

**Goal**: Raise staff awareness of equity gaps and enlist support

**Steps**:

1. Open **Dashboard 3: Equity Outcomes Analysis**
2. Identify one equity concern to highlight, e.g.:
   - "African American students have 20% lower pass rate in Algebra 1"
3. Screenshot relevant chart (e.g., "GPA Distribution by Subgroup")
4. Create 1-slide presentation with:
   - **Title**: "Equity Spotlight: Algebra 1 Pass Rates"
   - **Chart**: GPA distribution showing gap
   - **Question**: "What barriers might African American students be facing in Algebra 1?"
   - **Action**: "How can we culturally responsive teaching practices?"
5. Present at:
   - Staff meeting (5 minutes)
   - Department meeting (10 minutes)
   - PLC meeting (15 minutes with discussion)

**Facilitation Tips**:
- Frame as **shared responsibility**, not blame
- Ask staff for ideas, don't prescribe solutions
- Celebrate small wins ("Gap narrowed by 3 points this month!")
- Follow up next month with progress update

**Frequency**: Monthly (different equity topic each month)

---

## Section 3: Interpreting the Data

### Understanding Wellbeing Risk Levels

| Wellbeing Level | Compound Risk Score | What It Means | Counselor Action |
|-----------------|---------------------|---------------|------------------|
| **Low** | 0-40 | Student thriving, no major concerns | No action, continue universal supports |
| **Moderate** | 41-65 | Early warning signs in 1-2 domains | Brief check-in, monitor, Tier 2 intervention |
| **High** | 66-80 | Multiple risk factors, needs support | Add to caseload, Tier 2-3 intervention, SST if not improving |
| **Critical** | 81-100 | Severe risk across domains | **Immediate action**: Contact today, intensive services, consider 504/IEP |

**Important**: Compound risk is calculated as weighted average of attendance, discipline, and academic risk.

---

### Understanding Primary Concern

| Primary Concern | Definition | Example Intervention |
|-----------------|------------|---------------------|
| **Attendance** | Attendance risk is highest of 3 domains | Check-in/Check-out, attendance contract, transportation support, home visit |
| **Behavior** | Discipline risk is highest | Restorative circles, social skills group, behavior contract, mentoring |
| **Academic** | Academic risk is highest | Tutoring, study skills group, class schedule change, credit recovery |
| **Multi-factor** | Multiple domains equally high (no clear primary) | **Comprehensive plan**: Address all domains simultaneously, consider intensive case management |

**Tip**: Multi-factor students often have **underlying root cause** (e.g., housing instability, mental health, substance use). Look deeper.

---

### Understanding Equity Gaps

**What is an equity gap?**
- Difference in outcomes between demographic subgroups
- Example: "Hispanic students have 78% attendance vs. 88% district average" = **10 percentage point gap**

**How large is too large?**
- **Small gap**: <3 percentage points (may be statistical noise)
- **Moderate gap**: 3-7 percentage points (monitor, investigate causes)
- **Large gap**: >7 percentage points (**action required**, consider root cause analysis)

**Common root causes**:
- Implicit bias in discipline referrals
- Language barriers for ELL families
- Lack of culturally responsive curriculum
- Transportation barriers for low-income students
- Under-identification of SPED students in certain groups

---

## Section 4: Intervention Strategies by Risk Type

### High Attendance Risk (>70)

**Tier 2 Interventions** (Moderate risk):
- ✅ Check-in/Check-out (CICO) - daily accountability
- ✅ Attendance contract with incentives
- ✅ Parent meeting to identify barriers
- ✅ Peer mentoring (pair with strong attender)

**Tier 3 Interventions** (High/Critical risk):
- ✅ Intensive case management (weekly contact)
- ✅ Home visit with family liaison
- ✅ Transportation assistance (bus pass, carpool)
- ✅ School-Based Health Center referral
- ✅ SART/SARB process (if no improvement)

---

### High Discipline Risk (>70)

**Tier 2 Interventions**:
- ✅ Restorative circles (weekly)
- ✅ Social skills group (lunch bunch)
- ✅ Anger management curriculum
- ✅ Behavior contract with replacement behaviors

**Tier 3 Interventions**:
- ✅ Functional Behavior Assessment (FBA)
- ✅ Behavior Intervention Plan (BIP)
- ✅ Mental health counseling (individual)
- ✅ Consider 504 or IEP eligibility (Emotional Disturbance)
- ✅ Alternative education placement (if safety concern)

---

### High Academic Risk (>70)

**Tier 2 Interventions**:
- ✅ After-school tutoring (2-3x per week)
- ✅ Study skills group
- ✅ Peer tutoring or homework club
- ✅ Schedule adjustment (reduce course load, add support class)

**Tier 3 Interventions**:
- ✅ Intensive academic intervention (daily)
- ✅ Credit recovery program
- ✅ 504 plan (if testing/anxiety accommodations needed)
- ✅ IEP evaluation (if suspected learning disability)
- ✅ Alternative scheduling (evening school, independent study)

---

### Multi-Factor Risk (High in all 3 domains)

**Comprehensive Approach**:
1. **Build relationship first** - Student needs to trust you
2. **Identify root cause** - Often trauma, mental health, or family crisis
3. **Coordinate services** - Loop in mental health, family liaison, community partners
4. **Address basic needs** - Food, housing, safety (Maslow's hierarchy)
5. **Academic support** - Once stabilized, address academics

**Community Resources to Connect**:
- School-Based Health Center (mental health, physical health)
- McKinney-Vento liaison (homeless services)
- Foster youth liaison (AB 490 supports)
- Community-based organization (mentoring, after-school program)
- County mental health services (intensive therapy, case management)

---

## Section 5: Best Practices

### Time Management for Caseload

**Recommended Caseload Sizes**:
- **Crisis students** (Critical risk): Max 5-10 students (daily/weekly contact)
- **Active caseload** (High risk): Max 20-30 students (bi-weekly contact)
- **Monitoring** (Moderate risk): Max 50-75 students (monthly check-in)

**Weekly Schedule Template**:
- **Monday**: Review dashboards, identify new students, outreach planning
- **Tuesday-Thursday**: Student check-ins, groups, SST meetings, parent calls
- **Friday**: Case note documentation, data entry, planning for next week

**Efficiency Tips**:
- ✅ Batch tasks (e.g., all parent calls on Tuesday afternoon)
- ✅ Use lunch or passing period for quick check-ins
- ✅ Delegate to interns or volunteers (under supervision)
- ✅ Close cases that have stabilized (move to monitoring tier)

---

### Documentation Best Practices

**What to document in case notes**:
- Risk score from dashboard (provides objective baseline)
- Date and type of contact (e.g., "Individual check-in, 15 min")
- Student self-report (e.g., "Student reports conflict with peer")
- Interventions provided (e.g., "Taught deep breathing, scheduled follow-up")
- Referrals made (e.g., "Referred to School-Based Health Center for intake")
- Progress or concerns (e.g., "Attendance improved from 80% to 88%")

**Where to document**:
- Aeries counseling log (secure, accessible to admin)
- Google Sheets caseload tracker (for your own time management)
- Dashboard exports (save monthly snapshots to show progress)

**How often**:
- After **every** contact with student or parent
- Weekly summary for active caseload students
- Monthly review of entire caseload

---

### Privacy and FERPA Compliance

**Your Responsibilities**:
- 🔒 Access data only for students on your caseload or assigned grade level
- 🔒 Do not discuss individual students in public spaces (hallways, staff lounge)
- 🔒 Export data only for approved purposes (case management, SST, equity review)
- 🔒 Store exported data on secure, password-protected devices
- 🔒 Delete exported data after use

**When sharing data**:
- ✅ SST meetings: OK to share with team (educational need)
- ✅ Principal: OK to share for administrative purposes
- ✅ Teachers: OK to share for instructional support (only relevant students)
- ❌ Other students: Never share peer data
- ❌ Unauthorized staff: Don't share unless legitimate educational interest
- ❌ Parents: Only share **their child's data**, not other students

---

## Section 6: Troubleshooting

### Issue: Student is not showing up in dashboard

**Possible Causes**:
1. Student enrolled after data refresh (data is day-old)
2. Student is at different school (check filter)
3. Student is in grade not assigned to you (check filter)

**Solution**:
- Check **School** and **Grade Level** filters
- Verify student enrollment in Aeries
- Contact analytics team if student should appear: analytics@district.edu

---

### Issue: Risk score doesn't match my observations

**Example**: "Student seems fine in my check-ins, but dashboard shows Critical risk"

**Possible Causes**:
1. **Data lag**: Dashboard shows historical data, student may have just improved
2. **Academic risk high**: You may see social-emotional wellness, but academics are poor
3. **Student masking**: Student appears fine but is struggling internally

**Action**:
- Check **date range** (ensure looking at recent data)
- Review all 3 risk domains (attendance, discipline, academic) - may be siloed
- Use dashboard as **conversation starter**: "I see you've missed a lot of class. Tell me what's going on."

**Trust your professional judgment** - Dashboard is **one data point**, not the whole story.

---

### Issue: Equity gap data is confusing

**Example**: "Dashboard shows 'Hispanic students below average' but I thought they were doing well"

**Possible Causes**:
1. **Aggregation masking variation**: Some Hispanic students thriving, others struggling (average hides this)
2. **Comparing to wrong baseline**: Dashboard compares to district average, not school average
3. **Small sample size**: If <30 students in subgroup, data may be unreliable

**Action**:
- Click on subgroup to see **distribution** (not just average)
- Filter to your school to see school-specific patterns
- Contact analytics team for deeper analysis: analytics@district.edu

---

## Quick Reference

| Task | Dashboard | Action |
|------|-----------|--------|
| **Add students to caseload** | Dashboard 2 | Filter: High/Critical → Export table |
| **Daily check-in list** | Dashboard 2 | Click Risk Matrix → Focus top-right quadrant |
| **Equity review** | Dashboard 3 | Screenshot charts → Export gap table |
| **SST prep** | Dashboard 2 | Find student in table → Screenshot profile |
| **Staff equity presentation** | Dashboard 3 | Screenshot gap chart → Create 1-slide presentation |

---

## Getting Help

| Issue | Contact | Response Time |
|-------|---------|---------------|
| **Login problems** | IT Helpdesk: support@district.edu | 1 hour |
| **Data questions** | Analytics Team: analytics@district.edu | 24 hours |
| **Crisis resources** | School-Based Health: *(your school contact)* | Same day |
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

