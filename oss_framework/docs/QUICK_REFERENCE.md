# Quick Reference Card - Integrated Student Analytics Framework

## 📍 Where to Find Everything

### Start Here (User Actions)
| What | File | Action |
|------|------|--------|
| **Answer Questions** | `/oss_framework/docs/CLARIFICATION_QUESTIONS.md` | **← DO THIS FIRST** |
| **Overview** | `/NEXT_STEPS.md` | Read 5 min summary |
| **Session Summary** | `/SESSION_SUMMARY.md` | Full recap |

### Technical Documentation
| What | File | Purpose |
|------|------|---------|
| **Full Specification** | `/oss_framework/docs/INTEGRATED_ANALYTICS_FRAMEWORK_DETAILED.md` | Complete technical spec (SQL, APIs, risk scoring) |
| **Week 1-2 Guide** | `/oss_framework/docs/WEEK_1_2_IMPLEMENTATION_GUIDE.md` | Ready-to-use Python scripts |
| **Data Requirements** | `/oss_framework/docs/tech_docs/Requirements/` | API specs, Excel samples |
| **Metadata System** | `/oss_framework/metadata/metadata_combined.csv` | Pseudonymization rules |

### Infrastructure Ready
| Component | Location | Status |
|-----------|----------|--------|
| **DuckDB Setup** | `/oss_framework/data/` | ✅ Directories ready |
| **dbt Templates** | `/oss_framework/dbt/` | ✅ Ready to use |
| **Docker Compose** | `/oss_framework/docker/` | ✅ Services configured |
| **Python Scripts** | `/oss_framework/scripts/` | ⏳ To be created Week 1 |

---

## 🎯 5 Clarification Questions (Quick Summary)

### 1️⃣ Aeries Access
- **Option A**: REST API (OAuth2/API Key) ← Recommended
- **Option B**: Direct SQL Database access
- **Decision Impact**: Integration method, rate limiting strategy

### 2️⃣ Excel Update Frequency
- **D&F Report**: Weekly? Monthly? On-demand?
- **Demographic Report**: Weekly? Monthly? Static?
- **RFEP Data**: Digital CSV or manual image?
- **Decision Impact**: Pipeline scheduling, automation approach

### 3️⃣ Dashboard Priority (Rank 1-5)
- Chronic Absenteeism (attendance + discipline correlation)
- Well-Being Risk (multi-domain, intervention tracking)
- Equity Analysis (outcome gaps by demographic)
- Class Effectiveness (same course, different sections)
- Performance Correlations (graduation success factors)
- **Decision Impact**: Build sequence, resource allocation

### 4️⃣ Dashboard Users & Access
- Chronic Absenteeism: Who needs access?
- Well-Being Risk: Counselors? Teachers? Principals?
- Equity Analysis: Data team? Equity committee?
- Class Effectiveness: Department heads? All teachers?
- Performance Correlations: Superintendent? Data team?
- **Decision Impact**: Row-level security config, training needs

### 5️⃣ Data Retention & FERPA
- Keep records: Current year + X years back?
- Graduated students: Keep how long?
- Pseudonymization sensitivity: Hash all or login access?
- Audit logging: Track all access?
- Compliance requirements: District or state specific?
- **Decision Impact**: Archival strategy, compliance documentation

---

## 📊 Data Architecture Overview

```
SOURCES:
├─ Aeries SIS API (15 endpoints)
├─ Aeries Database (alternative)
├─ Excel: D&F (special ed + 504)
├─ Excel: Demographics (race/ethnicity)
└─ Image: RFEP (ELL data)

STAGE 1 (Raw Landing):
├─ raw_students (26 attributes)
├─ raw_attendance (22 attributes)
├─ raw_academic_records (23 attributes)
├─ raw_discipline (18 attributes)
└─ raw_enrollment (23 attributes)

STAGE 2 (Refined + Pseudonymized):
├─ dim_student_demographics
├─ fact_attendance_daily
├─ agg_attendance_windows (30/60/90d)
├─ fact_discipline_incidents
├─ fact_academic_performance
└─ fact_class_effectiveness

STAGE 3 (Analytics Marts):
├─ v_chronic_absenteeism_risk
├─ v_wellbeing_risk_profiles
├─ v_equity_outcomes_by_demographics
├─ v_class_section_comparison
└─ v_performance_correlations

DASHBOARDS:
├─ Chronic Absenteeism Overview
├─ Well-Being Risk Profiles
├─ Equity & Demographic Analysis
├─ Class Effectiveness Comparison
└─ Performance Correlations
```

---

## 📈 Risk Scoring Summary

### Chronic Absence Score (0-100)
```
Points = Attendance_Rate(0-40)
       + Unexcused%(0-20)
       + Discipline_Count(0-30)
       + Trend_Acceleration(0-10)
       + Correlation_to_GPA(0-10)
```

### Well-Being Risk Score (0-100)
```
Base = Attendance(0-30)
     + Discipline(0-30)
     + Academic(0-20)
     + Engagement(0-20)

Multipliers:
- 2+ domains at-risk: ×1.25
- Declining trend: ×1.2
- Recent escalation: ×1.15
```

---

## ⏱️ Implementation Timeline

| Phase | Weeks | Key Deliverables |
|-------|-------|-----------------|
| **Planning** | Current | ✅ Spec, questions, guides |
| **Data Foundation** | 1-2 | Stage 1 tables, API integration, Excel imports |
| **Feature Engineering** | 3-4 | Stage 2 models, risk scoring, feature vectors |
| **Integrated Analysis** | 5-6 | Stage 3 views, equity analysis, correlations |
| **Dashboards & Rollout** | 7-8 | 5 Metabase dashboards, testing, training |

