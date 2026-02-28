#!/usr/bin/env python3
"""
Data Normalization and Analysis Script
5-Year Enrollment & Outcomes Study

This script normalizes and integrates data from multiple Excel files,
then performs longitudinal analysis of student progression.

CONFIGURATION REQUIRED (Lines 20-30):
- Set COURSE_308_IS_000308 based on user confirmation
- Set APEX_COURSE_ID based on which course represents Apex Math 8
- Set INCLUDE_CSV based on whether to include CSV data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION SECTION - UPDATE THESE BASED ON USER CLARIFICATIONS
# ============================================================================

# Question 1: Is Course ID 308 the same as "000308"?
COURSE_308_IS_000308 = True  # Set to True if they're the same, False if different

# Question 2: Which Course ID represents "Apex Math 8" (accelerated pathway)?
# Options: 329 or 325
APEX_COURSE_ID = 325  # UPDATE THIS: 325 or 329
REGULAR_MATH8_ID = 329 if APEX_COURSE_ID == 325 else 325

# Question 3: Include CSV file in analysis?
INCLUDE_CSV = False  # Recommended: False (limited data, no demographics)

# Target Course ID for analysis (Algebra 1)
ALGEBRA1_COURSE_ID = 308

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def standardize_academic_year(year_value):
    """
    Convert various Academic Year formats to standard 'YY-YY' format.

    Handles:
    - Timestamps: '2021-08-20' → '21-22'
    - Full format: '2022-2023' → '22-23'
    - Already standard: '23-24' → '23-24'
    """
    if pd.isna(year_value):
        return None

    # If already in YY-YY format
    if isinstance(year_value, str) and len(year_value) == 5 and "-" in year_value:
        parts = year_value.split("-")
        if len(parts[0]) == 2 and len(parts[1]) == 2:
            return year_value

    # If timestamp (datetime object)
    if isinstance(year_value, (pd.Timestamp, datetime)):
        year = year_value.year
        # School year starts in fall, so Aug-Dec = year1, Jan-Jul = year2
        if year_value.month >= 8:
            year1 = year % 100
            year2 = (year + 1) % 100
        else:
            year1 = (year - 1) % 100
            year2 = year % 100
        return f"{year1:02d}-{year2:02d}"

    # If full format like '2022-2023'
    if isinstance(year_value, str) and len(year_value) == 9:
        year1 = int(year_value[:4]) % 100
        year2 = int(year_value[5:9]) % 100
        return f"{year1:02d}-{year2:02d}"

    return str(year_value)


def load_and_standardize_excel(file_path, sheet_name="Master Data"):
    """
    Load Excel file and standardize column names and formats.
    """
    print(f"\nLoading: {file_path} (Sheet: {sheet_name})")
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Standardize column names
    column_mapping = {
        "Academic year": "Academic Year",
        "student_id_raw": "State Student ID",
        "course_id": "Course ID",
        "school_year": "Academic Year",
    }

    df = df.rename(columns=column_mapping)

    # Standardize Academic Year format
    if "Academic Year" in df.columns:
        df["Academic Year"] = df["Academic Year"].apply(standardize_academic_year)

    # Convert Course ID to integer
    if "Course ID" in df.columns:
        df["Course ID"] = df["Course ID"].astype(int)

    print(f"  Records: {len(df)}")
    print(f"  Students: {df['State Student ID'].nunique()}")
    print(f"  Years: {sorted(df['Academic Year'].unique())}")

    return df


# ============================================================================
# DATA LOADING AND NORMALIZATION
# ============================================================================

print("=" * 80)
print("DATA NORMALIZATION & INTEGRATION")
print("=" * 80)
print(f"\nConfiguration:")
print(f"  Course 308 = '000308': {COURSE_308_IS_000308}")
print(f"  Apex Math 8 Course ID: {APEX_COURSE_ID}")
print(f"  Regular Math 8 Course ID: {REGULAR_MATH8_ID}")
print(f"  Include CSV: {INCLUDE_CSV}")

# Load Excel files
algebra_df = load_and_standardize_excel("Algebra 1A 23-26.xlsx")
lead_df = load_and_standardize_excel("Lead 21-26.xlsx")
math8_df = load_and_standardize_excel("MATH 8 and Apex Data 21-26.xlsx")

# Add pathway labels to Math 8 data
math8_df["Math Pathway"] = math8_df["Course ID"].apply(
    lambda x: "Apex Math 8" if x == APEX_COURSE_ID else "Regular Math 8"
)

# Load CSV if requested
if INCLUDE_CSV:
    csv_df = pd.read_csv("academicrecords .csv")
    csv_df = csv_df.rename(
        columns={
            "student_id_raw": "State Student ID",
            "course_id": "Course ID",
            "school_year": "Academic Year",
        }
    )
    csv_df["Academic Year"] = csv_df["Academic Year"].apply(standardize_academic_year)
    print(f"\nLoaded CSV: {len(csv_df)} records")

# ============================================================================
# CREATE UNIFIED ENROLLMENT TABLE
# ============================================================================

print("\n" + "=" * 80)
print("CREATING UNIFIED ENROLLMENT TABLE")
print("=" * 80)

# Combine all enrollment data
all_enrollments = []

# Algebra enrollments
algebra_df["Course Name"] = "Algebra 1"
all_enrollments.append(
    algebra_df[
        [
            "State Student ID",
            "Last Name",
            "First Name",
            "Grade",
            "Sex",
            "Description_STU_ETH",
            "Description_STU_RC1",
            "Section#",
            "Course ID",
            "Course Name",
            "Academic Year",
        ]
    ]
)

# LEAD enrollments
lead_df["Course Name"] = "LEAD Program"
all_enrollments.append(
    lead_df[
        [
            "State Student ID",
            "Last Name",
            "First Name",
            "Grade",
            "Sex",
            "Description_STU_ETH",
            "Description_STU_RC1",
            "Section#",
            "Course ID",
            "Course Name",
            "Academic Year",
        ]
    ]
)

# Math 8 enrollments
math8_df["Course Name"] = math8_df["Math Pathway"]
all_enrollments.append(
    math8_df[
        [
            "State Student ID",
            "Last Name",
            "First Name",
            "Grade",
            "Sex",
            "Description_STU_ETH",
            "Description_STU_RC1",
            "Section#",
            "Course ID",
            "Course Name",
            "Academic Year",
        ]
    ]
)

unified_df = pd.concat(all_enrollments, ignore_index=True)

print(f"\nUnified Enrollment Table:")
print(f"  Total records: {len(unified_df)}")
print(f"  Unique students: {unified_df['State Student ID'].nunique()}")
print(f"  Academic years: {sorted(unified_df['Academic Year'].unique())}")
print(f"  Courses: {unified_df['Course Name'].unique()}")

# Save unified table
unified_df.to_excel("unified_enrollments.xlsx", index=False)
print("\n✓ Saved: unified_enrollments.xlsx")

# ============================================================================
# CREATE DEMOGRAPHIC MASTER TABLE
# ============================================================================

print("\n" + "=" * 80)
print("CREATING DEMOGRAPHIC MASTER TABLE")
print("=" * 80)

# Create one row per student with their demographics
# Use most recent record for each student
demo_df = (
    unified_df.sort_values("Academic Year", ascending=False)
    .groupby("State Student ID")
    .first()
    .reset_index()
)
demo_df = demo_df[
    [
        "State Student ID",
        "Last Name",
        "First Name",
        "Sex",
        "Description_STU_ETH",
        "Description_STU_RC1",
    ]
]

print(f"\nDemographic Master Table:")
print(f"  Total students: {len(demo_df)}")
print(f"\nSex distribution:")
print(demo_df["Sex"].value_counts())
print(f"\nRace/Ethnicity distribution:")
print(demo_df["Description_STU_RC1"].value_counts())

# Save demographic table
demo_df.to_excel("student_demographics.xlsx", index=False)
print("\n✓ Saved: student_demographics.xlsx")

# ============================================================================
# TASK A: 7th to 8th GRADE MATH SUCCESS PIPELINE
# ============================================================================

print("\n" + "=" * 80)
print("TASK A: 7TH TO 8TH GRADE MATH SUCCESS PIPELINE")
print("=" * 80)

# Get 7th graders from Math 8 data
grade7_cohorts = math8_df[math8_df["Grade"] == 7].copy()
grade7_cohorts = grade7_cohorts.sort_values(["State Student ID", "Academic Year"])

# For each 7th grader, try to find them in 8th grade Algebra the following year
pipeline_results = []

for _, student in grade7_cohorts.iterrows():
    student_id = student["State Student ID"]
    grade7_year = student["Academic Year"]
    math_pathway = student["Math Pathway"]

    # Calculate expected 8th grade year (next year)
    year_parts = grade7_year.split("-")
    year1 = int(year_parts[0]) + 1
    year2 = int(year_parts[1]) + 1
    expected_8th_year = f"{year1:02d}-{year2:02d}"

    # Look for this student in 8th grade Algebra
    algebra_record = algebra_df[
        (algebra_df["State Student ID"] == student_id)
        & (algebra_df["Academic Year"] == expected_8th_year)
        & (algebra_df["Grade"] == 8)
    ]

    took_algebra = len(algebra_record) > 0

    pipeline_results.append(
        {
            "State Student ID": student_id,
            "Last Name": student["Last Name"],
            "First Name": student["First Name"],
            "7th Grade Year": grade7_year,
            "7th Grade Math Pathway": math_pathway,
            "7th Grade Course ID": student["Course ID"],
            "Sex": student["Sex"],
            "Description_STU_ETH": student["Description_STU_ETH"],
            "Description_STU_RC1": student["Description_STU_RC1"],
            "Expected 8th Grade Year": expected_8th_year,
            "Took 8th Grade Algebra": took_algebra,
        }
    )

pipeline_df = pd.DataFrame(pipeline_results)

print(f"\n7th to 8th Grade Pipeline Analysis:")
print(f"  Total 7th graders tracked: {len(pipeline_df)}")
print(
    f"  Students who took 8th grade Algebra: {pipeline_df['Took 8th Grade Algebra'].sum()}"
)
print(
    f"  Progression rate: {pipeline_df['Took 8th Grade Algebra'].sum() / len(pipeline_df) * 100:.1f}%"
)

# Breakdown by pathway
print(f"\nBy Math Pathway:")
pathway_stats = pipeline_df.groupby("7th Grade Math Pathway")[
    "Took 8th Grade Algebra"
].agg(["count", "sum", "mean"])
pathway_stats.columns = ["Total Students", "Took Algebra", "Progression Rate"]
pathway_stats["Progression Rate"] = pathway_stats["Progression Rate"] * 100
print(pathway_stats.to_string())

# Breakdown by demographics
print(f"\nBy Sex:")
sex_stats = pipeline_df.groupby("Sex")["Took 8th Grade Algebra"].agg(
    ["count", "sum", "mean"]
)
sex_stats.columns = ["Total Students", "Took Algebra", "Progression Rate"]
sex_stats["Progression Rate"] = sex_stats["Progression Rate"] * 100
print(sex_stats.to_string())

print(f"\nBy Race:")
race_stats = pipeline_df.groupby("Description_STU_RC1")["Took 8th Grade Algebra"].agg(
    ["count", "sum", "mean"]
)
race_stats.columns = ["Total Students", "Took Algebra", "Progression Rate"]
race_stats["Progression Rate"] = race_stats["Progression Rate"] * 100
print(race_stats.to_string())

# Cross-tabulation: Pathway x Sex
print(f"\nPathway × Sex Crosstab (Progression Rates):")
crosstab = (
    pd.crosstab(
        pipeline_df["7th Grade Math Pathway"],
        pipeline_df["Sex"],
        pipeline_df["Took 8th Grade Algebra"],
        aggfunc="mean",
    )
    * 100
)
print(crosstab.to_string())

# Save pipeline analysis
pipeline_df.to_excel("task_a_pipeline_analysis.xlsx", index=False)
print("\n✓ Saved: task_a_pipeline_analysis.xlsx")

# ============================================================================
# TASK B: LEAD PROGRAM LONGITUDINAL TRENDS
# ============================================================================

print("\n" + "=" * 80)
print("TASK B: LEAD PROGRAM LONGITUDINAL TRENDS")
print("=" * 80)

# Enrollment volume by year
enrollment_by_year = (
    lead_df.groupby("Academic Year")
    .agg(
        {
            "State Student ID": "count",
            "Sex": lambda x: (x == "F").sum(),
            "Description_STU_ETH": lambda x: x.str.contains("Yes", na=False).sum(),
        }
    )
    .reset_index()
)

enrollment_by_year.columns = [
    "Academic Year",
    "Total Enrollment",
    "Female Count",
    "Hispanic/Latino Count",
]
enrollment_by_year["Male Count"] = (
    enrollment_by_year["Total Enrollment"] - enrollment_by_year["Female Count"]
)
enrollment_by_year["Female %"] = (
    enrollment_by_year["Female Count"] / enrollment_by_year["Total Enrollment"] * 100
).round(1)
enrollment_by_year["Male %"] = (
    enrollment_by_year["Male Count"] / enrollment_by_year["Total Enrollment"] * 100
).round(1)
enrollment_by_year["Hispanic/Latino %"] = (
    enrollment_by_year["Hispanic/Latino Count"]
    / enrollment_by_year["Total Enrollment"]
    * 100
).round(1)

print("\nLEAD Program Enrollment Trends (2021-2026):")
print(enrollment_by_year.to_string(index=False))

# Representation analysis by year
print("\n" + "=" * 80)
print("LEAD Program Representation Analysis")
print("=" * 80)

for year in sorted(lead_df["Academic Year"].unique()):
    year_data = lead_df[lead_df["Academic Year"] == year]

    print(f"\n{year}:")
    print(f"  Total: {len(year_data)} students")

    print(f"\n  Sex Distribution:")
    sex_dist = year_data["Sex"].value_counts()
    for sex, count in sex_dist.items():
        pct = count / len(year_data) * 100
        print(f"    {sex}: {count} ({pct:.1f}%)")

    print(f"\n  Ethnicity Distribution:")
    eth_dist = year_data["Description_STU_ETH"].value_counts()
    for eth, count in eth_dist.items():
        pct = count / len(year_data) * 100
        eth_short = eth[:40] + "..." if len(eth) > 40 else eth
        print(f"    {eth_short}: {count} ({pct:.1f}%)")

    print(f"\n  Race Distribution:")
    race_dist = year_data["Description_STU_RC1"].value_counts()
    for race, count in race_dist.items():
        pct = count / len(year_data) * 100
        print(f"    {race}: {count} ({pct:.1f}%)")

# Create detailed representation table
representation_data = []

for year in sorted(lead_df["Academic Year"].unique()):
    year_data = lead_df[lead_df["Academic Year"] == year]
    total = len(year_data)

    # Sex breakdown
    for sex in year_data["Sex"].unique():
        count = (year_data["Sex"] == sex).sum()
        representation_data.append(
            {
                "Academic Year": year,
                "Category": "Sex",
                "Group": sex,
                "Count": count,
                "Percentage": round(count / total * 100, 1),
            }
        )

    # Race breakdown
    for race in year_data["Description_STU_RC1"].unique():
        count = (year_data["Description_STU_RC1"] == race).sum()
        representation_data.append(
            {
                "Academic Year": year,
                "Category": "Race",
                "Group": race,
                "Count": count,
                "Percentage": round(count / total * 100, 1),
            }
        )

    # Ethnicity breakdown
    for eth in year_data["Description_STU_ETH"].unique():
        count = (year_data["Description_STU_ETH"] == eth).sum()
        eth_short = eth[:30]
        representation_data.append(
            {
                "Academic Year": year,
                "Category": "Ethnicity",
                "Group": eth_short,
                "Count": count,
                "Percentage": round(count / total * 100, 1),
            }
        )

representation_df = pd.DataFrame(representation_data)

# Save LEAD analysis
enrollment_by_year.to_excel("task_b_enrollment_trends.xlsx", index=False)
representation_df.to_excel("task_b_representation_analysis.xlsx", index=False)

print("\n✓ Saved: task_b_enrollment_trends.xlsx")
print("\n✓ Saved: task_b_representation_analysis.xlsx")

# ============================================================================
# SUMMARY REPORT
# ============================================================================

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - FILES GENERATED")
print("=" * 80)

print("\nGenerated files:")
print("  1. unified_enrollments.xlsx - All enrollment data (normalized)")
print("  2. student_demographics.xlsx - Master demographic table")
print("  3. task_a_pipeline_analysis.xlsx - 7th → 8th grade progression")
print("  4. task_b_enrollment_trends.xlsx - LEAD enrollment by year")
print("  5. task_b_representation_analysis.xlsx - LEAD representation details")

print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)

print(f"\nTask A - Math Pipeline:")
print(f"  • {len(pipeline_df)} students tracked from 7th to 8th grade")
print(
    f"  • {pipeline_df['Took 8th Grade Algebra'].sum()} students ({pipeline_df['Took 8th Grade Algebra'].sum() / len(pipeline_df) * 100:.1f}%) took Algebra in 8th grade"
)
apex_rate = (
    pipeline_df[pipeline_df["7th Grade Math Pathway"] == "Apex Math 8"][
        "Took 8th Grade Algebra"
    ].mean()
    * 100
)
regular_rate = (
    pipeline_df[pipeline_df["7th Grade Math Pathway"] == "Regular Math 8"][
        "Took 8th Grade Algebra"
    ].mean()
    * 100
)
print(f"  • Apex Math 8 → Algebra: {apex_rate:.1f}%")
print(f"  • Regular Math 8 → Algebra: {regular_rate:.1f}%")

print(f"\nTask B - LEAD Program:")
print(
    f"  • Total enrollment grew from {enrollment_by_year.iloc[0]['Total Enrollment']} to {enrollment_by_year.iloc[-1]['Total Enrollment']} students"
)
print(
    f"  • Latest year gender split: {enrollment_by_year.iloc[-1]['Female %']:.1f}% Female, {enrollment_by_year.iloc[-1]['Male %']:.1f}% Male"
)
print(f"  • 5-year enrollment: {lead_df['State Student ID'].nunique()} unique students")

print("\n" + "=" * 80)
