#!/usr/bin/env python3
"""
publish_to_motherduck.py

Publishes dimension and fact tables from local DuckDB to MotherDuck cloud.

Usage:
    python publish_to_motherduck.py [--dry-run] [--tables dim_students,fact_enrollment]

Requirements:
    - MOTHERDUCK_TOKEN environment variable must be set
    - Local DuckDB database at ../data/oea.duckdb must exist
    - Tables must exist in local database before publishing

Phase 4.2 Implementation:
    1. Initialize MotherDuck database 'aeries_data_mart' with schemas
    2. Publish dimension tables (dim_students, dim_student_demographics)
    3. Publish fact tables (fact_enrollment, fact_academic_records, fact_discipline, fact_attendance)
    4. Verify data integrity (row counts match)
    5. Test hybrid queries (local + cloud)

Updated: Added stg_aeries__programs to staging tables
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MotherDuckPublisher:
    """Manages publishing local DuckDB tables to MotherDuck cloud."""

    # Schema configuration for MotherDuck
    SCHEMAS = ["raw", "staging", "core", "analytics", "privacy"]

    # Tables to publish (in dependency order)
    STAGING_TABLES = [
        "stg_aeries__students",
        "stg_aeries__attendance",
        "stg_aeries__academic_records",
        "stg_aeries__discipline",
        "stg_aeries__enrollment",
        "stg_aeries__programs",  # Added: Program participation data
    ]

    DIMENSION_TABLES = [
        "dim_students",
        "dim_student_demographics",
    ]

    FACT_TABLES = [
        "fact_enrollment",
        "fact_academic_records",
        "fact_discipline",
        "fact_attendance",
    ]

    ANALYTICS_TABLES = [
        "analytics_for_hex",           # Student-level analytics with race
        "equity_by_race",              # Aggregated equity outcomes by race
        "school_summary",              # School-level summary metrics
        "math_pathways_7th_grade",     # 7th grade Math 8 vs Apex Math 8
        "algebra_1_outcomes",          # 8th grade Algebra 1 outcomes
        "lead_program_enrollment",     # LEAD program 5-year demographics
        "math_8_cohort_tracking",      # Math 8 → Algebra 1 cohort tracking
        "math_8_enrollment_by_year",   # Math 8 enrollment by year
        "apex_math_8_enrollment_by_year", # Apex Math 8 enrollment by year
        "lead_enrollment_by_year",     # LEAD enrollment by year
    ]


    def __init__(self, local_db_path: str, motherduck_token: str, dry_run: bool = False):
        """
        Initialize publisher.

        Args:
            local_db_path: Path to local DuckDB database
            motherduck_token: MotherDuck authentication token
            dry_run: If True, only print what would be done
        """
        self.local_db_path = Path(local_db_path)
        self.motherduck_token = motherduck_token
        self.dry_run = dry_run

        if not self.local_db_path.exists():
            raise FileNotFoundError(f"Local database not found: {self.local_db_path}")

        logger.info(f"Initialized MotherDuckPublisher")
        logger.info(f"  Local DB: {self.local_db_path}")
        logger.info(f"  Dry run: {self.dry_run}")

    def _execute_sql(self, conn, sql: str, description: str | None = None):
        """Execute SQL and log results."""
        if description:
            logger.info(f"{description}")

        if self.dry_run:
            logger.info(f"  [DRY RUN] Would execute: {sql[:100]}...")
            return None

        try:
            result = conn.execute(sql).fetchall()
            logger.info(f"  ✓ Success")
            return result
        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            raise

    def connect_local(self):
        """Connect to local DuckDB database."""
        try:
            import duckdb

            conn = duckdb.connect(str(self.local_db_path), read_only=True)
            logger.info("✓ Connected to local DuckDB")
            return conn
        except Exception as e:
            logger.error(f"✗ Failed to connect to local DuckDB: {e}")
            raise

    def connect_motherduck(self):
        """Connect to MotherDuck cloud database."""
        try:
            import duckdb

            # Connect to MotherDuck with token
            # Format: md:database_name?motherduck_token=xxx
            md_connection_string = f"md:aeries_data_mart?motherduck_token={self.motherduck_token}"

            if self.dry_run:
                logger.info("[DRY RUN] Would connect to MotherDuck")
                return None

            conn = duckdb.connect(md_connection_string)
            logger.info("✓ Connected to MotherDuck")
            return conn
        except Exception as e:
            logger.error(f"✗ Failed to connect to MotherDuck: {e}")
            raise

    def initialize_motherduck_database(self, md_conn):
        """Create database and schemas if they don't exist."""
        logger.info("\n=== Initializing MotherDuck Database ===")

        # Create schemas
        for schema in self.SCHEMAS:
            sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"
            self._execute_sql(md_conn, sql, f"Creating schema: {schema}")

    def get_local_table_info(self, local_conn, schema: str, table: str) -> Tuple[int, str]:
        """
        Get row count and DDL for a local table.

        Returns:
            (row_count, create_statement)
        """
        # Get row count
        count_sql = f"SELECT COUNT(*) FROM {schema}.{table};"
        count_result = local_conn.execute(count_sql).fetchone()
        row_count = count_result[0] if count_result else 0

        # Get table schema (DDL)
        # DuckDB doesn't have SHOW CREATE TABLE, so we'll construct from DESCRIBE
        describe_sql = f"DESCRIBE {schema}.{table};"
        columns = local_conn.execute(describe_sql).fetchall()

        return row_count, columns

    def publish_table(self, local_conn, md_conn, local_schema: str, table: str):
        """
        Publish a single table from local to MotherDuck.

        Strategy:
            1. Get local table info (row count, schema)
            2. Drop existing table in MotherDuck (if exists)
            3. Create table in MotherDuck with same schema
            4. Insert data from local to MotherDuck
            5. Verify row counts match
        """
        # Map local schema to cloud schema
        cloud_schema = local_schema.replace("main_", "")

        logger.info(f"\n--- Publishing {local_schema}.{table} -> {cloud_schema}.{table} ---")

        # Get local table info
        try:
            local_row_count, columns = self.get_local_table_info(local_conn, local_schema, table)
            logger.info(f"  Local rows: {local_row_count:,}")
        except Exception as e:
            logger.error(f"  ✗ Failed to read local table: {e}")
            return False

        if self.dry_run:
            logger.info(f"  [DRY RUN] Would publish {local_row_count:,} rows to MotherDuck")
            return True

        try:
            # Attach local database to MotherDuck connection
            attach_sql = f"ATTACH '{self.local_db_path}' AS local_db (READ_ONLY);"
            md_conn.execute(attach_sql)
            logger.info(f"  ✓ Attached local database")

            # Drop existing table in MotherDuck
            drop_sql = f"DROP TABLE IF EXISTS {cloud_schema}.{table};"
            self._execute_sql(md_conn, drop_sql, f"Dropping existing table")

            # Create table and insert data in one operation
            # Use CREATE TABLE AS SELECT for efficiency
            create_sql = f"""
                CREATE TABLE {cloud_schema}.{table} AS 
                SELECT * FROM local_db.{local_schema}.{table};
            """
            self._execute_sql(md_conn, create_sql, f"Creating and populating table")

            # Verify row count
            verify_sql = f"SELECT COUNT(*) FROM {cloud_schema}.{table};"
            md_row_count = md_conn.execute(verify_sql).fetchone()[0]

            if md_row_count == local_row_count:
                logger.info(f"  ✓ Verified: {md_row_count:,} rows in MotherDuck")
                return True
            else:
                logger.error(
                    f"  ✗ Row count mismatch! Local: {local_row_count:,}, MotherDuck: {md_row_count:,}"
                )
                return False

        except Exception as e:
            logger.error(f"  ✗ Failed to publish table: {e}")
            return False
        finally:
            # Detach local database
            try:
                md_conn.execute("DETACH local_db;")
            except:
                pass

    def test_hybrid_query(self, local_conn, md_conn):
        """Test querying both local and cloud data together."""
        logger.info("\n=== Testing Hybrid Query ===")

        if self.dry_run:
            logger.info("[DRY RUN] Would test hybrid query")
            return True

        try:
            # Attach local database
            md_conn.execute(f"ATTACH '{self.local_db_path}' AS local_db (READ_ONLY);")

            # Test query joining local staging with cloud core
            test_sql = """
                SELECT 
                    'local_staging' as source,
                    COUNT(*) as row_count
                FROM local_db.main_staging.stg_aeries__students
                UNION ALL
                SELECT 
                    'cloud_core' as source,
                    COUNT(*) as row_count
                FROM core.dim_students;
            """

            result = md_conn.execute(test_sql).fetchall()
            logger.info("  ✓ Hybrid query successful:")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]:,} rows")

            return True

        except Exception as e:
            logger.error(f"  ✗ Hybrid query failed: {e}")
            return False
        finally:
            try:
                md_conn.execute("DETACH local_db;")
            except:
                pass

    def publish_all(self, table_filter: List[str] | None = None):
        """
        Publish all tables to MotherDuck.

        Args:
            table_filter: Optional list of specific tables to publish
        """
        logger.info("\n" + "=" * 60)
        logger.info("MOTHERDUCK PUBLICATION PROCESS")
        logger.info("=" * 60)

        # Connect to databases
        local_conn = self.connect_local()
        md_conn = self.connect_motherduck()

        if not self.dry_run:
            # Initialize MotherDuck database
            self.initialize_motherduck_database(md_conn)

        # Determine which tables to publish
        all_tables = self.STAGING_TABLES + self.DIMENSION_TABLES + self.FACT_TABLES + self.ANALYTICS_TABLES
        tables_to_publish = table_filter if table_filter else all_tables

        # Track results
        results = {"success": [], "failed": []}

        # Publish staging tables first
        logger.info("\n=== Publishing Staging Tables ===")
        for table in self.STAGING_TABLES:
            if table in tables_to_publish:
                # Staging tables are in main_staging schema locally, staging in MotherDuck
                success = self.publish_table(local_conn, md_conn, "main_staging", table)
                if success:
                    results["success"].append(table)
                else:
                    results["failed"].append(table)

        # Publish dimensions (facts may depend on them)
        logger.info("\n=== Publishing Dimension Tables ===")
        for table in self.DIMENSION_TABLES:
            if table in tables_to_publish:
                # Dimensions are in main_core schema locally, core in MotherDuck
                success = self.publish_table(local_conn, md_conn, "main_core", table)
                if success:
                    results["success"].append(table)
                else:
                    results["failed"].append(table)

        # Publish facts
        logger.info("\n=== Publishing Fact Tables ===")
        for table in self.FACT_TABLES:
            if table in tables_to_publish:
                # Facts are in main_core schema locally, core in MotherDuck
                success = self.publish_table(local_conn, md_conn, "main_core", table)
                if success:
                    results["success"].append(table)
                else:
                    results["failed"].append(table)


        # Publish analytics (for Hex dashboards)
        logger.info("\n=== Publishing Analytics Tables ===")
        for table in self.ANALYTICS_TABLES:
            if table in tables_to_publish:
                # Analytics are in main_main_analytics schema locally, analytics in MotherDuck
                success = self.publish_table(local_conn, md_conn, "main_main_analytics", table)
                if success:
                    results["success"].append(table)
                else:
                    results["failed"].append(table)

        # Test hybrid queries
        if not self.dry_run and md_conn:
            self.test_hybrid_query(local_conn, md_conn)

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("PUBLICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Successfully published: {len(results['success'])} tables")
        for table in results["success"]:
            logger.info(f"    - {table}")

        if results["failed"]:
            logger.info(f"✗ Failed to publish: {len(results['failed'])} tables")
            for table in results["failed"]:
                logger.info(f"    - {table}")

        # Close connections
        local_conn.close()
        if md_conn:
            md_conn.close()

        return len(results["failed"]) == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Publish DuckDB tables to MotherDuck cloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Publish all tables (dry run)
  python publish_to_motherduck.py --dry-run
  
  # Publish all tables
  python publish_to_motherduck.py
  
  # Publish specific tables only
  python publish_to_motherduck.py --tables dim_students,fact_enrollment
        """,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Print what would be done without making changes"
    )

    parser.add_argument(
        "--tables", type=str, help="Comma-separated list of tables to publish (default: all)"
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="../data/oea.duckdb",
        help="Path to local DuckDB database (default: ../data/oea.duckdb)",
    )

    args = parser.parse_args()

    # Check for MOTHERDUCK_TOKEN
    motherduck_token = os.environ.get("MOTHERDUCK_TOKEN")
    if not motherduck_token:
        logger.error("ERROR: MOTHERDUCK_TOKEN environment variable not set")
        logger.error("Please set your MotherDuck token:")
        logger.error("  export MOTHERDUCK_TOKEN='your_token_here'")
        sys.exit(1)

    # Parse table filter
    table_filter: List[str] | None = None
    if args.tables:
        table_filter = [t.strip() for t in args.tables.split(",")]

    # Create publisher and run
    try:
        publisher = MotherDuckPublisher(
            local_db_path=args.db_path, motherduck_token=motherduck_token, dry_run=args.dry_run
        )

        success = publisher.publish_all(table_filter=table_filter)

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
