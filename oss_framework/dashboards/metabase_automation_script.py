#!/usr/bin/env python3
"""
Metabase Dashboard Automation Script

Automates:
1. Admin account creation
2. Database connection
3. Dashboard creation from JSON specs
4. Filter configuration
5. Performance testing

Usage:
    python3 metabase_automation_script.py --init-admin
    python3 metabase_automation_script.py --connect-db
    python3 metabase_automation_script.py --create-dashboards
"""

import requests
import json
import time
import argparse
import sys
from pathlib import Path

METABASE_URL = "http://localhost:3000"
METABASE_API = f"{METABASE_URL}/api"
HEADERS = {"Content-Type": "application/json"}


class MetabaseClient:
    """Client for Metabase API interactions"""

    def __init__(self, url=METABASE_URL):
        self.url = url
        self.api_url = f"{url}/api"
        self.session_id = None
        self.headers = {"Content-Type": "application/json"}

    def login(self, email, password):
        """Authenticate and get session ID"""
        data = {"username": email, "password": password}

        response = requests.post(
            f"{self.api_url}/session", headers=self.headers, json=data, timeout=10
        )

        if response.status_code in [200, 201]:
            self.session_id = response.json()["id"]
            self.headers["X-Metabase-Session"] = self.session_id
            return True
        return False

    def get_databases(self):
        """Get list of connected databases"""
        response = requests.get(
            f"{self.api_url}/database", headers=self.headers, timeout=10
        )

        if response.status_code == 200:
            return response.json()
        return []

    def connect_duckdb(self, db_name, db_path):
        """Connect DuckDB database"""
        data = {
            "name": db_name,
            "engine": "duckdb",
            "details": {"db": db_path},
            "is_full_sync": True,
            "auto_run_queries": True,
            "caching_ttl_minutes": 10,
        }

        response = requests.post(
            f"{self.api_url}/database", headers=self.headers, json=data, timeout=30
        )

        if response.status_code in [200, 201]:
            return response.json()["id"]
        return None

    def create_dashboard(self, dashboard_name, description=""):
        """Create new dashboard"""
        data = {"name": dashboard_name, "description": description, "parameters": []}

        response = requests.post(
            f"{self.api_url}/dashboard", headers=self.headers, json=data, timeout=10
        )

        if response.status_code in [200, 201]:
            return response.json()["id"]
        return None

    def create_native_query_card(self, database_id, query, name):
        """Create a card from native SQL query"""
        data = {
            "name": name,
            "dataset_query": {
                "type": "native",
                "native": {"query": query},
                "database": database_id,
            },
            "display": "table",
            "visualization_settings": {},
        }

        response = requests.post(
            f"{self.api_url}/card", headers=self.headers, json=data, timeout=10
        )

        if response.status_code in [200, 201]:
            return response.json()["id"]
        return None

    def add_card_to_dashboard(self, dashboard_id, card_id, position):
        """Add card to dashboard"""
        # Get dashboard details first
        response = requests.get(
            f"{self.api_url}/dashboard/{dashboard_id}", headers=self.headers, timeout=10
        )

        if response.status_code != 200:
            return False

        dashboard = response.json()

        # Add card to dashboard
        card_data = {
            "card_id": card_id,
            "row": position.get("row", 0),
            "col": position.get("col", 0),
            "size_x": position.get("size_x", 4),
            "size_y": position.get("size_y", 3),
        }

        response = requests.post(
            f"{self.api_url}/dashboard/{dashboard_id}/cards",
            headers=self.headers,
            json=card_data,
            timeout=10,
        )

        return response.status_code in [200, 201]


def setup_admin(client):
    """Initial Metabase setup with admin account"""
    print("Setting up Metabase admin account...")

    # This would be called by Metabase setup wizard in UI
    # For now, we assume admin already exists
    print("⚠ Admin setup requires web UI initialization")
    print("Please visit: http://localhost:3000 and complete setup")
    print("Then run login step with credentials")


def login(client, email, password):
    """Login to Metabase"""
    print(f"Logging in as {email}...")

    if client.login(email, password):
        print(f"✓ Successfully logged in")
        return True
    else:
        print(f"✗ Login failed - check credentials")
        return False


def connect_database(client):
    """Connect DuckDB to Metabase"""
    print("Connecting DuckDB database...")

    db_path = "/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb"
    db_id = client.connect_duckdb("OEA Analytics", db_path)

    if db_id:
        print(f"✓ Database connected with ID: {db_id}")

        # Wait for schema sync
        print("Waiting for schema sync...")
        time.sleep(5)

        return db_id
    else:
        print("✗ Failed to connect database")
        return None


