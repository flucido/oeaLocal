# Metabase Training Guide - OSS Student Analytics

## Overview

This guide provides comprehensive training materials for using Metabase dashboards to analyze student wellbeing and performance data.

**Quick Facts:**
- **URL**: http://localhost:3000 (or district server URL in production)
- **Login**: Use your district username and password
- **Data**: Updated daily at 2:00 AM
- **Dashboards**: 5 pre-built dashboards available to all users

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [How to Use Each Dashboard](#how-to-use-each-dashboard)
4. [Common Tasks](#common-tasks)
5. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Getting Started

### Step 1: Access Metabase

1. Open your web browser
2. Navigate to: **http://localhost:3000**
3. Enter your login credentials:
   - **Email**: Your district email (e.g., john.doe@district.local)
   - **Password**: Your district password

### Step 2: Navigate to Dashboards

Once logged in, you'll see the Metabase home page:

1. Click **"Dashboards"** (left menu) or look for dashboard cards
2. You'll see 5 available dashboards
3. Click on any dashboard to open it

### Step 3: Basic Navigation

- **Home**: Click the Metabase logo to return to home
- **Search**: Use the search box (top right) to find dashboards or questions
- **Filters**: Some dashboards have filters at the top - use these to narrow data
- **Refresh**: Click "⟳" to refresh dashboard data
- **Settings**: Click your profile icon (top right) for account settings

---

## Dashboard Overview

### Dashboard 1: Chronic Absenteeism Risk
**Purpose**: Identify students at risk of chronic absenteeism and school-level trends

**Key Visualizations**:
- **Risk Distribution**: Pie chart showing percentage of students in each risk category
- **Top 20 At-Risk Students**: Table listing students with highest absenteeism risk
- **School Comparison**: Which schools have highest absenteeism issues
- **Grade Level Analysis**: Compare risk across different grade levels

**Data Includes**:
- Last 30 days attendance data
- Unexcused absence rates
- Discipline incidents correlation
- 90-day trends

**Who Should Use**: Attendance counselors, principals, grade-level teachers

---

### Dashboard 2: Wellbeing & Mental Health Risk
**Purpose**: Comprehensive student wellbeing assessment across multiple domains

**Key Visualizations**:
- **Overall Risk Distribution**: How many students in each wellbeing category
- **Multi-Domain Risk**: Heatmap showing attendance, discipline, and academic risks
- **Primary Concern**: What's the main issue for at-risk students
- **High-Risk Domain Count**: How many problem areas does each student have
- **Critical Students**: Students requiring immediate intervention

**Data Includes**:
- Attendance risk (last 30 days)
- Discipline risk (incident history)
- Academic risk (grades, graduation probability)
- Compound risk score (weighted average)

**Who Should Use**: Counselors, social workers, intervention specialists

---

### Dashboard 3: Equity Outcomes Analysis
**Purpose**: Identify disparities in student outcomes across demographic groups

**Key Visualizations**:
- **Equity Outcomes by Group**: Compare attendance, GPA, and discipline across demographics
- **Attendance Equity Gap**: Which groups have lower attendance
- **GPA Distribution**: Academic performance by demographic
- **College Readiness**: Percentage college-ready (GPA ≥ 2.5) by group
- **Discipline Equity**: Discipline incident rates by demographic

**Data Includes**:
- Race/ethnicity breakdown
- ELL (English Language Learner) students
- SPED (Special Education) students
- FRL (Free/Reduced Lunch) students

**Who Should Use**: Administrators, equity officers, program coordinators

---

### Dashboard 4: Class Effectiveness & Teacher Quality
**Purpose**: Understand which courses and teachers are most effective

**Key Visualizations**:
- **Effectiveness Rating Distribution**: Count of highly effective vs. needs improvement classes
- **Top Performing Classes**: Highest pass rate and grade average courses
- **Pass Rate vs. Class Size**: Does class size affect performance
- **Equity in Class Performance**: Do ELL, SPED, FRL students pass at similar rates
- **Course Effectiveness Comparison**: Average performance by course
- **Grade Distribution**: Range of grades across all sections

**Data Includes**:
- Student pass rates by class
- Average grades by section
- Pass rates for subgroups (ELL, SPED, FRL)
- Teacher effectiveness ratings

**Who Should Use**: Instructional coaches, curriculum specialists, administrators

---

### Dashboard 5: Performance Correlations & Insights
**Purpose**: Understand statistical relationships between key metrics

**Key Visualizations**:
- **Key Correlations**: Strength of relationship between attendance, discipline, and GPA
- **Correlation Strength**: Is each relationship strong, moderate, or weak
- **Positive vs. Negative**: Which relationships help or hurt outcomes
- **Statistical Confidence**: How confident are we in these relationships

**Data Includes**:
- Pearson correlation coefficients (-1 to +1)
- Statistical strength (Strong/Moderate/Weak/Negligible)
- Relationship direction (Positive/Negative)
- Sample size and confidence level

**Who Should Use**: Data analysts, researchers, strategic planners

---

## How to Use Each Dashboard

### Viewing Data

1. **Open a Dashboard**: Click on dashboard name from the home page
2. **Read the visualizations**: 
   - Look at titles and labels to understand what each chart shows
   - Note the data range (e.g., "Last 30 days")
3. **Hover over data**: Hover your mouse over charts to see exact numbers
4. **Click for details**: Click on chart elements to see underlying data

### Using Filters

Some dashboards have filter buttons at the top:

1. **Click the filter button** (looks like "⋙")
2. **Select criteria** (e.g., School, Grade Level)
3. **Apply**: The dashboard updates automatically
4. **Clear filters**: Click "Reset all filters"

### Exporting Data

To download data from a dashboard:

1. **View a specific visualization** you want to export
2. **Click the three dots "⋮"** (top right of visualization)
3. **Select "Download"**
4. **Choose format**: CSV, PNG, or native
5. **Save** to your computer

### Creating Your Own Questions

To write a custom query:

1. Click **"+ New"** (top right)
2. Select **"SQL query"**
3. Choose database: **"OSS Analytics"**
4. Write your SQL query
5. Click **"▶ Run"** to execute
6. Save as new question if desired

---

## Common Tasks

### Task 1: Find At-Risk Students

1. Open **Dashboard 1: Chronic Absenteeism Risk**
2. Look at **"Top 20 At-Risk Students"** table
3. Click on any student row for details (if enabled)
4. Export the table if needed for intervention planning

### Task 2: Monitor Equity Gaps

1. Open **Dashboard 3: Equity Outcomes Analysis**
2. Review **"Attendance Equity Gap"** bar chart
3. Note which demographic groups have lowest attendance
4. Click through to see which courses/schools have the gaps

### Task 3: Evaluate Teacher Effectiveness

1. Open **Dashboard 4: Class Effectiveness**
2. Sort by **"Top Performing Classes"**
3. Note the characteristics of highly effective sections
4. Compare to lower-performing sections in same course

### Task 4: Understand Data Relationships

1. Open **Dashboard 5: Performance Correlations**
2. Review the correlation table
3. Note which correlations are strongest
4. Use this to inform intervention strategies

### Task 5: Generate a Report

1. Open desired dashboard(s)
2. Apply filters to narrow scope
3. Take screenshots or export visualizations
4. Create a presentation or document
5. Share findings with colleagues

---

## FAQ & Troubleshooting

### Q: I forgot my password. What do I do?

**A:** Contact your district IT department. They can reset your password through the system.

### Q: The dashboard is loading slowly. Why?

**A:** 
- The database might be syncing (happens daily at 2:00 AM)
- Try refreshing your browser
- If still slow, close other browser tabs/applications
- Contact IT support if problem persists

### Q: Why is the data different than what I expected?

**A:**
- Data is updated daily at 2:00 AM - you might be looking at previous day's snapshot
- Some data points are aggregated/rounded for privacy (e.g., groups with <5 students are hidden)
- Review the data definitions in the "Data Dictionary" below

### Q: Can I edit or delete a dashboard?

**A:**
- If you're an **Administrator** or **Data Analyst**: Yes, but changes affect everyone
- If you're an **Educator**: No, you have view-only access
- Contact your administrator if you need editing access

### Q: How do I share a dashboard with someone else?

**A:**
1. Open the dashboard
2. Click the **share icon** (top right)
3. Choose sharing method:
   - **Email**: Send link to colleague
   - **Embed**: Get code to embed in website
   - **Public link**: Create shareable URL

### Q: What does "risk score" mean?

**A:** Risk scores (0-100) are calculated using a machine learning algorithm that weighs:
- Attendance patterns
- Discipline incidents
- Academic performance
- Historical trends

A higher score means higher risk of negative outcomes.

### Q: How often is data refreshed?

**A:** 
- **Automatic refresh**: Daily at 2:00 AM
- **Manual refresh**: Click the "⟳" button on any dashboard
- **Real-time data**: Not available (30-day delay for data privacy and aggregation)

### Q: Can I access this from home?

**A:** 
- **Local access**: Yes, if on district VPN or network
- **Remote access**: Contact IT to set up secure remote access
- **Mobile**: Metabase has mobile app (iOS/Android)

---

## Data Definitions

### Common Terms

| Term | Definition |
|------|-----------|
| **Risk Score** | 0-100 scale where higher = more at-risk |
| **Well being Risk Level** | Category: Low / Moderate / High / Critical |
| **Attendance Rate** | Percentage of school days student attended (0-100%) |
| **Unexcused Absence** | Absence not approved by parent/school |
| **Discipline Incident** | Any formal disciplinary action |
| **GPA** | Grade Point Average (0-4.0 scale) |
| **Pass Rate** | % of students earning passing grade in class |
| **Effectiveness Rating** | Teacher/class rating: Highly Effective / Effective / Adequate / Needs Improvement |

### Data Availability

| Dashboard | Data Period | Update Frequency |
|-----------|-------------|------------------|
| Chronic Absenteeism | Last 30-90 days | Daily at 2 AM |
| Wellbeing Risk | Current year | Daily at 2 AM |
| Equity Outcomes | Current year | Daily at 2 AM |
| Class Effectiveness | Current year | Daily at 2 AM |
| Performance Correlations | Full history | Daily at 2 AM |

---

## Privacy & Security

### Data Protection

- All student data is **pseudonymized** (real names replaced with codes)
- Data is encrypted in transit and at rest
- Only authorized staff can access student information
- Audit logs track all data access

### Your Responsibilities

- **Don't share credentials**: Your login is personal - don't give password to others
- **Report suspicious activity**: Contact IT if you see unauthorized access
- **Use data responsibly**: Only access data you need for your role
- **Protect student privacy**: Don't screenshot or share individual student data without permission

---

## Getting Help

### Support Resources

1. **This Guide**: Review the FAQ and How-To sections
2. **In-App Help**: Click "?" icon in Metabase for built-in help
3. **IT Help Desk**: Contact district IT for technical issues
4. **Data Team**: Contact analytics team for data questions

### Contact Information

- **IT Help Desk**: (XXX) XXX-XXXX or it-support@district.local
- **Analytics Team**: analytics@district.local
- **Metabase Documentation**: https://www.metabase.com/docs/latest/

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Open quick search |
| `Esc` | Close dialog/menu |
| `Ctrl/Cmd + D` | Go to dashboards |
| `Ctrl/Cmd + Shift + /` | Open help |
| `Ctrl/Cmd + ,` | Open settings |

---

## Tips & Tricks

### Tip 1: Save Your Favorite Dashboards

Click the **star icon** on a dashboard to save it as favorite. These appear at the top of your home page.

### Tip 2: Create Custom Views

Use the SQL query editor to create custom questions:
- Choose specific columns
- Filter to specific schools/grades
- Create calculations
- Save for later use

### Tip 3: Schedule Email Reports

1. Open a dashboard
2. Click **"⋮"** (three dots)
3. Select **"Schedule email"**
4. Choose frequency (daily, weekly, etc.)
5. Receive automated reports

### Tip 4: Drill Down into Data

Many visualizations allow drilling down:
1. Click on a bar, slice, or data point
2. View filtered detail view
3. Continue clicking to explore

### Tip 5: Compare Across Time

Use date filters to compare:
- Current week vs. last week
- This month vs. last month
- Year-over-year trends

---

## Training Checklist

After this training, you should be able to:

- [ ] Log into Metabase with your credentials
- [ ] Navigate between dashboards
- [ ] Understand what each dashboard shows
- [ ] Apply filters to focus on specific data
- [ ] Export data for reports
- [ ] Create a simple SQL query
- [ ] Share a dashboard with colleagues
- [ ] Find the answer to common questions in FAQs

---

## Next Steps

1. **Practice**: Spend 15 minutes exploring each dashboard
2. **Experiment**: Try filters, exports, and different views
3. **Ask Questions**: Use the FAQ or contact support
4. **Share**: Show your colleagues what you learned
5. **Integrate**: Use Metabase insights in your daily work

---

## Document Information

- **Created**: January 27, 2026
- **Metabase Version**: Latest
- **Data Updated**: Daily at 2:00 AM
- **Questions**: Contact analytics@district.local

---

**Thank you for participating in OSS Student Analytics training! We're excited to empower your decision-making with data. 📊**
