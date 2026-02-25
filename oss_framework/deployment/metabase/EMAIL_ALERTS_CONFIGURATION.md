# Email Alerts & Automated Reports Configuration Guide

**Status**: ✅ **Configuration Ready**  
**Date**: January 27, 2026  
**Effort**: 20-30 minutes setup + testing

---

## Overview

This guide enables automated email notifications and scheduled reports in Metabase to proactively notify stakeholders about at-risk students and key metrics.

---

## Architecture

```
Metabase Dashboard
       │
       ├─→ Alert Rule
       │   (e.g., >10% at-risk students)
       │   └─→ Email Notification
       │       (Sent to specified recipients)
       │
       └─→ Scheduled Report
           (e.g., Daily/Weekly dashboard)
           └─→ Email Delivery
               (With dashboard snapshot)
```

---

## Prerequisites

### 1. SMTP Configuration

You'll need:
- **SMTP Server**: smtp.gmail.com, smtp.office365.com, or your district's mail server
- **Email Account**: service account (e.g., metabase@yourdomain.com)
- **Password**: SMTP password or app-specific password
- **Port**: 587 (TLS) or 465 (SSL)

### 2. District Approval

- Confirm email sending is allowed by IT policy
- Get list of recipient email addresses
- Verify SMTP credentials

---

## Part 1: Configure SMTP Email

### Step 1: Access Admin Settings

1. Open Metabase: https://localhost:3000
2. Click **Settings** (gear icon, top right)
3. Click **Admin Settings**
4. Go to **Email** in the sidebar

### Step 2: Enable Email

```
SMTP Host: smtp.gmail.com          (Gmail)
           smtp.office365.com       (Outlook)
           mail.yourdomain.com      (Your domain)

SMTP Port: 587                      (TLS)
           465                      (SSL)

SMTP Username: metabase@gmail.com
               metabase@yourdomain.com

SMTP Password: [App-specific password]

From Address: metabase@yourdomain.com
From Name: Metabase Analytics

TLS Required: Yes (checked)
```

### Step 3: Test Email Connection

1. Enter test email address in "Send a test email"
2. Click **Send test email**
3. Check inbox for test email
4. If successful, save settings

### Step 4: Example SMTP Credentials

**For Gmail:**
- Host: smtp.gmail.com
- Port: 587
- Username: your-email@gmail.com
- Password: [App-specific password - see setup below]
- TLS: Yes

**For Microsoft Outlook:**
- Host: smtp.office365.com
- Port: 587
- Username: your-email@outlook.com
- Password: Your Outlook password
- TLS: Yes

**For Custom Domain:**
- Contact IT for SMTP details
- Usually: mail.yourdomain.com or smtp.yourdomain.com
- Port: 587 or 465

---

## Part 2: Create Alert Rules

### Alert 1: High At-Risk Student Count

**Purpose**: Notify when too many students are at-risk

#### Step 1: Navigate to Question

1. Go to: Dashboard 2 (Chronic Absenteeism Risk)
2. Or create new question with SQL:
   ```sql
   SELECT COUNT(*) as at_risk_count
   FROM v_chronic_absenteeism_risk
   WHERE risk_level IN ('High', 'Critical')
   ```

#### Step 2: Set Alert

1. Click **📊 Visualization** button
2. Click **⚙️ Settings** → **Alerts**
3. Click **+ Add alert**

#### Step 3: Configure Alert

```
Alert Name: Critical Absenteeism Risk Count

Condition: When this question returns
Greater than or equal to: 340

(340 = 10% of 3,400 students)

Send to: [recipients list]
Recipients:
  - counselor@yourdomain.com
  - principal@yourdomain.com
  - data-team@yourdomain.com

Check frequency:
  Every: 1 hour
  (Or daily, weekly, etc.)

Include details: Yes (shows query results in email)
```

#### Step 4: Save Alert

✅ Alert will monitor student at-risk count automatically

---

### Alert 2: Specific Class Performance Drop

**Purpose**: Alert when a class GPA drops below threshold

#### Step 1: Create Question

```sql
SELECT 
    class_section,
    ROUND(avg_gpa, 2) as avg_gpa,
    ROUND(pct_pass, 1) as pct_pass
FROM v_class_section_comparison
WHERE avg_gpa < 2.0
ORDER BY avg_gpa
```

