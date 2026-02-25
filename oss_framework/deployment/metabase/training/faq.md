# Metabase Analytics - Frequently Asked Questions (FAQ)

**Version**: 1.0  
**Last Updated**: January 2026  
**Audience**: All Users

---

## General Questions

### 1. How often is data updated?

Data refreshes **daily at 6:00 AM** via automated process.

- Data reflects the **previous day** as of 6 AM
- Example: On Tuesday at 9 AM, you see data through Monday 11:59 PM
- Timeframe: Data updated within 30 minutes (6:00-6:30 AM)
- If urgent data needed: Contact helpdesk for manual refresh

### 2. How far back does the data go?

**Current school year only**

- Historical view: Up to 90 days (via date range filter)
- Trend analysis: 30-day, 60-day, or 90-day windows
- Previous years: Not available in current system
- Graduated students: Archived after 5 years per FERPA policy

### 3. Can I see student names?

**Depends on your role**:

| Role | See Student Names? | See Student IDs? |
|------|-------------------|------------------|
| Administrator | Yes | Yes (hashed) |
| Principal | Yes (your school only) | Yes (hashed) |
| Counselor | Yes (your school/grade) | Yes (hashed) |
| Teacher | Yes (your classes only) | Yes (hashed) |
| Board Member | **NO** | **NO** |

**Privacy Note**: All data is FERPA-protected. Do not share student-identifiable information via unsecured channels.

### 4. Can I access Metabase from home?

**Check with your IT department**.

Access policy varies by district:
- Some districts: VPN required
- Some districts: District network only
- Some districts: Full remote access

Security requirements:
- Use district-issued device (if required)
- Connect via VPN (if required)
- Do not access from public WiFi

### 5. What browsers are supported?

**Supported** (latest versions):
- ✅ Google Chrome (recommended)
- ✅ Mozilla Firefox
- ✅ Safari (Mac only)
- ✅ Microsoft Edge (Chromium version)

**Not supported**:
- ❌ Internet Explorer (any version)
- ❌ Opera
- ❌ Older browser versions (>2 years old)

**Performance**: Chrome typically performs best with Metabase.

---

## Data Questions

### 6. What does "risk score" mean?

**Risk Score**: 0-100 composite metric combining:
- **Attendance** (30% weight): Attendance rate, absences
- **Behavior** (30% weight): Discipline incidents, suspensions
- **Academics** (40% weight): GPA, failing grades, course completion

**Interpretation**:
- 0-25: **Low risk** - On track
- 26-50: **Medium risk** - Early warning signs
- 51-75: **High risk** - Intervention recommended
- 76-100: **Critical risk** - Immediate action required

**Calculation**: Automated daily based on latest data from Aeries SIS.

### 7. What is "chronic absenteeism"?

**Definition**: Missing 10% or more of school days.

**Math**:
- 180 school days per year
- 10% = 18 days
- **Chronically absent** = Missed 18+ days

**Why it matters**:
- National accountability metric
- Research shows 18+ absences → lower achievement
- Used for federal/state reporting

**Includes**:
- Excused absences (sick, appointments)
- Unexcused absences (truancy)
- Suspensions (if out of school)

**Excludes**:
- School holidays
- District closures (snow days, etc.)
- Approved independent study

### 8. How is GPA calculated?

**Standard 4.0 scale**:
- A = 4.0
- B = 3.0
- C = 2.0
- D = 1.0
- F = 0.0

**Calculation**: Average of all courses

**Source**: Pulled directly from Aeries SIS

**Updates**: Recalculated daily when grades are posted

**Note**: Weighted GPA (honors/AP) not currently included in analytics.

### 9. What does "wellbeing risk level" mean?

**Four levels**:

**Low** (Green):
- Attendance >90%
- No discipline incidents
- GPA >2.5
- On track academically

**Medium** (Yellow):
- Attendance 80-90%
- 1-2 minor discipline incidents
- GPA 2.0-2.5
- Some concerns, monitoring needed

**High** (Orange):
- Attendance 70-80%
- 3+ discipline incidents OR 1 major
- GPA 1.5-2.0
- Multiple risk factors, intervention recommended

