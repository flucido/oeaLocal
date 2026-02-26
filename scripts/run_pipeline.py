#!/usr/bin/env python3
"""
run_pipeline.py - Simple orchestration for local-data-stack

Replaces Dagster with a straightforward Python script that runs:
1. Stage 1: Data ingestion (Aeries API + Excel imports via dlt)
2. Stage 2: Data refinement (dbt transformations)
3. Stage 3: Analytics marts (dbt analytics models)

No cloud dependencies. All processing happens locally with DuckDB.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PipelineOrchestrator:
    """Simple orchestrator for the local data pipeline."""

    def __init__(self, dbt_project_dir: Optional[str] = None):
        self.project_root = project_root
        self.dbt_project_dir = dbt_project_dir or self.project_root / "oss_framework" / "dbt"
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Simple logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_command(self, cmd: str, description: str, workdir: Optional[Path] = None) -> bool:
        """
        Run a shell command and return success status.

        Args:
            cmd: Command to execute
            description: Human-readable description
            workdir: Working directory (defaults to project root)

        Returns:
            True if command succeeded (exit code 0), False otherwise
        """
        self.log(f"Starting: {description}")
        self.log(f"Command: {cmd}")

        cwd = workdir or self.project_root

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            if result.returncode == 0:
                self.log(f"✓ Completed: {description}", "SUCCESS")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                self.log(f"✗ Failed: {description}", "ERROR")
                if result.stderr:
                    print(f"Error output:\n{result.stderr}")
                if result.stdout:
                    print(f"Standard output:\n{result.stdout}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"✗ Timeout: {description}", "ERROR")
            return False
        except Exception as e:
            self.log(f"✗ Exception: {description} - {str(e)}", "ERROR")
            return False

    def stage1_ingestion(self) -> bool:
        """
        Stage 1: Ingest raw data from external sources.

        Runs dlt pipelines to extract data from:
        - Aeries API (student, enrollment, attendance, grades)
        - Excel imports (supplemental data)

        Writes to: data/stage1/raw/
        """
        self.log("=== STAGE 1: DATA INGESTION ===")

        # Check if ingestion scripts exist
        aeries_pipeline = (
            self.project_root / "oss_framework" / "pipelines" / "aeries_dlt_pipeline.py"
        )
        excel_pipeline = (
            self.project_root / "oss_framework" / "pipelines" / "excel_imports_dlt_pipeline.py"
        )

        success = True

        if aeries_pipeline.exists():
            success = success and self.run_command(
                f"python {aeries_pipeline}", "Aeries API ingestion (dlt)"
            )
        else:
            self.log(f"Skipping: {aeries_pipeline} not found", "WARNING")

        if excel_pipeline.exists():
            success = success and self.run_command(
                f"python {excel_pipeline}", "Excel imports ingestion (dlt)"
            )
        else:
            self.log(f"Skipping: {excel_pipeline} not found", "WARNING")

        return success

    def stage2_refinement(self) -> bool:
        """
        Stage 2: Refine and standardize raw data.

        Runs dbt models tagged with 'stage2' or in mart_core.
        Applies data quality, normalization, deduplication.

        Writes to: DuckDB tables in mart_core schema
        """
        self.log("=== STAGE 2: DATA REFINEMENT ===")

        return self.run_command(
            "dbt run --select tag:staging",
            "dbt refinement models (staging layer)",
            workdir=self.dbt_project_dir,
        )

    def stage3_analytics(self) -> bool:
        """
        Stage 3: Build analytics marts and aggregations.

        Runs dbt models for:
        - Feature engineering (mart_features)
        - Risk scoring (mart_scoring)
        - Analytics views (mart_analytics)

        Writes to: DuckDB tables in analytics schemas
        """
        self.log("=== STAGE 3: ANALYTICS MARTS ===")

        # Seed required mapping tables first
        success = self.run_command(
            "dbt seed --select school_cds_mapping_seed",
            "dbt seed school mapping table",
            workdir=self.dbt_project_dir,
        )

        # Build privacy layer required by core marts
        if success:
            success = success and self.run_command(
                "dbt run --select mart_privacy",
                "dbt privacy pseudonymization models",
                workdir=self.dbt_project_dir,
            )

        # Run core marts
        if success:
            success = success and self.run_command(
                "dbt run --select mart_core",
                "dbt core dimension/fact tables",
                workdir=self.dbt_project_dir,
            )

        # Then features, scoring, and analytics
        if success:
            success = success and self.run_command(
                "dbt run --select mart_features mart_scoring mart_analytics",
                "dbt analytics models",
                workdir=self.dbt_project_dir,
            )

        return success

    def run_tests(self) -> bool:
        """Run dbt tests to validate data quality."""
        self.log("=== RUNNING DATA QUALITY TESTS ===")

        return self.run_command("dbt test", "dbt data quality tests", workdir=self.dbt_project_dir)

    def run_full_pipeline(self, skip_tests: bool = False) -> bool:
        """
        Run the complete data pipeline.

        Args:
            skip_tests: If True, skip dbt test execution

        Returns:
            True if all stages succeeded
        """
        self.log("╔═══════════════════════════════════════════════════╗")
        self.log("║   LOCAL DATA STACK PIPELINE - FULL RUN          ║")
        self.log("╚═══════════════════════════════════════════════════╝")

        # Stage 1: Ingestion
        if not self.stage1_ingestion():
            self.log("Pipeline failed at Stage 1 (Ingestion)", "ERROR")
            return False

        # Stage 2: Refinement
        if not self.stage2_refinement():
            self.log("Pipeline failed at Stage 2 (Refinement)", "ERROR")
            return False

        # Stage 3: Analytics
        if not self.stage3_analytics():
            self.log("Pipeline failed at Stage 3 (Analytics)", "ERROR")
            return False

        # Tests (optional)
        if not skip_tests:
            if not self.run_tests():
                self.log("Data quality tests failed (pipeline completed)", "WARNING")

        # Success summary
        elapsed = datetime.now() - self.start_time
        self.log("╔═══════════════════════════════════════════════════╗")
        self.log("║   PIPELINE COMPLETED SUCCESSFULLY                ║")
        self.log(f"║   Duration: {elapsed}                           ║")
        self.log("╚═══════════════════════════════════════════════════╝")

        return True


def main():
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Local Data Stack Pipeline Orchestrator")
    parser.add_argument(
        "--stage",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Run specific stage or entire pipeline (default: all)",
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip dbt tests after pipeline run"
    )
    parser.add_argument(
        "--dbt-dir", type=str, help="Path to dbt project directory (default: oss_framework/dbt)"
    )

    args = parser.parse_args()

    orchestrator = PipelineOrchestrator(dbt_project_dir=args.dbt_dir)

    # Run requested stage(s)
    if args.stage == "1":
        success = orchestrator.stage1_ingestion()
    elif args.stage == "2":
        success = orchestrator.stage2_refinement()
    elif args.stage == "3":
        success = orchestrator.stage3_analytics()
    else:  # "all"
        success = orchestrator.run_full_pipeline(skip_tests=args.skip_tests)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
