#!/usr/bin/env python3
"""
Complete 5-Year Enrollment & Performance Analysis
Integrates Excel enrollment data with CSV grade data via student ID mapping

Usage: python3 analyze_with_grades.py
"""

import pandas as pd
import numpy as np
import glob
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION
# ============================================================================

COURSE_308 = 308  # Algebra 1
COURSE_325 = 325  # Regular Math 8
COURSE_329 = 329  # Apex Math 8
COURSE_1205 = 1205  # LEAD Program

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def standardize_academic_year(year_value):
    """Convert various Academic Year formats to standard 'YY-YY' format."""
    if pd.isna(year_value):
        return None

    year_str = str(year_value)

    # Already in YY-YY format
    if "-" in year_str and len(year_str) <= 5:
        return year_str

    # Timestamp format: '2021-08-20'
    if len(year_str) == 10 and year_str.count("-") == 2:
        try:
            date = pd.to_datetime(year_str)
            if date.month >= 8:  # Fall semester
                start_year = date.year
            else:  # Spring semester
                start_year = date.year - 1
            end_year = start_year + 1
            return f"{start_year % 100:02d}-{end_year % 100:02d}"
        except:
            pass

    # YYYY-YYYY format: '2022-2023'
    if len(year_str) == 9 and "-" in year_str:
        start_year = int(year_str[:4])
        end_year = int(year_str[5:9])
        return f"{start_year % 100:02d}-{end_year % 100:02d}"

    return year_str


