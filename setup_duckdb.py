#!/usr/bin/env python3
"""
Metabase DuckDB Database Setup Script
This script adds a DuckDB database to Metabase via the HTTP API
"""

import requests
import json
import sys
from typing import Optional, Dict, Any


class MetabaseAPI:
    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = base_url
        self.session = requests.Session()
        self.authenticated = False

        if username and password:
            self.login(username, password)

    def login(self, username: str, password: str) -> bool:
        """Authenticate with Metabase"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/session",
                json={"username": username, "password": password},
                timeout=10,
            )
            if response.status_code == 200:
                print(f"✓ Logged in as {username}")
                self.authenticated = True
                return True
            else:
                print(f"✗ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

    def get_databases(self) -> list:
        """Get list of existing databases"""
        try:
            response = self.session.get(f"{self.base_url}/api/database", timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("✗ Not authenticated. Please login first or provide credentials.")
                return []
            else:
                print(f"✗ Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"✗ Error getting databases: {e}")
            return []

    def add_duckdb_database(
        self,
        file_path: str,
        display_name: str = "OSS Analytics",
        description: str = "",
        read_only: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Add a DuckDB database to Metabase"""
        try:
            payload = {
                "name": display_name,
                "description": description,
                "engine": "duckdb",
                "details": {"db": file_path, "read_only": read_only},
                "is_full_sync": False,
                "auto_run_queries": True,
                "caching_ttl": 86400,
            }

            response = self.session.post(
                f"{self.base_url}/api/database", json=payload, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ DuckDB database added successfully!")
                print(f"  Name: {result.get('name')}")
                print(f"  ID: {result.get('id')}")
                print(f"  Engine: {result.get('engine')}")
                return result
            elif response.status_code == 401:
                print("✗ Not authenticated. Please login first or provide credentials.")
                return None
            else:
                print(f"✗ Failed to add database: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error adding database: {e}")
            return None

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    print("=" * 70)
    print("Metabase DuckDB Database Setup")
    print("=" * 70)

    # Configuration
    METABASE_URL = "http://localhost:3000"
    DUCKDB_FILE = (
        "/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb"
    )
    DB_NAME = "OSS Analytics"

    # Initialize API
    api = MetabaseAPI(METABASE_URL)

    # Test connection
    print("\n1. Testing Metabase connection...")
    if not api.test_connection():
        print(f"✗ Cannot connect to {METABASE_URL}")
        sys.exit(1)
    print(f"✓ Connected to Metabase")

    # Try login if credentials provided
    print("\n2. Checking authentication...")
    print("\nTo add the database, you need to either:")
    print("  a) Provide login credentials here")
    print("  b) Already be authenticated via browser")
    print(
        "\nEnter Metabase credentials (or press Enter to skip and use browser session):"
    )

    username = input("Username (default: admin): ").strip() or "admin"
    password = input("Password: ").strip()

    if password:
        if not api.login(username, password):
            print("\n✗ Authentication failed. Try manual setup:")
            print(f"  1. Go to {METABASE_URL}")
            print("  2. Log in with your credentials")
            print("  3. Follow the manual steps in setup_duckdb_metabase.md")
            sys.exit(1)
    else:
        print("\n⚠ Skipping login. If you get 'Unauthenticated' errors, login first.")

    # List existing databases
    print("\n3. Checking existing databases...")
    dbs = api.get_databases()
    if dbs:
        print(f"  Found {len(dbs)} database(s):")
        for db in dbs:
            print(
                f"    - {db.get('name')} (ID: {db.get('id')}, Engine: {db.get('engine')})"
            )

        # Check if OSS Analytics already exists
        if any(db.get("name") == DB_NAME for db in dbs):
            print(f"\n⚠ Database '{DB_NAME}' already exists!")
            print(
                "  If you want to reconfigure it, delete it from Admin Settings first."
            )
            sys.exit(0)

    # Add DuckDB database
    print(f"\n4. Adding DuckDB database: {DB_NAME}")
    print(f"  File: {DUCKDB_FILE}")
    print(f"  Read-only: true")

    result = api.add_duckdb_database(
        file_path=DUCKDB_FILE,
        display_name=DB_NAME,
        description="Open Source Student Analytics Database",
        read_only=True,
    )

    if result:
        print("\n" + "=" * 70)
        print("SUCCESS: DuckDB database added to Metabase")
        print("=" * 70)
        print(f"\nDatabase ID: {result.get('id')}")
        print(f"Database Name: {result.get('name')}")
        print(f"\nNext steps:")
        print(f"  1. Open {METABASE_URL}/admin/databases/{result.get('id')}")
        print(f"  2. Run a test query to verify the connection")
        print(f"  3. Create dashboards using this database")
    else:
        print("\n" + "=" * 70)
        print("FAILED: Could not add database via API")
        print("=" * 70)
        print("\nTry the manual setup:")
        print(f"  1. Go to {METABASE_URL}")
        print("  2. Click Settings (gear icon) > Admin Settings > Databases")
        print("  3. Click 'Add database' and select 'DuckDB'")
        print(f"  4. Configure with the settings above")


if __name__ == "__main__":
    main()
