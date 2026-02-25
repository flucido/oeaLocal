import duckdb
import os
import sys

try:
    con = duckdb.connect("../../data/oea.duckdb")
    con.execute("INSTALL motherduck; LOAD motherduck;")
    token = os.environ.get("MOTHERDUCK_TOKEN")
    
    # We execute against the local db and attach motherduck
    con.execute(f"ATTACH 'md:aeries_data_mart' AS md (MOTHERDUCK_TOKEN '{token}');")
    
    con.execute("CREATE SCHEMA IF NOT EXISTS md.main_main_analytics;")
    tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main_main_analytics' AND table_catalog='oea'").fetchall()
    for t in tables:
        t_name = t[0]
        print(f"Copying {t_name}...")
        con.execute(f"CREATE OR REPLACE TABLE md.main_main_analytics.{t_name} AS SELECT * FROM oea.main_main_analytics.{t_name}")
        
    print("\nCopying complete!")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
