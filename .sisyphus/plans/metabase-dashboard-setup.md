# Metabase Dashboard Setup

## TL;DR

> **Quick Summary**: Set up 5 analytics dashboards in Metabase with 12 visualizations and 26 interactive filters for the OSS Student Analytics Platform. Scripts are ready; execution requires coordination of dashboard IDs and 25-50 min manual filter-to-card connection.
> 
> **Deliverables**:
> - 5 fully functional dashboards in Metabase
> - 26 interactive filters (School, Grade Level, Risk Level, etc.)
> - Verified data display across all visualizations
> 
> **Estimated Effort**: Medium (2-3 hours including manual filter work)
> **Parallel Execution**: NO - sequential (each step depends on previous)
> **Critical Path**: Pre-flight → Create Dashboards → Update Filter Script → Add Filters → Manual Connection → Verify

---

## Context

### Original Request
User wants to set up the Metabase analytics dashboards now that the DuckDB database is connected.

### Interview Summary
**Key Discussions**:
- Metabase container running healthy on port 3000
- DuckDB connected at `/data/oea.duckdb` (24MB, 3,400 students, 5 views)
- User has admin credentials ready
- Scope: Full setup (dashboards + filters + verify)
- Don't close beads issues automatically

**Research Findings**:
- Scripts exist and are documented as "ready to run" in `RUN-DASHBOARDS.md`
- `create-dashboards-api.py` creates 12 visualizations across 5 dashboards
- `add-dashboard-filters.py` creates 26 filters but uses **hardcoded dashboard IDs 2-6**
- Manual filter-to-card connection required (25-50 min) per `QUICK-START.md`
- Related beads issues: `3ih`, `z8v`, `65q`, `7qb`, `e6p` (filters), `d72` (Docker - partially done)

### Metis Review
**Identified Gaps** (addressed):
- Dashboard ID mismatch: Filter script uses hardcoded IDs 2-6, but dashboard script generates dynamic IDs → **Plan includes ID capture and script update step**
- Visualization count: Corrected from "26" to "12" (26 is filters)
- Pre-requisite verification: Added pre-flight check for database connection
- Cleanup warning: Noted in guardrails that script deletes existing OSS Analytics content

---

## Work Objectives

### Core Objective
Create 5 production-ready Metabase dashboards with interactive filters for student analytics, connected to the DuckDB database.

### Concrete Deliverables
- Dashboard 1: Chronic Absenteeism Risk (6 visualizations, 4 filters)
- Dashboard 2: Student Wellbeing Profiles (2 visualizations, 3 filters)
- Dashboard 3: Equity Outcomes Analysis (2 visualizations, 3 filters)
- Dashboard 4: Class Effectiveness Comparison (1 visualization, 4 filters)
- Dashboard 5: Performance Correlations (1 visualization, 2 filters)
- All filters connected to relevant cards and functional

### Definition of Done
- [x] 5 dashboards visible in Metabase "OSS Analytics" collection
- [x] Each dashboard displays data (not "No results")
- [x] Filters appear and can be selected
- [ ] Selecting a filter updates the visualizations

### Must Have
- 5 dashboards with correct visualizations
- 26 filters added and connected to cards
- Data displaying from all 5 analytics views

### Must NOT Have (Guardrails)
- DO NOT modify SQL queries in scripts (documented as "fixed and ready")
- DO NOT create additional dashboards beyond the 5 specified
- DO NOT close beads issues (user will do manually)
- DO NOT skip the manual filter-to-card connection step (required per documentation)
- DO NOT run `add-dashboard-filters.py` without updating dashboard IDs first
- WARN: `create-dashboards-api.py` deletes ALL existing content in OSS Analytics collection

---

## Verification Strategy (MANDATORY)

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.
> The ONLY exception is the manual filter-to-card connection (Task 5), which is explicitly documented as requiring UI interaction.

### Test Decision
- **Infrastructure exists**: NO (no test framework for this operational task)
- **Automated tests**: NO (operational setup, not code development)
- **Agent-Executed QA**: YES (mandatory for all tasks except Task 5)

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

