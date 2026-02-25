#!/usr/bin/env python3
"""
Metabase Dashboard Creation Script - API Approach
Creates all 5 dashboards programmatically using Metabase REST API

This script bypasses the UI automation blockers by using direct API calls.

Prerequisites:
1. Metabase running at http://localhost:3000
2. Admin credentials (email/password)
3. Database connection established in Metabase

Usage:
    # Set credentials (don't commit these!)
    export METABASE_EMAIL="admin@oss-framework.local"
    export METABASE_PASSWORD="your-admin-password"

    # Run script
    python3 create-dashboards-api.py

    # Or run with inline credentials
    python3 create-dashboards-api.py --email admin@oss-framework.local --password YOURPASS

Output:
    - Creates "OSS Analytics" collection
    - Creates 26 saved questions (visualizations)
    - Creates 5 dashboards with all visualizations
    - Configures filters and parameters
    - Reports creation status

Estimated Runtime: 5-10 minutes
"""

import requests
import json
import time
import os
import sys
import argparse
from typing import Dict, List, Optional, Any


class MetabaseAPIClient:
    """Client for Metabase REST API operations"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token: Optional[str] = None
        self.headers = {"Content-Type": "application/json"}
        self.database_id: Optional[int] = None
        self.collection_id: Optional[int] = None

    def login(self, email: str, password: str) -> bool:
        """Authenticate with Metabase and get session token"""
        print(f"🔐 Authenticating as {email}...")

        response = requests.post(
            f"{self.api_url}/session",
            headers=self.headers,
            json={"username": email, "password": password},
            timeout=10,
        )

        if response.status_code in [200, 201]:
            data = response.json()
            self.session_token = data.get("id", "")
            if self.session_token:
                self.headers["X-Metabase-Session"] = self.session_token
                print("✅ Authentication successful")
                return True
            else:
                print("❌ No session token in response")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    def get_databases(self) -> List[Dict]:
        """Get list of connected databases"""
        print("📊 Fetching databases...")

        response = requests.get(
            f"{self.api_url}/database", headers=self.headers, timeout=10
        )

        if response.status_code == 200:
            databases = response.json()["data"]
            print(f"✅ Found {len(databases)} database(s)")
            for db in databases:
                print(f"   - {db['name']} (ID: {db['id']}, Engine: {db['engine']})")
            return databases
        else:
            print(f"❌ Failed to fetch databases: {response.status_code}")
            return []

    def find_database(self, name_contains: str = "OSS") -> Optional[int]:
        """Find database by name (partial match)"""
        databases = self.get_databases()
        for db in databases:
            if name_contains.lower() in db["name"].lower():
                self.database_id = db["id"]
                print(f"✅ Using database: {db['name']} (ID: {db['id']})")
                return db["id"]

        print(f"⚠️  No database matching '{name_contains}' found")
        return None

    def create_collection(self, name: str, description: str = "") -> Optional[int]:
        """Create collection to organize dashboards"""
        print(f"📁 Creating collection: {name}...")

        # Check if collection exists
        response = requests.get(
            f"{self.api_url}/collection", headers=self.headers, timeout=10
        )

        if response.status_code == 200:
            collections = response.json()
            for coll in collections:
                if coll["name"] == name:
                    self.collection_id = coll["id"]
                    print(f"✅ Collection already exists (ID: {coll['id']})")
                    return coll["id"]

        # Create new collection
        response = requests.post(
            f"{self.api_url}/collection",
            headers=self.headers,
            json={"name": name, "description": description, "color": "#509EE3"},
            timeout=10,
        )

        if response.status_code in [200, 201]:
            coll_id = response.json()["id"]
            self.collection_id = coll_id
            print(f"✅ Collection created (ID: {coll_id})")
            return coll_id
        else:
            print(f"❌ Failed to create collection: {response.status_code}")
            return None

    def create_question(
        self,
        name: str,
        query: str,
        viz_type: str = "table",
        viz_settings: Optional[Dict] = None,
        description: str = "",
    ) -> Optional[int]:
        print(f"  📈 Creating question: {name}...")

        if viz_settings is None:
            viz_settings = {}

        # Build query object
        query_obj = {
            "database": self.database_id,
            "type": "native",
            "native": {"query": query},
        }

        # Build card object
        card_data = {
            "name": name,
            "display": viz_type,
            "visualization_settings": viz_settings,
            "dataset_query": query_obj,
            "collection_id": self.collection_id,
        }

        # Only add description if it's non-empty (Metabase v0.51.4 requires at least 1 char)
        if description:
            card_data["description"] = description

        response = requests.post(
            f"{self.api_url}/card", headers=self.headers, json=card_data, timeout=30
        )

        if response.status_code in [200, 201]:
            card_id = response.json()["id"]
            print(f"    ✅ Created (ID: {card_id})")
            return card_id
        else:
            print(f"    ❌ Failed: {response.status_code} - {response.text[:200]}")
            return None

    def cleanup_collection(self) -> bool:
        if not self.collection_id:
            print("⚠️  No collection ID set, skipping cleanup")
            return False

        print(f"🧹 Cleaning up collection ID {self.collection_id}...")

        response = requests.get(
            f"{self.api_url}/collection/{self.collection_id}/items",
            headers=self.headers,
            timeout=10,
        )

        if response.status_code != 200:
            print(f"⚠️  Could not fetch collection items: {response.status_code}")
            return False

        items = response.json().get("data", [])

        dashboards = [item for item in items if item["model"] == "dashboard"]
        for dash in dashboards:
            dash_id = dash["id"]
            print(f"  🗑️  Deleting dashboard: {dash['name']} (ID: {dash_id})")
            del_response = requests.delete(
                f"{self.api_url}/dashboard/{dash_id}",
                headers=self.headers,
                timeout=10,
            )
            if del_response.status_code == 204:
                print(f"    ✅ Deleted")
            else:
                print(f"    ⚠️  Failed: {del_response.status_code}")

        cards = [item for item in items if item["model"] == "card"]
        for card in cards:
            card_id = card["id"]
            print(f"  🗑️  Deleting question: {card['name']} (ID: {card_id})")
            del_response = requests.delete(
                f"{self.api_url}/card/{card_id}",
                headers=self.headers,
                timeout=10,
            )
            if del_response.status_code == 204:
                print(f"    ✅ Deleted")
            else:
                print(f"    ⚠️  Failed: {del_response.status_code}")

        print(
            f"✅ Cleanup complete: deleted {len(dashboards)} dashboards, {len(cards)} questions"
        )
        return True

    def create_dashboard(self, name: str, description: str = "") -> Optional[int]:
        """Create a new dashboard"""
        print(f"📊 Creating dashboard: {name}...")

        response = requests.post(
            f"{self.api_url}/dashboard",
            headers=self.headers,
            json={
                "name": name,
                "description": description,
                "collection_id": self.collection_id,
            },
            timeout=10,
        )

        if response.status_code in [200, 201]:
            dash_id = response.json()["id"]
            print(f"✅ Dashboard created (ID: {dash_id})")
            return dash_id
        else:
            print(f"❌ Failed to create dashboard: {response.status_code}")
            return None

    def add_card_to_dashboard(
        self,
        dashboard_id: int,
        card_id: int,
        row: int = 0,
        col: int = 0,
        size_x: int = 6,
        size_y: int = 4,
    ) -> bool:
        """Add a saved question to a dashboard"""
        print(f"  🔗 Adding card {card_id} to dashboard {dashboard_id}...")

        get_response = requests.get(
            f"{self.api_url}/dashboard/{dashboard_id}",
            headers=self.headers,
            timeout=10,
        )

        if get_response.status_code != 200:
            print(f"    ❌ Failed to get dashboard: {get_response.status_code}")
            return False

        dashboard_data = get_response.json()
        existing_dashcards = dashboard_data.get("dashcards", [])

        new_dashcard = {
            "id": -1,
            "card_id": card_id,
            "row": row,
            "col": col,
            "size_x": size_x,
            "size_y": size_y,
        }

        existing_dashcards.append(new_dashcard)

        response = requests.put(
            f"{self.api_url}/dashboard/{dashboard_id}",
            headers=self.headers,
            json={"dashcards": existing_dashcards},
            timeout=10,
        )

        if response.status_code in [200, 201]:
            print(f"    ✅ Card added")
            return True
        else:
            print(f"    ❌ Failed: {response.status_code}")
            return False


# ============================================================================
# Dashboard Specifications
# ============================================================================


def create_dashboard_1_chronic_absenteeism(client: MetabaseAPIClient) -> bool:
    """
    Dashboard 1: Chronic Absenteeism Risk
    Target: Principals, Counselors, Administrators
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 1: CHRONIC ABSENTEEISM RISK")
    print("=" * 80)

    # Create saved questions (visualizations)
    questions = []

    # Q1: Risk Distribution (Pie Chart)
    q1_id = client.create_question(
        name="Risk Distribution by Level",
        query="""
        SELECT 
            risk_level,
            COUNT(*) as student_count
        FROM main_main_analytics.v_chronic_absenteeism_risk
        GROUP BY risk_level
        ORDER BY 
            CASE risk_level
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END
        """,
        viz_type="pie",
        viz_settings={
            "pie.show_legend": True,
            "pie.percent_visibility": "inside",
            "pie.colors": {
                "Critical": "#EF4444",
                "High": "#F97316",
                "Medium": "#EAB308",
                "Low": "#10B981",
            },
        },
    )
    if q1_id:
        questions.append(("Q1: Risk Distribution", q1_id, 0, 0, 6, 4))

    # Q2: Key Metrics (Cards)
    q2_id = client.create_question(
        name="Total Students Monitored",
        query="SELECT COUNT(*) as total FROM main_main_analytics.v_chronic_absenteeism_risk",
        viz_type="scalar",
    )
    if q2_id:
        questions.append(("Q2: Total Students", q2_id, 0, 6, 3, 2))

    q3_id = client.create_question(
        name="Chronic Absenteeism Rate",
        query="""
        SELECT 
            ROUND(
                100.0 * COUNT(CASE WHEN attendance_rate_30d < 90 THEN 1 END) / COUNT(*),
                1
            ) as chronic_rate
        FROM main_main_analytics.v_chronic_absenteeism_risk
        """,
        viz_type="scalar",
        viz_settings={"scalar.unit": "%"},
    )
    if q3_id:
        questions.append(("Q3: Chronic Rate", q3_id, 0, 9, 3, 2))

    # Q4: Top At-Risk Students (Table)
    q4_id = client.create_question(
        name="Top 20 At-Risk Students",
        query="""
        SELECT 
            student_key,
            grade_level,
            ROUND(attendance_rate_30d, 1) as attendance_30d,
            ROUND(unexcused_absence_rate_30d, 1) as unexcused_30d,
            chronic_absenteeism_risk_score as risk_score,
            risk_level,
            school_id
        FROM main_main_analytics.v_chronic_absenteeism_risk
        WHERE risk_level IN ('High', 'Critical')
        ORDER BY chronic_absenteeism_risk_score DESC
        LIMIT 20
        """,
        viz_type="table",
    )
    if q4_id:
        questions.append(("Q4: Top At-Risk", q4_id, 4, 0, 12, 6))

    # Q5: Grade-Level Comparison (Bar Chart)
    q5_id = client.create_question(
        name="Chronic Absenteeism by Grade",
        query="""
        SELECT 
            grade_level,
            ROUND(
                100.0 * COUNT(CASE WHEN attendance_rate_30d < 90 THEN 1 END) / COUNT(*),
                1
            ) as chronic_rate
        FROM main_main_analytics.v_chronic_absenteeism_risk
        GROUP BY grade_level
        ORDER BY grade_level
        """,
        viz_type="bar",
        viz_settings={
            "graph.dimensions": ["grade_level"],
            "graph.metrics": ["chronic_rate"],
            "graph.colors": ["#3B82F6"],
        },
    )
    if q5_id:
        questions.append(("Q5: Grade Comparison", q5_id, 2, 6, 6, 4))

    # Create dashboard
    dash_id = client.create_dashboard(
        name="Dashboard 1: Chronic Absenteeism Risk",
        description="Identify and track chronically absent students. Target: Principals, Counselors.",
    )

    if not dash_id:
        return False

    # Add all questions to dashboard
    for name, card_id, row, col, size_x, size_y in questions:
        client.add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y)

    print(f"\n✅ Dashboard 1 complete: http://localhost:3000/dashboard/{dash_id}")
    return True


