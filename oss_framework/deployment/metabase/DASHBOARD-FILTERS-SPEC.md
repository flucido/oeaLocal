# Dashboard Parameterized Filters - Implementation Specification

**Status**: Ready for Implementation  
**Date**: January 29, 2026  
**Context**: Dashboards created (IDs 32-36), filters need to be added

---

## Overview

All 5 dashboards have been created successfully but lack parameterized filters for user interactivity. This document specifies the exact filters needed for each dashboard to enable:
- School-level filtering
- Grade-level filtering
- Time range selection
- Row limit controls
- FERPA-compliant minimum cohort size

---

## Implementation Approach

### Option 1: Metabase API (Recommended)

Extend `create-dashboards-api.py` with filter methods:

```python
def add_dashboard_parameter(
    self,
    dashboard_id: int,
    parameter_type: str,  # "string/=", "number/=", "date/range"
    name: str,
    slug: str,
    default: Any = None
) -> Optional[str]:
    """Add a parameter to a dashboard"""
    
def link_card_to_parameter(
    self,
    dashboard_id: int,
    card_id: int,
    parameter_id: str,
    target: Dict  # Field mapping
) -> bool:
    """Link a dashboard card to a parameter"""
```

### Option 2: Manual (via UI)

1. Open http://localhost:3000
2. Navigate to dashboard
3. Click "⚙️" → "Add a Filter"
4. Select filter type
5. Configure options
6. Connect to questions
7. Save

---

## Dashboard 1: Chronic Absenteeism Risk (ID: 32)

### Filters Required

#### Filter 1: School Selection
- **Type**: `string/=` (dropdown)
- **Name**: "School"
- **Slug**: `school_filter`
- **Options**: Query schools from `dim_schools.school_name`
- **Default**: "All Schools"
- **SQL Variable**: `{{school_filter}}`
- **Connected Questions**: All (IDs 49-53)

#### Filter 2: Grade Level
- **Type**: `string/=` (dropdown)
- **Name**: "Grade Level"
- **Slug**: `grade_filter`
- **Options**: [9, 10, 11, 12, "All Grades"]
- **Default**: "All Grades"
- **SQL Variable**: `{{grade_filter}}`
- **Connected Questions**: All (IDs 49-53)

#### Filter 3: Risk Level
- **Type**: `string/=` (dropdown, multi-select)
- **Name**: "Risk Level"
- **Slug**: `risk_filter`
- **Options**: ["Critical", "High", "Medium", "Low", "All"]
- **Default**: "All"
- **SQL Variable**: `{{risk_filter}}`
- **Connected Questions**: 49, 52, 53

#### Filter 4: Row Limit (for Table)
- **Type**: `number/=`
- **Name**: "Number of Students"
- **Slug**: `row_limit`
- **Options**: [10, 20, 50, 100, 500]
- **Default**: 50
- **SQL Variable**: `{{row_limit}}`
- **Connected Questions**: 52 (Top 20 At-Risk Students)

### SQL Modifications

**Current Query (Question 52 - Top 20 At-Risk Students):**
```sql
SELECT 
    student_key,
    grade_level,
    attendance_rate_30d,
    risk_score,
    primary_school
FROM main_main_analytics.v_chronic_absenteeism_risk
ORDER BY risk_score DESC
LIMIT 20
```

**Modified Query with Filters:**
```sql
SELECT 
    student_key,
    grade_level,
    attendance_rate_30d,
    risk_score,
    primary_school
FROM main_main_analytics.v_chronic_absenteeism_risk
WHERE 1=1
    [[AND primary_school = {{school_filter}}]]
    [[AND grade_level = {{grade_filter}}]]
    [[AND wellbeing_risk_level = {{risk_filter}}]]
ORDER BY risk_score DESC
LIMIT [[{{row_limit}}]]
```

**Note**: `[[ ]]` syntax is Metabase's optional parameter syntax (filters are applied only if parameter is set).

---

## Dashboard 2: Student Wellbeing Risk Profiles (ID: 33)

### Filters Required

#### Filter 1: School Selection
- **Type**: `string/=` (dropdown)
- **Name**: "School"
- **Slug**: `school_filter`
- **Options**: Query from `dim_schools`
- **Default**: "All Schools"
- **Connected Questions**: All (IDs 54-55)

