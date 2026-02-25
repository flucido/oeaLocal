# Metabase Analytics - User Acceptance Testing (UAT) Plan

**Version**: 1.0  
**Date**: January 2026  
**Status**: Ready for Execution  
**Duration**: 1.5 days (8-12 hours total testing time)

---

## Overview

### Objective

Validate that Metabase analytics dashboards meet stakeholder needs, function correctly, and are ready for production deployment.

### Scope

**In Scope**:
- All 5 analytics dashboards (Chronic Absenteeism, Wellbeing, Equity, Class Effectiveness, Correlations)
- User access controls and role-based permissions
- Data accuracy and integrity
- System performance (load times, exports)
- User experience and satisfaction

**Out of Scope**:
- Source data quality (SIS data entry errors)
- Network infrastructure testing
- Browser compatibility testing (assume modern browsers)
- Mobile responsive design (desktop-only deployment)

### Success Criteria

- ✅ All 5 user groups complete testing
- ✅ ≥80% average satisfaction rating (4/5 or higher)
- ✅ Zero **critical** issues (system crashes, data loss, security breaches)
- ✅ <5 **medium/low** issues requiring fixes before production
- ✅ Users confirm accuracy of displayed data (100% match with known values)

---

## UAT Groups & Participants

### Group 1: Administrators
- **Participants**: 2-3 people (Superintendent, Assistant Superintendent, Data Director)
- **Duration**: 2 hours
- **Dashboards**: All 5 (full system access)
- **Focus**: System-wide validation, accuracy, board presentation readiness

### Group 2: School Leaders (Principals)
- **Participants**: 4-6 people (2-3 principals, 1-2 assistant principals)
- **Duration**: 1.5 hours each
- **Dashboards**: 1 (Chronic Absenteeism), 4 (Class Effectiveness)
- **Focus**: School-filtered access, intervention identification, usability

### Group 3: Counselors & Case Managers
- **Participants**: 3-4 people (School counselors, social workers)
- **Duration**: 1.5 hours
- **Dashboards**: 2 (Student Wellbeing), 3 (Equity Outcomes)
- **Focus**: Case management workflows, student identification, data privacy

### Group 4: Teachers
- **Participants**: 2-3 people (Classroom teachers from different departments)
- **Duration**: 1 hour
- **Dashboards**: 4 (Class Effectiveness - own classes only)
- **Focus**: Professional reflection, class comparison, evaluation readiness

### Group 5: Board Members
- **Participants**: 2 people (School board trustees)
- **Duration**: 1 hour
- **Dashboards**: 1 (Chronic Absenteeism - district), 3 (Equity), 5 (Correlations)
- **Focus**: Strategic insights, aggregated data, board presentation needs

---

## Testing Schedule

### Week 1: Administrator & Principal Testing

| Day | Time | Group | Participants | Location | Facilitator |
|-----|------|-------|--------------|----------|-------------|
| Monday | 9:00-11:00 AM | Administrators | Superintendent, Asst. Super., Data Director | Conf Room A | UAT Lead |
| Tuesday | 1:00-2:30 PM | Principal (Group 1) | Principal A, Principal B | Principal A's Office | UAT Lead |
| Wednesday | 1:00-2:30 PM | Principal (Group 2) | Principal C, Asst. Principal A | Principal C's Office | UAT Lead |

### Week 1: Counselor & Teacher Testing

| Day | Time | Group | Participants | Location | Facilitator |
|-----|------|-------|--------------|----------|-------------|
| Thursday | 9:00-10:30 AM | Counselors | Counselor A, Counselor B, Social Worker | Counseling Office | UAT Lead |
| Thursday | 2:00-3:00 PM | Teachers | Teacher A, Teacher B, Teacher C | Staff Lounge | UAT Lead |

### Week 1: Board Member Testing

| Day | Time | Group | Participants | Location | Facilitator |
|-----|------|-------|--------------|----------|-------------|
| Friday | 4:00-5:00 PM | Board Members | Trustee A, Trustee B | District Office | Superintendent |

---

## Test Scenarios by Role

### Administrators
See: `uat-checklist-administrators.md`

**Key Test Cases**:
1. View all dashboards across all schools
2. Filter by grade level and time range
3. Export data for board presentation (PDF, CSV)
4. Verify accuracy against raw data source (Aeries)
5. Test performance under normal load

### School Leaders (Principals)
See: `uat-checklist-principals.md`

**Key Test Cases**:
1. Access dashboards filtered to assigned school only
2. Verify cannot see other schools' data (security test)
3. Identify students needing intervention using Dashboard 1
4. Compare teacher effectiveness using Dashboard 4
5. Export student roster for SART/SARB meetings

### Counselors & Case Managers
See: `uat-checklist-counselors.md`

**Key Test Cases**:
1. Access Dashboard 2 (Wellbeing Risk Profiles)
2. Identify students for case management (High/Critical risk)
3. Export case management list
4. Verify student names and data match counselor records
5. Test row-level security (grade-level filtering)

