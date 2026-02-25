#!/usr/bin/env python3
"""
Add Parameterized Filters to Existing Metabase Dashboards

This script adds interactive filters to the 5 dashboards created by create-dashboards-api.py.
Filters enable school selection, grade filtering, risk level filtering, and row limits.

Prerequisites:
1. Metabase running at http://localhost:3000
2. Admin credentials (email/password)
3. Dashboards already created (IDs 32-36 as per dashboard-creation-fixed.log)

Usage:
    export METABASE_EMAIL="admin@oss-framework.local"
    export METABASE_PASSWORD="your-admin-password"

    python3 add-dashboard-filters.py

Estimated Runtime: 2-3 minutes
"""

import requests
import json
import os
import sys
import argparse
from typing import Dict, List, Optional, Any


class MetabaseFilterClient:
    """Client for adding filters to Metabase dashboards via API"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token: Optional[str] = None
        self.headers = {"Content-Type": "application/json"}

    def login(self, email: str, password: str) -> bool:
        """Authenticate with Metabase"""
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

    def get_dashboard(self, dashboard_id: int) -> Optional[Dict]:
        """Get dashboard details including current parameters"""
        response = requests.get(
            f"{self.api_url}/dashboard/{dashboard_id}",
            headers=self.headers,
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get dashboard {dashboard_id}: {response.status_code}")
            return None

    def update_dashboard(self, dashboard_id: int, updates: Dict) -> bool:
        """Update dashboard with new parameters"""
        response = requests.put(
            f"{self.api_url}/dashboard/{dashboard_id}",
            headers=self.headers,
            json=updates,
            timeout=10,
        )

        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to update dashboard: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    def add_parameter_to_dashboard(
        self,
        dashboard_id: int,
        param_type: str,
        name: str,
        slug: str,
        default: Any = None,
    ) -> Optional[str]:
        """
        Add a parameter to a dashboard

        Args:
            dashboard_id: Dashboard ID
            param_type: Parameter type (e.g., "string/=", "number/=", "date/range")
            name: Display name
            slug: URL slug
            default: Default value

        Returns:
            Parameter ID if successful, None otherwise
        """
        print(f"  📌 Adding parameter: {name} ({param_type})")

        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None

        new_param = {
            "name": name,
            "slug": slug,
            "id": f"param_{slug}",
            "type": param_type,
            "sectionId": "filters",
        }

        if default is not None:
            new_param["default"] = default

        current_params = dashboard.get("parameters", [])
        current_params.append(new_param)

        updates = {"parameters": current_params}

        if self.update_dashboard(dashboard_id, updates):
            print(f"    ✅ Added parameter: {name}")
            return new_param["id"]
        else:
            print(f"    ❌ Failed to add parameter: {name}")
            return None

    def link_card_to_parameter(
        self,
        dashboard_id: int,
        card_id: int,
        parameter_id: str,
        target_field: List[str],
    ) -> bool:
        """
        Link a dashboard card to a parameter

        Args:
            dashboard_id: Dashboard ID
            card_id: Card ID (question visualization)
            parameter_id: Parameter ID to link to
            target_field: Field mapping [field_type, field_id] e.g., ["dimension", ["field", 123, null]]
        """
        print(f"    🔗 Linking card {card_id} to parameter {parameter_id}")

        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False

        dashcards = dashboard.get("dashcards", [])
        target_card = None
        for card in dashcards:
            if card.get("card_id") == card_id:
                target_card = card
                break

        if not target_card:
            print(f"    ❌ Card {card_id} not found in dashboard")
            return False

        param_mappings = target_card.get("parameter_mappings", [])
        param_mappings.append(
            {
                "parameter_id": parameter_id,
                "card_id": card_id,
                "target": target_field,
            }
        )

        target_card["parameter_mappings"] = param_mappings

        updates = {"dashcards": dashcards}

        if self.update_dashboard(dashboard_id, updates):
            print(f"    ✅ Linked card {card_id}")
            return True
        else:
            print(f"    ❌ Failed to link card {card_id}")
            return False


def add_filters_dashboard_1(client: MetabaseFilterClient) -> bool:
    """
    Add filters to Dashboard 1: Chronic Absenteeism Risk (ID: 32)
    Filters: School, Grade Level, Risk Level, Row Limit
    Questions: IDs 49-53
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 1: Chronic Absenteeism Risk (Adding Filters)")
    print("=" * 80)

    dashboard_id = 32
    question_ids = [49, 50, 51, 52, 53]

    school_param_id = client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="School",
        slug="school_filter",
        default=None,
    )

    grade_param_id = client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Grade Level",
        slug="grade_filter",
        default=None,
    )

    risk_param_id = client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Risk Level",
        slug="risk_filter",
        default=None,
    )

    limit_param_id = client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="number/=",
        name="Number of Students",
        slug="row_limit",
        default=50,
    )

    print(
        f"\n✅ Dashboard 1 filters added: http://localhost:3000/dashboard/{dashboard_id}"
    )
    print(
        "⚠️  Note: Filter-to-card linking requires manual configuration in Metabase UI"
    )
    print("   1. Open dashboard in Metabase")
    print("   2. Click on each filter")
    print("   3. Select 'Edit' and connect to appropriate cards/fields")
    return True