#### Filter 2: Grade Level
- **Type**: `string/=` (dropdown)
- **Name**: "Grade Level"
- **Slug**: `grade_filter`
- **Options**: [9, 10, 11, 12, "All Grades"]
- **Default**: "All Grades"
- **Connected Questions**: All (IDs 54-55)

#### Filter 3: Wellbeing Level
- **Type**: `string/=` (dropdown, multi-select)
- **Name**: "Wellbeing Level"
- **Slug**: `wellbeing_filter`
- **Options**: ["Critical", "High", "Moderate", "Low", "All"]
- **Default**: "All"
- **Connected Questions**: 54, 55

#### Filter 4: Primary Concern
- **Type**: `string/=` (dropdown)
- **Name**: "Primary Concern"
- **Slug**: `concern_filter`
- **Options**: ["Multi-factor", "Attendance", "Behavior", "Academic", "All"]
- **Default**: "All"
- **Connected Questions**: 54

### SQL Modifications

**Question 54 - Students by Wellbeing Level (Modified):**
```sql
SELECT 
    student_key,
    grade_level,
    school_id,
    attendance_risk,
    discipline_risk,
    academic_risk,
    compound_risk,
    primary_concern,
    recommended_action
FROM main_main_analytics.v_wellbeing_risk_profiles
WHERE 1=1
    [[AND school_id = {{school_filter}}]]
    [[AND grade_level = {{grade_filter}}]]
    [[AND wellbeing_level = {{wellbeing_filter}}]]
    [[AND primary_concern = {{concern_filter}}]]
ORDER BY compound_risk DESC
```

---

## Dashboard 3: Equity Outcomes Analysis (ID: 34)

### Filters Required

#### Filter 1: School Selection
- **Type**: `string/=` (dropdown)
- **Name**: "School"
- **Slug**: `school_filter`
- **Options**: Query from `dim_schools`
- **Default**: "All Schools"
- **Connected Questions**: All (IDs 56-57)

#### Filter 2: Grade Level
- **Type**: `string/=` (dropdown)
- **Name**: "Grade Level"
- **Slug**: `grade_filter`
- **Options**: [9, 10, 11, 12, "All Grades"]
- **Default**: "All Grades"
- **Connected Questions**: All (IDs 56-57)

#### Filter 3: Demographic Category
- **Type**: `string/=` (dropdown)
- **Name**: "Demographic Dimension"
- **Slug**: `demographic_filter`
- **Options**: ["Race/Ethnicity", "English Learner", "Special Education", "Free/Reduced Lunch", "Gender", "All"]
- **Default**: "Race/Ethnicity"
- **Connected Questions**: 56, 57

#### Filter 4: Minimum Student Count (FERPA)
- **Type**: `number/=`
- **Name**: "Min Students (FERPA)"
- **Slug**: `min_students`
- **Options**: [5, 10, 15, 20]
- **Default**: 5
- **SQL Variable**: `{{min_students}}`
- **Connected Questions**: 56, 57
- **Purpose**: Enforce k-anonymity (FERPA compliance)

### SQL Modifications

**Question 56 - Attendance Rate by Demographic (Modified):**
```sql
SELECT 
    demographic_group,
    cohort_size,
    pct_good_attendance,
    avg_gpa,
    pct_college_ready,
    disparity_from_average
FROM main_main_analytics.v_equity_outcomes_by_demographics
WHERE 1=1
    [[AND cohort_size >= {{min_students}}]]
    [[AND demographic_category = {{demographic_filter}}]]
ORDER BY pct_good_attendance DESC
```

**Note**: The view `v_equity_outcomes_by_demographics` already aggregates by demographics. Filter applies post-aggregation.

---

## Dashboard 4: Class Effectiveness Comparison (ID: 35)

### Filters Required

#### Filter 1: School Selection
- **Type**: `string/=` (dropdown)
- **Name**: "School"
- **Slug**: `school_filter`
- **Options**: Query from `dim_schools`
- **Default**: "All Schools"
- **Connected Questions**: 58

#### Filter 2: Subject Area
- **Type**: `string/=` (dropdown)
- **Name**: "Subject Area"
- **Slug**: `subject_filter`
- **Options**: ["Math", "English", "Science", "Social Studies", "All"]
- **Default**: "All"
- **Connected Questions**: 58

#### Filter 3: Grade Level
- **Type**: `string/=` (dropdown)
- **Name**: "Grade Level"
- **Slug**: `grade_filter`
- **Options**: [9, 10, 11, 12, "All Grades"]
- **Default**: "All Grades"
- **Connected Questions**: 58