#### Step 2: Configure Alert

```
Alert Name: Classes at Critical GPA

Condition: When this question returns
Greater than or equal to: 5

(Alert if 5+ classes below 2.0 GPA)

Recipients: academic-team@yourdomain.com

Check frequency: Daily at 8:00 AM
```

---

### Alert 3: Equity Disparity Detection

**Purpose**: Alert on demographic performance gaps

#### Step 1: Create Question

```sql
SELECT 
    demographic_group,
    ROUND(gpa_disparity, 2) as gpa_gap,
    ROUND(attendance_disparity, 2) as attendance_gap
FROM v_equity_outcomes_by_demographics
WHERE gpa_disparity > 0.5
```

#### Step 2: Configure Alert

```
Alert Name: Equity Disparity Alert

Condition: When this question returns
Greater than or equal to: 1

(Alert if any demographic has >0.5 GPA gap)

Recipients: equity-team@yourdomain.com

Check frequency: Weekly (Monday 9:00 AM)
```

---

## Part 3: Create Scheduled Reports

### Report 1: Daily At-Risk Summary

**Frequency**: Every morning at 7:00 AM  
**Recipients**: All stakeholders

#### Step 1: Create Dashboard Snapshot

1. Go to: Dashboard 2 (Chronic Absenteeism Risk)
2. Click **📧 Share** → **Email dashboard**

#### Step 2: Schedule Delivery

```
Dashboard: Chronic Absenteeism Risk

Schedule: Daily
Time: 7:00 AM (school start time)

Recipients:
  - counselors@yourdomain.com
  - principal@yourdomain.com
  - data-analysts@yourdomain.com

Include filters: Yes (default filters applied)
```

#### Step 3: Customize Message

```
Subject: 📊 Daily At-Risk Student Summary

Message:
"Attached is your daily summary of students at-risk for chronic absenteeism.

Key metrics:
- Students monitored: 3,400
- At-risk: [Count in attachment]
- High priority: [Critical count]

Click the link below to view interactive dashboard for details:
https://metabase.yourdomain.com/dashboard/2"
```

### Report 2: Weekly Equity Analysis

**Frequency**: Every Friday at 4:00 PM  
**Recipients**: Leadership team

#### Step 1: Schedule Equity Dashboard

1. Go to: Dashboard 4 (Equity Outcomes Analysis)
2. Click **📧 Share** → **Email dashboard**

#### Step 2: Configure Schedule

```
Dashboard: Equity Outcomes Analysis

Schedule: Weekly (Friday)
Time: 4:00 PM (end of school week)

Recipients: leadership@yourdomain.com

Frequency: Recurring every week

Include attached PDF: Yes
```

### Report 3: Monthly Class Effectiveness Report

**Frequency**: First of each month  
**Recipients**: Academic leadership

#### Step 1: Create Custom Summary

SQL Query for report:
```sql
SELECT 
    'Class Effectiveness Summary' as report_name,
    COUNT(*) as total_classes,
    ROUND(AVG(avg_gpa), 2) as avg_district_gpa,
    COUNT(CASE WHEN avg_gpa >= 3.5 THEN 1 END) as excellent_count,
    COUNT(CASE WHEN avg_gpa < 2.0 THEN 1 END) as at_risk_count
FROM v_class_section_comparison
```

#### Step 2: Schedule Delivery

```
Dashboard: Class Effectiveness & Teacher Quality

Schedule: Monthly
Day: 1st of month
Time: 8:00 AM

Recipients: academic-leadership@yourdomain.com

Subject: 📊 Monthly Class Effectiveness Report
```

---

## Part 4: Alert Thresholds Reference

### Recommended Alert Thresholds

#### Chronic Absenteeism
```
🟡 Yellow Alert (High):    >25% of students (850+)
🔴 Red Alert (Critical):   >35% of students (1,190+)

Frequency: Daily check
Recipients: Counseling team
```

#### Wellbeing Risk
```
🟡 Yellow Alert:   >30% multi-domain risk (1,020+ students)
🔴 Red Alert:      >45% critical level (1,530+ students)

Frequency: Daily check
Recipients: Student services, counselors
```

