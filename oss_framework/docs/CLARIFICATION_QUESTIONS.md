# 5 Critical Clarification Questions
## Before Week 1 Implementation Begins

**Status**: Ready to answer clarification questions before starting Week 1-2 data foundation work.

**Timeline Impact**: These answers will determine exact implementation approach for Weeks 1-8.

---

## Question 1: Aeries Access Method

**Context**: The Aeries API requires authentication. We have two implementation paths:

### Option A: REST API Access (Recommended for security)
- Use Aeries API endpoints (OAuth2 or API key)
- Query `/api/v5/reports/*` endpoints
- Real-time data pull every hour/day
- **Requires**: API credentials (Client ID + Secret OR API Key)
- **Pros**: Minimal database access rights, audit trail
- **Cons**: Rate limiting (typically 1000 req/hr), API call costs if applicable

### Option B: Direct Database Access
- Connect directly to Aeries SQL Server database
- Full control over query timing and complexity
- **Requires**: SQL Server credentials, network access to Aeries database
- **Pros**: Unlimited queries, better for bulk ETL
- **Cons**: Requires elevated database permissions, higher security risk

### **What we need from you**:
1. Do you have Aeries API credentials available? (Client ID/Secret or API Key?)
2. If not, do you have SQL Server database access to the Aeries database?
3. Which option is preferred by your IT department?

---

## Question 2: Excel Report Update Frequency

**Context**: We have 3 Excel reports that need to be imported:
- `D and F w_504 SE.xlsx` (D/F grades + 504 status + Special Education flags)
- `Demographic Data by Course 24_25.xlsx` (Race/ethnicity by section)
- `RFEP.png` (English learner language proficiency data)

### **What we need from you**:
1. **D&F Report**: How often is this updated? (Weekly? Monthly? End of grading period?)
2. **Demographic Report**: How often is this updated? (Static for year? Updated as students transfer?)
3. **RFEP Data**: Is this digital data (CSV/Excel) or manual/image data? How often updated?

**Implementation Impact**:
- **If weekly**: We'll set up automated pipelines to pull files from shared folder/OneDrive
- **If monthly**: We can use manual upload or scheduled pull from archive
- **If manual**: We'll create a simple dashboard for staff to upload latest versions

---

## Question 3: Priority Analytics (Which matters most?)

**Context**: We have 5 dashboards planned. Resources may require sequencing.

### Dashboard Priority Ranking (1 = highest):

**Dashboard 1: Chronic Absenteeism Overview**
- KPIs: Attendance rates, chronic absence flags, trend lines
- Users: Attendance counselors, administrators
- **Priority**: ___

**Dashboard 2: Student Well-Being Risk Profiles**
- KPIs: Multi-domain risk (attendance + discipline + academics)
- Users: School counselors, case managers
- **Priority**: ___

**Dashboard 3: Equity & Demographic Analysis**
- KPIs: Outcome gaps by race, ELL, SPED, SES, housing
- Users: Equity committee, data team
- **Priority**: ___

**Dashboard 4: Class Effectiveness Comparison**
- KPIs: Same course, different sections - which teacher/section performs better?
- Users: Department heads, instructional coaches
- **Priority**: ___

**Dashboard 5: Performance Correlations**
- KPIs: What factors predict graduation? (Attendance-GPA, discipline-grades, etc.)
- Users: Data analysts, superintendent
- **Priority**: ___

### **What we need from you**:
Rank these 1-5 (1 = do first, 5 = do last). This will determine which dashboards we complete in Week 7-8 first.

---

## Question 4: Dashboard Users & Access Levels

**Context**: Different users need different data visibility (teachers see their class, counselors see assigned students, etc.)

### **What we need from you**:

1. **Chronic Absenteeism Dashboard**:
   - Who needs access? (All staff? Attendance counselors only? Administrators?)
   - Should teachers see only their own students' attendance?

