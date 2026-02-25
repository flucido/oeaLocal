#!/usr/bin/env python3
"""
Verify DuckDB database setup in Metabase
Run this AFTER you've manually added the database in Metabase
"""

import requests
import json
import sys


def verify_setup():
    print("=" * 70)
    print("DuckDB Database Setup Verification")
    print("=" * 70)

    METABASE_URL = "http://localhost:3000"
    DUCKDB_FILE = (
        "/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb"
    )
    DB_NAME = "OSS Analytics"

    # Step 1: Check if Metabase is running
    print("\n1. Checking Metabase connection...")
    try:
        response = requests.get(f"{METABASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✓ Metabase is running at {METABASE_URL}")
        else:
            print(f"   ✗ Metabase returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Cannot connect to Metabase: {e}")
        return False

    # Step 2: Check if DuckDB file exists
    print("\n2. Checking DuckDB file...")
    import os

    if os.path.exists(DUCKDB_FILE):
        size_mb = os.path.getsize(DUCKDB_FILE) / (1024 * 1024)
        print(f"   ✓ DuckDB file exists ({size_mb:.1f} MB)")
    else:
        print(f"   ✗ DuckDB file not found: {DUCKDB_FILE}")
        return False

    # Step 3: Try to list databases (requires login)
    print("\n3. Attempting to list databases...")
    print("   (This requires authentication - you may need to provide credentials)")

    session = requests.Session()

    # Try to get databases without auth first
    response = session.get(f"{METABASE_URL}/api/database")

    if response.status_code == 401:
        print("   ⚠ Not authenticated. Prompting for login...")

        # Get login credentials
        username = input("\n   Enter Metabase username: ").strip()
        password = input("   Enter Metabase password: ").strip()

        # Try to login
        login_response = session.post(
            f"{METABASE_URL}/api/session",
            json={"username": username, "password": password},
        )

        if login_response.status_code != 200:
            print(f"   ✗ Login failed: {login_response.status_code}")
            print("   Please verify your credentials and try again")
            return False

        print(f"   ✓ Logged in as {username}")

        # Try again
        response = session.get(f"{METABASE_URL}/api/database")

    if response.status_code == 200:
        databases = response.json()
        print(f"   ✓ Found {len(databases)} database(s)")

        # Look for OSS Analytics
        oss_db = None
        for db in databases:
            print(
                f"      - {db.get('name')} (ID: {db.get('id')}, Engine: {db.get('engine')})"
            )
            if db.get("name") == DB_NAME:
                oss_db = db

        if oss_db:
            print(f"\n   ✓ Found '{DB_NAME}' database!")
            print(f"      Database ID: {oss_db.get('id')}")
            print(f"      Engine: {oss_db.get('engine')}")
            print(f"      Tables: {oss_db.get('tables_count', 'Unknown')}")

            # Try to get more details
            db_id = oss_db.get("id")
            details_response = session.get(f"{METABASE_URL}/api/database/{db_id}")

            if details_response.status_code == 200:
                details = details_response.json()
                print(f"\n   Database Details:")
                print(f"      Created: {details.get('created_at', 'Unknown')}")
                print(
                    f"      Initial Sync: {details.get('initial_sync_status', 'Unknown')}"
                )
                print(
                    f"      Auto Run Queries: {details.get('auto_run_queries', 'Unknown')}"
                )

                # Check if tables are synced
                if details.get("tables_count", 0) > 0:
                    print(f"      Tables Found: {details.get('tables_count')}")
                    print(f"\n   ✓ DATABASE SETUP SUCCESSFUL!")
                else:
                    print(
                        f"      ⚠ No tables found yet - sync may still be in progress"
                    )

            return True
        else:
            print(f"\n   ✗ Database '{DB_NAME}' not found")
            print(f"      Please check if it was added with the correct name")
            return False
    else:
        print(f"   ✗ Failed to get databases: {response.status_code}")
        print(f"      Response: {response.text}")
        return False


if __name__ == "__main__":
    success = verify_setup()

    print("\n" + "=" * 70)
    if success:
        print("✓ Setup appears to be complete!")
        print("\nNext steps:")
        print("  1. Go to http://localhost:3000")
        print("  2. Create a new dashboard")
        print("  3. Add questions from the OSS Analytics database")
        sys.exit(0)
    else:
        print("✗ Setup verification failed")
        print("\nNext steps:")
        print("  1. Verify DuckDB file path is correct")
        print("  2. Check Metabase is running (http://localhost:3000)")
        print("  3. Manually add the database through the UI")
        print("  4. Run this script again to verify")
        sys.exit(1)