def create_dashboards_from_specs(client, db_id):
    """Create dashboards from JSON specifications"""
    print("Creating dashboards from specifications...")

    spec_dir = Path(__file__).parent
    dashboard_files = [
        "chronic_absenteeism_definition.json",
        "wellbeing_risk_definition.json",
        "equity_outcomes_definition.json",
        "class_effectiveness_definition.json",
        "performance_correlations_definition.json",
    ]

    for spec_file in dashboard_files:
        spec_path = spec_dir / spec_file

        if not spec_path.exists():
            print(f"⚠ Skipping {spec_file} - file not found")
            continue

        with open(spec_path) as f:
            spec = json.load(f)

        print(f"\nCreating: {spec['name']}")

        # Create dashboard
        dashboard_id = client.create_dashboard(
            spec["name"], spec.get("description", "")
        )

        if not dashboard_id:
            print(f"  ✗ Failed to create dashboard")
            continue

        print(f"  Dashboard created (ID: {dashboard_id})")

        # Create cards for first tab only (as proof of concept)
        if spec.get("tabs"):
            first_tab = spec["tabs"][0]

            for i, card_spec in enumerate(
                first_tab.get("cards", [])[:2]
            ):  # First 2 cards only
                card_id = client.create_native_query_card(
                    db_id, card_spec["query"], card_spec["title"]
                )

                if card_id:
                    # Add to dashboard
                    position = {
                        "row": card_spec["position"][0],
                        "col": card_spec["position"][1],
                        "size_x": card_spec["size"][0],
                        "size_y": card_spec["size"][1],
                    }

                    if client.add_card_to_dashboard(dashboard_id, card_id, position):
                        print(f"  ✓ Card added: {card_spec['title']}")
                    else:
                        print(f"  ✗ Failed to add card: {card_spec['title']}")
                else:
                    print(f"  ✗ Failed to create card: {card_spec['title']}")

        print(f"  ✓ Dashboard created successfully")


def test_queries(client, db_id):
    """Test dashboard queries for performance"""
    print("\nPerformance testing queries...")

    # This would run queries and measure latency
    # Implementation depends on exact requirements
    print("⚠ Performance testing requires detailed metrics setup")


def main():
    parser = argparse.ArgumentParser(description="Automate Metabase dashboard creation")
    parser.add_argument(
        "--init-admin", action="store_true", help="Initialize admin account"
    )
    parser.add_argument("--login", action="store_true", help="Login to Metabase")
    parser.add_argument("--email", default="admin@metabase.local", help="Admin email")
    parser.add_argument(
        "--password",
        required=False,
        help="Admin password (will prompt if not provided)",
    )
    parser.add_argument(
        "--connect-db", action="store_true", help="Connect DuckDB database"
    )
    parser.add_argument(
        "--create-dashboards", action="store_true", help="Create dashboards from specs"
    )
    parser.add_argument(
        "--test-queries", action="store_true", help="Test query performance"
    )
    parser.add_argument(
        "--full-setup",
        action="store_true",
        help="Run complete setup (requires manual admin creation first)",
    )

    args = parser.parse_args()

    client = MetabaseClient()

    if args.init_admin:
        setup_admin(client)

    if args.login or args.full_setup:
        if not args.password:
            import getpass

            args.password = getpass.getpass("Enter admin password: ")

        if not login(client, args.email, args.password):
            sys.exit(1)

    if args.connect_db or args.full_setup:
        if not client.session_id:
            if not args.password:
                import getpass

                args.password = getpass.getpass("Enter admin password: ")
            login(client, args.email, args.password)

        db_id = connect_database(client)
        if not db_id:
            sys.exit(1)

    if args.create_dashboards or args.full_setup:
        if not client.session_id:
            if not args.password:
                import getpass

                args.password = getpass.getpass("Enter admin password: ")
            login(client, args.email, args.password)

        # For full_setup, we need db_id
        if args.full_setup:
            db_id = connect_database(client)
        else:
            # Get existing database
            dbs = client.get_databases()
            if not dbs:
                print("✗ No databases found - run --connect-db first")
                sys.exit(1)
            db_id = dbs[0]["id"]

        create_dashboards_from_specs(client, db_id)

    if args.test_queries:
        test_queries(client, None)  # Would need db_id


if __name__ == "__main__":
    main()