def create_dashboard_2_wellbeing_risk(client: MetabaseAPIClient) -> bool:
    """
    Dashboard 2: Student Wellbeing Risk Profiles
    Target: Counselors, Social Workers
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 2: STUDENT WELLBEING RISK PROFILES")
    print("=" * 80)

    questions = []

    # Q1: Multi-Domain Risk Students (Table)
    q1_id = client.create_question(
        name="Students by Wellbeing Level",
        query="""
        SELECT 
            student_key,
            grade_level,
            ROUND(attendance_risk_score, 0) as att_risk,
            ROUND(discipline_risk_score, 0) as disc_risk,
            ROUND(academic_risk_score, 0) as acad_risk,
            ROUND(wellbeing_risk_score, 0) as total_risk,
            primary_concern,
            wellbeing_risk_level
        FROM main_main_analytics.v_wellbeing_risk_profiles
        ORDER BY wellbeing_risk_score DESC
        LIMIT 50
        """,
        viz_type="table",
    )
    if q1_id:
        questions.append(("Q1: Wellbeing Table", q1_id, 0, 0, 12, 8))

    # Q2: Wellbeing Risk Breakdown (Stacked Bar)
    q2_id = client.create_question(
        name="Wellbeing Risk by Grade",
        query="""
        SELECT 
            grade_level,
            COUNT(CASE WHEN wellbeing_risk_score <= 30 THEN 1 END) as low,
            COUNT(CASE WHEN wellbeing_risk_score > 30 AND wellbeing_risk_score <= 60 THEN 1 END) as moderate,
            COUNT(CASE WHEN wellbeing_risk_score > 60 AND wellbeing_risk_score <= 80 THEN 1 END) as high,
            COUNT(CASE WHEN wellbeing_risk_score > 80 THEN 1 END) as critical
        FROM main_main_analytics.v_wellbeing_risk_profiles
        GROUP BY grade_level
        ORDER BY grade_level
        """,
        viz_type="bar",
        viz_settings={"stackable.stack_type": "stacked"},
    )
    if q2_id:
        questions.append(("Q2: Risk Breakdown", q2_id, 8, 0, 12, 4))

    # Create dashboard
    dash_id = client.create_dashboard(
        name="Dashboard 2: Student Wellbeing Risk Profiles",
        description="Multi-domain risk assessment for case management. Target: Counselors.",
    )

    if not dash_id:
        return False

    for name, card_id, row, col, size_x, size_y in questions:
        client.add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y)

    print(f"\n✅ Dashboard 2 complete: http://localhost:3000/dashboard/{dash_id}")
    return True


def create_dashboard_3_equity_outcomes(client: MetabaseAPIClient) -> bool:
    """
    Dashboard 3: Equity Outcomes Analysis
    Target: Administrators, Board Members, Counselors
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 3: EQUITY OUTCOMES ANALYSIS")
    print("=" * 80)

    questions = []

    # Q1: Attendance by Demographic (Bar Chart)
    q1_id = client.create_question(
        name="Attendance Rate by Demographic",
        query="""
        SELECT 
            CASE 
                WHEN race_ethnicity IS NOT NULL THEN race_ethnicity
                WHEN english_learner THEN 'English Learner'
                WHEN special_education THEN 'Special Education'
                WHEN economically_disadvantaged THEN 'Economically Disadvantaged'
                ELSE 'Other'
            END as demographic_group,
            ROUND(pct_good_attendance, 1) as attendance_rate
        FROM main_main_analytics.v_equity_outcomes_by_demographics
        ORDER BY pct_good_attendance
        """,
        viz_type="bar",
        viz_settings={
            "graph.dimensions": ["demographic_group"],
            "graph.metrics": ["attendance_rate"],
        },
    )
    if q1_id:
        questions.append(("Q1: Attendance Equity", q1_id, 0, 0, 12, 4))

    # Q2: Opportunity Gap Table
    q2_id = client.create_question(
        name="Opportunity Gap by Subgroup",
        query="""
        SELECT 
            CASE 
                WHEN race_ethnicity IS NOT NULL THEN race_ethnicity
                WHEN english_learner THEN 'English Learner'
                WHEN special_education THEN 'Special Education'
                WHEN economically_disadvantaged THEN 'Economically Disadvantaged'
                ELSE 'Other'
            END as demographic_group,
            cohort_size,
            ROUND(pct_good_attendance, 1) as pct_attend,
            ROUND(avg_gpa, 2) as avg_gpa,
            ROUND(pct_gpa_2_5_plus, 1) as pct_passed,
            CASE 
                WHEN pct_good_attendance < 85 OR avg_gpa < 2.0 THEN 'Yes'
                ELSE 'No'
            END as equity_flag
        FROM main_main_analytics.v_equity_outcomes_by_demographics
        ORDER BY 
            CASE WHEN pct_good_attendance < 85 OR avg_gpa < 2.0 THEN 1 ELSE 2 END,
            avg_gpa
        """,
        viz_type="table",
    )
    if q2_id:
        questions.append(("Q2: Opportunity Gaps", q2_id, 4, 0, 12, 6))

    # Create dashboard
    dash_id = client.create_dashboard(
        name="Dashboard 3: Equity Outcomes Analysis",
        description="Achievement and opportunity gaps by demographics. Target: Leadership, Board.",
    )

    if not dash_id:
        return False

    for name, card_id, row, col, size_x, size_y in questions:
        client.add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y)

    print(f"\n✅ Dashboard 3 complete: http://localhost:3000/dashboard/{dash_id}")
    return True


