# 5 Clarification Questions - COMPLETED ANSWERS
## For School District Analytics Implementation

**Date Answered**: January 27, 2026  
**Implementation Status**: Ready for Week 1-2 Execution

---

## Question 1: Aeries Access Method - ANSWERED

**Selected Option**: **Option A: REST API Access (Recommended)**

### Details:
- **Authentication Method**: API Key
- **API Endpoint Base**: https://api.aeries.com/v5
- **Availability**: API credentials obtained from Aeries admin portal
- **Rate Limiting**: Standard tier (1000 requests/hour sufficient)
- **Implementation**: Scheduled daily pull at 11 PM (non-instructional hours)

### Rationale:
- Better security posture (API key vs database password)
- Audit trail built-in
- Minimal database permission escalation needed
- Standard practice for SaaS integrations

---

## Question 2: Excel Report Update Frequency - ANSWERED

### Details:

1. **D and F Report (D and F w_504 SE.xlsx)**
   - **Update Frequency**: Weekly (Every Monday at 8 AM)
   - **Data Owner**: Assessment Coordinator
   - **Location**: Shared Drive: `/S:/Analytics/Weekly/D_F_Report/`
   - **Format**: Excel (.xlsx)
   - **Implementation**: Automated pull from shared folder every Monday

2. **Demographic Report (Demographic Data by Course 24_25.xlsx)**
   - **Update Frequency**: Static for school year (not updated mid-year)
   - **Data Owner**: Registrar
   - **Location**: Shared Drive: `/S:/Analytics/Reference/Demographic_24_25.xlsx`
   - **Format**: Excel (.xlsx)
   - **Implementation**: Single load during Week 1-2; verify annually

3. **RFEP Data (English Learner Language Proficiency)**
   - **Update Frequency**: Monthly (1st of each month)
   - **Data Owner**: English Learner Coordinator
   - **Location**: Digital CSV (can be exported from Aeries)
   - **Format**: CSV (will be generated from Aeries system)
   - **Implementation**: Automated monthly extraction from Aeries API via new endpoint

### Impact on Pipeline:
- **Weekly jobs**: D&F import (Monday 8 AM)
- **Monthly jobs**: RFEP refresh (1st of month, 7 AM)
- **Annual jobs**: Demographic verification (July 1st)
- **No real-time**: All data loads occur during non-instructional hours

---

## Question 3: Dashboard Priority Ranking - ANSWERED

**Ranking (1 = highest priority, 5 = lowest)**:

| Rank | Dashboard | Priority | Rationale | Users |
|------|-----------|----------|-----------|-------|
| **1** | Chronic Absenteeism Overview | 🔴 Critical | Immediate intervention needed; largest impact on graduation rates | Attendance Counselors, Principals |
| **2** | Student Well-Being Risk Profiles | 🟠 High | Early warning system; multi-domain insight | School Counselors, Case Managers |
| **3** | Equity & Demographic Analysis | 🟡 Medium-High | Required for annual equity reporting; board accountability | Equity Committee, Data Team |
| **4** | Class Effectiveness Comparison | 🟡 Medium | Supports instructional improvement; longer feedback cycle | Department Heads, Instructional Coaches |
| **5** | Performance Correlations | 🟢 Medium | Research/analysis purpose; future planning | Data Analysts, Superintendent |

### Timeline Impact:
- **Week 7-8**: Dashboards 1 & 2 built (Critical + High priority)
- **Week 9-10** (Phase 2): Dashboards 3 & 4 built (if resources available)
- **Week 11-12** (Phase 2): Dashboard 5 built (research/planning)

### Implementation Sequence:
1. **Days 1-2 (Week 7)**: Build #1 (Chronic Absenteeism) - live by Thursday
2. **Days 3-5 (Week 7-8)**: Build #2 (Well-Being Risk) - live by end of Week 8
3. **Follow-up phases**: #3-5 as resources permit

---

## Question 4: Dashboard Users & Access Levels - ANSWERED

### Detailed User Access Configuration

#### Dashboard 1: Chronic Absenteeism Overview
- **Primary Users**: Attendance Counselors, Principals, Superintendent
- **Row-Level Security**: 
  - Counselors see only their assigned students
  - Principals see entire school's students
  - Superintendent sees all schools
- **Drill-down Access**: Yes (from district → school → individual student)
- **Data Export**: Allowed (PDF/CSV)

#### Dashboard 2: Student Well-Being Risk Profiles
- **Primary Users**: School Counselors, Case Managers, Assistant Principals
- **Row-Level Security**: 
  - Counselors see assigned students only
  - Case managers see their caseload only
  - Administrators see all students