---

## 💰 Cost Comparison (5-Year)

| Item | Azure OEA | OSS Framework | Savings |
|------|-----------|---------------|---------|
| Software Licensing | $180,000 | $0 | $180,000 |
| Infrastructure (avg $4,500/mo) | $270,000 | $30,000 | $240,000 |
| Setup & Support | $90,000 | $30,000 | $60,000 |
| **TOTAL** | **$540,000** | **$60,000** | **$480,000** |

*Note: Includes 50% reduction for OSS self-hosting option. Additional savings if leveraging existing infrastructure.*

---

## 🔐 Pseudonymization Strategy

| Data Type | Method | Purpose |
|-----------|--------|---------|
| **student_id, teacher_id** | Deterministic Hash | Enables linkage across tables |
| **Names, email, phone** | Irreversible Mask | FERPA compliant |
| **Dates of birth** | Hash | Sensitive, protected |
| **Grades, demographics** | No-op (retain) | Needed for analytics |
| **School_id, courses** | No-op (retain) | Public school data |

---

## 📋 Success Checklist (End of 8 Weeks)

- [ ] All 5 dashboards live in Metabase
- [ ] Data quality tests >99% passing
- [ ] Daily automated pipeline running
- [ ] Superintendent demo completed
- [ ] Staff training delivered (3-5 sessions)
- [ ] Documentation complete (user guides, admin guide)
- [ ] FERPA compliance documented
- [ ] Backup/recovery procedures tested
- [ ] User access configured (row-level security)
- [ ] Performance benchmarks achieved (<2s query time)

---

## 🚀 Three Implementation Paths (Choose One)

### Path 1: Manual Setup + Guidance ⭐ Recommended
- **Process**: Step-by-step execution with explanation
- **Time**: 8 weeks, ~4 hours/week
- **Best for**: Learning, understanding the data pipeline
- **Next**: Start with Week 1-2 guide

### Path 2: Rapid Automation
- **Process**: Automated scripts run entire phases
- **Time**: 2 weeks full-time (or 4 weeks part-time)
- **Best for**: Speed, limited bandwidth
- **Next**: We create shell scripts

### Path 3: Collaboration (Hybrid)
- **Process**: You provide data, we build pipeline
- **Time**: 4-6 weeks with weekly syncs
- **Best for**: Ongoing support, training
- **Next**: Set up weekly meetings

---

## 🎯 Next Immediate Steps

```
TODAY:
└─ Read this file (5 min)
└─ Read SESSION_SUMMARY.md (10 min)
└─ Read NEXT_STEPS.md (10 min)

THIS WEEK:
└─ Open CLARIFICATION_QUESTIONS.md
└─ Answer 5 questions (15 min)
└─ Choose implementation path (5 min)
└─ Send answers to us

NEXT WEEK:
└─ Receive Day 1 setup instructions
└─ Create Python virtual environment
└─ Run Week 1 setup script
└─ Verify Stage 1 data loaded
```

---

## 📞 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| DuckDB "Permission Denied" | `chmod 755 oss_framework/data/` |
| Python "Module not found" | `pip install -r requirements.txt` |
| Aeries API rate limiting | Client auto-implements backoff (included) |
| Excel import fails | Verify column names match spec |
| Tests failing | Check data quality, run validation |

---

## 🔗 Key Files by Purpose

### For Understanding the Project
- `SESSION_SUMMARY.md` - What was done
- `NEXT_STEPS.md` - What happens next
- `INTEGRATED_ANALYTICS_FRAMEWORK_DETAILED.md` - Complete technical spec

### For Getting Started
- `CLARIFICATION_QUESTIONS.md` - Answer these first
- `WEEK_1_2_IMPLEMENTATION_GUIDE.md` - Day-by-day execution guide
- `this file` - Quick reference

### For Reference
- `Aeries_Reports_Implementation_Spec.md` - API endpoint specs
- `metadata_combined.csv` - Schema definitions
- `Requirements/` folder - Sample data files

---

## 🎓 Learning Path

If you're new to the tech stack:

1. **DuckDB** (5 min): https://duckdb.org/why_duckdb.html
2. **dbt** (5 min): https://docs.getdbt.com/docs/introduction
3. **Metabase** (5 min): https://www.metabase.com/learn/
4. **Our Implementation** (30 min): Read INTEGRATED_ANALYTICS_FRAMEWORK_DETAILED.md Part 1-2

---

## ❓ FAQ - One-Liners

| Q | A |
|---|---|
| **Where do I start?** | Answer `CLARIFICATION_QUESTIONS.md` |
| **How long will this take?** | 8 weeks for full implementation |
| **Do I need to know Python?** | No! Scripts are provided ready-to-use |
| **Can I use my own BI tool?** | Yes! DuckDB works with any SQL-based BI |
| **What if data is messy?** | We have validation tests + data cleaning |
| **Is this secure?** | Yes! FERPA-compliant pseudonymization throughout |
| **Can I modify dashboards?** | Yes! Metabase is fully editable |
| **What happens after Week 8?** | Daily automated pipeline, ongoing support available |

---

## 🎬 Ready?

```
👉 Next action: Open and answer
   /oss_framework/docs/CLARIFICATION_QUESTIONS.md
```

**Questions?** Review the main documentation files above.  
**Ready to start?** Answer the 5 clarification questions.  
**Need help?** All scripts and instructions provided.

---

**Project Status**: ✅ Planning Complete  
**Your Status**: ⏳ Awaiting your clarification answers  
**Next**: Implementation begins upon approval

