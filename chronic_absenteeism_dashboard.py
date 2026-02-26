#!/usr/bin/env python3
"""
Chronic Absenteeism Risk Dashboard
Built with Plotly Dash - Production-ready analytics dashboarding
"""

import duckdb
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from datetime import datetime
import os
from pathlib import Path
from typing import Optional


class ChronicAbsenteeismDashboard:
    def __init__(
        self,
        duckdb_path: Optional[str] = None,
    ):
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
        """Connect to DuckDB"""
        try:
            self.conn = duckdb.connect(self.db_path, read_only=True)

            # Verify data is accessible
            result = self.conn.execute(
                "SELECT COUNT(*) as count FROM main_main_analytics.v_chronic_absenteeism_risk"
            ).fetchall()

            count = result[0][0] if result else 0
            print(f"✓ Connected to DuckDB. Found {count} at-risk students.")
            return count > 0
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

    def load_data(self) -> dict:
        """Load all required data from database"""
        try:
            data = {}

            # 1. Students at risk (High/Critical)
            query = """
                SELECT COUNT(DISTINCT student_key) as count
                FROM main_main_analytics.v_chronic_absenteeism_risk
                WHERE risk_level IN ('High', 'Critical')
            """
            data["at_risk_count"] = self.conn.execute(query).fetchall()[0][0]

            # 2. Chronic absence rate
            query = """
                SELECT
                    ROUND(
                        COUNT(CASE WHEN risk_level != 'Low' THEN 1 END) * 100.0 /
                        COUNT(DISTINCT student_key),
                        1
                    ) as rate
                FROM main_main_analytics.v_chronic_absenteeism_risk
            """
            data["chronic_rate"] = self.conn.execute(query).fetchall()[0][0]

            # 3. Declining attendance
            query = """
                SELECT COUNT(DISTINCT student_key) as count
                FROM main_main_analytics.v_chronic_absenteeism_risk
                WHERE attendance_trend_90d = 'declining'
            """
            data["declining_count"] = self.conn.execute(query).fetchall()[0][0]

            # 4. Risk distribution
            query = """
                SELECT risk_level, COUNT(DISTINCT student_key) as count
                FROM main_main_analytics.v_chronic_absenteeism_risk
                GROUP BY risk_level
                ORDER BY risk_level
            """
            data["risk_dist"] = pd.DataFrame(
                self.conn.execute(query).fetchall(), columns=["risk_level", "count"]
            )

            # 5. Top at-risk students
            query = """
                SELECT
                    student_key as student_id,
                    risk_level,
                    ROUND(attendance_rate_30d, 1) as absence_rate,
                    attendance_trend_90d as trend,
                    COALESCE(_loaded_at::varchar, 'N/A') as last_update
                FROM main_main_analytics.v_chronic_absenteeism_risk
                WHERE risk_level IN ('High', 'Critical')
                ORDER BY chronic_absenteeism_risk_score DESC
                LIMIT 50
            """
            data["top_students"] = pd.DataFrame(
                self.conn.execute(query).fetchall(),
                columns=[
                    "Student ID",
                    "Risk Level",
                    "Attendance %",
                    "Trend",
                    "Last Update",
                ],
            )

            # 6. Attendance trends by grade
            query = """
                SELECT
                    grade_level as grade,
                    COUNT(DISTINCT student_key) as total_students,
                    COUNT(CASE WHEN risk_level = 'High' THEN 1 END) as high_count,
                    COUNT(CASE WHEN risk_level = 'Critical' THEN 1 END) as critical_count,
                    ROUND(AVG(CASE WHEN attendance_trend_90d = 'declining' THEN 1 ELSE 0 END) * 100, 1) as pct_declining
                FROM main_main_analytics.v_chronic_absenteeism_risk
                GROUP BY grade_level
                ORDER BY grade_level
            """
            data["by_grade"] = pd.DataFrame(
                self.conn.execute(query).fetchall(),
                columns=["Grade", "Total", "High Risk", "Critical", "% Declining"],
            )

            print("✓ All data loaded successfully")
            return data
        except Exception as e:
            print(f"✗ Data loading failed: {e}")
            return {}

    def build_layout(self, data: dict):
        """Build Dash layout"""
        self.app.layout = html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Chronic Absenteeism Risk Dashboard",
                            style={
                                "color": "#fff",
                                "textAlign": "center",
                                "paddingTop": "20px",
                            },
                        ),
                        html.P(
                            "Real-time student absenteeism analytics",
                            style={"color": "#ddd", "textAlign": "center"},
                        ),
                    ],
                    style={
                        "backgroundColor": "#2c3e50",
                        "paddingBottom": "20px",
                        "marginBottom": "30px",
                    },
                ),
                # Top metrics row
                html.Div(
                    [
                        # At Risk Count
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Students at Risk",
                                            style={
                                                "color": "#7f8c8d",
                                                "fontSize": "14px",
                                            },
                                        ),
                                        html.H2(
                                            f"{data.get('at_risk_count', 0):,}",
                                            style={
                                                "color": "#e74c3c",
                                                "fontSize": "36px",
                                            },
                                        ),
                                        html.P(
                                            "High/Critical Risk Level",
                                            style={
                                                "color": "#95a5a6",
                                                "fontSize": "12px",
                                            },
                                        ),
                                    ],
                                    style={"padding": "20px"},
                                )
                            ],
                            style={
                                "backgroundColor": "#ecf0f1",
                                "borderRadius": "8px",
                                "flex": "1",
                                "margin": "10px",
                            },
                        ),
                        # Chronic Rate
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Chronic Absence Rate",
                                            style={
                                                "color": "#7f8c8d",
                                                "fontSize": "14px",
                                            },
                                        ),
                                        html.H2(
                                            f"{data.get('chronic_rate', 0):.1f}%",
                                            style={
                                                "color": "#f39c12",
                                                "fontSize": "36px",
                                            },
                                        ),
                                        html.P(
                                            "Of student population",
                                            style={
                                                "color": "#95a5a6",
                                                "fontSize": "12px",
                                            },
                                        ),
                                    ],
                                    style={"padding": "20px"},
                                )
                            ],
                            style={
                                "backgroundColor": "#ecf0f1",
                                "borderRadius": "8px",
                                "flex": "1",
                                "margin": "10px",
                            },
                        ),
                        # Declining
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Declining Attendance",
                                            style={
                                                "color": "#7f8c8d",
                                                "fontSize": "14px",
                                            },
                                        ),
                                        html.H2(
                                            f"{data.get('declining_count', 0):,}",
                                            style={
                                                "color": "#e67e22",
                                                "fontSize": "36px",
                                            },
                                        ),
                                        html.P(
                                            "Last 30 days trend",
                                            style={
                                                "color": "#95a5a6",
                                                "fontSize": "12px",
                                            },
                                        ),
                                    ],
                                    style={"padding": "20px"},
                                )
                            ],
                            style={
                                "backgroundColor": "#ecf0f1",
                                "borderRadius": "8px",
                                "flex": "1",
                                "margin": "10px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "marginBottom": "30px",
                    },
                ),
                # Charts row
                html.Div(
                    [
                        # Risk Distribution Bar
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=px.bar(
                                        data["risk_dist"],
                                        x="risk_level",
                                        y="count",
                                        title="Risk Level Distribution",
                                        color="risk_level",
                                        color_discrete_map={
                                            "Critical": "#c0392b",
                                            "High": "#e74c3c",
                                            "Medium": "#f39c12",
                                            "Low": "#27ae60",
                                        },
                                    )
                                )
                            ],
                            style={"flex": "1", "margin": "10px"},
                        ),
                        # Risk Pie
                        html.Div(
                            [
                                dcc.Graph(
                                    figure=px.pie(
                                        data["risk_dist"],
                                        values="count",
                                        names="risk_level",
                                        title="Risk Level Breakdown",
                                        color_discrete_map={
                                            "Critical": "#c0392b",
                                            "High": "#e74c3c",
                                            "Medium": "#f39c12",
                                            "Low": "#27ae60",
                                        },
                                    )
                                )
                            ],
                            style={"flex": "1", "margin": "10px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "marginBottom": "30px",
                    },
                ),
                # Top Students Table
                html.Div(
                    [
                        html.H3("Top 50 At-Risk Students"),
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th(
                                                col,
                                                style={
                                                    "padding": "10px",
                                                    "textAlign": "left",
                                                    "backgroundColor": "#34495e",
                                                    "color": "#fff",
                                                },
                                            )
                                            for col in data["top_students"].columns
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    [
                                        html.Tr(
                                            [
                                                html.Td(
                                                    str(val),
                                                    style={
                                                        "padding": "8px",
                                                        "borderBottom": "1px solid #ddd",
                                                    },
                                                )
                                                for val in row
                                            ]
                                        )
                                        for row in data["top_students"].values
                                    ]
                                ),
                            ],
                            style={
                                "width": "100%",
                                "borderCollapse": "collapse",
                                "marginBottom": "30px",
                            },
                        ),
                    ]
                ),
                # Grade-level table
                html.Div(
                    [
                        html.H3("Attendance Trends by Grade"),
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th(
                                                col,
                                                style={
                                                    "padding": "10px",
                                                    "textAlign": "left",
                                                    "backgroundColor": "#34495e",
                                                    "color": "#fff",
                                                },
                                            )
                                            for col in data["by_grade"].columns
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    [
                                        html.Tr(
                                            [
                                                html.Td(
                                                    str(val),
                                                    style={
                                                        "padding": "8px",
                                                        "borderBottom": "1px solid #ddd",
                                                    },
                                                )
                                                for val in row
                                            ]
                                        )
                                        for row in data["by_grade"].values
                                    ]
                                ),
                            ],
                            style={"width": "100%", "borderCollapse": "collapse"},
                        ),
                    ]
                ),
            ],
            style={
                "padding": "20px",
                "fontFamily": "Arial, sans-serif",
                "maxWidth": "1400px",
                "margin": "0 auto",
            },
        )

    def run(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """Run the dashboard"""
        if not self.connect_database():
            print("✗ Failed to connect to database")
            return False

        data = self.load_data()
        if not data:
            print("✗ Failed to load data")
            return False

        self.build_layout(data)

        print(f"✓ Dashboard ready at http://localhost:{port}")
        print("  Starting server...")
        self.app.run(host=host, port=port, debug=debug)
        return True


if __name__ == "__main__":
    dashboard = ChronicAbsenteeismDashboard()
    dashboard.run(port=8050, debug=True)
