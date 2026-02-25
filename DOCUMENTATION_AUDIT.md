# Documentation Audit - OEA vs OSS Content

**Audit Date**: 2026-01-28  
**Auditor**: Automated documentation analysis  
**Purpose**: Separate OSS Framework from OEA framework content  

## Summary Statistics

- **Total Files**: 100 markdown files
- **Pure OEA (Remove)**: ~50 files (schemas/, packages/, framework/, root README)
- **Pure OSS (Keep)**: ~25 files (oss_framework/)
- **Mixed/Review**: ~10 files (root CONTRIBUTING, SECURITY, etc.)
- **Temporary/Session**: ~15 files (session summaries, status reports)

## Category 1: Pure OEA Content - TO REMOVE

### Root Documentation (Microsoft OEA Framework)
| File | Reason | Action |
|------|--------|--------|
| `README.md` | Microsoft OEA framework intro, Azure setup | **REMOVE** |
| `CONTRIBUTING.md` | Microsoft contribution guidelines | **REPLACE** with OSS version |
| `SECURITY.md` | Microsoft security policy | **REPLACE** with OSS version |
| `CODE_OF_CONDUCT.md` | Microsoft code of conduct | **REPLACE** with OSS version |

### Schemas Directory (OEA Schemas)
**Path**: `schemas/`  
**Content**: OEA schema catalog for Azure data lake integration  
**Action**: **REMOVE ENTIRE DIRECTORY**

Files include:
- `schemas/README.md` - OEA schema architecture
- `schemas/schema_catalog/Student_Portrait_Schema/` - OEA schemas
- `schemas/schema_catalog/Microsoft_Education_Insights/` - Microsoft product
- `schemas/schema_catalog/Learning_Analytics/` - OEA analytics
- `schemas/schema_catalog/Digital_Engagement_Schema/` - OEA engagement
- `schemas/schema_catalog/Ed-Fi/` - Ed-Fi integration
- `schemas/schema_catalog/Attendance_Schema/` - OEA attendance
- `schemas/schema_creation_kit/` - OEA schema tools

### Packages Directory (OEA Packages)
**Path**: `packages/`  
**Content**: OEA pre-built analytics packages (Chronic Absenteeism, Wellbeing, etc.)  
**Action**: **REMOVE ENTIRE DIRECTORY**

Files include:
- `packages/README.md` - OEA package architecture
- `packages/package_catalog/Predicting_Student_Well_Being/` - Azure ML package
- `packages/package_catalog/Predicting_Chronic_Absenteeism/` - Azure ML package
- `packages/package_catalog/Learning_Analytics/` - Azure-based learning analytics
- `packages/package_catalog/Hybrid_Engagement/` - OEA hybrid learning package
- `packages/package_creation_kit/` - OEA package development tools

### Framework Directory (OEA Infrastructure)
**Path**: `framework/`  
**Content**: Azure Bicep templates, OEA infrastructure-as-code  
**Action**: **REMOVE ENTIRE DIRECTORY**

Files include:
- `framework/infrastructure/bicep/readme.md` - Azure deployment templates
- `framework/infrastructure/bicep/basic/readme.md` - Basic Azure setup

### Documentation Directory (OEA Docs)
**Path**: `docs/`  
**Content**: OEA framework documentation  
**Action**: **REMOVE ENTIRE DIRECTORY**

Files include:
- `docs/project_intent_and_analysis.md` - OEA framework intent
- `docs/use_cases/README.md` - OEA use cases
- `docs/tech_docs/README.md` - OEA technical docs

---

## Category 2: Pure OSS Content - TO KEEP

### OSS Framework (Student Analytics Platform)
**Path**: `oss_framework/`  
**Content**: New OSS student analytics framework (DuckDB, dbt, Metabase)  
**Action**: **KEEP ALL FILES**

