# Metabase Analytics - Troubleshooting Guide

**Version**: 1.0  
**Last Updated**: January 2026  
**Support**: analytics@district.edu

---

## Common Issues and Solutions

### Issue 1: "I can't log in"

**Symptoms**:
- Login page shows "Invalid username or password"
- Account appears locked
- Page won't load

**Solutions**:

1. **Verify your credentials**:
   - Username is your district email address (e.g., jsmith@district.edu)
   - Password is case-sensitive
   - Check Caps Lock is off

2. **Reset your password**:
   - Click "Forgot password?" on login page
   - Enter your email address
   - Check email for reset link (check spam folder)
   - Link expires in 24 hours

3. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   - Select "Cached images and files"
   - Click "Clear data"
   - Try logging in again

4. **Try a different browser**:
   - Supported: Chrome, Firefox, Safari (latest versions)
   - Unsupported: Internet Explorer

5. **Contact helpdesk**:
   - Email: analytics@district.edu
   - Include: Your name, role, and error message screenshot

---

### Issue 2: "My school's data is missing"

**Symptoms**:
- Dashboard shows "No results" or empty charts
- Row counts are zero
- Expected students don't appear

**Solutions**:

1. **Check school filter**:
   - Look at top of dashboard
   - Verify correct school is selected
   - If set to wrong school, change selection and click "Apply"

2. **Check date range filter**:
   - Default is "Last 30 days"
   - If viewing historical data, expand range to "Last 90 days"
   - Some students may have left/transferred during selected period

3. **Check other filters**:
   - Grade level: Ensure grades are checked (not all unchecked)
   - Risk level: Ensure at least one level is selected
   - Click "Reset" to clear all filters

4. **Verify data was loaded**:
   - Data updates daily at 6:00 AM
   - If viewing very recent changes, they may not appear until next day
   - Contact helpdesk if data is >24 hours stale

5. **Check your role permissions**:
   - Some roles can only see specific schools
   - Contact administrator if you need access to additional schools

---

### Issue 3: "A dashboard is slow"

**Symptoms**:
- Dashboard takes >10 seconds to load
- Visualizations show "Loading..." indefinitely
- Browser becomes unresponsive

**Solutions**:

1. **Refresh the page**:
   - Click browser refresh button or press F5
   - Wait 30 seconds for initial load

2. **Clear browser cache**:
   - Chrome: Ctrl+Shift+Delete
   - Clear "Cached images and files"
   - Restart browser

3. **Reduce filter scope**:
   - Instead of "All Schools", select one school
   - Reduce date range from 90 days to 30 days
   - Fewer filters = faster queries

4. **Check internet connection**:
   - Run speed test: fast.com
   - Minimum required: 5 Mbps download
   - If on WiFi, try moving closer to router

5. **Try different browser**:
   - Chrome usually performs best
   - Disable browser extensions temporarily
   - Close other tabs to free memory

6. **Contact helpdesk if persistent**:
   - Note which specific dashboard is slow
   - Include screenshot of loading time
   - Mention your internet speed

---

### Issue 4: "I need to report a data error"

**Symptoms**:
- Student data appears incorrect
- Counts don't match expectations
- Metrics seem wrong

**Steps to Report**:

1. **Document the issue**:
   - Dashboard name and visualization
   - Specific student (if applicable) - use ID, not name
   - Expected value vs. actual value
   - Date when error was noticed

2. **Take a screenshot**:
   - Include full dashboard with filters visible
   - Highlight the incorrect data

3. **Email helpdesk**:
   - To: analytics@district.edu
   - Subject: "Data Error Report - [Dashboard Name]"
   - Attach screenshot
   - Include documentation from Step 1

4. **Response time**:
   - Acknowledgment within 24 hours
   - Investigation within 2-3 business days
   - Resolution time varies by complexity

5. **Do NOT attempt to fix yourself**:
   - Only admins can modify data
   - Report, don't edit

---

### Issue 5: "I can't export data"

**Symptoms**:
- Download button is grayed out
- Export fails with error
- CSV file is empty

**Solutions**:

1. **Check your permissions**:
   - Some roles cannot export certain data
   - Contact admin if you need export access

2. **Try different export format**:
   - If CSV fails, try PDF
   - If PDF fails, try CSV
   - Screenshot as last resort

3. **Clear browser downloads**:
   - Empty Downloads folder
   - Ensure sufficient disk space (>100 MB)

4. **Disable popup blocker**:
   - Allow popups from Metabase URL
   - Check browser settings > Privacy

5. **Export smaller dataset**:
   - Apply more filters to reduce row count
   - Export limits: 10,000 rows for CSV
   - Split large exports into multiple smaller ones

---

### Issue 6: "Dashboard shows 'No permission to see this'"

