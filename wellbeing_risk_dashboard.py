#!/usr/bin/env python3
"""
Wellbeing & Mental Health Risk Dashboard
Built with Plotly Dash - Production-ready analytics dashboarding
"""

import duckdb
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from datetime import datetime


class WellbeingRiskDashboard:
    def __init__(
        self,
        duckdb_path: str = "/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb",
    ):
        self.db_path = duckdb_path
        self.conn = None
        self.app = Dash(__name__)

    def connect_database(self) -> bool:
        """Connect to DuckDB"""
        try:
            self.conn = duckdb.connect(self.db_path, read_only=True)

            result = self.conn.execute(
                "SELECT COUNT(*) as count FROM main_main_analytics.v_wellbeing_risk_profiles"
            ).fetchall()

            count = result[0][0] if result else 0
            print(f"✓ Connected to DuckDB. Found {count} wellbeing profiles.")
            return count > 0
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def load_data(self) -> dict:
        """Load all required data"""
        try:
            data = {}

            # Get all wellbeing data
            query = """
                SELECT *
                FROM main_main_analytics.v_wellbeing_risk_profiles
                LIMIT 100
            """
            data["wellbeing"] = pd.DataFrame(self.conn.execute(query).fetchall())

            print("✓ All wellbeing data loaded")
            return data
        except Exception as e:
            print(f"✗ Data loading failed: {e}")
            return {}

    def build_layout(self, data: dict):
        """Build dashboard layout"""
        self.app.layout = html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Wellbeing & Mental Health Risk Dashboard",
                            style={
                                "color": "#fff",
                                "textAlign": "center",
                                "paddingTop": "20px",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#2c3e50",
                        "paddingBottom": "20px",
                        "marginBottom": "30px",
                    },
                ),
                html.Div(
                    [
                        html.H2("Wellbeing Risk Data"),
                        html.P(f"Total profiles: {len(data.get('wellbeing', []))}"),
                    ],
                    style={"padding": "20px"},
                ),
            ],
            style={"padding": "20px", "fontFamily": "Arial, sans-serif"},
        )

    def run(self, host: str = "0.0.0.0", port: int = 8051, debug: bool = False):
        """Run the dashboard"""
        if not self.connect_database():
            return False

        data = self.load_data()
        if not data:
            return False

        self.build_layout(data)
        print(f"✓ Wellbeing dashboard ready at http://localhost:{port}")
        self.app.run(host=host, port=port, debug=debug)
        return True


if __name__ == "__main__":
    dashboard = WellbeingRiskDashboard()
    dashboard.run(port=8051, debug=True)