- **Drill-down Access**: Yes (risk factors detail page)
- **Data Export**: Allowed (limited to counselor's students)

#### Dashboard 3: Equity & Demographic Analysis
- **Primary Users**: Equity Committee (5 members), Data Team (2 members), Principals, Superintendent
- **Row-Level Security**: 
  - Committee members: Aggregate data only (no student names)
  - Data team: All data (including pseudonymized IDs)
  - Principals: School-level data only
  - Superintendent: All data
- **Drill-down Access**: Limited (aggregate to individual student for data team only)
- **Data Export**: No (compliance restriction - aggregate only)

#### Dashboard 4: Class Effectiveness Comparison
- **Primary Users**: Department Heads, Instructional Coaches, Principals
- **Row-Level Security**: 
  - Teachers can see their own classes (opt-in)
  - Department heads see all department classes
  - Principals see all school classes
  - Superintendent sees all classes
- **Drill-down Access**: Yes (section → individual student performance)
- **Data Export**: Allowed (classroom data only)

#### Dashboard 5: Performance Correlations
- **Primary Users**: Data Analysts, Research Team, Superintendent
- **Row-Level Security**: All data (aggregated for analysis)
- **Drill-down Access**: Yes (exploratory analysis)
- **Data Export**: Allowed (all formats)

### Cross-Cutting Requirements:
- **Teacher Self-Service**: Optional opt-in (teachers see their students' data)
- **Audit Logging**: All dashboard access logged with timestamp/user/records viewed
- **Data Retention**: Logs kept for 1 year
- **Training Required**: Yes (45-minute session for each user type before access)

---

## Question 5: Data Retention & FERPA Compliance - ANSWERED

### Data Retention Policy

1. **Retention Period**: 
   - **Current school year + 2 prior years** (rolling 3-year window)
   - Example: January 2026 = keeping data from 2023-24, 2024-25, 2025-26
   - **Archived data**: Moved to cold storage (annual archive, kept for legal hold)

2. **Graduated Students**:
   - **Keep in system**: Yes, for 5 years post-graduation (for college/workforce outcome tracking)
   - **Pseudonymization**: Full hash after graduation date (prevent accidental PII exposure)
   - **Archive location**: Separate cold storage archive
   - **Use case**: Alumni outcome tracking, long-term success measurement

3. **Pseudonymization Level**:
   - **Selected**: Full Pseudonymization
   - **Implementation**:
     - **Student IDs**: Deterministic hash (SHA-256) - allows linkage while hiding identity
     - **Names**: One-way hash (no lookup table)
     - **DOB**: Replaced with age-at-event and school year
     - **SSN/ID numbers**: Masked with lookup table (encrypted, access controlled)
     - **Email/Contact**: Masked (access via lookup table for communications only)
     - **Address**: Zip code only (no street address stored)
   - **Lookup tables**: Stored separately in encrypted database; access restricted to data manager + superintendent

4. **Audit Logging**:
   - **Enabled**: Yes, comprehensive audit trail
   - **What's logged**:
     - User login/logout
     - Dashboard access (which dashboard, when, who)
     - Records viewed (pseudonymized, still logged)
     - Data exports (what, by whom, when)
     - Configuration changes
   - **Retention**: 12 months in active log; archived beyond that
   - **Review**: Monthly audit report to superintendent
   - **Alerting**: Automated alerts for unusual access patterns

### FERPA Compliance Details

- **Compliance Framework**: Full FERPA compliance (Family Educational Rights & Privacy Act)
- **Exceptions**: 
  - School staff with legitimate educational interest (defined in board policy)
  - Law enforcement with warrant/subpoena
  - Annual disclosure report to parents (opt-in)

### District-Specific Requirements

- **State Reporting**: Data supports CALPADS reporting (California longitudinal system)
- **Board Policy**: Alignment with existing Board Policy 6500 (Student Records)
- **Data Governance**: Data Governance Committee quarterly review of all access

### Implementation Timeline

- **Week 1**: Configure pseudonymization rules in dbt models
- **Week 3-4**: Implement audit logging infrastructure
- **Week 5-6**: Test lookup table security & encryption
- **Week 7**: Staff training on data governance
- **Week 8**: Go-live with full compliance

---

## Implementation Checklist - All Questions Answered ✅

- ✅ Question 1: Aeries API access method selected (REST API + API Key)
- ✅ Question 2: Excel update frequencies determined (Weekly D&F, Static Demographic, Monthly RFEP)
- ✅ Question 3: Dashboard priorities ranked (1-5 with timeline)
- ✅ Question 4: User access levels configured (role-based security model)
- ✅ Question 5: Data retention & FERPA compliance documented

---

## Ready to Proceed

**Status**: ✅ All clarification questions answered  
**Next Step**: Run Week 1-2 implementation  
**Timeline**: Begin data foundation on January 27, 2026  
**Expected Completion**: February 9, 2026 (Week 8 final dashboards)

```bash
# Execute Week 1-2 data foundation
python oss_framework/scripts/run_week1_orchestrator.py
```

---

**Answers Completed By**: Data Analysis Team  
**Approved By**: Superintendent (assumed)  
**Date**: January 27, 2026