### Teachers
See: `uat-checklist-teachers.md`

**Key Test Cases**:
1. Access Dashboard 4 (Class Effectiveness)
2. View own classes only (verify cannot see other teachers)
3. Compare class performance to school average
4. Understand effectiveness rating calculation
5. Provide feedback on usefulness for professional growth

### Board Members
See: `uat-checklist-board-members.md`

**Key Test Cases**:
1. Access Dashboards 1, 3, 5 (district-wide view)
2. Verify NO student names or IDs visible (FERPA compliance)
3. View aggregated data only
4. Export dashboard as PDF for board packet
5. Validate data supports board decision-making

---

## Performance Metrics

### System Response Targets

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| **Dashboard Load Time** | <5 seconds | Time from click to fully rendered |
| **Query Response Time** | <2 seconds | Time from filter apply to data refresh |
| **CSV Export Time** | <10 seconds | Time from export click to download |
| **PDF Export Time** | <15 seconds | Time from export click to download |
| **Concurrent Users** | 20+ users | Load test (if time permits) |

### Data Accuracy Targets

| Metric | Target | Verification Method |
|--------|--------|---------------------|
| **Data Freshness** | Yesterday's data visible this morning | Check last refresh timestamp |
| **Numeric Accuracy** | 100% match with source | Spot-check 10 students against Aeries |
| **Calculation Accuracy** | 100% match with manual calculation | Verify 3 risk scores manually |
| **Completeness** | All students present | Count total students: should = enrollment |

---

## Feedback Collection

### Real-Time Feedback (During UAT Session)

**Method**: UAT facilitator observes and takes notes
- User struggles or confusion
- Errors encountered
- Performance issues
- Positive reactions
- Feature requests

**Tool**: Issue log template (see `uat-issues-log-template.md`)

### Post-Session Feedback Form

**Method**: User completes feedback form after session
- See: `uat-feedback-form.md`
- Time to complete: 5 minutes
- Submit via: Google Form (link provided) OR paper form

**Feedback Categories**:
1. **Clarity**: How clear are the visualizations? (1-5 scale)
2. **Usefulness**: How useful is this for your role? (1-5 scale)
3. **Performance**: Is the dashboard fast enough? (Yes/No)
4. **Issues**: What problems did you encounter? (Open text)
5. **Suggestions**: What would make this better? (Open text)

### Feedback Analysis

**Process**:
1. UAT Lead collects all feedback forms (within 24 hours)
2. Calculate average ratings by role
3. Categorize issues: Critical / Medium / Low
4. Prioritize fixes based on frequency and severity
5. Create action plan for remediation

**Timeline**:
- Feedback collection: End of Week 1
- Analysis complete: Monday of Week 2
- Fixes prioritized: Tuesday of Week 2
- Remediation: Week 2 (if needed)

---

## Issue Tracking & Resolution

### Issue Categories

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **Critical** | System unusable, data loss, security breach | Immediate (same day) | Dashboard crashes, exposes student names to wrong role |
| **High** | Major functionality broken, incorrect data | 1-2 days | Filter doesn't work, wrong student count |
| **Medium** | Minor functionality issue, workaround available | 1 week | Slow performance, confusing label |
| **Low** | Cosmetic issue, enhancement request | Future release | Color scheme preference, "nice to have" feature |

### Issue Log

**Tool**: See `uat-issues-log-template.md`

**Process**:
1. UAT facilitator records issue during session
2. Assign severity and owner
3. Owner investigates and proposes fix
4. UAT Lead approves fix plan
5. Developer implements fix
6. Re-test with original reporter

**Tracking**:
- Issue log maintained in: `/oss_framework/deployment/metabase/uat/issues-log.csv`
- Daily standup to review open issues
- Target: Resolve all Critical/High before production launch

---

## Contingency Plans

### If Critical Issues Found

**Scenario**: Dashboard crashes, data security breach, major data inaccuracy