#### Filter 4: Effectiveness Rating
- **Type**: `string/=` (dropdown, multi-select)
- **Name**: "Effectiveness Rating"
- **Slug**: `effectiveness_filter`
- **Options**: ["Highly Effective", "Effective", "Adequate", "Needs Improvement", "All"]
- **Default**: "All"
- **Connected Questions**: 58

### SQL Modifications

**Question 58 - Class Section Performance (Modified):**
```sql
SELECT 
    course_name,
    teacher_id_hash,
    section_name,
    enrollment_count,
    pct_passed,
    avg_grade,
    effectiveness_rating,
    comparison_to_course_avg
FROM main_main_analytics.v_class_section_comparison
WHERE 1=1
    [[AND school_id = {{school_filter}}]]
    [[AND subject_area = {{subject_filter}}]]
    [[AND grade_level = {{grade_filter}}]]
    [[AND effectiveness_rating = {{effectiveness_filter}}]]
ORDER BY pct_passed DESC
```

---

## Dashboard 5: Performance Correlations (ID: 36)

### Filters Required

#### Filter 1: School Selection
- **Type**: `string/=` (dropdown)
- **Name**: "School"
- **Slug**: `school_filter`
- **Options**: Query from `dim_schools`
- **Default**: "All Schools"
- **Connected Questions**: 59

#### Filter 2: Time Period
- **Type**: `string/=` (dropdown)
- **Name**: "Time Period"
- **Slug**: `timeframe_filter`
- **Options**: ["Current Month", "Current Term", "Year-to-Date", "All Time"]
- **Default**: "Year-to-Date"
- **Connected Questions**: 59

#### Filter 3: Grade Level
- **Type**: `string/=` (dropdown)
- **Name**: "Grade Level"
- **Slug**: `grade_filter`
- **Options**: [9, 10, 11, 12, "All Grades"]
- **Default**: "All Grades"
- **Connected Questions**: 59

### SQL Modifications

**Question 59 - Performance Correlations (Modified):**
```sql
SELECT 
    correlation_name,
    correlation_value,
    strength,
    direction,
    sample_size,
    interpretation
FROM main_main_analytics.v_performance_correlations
WHERE 1=1
    [[AND school_id = {{school_filter}}]]
    [[AND timeframe = {{timeframe_filter}}]]
    [[AND grade_level = {{grade_filter}}]]
ORDER BY ABS(correlation_value) DESC
```

**Note**: The correlation view currently returns aggregate values. May need to recompute correlations per filter if school/grade filtering is required at computation level (not post-aggregation).

---

## Implementation Script Enhancement

### New Methods for `create-dashboards-api.py`

```python
def add_dashboard_parameter(
    self,
    dashboard_id: int,
    parameter_type: str,
    name: str,
    slug: str,
    default: Any = None,
    values_source_type: str = "static",
    values_source_config: Optional[Dict] = None
) -> Optional[str]:
    """
    Add a parameter (filter) to a dashboard.
    
    Args:
        dashboard_id: Dashboard ID
        parameter_type: Type of parameter (e.g., "string/=", "number/=", "date/range")
        name: Display name
        slug: URL-safe identifier
        default: Default value
        values_source_type: "static" (hardcoded) or "card" (query-based)
        values_source_config: For query-based filters, specify card_id and value_field
    
    Returns:
        Parameter ID if successful, None otherwise
    """
    # Get current dashboard
    response = requests.get(
        f"{self.api_url}/dashboard/{dashboard_id}",
        headers=self.headers,
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"    ❌ Failed to get dashboard: {response.status_code}")
        return None
    
    dashboard_data = response.json()
    parameters = dashboard_data.get("parameters", [])
    
    # Create new parameter
    new_parameter = {
        "id": slug,
        "name": name,
        "slug": slug,
        "type": parameter_type,
        "default": default,
        "values_source_type": values_source_type
    }
    
    if values_source_config:
        new_parameter["values_source_config"] = values_source_config
    
    parameters.append(new_parameter)
    
    # Update dashboard with new parameter
    update_response = requests.put(
        f"{self.api_url}/dashboard/{dashboard_id}",
        headers=self.headers,
        json={"parameters": parameters},
        timeout=10
    )
    
    if update_response.status_code == 200:
        print(f"    ✅ Added parameter: {name}")
        return slug
    else:
        print(f"    ❌ Failed to add parameter: {update_response.status_code}")
        return None


def link_card_to_parameter(
    self,
    dashboard_id: int,
    card_id: int,
    parameter_id: str,
    target_field: List[str]  # e.g., ["dimension", ["field", 123, None]]
) -> bool:
    """
    Link a dashboard card (question) to a parameter.
    
    Args:
        dashboard_id: Dashboard ID
        card_id: Question/card ID
        parameter_id: Parameter slug
        target_field: Field mapping (Metabase field reference format)
    
    Returns:
        True if successful, False otherwise
    """
    # Get dashboard
    response = requests.get(
        f"{self.api_url}/dashboard/{dashboard_id}",
        headers=self.headers,
        timeout=10
    )
    
    if response.status_code != 200:
        return False
    
    dashboard_data = response.json()
    dashcards = dashboard_data.get("dashcards", [])
    
    # Find the dashcard with this card_id
    for dashcard in dashcards:
        if dashcard["card_id"] == card_id:
            # Add parameter mapping
            if "parameter_mappings" not in dashcard:
                dashcard["parameter_mappings"] = []
            
            dashcard["parameter_mappings"].append({
                "parameter_id": parameter_id,
                "card_id": card_id,
                "target": target_field
            })
    
    # Update dashboard
    update_response = requests.put(
        f"{self.api_url}/dashboard/{dashboard_id}",
        headers=self.headers,
        json={"dashcards": dashcards},
        timeout=10
    )
    
    return update_response.status_code == 200
```