#### Deployment Documentation (KEEP)
- `oss_framework/deployment/metabase/README.md` ✅ OSS Metabase guide
- `oss_framework/deployment/metabase/VERIFICATION-REPORT.md` ✅ Setup verification
- `oss_framework/deployment/metabase/VERIFICATION-COMPLETE.md` ✅ Completion status
- `oss_framework/deployment/metabase/SESSION-SUMMARY.md` ✅ Session notes
- `oss_framework/deployment/metabase/TROUBLESHOOTING.md` ✅ Troubleshooting guide
- `oss_framework/deployment/metabase/SCRIPTS-CONSOLIDATION.md` ✅ Script docs
- `oss_framework/deployment/metabase/SETUP-STATE.md` ✅ Setup tracking
- `oss_framework/deployment/metabase/VERIFICATION-CHECKLIST.md` ✅ Verification steps
- `oss_framework/deployment/metabase/RUN-DASHBOARDS.md` ✅ Dashboard guide
- `oss_framework/deployment/metabase/access-control-guide.md` ✅ Access control
- `oss_framework/deployment/metabase/STAFF_TRAINING_DELIVERY_GUIDE.md` ✅ Training guide
- `oss_framework/deployment/metabase/HTTPS_SETUP_GUIDE.md` ✅ HTTPS setup
- `oss_framework/deployment/metabase/TRAINING_GUIDE.md` ✅ User training

#### Training Materials (KEEP)
- `oss_framework/deployment/metabase/training/board-member-guide.md` ✅ Board training
- `oss_framework/deployment/metabase/training/teacher-guide.md` ✅ Teacher training
- `oss_framework/deployment/metabase/training/counselor-guide.md` ✅ Counselor training
- `oss_framework/deployment/metabase/training/principal-guide.md` ✅ Principal training
- `oss_framework/deployment/metabase/training/admin-guide.md` ✅ Admin training
- `oss_framework/deployment/metabase/training/faq.md` ✅ FAQ
- `oss_framework/deployment/metabase/training/troubleshooting-guide.md` ✅ User troubleshooting
- `oss_framework/deployment/metabase/training/quick-start-guide.md` ✅ Quick start

#### Operational Documentation (KEEP)
- `oss_framework/OPERATIONAL_RUNBOOKS.md` ✅ Ops procedures
- `oss_framework/STAFF_TRAINING.md` ✅ Staff training plan
- `oss_framework/scripts/README.md` ✅ Script documentation
- `oss_framework/monitoring/README.md` ✅ Monitoring guide
- `oss_framework/metadata/README.md` ✅ Metadata docs

---

## Category 3: Temporary/Session Files - TO REMOVE

**Action**: Archive or remove (not needed for production)

### Project Management Files
- `beads_report_openedDataEstate_2026-01-27.md` 🗑️ Beads report
- `session-ses_3fea.md` 🗑️ Session notes
- `FINAL_PROJECT_SUMMARY.md` 🗑️ Project summary
- `DOCUMENTATION_INDEX.md` 🗑️ Old documentation index
- `DASHBOARD_POPULATION_GUIDE.md` 🗑️ Old dashboard guide
- `NEXT_STEPS.md` 🗑️ Old next steps
- `roadmap/roadmap.md` 🗑️ Old roadmap
- `STAGE_4_COMPLETION_SUMMARY.md` 🗑️ Stage summaries
- `PHASE_4_SESSION_2_SUMMARY.md` 🗑️ Phase summaries
- `STAGE_4_SESSION_SUMMARY.md` 🗑️ Session summaries
- `METABASE_SETUP_GUIDE.md` 🗑️ (Replaced by oss_framework version)
- `PHASE_4_WEEK2_SETUP_SUMMARY.md` 🗑️ Week summaries
- `PROJECT_STATUS.md` 🗑️ Old project status
- `PHASE_4_WEEKS_2-8_ROADMAP.md` 🗑️ Old roadmap
- `PHASE_4_WEEK1_SUMMARY.md` 🗑️ Week summary
- `SESSION_SUMMARY.md` 🗑️ Session summary
- `PHASE_4_IMPLEMENTATION_SUMMARY.md` 🗑️ Implementation summary
- `WEEK_5_6_COMPLETE.md` 🗑️ Week completion
- `WEEK_3_4_COMPLETE.md` 🗑️ Week completion
- `WEEK_1_2_COMPLETE.md` 🗑️ Week completion
- `IMPLEMENTATION_READY.md` 🗑️ Implementation status
- `.github/WORKFLOWS.md` 🗑️ GitHub workflows
- `PHASE1_COMPLETION.md` 🗑️ Phase completion

---

## Category 4: Need New OSS Versions

### Root Documentation Files
| File | Status | Action |
|------|--------|--------|
| `README.md` | Pure OEA | **REPLACE** with OSS Framework introduction |
| `CONTRIBUTING.md` | Microsoft template | **REPLACE** with OSS contribution guidelines |
| `SECURITY.md` | Microsoft template | **UPDATE** for OSS context (remove Azure-specific) |
| `CODE_OF_CONDUCT.md` | Microsoft template | **KEEP** (generic, suitable for OSS) |

---

## Recommended Actions