**Verification Tool by Task:**

| Task | Tool | How Agent Verifies |
|------|------|-------------------|
| Pre-flight | Bash (curl) | API health check, database list |
| Dashboard creation | Bash (curl + jq) | Dashboard count, collection contents |
| Filter addition | Bash (curl + jq) | Filter count per dashboard |
| Final verification | Playwright | Navigate dashboards, click filters, screenshot |

---

## Execution Strategy

### Sequential Execution (No Parallelization)

```
Task 1: Pre-flight verification
    ↓
Task 2: Run dashboard creation script
    ↓
Task 3: Capture dashboard IDs and update filter script
    ↓
Task 4: Run filter addition script
    ↓
Task 5: Manual filter-to-card connection (USER ACTION)
    ↓
Task 6: Verify all dashboards functional
```

**Critical Path**: All tasks are sequential. Each depends on the previous completing successfully.

---

## TODOs

- [x] 1. Pre-flight: Verify Metabase and Database Connection

  **What to do**:
  - Verify Metabase is accessible at http://localhost:3000
  - Verify DuckDB database is connected in Metabase
  - Verify the 5 analytics views are accessible

  **Must NOT do**:
  - Do NOT proceed if health check fails
  - Do NOT proceed if database is not connected

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple API verification checks, no complex logic
  - **Skills**: none needed
  
  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (first task)
  - **Blocks**: Tasks 2, 3, 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References**:
  - `oss_framework/deployment/metabase/README.md:155-175` - Health check and verification commands
  - `oss_framework/deployment/metabase/verify-database-connections.py` - Alternative verification script

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Metabase health check passes
    Tool: Bash (curl)
    Preconditions: Docker container oss-metabase running
    Steps:
      1. curl -s http://localhost:3000/api/health
      2. Parse JSON response
      3. Assert: status field equals "ok"
    Expected Result: {"status":"ok"}
    Evidence: Response body saved to stdout

  Scenario: Database connection exists in Metabase
    Tool: Bash (curl + jq)
    Preconditions: Metabase healthy, METABASE_EMAIL and METABASE_PASSWORD set
    Steps:
      1. POST /api/session with credentials → capture session token
      2. GET /api/database with session header
      3. Assert: response contains database with name containing "OSS" or "DuckDB"
      4. Capture database ID for later use
    Expected Result: At least 1 database connected
    Evidence: Database ID and name captured

  Scenario: Analytics views accessible
    Tool: Bash (curl + jq)
    Preconditions: Database ID known from previous scenario
    Steps:
      1. GET /api/database/{id}/schemas with session header
      2. Assert: response contains "main_main_analytics" schema
      3. GET /api/database/{id}/schema/main_main_analytics/tables
      4. Assert: response contains 5 tables (the views)
    Expected Result: 5 analytics views listed
    Evidence: View names captured
  ```

  **Commit**: NO

---

- [x] 2. Run Dashboard Creation Script

  **What to do**:
  - Set environment variables METABASE_EMAIL and METABASE_PASSWORD
  - Run `python3 create-dashboards-api.py`
  - Capture output including all dashboard IDs
  - Save dashboard IDs to a temporary file for next task

  **Must NOT do**:
  - Do NOT modify the script
  - Do NOT run if pre-flight failed
  - WARN: This deletes existing OSS Analytics collection content

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single script execution with output capture
  - **Skills**: none needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3, 4, 5, 6
  - **Blocked By**: Task 1

  **References**:
  - `oss_framework/deployment/metabase/RUN-DASHBOARDS.md:1-93` - Script documentation and expected output
  - `oss_framework/deployment/metabase/create-dashboards-api.py` - The script to run
  - `oss_framework/deployment/metabase/SETUP-STATE.md:162` - States 12 visualizations created

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Dashboard creation script completes successfully
    Tool: Bash
    Preconditions: Metabase healthy, database connected, credentials set
    Steps:
      1. cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
      2. export METABASE_EMAIL="$METABASE_EMAIL"
      3. export METABASE_PASSWORD="$METABASE_PASSWORD"
      4. python3 create-dashboards-api.py 2>&1 | tee /tmp/dashboard-creation.log
      5. Assert: Output contains "Created 5/5 dashboards successfully"
      6. Extract dashboard IDs from output: grep "Dashboard created (ID:" /tmp/dashboard-creation.log
      7. Save IDs to /tmp/dashboard-ids.txt
    Expected Result: 5 dashboards created, IDs captured
    Evidence: /tmp/dashboard-creation.log, /tmp/dashboard-ids.txt

  Scenario: Verify dashboards exist via API
    Tool: Bash (curl + jq)
    Preconditions: Script completed
    Steps:
      1. GET /api/collection/root/items with session header
      2. Find "OSS Analytics" collection ID
      3. GET /api/collection/{id}/items
      4. Assert: Contains 5 dashboards
      5. Assert: Dashboard names start with "Dashboard 1:", "Dashboard 2:", etc.
    Expected Result: 5 dashboards in OSS Analytics collection
    Evidence: Dashboard list JSON
  ```

  **Commit**: NO