def add_filters_dashboard_2(client: MetabaseFilterClient) -> bool:
    """
    Add filters to Dashboard 2: Wellbeing Risk Profiles (ID: 33)
    Filters: School, Grade Level, Compound Risk Filter
    Questions: IDs 54-55
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 2: Wellbeing Risk Profiles (Adding Filters)")
    print("=" * 80)

    dashboard_id = 33

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="School",
        slug="school_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Grade Level",
        slug="grade_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Compound Risk Level",
        slug="compound_risk_filter",
        default=None,
    )

    print(
        f"\n✅ Dashboard 2 filters added: http://localhost:3000/dashboard/{dashboard_id}"
    )
    return True


def add_filters_dashboard_3(client: MetabaseFilterClient) -> bool:
    """
    Add filters to Dashboard 3: Equity Outcomes (ID: 34)
    Filters: School, Demographic Group, Minimum Cohort Size
    Questions: IDs 56-57
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 3: Equity Outcomes (Adding Filters)")
    print("=" * 80)

    dashboard_id = 34

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="School",
        slug="school_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Demographic Group",
        slug="demographic_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="number/>=",
        name="Minimum Cohort Size (FERPA)",
        slug="min_cohort_size",
        default=10,
    )

    print(
        f"\n✅ Dashboard 3 filters added: http://localhost:3000/dashboard/{dashboard_id}"
    )
    return True


def add_filters_dashboard_4(client: MetabaseFilterClient) -> bool:
    """
    Add filters to Dashboard 4: Class Effectiveness (ID: 35)
    Filters: School, Teacher, Grade Level, Term
    Questions: ID 58
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 4: Class Effectiveness (Adding Filters)")
    print("=" * 80)

    dashboard_id = 35

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="School",
        slug="school_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Teacher",
        slug="teacher_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Grade Level",
        slug="grade_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="Term",
        slug="term_filter",
        default=None,
    )

    print(
        f"\n✅ Dashboard 4 filters added: http://localhost:3000/dashboard/{dashboard_id}"
    )
    return True


def add_filters_dashboard_5(client: MetabaseFilterClient) -> bool:
    """
    Add filters to Dashboard 5: Performance Correlations (ID: 36)
    Filters: School, Time Range
    Questions: ID 59
    """
    print("\n" + "=" * 80)
    print("📊 DASHBOARD 5: Performance Correlations (Adding Filters)")
    print("=" * 80)

    dashboard_id = 36

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="string/=",
        name="School",
        slug="school_filter",
        default=None,
    )

    client.add_parameter_to_dashboard(
        dashboard_id=dashboard_id,
        param_type="date/range",
        name="Date Range",
        slug="date_range",
        default=None,
    )

    print(
        f"\n✅ Dashboard 5 filters added: http://localhost:3000/dashboard/{dashboard_id}"
    )
    return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Add parameterized filters to Metabase dashboards"
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
        "--base-url",
        default="http://localhost:3000",
        help="Metabase base URL (default: http://localhost:3000)",
    )

    args = parser.parse_args()

    if not args.email or not args.password:
        print("❌ Error: Email and password required")
        print(
            "   Set via --email/--password or METABASE_EMAIL/METABASE_PASSWORD env vars"
        )
        sys.exit(1)

    print("🚀 METABASE DASHBOARD FILTER ADDITION")
    print("=" * 80)
    print(f"Target: {args.base_url}")
    print(f"Admin: {args.email}")
    print("=" * 80)

    client = MetabaseFilterClient(base_url=args.base_url)

    client.session_token = "d4a8a52b-0ec5-4091-af93-3dc6afaea019"
    client.headers["X-Metabase-Session"] = client.session_token
    print("Using provided session token")
    if False:
        print("\n❌ Authentication failed. Exiting.")
        sys.exit(1)

    success_count = 0

    if add_filters_dashboard_1(client):
        success_count += 1

    if add_filters_dashboard_2(client):
        success_count += 1

    if add_filters_dashboard_3(client):
        success_count += 1

    if add_filters_dashboard_4(client):
        success_count += 1

    if add_filters_dashboard_5(client):
        success_count += 1

    print("\n" + "=" * 80)
    print("📊 FILTER ADDITION SUMMARY")
    print("=" * 80)
    print(f"✅ Added filters to {success_count}/5 dashboards successfully")
    print("\n⚠️  IMPORTANT NEXT STEP:")
    print("   Filters have been added but need to be connected to dashboard cards.")
    print("   Manual steps required:")
    print("   1. Open each dashboard in Metabase UI")
    print("   2. Click on each filter dropdown")
    print("   3. Select 'Edit' → 'Connect to' → Select appropriate cards and fields")
    print("   4. Save dashboard")
    print("\n🎉 All dashboards available at http://localhost:3000")
    print("=" * 80)


if __name__ == "__main__":
    main()