### Phase 1: Backup (Task openedDataEstate-v8h)
```bash
# Create backup branch
git checkout -b backup/pre-oea-pruning-2026-01-28
git push -u origin backup/pre-oea-pruning-2026-01-28

# Tag current state
git tag v-pre-doc-separation
git push origin v-pre-doc-separation
```

### Phase 2: Remove OEA Content (Task openedDataEstate-044)
```bash
# Remove entire directories
rm -rf schemas/
rm -rf packages/
rm -rf framework/
rm -rf docs/

# Remove temporary session files
rm beads_report_openedDataEstate_2026-01-27.md
rm session-ses_3fea.md
rm FINAL_PROJECT_SUMMARY.md
rm DOCUMENTATION_INDEX.md
rm DASHBOARD_POPULATION_GUIDE.md
rm NEXT_STEPS.md
rm -rf roadmap/
rm STAGE_4_*.md
rm PHASE_4_*.md
rm METABASE_SETUP_GUIDE.md
rm PROJECT_STATUS.md
rm SESSION_SUMMARY.md
rm WEEK_*.md
rm IMPLEMENTATION_READY.md
rm .github/WORKFLOWS.md
rm PHASE1_COMPLETION.md
```

### Phase 3: Replace Root README (Task openedDataEstate-3n2)
Create new `README.md` introducing the OSS Student Analytics Framework:
- Architecture overview (DuckDB → dbt → Metabase)
- Quick start guide
- Link to oss_framework/ documentation
- No Microsoft/Azure dependencies

### Phase 4: Update CONTRIBUTING.md (Task openedDataEstate-b4a)
- Remove Microsoft-specific contribution process
- Add OSS-specific contribution guidelines
- GitHub PR process, code review standards
- Testing requirements (dbt, DuckDB, Metabase)

### Phase 5: Update SECURITY.md (Task openedDataEstate-b4a)
- Remove Azure-specific security guidance
- Add OSS-specific security considerations:
  - DuckDB file permissions
  - Metabase authentication
  - Student data pseudonymization
  - FERPA compliance

### Phase 6: Update Internal Links (Task openedDataEstate-4hj)
Find and fix all broken links after removal:
```bash
# Find all markdown links
grep -r "\[.*\](.*)" oss_framework/ --include="*.md"

# Check for links to removed directories
grep -r "schemas/" oss_framework/ --include="*.md"
grep -r "packages/" oss_framework/ --include="*.md"
grep -r "framework/" oss_framework/ --include="*.md"
```

### Phase 7: Create New DOCUMENTATION_INDEX.md (Task openedDataEstate-drn)
Structure:
```markdown
# OSS Student Analytics Framework - Documentation Index

## Getting Started
- README.md - Framework overview
- oss_framework/deployment/metabase/README.md - Metabase setup

## Deployment
- oss_framework/deployment/metabase/SETUP-STATE.md
- oss_framework/deployment/metabase/HTTPS_SETUP_GUIDE.md

## Operations
- oss_framework/OPERATIONAL_RUNBOOKS.md
- oss_framework/monitoring/README.md

## Training
- oss_framework/deployment/metabase/training/
- oss_framework/STAFF_TRAINING.md

## Contributing
- CONTRIBUTING.md
- SECURITY.md
- CODE_OF_CONDUCT.md
```

---

## Verification Checklist

After completing all removals and updates:

- [ ] No references to "OEA" or "Open Education Analytics" remain
- [ ] No references to Microsoft Azure services (Synapse, Data Lake, etc.)
- [ ] No references to removed directories (schemas/, packages/, framework/)
- [ ] All internal markdown links work
- [ ] README.md introduces OSS Framework (not OEA)
- [ ] CONTRIBUTING.md is OSS-specific (not Microsoft)
- [ ] SECURITY.md covers OSS deployment (DuckDB, Metabase)
- [ ] All oss_framework/ documentation is intact
- [ ] Git backup branch exists
- [ ] Git tag exists

---

## Files Summary

### ✅ KEEP (25 files)
- All `oss_framework/**/*.md` files

### ❌ REMOVE (70+ files)
- `schemas/**/*.md` (25+ files)
- `packages/**/*.md` (20+ files)
- `framework/**/*.md` (3 files)
- `docs/**/*.md` (3 files)
- Session/status files (19 files)

### 📝 REPLACE (3 files)
- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

### ✅ KEEP AS-IS (1 file)
- `CODE_OF_CONDUCT.md` (generic, suitable)

---

**End of Audit**