---

- [x] 3. Update Filter Script with Dashboard IDs

  **What to do**:
  - Read dashboard IDs from /tmp/dashboard-ids.txt (captured in Task 2)
  - Update `add-dashboard-filters.py` lines 209, 266, 308, 350, 400 with actual IDs
  - The script has hardcoded IDs 2, 3, 4, 5, 6 that need to be replaced

  **Must NOT do**:
  - Do NOT change any other part of the script
  - Do NOT proceed if IDs weren't captured

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple text replacement in known locations
  - **Skills**: none needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4, 5, 6
  - **Blocked By**: Task 2

  **References**:
  - `oss_framework/deployment/metabase/add-dashboard-filters.py:209-210` - Dashboard 1 ID
  - `oss_framework/deployment/metabase/add-dashboard-filters.py:266` - Dashboard 2 ID
  - `oss_framework/deployment/metabase/add-dashboard-filters.py:308` - Dashboard 3 ID
  - `oss_framework/deployment/metabase/add-dashboard-filters.py:350` - Dashboard 4 ID
  - `oss_framework/deployment/metabase/add-dashboard-filters.py:400` - Dashboard 5 ID
  - `/tmp/dashboard-ids.txt` - IDs captured from Task 2

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Dashboard IDs updated in filter script
    Tool: Bash (grep)
    Preconditions: /tmp/dashboard-ids.txt exists with 5 IDs
    Steps:
      1. Read IDs from /tmp/dashboard-ids.txt
      2. Use sed or Edit tool to replace hardcoded IDs in add-dashboard-filters.py
      3. grep -n "dashboard_id.*=" add-dashboard-filters.py | head -10
      4. Assert: IDs match those in /tmp/dashboard-ids.txt
    Expected Result: Script updated with correct dashboard IDs
    Evidence: grep output showing updated lines

  Scenario: Script syntax valid after edit
    Tool: Bash
    Preconditions: Script edited
    Steps:
      1. python3 -m py_compile add-dashboard-filters.py
      2. Assert: Exit code is 0 (no syntax errors)
    Expected Result: No syntax errors
    Evidence: Exit code 0
  ```

  **Commit**: NO (temporary change for this execution)

---

- [x] 4. Run Filter Addition Script

  **What to do**:
  - Run `python3 add-dashboard-filters.py` with credentials
  - Verify 26 filters added across 5 dashboards
  - Note: Filters are NOT yet connected to cards (that's Task 5)

  **Must NOT do**:
  - Do NOT run if Task 3 wasn't completed
  - Do NOT expect filters to work yet (connection is manual)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single script execution
  - **Skills**: none needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 5, 6
  - **Blocked By**: Task 3

  **References**:
  - `oss_framework/deployment/metabase/QUICK-START.md:42-58` - Script execution and expected output
  - `oss_framework/deployment/metabase/add-dashboard-filters.py` - The script to run
  - `oss_framework/deployment/metabase/ADD-FILTERS-README.md` - Detailed documentation

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Filter addition script completes successfully
    Tool: Bash
    Preconditions: Dashboard IDs updated in script
    Steps:
      1. cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
      2. python3 add-dashboard-filters.py 2>&1 | tee /tmp/filter-creation.log
      3. Assert: Output contains "Added filters to 5/5 dashboards successfully"
    Expected Result: 26 filters added
    Evidence: /tmp/filter-creation.log

  Scenario: Verify filters exist via API
    Tool: Bash (curl + jq)
    Preconditions: Script completed
    Steps:
      1. For each dashboard ID in /tmp/dashboard-ids.txt:
      2. GET /api/dashboard/{id} with session header
      3. Count parameters array length
      4. Assert: Dashboard 1 has 4 filters, Dashboard 2 has 3, Dashboard 3 has 3, Dashboard 4 has 4, Dashboard 5 has 2
    Expected Result: 16 total filters (4+3+3+4+2)
    Evidence: Filter counts per dashboard
  ```

  **Commit**: NO