**Critical** (Red):
- Attendance <70%
- Serious/repeated discipline issues
- GPA <1.5
- Immediate comprehensive intervention needed

### 10. Why don't I see a specific student?

**Possible reasons**:

1. **Not in your assigned scope**:
   - Principals: Student is at different school
   - Counselors: Student is in different grade level
   - Teachers: Student not in your class

2. **Data filters applied**:
   - Check school filter
   - Check grade level filter
   - Check risk level filter
   - Click "Reset" to clear all filters

3. **Student transferred/graduated**:
   - Check date range (student may have left mid-year)
   - Graduated students archived annually

4. **Data privacy suppression**:
   - Cells with <10 students may be suppressed
   - Aggregate views don't show individual students

5. **Data sync timing**:
   - New enrollments appear next day (after 6 AM refresh)

**Still can't find them?** Contact helpdesk with student ID.

---

## Dashboard Functionality

### 11. Can I create my own dashboards?

**Admins only**.

Regular users cannot create custom dashboards for security/data governance reasons.

**If you need a custom report**:
1. Email analytics@district.edu
2. Describe what data you need
3. Explain business use case
4. Include mockup/sketch if possible
5. Typical turnaround: 2-4 weeks

### 12. Can I save my filter settings?

**Not currently available**.

Workaround:
- Bookmark the dashboard URL after applying filters
- Filters are encoded in URL parameters
- Clicking bookmark restores your filter settings

Future feature: Saved filter presets (on roadmap).

### 13. Can I share a dashboard link with colleagues?

**Yes, but...**

- Recipient must have Metabase account
- Recipient must have permission to view that dashboard
- Sharing doesn't grant permission (admin does)

**How to share**:
1. Copy dashboard URL from browser address bar
2. Email/message to colleague
3. They click link and log in
4. If they lack permission, they'll see "403 Forbidden"

**Tip**: Share screenshot instead if colleague doesn't need interactive access.

### 14. How do I export data?

**CSV Export** (tables/data):
1. Hover over table or chart
2. Click ⋯ (three dots) in top right
3. Select "Download results"
4. Choose ".csv"
5. Open in Excel/Google Sheets

**PDF Export** (dashboard/report):
1. Click ⋯ at top right of dashboard
2. Select "Print" or "Download as PDF"
3. Configure settings
4. Download

**Limits**:
- CSV: Up to 10,000 rows per export
- PDF: All visualizations on dashboard

**FERPA Reminder**: Exported files contain student data. Secure them appropriately.

### 15. Can I print dashboards?

**Yes**.

**Method 1 - Browser Print**:
1. Click ⋯ (top right of dashboard)
2. Select "Print"
3. Use browser print dialog
4. **Tip**: Use Landscape orientation for wide dashboards

**Method 2 - PDF Export**:
1. Export to PDF (see Q14)
2. Open PDF
3. Print from PDF viewer