**Symptoms**:
- Error message: "You don't have permission to see this"
- Dashboard appears in list but won't open
- 403 Forbidden error

**Solutions**:

1. **Verify your role**:
   - Different roles see different dashboards
   - Example: Teachers only see Dashboard 4
   - Check with admin if unsure of your assigned dashboards

2. **Request access**:
   - Email your school administrator
   - Explain which dashboard and why you need access
   - Include your role and justification
   - Access requests take 1-2 business days

3. **Check if you're logged in**:
   - Session may have expired
   - Log out and log back in

---

### Issue 7: "Filters aren't working"

**Symptoms**:
- Selecting filter doesn't change data
- "Apply" button does nothing
- Data shows wrong filter values

**Solutions**:

1. **Click "Apply" after selecting**:
   - Some filters require clicking "Apply" button
   - Others auto-apply (dashboard-dependent)

2. **Check for conflicting filters**:
   - Example: School A + Grade 13 = no results (no 13th grade)
   - Reset all filters and try one at a time

3. **Refresh dashboard**:
   - Click refresh icon (🔄) top right
   - Reapply filters

4. **Check filter is relevant**:
   - Not all filters apply to all visualizations
   - Some visualizations may ignore certain filters

---

### Issue 8: "I see someone else's name when logged in"

**Symptoms**:
- Dashboard shows wrong user name
- Account appears to be someone else's

**Solutions**:

1. **Log out immediately**:
   - Click user icon (top right) → Log out
   - Close browser completely

2. **Clear browser data**:
   - Clear cookies and cache
   - Close all browser windows

3. **Log in with YOUR credentials**:
   - Ensure you're using your own email

4. **Report to helpdesk immediately**:
   - This is a security issue
   - Email: analytics@district.edu
   - Subject: "URGENT: Account Access Issue"

---

### Issue 9: "Visualization shows 'Error running query'"

**Symptoms**:
- Red error message on chart/table
- "Error running query" text
- Data doesn't load

**Solutions**:

1. **Refresh the visualization**:
   - Click ⋯ on visualization
   - Select "Refresh"

2. **Check filters**:
   - Invalid filter combination may cause error
   - Click "Reset" to clear filters

3. **Wait and retry**:
   - Database may be temporarily busy
   - Wait 30 seconds and refresh

4. **Contact helpdesk if persistent**:
   - Include dashboard and visualization name
   - Screenshot error message

---

### Issue 10: "I need access to a dashboard I can't see"

**Symptoms**:
- Dashboard isn't in your list
- Search doesn't find it
- Colleagues can see it but you can't

**Solutions**:

1. **Verify it exists**:
   - Ask colleague for exact dashboard name
   - Confirm spelling

2. **Check your role**:
   - Role-based access limits what you see:
     - **Admins**: All 5 dashboards
     - **Principals**: Dashboards 1, 4
     - **Counselors**: Dashboards 2, 3
     - **Teachers**: Dashboard 4 only
     - **Board Members**: Dashboards 1, 3, 5

3. **Request access**:
   - Email administrator
   - Explain business need for access
   - Provide justification based on your role
   - Include dashboard name

4. **Access decision timeline**:
   - Request reviewed within 2 business days
   - May require approval from IT/Privacy
   - Typically granted if role-appropriate

---

## Technical Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Not logged in | Log in again |
| 403 | No permission | Request access from admin |
| 404 | Dashboard not found | Check spelling, or dashboard deleted |
| 500 | Server error | Wait 5 min, retry. If persistent, contact helpdesk |
| 503 | Service unavailable | Maintenance in progress, try later |

---

## When to Contact Helpdesk

**Contact helpdesk if**:
- ✅ Can't log in after password reset
- ✅ Data appears incorrect or missing >24 hours
- ✅ Dashboard consistently slow despite troubleshooting
- ✅ Error persists after trying all solutions
- ✅ Need access to additional dashboards
- ✅ Security concern (seeing wrong account)

**Don't contact helpdesk for**:
- ❌ Forgot password (use self-service reset)
- ❌ Don't know how to use dashboard (see role guides)
- ❌ Filter not applied (click "Apply" button)
- ❌ General training questions (see FAQ)

---

## Helpdesk Contact Information

**Email**: analytics@district.edu  
**Response Time**: Within 24 business hours  
**Urgent Issues**: Mark subject line "URGENT"

**Include in your email**:
1. Your name and role
2. Dashboard name
3. Specific issue description
4. Screenshot (if applicable)
5. Error message (if any)
6. What you've already tried

---

## Self-Service Resources

Before contacting helpdesk, check:
- **Quick Start Guide**: quick-start-guide.md
- **FAQ**: faq.md
- **Role-Specific Guide**: See your role guide
- **Training Videos**: *(coming soon)*

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Questions**: analytics@district.edu