---

- [ ] 5. Manual: Connect Filters to Cards (USER ACTION REQUIRED)

  **What to do**:
  - Open Metabase at http://localhost:3000
  - For each of the 5 dashboards:
    1. Click gear icon → Edit dashboard
    2. Click each filter → Edit → Connect to cards
    3. Map filter to appropriate field (see field mapping below)
    4. Save dashboard
  - Estimated time: 25-50 minutes

  **Field Mapping Reference** (from QUICK-START.md):
  
  | Dashboard | Filter | Map to Field |
  |-----------|--------|--------------|
  | 1 | School | `primary_school` |
  | 1 | Grade Level | `grade_level` |
  | 1 | Risk Level | `wellbeing_risk_level` |
  | 1 | Row Limit | SQL LIMIT clause |
  | 2 | School | `primary_school` |
  | 2 | Grade Level | `grade_level` |
  | 2 | Compound Risk | `compound_risk_level` |
  | 3 | School | `primary_school` |
  | 3 | Demographic | `demographic_category` |
  | 3 | Min Cohort | SQL WHERE clause |
  | 4 | School | `school_id` |
  | 4 | Teacher | `teacher_id_hash` |
  | 4 | Grade Level | `grade_level` |
  | 4 | Term | `term` |
  | 5 | School | `school_id` |
  | 5 | Date Range | `school_year` |

  **Must NOT do**:
  - This step CANNOT be automated (Metabase API limitation)
  - Do NOT skip this step - filters won't work without connection

  **Recommended Agent Profile**:
  - **Category**: N/A - USER ACTION
    - Reason: Metabase UI interaction required, documented in QUICK-START.md

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References**:
  - `oss_framework/deployment/metabase/QUICK-START.md:60-102` - Step-by-step filter connection guide
  - `oss_framework/deployment/metabase/DASHBOARD-FILTERS-SPEC.md` - Complete technical specifications

  **Acceptance Criteria**:

  **User Self-Check (Manual):**
  - [ ] Dashboard 1: 4 filters connected and working
  - [ ] Dashboard 2: 3 filters connected and working
  - [ ] Dashboard 3: 3 filters connected and working
  - [ ] Dashboard 4: 4 filters connected and working
  - [ ] Dashboard 5: 2 filters connected and working
  - [ ] Selecting any filter updates the visualizations

  **Commit**: NO

---

