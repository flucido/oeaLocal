#!/usr/bin/env python3
"""
Metabase Database Connection Verifier
Tests database connections in both Metabase instances
"""

import requests
import sys
import json
from getpass import getpass


def check_metabase_health(url):
    """Check if Metabase is running"""
    try:
        response = requests.get(f"{url}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def login_metabase(url, email, password):
    """Login to Metabase and get session token"""
    try:
        response = requests.post(
            f"{url}/api/session",
            json={"username": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def get_databases(url, session_token):
    """Get list of configured databases"""
    try:
        response = requests.get(
            f"{url}/api/database",
            headers={
                "Content-Type": "application/json",
                "X-Metabase-Session": session_token,
            },
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Failed to get databases: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching databases: {e}")
        return []


def test_database_query(url, session_token, database_id, query):
    """Test a SQL query against a database"""
    try:
        response = requests.post(
            f"{url}/api/dataset",
            headers={
                "Content-Type": "application/json",
                "X-Metabase-Session": session_token,
            },
            json={
                "database": database_id,
                "type": "native",
                "native": {"query": query},
            },
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "rows": len(data.get("data", {}).get("rows", [])),
                "columns": data.get("data", {}).get("cols", []),
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("=" * 70)
    print("Metabase Database Connection Verification")
    print("=" * 70)

    instances = [
        {"name": "oss-metabase", "url": "http://localhost:3000"},
        {"name": "sis-metabase", "url": "http://localhost:3001"},
    ]

    results = {}

    for instance in instances:
        name = instance["name"]
        url = instance["url"]

        print(f"\n\n📊 Testing: {name} ({url})")
        print("-" * 70)

        if not check_metabase_health(url):
            print(f"❌ {name} is not responding at {url}")
            results[name] = {"status": "unhealthy"}
            continue

        print(f"✅ {name} is healthy")

        print(f"\nEnter admin credentials for {name}:")
        email = input("Email: ").strip()
        if not email:
            print("⏭️  Skipping authentication test")
            results[name] = {"status": "healthy", "authenticated": False}
            continue

        password = getpass("Password: ")

        session_token = login_metabase(url, email, password)
        if not session_token:
            print(f"❌ Authentication failed")
            results[name] = {"status": "healthy", "authenticated": False}
            continue

        print(f"✅ Authentication successful")

        databases = get_databases(url, session_token)
        print(f"\n📦 Found {len(databases)} database(s):")

        if not databases:
            print("⚠️  No databases configured")
            results[name] = {
                "status": "healthy",
                "authenticated": True,
                "databases": [],
            }
            continue

        db_results = []
        for db in databases:
            db_id = db.get("id")
            db_name = db.get("name")
            db_engine = db.get("engine")

            print(f"\n  Database: {db_name}")
            print(f"    ID: {db_id}")
            print(f"    Engine: {db_engine}")

            if db_engine == "duckdb":
                print(f"    Testing DuckDB connection...")

                schema_test = test_database_query(
                    url,
                    session_token,
                    db_id,
                    "SELECT schema_name, table_name FROM information_schema.tables WHERE table_schema = 'main_main_analytics' LIMIT 5;",
                )

                if schema_test["success"]:
                    print(f"    ✅ Schema query: {schema_test['rows']} table(s) found")
                else:
                    print(f"    ❌ Schema query failed: {schema_test['error']}")

                data_test = test_database_query(
                    url,
                    session_token,
                    db_id,
                    "SELECT COUNT(*) as count FROM main_main_analytics.v_chronic_absenteeism_risk;",
                )

                if data_test["success"]:
                    print(f"    ✅ Data query: {data_test['rows']} row(s) returned")
                else:
                    print(f"    ❌ Data query failed: {data_test['error']}")

                db_results.append(
                    {
                        "name": db_name,
                        "engine": db_engine,
                        "schema_test": schema_test["success"],
                        "data_test": data_test["success"],
                    }
                )
            else:
                db_results.append(
                    {"name": db_name, "engine": db_engine, "tested": False}
                )

        results[name] = {
            "status": "healthy",
            "authenticated": True,
            "databases": db_results,
        }

    print_summary(results)


def print_summary(results):
    print("\n\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Status: {result.get('status', 'unknown')}")
        print(f"  Authenticated: {result.get('authenticated', False)}")

        databases = result.get("databases", [])
        if databases:
            print(f"  Databases: {len(databases)}")
            for db in databases:
                print(f"    - {db['name']} ({db['engine']})")
                if db.get("tested"):
                    schema_ok = "✅" if db.get("schema_test") else "❌"
                    data_ok = "✅" if db.get("data_test") else "❌"
                    print(f"      Schema: {schema_ok}  Data: {data_ok}")
        else:
            print(f"  Databases: 0")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