#### Equity Disparities
```
🟡 Yellow Alert:   GPA gap > 0.25 between groups
🔴 Red Alert:      GPA gap > 0.5 between groups

Frequency: Weekly check (Monday morning)
Recipients: Equity officer, leadership
```

#### Class Performance
```
🟡 Yellow Alert:   >5 classes with GPA < 2.5
🔴 Red Alert:      >10 classes with GPA < 2.0

Frequency: Weekly check (Monday)
Recipients: Academic deans, department heads
```

#### Pass Rate Issues
```
🟡 Yellow Alert:   >5% classes below 80% pass rate
🔴 Red Alert:      >10% classes below 70% pass rate

Frequency: Weekly check
Recipients: Academic team
```

---

## Part 5: Email Template Examples

### Template 1: Student Alert Email

```
Subject: 🚨 URGENT: Increased At-Risk Student Count

From: Metabase Analytics <metabase@yourdomain.com>
To: counselor@yourdomain.com

---

Alert: Chronic Absenteeism Risk Count

Current Status: 🔴 CRITICAL
At-Risk Students: 1,250 (36.8% of 3,400)

This exceeds the threshold of 1,190 (35%).

Top 5 At-Risk Students by Risk Score:
[Table from query results]

IMMEDIATE ACTION RECOMMENDED:
1. Review attached dashboard for patterns
2. Identify intervention priorities
3. Schedule support meetings

Dashboard: https://metabase.yourdomain.com/dashboard/2

Questions? Contact: data-team@yourdomain.com

---

Sent automatically at 8:00 AM daily
Next check: Tomorrow at 8:00 AM
```

### Template 2: Weekly Leadership Report

```
Subject: 📊 Weekly Analytics Report - Week of Jan 27

From: Metabase Analytics <metabase@yourdomain.com>
To: leadership@yourdomain.com

---

WEEKLY SUMMARY (Jan 27 - Feb 2)

✅ Positive Trends:
  • 5 classes improved GPA this week
  • Attendance up 2% from last week
  • Equity gap narrowed in 2 demographics

⚠️ Areas of Concern:
  • 12 students entered "Critical" risk level
  • 3 classes below 2.0 GPA threshold
  • One demographic showing widening disparity

📊 Key Metrics:
  • Total Students Monitored: 3,400
  • At-Risk Students: 1,180 (34.7%)
  • Classes Below 2.5 GPA: 18 (6%)
  • Equity Disparity Range: 0.3-0.8

Detailed Dashboard: https://metabase.yourdomain.com/dashboard/2

---

This report is sent automatically every Friday at 4:00 PM.
```

---

## Part 6: Test Alerts & Reports

### Test Checklist

- [ ] SMTP configuration tested (test email sent)
- [ ] Email received successfully
- [ ] Alert rule created and saved
- [ ] Scheduled report configured
- [ ] Email recipients verified
- [ ] Time zones correct (UTC vs local)
- [ ] Email templates look correct
- [ ] Links in emails work properly
- [ ] Attachments include full dashboard
- [ ] Test message received by all recipients

### Troubleshooting

**Issue**: Email not sending

**Solutions**:
```
1. Check SMTP credentials in Admin Settings
2. Verify email account allows SMTP access
3. Check firewall allows port 587/465
4. Look at Metabase logs: docker logs oss-metabase
5. Verify recipient email addresses are valid
```

**Issue**: Alert triggers too frequently

**Solution**: Increase threshold or check frequency
```sql
-- Check current alert triggers
-- Review query to ensure it matches intent
-- Adjust numbers in threshold
```

**Issue**: Email shows incorrect times

**Solution**: Set timezone in Admin Settings
```
Settings → Localization → Time zone
Set to: America/Los_Angeles (or your timezone)
```

---

## Part 7: Monitor Alert Performance

### Check Alert Logs

```bash
# View Metabase logs
docker logs -f oss-metabase

# Search for alert-related messages
docker logs oss-metabase | grep -i "alert\|email"

# Check email queue
# (In Metabase Admin → Emails)
```

### Email Delivery Report

Access in Metabase: **Admin Settings → Emails → Email Log**

Shows:
- Email address sent to
- Subject line
- Sent timestamp
- Delivery status (success/failure)
- Error messages if failed

---

## Part 8: Advanced Configuration