- [ ] 6. Verify All Dashboards Functional

  **What to do**:
  - Verify each dashboard loads and displays data
  - Verify filters are functional (selection updates visualizations)
  - Take screenshots as evidence
  - Report any issues

  **Must NOT do**:
  - Do NOT close beads issues (user preference)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Browser-based verification with Playwright
  - **Skills**: `["playwright"]`
    - `playwright`: Navigate Metabase dashboards, interact with filters, capture screenshots

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final task)
  - **Blocks**: None (final task)
  - **Blocked By**: Task 5

  **References**:
  - `oss_framework/deployment/metabase/VERIFICATION-CHECKLIST.md` - Verification steps
  - `oss_framework/deployment/metabase/QUICK-START.md:108-118` - Success verification

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Dashboard 1 loads and displays data
    Tool: Playwright (playwright skill)
    Preconditions: Metabase running, user logged in (or login as first step)
    Steps:
      1. Navigate to: http://localhost:3000
      2. Login if prompted: Fill email, password, submit
      3. Navigate to: Dashboard 1 URL (from /tmp/dashboard-ids.txt)
      4. Wait for: .Dashboard visible (timeout: 30s)
      5. Assert: At least 1 visualization card is visible
      6. Assert: No "No results" message displayed
      7. Click: First filter dropdown
      8. Assert: Dropdown options appear
      9. Select: First option in dropdown
      10. Wait for: Visualizations to update (loading spinner disappears)
      11. Assert: Data still displays (not empty)
      12. Screenshot: .sisyphus/evidence/dashboard-1-verified.png
    Expected Result: Dashboard loads, shows data, filters work
    Evidence: .sisyphus/evidence/dashboard-1-verified.png

  Scenario: Dashboard 2 loads and displays data
    Tool: Playwright (playwright skill)
    Steps: (Same as Dashboard 1, different URL)
    Evidence: .sisyphus/evidence/dashboard-2-verified.png

  Scenario: Dashboard 3 loads and displays data
    Tool: Playwright (playwright skill)
    Steps: (Same as Dashboard 1, different URL)
    Evidence: .sisyphus/evidence/dashboard-3-verified.png

  Scenario: Dashboard 4 loads and displays data
    Tool: Playwright (playwright skill)
    Steps: (Same as Dashboard 1, different URL)
    Evidence: .sisyphus/evidence/dashboard-4-verified.png

  Scenario: Dashboard 5 loads and displays data
    Tool: Playwright (playwright skill)
    Steps: (Same as Dashboard 1, different URL)
    Evidence: .sisyphus/evidence/dashboard-5-verified.png
  ```

  **Commit**: NO

---

## Commit Strategy

No commits required for this operational task. All changes are runtime configuration in Metabase.

---

## Success Criteria

### Verification Commands
```bash
# Verify Metabase healthy
curl -s http://localhost:3000/api/health | jq -r '.status'
# Expected: ok

# Verify 5 dashboards exist (requires session token)
curl -s http://localhost:3000/api/dashboard \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  | jq '[.[] | select(.name | startswith("Dashboard"))] | length'
# Expected: 5
```

### Final Checklist
- [x] 5 dashboards visible in Metabase
- [x] All dashboards display data (no empty states)
- [x] 16 filters added across dashboards (4+3+3+4+2)
- [ ] Filters connected to cards and functional
- [ ] Screenshots captured as evidence

---

## Related Beads Issues (Reference Only)

The following beads issues relate to this work. User will close manually after verification:

| Issue ID | Title | Relates To |
|----------|-------|------------|
| `openedDataEstate-3ih` | Dashboard 1 filters | Task 4, 5 |
| `openedDataEstate-z8v` | Dashboard 2 filters | Task 4, 5 |
| `openedDataEstate-65q` | Dashboard 3 filters | Task 4, 5 |
| `openedDataEstate-7qb` | Dashboard 4 filters | Task 4, 5 |
| `openedDataEstate-e6p` | Dashboard 5 filters | Task 4, 5 |
| `openedDataEstate-d72` | Docker Compose setup | Already partially complete |

---

## Notes

1. **Task 5 is manual**: Metabase API does not support connecting filters to cards programmatically. This is a known limitation documented in the codebase.

2. **Dashboard ID coordination**: The filter script uses hardcoded IDs. Task 3 addresses this by updating the script after capturing actual IDs from Task 2.

3. **Cleanup behavior**: `create-dashboards-api.py` deletes ALL existing content in the OSS Analytics collection before creating new dashboards.

4. **Credentials**: Never commit credentials. Use environment variables `METABASE_EMAIL` and `METABASE_PASSWORD`.