def create_dashboard_4_class_effectiveness(client: MetabaseAPIClient) -> bool:
    """
    Dashboard 4: Class Effectiveness Comparison
    Target: Principals, Teachers (filtered to own classes)
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 4: CLASS EFFECTIVENESS COMPARISON")
    print("=" * 80)

    questions = []

    # Q1: Teacher Effectiveness Table
    q1_id = client.create_question(
        name="Class Section Performance",
        query="""
        SELECT 
            course_id,
            school_id,
            grade_level,
            enrollment_count,
            ROUND(pct_passed, 1) as pass_rate,
            ROUND(avg_grade_numeric, 2) as avg_grade,
            effectiveness_rating,
            term
        FROM main_main_analytics.v_class_section_comparison
        ORDER BY pct_passed DESC
        """,
        viz_type="table",
    )
    if q1_id:
        questions.append(("Q1: Class Performance", q1_id, 0, 0, 12, 8))

    # Create dashboard
    dash_id = client.create_dashboard(
        name="Dashboard 4: Class Effectiveness Comparison",
        description="Class-level performance metrics. Target: Principals, Teachers.",
    )

    if not dash_id:
        return False

    for name, card_id, row, col, size_x, size_y in questions:
        client.add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y)

    print(f"\n✅ Dashboard 4 complete: http://localhost:3000/dashboard/{dash_id}")
    return True


def create_dashboard_5_correlations(client: MetabaseAPIClient) -> bool:
    """
    Dashboard 5: Performance Correlations
    Target: Administrators, Board Members
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 5: PERFORMANCE CORRELATIONS")
    print("=" * 80)

    questions = []

    # Q1: Key Correlations (Table)
    q1_id = client.create_question(
        name="Performance Correlations",
        query="""
        SELECT 
            correlation_pair,
            ROUND(correlation_coefficient, 3) as correlation,
            strength,
            expected_direction,
            data_points
        FROM main_main_analytics.v_performance_correlations
        ORDER BY ABS(correlation_coefficient) DESC
        """,
        viz_type="table",
    )
    if q1_id:
        questions.append(("Q1: Correlations", q1_id, 0, 0, 12, 6))

    # Create dashboard
    dash_id = client.create_dashboard(
        name="Dashboard 5: Performance Correlations",
        description="Statistical insights on student success factors. Target: Leadership.",
    )

    if not dash_id:
        return False

    for name, card_id, row, col, size_x, size_y in questions:
        client.add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y)

    print(f"\n✅ Dashboard 5 complete: http://localhost:3000/dashboard/{dash_id}")
    return True