### Custom Email Template Variables

Available variables in email templates:
- `${DASHBOARD_NAME}` - Dashboard name
- `${TIMESTAMP}` - When email was sent
- `${RECIPIENTS}` - Email recipients
- `${QUERY_RESULTS}` - Question/alert results
- `${ALERT_CONDITION}` - What triggered alert

### Conditional Escalation

Create escalation rules (requires API):

```bash
# If at-risk > 50%, escalate to superintendent
ALERT_THRESHOLD_CRITICAL=1700  # 50% of 3,400

# If at-risk > 35%, alert academic team
ALERT_THRESHOLD_HIGH=1190
```

### Integration with Other Systems

Can integrate with:
- **Slack**: Forward alerts to #student-services channel
- **Teams**: Post to Teams channel
- **Google Workspace**: Send to Google Groups
- **Canvas/Schoology**: API integration for automated interventions

---

## Part 9: Best Practices

### ✅ Do's

- ✅ Test alerts before production
- ✅ Set realistic thresholds (avoid alert fatigue)
- ✅ Review alerts monthly for relevance
- ✅ Archive old/outdated alerts
- ✅ Use meaningful subject lines
- ✅ Include actionable information
- ✅ Set recipient access levels appropriately

### ❌ Don'ts

- ❌ Over-alerting (leads to fatigue)
- ❌ Sending sensitive data in email subjects
- ❌ Excessive attachment sizes (keep <10MB)
- ❌ Alerting non-critical metrics
- ❌ Forgetting to test new alerts
- ❌ Ignoring bounced emails

---

## Part 10: Success Metrics

### Track Effectiveness

```
Metric: Alert Response Time
Target: <2 hours from alert sent to action taken
Track: Via ticket system or action log

Metric: False Alert Rate
Target: <10% of alerts (high signal-to-noise ratio)
Track: Monthly alert audit

Metric: Intervention Success Rate
Target: >70% of alerted students show improvement
Track: Monitor GPA/attendance after intervention

Metric: Stakeholder Satisfaction
Target: >4/5 rating on usefulness of alerts
Track: Quarterly survey
```

---

## Deployment Checklist

### Phase 1: Setup (Day 1)
- [ ] Configure SMTP in Admin Settings
- [ ] Send test email
- [ ] Verify email delivery

### Phase 2: Testing (Day 2-3)
- [ ] Create test alert rules
- [ ] Verify alerts trigger correctly
- [ ] Test scheduled reports
- [ ] Verify recipient emails receive messages

### Phase 3: Production (Week 1)
- [ ] Create all alert rules from Part 2
- [ ] Set up scheduled reports from Part 3
- [ ] Notify stakeholders of alerts
- [ ] Monitor for issues

### Phase 4: Optimization (Week 2+)
- [ ] Review alert frequency
- [ ] Adjust thresholds based on feedback
- [ ] Archive ineffective alerts
- [ ] Train staff on interpreting alerts

---

## Summary Table

| Component | Status | Effort | Value |
|-----------|--------|--------|-------|
| SMTP Setup | 📋 Ready | 10 min | High |
| Alert Rules | 📋 Ready | 15 min | Very High |
| Scheduled Reports | 📋 Ready | 10 min | High |
| Testing | 📋 Ready | 10 min | Critical |
| **Total** | **📋 Ready** | **45 min** | **Excellent** |

---

## Support & Resources

### Configuration Help
- Metabase Email Settings: Admin → Settings → Email
- Metabase Alerts: Admin → Settings → Alerts
- Alert Documentation: https://www.metabase.com/docs/latest/admin-guide/alerts

### Troubleshooting
- Check Metabase logs: `docker logs oss-metabase`
- Verify SMTP credentials
- Test with curl: `curl -s http://localhost:3000/api/email`
- Contact IT for SMTP firewall issues

### Next Steps

1. ✅ Configure SMTP email
2. ✅ Create alert rules (Part 2)
3. ✅ Set up scheduled reports (Part 3)
4. ✅ Test all alerts and reports
5. ✅ Deploy to production
6. ✅ Train stakeholders on using alerts

---

**Status**: ✅ Configuration Guide Complete - Ready for Implementation

*Follow the steps above to enable automated email alerts and scheduled reports for proactive student support.*
