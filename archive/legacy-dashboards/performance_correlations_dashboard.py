#!/usr/bin/env python3
"""
Performance Correlations Dashboard
Built with Plotly Dash - Production-ready analytics dashboarding
"""

import duckdb
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
import os
from pathlib import Path
from typing import Optional

class PerformanceCorrelationsDashboardDashboard:
    def __init__(self, duckdb_path: Optional[str] = None):
        default_path = Path(__file__).resolve().parent / "oss_framework" / "data" / "oea.duckdb"
        db_path = Path(duckdb_path or os.getenv("DUCKDB_DATABASE_PATH", str(default_path)))
        
        if not db_path.exists():
            raise FileNotFoundError(
                f"DuckDB database not found at {db_path}.\n"
                f"Run the data pipeline first: python scripts/run_pipeline.py\n"
                f"Or set DUCKDB_DATABASE_PATH environment variable."
            )
        
        self.db_path = str(db_path)
        self.conn = None
        self.app = Dash(__name__)

    def connect_database(self) -> bool:
        try:
            self.conn = duckdb.connect(self.db_path, read_only=True)
            result = self.conn.execute(
                "SELECT COUNT(*) as count FROM main_analytics.v_performance_correlations"
            ).fetchall()
            count = result[0][0] if result else 0
            print(f"✓ Connected to DuckDB. Found {count} records.")
            return count > 0
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def load_data(self) -> dict:
        try:
            data = {}
            query = "SELECT * FROM main_analytics.v_performance_correlations LIMIT 100"
            data['records'] = pd.DataFrame(self.conn.execute(query).fetchall())
            print("✓ All data loaded")
            return data
        except Exception as e:
            print(f"✗ Data loading failed: {e}")
            return {}

    def build_layout(self, data: dict):
        self.app.layout = html.Div([
            html.Div([
                html.H1("Performance Correlations Dashboard", style={"color": "#fff", "textAlign": "center", "paddingTop": "20px"}),
            ], style={"backgroundColor": "#2c3e50", "paddingBottom": "20px", "marginBottom": "30px"}),
            html.Div([
                html.H2("Dashboard Data"),
                html.P(f"Total records: {len(data.get('records', []))}")
            ], style={"padding": "20px"})
        ], style={"padding": "20px", "fontFamily": "Arial, sans-serif"})

    def run(self, host: str = "0.0.0.0", port: int = 8054, debug: bool = False):
        if not self.connect_database():
            return False
        data = self.load_data()
        if not data:
            return False
        self.build_layout(data)
        print(f"✓ Dashboard ready at http://localhost:{port}")
        self.app.run(host=host, port=port, debug=debug)
        return True

if __name__ == "__main__":
    dashboard = PerformanceCorrelationsDashboardDashboard()
    dashboard.run(port=8054, debug=True)