**Best practices**:
- Remove sensitive data before printing if leaving unattended
- Use color printer for risk-level color coding
- Print one dashboard per page (don't combine)

---

## Access & Permissions

### 16. How do I reset my password?

**Self-service reset**:
1. Go to Metabase login page
2. Click "Forgot password?"
3. Enter your email address
4. Check email for reset link (check spam)
5. Click link and create new password
6. Log in with new password

**Password requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Cannot reuse last 5 passwords

**Link expires**: 24 hours

**Still having trouble?** Email analytics@district.edu

### 17. Who do I contact for access to additional dashboards?

**Your school/district administrator**.

Access decisions based on:
- Your role (principal, counselor, teacher, etc.)
- Business need (why do you need access?)
- Data governance policies
- FERPA compliance

**Process**:
1. Email administrator with request
2. Explain which dashboard and why
3. Wait for approval (1-2 business days)
4. Administrator submits request to IT
5. Access granted within 48 hours of approval

### 18. What if I see data I shouldn't have access to?

**Report immediately**:
1. **Do NOT** screenshot or download the data
2. **Log out** immediately
3. **Email** analytics@district.edu
4. **Subject**: "URGENT: Data Access Issue"
5. **Describe** what you saw and why it's unexpected

This is a security/privacy issue and will be investigated promptly.

### 19. Can I delegate my dashboard access to someone else?

**NO**.

Sharing credentials violates:
- District IT policy
- FERPA regulations
- Acceptable use agreement

Each user must have their own account with appropriate permissions.

**If someone needs access**: They must request their own account through administrator.

---

## Technical Questions

### 20. Why is the dashboard slow sometimes?

**Common causes**:

1. **Large data volume**:
   - "All Schools" + "All Grades" = slower
   - Solution: Filter to specific school or grade

2. **Complex visualizations**:
   - Charts with 1,000+ data points take longer
   - Solution: Apply date range filter (reduce from 90 to 30 days)

3. **Peak usage times**:
   - 8-9 AM and 12-1 PM typically busiest
   - Solution: Use dashboards at off-peak times

4. **Browser performance**:
   - Too many tabs open
   - Solution: Close unused tabs, clear cache

5. **Network speed**:
   - Slow WiFi or internet
   - Solution: Move closer to router, use wired connection

**Acceptable performance**: <5 seconds to load dashboard

**If consistently slow**: See Troubleshooting Guide or contact helpdesk.

### 21. What happens if the system goes down?

**During planned maintenance**:
- Advance notice via email (48 hours)
- Typically outside school hours
- Duration: 1-2 hours
- Banner notification on login page

**During unplanned outage**:
- IT automatically notified
- Status updates via email
- Typical resolution: <4 hours
- Check email for updates

**Workaround**: Email analytics@district.edu for urgent data needs during outages.

### 22. Is my data secure?

**Yes**. Security measures include:

**Technical**:
- ✅ Encrypted connections (HTTPS)
- ✅ Role-based access control
- ✅ Audit logging (all access tracked)
- ✅ Regular security updates
- ✅ Nightly backups

**Policy**:
- ✅ FERPA compliant
- ✅ Annual security training required
- ✅ Data use agreements signed
- ✅ Regular compliance audits

**Your responsibility**:
- Don't share passwords
- Log out when done
- Don't export to personal devices
- Report security concerns immediately

---

## Support

### 23. How do I get training?

**Resources available**:
- **Quick Start Guide**: quick-start-guide.md
- **Role-Specific Guides**: See admin-guide.md, principal-guide.md, etc.
- **Troubleshooting Guide**: troubleshooting-guide.md
- **FAQ**: This document
- **Training Videos**: *(coming soon)*

**Live training sessions**:
- Scheduled at beginning of school year
- Role-based sessions (principals, counselors, teachers)
- Duration: 45 minutes
- Recorded for later viewing

**Request training**:
- Email analytics@district.edu
- Subject: "Training Request"
- Include your role and preferred dates

### 24. Where do I report a bug or request a feature?

**Email**: analytics@district.edu

**Bug report should include**:
1. What you were doing
2. What you expected to happen
3. What actually happened
4. Screenshot (if applicable)
5. Your browser and version

**Feature request should include**:
1. What you need
2. Why you need it (use case)
3. How often you'd use it
4. How urgent (critical vs. nice-to-have)

**Timeline**:
- Bugs: Assessed within 2 business days
- Features: Added to roadmap, prioritized quarterly

### 25. Who do I contact for help?

**For all Metabase questions/issues**:
- **Email**: analytics@district.edu
- **Response Time**: Within 24 business hours
- **Urgent Issues**: Mark subject "URGENT" (response within 4 hours)

**Include in your request**:
- Your name and role
- Dashboard name (if applicable)
- Issue description
- What you've already tried
- Screenshot (if helpful)

**Before contacting**:
- Check this FAQ
- Check Troubleshooting Guide
- Try basic troubleshooting (refresh, clear cache, log out/in)

---

## Additional Resources

- **Quick Start Guide**: quick-start-guide.md
- **Troubleshooting Guide**: troubleshooting-guide.md
- **Admin Guide**: admin-guide.md
- **Principal Guide**: principal-guide.md
- **Counselor Guide**: counselor-guide.md
- **Teacher Guide**: teacher-guide.md
- **Board Member Guide**: board-member-guide.md

---

**Have a question not answered here?**  
Email: analytics@district.edu

**Last Updated**: January 2026  
**Version**: 1.0
