#!/usr/bin/env python3
"""
Dashboard Query Performance Validation Script
Validates that all dashboard queries meet performance targets (p95 <2s, p99 <3s)
Tests against DuckDB analytics database with 500K+ records
"""

import duckdb
import time
import json
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QueryPerformance:
    """Performance metrics for a single query"""

    query_name: str
    dashboard: str
    tab: str
    card: str
    execution_times: List[float]  # milliseconds
    row_count: int

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.execution_times)

    @property
    def median_ms(self) -> float:
        return statistics.median(self.execution_times)

    @property
    def p95_ms(self) -> float:
        sorted_times = sorted(self.execution_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]

    @property
    def p99_ms(self) -> float:
        sorted_times = sorted(self.execution_times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[idx]

    @property
    def max_ms(self) -> float:
        return max(self.execution_times)

    @property
    def passes(self) -> bool:
        """Passes if p95 < 2000ms and p99 < 3000ms"""
        return self.p95_ms < 2000 and self.p99_ms < 3000


class DashboardQueryValidator:
    """Validates dashboard query performance"""

    def __init__(self, db_path: str = "oss_framework/data/oea.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path, read_only=True)
        self.results: Dict[str, QueryPerformance] = {}

    def test_query(
        self,
        name: str,
        dashboard: str,
        tab: str,
        card: str,
        query: str,
        iterations: int = 5,
    ) -> QueryPerformance:
        """Test a query and record performance metrics"""

        execution_times = []
        row_count = 0

        print(f"  Testing: {dashboard:40} / {tab:20} / {card:30}", end="", flush=True)

        try:
            for i in range(iterations):
                start = time.time()
                result = self.conn.execute(query).fetchall()
                elapsed = (time.time() - start) * 1000  # Convert to ms

                execution_times.append(elapsed)
                if i == 0:
                    row_count = len(result) if result else 0

            perf = QueryPerformance(
                query_name=name,
                dashboard=dashboard,
                tab=tab,
                card=card,
                execution_times=execution_times,
                row_count=row_count,
            )

            self.results[name] = perf

            # Format output
            status = "✓" if perf.passes else "✗"
            print(
                f" {status} p95={perf.p95_ms:6.0f}ms, p99={perf.p99_ms:6.0f}ms, rows={row_count:,}"
            )

            return perf

        except Exception as e:
            print(f" ✗ ERROR: {str(e)[:50]}")
            return None

    def validate_all_dashboards(self) -> Dict[str, List[QueryPerformance]]:
        """Validate all dashboard queries"""

        print("\n" + "=" * 120)
        print("🎯 Dashboard Query Performance Validation")
        print("=" * 120)
        print(f"Database: {self.db_path}")
        print(f"Target: p95 < 2000ms, p99 < 3000ms")
        print("=" * 120)

        # ====================================================================
        # Dashboard 1: Chronic Absenteeism Risk
        # ====================================================================
        print("\n📊 Dashboard 1: Chronic Absenteeism Risk")
        print("-" * 120)

        # Tab 1: Overview
        self.test_query(
            "chronic_1_1_at_risk",
            "Chronic Absenteeism Risk",
            "Overview",
            "Students at Risk",
            """
            SELECT COUNT(*) as count 
            FROM main_main_analytics.v_chronic_absenteeism_risk 
            WHERE risk_classification IN ('Critical', 'High')
            """,
        )

        self.test_query(
            "chronic_1_2_absence_rate",
            "Chronic Absenteeism Risk",
            "Overview",
            "Chronic Absence Rate (%)",
            """
            SELECT ROUND(AVG(CASE WHEN chronic_absence_flag = true THEN 100 ELSE 0 END), 1) as rate
            FROM main_main_analytics.v_chronic_absenteeism_risk
            """,
        )

        self.test_query(
            "chronic_1_3_declining",
            "Chronic Absenteeism Risk",
            "Overview",
            "Declining Attendance (30d)",
            """
            SELECT COUNT(*) as count
            FROM main_main_analytics.v_chronic_absenteeism_risk
            WHERE attendance_trend_30d = 'declining' OR attendance_rate_30d < 85
            """,
        )

        # Tab 2: Risk Distribution
        self.test_query(
            "chronic_2_1_distribution",
            "Chronic Absenteeism Risk",
            "Risk Distribution",
            "Risk Score Distribution",
            """
            SELECT 
                ROUND(chronic_absenteeism_risk_score * 10) / 10 as risk_score,
                COUNT(*) as student_count
            FROM main_main_analytics.v_chronic_absenteeism_risk
            GROUP BY ROUND(chronic_absenteeism_risk_score * 10) / 10
            ORDER BY risk_score
            """,
        )

        self.test_query(
            "chronic_2_2_breakdown",
            "Chronic Absenteeism Risk",
            "Risk Distribution",
            "Risk Classification Breakdown",
            """
            SELECT 
                risk_classification,
                COUNT(*) as count
            FROM main_main_analytics.v_chronic_absenteeism_risk
            GROUP BY risk_classification
            ORDER BY risk_classification
            """,
        )

        # Tab 3: At-Risk Students
        self.test_query(
            "chronic_3_1_students",
            "Chronic Absenteeism Risk",
            "At-Risk Students",
            "Priority Intervention List",
            """
            SELECT 
                student_key, grade_level, school_id,
                ROUND(chronic_absenteeism_risk_score, 2) as risk_score,
                risk_classification, ROUND(attendance_rate_30d, 1) as attendance_rate_30d,
                discipline_incidents_30d
            FROM main_main_analytics.v_chronic_absenteeism_risk
            WHERE risk_classification IN ('Critical', 'High')
            ORDER BY chronic_absenteeism_risk_score DESC
            LIMIT 50
            """,
        )

        # Tab 4: Trends & Analysis
        self.test_query(
            "chronic_4_1_trends",
            "Chronic Absenteeism Risk",
            "Trends & Analysis",
            "Attendance Trend (Last 90 Days)",
            """
            SELECT 
                grade_level,
                ROUND(AVG(attendance_rate_30d), 1) as avg_30d,
                ROUND(AVG(attendance_rate_60d), 1) as avg_60d,
                ROUND(AVG(attendance_rate_90d), 1) as avg_90d
            FROM main_main_analytics.v_chronic_absenteeism_risk
            GROUP BY grade_level
            ORDER BY grade_level
            """,
        )

        # ====================================================================
        # Dashboard 2: Wellbeing & Mental Health Risk
        # ====================================================================
        print("\n📊 Dashboard 2: Wellbeing & Mental Health Risk")
        print("-" * 120)

        self.test_query(
            "wellbeing_1_1_high_risk",
            "Wellbeing & Mental Health Risk",
            "Risk Dashboard",
            "High Risk Count",
            """
            SELECT COUNT(*) as count
            FROM main_main_analytics.v_wellbeing_risk_profiles
            WHERE overall_risk_level = 'High'
            """,
        )

        self.test_query(
            "wellbeing_1_2_medium_risk",
            "Wellbeing & Mental Health Risk",
            "Risk Dashboard",
            "Medium Risk Count",
            """
            SELECT COUNT(*) as count
            FROM main_main_analytics.v_wellbeing_risk_profiles
            WHERE overall_risk_level = 'Medium'
            """,
        )

        self.test_query(
            "wellbeing_1_3_active_cases",
            "Wellbeing & Mental Health Risk",
            "Risk Dashboard",
            "Active Cases",
            """
            SELECT COUNT(*) as count
            FROM main_main_analytics.v_wellbeing_risk_profiles
            WHERE has_active_case_plan = true
            """,
        )

        # ====================================================================
        # Dashboard 3: Equity Outcomes Analysis
        # ====================================================================
        print("\n📊 Dashboard 3: Equity Outcomes Analysis")
        print("-" * 120)

        self.test_query(
            "equity_1_1_achievement",
            "Equity Outcomes Analysis",
            "Achievement Gap Analysis",
            "Achievement Outcomes",
            """
            SELECT 
                demographic_category, demographic_value,
                ROUND(AVG(academic_performance_score), 2) as avg_performance,
                ROUND(AVG(graduation_rate), 1) as graduation_rate,
                COUNT(*) as student_count
            FROM main_main_analytics.v_equity_outcomes_by_demographics
            WHERE student_count >= 5
            GROUP BY demographic_category, demographic_value
            ORDER BY demographic_category, AVG(academic_performance_score) DESC
            """,
        )

        # ====================================================================
        # Dashboard 4: Class Effectiveness & Teacher Quality
        # ====================================================================
        print("\n📊 Dashboard 4: Class Effectiveness & Teacher Quality")
        print("-" * 120)

        self.test_query(
            "class_1_1_performance",
            "Class Effectiveness",
            "My Classes",
            "Class Performance vs Peer Average",
            """
            SELECT 
                class_id, subject,
                ROUND(avg_student_learning_gain, 2) as learning_gain,
                ROUND(peer_avg_learning_gain, 2) as peer_avg,
                COUNT(DISTINCT student_id) as student_count
            FROM main_main_analytics.v_class_section_comparison
            GROUP BY class_id, subject, avg_student_learning_gain, peer_avg_learning_gain
            ORDER BY avg_student_learning_gain DESC
            """,
        )

        # ====================================================================
        # Dashboard 5: Performance Correlations & Interventions
        # ====================================================================
        print("\n📊 Dashboard 5: Performance Correlations & Interventions")
        print("-" * 120)

        self.test_query(
            "perf_1_1_correlations",
            "Performance Correlations",
            "Root Cause Analysis",
            "Key Performance Correlations",
            """
            SELECT 
                correlation_name,
                ROUND(correlation_coefficient, 3) as correlation_coef,
                p_value
            FROM main_main_analytics.v_performance_correlations
            ORDER BY ABS(correlation_coefficient) DESC
            """,
        )

        return self.results

    def print_summary(self):
        """Print validation summary"""

        print("\n" + "=" * 120)
        print("📋 Performance Validation Summary")
        print("=" * 120)

        # Group by dashboard
        by_dashboard = {}
        for perf in self.results.values():
            if perf.dashboard not in by_dashboard:
                by_dashboard[perf.dashboard] = []
            by_dashboard[perf.dashboard].append(perf)

        # Print summary by dashboard
        total_passed = 0
        total_failed = 0

        for dashboard, perfs in by_dashboard.items():
            passed = sum(1 for p in perfs if p.passes)
            failed = len(perfs) - passed
            total_passed += passed
            total_failed += failed

            status = "✓" if failed == 0 else "✗"
            print(f"\n{status} {dashboard:40} {passed}/{len(perfs)} queries pass")

            for perf in perfs:
                status = "✓" if perf.passes else "✗"
                print(
                    f"    {status} {perf.card:40} p95={perf.p95_ms:6.0f}ms, p99={perf.p99_ms:6.0f}ms"
                )

        # Overall summary
        total = total_passed + total_failed
        print("\n" + "-" * 120)
        print(f"Overall: {total_passed}/{total} queries pass")
        print(f"Pass Rate: {total_passed / total * 100:.1f}%")

        if total_failed > 0:
            print(f"\n⚠️  {total_failed} queries exceeded performance targets:")
            for perf in self.results.values():
                if not perf.passes:
                    if perf.p95_ms >= 2000:
                        print(
                            f"  • {perf.dashboard}/{perf.card}: p95={perf.p95_ms:.0f}ms (target: <2000ms)"
                        )
                    if perf.p99_ms >= 3000:
                        print(
                            f"  • {perf.dashboard}/{perf.card}: p99={perf.p99_ms:.0f}ms (target: <3000ms)"
                        )
        else:
            print("\n✓ All queries meet performance targets!")

        print("=" * 120)

    def export_report(self, filename: str = "reports/dashboard_performance_report.json"):
        """Export detailed report"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "database": self.db_path,
            "targets": {"p95_ms": 2000, "p99_ms": 3000},
            "summary": {
                "total_queries": len(self.results),
                "passed": sum(1 for p in self.results.values() if p.passes),
                "failed": sum(1 for p in self.results.values() if not p.passes),
            },
            "queries": [],
        }

        for name, perf in self.results.items():
            report["queries"].append(
                {
                    "name": name,
                    "dashboard": perf.dashboard,
                    "tab": perf.tab,
                    "card": perf.card,
                    "metrics": {
                        "mean_ms": round(perf.mean_ms, 1),
                        "median_ms": round(perf.median_ms, 1),
                        "p95_ms": round(perf.p95_ms, 1),
                        "p99_ms": round(perf.p99_ms, 1),
                        "max_ms": round(perf.max_ms, 1),
                    },
                    "row_count": perf.row_count,
                    "passes": perf.passes,
                }
            )

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report exported to: {filename}")


def main():
    """Run validation"""

    validator = DashboardQueryValidator()
    validator.validate_all_dashboards()
    validator.print_summary()
    validator.export_report()


if __name__ == "__main__":
    main()