### Usage Example

```python
# Add school filter to Dashboard 1
client.add_dashboard_parameter(
    dashboard_id=32,
    parameter_type="string/=",
    name="School",
    slug="school_filter",
    default="All Schools",
    values_source_type="card",
    values_source_config={
        "card_id": 99,  # Query that returns school names
        "value_field": ["field", "school_name", None]
    }
)

# Link filter to all questions in Dashboard 1
for question_id in [49, 50, 51, 52, 53]:
    client.link_card_to_parameter(
        dashboard_id=32,
        card_id=question_id,
        parameter_id="school_filter",
        target_field=["dimension", ["field", "primary_school", None]]
    )
```

---

## Verification Checklist

After adding filters, verify each dashboard:

### Dashboard 1: Chronic Absenteeism Risk
- [ ] School dropdown shows all schools from database
- [ ] Grade dropdown shows grades 9-12
- [ ] Risk level multi-select shows all 4 levels
- [ ] Row limit slider works (10-500)
- [ ] All 5 visualizations respond to filters
- [ ] "All Schools" shows full dataset (3,400 students)
- [ ] Selecting specific school reduces dataset appropriately

### Dashboard 2: Wellbeing Risk
- [ ] School filter works
- [ ] Grade filter works
- [ ] Wellbeing level filter shows Critical/High/Moderate/Low
- [ ] Primary concern filter shows 4 categories
- [ ] Both visualizations respond to filters

### Dashboard 3: Equity Outcomes
- [ ] School filter works
- [ ] Grade filter works
- [ ] Demographic dimension dropdown shows 5 categories
- [ ] Minimum student count enforces FERPA (default 5)
- [ ] Cohorts below minimum are hidden
- [ ] Both visualizations respond to filters

### Dashboard 4: Class Effectiveness
- [ ] School filter works
- [ ] Subject area dropdown shows 4 subjects
- [ ] Grade filter works
- [ ] Effectiveness rating multi-select shows 4 levels
- [ ] Table responds to all filters

### Dashboard 5: Performance Correlations
- [ ] School filter works
- [ ] Time period dropdown shows 4 options
- [ ] Grade filter works
- [ ] Correlation table responds to filters
- [ ] Sample sizes recalculate per filter

---

## Next Steps

1. **Extend Script**: Add `add_dashboard_parameter()` and `link_card_to_parameter()` methods
2. **Run Script**: Execute enhanced script to add filters to all 5 dashboards
3. **Verify**: Test each dashboard filter interactively
4. **Document**: Update verification checklist with actual results
5. **Close Beads**: Mark filter tasks complete

---

**Estimated Implementation Time**: 3-4 hours (scripted) or 1-2 hours (manual via UI)

**Dependencies**: Metabase must be running at http://localhost:3000 with dashboards IDs 32-36 already created.
