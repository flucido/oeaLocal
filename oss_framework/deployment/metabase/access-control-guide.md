# Metabase Access Control & Security Configuration Guide

**Version**: 1.0  
**Last Updated**: January 27, 2026  
**Audience**: System Administrators, Security Officers  
**Estimated Implementation Time**: 8-12 hours

---

## Table of Contents

1. [Overview](#overview)
2. [User Roles & Permissions Matrix](#user-roles--permissions-matrix)
3. [Prerequisites](#prerequisites)
4. [Implementation Steps](#implementation-steps)
   - [Step 1: Create User Groups](#step-1-create-user-groups-30-minutes)
   - [Step 2: Create User Accounts](#step-2-create-user-accounts-45-minutes)
   - [Step 3: Configure Database Permissions](#step-3-configure-database-permissions-45-minutes)
   - [Step 4: Configure Collection Permissions](#step-4-configure-collection-permissions-30-minutes)
   - [Step 5: Implement Row-Level Security](#step-5-implement-row-level-security-3-4-hours)
   - [Step 6: Configure Field Masking](#step-6-configure-field-masking-45-minutes)
   - [Step 7: Session & Authentication Settings](#step-7-session--authentication-settings-30-minutes)
   - [Step 8: Verify Access Controls](#step-8-verify-access-controls-1-hour)
   - [Step 9: Document Configuration](#step-9-document-configuration-30-minutes)
5. [Row-Level Security (RLS) Details](#row-level-security-rls-details)
6. [Testing & Verification](#testing--verification)
7. [Troubleshooting](#troubleshooting)
8. [FERPA Compliance Checklist](#ferpa-compliance-checklist)
9. [Maintenance & Audit](#maintenance--audit)

---

## Overview

This guide provides step-by-step instructions for implementing role-based access control (RBAC) in your Metabase analytics deployment. Proper access controls ensure:

- **Data Privacy**: Users only see data they're authorized to access
- **FERPA Compliance**: Student information is protected according to federal regulations
- **Role-Based Access**: Different stakeholder groups see appropriate dashboards and data
- **Accountability**: Audit logs track who accessed what data and when

### What You'll Configure

By the end of this guide, you will have:
- ✅ 5 user groups with defined permissions
- ✅ User accounts assigned to appropriate groups
- ✅ Row-level security (RLS) filtering data by school/grade/class
- ✅ Field-level masking hiding sensitive information
- ✅ Session timeout and password policies
- ✅ Testing procedures to verify access controls

---

## User Roles & Permissions Matrix

### Role 1: Superintendent / District Administrator

**Access Scope**: Full district visibility, all functionality

| Capability | Access Level |
|------------|--------------|
| **Dashboards** | ✅ All 5 dashboards |
| **Schools** | ✅ All schools (no filters) |
| **Grade Levels** | ✅ All grades (9-12) |
| **Student Data** | ✅ Full access (aggregated + individual) |
| **Edit Rights** | ✅ Can create/edit queries and dashboards |
| **Export** | ✅ Unlimited (CSV, PDF, JSON) |
| **Admin Panel** | ✅ Full access to settings |

**Use Cases**:
- District-wide trend analysis
- Cross-school performance comparisons
- Board meeting preparation
- Strategic planning and resource allocation

---

### Role 2: School Principal

**Access Scope**: School-level visibility only

| Capability | Access Level |
|------------|--------------|
| **Dashboards** | ✅ All 5 dashboards |
| **Schools** | ⚠️ **LOCKED TO THEIR SCHOOL ONLY** |
| **Grade Levels** | ✅ All grades at their school |
| **Student Data** | ⚠️ Student IDs visible, names hidden |
| **Edit Rights** | ⚠️ Limited (personal queries only, cannot edit dashboards) |
| **Export** | ⚠️ CSV only (their school's data) |
| **Admin Panel** | ❌ No access |

**Data Filtering**:
```sql
-- Auto-applied filter for all queries
WHERE primary_school = 'Lincoln High School'  -- Their assigned school
```

**Cannot See**:
- ❌ Other schools' data
- ❌ Student names (only hashed IDs)
- ❌ District-wide aggregations that include other schools

**Use Cases**:
- Monitor school attendance trends
- Identify at-risk students for intervention
- Evaluate class and teacher effectiveness
- Prepare for SART/SARB meetings

---

### Role 3: Counselor / Case Manager

**Access Scope**: Grade-level visibility with student names (for case management)

| Capability | Access Level |
|------------|--------------|
| **Dashboards** | ⚠️ Dashboard 2 (Wellbeing) + Dashboard 3 (Equity) ONLY |
| **Schools** | ⚠️ Their assigned school |
| **Grade Levels** | ⚠️ **LOCKED TO ASSIGNED GRADES** (e.g., 9-10 only) |
| **Student Data** | ✅ **STUDENT NAMES VISIBLE** (required for casework) |
| **Edit Rights** | ❌ None |
| **Export** | ⚠️ CSV only (their assigned students) |
| **Admin Panel** | ❌ No access |

**Data Filtering**:
```sql
-- Auto-applied filter for all queries
WHERE primary_school = 'Lincoln High School'
  AND grade_level IN (9, 10)  -- Assigned grades only
```

**Dashboard Access**:
- ✅ Dashboard 2: Wellbeing & Mental Health Risk
- ✅ Dashboard 3: Equity Outcomes Analysis
- ❌ Dashboard 1: Chronic Absenteeism (administrative focus)
- ❌ Dashboard 4: Class Effectiveness (principal/teacher focus)
- ❌ Dashboard 5: Performance Correlations (research focus)

**Use Cases**:
- Identify students needing counseling services
- Build intervention case portfolios
- Track student wellbeing over time
- Coordinate with teachers on at-risk students

---

### Role 4: Teacher

**Access Scope**: Class-level visibility only (their own classes)

| Capability | Access Level |
|------------|--------------|
| **Dashboards** | ⚠️ Dashboard 4 (Class Effectiveness) ONLY |
| **Schools** | ⚠️ Their school |
| **Grade Levels** | ⚠️ Grades they teach |
| **Student Data** | ⚠️ **LOCKED TO THEIR CLASSES** (roster + grades only) |
| **Edit Rights** | ❌ None |
| **Export** | ⚠️ Roster only (their classes) |
| **Admin Panel** | ❌ No access |

**Data Filtering**:
```sql
-- Auto-applied filter for all queries
WHERE teacher_id_hash = 'TEACHER_ABC123_HASH'  -- Authenticated user's ID
```

**Dashboard Access**:
- ✅ Dashboard 4: Class Effectiveness (their classes only)
- ❌ All other dashboards

**Can See**:
- ✅ Their class pass rates and average grades
- ✅ Comparison to school average (anonymized)
- ✅ Student roster with grades
- ✅ Subgroup performance (ELL, SPED, FRL)

**Cannot See**:
- ❌ Other teachers' class data
- ❌ Individual student attendance/discipline records
- ❌ School-wide or district-level data

**Use Cases**:
- Monitor class performance trends
- Identify struggling students for targeted support
- Reflect on teaching effectiveness
- Prepare for evaluations

---

### Role 5: Board Member

**Access Scope**: District-level aggregated data only (no student names)

| Capability | Access Level |
|------------|--------------|
| **Dashboards** | ⚠️ Dashboards 1, 3, 5 ONLY (executive summaries) |
| **Schools** | ✅ All schools (aggregated view) |
| **Grade Levels** | ✅ All grades (aggregated) |
| **Student Data** | ❌ **NO STUDENT NAMES** (aggregated metrics only) |
| **Edit Rights** | ❌ None |
| **Export** | ⚠️ PDF reports only (no raw data) |
| **Admin Panel** | ❌ No access |

**Data Masking**:
- All student identifiers removed or redacted
- Only aggregated metrics visible (counts, averages, percentages)
- No drill-down to individual student records

**Dashboard Access**:
- ✅ Dashboard 1: Chronic Absenteeism Risk (aggregated)
- ✅ Dashboard 3: Equity Outcomes Analysis
- ✅ Dashboard 5: Performance Correlations & Insights
- ❌ Dashboard 2: Wellbeing (too granular, contains student names)
- ❌ Dashboard 4: Class Effectiveness (teacher-specific, personnel data)

**Use Cases**:
- Board meeting presentations
- Policy decision support
- District accountability monitoring
- Strategic goal setting

---

## Prerequisites

Before beginning access control configuration, ensure:

- [ ] **Metabase is running** and accessible at `http://localhost:3000`
- [ ] **Admin account created** and you can log in
- [ ] **Database connected** (OSS Analytics database with 5 views)
- [ ] **All 5 dashboards created** (Tasks 4.02-4.06 complete)
- [ ] **Backup created** of Metabase configuration
- [ ] **List of users** with their roles and school assignments

**Estimated Total Time**: 8-12 hours

---

## Implementation Steps

### Step 1: Create User Groups (30 minutes)

**Objective**: Define groups corresponding to user roles

**Instructions**:

1. **Log in to Metabase** as admin
2. **Navigate to Admin Panel**:
   - Click gear icon (⚙️) in top-right corner
   - Select **"Admin Settings"**
3. **Go to People Management**:
   - Click **"People"** in left sidebar
   - Click **"Groups"** tab
4. **Create Each Group**:

   Click **"+ Create a group"** button and create:

   | Group Name | Description |
   |------------|-------------|
   | `Administrators` | District superintendents and data analytics team |
   | `Principals` | School principals and assistant principals |
   | `Counselors` | School counselors, social workers, case managers |
   | `Teachers` | Classroom teachers |
   | `Board_Members` | School board members and trustees |

5. **Verify Groups Created**:
   - You should see 5 new groups listed
   - Each should show "0 members" initially

**Success Criteria**:
- ✅ 5 groups visible in Admin → People → Groups
- ✅ Each group has clear description
- ✅ Ready to assign users

---

### Step 2: Create User Accounts (45 minutes)

**Objective**: Create individual user accounts and assign to appropriate groups

**Instructions**:

1. **Navigate to People Management**:
   - Admin Settings → **"People"**
   - Ensure you're on the **"Members"** tab
2. **For Each Staff Member, Create Account**:

   Click **"+ Add someone"** and fill out:
   - **Email**: `firstname.lastname@district.edu`
   - **First Name**: User's first name
   - **Last Name**: User's last name
   - **Group**: Select appropriate group from dropdown

3. **Example User Accounts** (for testing):

   | Email | Name | Group | School | Grade Levels |
   |-------|------|-------|--------|--------------|
   | `superintendent@district.local` | District Admin | Administrators | All | All |
   | `principal.lincoln@district.local` | Jane Smith | Principals | Lincoln High | 9-12 |
   | `principal.washington@district.local` | John Doe | Principals | Washington High | 9-12 |
   | `counselor.lincoln.9@district.local` | Maria Garcia | Counselors | Lincoln High | 9-10 |
   | `counselor.lincoln.11@district.local` | David Lee | Counselors | Lincoln High | 11-12 |
   | `teacher.math.101@district.local` | Sarah Johnson | Teachers | Lincoln High | 9-12 |
   | `boardmember1@district.local` | Board Member 1 | Board_Members | All | All |

4. **Send Invitations**:
   - **Option A**: Users receive email with password setup link
   - **Option B**: Set temporary password, require change on first login

5. **Document User Assignments**:
   - Keep spreadsheet of: Email, Name, Group, School, Grade Levels
   - This will be needed for Step 5 (RLS configuration)

**Success Criteria**:
- ✅ All staff members have accounts created
- ✅ Each user assigned to correct group
- ✅ Users documented with school/grade assignments

---

### Step 3: Configure Database Permissions (45 minutes)

**Objective**: Set base-level permissions for each group to access the database

**Instructions**:

1. **Navigate to Permissions Panel**:
   - Admin Settings → **"Permissions"**
   - Select **"Data"** tab (database permissions)
2. **Select Database**: Click on `OSS Analytics` database
3. **Configure Table Access by Group**:

   For each of the 5 analytics views, set permissions per group:

   **View 1: `v_chronic_absenteeism_risk`**
   | Group | Access Level | Notes |
   |-------|-------------|-------|
   | Administrators | ✅ Unrestricted | Full query access |
   | Principals | ⚠️ Sandboxed | Filtered by school |
   | Counselors | ❌ No access | Not authorized for this view |
   | Teachers | ❌ No access | Not authorized |
   | Board_Members | ⚠️ Limited | Aggregated only |

   **View 2: `v_wellbeing_risk_profiles`**
   | Group | Access Level | Notes |
   |-------|-------------|-------|
   | Administrators | ✅ Unrestricted | Full query access |
   | Principals | ⚠️ Sandboxed | Filtered by school |
   | Counselors | ⚠️ Sandboxed | Filtered by school + grade |
   | Teachers | ❌ No access | Not authorized |
   | Board_Members | ❌ No access | Too granular |

   **View 3: `v_equity_outcomes_by_demographics`**
   | Group | Access Level | Notes |
   |-------|-------------|-------|
   | Administrators | ✅ Unrestricted | Full query access |
   | Principals | ⚠️ Sandboxed | Filtered by school |
   | Counselors | ⚠️ Sandboxed | Filtered by school |
   | Teachers | ❌ No access | Not authorized |
   | Board_Members | ⚠️ Limited | Aggregated only |

   **View 4: `v_class_section_comparison`**
   | Group | Access Level | Notes |
   |-------|-------------|-------|
   | Administrators | ✅ Unrestricted | Full query access |
   | Principals | ⚠️ Sandboxed | Filtered by school |
   | Counselors | ❌ No access | Not relevant to role |
   | Teachers | ⚠️ Sandboxed | Filtered by teacher ID |
   | Board_Members | ❌ No access | Personnel data |

   **View 5: `v_performance_correlations`**
   | Group | Access Level | Notes |
   |-------|-------------|-------|
   | Administrators | ✅ Unrestricted | Full query access |
   | Principals | ⚠️ Sandboxed | Filtered by school |
   | Counselors | ❌ No access | Research-focused |
   | Teachers | ❌ No access | Research-focused |
   | Board_Members | ⚠️ Limited | Aggregated only |

4. **Configure Access Levels**:

   **For "Unrestricted" access**:
   - Click the cell for that group/table
   - Select **"Unrestricted"**

   **For "Sandboxed" access**:
   - Click the cell
   - Select **"Sandboxed"**
   - Configure sandbox filter (see Step 5 for details)

   **For "No access"**:
   - Click the cell
   - Select **"No"** or leave blank

5. **Save Changes**: Click **"Save Changes"** button at bottom

**Success Criteria**:
- ✅ All 5 views configured with appropriate permissions
- ✅ Sandboxed access marked for groups needing RLS
- ✅ No access set for unauthorized groups

---

### Step 4: Configure Collection Permissions (30 minutes)

**Objective**: Control which groups can access which dashboards

**Instructions**:

1. **Navigate to Collections**:
   - Click **"Collections"** in main navigation bar
   - Locate **"OSS Analytics"** collection (contains all 5 dashboards)
2. **Option A: Create Sub-Collections by Role** (Recommended)

   **Structure**:
   ```
   OSS Analytics/
   ├── Admin Dashboards/          (Administrators only)
   │   ├── Dashboard 1: Chronic Absenteeism
   │   ├── Dashboard 2: Wellbeing Risk
   │   ├── Dashboard 3: Equity Outcomes
   │   ├── Dashboard 4: Class Effectiveness
   │   └── Dashboard 5: Performance Correlations
   ├── Principal Dashboards/      (Principals + Administrators)
   │   └── [Same 5 dashboards]
   ├── Counselor Dashboards/      (Counselors + Administrators)
   │   ├── Dashboard 2: Wellbeing Risk
   │   └── Dashboard 3: Equity Outcomes
   ├── Teacher Dashboards/        (Teachers + Administrators)
   │   └── Dashboard 4: Class Effectiveness
   └── Board Dashboards/          (Board Members + Administrators)
       ├── Dashboard 1: Chronic Absenteeism
       ├── Dashboard 3: Equity Outcomes
       └── Dashboard 5: Performance Correlations
   ```

   **Implementation**:
   1. Create sub-collection: Click **"+ New collection"**
   2. Name it (e.g., "Principal Dashboards")
   3. Move or copy dashboards into collection
   4. Set permissions: Click **"..."** → **"Edit permissions"**
   5. Grant view access to appropriate group(s)

3. **Option B: Single Collection with Dashboard-Level Permissions**

   If you prefer flat structure:
   1. Keep all dashboards in root "OSS Analytics" collection
   2. For each dashboard, set individual permissions:
      - Click dashboard **"..."** menu
      - Select **"Move to collection"** or **"Edit permissions"**
      - Grant access to specific groups

4. **Set Permissions for Each Sub-Collection**:

   **Admin Dashboards**:
   - Administrators: ✅ Edit
   - All others: ❌ No access

   **Principal Dashboards**:
   - Administrators: ✅ Edit
   - Principals: ✅ View
   - All others: ❌ No access

   **Counselor Dashboards**:
   - Administrators: ✅ Edit
   - Counselors: ✅ View
   - All others: ❌ No access

   **Teacher Dashboards**:
   - Administrators: ✅ Edit
   - Teachers: ✅ View
   - All others: ❌ No access

   **Board Dashboards**:
   - Administrators: ✅ Edit
   - Board_Members: ✅ View
   - All others: ❌ No access

5. **Verify Collection Access**:
   - Log out of admin account
   - Log in as test user from each group
   - Verify they see ONLY their authorized collections/dashboards

**Success Criteria**:
- ✅ Collections organized by role (or dashboard permissions set)
- ✅ Each group sees only authorized dashboards
- ✅ Administrators can edit, others can only view

---

### Step 5: Implement Row-Level Security (3-4 hours)

**Objective**: Ensure users only see data rows they're authorized to access

**CRITICAL STEP**: This is the most important security configuration.

#### Understanding RLS in Metabase

**What is Row-Level Security?**
- Filters which data rows are returned in queries
- Users see only their school/grade/classes automatically
- Implemented via User Attributes + Sandboxed Tables

**Methods**:
1. ✅ **User Attributes** (RECOMMENDED): Store user metadata, auto-inject into queries
2. ❌ **Separate Dashboards**: Create individual dashboards per user (not scalable)
3. ❌ **Database Views**: Create filtered views (not flexible, requires DB changes)

---

#### Step 5.1: Define User Attributes

**User Attributes** store metadata about each user (school, grades, teacher ID) that Metabase automatically injects into queries.

1. **Navigate to Settings**:
   - Admin Settings → **"Settings"** → **"Admin Settings"**
   - Scroll to **"User Attributes"** section
   - *(Note: In some Metabase versions, this may be under "Permissions" tab)*

2. **Create Attributes**:

   Click **"+ Add attribute"** for each:

   | Attribute Name | Type | Description | Example Value |
   |----------------|------|-------------|---------------|
   | `school` | Text | User's assigned school | `Lincoln High School` |
   | `grade_levels` | Text | Comma-separated grade levels | `9,10` |
   | `teacher_id` | Text | Teacher's hashed ID | `TEACHER_ABC123_HASH` |

3. **Configure Each Attribute**:
   - **Name**: `school` (lowercase, no spaces)
   - **Display Name**: "School"
   - **Type**: Text
   - Click **"Save"**

---

#### Step 5.2: Assign Attributes to Users

For each user account, set their attribute values:

1. **Navigate to People**:
   - Admin Settings → **"People"**
   - Click on a user's name
2. **Set User Attributes**:
   - Scroll to **"User Attributes"** section
   - Fill in values for each attribute

**Examples**:

**Principal at Lincoln High**:
```
school: Lincoln High School
grade_levels: 9,10,11,12
teacher_id: (leave blank)
```

**Counselor at Lincoln High (Grades 9-10)**:
```
school: Lincoln High School
grade_levels: 9,10
teacher_id: (leave blank)
```

**Math Teacher**:
```
school: Lincoln High School
grade_levels: 9,10,11,12
teacher_id: TEACHER_MATH_101_HASH
```

**Board Member**:
```
school: (leave blank - sees all schools aggregated)
grade_levels: (leave blank)
teacher_id: (leave blank)
```

3. **Repeat for All Users**: Assign attributes to every non-administrator user

**Success Criteria**:
- ✅ All principals have `school` attribute set
- ✅ All counselors have `school` + `grade_levels` attributes set
- ✅ All teachers have `school` + `teacher_id` attributes set

---

#### Step 5.3: Configure Data Sandboxing

**Data Sandboxing** applies user attributes as filters to database queries automatically.

1. **Navigate to Permissions**:
   - Admin Settings → **"Permissions"** → **"Data"**
   - Select `OSS Analytics` database
2. **For Each Group Needing RLS**, Configure Sandbox:

   **Example: Principals Group**

   1. Click on cell for Principals group + `v_chronic_absenteeism_risk` table
   2. Select **"Sandboxed"**
   3. Click **"Create a sandbox"**
   4. Configure filter:
      - **Column**: Select `primary_school`
      - **Operator**: "Is"
      - **Value**: Select **"User attribute"** → `school`
   5. Click **"Save"**

   **Result**: When a principal queries this table, Metabase automatically adds:
   ```sql
   WHERE primary_school = 'Lincoln High School'  -- Their school attribute
   ```

   **Example: Counselors Group**

   1. Click on cell for Counselors group + `v_wellbeing_risk_profiles` table
   2. Select **"Sandboxed"**
   3. Click **"Create a sandbox"**
   4. **Add Multiple Filters**:
      - Filter 1:
        - **Column**: `primary_school`
        - **Operator**: "Is"
        - **Value**: User attribute → `school`
      - Click **"+ Add filter"**
      - Filter 2:
        - **Column**: `grade_level`
        - **Operator**: "Is one of"
        - **Value**: User attribute → `grade_levels`
   5. Click **"Save"**

   **Result**: Counselors see only students at their school in their assigned grades.

   **Example: Teachers Group**

   1. Click on cell for Teachers group + `v_class_section_comparison` table
   2. Select **"Sandboxed"**
   3. Configure filter:
      - **Column**: `teacher_id_hash`
      - **Operator**: "Is"
      - **Value**: User attribute → `teacher_id`
   4. Click **"Save"**

   **Result**: Teachers see only their own classes.

3. **Repeat for All Sandboxed Tables**:
   - Use table in Step 3 to identify which groups need sandboxing for which views
   - Configure sandbox for each group/table combination marked as "Sandboxed"

**Success Criteria**:
- ✅ Principals sandboxed to their school on all 5 views
- ✅ Counselors sandboxed to school + grade on views 2 & 3
- ✅ Teachers sandboxed to their teacher ID on view 4
- ✅ All sandbox filters use user attributes (not hard-coded values)

---

#### Step 5.4: Update Dashboard Filters (if needed)

If dashboards have manual filters, update them to respect sandboxing:

1. **Open Each Dashboard**
2. **For Each Filter**:
   - Click **"Edit"** (if you have permissions)
   - If filter is set to "Optional", consider making it **"Required"**
   - If filter should be locked for non-admins, set **"Locked"** ✅
3. **Test**: Log in as non-admin user, verify they cannot change locked filters

**Success Criteria**:
- ✅ Filters that enforce RLS are locked (users cannot modify)
- ✅ Users cannot bypass sandbox by changing dashboard filters

---

### Step 6: Configure Field Masking (45 minutes)

**Objective**: Hide sensitive fields from unauthorized users

**Sensitive Fields Requiring Protection**:
- Student names (hide from principals, teachers, board; show to counselors)
- Teacher names (hide from board members)
- Student IDs (show only hashed versions)
- Dates of birth, SSN (never show to anyone except authorized admin)

**Instructions**:

1. **Navigate to Data Model**:
   - Admin Settings → **"Data Model"**
   - Select `OSS Analytics` database
   - Select schema: `main_main_analytics`
2. **For Each Sensitive Field**, Configure Visibility:

   **Example: `student_name_display` field in `v_chronic_absenteeism_risk`**

   1. Click on the view name (e.g., `v_chronic_absenteeism_risk`)
   2. Find field `student_name_display` in field list
   3. Click on field to expand settings
   4. Go to **"Visibility"** section
   5. Set visibility per group:
      - Administrators: ✅ **Visible**
      - Principals: ❌ **Hidden** or **Redacted**
      - Counselors: ✅ **Visible** (needed for case management)
      - Teachers: ❌ **Hidden**
      - Board_Members: ❌ **Hidden**
   6. Click **"Save Changes"**

   **Visibility Options**:
   - **Visible**: Field appears normally
   - **Redacted**: Field exists but shows `[Redacted]` or `***`
   - **Hidden**: Field does not appear in query results at all

3. **Configure All Sensitive Fields**:

   **In `v_chronic_absenteeism_risk`**:
   | Field | Admins | Principals | Counselors | Teachers | Board |
   |-------|--------|-----------|-----------|----------|-------|
   | `student_name_display` | ✅ | ❌ | ✅ | ❌ | ❌ |
   | `student_id_hash` | ✅ | ✅ | ✅ | ❌ | ❌ |
   | `student_id` (if exists, unhashed) | ✅ | ❌ | ❌ | ❌ | ❌ |

   **In `v_wellbeing_risk_profiles`**:
   | Field | Admins | Principals | Counselors | Teachers | Board |
   |-------|--------|-----------|-----------|----------|-------|
   | `student_name_display` | ✅ | ❌ | ✅ | ❌ | ❌ |
   | `date_of_birth` (if exists) | ✅ | ❌ | ✅ | ❌ | ❌ |

   **In `v_class_section_comparison`**:
   | Field | Admins | Principals | Counselors | Teachers | Board |
   |-------|--------|-----------|-----------|----------|-------|
   | `teacher_name` (if exists) | ✅ | ✅ | ❌ | ✅ | ❌ |
   | `teacher_id_hash` | ✅ | ✅ | ❌ | ✅ | ❌ |

4. **Save All Changes**: Click **"Save"** after configuring each view

**Success Criteria**:
- ✅ Student names hidden from principals, teachers, board members
- ✅ Student names visible to counselors (for case management)
- ✅ Teacher names hidden from board members (personnel privacy)
- ✅ All unhashed IDs hidden from all non-admin users

---

### Step 7: Session & Authentication Settings (30 minutes)

**Objective**: Enforce security policies for user sessions

**Instructions**:

1. **Navigate to Authentication Settings**:
   - Admin Settings → **"Settings"** → **"Authentication"**

2. **Configure Session Timeout**:
   - Find **"Session timeout"** setting
   - Set to: **30 minutes** of inactivity
   - Click **"Save"**
   - **Purpose**: Auto-logout inactive users to prevent unauthorized access

3. **Configure Password Policy**:

   Depending on Metabase version, you may have limited control. Recommended settings:
   - **Minimum length**: 12 characters
   - **Complexity**: Require uppercase, lowercase, number, special character
   - **Expiration**: 90 days (require password change)
   - **Reuse prevention**: Block last 5 passwords

   *(Note: Metabase open-source may not support all password policy features. Consider using SSO for stronger policies.)*

4. **Configure Multi-Factor Authentication (MFA)** (Optional):

   If available in your Metabase version:
   - Navigate to **"Admin Settings"** → **"Authentication"** → **"MFA"**
   - Enable for: **Administrators only** (minimum)
   - **Recommended**: Enable for all users if district policy requires

   *(Note: MFA may require Metabase Enterprise edition or external SSO)*

5. **Configure Login Rate Limiting** (if available):
   - **Max failed attempts**: 5
   - **Lockout duration**: 15 minutes
   - **Purpose**: Prevent brute-force password attacks

6. **Configure SSO Integration** (Optional but Recommended):

   If your district uses Single Sign-On (Google Workspace, Microsoft Azure AD, etc.):
   - Navigate to **"Admin Settings"** → **"Authentication"**
   - Select your SSO provider:
     - **Google**: Requires OAuth Client ID and Secret
     - **SAML**: Requires IdP metadata URL
     - **LDAP**: Requires server connection details
   - Follow provider-specific setup instructions
   - **Benefits**:
     - Centralized user management
     - Automatic de-provisioning when staff leaves
     - Stronger authentication policies
     - Easier for users (single login)

7. **Enable Audit Logging** (if available):
   - Navigate to **"Admin Settings"** → **"Audit"** (or **"Logs"**)
   - Enable audit log: ✅
   - **Track**: User logins, queries run, data exports, permission changes
   - **Review**: Monthly (check for suspicious activity)

**Success Criteria**:
- ✅ Session timeout set to 30 minutes
- ✅ Password policy configured (or SSO enabled)
- ✅ MFA enabled for administrators
- ✅ Audit logging enabled

---

### Step 8: Verify Access Controls (1 hour)

**Objective**: Test that all access controls work as expected

**Test Plan**: Log in as test users from each group and verify behavior

#### Test 1: Administrator Access

1. **Login as**: `superintendent@district.local`
2. **Verify**:
   - ✅ Can see all 5 dashboards
   - ✅ Can see all schools in filters (no restrictions)
   - ✅ Can create new queries (SQL editor accessible)
   - ✅ Can export data in multiple formats (CSV, PDF, JSON)
   - ✅ Admin panel accessible
3. **Test Query**:
   ```sql
   SELECT DISTINCT primary_school 
   FROM v_chronic_absenteeism_risk;
   ```
   **Expected**: All schools returned (e.g., Lincoln High, Washington High, etc.)

#### Test 2: Principal Access (Lincoln High)

1. **Login as**: `principal.lincoln@district.local`
2. **Verify**:
   - ✅ Can see all 5 dashboards
   - ⚠️ Data filtered to Lincoln High School ONLY
   - ❌ Cannot see Washington High School data
   - ⚠️ Student names are hidden (only IDs visible)
   - ✅ Can export CSV (Lincoln data only)
   - ❌ Admin panel not accessible
3. **Test Query**:
   ```sql
   SELECT DISTINCT primary_school 
   FROM v_chronic_absenteeism_risk;
   ```
   **Expected**: Only `Lincoln High School` (not other schools)
4. **Test Name Visibility**:
   - Open Dashboard 1 (Chronic Absenteeism)
   - Look at student table
   - **Expected**: Student names should be hidden/redacted

#### Test 3: Counselor Access (Lincoln High, Grades 9-10)

1. **Login as**: `counselor.lincoln.9@district.local`
2. **Verify**:
   - ✅ Can see Dashboard 2 (Wellbeing) + Dashboard 3 (Equity)
   - ❌ Cannot see Dashboards 1, 4, 5
   - ⚠️ Data filtered to Lincoln High + Grades 9-10 ONLY
   - ✅ Student names ARE VISIBLE (for case management)
   - ✅ Can export CSV (their students only)
3. **Test Query**:
   ```sql
   SELECT DISTINCT grade_level 
   FROM v_wellbeing_risk_profiles;
   ```
   **Expected**: Only `9` and `10` (not 11 or 12)
4. **Test Name Visibility**:
   - Open Dashboard 2 (Wellbeing Risk)
   - Look at student table
   - **Expected**: Student names should be visible

#### Test 4: Teacher Access

1. **Login as**: `teacher.math.101@district.local`
2. **Verify**:
   - ✅ Can see Dashboard 4 (Class Effectiveness) ONLY
   - ❌ Cannot see Dashboards 1, 2, 3, 5
   - ⚠️ Data filtered to THEIR CLASSES ONLY
   - ❌ Cannot see other teachers' data
   - ✅ Can export roster (their classes)
3. **Test Query**:
   ```sql
   SELECT DISTINCT teacher_id_hash 
   FROM v_class_section_comparison;
   ```
   **Expected**: Only `TEACHER_MATH_101_HASH` (their ID)

#### Test 5: Board Member Access

1. **Login as**: `boardmember1@district.local`
2. **Verify**:
   - ✅ Can see Dashboards 1, 3, 5
   - ❌ Cannot see Dashboards 2, 4
   - ⚠️ NO student names visible (all aggregated)
   - ⚠️ Cannot drill down to individual students
   - ✅ Can export PDF reports only (no CSV with raw data)
3. **Test Name Visibility**:
   - Open Dashboard 1 (Chronic Absenteeism)
   - Try to see student names
   - **Expected**: Names should be hidden/redacted
4. **Test Drill-Down Prevention**:
   - Click on a chart
   - **Expected**: Either drill-down is disabled, OR drilled data shows no names

#### Test 6: Cross-School Access Prevention

1. **Login as**: `principal.lincoln@district.local` (Lincoln High principal)
2. **Attempt to bypass filter**:
   - Manually modify URL parameter:
     ```
     http://localhost:3000/dashboard/1?school=Washington+High+School
     ```
   - OR try to modify dashboard filter to select Washington High
3. **Expected Result**:
   - Either: No data returned (RLS blocks it)
   - OR: Error message: "You don't have access to this data"
   - **MUST NOT**: Show Washington High data

#### Test 7: Session Timeout

1. **Login as any user**
2. **Wait**: 30 minutes without activity
3. **Attempt to click**: Any dashboard or page
4. **Expected**: Redirected to login page with "Session expired" message

**Testing Checklist**:
- [ ] Administrator: Full access verified
- [ ] Principal: School filter working, names hidden
- [ ] Counselor: Grade filter working, names visible
- [ ] Teacher: Class filter working, own classes only
- [ ] Board: Aggregated data only, no names
- [ ] Cross-school access prevented
- [ ] Session timeout working

---

### Step 9: Document Configuration (30 minutes)

**Objective**: Create reference document of all access control settings

Create file: `oss_framework/deployment/metabase/access-control-configuration.md`

**Template**:
```markdown
# OSS Analytics - Access Control Configuration

**Configured Date**: [Date]
**Configured By**: [Name]
**Metabase Version**: [Version]
**Last Reviewed**: [Date]

## User Groups

| Group Name | Member Count | Purpose |
|------------|--------------|---------|
| Administrators | 2 | Full system access |
| Principals | 4 | School-level access |
| Counselors | 8 | Grade-level wellbeing access |
| Teachers | 45 | Class-level access |
| Board_Members | 5 | Aggregated district access |

## User Attributes

| Attribute | Type | Purpose | Example |
|-----------|------|---------|---------|
| school | Text | Filter data to user's school | Lincoln High School |
| grade_levels | Text | Filter data to assigned grades | 9,10 |
| teacher_id | Text | Filter data to teacher's classes | TEACHER_ABC123_HASH |

## User Account Examples

| User | Group | School | Grade Levels | Teacher ID |
|------|-------|--------|--------------|-----------|
| superintendent@... | Administrators | (all) | (all) | - |
| principal.lincoln@... | Principals | Lincoln High | 9,10,11,12 | - |
| counselor.lincoln.9@... | Counselors | Lincoln High | 9,10 | - |
| teacher.math.101@... | Teachers | Lincoln High | 9,10,11,12 | TEACHER_MATH_101_HASH |
| boardmember1@... | Board_Members | (all) | (all) | - |

## Dashboard Permissions

| Dashboard | Administrators | Principals | Counselors | Teachers | Board |
|-----------|----------------|-----------|-----------|----------|-------|
| Dashboard 1: Absenteeism | ✅ Edit | ✅ View | ❌ | ❌ | ✅ View |
| Dashboard 2: Wellbeing | ✅ Edit | ✅ View | ✅ View | ❌ | ❌ |
| Dashboard 3: Equity | ✅ Edit | ✅ View | ✅ View | ❌ | ✅ View |
| Dashboard 4: Class Effectiveness | ✅ Edit | ✅ View | ❌ | ✅ View | ❌ |
| Dashboard 5: Correlations | ✅ Edit | ✅ View | ❌ | ❌ | ✅ View |

## Row-Level Security Filters

### Principals
- Filter: `primary_school = {{school}}`
- Applied to: All 5 dashboards

### Counselors
- Filter: `primary_school = {{school}} AND grade_level IN ({{grade_levels}})`
- Applied to: Dashboards 2, 3

### Teachers
- Filter: `teacher_id_hash = {{teacher_id}}`
- Applied to: Dashboard 4

### Board Members
- Filter: Aggregated views only (no RLS, data masked at field level)
- Applied to: Dashboards 1, 3, 5

## Field Visibility

| Field | Visible To | Hidden From | Reason |
|-------|-----------|-------------|--------|
| student_name_display | Admins, Counselors | Principals, Teachers, Board | FERPA compliance |
| student_id_hash | Admins, Principals, Counselors | Teachers, Board | Privacy |
| teacher_name | Admins, Principals, Teachers | Counselors, Board | Personnel privacy |
| date_of_birth | Admins, Counselors | All others | Sensitive PII |

## Session Settings

- **Timeout**: 30 minutes of inactivity
- **Password Policy**: 12+ chars, complexity required, 90-day expiration
- **MFA**: Enabled for Administrators
- **SSO**: [Configured/Not configured]
- **Audit Logging**: [Enabled/Disabled]

## Testing Results

- ✅ All 5 user roles tested
- ✅ RLS filters verified working
- ✅ Field masking verified
- ✅ Session timeout verified
- ✅ Export restrictions verified
- ✅ Cross-school access prevented

**Testing Date**: [Date]
**Tested By**: [Name]

## Maintenance Schedule

- **Daily**: Monitor audit logs for suspicious activity
- **Weekly**: Review failed login attempts
- **Monthly**: Review user access (remove inactive accounts)
- **Quarterly**: Re-test access controls with sample users
- **Annually**: Full security audit

**Next Review Date**: [Date + 90 days]
```

Save this document and keep it updated as you make changes to permissions.

**Success Criteria**:
- ✅ Configuration document created
- ✅ All settings documented
- ✅ Testing results recorded
- ✅ Maintenance schedule defined

---

## Row-Level Security (RLS) Details

### Understanding RLS in Metabase

**What is RLS?**
- Row-Level Security filters which data rows users can see
- Unlike column-level security (hiding fields), RLS controls access to specific records
- Example: Principal at Lincoln High can only query students at Lincoln High

**Why RLS Matters**:
- **Data Privacy**: Users can't access data outside their authorization
- **FERPA Compliance**: Students' information protected by school/grade filters
- **Audit Trail**: System logs show which user accessed what data

### RLS Implementation Methods

**Method 1: User Attributes + Data Sandboxing** (✅ RECOMMENDED)
- Define user metadata (school, grade, teacher ID)
- Metabase auto-injects filters into queries
- Most flexible and maintainable
- **Pros**: Scalable, centrally managed, easy to update
- **Cons**: Requires Metabase setup (not database-level)

**Method 2: Separate Dashboards per User** (❌ NOT RECOMMENDED)
- Create individual dashboards with hard-coded filters for each user
- **Pros**: Simple concept
- **Cons**: Not scalable (100 users = 100 dashboards), hard to maintain

**Method 3: Database-Level RLS** (❌ NOT AVAILABLE)
- Implement RLS in database itself (e.g., PostgreSQL RLS policies)
- **Pros**: Security enforced at database layer
- **Cons**: SQLite/DuckDB don't support native RLS

### RLS Testing Best Practices

**Test Coverage**:
- ✅ Test each role with sample user
- ✅ Verify filters apply automatically
- ✅ Attempt to bypass filters (should fail)
- ✅ Test with production-like data volume
- ✅ Verify performance (RLS shouldn't slow queries significantly)

**Common Bypass Attempts to Test**:
1. **URL parameter manipulation**: Change `?school=Lincoln` to `?school=Washington`
2. **Dashboard filter modification**: Try to change locked filters
3. **SQL injection**: Attempt SQL in text fields (should be sanitized)
4. **API access**: Try to query API directly without UI (should require auth)

**If Bypass Succeeds**:
- **Immediate action**: Disable affected user accounts
- **Root cause**: Likely filter not locked or sandbox not applied
- **Fix**: Review Step 5.3 (Data Sandboxing) and Step 5.4 (Dashboard Filters)

---

## Testing & Verification

### Pre-Production Testing Checklist

Before rolling out to all staff:

- [ ] **Functional Testing**: All 5 roles tested with sample users
- [ ] **RLS Verification**: Data filters confirmed working
- [ ] **Field Masking**: Sensitive fields hidden from unauthorized users
- [ ] **Export Restrictions**: CSV/PDF limits enforced
- [ ] **Session Timeout**: 30-minute timeout verified
- [ ] **Cross-School Access**: Bypass attempts fail
- [ ] **Performance**: Queries complete in <5 seconds
- [ ] **Audit Logging**: User actions logged correctly

### Production Testing Schedule

**Week 1: Pilot Group**
- Select 5-10 users (1-2 from each role)
- Grant access to production system
- Monitor usage daily
- Collect feedback via survey

**Week 2: Department Rollout**
- Expand to all administrators and principals
- Continue monitoring
- Address any issues immediately

**Week 3: Full Rollout**
- Grant access to all staff
- Provide training sessions
- Ongoing support via helpdesk

**Month 2: Post-Launch Review**
- Review audit logs for anomalies
- Survey user satisfaction
- Identify areas for improvement

---

## Troubleshooting

### Issue: User Can See Other Schools' Data

**Symptoms**: Principal at Lincoln High sees Washington High data

**Diagnostic Steps**:
1. Verify user attribute set correctly:
   - Admin → People → Select user → Check `school` attribute value
2. Verify sandbox applied to table:
   - Admin → Permissions → Data → Check table has "Sandboxed" (not "Unrestricted")
3. Test query directly:
   ```sql
   SELECT DISTINCT primary_school FROM v_chronic_absenteeism_risk;
   ```
   - Should return ONLY their school

**Solutions**:
- **Fix user attribute**: Set correct school name (match exactly as in database)
- **Re-apply sandbox**: Remove sandbox, save, then re-add with correct filter
- **Verify dashboard filters locked**: Edit dashboard, ensure filters are "Locked" ✅

---

### Issue: Counselor Cannot See Student Names

**Symptoms**: Counselor sees `[Redacted]` instead of student names

**Diagnostic Steps**:
1. Check field visibility:
   - Admin → Data Model → `v_wellbeing_risk_profiles` → `student_name_display`
   - Check if Counselors group has "Visible" permission
2. Check dashboard question:
   - Open Dashboard 2, edit a question
   - Verify `student_name_display` field is included in query

**Solutions**:
- **Set field visible**: Data Model → Field → Counselors → **Visible**
- **Add field to query**: Edit question, add `student_name_display` column
- **Refresh browser**: Clear cache, log out/in

---

### Issue: Session Timeout Not Working

**Symptoms**: Users stay logged in indefinitely

**Diagnostic Steps**:
1. Check session timeout setting:
   - Admin → Settings → Authentication → **"Session timeout"**
2. Verify value is numeric (e.g., `30` for 30 minutes)
3. Check Metabase logs for errors:
   ```bash
   docker logs oss-metabase | grep -i session
   ```

**Solutions**:
- **Set timeout value**: Enter `30` in session timeout field, click Save
- **Restart Metabase**: `docker-compose restart` (settings take effect after restart)
- **Clear browser cookies**: Users should clear cookies and log in again

---

### Issue: RLS Filter Can Be Bypassed via URL

**Symptoms**: User modifies URL parameter to see unauthorized data

**Example**:
```
http://localhost:3000/dashboard/1?school=Washington+High+School
```

**Root Cause**: Dashboard filter not locked or sandbox not applied

**Solutions**:
1. **Lock dashboard filters**:
   - Edit dashboard
   - Click filter settings
   - Enable **"Locked"** ✅ (users cannot modify)
2. **Use saved questions** (not ad-hoc queries):
   - Saved questions apply sandbox at query execution time
   - Users cannot modify underlying SQL
3. **Verify sandbox applied**:
   - Admin → Permissions → Data → Verify "Sandboxed" (not "Unrestricted")

---

### Issue: Board Members Can Drill Down to Student Names

**Symptoms**: Board member clicks chart and sees individual student records

**Root Cause**: Dashboard allows drill-down to underlying data

**Solutions**:
1. **Disable drill-down on charts**:
   - Edit dashboard
   - For each chart → Settings → **"Click behavior"** → **"Disabled"**
2. **Use aggregated-only views**:
   - Create separate database view: `v_absenteeism_aggregated`
   - No student-level records, only totals/averages
   - Point Board Member dashboards to this view instead
3. **Remove student name field from underlying questions**:
   - Edit each question on board dashboards
   - Remove `student_name_display` from SELECT clause

---

### Issue: Teacher Cannot Access Dashboard 4

**Symptoms**: Teacher logs in but Dashboard 4 not visible

**Diagnostic Steps**:
1. Verify user assigned to Teachers group:
   - Admin → People → Select user → Check "Groups" assignment
2. Verify Teachers group has access to collection:
   - Collections → Teacher Dashboards → Edit permissions
   - Check Teachers group has "View" permission
3. Verify Dashboard 4 is in correct collection:
   - Open Dashboard 4
   - Check "Collection" shown at top
   - Should be in "Teacher Dashboards" collection

**Solutions**:
- **Add user to group**: Admin → People → User → Add to "Teachers" group
- **Grant collection access**: Collections → Edit permissions → Teachers → **View**
- **Move dashboard**: Dashboard 4 → "..." → Move to "Teacher Dashboards" collection

---

### Issue: Export Button Missing for Non-Admins

**Symptoms**: Users cannot find export button on dashboards

**Diagnostic Steps**:
1. Check Metabase version (some versions restrict export by default)
2. Check group permissions:
   - Admin → Permissions → Collection → Verify group can "View" (not just "No access")
3. Check if dashboard is in personal collection (cannot share/export personal dashboards)

**Solutions**:
- **Upgrade Metabase**: Newer versions have better export controls
- **Grant view permission**: Collections → Edit permissions → Group → **View**
- **Move to shared collection**: Dashboard → Move to "OSS Analytics" collection

---

## FERPA Compliance Checklist

**FERPA** (Family Educational Rights and Privacy Act) protects student education records. Use this checklist to ensure compliance:

### Access Controls
- [ ] **Need-to-know basis**: Users only see data required for their job function
- [ ] **Student names restricted**: Only counselors (case management) see names
- [ ] **Board members see aggregated data**: No individual student records
- [ ] **Teachers see own classes only**: Cannot access other students' data

### Data Security
- [ ] **Session timeout enabled**: 30 minutes of inactivity
- [ ] **Strong passwords required**: 12+ characters, complexity enforced
- [ ] **MFA enabled for admins**: Multi-factor authentication protects privileged accounts
- [ ] **HTTPS enabled** (if accessible outside localhost): Encrypted connections only

### Audit & Monitoring
- [ ] **Audit logs enabled**: Track who accessed what data
- [ ] **Monthly log reviews**: Check for unusual access patterns
- [ ] **User access reviews**: Remove inactive accounts quarterly
- [ ] **Incident response plan**: Document steps if data breach occurs

### Data Exports
- [ ] **Export restrictions**: Counselors/teachers limited to their authorized students
- [ ] **Board members PDF only**: No raw data exports
- [ ] **Export logging**: Track all data exports in audit log
- [ ] **Training provided**: Users understand FERPA obligations before accessing data

### Training & Policies
- [ ] **FERPA training completed**: All users trained before access granted
- [ ] **Acceptable use policy signed**: Users agree to data protection policies
- [ ] **Annual refresher training**: Remind users of FERPA obligations yearly
- [ ] **Consequences documented**: Clear penalties for unauthorized access/sharing

### Technical Safeguards
- [ ] **Data encrypted at rest**: Database files protected
- [ ] **Backups encrypted**: Backup files also protected
- [ ] **No external sharing**: Metabase not exposed to internet (localhost only)
- [ ] **Secure disposal**: Old backups securely deleted

**FERPA Compliance Status**: [ ] Verified | [ ] Needs Work

**Last FERPA Review Date**: _______________

---

## Maintenance & Audit

### Daily Tasks

**Monitor Audit Logs** (5 minutes)
- Review recent user logins
- Check for failed login attempts (>3 failures = investigate)
- Verify no unusual export activity

**Check System Health** (5 minutes)
- Verify Metabase container running: `docker ps | grep oss-metabase`
- Check response time: `curl -w "@time_total:  %{time_total}\n" http://localhost:3000/api/health`
- Expected: <500ms response time

---

### Weekly Tasks

**User Access Review** (15 minutes)
- Check for new staff requiring accounts
- Verify recent hires assigned correct groups and attributes
- Remove accounts for departed staff (offboarding)

**Failed Login Report** (10 minutes)
```sql
-- If Metabase has audit log table, query for failed logins
SELECT user_email, COUNT(*) as failed_attempts, MAX(timestamp) as last_attempt
FROM audit_log
WHERE event_type = 'login_failed'
  AND timestamp >= NOW() - INTERVAL '7 days'
GROUP BY user_email
HAVING COUNT(*) >= 3
ORDER BY failed_attempts DESC;
```

**Action**: Investigate users with 3+ failed attempts (possible brute force)

---

### Monthly Tasks

**Comprehensive Access Audit** (1 hour)
- Review all user accounts:
  - [ ] Any inactive accounts? (no login in 30+ days) → Disable
  - [ ] Any shared accounts? (multiple people using one login) → Create individual accounts
  - [ ] Any privilege creep? (users with more access than needed) → Downgrade
- Review group memberships:
  - [ ] Staff changes? (principal moved schools) → Update user attributes
  - [ ] Role changes? (counselor became principal) → Change group assignment
- Review dashboard access:
  - [ ] New dashboards created? → Set permissions
  - [ ] Old dashboards unused? → Archive or delete

**Export Activity Report** (30 minutes)
```sql
-- Query for large data exports
SELECT user_email, dashboard_name, export_format, row_count, timestamp
FROM audit_log
WHERE event_type = 'export'
  AND timestamp >= NOW() - INTERVAL '30 days'
  AND row_count > 100  -- Flag exports of >100 records
ORDER BY row_count DESC;
```

**Action**: Review large exports, verify they're legitimate (not data exfiltration)

**Performance Review** (30 minutes)
- Check slow queries:
  - Queries taking >5 seconds → Optimize or add indexes
- Check dashboard load times:
  - Dashboards loading slowly → Simplify visualizations or pre-aggregate data

---

### Quarterly Tasks

**Full Access Control Re-Test** (2 hours)
- Re-run all tests from Step 8 (Verify Access Controls)
- Log in as test user from each role
- Verify RLS filters still working correctly
- Attempt bypass techniques (should all fail)

**FERPA Compliance Review** (1 hour)
- Re-review FERPA Compliance Checklist (above)
- Update documentation with any changes
- Confirm all staff completed annual FERPA training

**Security Patch Check** (30 minutes)
- Check for Metabase updates:
  ```bash
  docker pull metabase/metabase:latest
  docker-compose up -d  # Recreate with new image
  ```
- Review Metabase security advisories: https://github.com/metabase/metabase/security
- Test system after update (verify dashboards still work)

---

### Annual Tasks

**Comprehensive Security Audit** (4 hours)
- External security review (if budget allows)
- Penetration testing (attempt to breach access controls)
- Review all settings from this guide (Steps 1-9)
- Update documentation with any changes

**Disaster Recovery Test** (2 hours)
- Simulate server failure
- Restore Metabase from backup
- Verify all settings, users, dashboards intact
- Document recovery time

---

## Summary

Congratulations! If you've completed all steps in this guide, your Metabase deployment now has:

✅ **5 user groups** with appropriate permissions
✅ **Row-Level Security** filtering data by school/grade/class  
✅ **Field masking** hiding sensitive information
✅ **Session timeout** auto-logging out inactive users  
✅ **Tested access controls** verified with sample users from each role  
✅ **Documentation** of all configuration settings  
✅ **FERPA compliance** checklist completed  
✅ **Maintenance plan** for ongoing security

### Next Steps

1. **Train End Users** (Task 4.10):
   - Provide role-specific training guides (see `training/` folder)
   - Conduct live training sessions
   - Emphasize FERPA compliance

2. **Conduct UAT** (Task 4.08):
   - Schedule testing sessions with real users
   - Use UAT checklists in `uat/` folder
   - Address feedback before full rollout

3. **Production Deployment** (Task 4.09):
   - Follow deployment guide
   - Schedule launch communications
   - Provide ongoing support

### Getting Help

**Common Questions**:
- See `faq.md` in training materials
- See `troubleshooting-guide.md` for technical issues

**Support Contacts**:
- Technical issues: analytics@district.edu
- FERPA questions: privacy-officer@district.edu
- User account requests: helpdesk@district.edu

---

**Document Version**: 1.0  
**Last Updated**: January 27, 2026  
**Prepared By**: OSS Framework Development Team  
**Next Review Date**: April 27, 2026 (90 days)

---

*For additional information about OSS Analytics, see the main README in `/oss_framework/deployment/metabase/README.md`*