2. **Well-Being Risk Dashboard**:
   - Who needs access? (Counselors? Teachers? Principals?)
   - Should data be visible by assigned caseload?

3. **Equity Analysis Dashboard**:
   - Who needs access? (Data team? Equity committee? All administrators?)
   - Should this be aggregated (no individual student names) or detailed?

4. **Class Effectiveness Dashboard**:
   - Who needs access? (Department heads? All teachers? Principals?)
   - Should teachers see only their own sections or all sections?

5. **Performance Correlations Dashboard**:
   - Who needs access? (Superintendent? Data team? Instructional leaders?)
   - Is this for data exploration or board presentation?

**Implementation Impact**:
- We'll configure Metabase row-level security (RLS) based on user roles
- Test data filter sets for each role

---

## Question 5: Data Retention & FERPA Compliance

**Context**: FERPA (Family Educational Rights and Privacy Act) requires specific data handling:
- How long to retain personally identifiable information (PII)?
- When to archive/delete historical student records?
- Any state-specific retention requirements?

### **What we need from you**:

1. **Student Data Retention**: 
   - How many years should we keep records? (Current year + X years back?)
   - Example: Keep 5 years of student data, then archive to cold storage?

2. **Graduated Students**:
   - Should we keep analytics for students who have graduated/transferred out?
   - How long? (1 year? 3 years? Indefinitely for historical analysis?)

3. **Pseudonymization Sensitivity**:
   - Should we hash student IDs in all dashboards, or is login (identified) access acceptable?
   - Should admin reports show student names or only hashed IDs?

4. **Audit Trail Requirements**:
   - Do you need to track who accessed which student data and when?
   - Should we implement detailed logging for compliance audits?

5. **District/State Requirements**:
   - Are there specific data retention policies you must follow? (District policy? State requirements?)
   - Should we document the pseudonymization strategy for compliance review?

**Implementation Impact**:
- We'll configure dbt to mark records with `_deleted_at` for soft deletes (reversible)
- Create archive tables for historical data
- Document all pseudonymization rules for FERPA compliance
- Set up audit logging in Dagster

---

## Answer Template

Please provide answers in this format:

```
## Question 1: Aeries Access Method
Option chosen: [A / B]
Details: [Your API credentials status or DB access]
IT preference: [API / Database]

## Question 2: Excel Report Update Frequency
D&F Report: [Weekly / Monthly / On-demand]
Demographic Report: [Weekly / Monthly / Static]
RFEP Data: [Digital CSV / Manual image / Other]

## Question 3: Dashboard Priority
1. [Dashboard name] - Priority: ___
2. [Dashboard name] - Priority: ___
... etc

## Question 4: Dashboard Users & Access
[Your answer for each dashboard]

## Question 5: Data Retention & FERPA
[Your answer for each requirement]
```

---

## Next Steps After Clarification

Once we receive answers to these 5 questions, we will:

1. ✅ **Confirm implementation approach** for Aeries integration
2. ✅ **Set up automated pipelines** based on Excel update frequency
3. ✅ **Prioritize dashboard development** based on your ranking
4. ✅ **Configure user access/security** based on dashboard users
5. ✅ **Document data retention policy** and FERPA compliance strategy

Then we'll proceed directly to **Week 1 implementation** with no further blockers.

---

## Estimated Timeline After Clarification

| Week | Phase | Deliverable |
|------|-------|-------------|
| **1-2** | Data Foundation | ✅ Stage 1 tables, Aeries API integration, Excel imports |
| **3-4** | Feature Engineering | ✅ Stage 2 models, attendance windows, risk scoring |
| **5-6** | Integrated Analysis | ✅ Stage 3 views, equity analysis, correlations |
| **7-8** | Dashboards & Testing | ✅ 5 Metabase dashboards, user testing, superintendent demo |
| **After** | Support & Optimization | Ongoing monitoring, refinement, training |

---

**Ready to answer?** Please provide your responses and we'll kick off Week 1 immediately.
