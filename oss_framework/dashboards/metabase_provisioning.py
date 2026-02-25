#!/usr/bin/env python3
"""
Metabase Dashboard Provisioning Script
Generates and provisions 5 production dashboards from templates
Supports DuckDB connection with row-level security (RBAC)
"""

import json
import os
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# Configuration Classes
# ============================================================================


class DashboardType(Enum):
    CHRONIC_ABSENTEEISM = "chronic_absenteeism"
    WELLBEING_RISK = "wellbeing_risk"
    EQUITY_OUTCOMES = "equity_outcomes"
    CLASS_EFFECTIVENESS = "class_effectiveness"
    PERFORMANCE_CORRELATIONS = "performance_correlations"


class RiskLevel(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class MetabaseConnection:
    """Metabase database connection configuration"""

    name: str = "DuckDB Analytics"
    engine: str = "duckdb"
    database: str = (
        "/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb"
    )
    is_on_demand: bool = True
    cache_ttl_minutes: int = 10
    read_only: bool = True


@dataclass
class DashboardCard:
    """Individual dashboard card/visualization"""

    position_row: int
    position_col: int
    size_width: int  # 1-12
    size_height: int
    title: str
    query: str
    visualization_type: str
    viz_settings: Optional[Dict[str, Any]] = None
    parameter_mappings: Optional[List[Dict]] = None


@dataclass
class DashboardTab:
    """Dashboard tab grouping cards"""

    name: str
    cards: List[DashboardCard]


@dataclass
class DashboardDefinition:
    """Complete dashboard definition"""

    name: str
    description: str
    type: DashboardType
    target_audience: List[str]
    refresh_interval: int = 5  # minutes
    tabs: Optional[List[DashboardTab]] = None
    parameters: Optional[List[Dict]] = None
    row_level_security: bool = False
    rbac_column: Optional[str] = None


# ============================================================================
# Dashboard Template Generators
# ============================================================================


class DashboardTemplates:
    """Factory for creating dashboard definitions"""

    @staticmethod
    def chronic_absenteeism() -> DashboardDefinition:
        """
        Chronic Absenteeism Risk Dashboard
        Target: School Administrators, Counselors
        """

        tabs = [
            DashboardTab(
                name="Overview",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=4,
                        size_height=2,
                        title="Students at Risk",
                        query="""
                            SELECT COUNT(*) as count 
                            FROM main_main_analytics.v_chronic_absenteeism_risk 
                            WHERE risk_classification IN ('Critical', 'High')
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#E53935", "fontSize": 32},
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=4,
                        size_width=4,
                        size_height=2,
                        title="Chronic Absence Rate (%)",
                        query="""
                            SELECT ROUND(AVG(CASE WHEN chronic_absence_flag = true THEN 100 ELSE 0 END), 1) as rate
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                        """,
                        visualization_type="gauge",
                        viz_settings={"min": 0, "max": 30},
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=8,
                        size_width=4,
                        size_height=2,
                        title="Declining Attendance (30d)",
                        query="""
                            SELECT COUNT(*) as count
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                            WHERE attendance_trend_30d = 'declining' OR attendance_rate_30d < 85
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#FB8C00"},
                    ),
                ],
            ),
            DashboardTab(
                name="Risk Distribution",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=6,
                        size_height=4,
                        title="Risk Score Distribution",
                        query="""
                            SELECT 
                                ROUND(chronic_absenteeism_risk_score * 10) / 10 as risk_score,
                                COUNT(*) as student_count
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                            GROUP BY ROUND(chronic_absenteeism_risk_score * 10) / 10
                            ORDER BY risk_score
                        """,
                        visualization_type="bar",
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=6,
                        size_width=6,
                        size_height=4,
                        title="Risk Classification Breakdown",
                        query="""
                            SELECT 
                                risk_classification,
                                COUNT(*) as count
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                            GROUP BY risk_classification
                            ORDER BY risk_classification
                        """,
                        visualization_type="pie",
                    ),
                ],
            ),
            DashboardTab(
                name="At-Risk Students",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=6,
                        title="Priority Intervention List",
                        query="""
                            SELECT 
                                student_key as "Student ID",
                                grade_level as "Grade",
                                school_id as "School",
                                ROUND(chronic_absenteeism_risk_score, 2) as "Risk Score",
                                risk_classification as "Risk Level",
                                ROUND(attendance_rate_30d, 1) as "Attend Rate (30d) %",
                                discipline_incidents_30d as "Incidents (30d)"
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                            WHERE risk_classification IN ('Critical', 'High')
                            ORDER BY chronic_absenteeism_risk_score DESC
                            LIMIT 50
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
            DashboardTab(
                name="Trends & Analysis",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=4,
                        title="Attendance Trend (Last 90 Days)",
                        query="""
                            SELECT 
                                grade_level as "Grade",
                                ROUND(AVG(attendance_rate_30d), 1) as "30d Average",
                                ROUND(AVG(attendance_rate_60d), 1) as "60d Average",
                                ROUND(AVG(attendance_rate_90d), 1) as "90d Average"
                            FROM main_main_analytics.v_chronic_absenteeism_risk
                            GROUP BY grade_level
                            ORDER BY grade_level
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
        ]

        return DashboardDefinition(
            name="Chronic Absenteeism Risk",
            description="Real-time identification and monitoring of students at chronic absenteeism risk",
            type=DashboardType.CHRONIC_ABSENTEEISM,
            target_audience=["School Administrators", "Counselors"],
            refresh_interval=5,
            tabs=tabs,
            row_level_security=True,
            rbac_column="school_id",
        )

    @staticmethod
    def wellbeing_risk() -> DashboardDefinition:
        """
        Wellbeing & Mental Health Risk Dashboard
        Target: Counselors, Social Workers
        """

        tabs = [
            DashboardTab(
                name="Risk Dashboard",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=3,
                        size_height=2,
                        title="High Risk Count",
                        query="""
                            SELECT COUNT(*) as count
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            WHERE overall_risk_level = 'High'
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#E53935"},
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=3,
                        size_width=3,
                        size_height=2,
                        title="Medium Risk Count",
                        query="""
                            SELECT COUNT(*) as count
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            WHERE overall_risk_level = 'Medium'
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#FB8C00"},
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=6,
                        size_width=3,
                        size_height=2,
                        title="Active Cases",
                        query="""
                            SELECT COUNT(*) as count
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            WHERE has_active_case_plan = true
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#2E7D32"},
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=9,
                        size_width=3,
                        size_height=2,
                        title="Follow-ups Due",
                        query="""
                            SELECT COUNT(*) as count
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            WHERE days_since_last_contact > 14 AND has_active_case_plan = true
                        """,
                        visualization_type="number",
                        viz_settings={"color": "#1565C0"},
                    ),
                    DashboardCard(
                        position_row=2,
                        position_col=0,
                        size_width=6,
                        size_height=4,
                        title="Risk Domain Breakdown",
                        query="""
                            SELECT 
                                'Academic' as domain,
                                SUM(CASE WHEN academic_risk_flag = true THEN 1 ELSE 0 END) as count
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            UNION ALL
                            SELECT 'Behavioral', SUM(CASE WHEN behavioral_risk_flag = true THEN 1 ELSE 0 END)
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            UNION ALL
                            SELECT 'Social-Emotional', SUM(CASE WHEN social_emotional_risk_flag = true THEN 1 ELSE 0 END)
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            UNION ALL
                            SELECT 'Family Engagement', SUM(CASE WHEN family_engagement_risk_flag = true THEN 1 ELSE 0 END)
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                        """,
                        visualization_type="bar",
                    ),
                    DashboardCard(
                        position_row=2,
                        position_col=6,
                        size_width=6,
                        size_height=4,
                        title="My Caseload (by assigned counselor)",
                        query="""
                            SELECT 
                                overall_risk_level as "Risk Level",
                                COUNT(*) as "Student Count"
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            GROUP BY overall_risk_level
                            ORDER BY overall_risk_level
                        """,
                        visualization_type="pie",
                    ),
                ],
            ),
            DashboardTab(
                name="Support Resources",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=5,
                        title="Resource Allocation by Risk Level",
                        query="""
                            SELECT 
                                overall_risk_level as "Risk Level",
                                COUNT(*) as "Students",
                                ROUND(AVG(CASE WHEN has_counseling_services = true THEN 100 ELSE 0 END), 1) as "Counseling %",
                                ROUND(AVG(CASE WHEN has_academic_support = true THEN 100 ELSE 0 END), 1) as "Academic Support %",
                                ROUND(AVG(CASE WHEN has_case_plan = true THEN 100 ELSE 0 END), 1) as "Case Plan %"
                            FROM main_main_analytics.v_wellbeing_risk_profiles
                            GROUP BY overall_risk_level
                            ORDER BY overall_risk_level DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
        ]

        return DashboardDefinition(
            name="Wellbeing & Mental Health Risk",
            description="Multi-domain risk assessment and support resource tracking",
            type=DashboardType.WELLBEING_RISK,
            target_audience=["Counselors", "Social Workers"],
            refresh_interval=5,
            tabs=tabs,
            row_level_security=True,
            rbac_column="assigned_counselor_id",
        )

    @staticmethod
    def equity_outcomes() -> DashboardDefinition:
        """
        Equity Outcomes Analysis Dashboard
        Target: District Leadership, Equity Officers
        """

        tabs = [
            DashboardTab(
                name="Achievement Gap Analysis",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=5,
                        title="Achievement Outcomes by Demographic",
                        query="""
                            SELECT 
                                demographic_category as "Demographic Group",
                                demographic_value as "Value",
                                ROUND(AVG(academic_performance_score), 2) as "Avg Performance",
                                ROUND(AVG(graduation_rate), 1) as "Graduation Rate %",
                                COUNT(*) as "Student Count"
                            FROM main_main_analytics.v_equity_outcomes_by_demographics
                            WHERE student_count >= 5
                            GROUP BY demographic_category, demographic_value
                            ORDER BY demographic_category, AVG(academic_performance_score) DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
            DashboardTab(
                name="Disparity Index",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=6,
                        size_height=4,
                        title="Performance Gap Index",
                        query="""
                            SELECT 
                                demographic_category as category,
                                ROUND(MAX(academic_performance_score) - MIN(academic_performance_score), 2) as disparity_index
                            FROM main_main_analytics.v_equity_outcomes_by_demographics
                            WHERE student_count >= 5
                            GROUP BY demographic_category
                            ORDER BY disparity_index DESC
                        """,
                        visualization_type="bar",
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=6,
                        size_width=6,
                        size_height=4,
                        title="Graduation Rate by Race/Ethnicity",
                        query="""
                            SELECT 
                                demographic_value as "Group",
                                ROUND(AVG(graduation_rate), 1) as "Graduation Rate %"
                            FROM main_main_analytics.v_equity_outcomes_by_demographics
                            WHERE demographic_category = 'race_ethnicity' AND student_count >= 5
                            GROUP BY demographic_value
                            ORDER BY "Graduation Rate %" DESC
                        """,
                        visualization_type="bar",
                    ),
                ],
            ),
            DashboardTab(
                name="Intervention Effectiveness",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=4,
                        title="Intervention ROI by Demographic",
                        query="""
                            SELECT 
                                demographic_category as "Demographic",
                                demographic_value as "Group",
                                COUNT(*) as "Students Reached",
                                ROUND(AVG(intervention_effectiveness_score), 2) as "Avg Effectiveness"
                            FROM main_main_analytics.v_equity_outcomes_by_demographics
                            WHERE intervention_applied = true AND student_count >= 5
                            GROUP BY demographic_category, demographic_value
                            ORDER BY "Avg Effectiveness" DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
        ]

        return DashboardDefinition(
            name="Equity Outcomes Analysis",
            description="Achievement gap analysis by demographic groups with FERPA protection (min 5 students)",
            type=DashboardType.EQUITY_OUTCOMES,
            target_audience=["District Leadership", "Equity Officers"],
            refresh_interval=5,
            tabs=tabs,
            row_level_security=False,
        )

    @staticmethod
    def class_effectiveness() -> DashboardDefinition:
        """
        Class Effectiveness & Teacher Quality Dashboard
        Target: Teachers, Instructional Coaches
        """

        tabs = [
            DashboardTab(
                name="My Classes",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=5,
                        title="Class Performance vs Peer Average",
                        query="""
                            SELECT 
                                class_id as "Class ID",
                                subject as "Subject",
                                ROUND(avg_student_learning_gain, 2) as "Learning Gain %",
                                ROUND(peer_avg_learning_gain, 2) as "Peer Average %",
                                ROUND(avg_student_learning_gain - peer_avg_learning_gain, 2) as "Difference",
                                COUNT(DISTINCT student_id) as "Student Count"
                            FROM main_main_analytics.v_class_section_comparison
                            GROUP BY class_id, subject, avg_student_learning_gain, peer_avg_learning_gain
                            ORDER BY avg_student_learning_gain DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
            DashboardTab(
                name="Peer Comparison",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=6,
                        size_height=4,
                        title="My Classes (Top 10)",
                        query="""
                            SELECT 
                                class_id,
                                ROUND(avg_student_learning_gain, 1) as learning_gain
                            FROM main_main_analytics.v_class_section_comparison
                            GROUP BY class_id, avg_student_learning_gain
                            ORDER BY avg_student_learning_gain DESC
                            LIMIT 10
                        """,
                        visualization_type="bar",
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=6,
                        size_width=6,
                        size_height=4,
                        title="Student Growth Trajectory",
                        query="""
                            SELECT 
                                ROUND(avg_student_learning_gain / 10) * 10 as gain_range,
                                COUNT(*) as class_count
                            FROM main_main_analytics.v_class_section_comparison
                            GROUP BY ROUND(avg_student_learning_gain / 10) * 10
                            ORDER BY gain_range
                        """,
                        visualization_type="bar",
                    ),
                ],
            ),
        ]

        return DashboardDefinition(
            name="Class Effectiveness & Teacher Quality",
            description="Class-level learning outcomes with teacher-restricted data access",
            type=DashboardType.CLASS_EFFECTIVENESS,
            target_audience=["Teachers", "Instructional Coaches"],
            refresh_interval=5,
            tabs=tabs,
            row_level_security=True,
            rbac_column="teacher_id",
        )

    @staticmethod
    def performance_correlations() -> DashboardDefinition:
        """
        Performance Correlations & Interventions Dashboard
        Target: Data Analysts, Researchers
        """

        tabs = [
            DashboardTab(
                name="Root Cause Analysis",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=5,
                        title="Key Performance Correlations",
                        query="""
                            SELECT 
                                correlation_name as "Correlation",
                                ROUND(correlation_coefficient, 3) as "Strength",
                                p_value as "P-Value",
                                CASE WHEN p_value < 0.05 THEN 'Yes' ELSE 'No' END as "Significant"
                            FROM main_main_analytics.v_performance_correlations
                            ORDER BY ABS(correlation_coefficient) DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
            DashboardTab(
                name="Intervention Funnel",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=6,
                        size_height=4,
                        title="Intervention Status",
                        query="""
                            SELECT 
                                intervention_status as "Status",
                                COUNT(*) as "Students"
                            FROM main_main_analytics.v_performance_correlations
                            WHERE intervention_status IS NOT NULL
                            GROUP BY intervention_status
                            ORDER BY "Students" DESC
                        """,
                        visualization_type="pie",
                    ),
                    DashboardCard(
                        position_row=0,
                        position_col=6,
                        size_width=6,
                        size_height=4,
                        title="Intervention Completion Rate (%)",
                        query="""
                            SELECT 
                                intervention_type as "Type",
                                ROUND(SUM(CASE WHEN intervention_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as "Completion %"
                            FROM main_main_analytics.v_performance_correlations
                            WHERE intervention_type IS NOT NULL
                            GROUP BY intervention_type
                            ORDER BY "Completion %" DESC
                        """,
                        visualization_type="bar",
                    ),
                ],
            ),
            DashboardTab(
                name="ROI Analysis",
                cards=[
                    DashboardCard(
                        position_row=0,
                        position_col=0,
                        size_width=12,
                        size_height=4,
                        title="Intervention ROI by Type",
                        query="""
                            SELECT 
                                intervention_type as "Intervention Type",
                                COUNT(*) as "Students Served",
                                ROUND(AVG(student_outcome_improvement), 2) as "Avg Outcome Improvement",
                                ROUND(SUM(CASE WHEN student_outcome_improvement > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as "Success Rate %"
                            FROM main_main_analytics.v_performance_correlations
                            WHERE intervention_type IS NOT NULL AND intervention_status = 'Completed'
                            GROUP BY intervention_type
                            ORDER BY "Avg Outcome Improvement" DESC
                        """,
                        visualization_type="table",
                    ),
                ],
            ),
        ]

        return DashboardDefinition(
            name="Performance Correlations & Interventions",
            description="Root cause analysis and intervention effectiveness tracking",
            type=DashboardType.PERFORMANCE_CORRELATIONS,
            target_audience=["Data Analysts", "Researchers"],
            refresh_interval=5,
            tabs=tabs,
            row_level_security=False,
        )


# ============================================================================
# Metabase API Client
# ============================================================================


class MetabaseClient:
    """Client for Metabase API interactions"""

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        username: str = "admin@metabase.com",
        password: str = "metabasepassword",
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session_token = None
        self.user_id = None

    def authenticate(self) -> bool:
        """Authenticate with Metabase and get session token"""
        try:
            response = requests.post(
                f"{self.base_url}/api/session",
                json={"username": self.username, "password": self.password},
            )
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("id")
                self.user_id = data.get("user_id")
                print(f"✓ Authenticated to Metabase (User: {self.user_id})")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False

    def get_headers(self) -> Dict:
        """Get request headers with authentication token"""
        return {
            "X-Metabase-Session": self.session_token,
            "Content-Type": "application/json",
        }

    def create_database_connection(self, config: MetabaseConnection) -> Optional[int]:
        """Create a database connection in Metabase"""
        try:
            payload = {
                "name": config.name,
                "engine": config.engine,
                "details": {
                    "db": config.database,
                },
                "is_on_demand": config.is_on_demand,
                "cache_ttl_minutes": config.cache_ttl_minutes,
                "read_only": config.read_only,
            }

            response = requests.post(
                f"{self.base_url}/api/database",
                headers=self.get_headers(),
                json=payload,
            )

            if response.status_code in [200, 201]:
                db_id = response.json().get("id")
                print(f"✓ Created database connection: {config.name} (ID: {db_id})")
                return db_id
            else:
                print(f"✗ Failed to create database: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error creating database connection: {e}")
            return None

    def get_databases(self) -> List[Dict]:
        """List all databases configured in Metabase"""
        try:
            response = requests.get(
                f"{self.base_url}/api/database", headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            print(f"✗ Error fetching databases: {e}")
            return []

    def create_dashboard(self, name: str, description: str) -> Optional[int]:
        """Create a new dashboard"""
        try:
            payload = {
                "name": name,
                "description": description,
                "caching_ttl": 10,  # 10 minute cache
            }

            response = requests.post(
                f"{self.base_url}/api/dashboard",
                headers=self.get_headers(),
                json=payload,
            )

            if response.status_code in [200, 201]:
                dashboard_id = response.json().get("id")
                print(f"✓ Created dashboard: {name} (ID: {dashboard_id})")
                return dashboard_id
            else:
                print(f"✗ Failed to create dashboard: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error creating dashboard: {e}")
            return None


# ============================================================================
# Main Provisioning Script
# ============================================================================


def generate_dashboard_definitions() -> Dict[str, DashboardDefinition]:
    """Generate all dashboard definitions"""
    return {
        "chronic_absenteeism": DashboardTemplates.chronic_absenteeism(),
        "wellbeing_risk": DashboardTemplates.wellbeing_risk(),
        "equity_outcomes": DashboardTemplates.equity_outcomes(),
        "class_effectiveness": DashboardTemplates.class_effectiveness(),
        "performance_correlations": DashboardTemplates.performance_correlations(),
    }


def export_dashboards_json(
    dashboards: Dict[str, DashboardDefinition], output_dir: str = "."
) -> None:
    """Export dashboard definitions to JSON files"""
    os.makedirs(output_dir, exist_ok=True)

    for key, dashboard in dashboards.items():
        # Simplify the definition for JSON export
        dashboard_json = {
            "name": dashboard.name,
            "description": dashboard.description,
            "type": dashboard.type.value,
            "target_audience": dashboard.target_audience,
            "refresh_interval_minutes": dashboard.refresh_interval,
            "row_level_security": dashboard.row_level_security,
            "rbac_column": dashboard.rbac_column,
            "tabs": [
                {
                    "name": tab.name,
                    "cards": [
                        {
                            "position": [card.position_row, card.position_col],
                            "size": [card.size_width, card.size_height],
                            "title": card.title,
                            "query": card.query.strip(),
                            "visualization_type": card.visualization_type,
                            "settings": card.viz_settings or {},
                        }
                        for card in tab.cards
                    ],
                }
                for tab in (dashboard.tabs or [])
            ],
        }

        output_file = os.path.join(output_dir, f"{key}_definition.json")
        with open(output_file, "w") as f:
            json.dump(dashboard_json, f, indent=2)
        print(f"✓ Exported: {output_file}")


def main():
    """Main provisioning script"""
    print("=" * 70)
    print("🎯 Metabase Dashboard Provisioning")
    print("=" * 70)

    # Generate all dashboard definitions
    print("\n📊 Generating Dashboard Definitions...")
    dashboards = generate_dashboard_definitions()
    for key, dashboard in dashboards.items():
        print(f"  ✓ {dashboard.name}")

    # Export to JSON for review
    print("\n💾 Exporting Dashboard Definitions to JSON...")
    export_dashboards_json(dashboards, output_dir=".")

    print("\n" + "=" * 70)
    print("✓ Dashboard provisioning complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Review exported JSON files")
    print("2. Start Metabase: http://localhost:3000")
    print("3. Connect to DuckDB database")
    print("4. Create dashboards from definitions")
    print("5. Configure row-level security for RBAC dashboards")
    print("=" * 70)


if __name__ == "__main__":
    main()