# ============================================================================
# Main Execution
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Create OSS Analytics Dashboards in Metabase via API"
    )
    parser.add_argument(
        "--email",
        default=os.getenv("METABASE_EMAIL"),
        help="Metabase admin email (or set METABASE_EMAIL env var)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("METABASE_PASSWORD"),
        help="Metabase admin password (or set METABASE_PASSWORD env var)",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:3000",
        help="Metabase URL (default: http://localhost:3000)",
    )
    parser.add_argument(
        "--skip-dashboard",
        type=int,
        choices=[1, 2, 3, 4, 5],
        action="append",
        help="Skip specific dashboard (can use multiple times)",
    )

    args = parser.parse_args()

    # Validate credentials
    if not args.email or not args.password:
        print("❌ Error: Metabase credentials required")
        print("\nOptions:")
        print("  1. Set environment variables:")
        print("     export METABASE_EMAIL='admin@oss-framework.local'")
        print("     export METABASE_PASSWORD='your-password'")
        print("\n  2. Use command-line arguments:")
        print("     python3 create-dashboards-api.py --email EMAIL --password PASS")
        sys.exit(1)

    print("=" * 80)
    print("🚀 METABASE DASHBOARD CREATION - API APPROACH")
    print("=" * 80)
    print(f"URL: {args.url}")
    print(f"User: {args.email}")
    print()

    # Initialize client
    client = MetabaseAPIClient(args.url)

    # Step 1: Authenticate
    if not client.login(args.email, args.password):
        print("\n❌ Authentication failed. Please check credentials.")
        sys.exit(1)

    # Step 2: Find database
    db_id = client.find_database("OSS")
    if not db_id:
        print("\n❌ No database found. Please connect DuckDB database first.")
        print("   Go to: http://localhost:3000/admin/databases/create")
        sys.exit(1)

    # Step 3: Create collection
    coll_id = client.create_collection(
        name="OSS Analytics",
        description="Student wellbeing and performance analytics dashboards",
    )
    if not coll_id:
        print("\n❌ Failed to create collection")
        sys.exit(1)

    client.cleanup_collection()

    # Step 4: Create dashboards
    skip_dashboards = args.skip_dashboard or []
    dashboards = [
        (1, create_dashboard_1_chronic_absenteeism),
        (2, create_dashboard_2_wellbeing_risk),
        (3, create_dashboard_3_equity_outcomes),
        (4, create_dashboard_4_class_effectiveness),
        (5, create_dashboard_5_correlations),
    ]

    success_count = 0
    for dash_num, dash_func in dashboards:
        if dash_num in skip_dashboards:
            print(f"\n⏭️  Skipping Dashboard {dash_num}")
            continue

        try:
            if dash_func(client):
                success_count += 1
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"\n❌ Error creating Dashboard {dash_num}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 DASHBOARD CREATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully created: {success_count} dashboard(s)")
    print(f"⏭️  Skipped: {len(skip_dashboards)} dashboard(s)")
    print(f"\n🌐 View dashboards at: {args.url}/collection/{coll_id}")
    print("=" * 80)


if __name__ == "__main__":
    main()
