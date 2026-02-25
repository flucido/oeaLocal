import duckdb
import os
import sys

# Connect to MotherDuck
try:
    con = duckdb.connect("md:aeries_data_mart")
    
    # List all tables and schemas
    print("--- Schemas and Tables ---")
    res = con.execute("""
        SELECT table_schema, table_name, table_type 
        FROM information_schema.tables 
        ORDER BY table_schema, table_name
    """).fetchall()
    for row in res:
        print(f"{row[0]}.{row[1]} ({row[2]})")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