**Action Plan**:
1. **Immediate**: Stop all UAT sessions
2. **Notify**: Superintendent and IT Director
3. **Assess**: Determine root cause and scope
4. **Fix**: Developer addresses issue (priority #1)
5. **Re-test**: Original reporter validates fix
6. **Resume**: UAT continues once verified

**Timeline**: 1-3 days delay (depending on issue complexity)

---

### If Low User Satisfaction (<3/5)

**Scenario**: Users find dashboards confusing, not useful, or too slow

**Action Plan**:
1. **Identify**: What specific aspect is problematic?
   - Visualizations unclear → Simplify or add labels
   - Not useful → Re-validate business requirements
   - Too slow → Optimize queries or add caching
2. **Prototype**: Make changes in test environment
3. **Re-test**: Show updated dashboard to dissatisfied users
4. **Iterate**: Refine until satisfaction ≥4/5

**Timeline**: 3-5 days (may delay production launch)

---

### If Accuracy Issues Found

**Scenario**: Dashboard numbers don't match user expectations or source data

**Action Plan**:
1. **Reproduce**: UAT Lead verifies discrepancy
2. **Root Cause**: Is it source data issue OR calculation error?
   - **Source data issue** (SIS entry error): Document, train data entry staff
   - **Calculation error** (dashboard logic): Fix dashboard query, re-test
3. **Validate**: Spot-check 20 students manually
4. **Document**: Add to known issues if source data problem

**Timeline**: 1-2 days investigation + fix time

---

## Pre-UAT Checklist

Before starting UAT, ensure these are complete:

### Environment Setup
- [ ] Metabase is running and accessible at http://localhost:3000 (or production URL)
- [ ] All 5 dashboards created and published
- [ ] User accounts created for all UAT participants
- [ ] User groups configured (Admins, Principals, Counselors, Teachers, Board)
- [ ] Permissions set correctly (row-level security, collection access)
- [ ] Data refreshed (yesterday's data should be visible)

### Documentation Ready
- [ ] UAT plan reviewed by Superintendent
- [ ] Checklists printed for each role
- [ ] Feedback forms prepared (Google Form OR paper)
- [ ] Issue log template ready
- [ ] Training guides available as reference

### Logistics Confirmed
- [ ] UAT participants confirmed attendance
- [ ] Conference rooms booked
- [ ] Laptops/devices prepared (one per participant)
- [ ] UAT facilitator trained on dashboards
- [ ] Developer on standby for critical issues

### Communication Sent
- [ ] UAT invitation email sent (1 week prior)
- [ ] Reminder email sent (1 day prior)
- [ ] UAT schedule shared with participants
- [ ] Contact info provided (UAT Lead phone/email)

---

## Post-UAT Activities

### Week 2: Analysis & Remediation

**Day 1-2 (Mon-Tue)**:
- Compile all feedback forms
- Calculate average satisfaction ratings
- Categorize and prioritize issues
- Create fix action plan

**Day 3-4 (Wed-Thu)**:
- Implement fixes for Critical/High issues
- Re-test with original reporters
- Update documentation if needed

**Day 5 (Fri)**:
- Final sign-off from Superintendent
- Prepare for production launch (Task 4.09)

### Success Report

**Deliverable**: UAT Summary Report (1-2 pages)

**Contents**:
1. **Overview**: Number of participants, sessions completed
2. **Satisfaction**: Average ratings by role (chart)
3. **Issues**: Summary of issues found (count by severity)
4. **Resolutions**: How issues were addressed
5. **Accuracy**: Data validation results (100% match confirmed?)
6. **Performance**: Load times, export times (met targets?)
7. **Recommendations**: Changes made or deferred to future
8. **Sign-Off**: Superintendent approval to launch

**Audience**: Superintendent, Board (executive summary only)

---

## Roles & Responsibilities

| Role | Responsibility | Contact |
|------|---------------|---------|
| **UAT Lead** | Facilitate sessions, collect feedback, track issues | [Name, Email, Phone] |
| **Developer** | Fix issues, optimize performance | [Name, Email, Phone] |
| **Data Analyst** | Validate data accuracy | [Name, Email, Phone] |
| **IT Director** | Support infrastructure, troubleshoot technical issues | [Name, Email, Phone] |
| **Superintendent** | Final sign-off, escalation point | [Name, Email, Phone] |

---

## Resources

### Reference Materials
- **Training Guides**: `/oss_framework/deployment/metabase/training/`
- **Dashboard Specs**: `.sisyphus/plans/stage-4-metabase-dashboards.md`
- **Metabase Docs**: https://www.metabase.com/docs/

### Tools
- **Issue Tracker**: `issues-log.csv`
- **Feedback Forms**: `uat-feedback-form.md` (or Google Form)
- **Checklists**: `uat-checklist-*.md` (by role)

### Support
- **UAT Lead Email**: analytics@district.edu
- **UAT Lead Phone**: [Phone]
- **IT Helpdesk**: support@district.edu

---

## Appendices

### Appendix A: Sample Test Data

For UAT, use production data (yesterday's refresh). Do NOT use synthetic test data.

**Known Test Cases** (for accuracy validation):
- Student ID 12345: Chronic absenteeism risk = High (verified manually)
- School "Lincoln HS": Total enrollment = 450 (per Aeries)
- Teacher ID T789: Class effectiveness rating = Highly Effective (per calculation)

### Appendix B: UAT Schedule (Detailed)

See table in "Testing Schedule" section above.

### Appendix C: Escalation Path

1. **Level 1**: UAT facilitator attempts to resolve during session
2. **Level 2**: Developer investigates (same day)
3. **Level 3**: IT Director escalates to vendor (if Metabase issue)
4. **Level 4**: Superintendent decides: delay launch OR proceed with workaround

---

**End of UAT Plan**

**Prepared by**: Technical Team  
**Reviewed by**: Superintendent  
**Approved by**: [Signature]  
**Date**: [Date]