def load_excel_enrollment(file_path, sheet_name="Master Data"):
    """Load and standardize Excel enrollment file."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Standardize column names
    df.columns = df.columns.str.strip()
    if "Academic year" in df.columns:
        df = df.rename(columns={"Academic year": "Academic Year"})

    # Standardize Academic Year
    df["Academic Year"] = df["Academic Year"].apply(standardize_academic_year)

    # Ensure Course ID is int
    df["Course ID"] = df["Course ID"].astype(int)

    # Ensure State Student ID is int
    df["State Student ID"] = df["State Student ID"].astype("int64")

    return df


def load_grade_files():
    """Load and combine all grade CSV files."""
    grade_files = sorted(glob.glob("Grade Files/grades_*.csv"))

    all_grades = []
    for file in grade_files:
        df = pd.read_csv(file)
        # Standardize academic year
        df["Academic Year"] = df["AcademicYear"].apply(standardize_academic_year)

        # Select relevant columns
        df = df[
            [
                "StudentID",
                "CourseID",
                "Academic Year",
                "MP_MarkingPeriod",
                "MP_Mark",
                "MP_Credit",
                "MP_TotalAbsences",
                "MP_TotalTardies",
                "MP_TotalDaysEnrolled",
                "MP_TotalDaysPresent",
            ]
        ]

        df = df.rename(
            columns={
                "StudentID": "local_id",
                "CourseID": "course_id",
                "MP_MarkingPeriod": "marking_period",
                "MP_Mark": "grade",
                "MP_Credit": "credit",
                "MP_TotalAbsences": "absences",
                "MP_TotalTardies": "tardies",
                "MP_TotalDaysEnrolled": "days_enrolled",
                "MP_TotalDaysPresent": "days_present",
            }
        )

        all_grades.append(df)

    combined = pd.concat(all_grades, ignore_index=True)
    return combined


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

print("=" * 80)
print("COMPLETE 5-YEAR ENROLLMENT & PERFORMANCE ANALYSIS")
print("=" * 80)

# Step 1: Load student ID mapping
print("\n[1/7] Loading student ID mapping...")
mapping = pd.read_csv("student_id_mapping.csv")
print(f"  Loaded: {len(mapping)} mappings ({mapping['local_id'].nunique()} students)")

# Step 2: Load Excel enrollment files
print("\n[2/7] Loading Excel enrollment files...")
algebra_df = load_excel_enrollment("Algebra 1A 23-26.xlsx")
print(
    f"  Algebra 1: {len(algebra_df)} records, {algebra_df['State Student ID'].nunique()} students"
)

math8_df = load_excel_enrollment("MATH 8 and Apex Data 21-26.xlsx")
print(
    f"  Math 8: {len(math8_df)} records, {math8_df['State Student ID'].nunique()} students"
)

lead_df = load_excel_enrollment("Lead 21-26.xlsx")
print(
    f"  LEAD: {len(lead_df)} records, {lead_df['State Student ID'].nunique()} students"
)

# Combine all enrollments
all_enrollments = pd.concat([algebra_df, math8_df, lead_df], ignore_index=True)
print(
    f"  Total: {len(all_enrollments)} records, {all_enrollments['State Student ID'].nunique()} unique students"
)

# Step 3: Load grade files
print("\n[3/7] Loading grade files...")
grades = load_grade_files()
print(f"  Loaded: {len(grades):,} grade records")
print(f"  Students: {grades['local_id'].nunique()}")
print(f"  Courses: {grades['course_id'].nunique()}")
print(f"  Years: {sorted(grades['Academic Year'].unique())}")

# Step 4: Join grades with mapping to add State Student IDs
print("\n[4/7] Joining grades with student ID mapping...")
grades_with_state_id = grades.merge(mapping, on="local_id", how="left")

matched = grades_with_state_id["state_id"].notna().sum()
total = len(grades_with_state_id)
print(f"  Matched: {matched:,} / {total:,} ({matched / total * 100:.1f}%)")

# Filter to only students in enrollment data
enrollment_state_ids = set(all_enrollments["State Student ID"].unique())
grades_filtered = grades_with_state_id[
    grades_with_state_id["state_id"].isin(enrollment_state_ids)
]
print(f"  Filtered to enrollment cohort: {len(grades_filtered):,} grade records")

# Step 5: Task A - 7th to 8th Grade Pipeline with Performance
print("\n[5/7] Task A: 7th → 8th Grade Math Pipeline Analysis...")

# Get 7th graders in Math 8 or Apex
seventh_graders = math8_df[math8_df["Grade"] == 7].copy()
seventh_graders["Pathway"] = seventh_graders["Course ID"].map(
    {COURSE_325: "Regular Math 8", COURSE_329: "Apex Math 8"}
)

print(f"  7th graders tracked: {len(seventh_graders)}")
print(
    f"    Regular Math 8: {len(seventh_graders[seventh_graders['Course ID'] == COURSE_325])}"
)
print(
    f"    Apex Math 8: {len(seventh_graders[seventh_graders['Course ID'] == COURSE_329])}"
)

# Find which students took Algebra in 8th grade
eighth_grade_algebra = algebra_df[
    (algebra_df["Grade"] == 8) & (algebra_df["Course ID"] == COURSE_308)
].copy()

# Match by State Student ID and academic year progression
progression_results = []
for _, student in seventh_graders.iterrows():
    state_id = student["State Student ID"]
    year_7th = student["Academic Year"]
    pathway = student["Pathway"]

    # Expected 8th grade year (next year)
    if pd.notna(year_7th):
        start_year = int(year_7th.split("-")[0])
        expected_8th_year = f"{(start_year + 1) % 100:02d}-{(start_year + 2) % 100:02d}"
    else:
        expected_8th_year = None

    # Check if student took Algebra in expected year
    took_algebra = (
        len(
            eighth_grade_algebra[
                (eighth_grade_algebra["State Student ID"] == state_id)
                & (eighth_grade_algebra["Academic Year"] == expected_8th_year)
            ]
        )
        > 0
    )

    # Get 7th grade Math performance
    math7_grades = grades_filtered[
        (grades_filtered["state_id"] == state_id)
        & (grades_filtered["Academic Year"] == year_7th)
        & (grades_filtered["course_id"].isin([COURSE_325, COURSE_329]))
    ]

    avg_7th_grade = None
    if len(math7_grades) > 0:
        # Calculate average across marking periods
        grade_map = {
            "A": 4.0,
            "A-": 3.7,
            "B+": 3.3,
            "B": 3.0,
            "B-": 2.7,
            "C+": 2.3,
            "C": 2.0,
            "C-": 1.7,
            "D+": 1.3,
            "D": 1.0,
            "D-": 0.7,
            "F": 0.0,
        }
        numeric_grades = math7_grades["grade"].map(grade_map).dropna()
        if len(numeric_grades) > 0:
            avg_7th_grade = numeric_grades.mean()

    # Get 8th grade Algebra performance if they took it
    alg_grades = None
    if took_algebra:
        alg_grade_records = grades_filtered[
            (grades_filtered["state_id"] == state_id)
            & (grades_filtered["Academic Year"] == expected_8th_year)
            & (grades_filtered["course_id"] == COURSE_308)
        ]
        if len(alg_grade_records) > 0:
            grade_map = {
                "A": 4.0,
                "A-": 3.7,
                "B+": 3.3,
                "B": 3.0,
                "B-": 2.7,
                "C+": 2.3,
                "C": 2.0,
                "C-": 1.7,
                "D+": 1.3,
                "D": 1.0,
                "D-": 0.7,
                "F": 0.0,
            }
            numeric_grades = alg_grade_records["grade"].map(grade_map).dropna()
            if len(numeric_grades) > 0:
                alg_grades = numeric_grades.mean()

    progression_results.append(
        {
            "State Student ID": state_id,
            "Sex": student.get("Sex"),
            "Race": student.get("Description_STU_RC1"),
            "Pathway": pathway,
            "7th Grade Year": year_7th,
            "7th Grade Math GPA": avg_7th_grade,
            "Took Algebra 8th": took_algebra,
            "8th Grade Algebra GPA": alg_grades,
        }
    )

progression_df = pd.DataFrame(progression_results)

# Calculate statistics
total_7th = len(progression_df)
took_algebra_count = progression_df["Took Algebra 8th"].sum()
progression_rate = took_algebra_count / total_7th * 100

print(f"\n  Overall Progression:")
print(f"    Total 7th graders: {total_7th}")
print(f"    Took 8th grade Algebra: {took_algebra_count} ({progression_rate:.1f}%)")

# By pathway
pathway_stats = (
    progression_df.groupby("Pathway")
    .agg(
        {
            "State Student ID": "count",
            "Took Algebra 8th": "sum",
            "7th Grade Math GPA": "mean",
            "8th Grade Algebra GPA": "mean",
        }
    )
    .round(2)
)
pathway_stats["Progression Rate %"] = (
    pathway_stats["Took Algebra 8th"] / pathway_stats["State Student ID"] * 100
).round(1)
pathway_stats = pathway_stats.rename(
    columns={
        "State Student ID": "Total Students",
        "Took Algebra 8th": "Took Algebra",
        "7th Grade Math GPA": "Avg 7th Math GPA",
        "8th Grade Algebra GPA": "Avg Algebra GPA",
    }
)

print("\n  By Pathway:")
print(pathway_stats.to_string())

# By sex
sex_stats = (
    progression_df.groupby("Sex")
    .agg(
        {
            "State Student ID": "count",
            "Took Algebra 8th": "sum",
            "7th Grade Math GPA": "mean",
            "8th Grade Algebra GPA": "mean",
        }
    )
    .round(2)
)
sex_stats["Progression Rate %"] = (
    sex_stats["Took Algebra 8th"] / sex_stats["State Student ID"] * 100
).round(1)
sex_stats = sex_stats.rename(
    columns={
        "State Student ID": "Total Students",
        "Took Algebra 8th": "Took Algebra",
        "7th Grade Math GPA": "Avg 7th Math GPA",
        "8th Grade Algebra GPA": "Avg Algebra GPA",
    }
)

print("\n  By Sex:")
print(sex_stats.to_string())

# By race (top groups only)
race_stats = (
    progression_df.groupby("Race")
    .agg(
        {
            "State Student ID": "count",
            "Took Algebra 8th": "sum",
            "7th Grade Math GPA": "mean",
            "8th Grade Algebra GPA": "mean",
        }
    )
    .round(2)
)
race_stats["Progression Rate %"] = (
    race_stats["Took Algebra 8th"] / race_stats["State Student ID"] * 100
).round(1)
race_stats = race_stats.rename(
    columns={
        "State Student ID": "Total Students",
        "Took Algebra 8th": "Took Algebra",
        "7th Grade Math GPA": "Avg 7th Math GPA",
        "8th Grade Algebra GPA": "Avg Algebra GPA",
    }
)
race_stats = race_stats[
    race_stats["Total Students"] >= 5
]  # Only show groups with 5+ students
race_stats = race_stats.sort_values("Total Students", ascending=False)

print("\n  By Race/Ethnicity (groups with 5+ students):")
print(race_stats.to_string())

# Save Task A results
progression_df.to_excel("task_a_pipeline_with_performance.xlsx", index=False)
print("\n  ✓ Saved: task_a_pipeline_with_performance.xlsx")

# Step 6: Task B - LEAD Program Analysis
print("\n[6/7] Task B: LEAD Program Longitudinal Trends...")

lead_by_year = (
    lead_df.groupby("Academic Year")
    .agg(
        {
            "State Student ID": "nunique",
            "Sex": lambda x: (x == "F").sum(),
            "Description_STU_ETH": lambda x: (x == "Yes, Hispanic or Latino").sum(),
        }
    )
    .round(0)
)

lead_by_year = lead_by_year.rename(
    columns={
        "State Student ID": "Total Enrollment",
        "Sex": "Female Count",
        "Description_STU_ETH": "Hispanic/Latino Count",
    }
)

# Add male count
lead_sex_counts = lead_df.groupby(["Academic Year", "Sex"]).size().unstack(fill_value=0)
if "M" in lead_sex_counts.columns:
    lead_by_year["Male Count"] = lead_sex_counts["M"]
else:
    lead_by_year["Male Count"] = 0

# Calculate percentages
lead_by_year["Female %"] = (
    lead_by_year["Female Count"] / lead_by_year["Total Enrollment"] * 100
).round(1)
lead_by_year["Male %"] = (
    lead_by_year["Male Count"] / lead_by_year["Total Enrollment"] * 100
).round(1)
lead_by_year["Hispanic/Latino %"] = (
    lead_by_year["Hispanic/Latino Count"] / lead_by_year["Total Enrollment"] * 100
).round(1)

lead_by_year = lead_by_year[
    [
        "Total Enrollment",
        "Female Count",
        "Hispanic/Latino Count",
        "Male Count",
        "Female %",
        "Male %",
        "Hispanic/Latino %",
    ]
]

print("\n  LEAD Enrollment Trends:")
print(lead_by_year.to_string())

lead_by_year.to_excel("task_b_lead_trends_updated.xlsx")
print("\n  ✓ Saved: task_b_lead_trends_updated.xlsx")

# Step 7: Create comprehensive output
print("\n[7/7] Creating comprehensive summary...")

# Save all grades with demographics
grades_with_demographics = grades_filtered.merge(
    all_enrollments[
        ["State Student ID", "Sex", "Description_STU_RC1", "Description_STU_ETH"]
    ].drop_duplicates(),
    left_on="state_id",
    right_on="State Student ID",
    how="left",
)

first_year = sorted(lead_by_year.index)[0]
last_year = sorted(lead_by_year.index)[-1]
summary_stats = {
    "Total Students Analyzed": all_enrollments["State Student ID"].nunique(),
    "Total Enrollment Records": len(all_enrollments),
    "Total Grade Records": len(grades_filtered),
    "7th Graders Tracked": len(seventh_graders),
    "Progressed to Algebra": took_algebra_count,
    "Progression Rate": f"{progression_rate:.1f}%",
    "LEAD Program Total Enrollment (5 years)": lead_df["State Student ID"].nunique(),
    "LEAD Enrollment Growth": f"{int(lead_by_year.loc[first_year, 'Total Enrollment'])} → {int(lead_by_year.loc[last_year, 'Total Enrollment'])}",
}

summary_df = pd.DataFrame([summary_stats]).T
summary_df.columns = ["Value"]
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)
print(summary_df.to_string())

summary_df.to_excel("analysis_summary.xlsx")
print("\n✓ Saved: analysis_summary.xlsx")

print("\n" + "=" * 80)
print("COMPLETE - All analysis files generated")
print("=" * 80)
print("\nGenerated files:")
print("  1. task_a_pipeline_with_performance.xlsx - 7th→8th pipeline with grades")
print("  2. task_b_lead_trends_updated.xlsx - LEAD program trends")
print("  3. analysis_summary.xlsx - Overall summary statistics")
