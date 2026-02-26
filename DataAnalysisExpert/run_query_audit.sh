#!/usr/bin/env bash
set +e
DB="oss_framework/data/oea.duckdb"
OUT="DataAnalysisExpert/query_audit"
mkdir -p "$OUT"
SUMMARY="$OUT/summary.txt"
: > "$SUMMARY"

audit_query() {
  local name="$1"
  local sql="$2"
  local safe
  safe=$(echo "$name" | tr ' /' '__')
  local logfile="$OUT/${safe}.log"
  duckdb "$DB" -c "$sql" > "$logfile" 2>&1
  local rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "PASS|$name|$logfile" >> "$SUMMARY"
  else
    echo "FAIL|$name|$logfile" >> "$SUMMARY"
  fi
}

audit_query "rill_chronic_total_students" "EXPLAIN ANALYZE SELECT COUNT(DISTINCT student_key) FROM main_main_analytics.v_chronic_absenteeism_risk;"
audit_query "rill_chronic_absence_count" "EXPLAIN ANALYZE SELECT SUM(chronic_absence_flag) FROM main_main_analytics.v_chronic_absenteeism_risk;"
audit_query "rill_chronic_absence_rate" "EXPLAIN ANALYZE SELECT SUM(chronic_absence_flag) * 100.0 / NULLIF(COUNT(DISTINCT student_key), 0) FROM main_main_analytics.v_chronic_absenteeism_risk;"
audit_query "rill_equity_cohort_size" "EXPLAIN ANALYZE SELECT SUM(cohort_size) FROM main_main_analytics.v_equity_outcomes_by_demographics;"
audit_query "rill_equity_avg_attendance" "EXPLAIN ANALYZE SELECT AVG(pct_good_attendance) FROM main_main_analytics.v_equity_outcomes_by_demographics;"
audit_query "rill_equity_avg_no_discipline" "EXPLAIN ANALYZE SELECT AVG(pct_no_discipline) FROM main_main_analytics.v_equity_outcomes_by_demographics;"
audit_query "rill_equity_avg_gpa" "EXPLAIN ANALYZE SELECT AVG(avg_gpa) FROM main_main_analytics.v_equity_outcomes_by_demographics;"

audit_query "json_chronic_students_at_risk" "SELECT COUNT(*) as count FROM main_main_analytics.v_chronic_absenteeism_risk WHERE risk_classification IN ('Critical','High');"
audit_query "json_chronic_declining_attendance" "SELECT COUNT(*) as count FROM main_main_analytics.v_chronic_absenteeism_risk WHERE attendance_trend_30d = 'declining' OR attendance_rate_30d < 85;"
audit_query "json_chronic_risk_distribution" "SELECT ROUND(chronic_absenteeism_risk_score * 10) / 10 as risk_score, COUNT(*) as student_count FROM main_main_analytics.v_chronic_absenteeism_risk GROUP BY 1 ORDER BY 1;"
audit_query "json_chronic_risk_classification_breakdown" "SELECT risk_classification, COUNT(*) as count FROM main_main_analytics.v_chronic_absenteeism_risk GROUP BY risk_classification ORDER BY risk_classification;"
audit_query "json_chronic_priority_list" "SELECT student_key, grade_level, school_id, ROUND(chronic_absenteeism_risk_score,2) as risk_score, risk_classification, ROUND(attendance_rate_30d,1), discipline_incidents_30d FROM main_main_analytics.v_chronic_absenteeism_risk WHERE risk_classification IN ('Critical', 'High') ORDER BY chronic_absenteeism_risk_score DESC LIMIT 50;"
audit_query "json_chronic_trends_analysis" "SELECT grade_level, ROUND(AVG(attendance_rate_30d),1), ROUND(AVG(attendance_rate_60d),1), ROUND(AVG(attendance_rate_90d),1) FROM main_main_analytics.v_chronic_absenteeism_risk GROUP BY grade_level ORDER BY grade_level;"
audit_query "json_equity_achievement_outcomes" "SELECT demographic_category, demographic_value, ROUND(AVG(academic_performance_score),2), ROUND(AVG(graduation_rate),1), COUNT(*) FROM main_main_analytics.v_equity_outcomes_by_demographics WHERE student_count >= 5 GROUP BY demographic_category, demographic_value ORDER BY demographic_category, AVG(academic_performance_score) DESC;"
audit_query "json_equity_performance_gap_index" "SELECT demographic_category, ROUND(MAX(academic_performance_score) - MIN(academic_performance_score),2) as disparity_index FROM main_main_analytics.v_equity_outcomes_by_demographics WHERE student_count >= 5 GROUP BY demographic_category ORDER BY disparity_index DESC;"
audit_query "json_equity_graduation_rate_race" "SELECT demographic_value, ROUND(AVG(graduation_rate),1) FROM main_main_analytics.v_equity_outcomes_by_demographics WHERE demographic_category = 'race_ethnicity' AND student_count >= 5 GROUP BY demographic_value ORDER BY 2 DESC;"
audit_query "json_equity_intervention_roi" "SELECT demographic_category, demographic_value, COUNT(*), ROUND(AVG(intervention_effectiveness_score),2) FROM main_main_analytics.v_equity_outcomes_by_demographics WHERE intervention_applied = true AND student_count >= 5 GROUP BY demographic_category, demographic_value ORDER BY 4 DESC;"

audit_query "py_chronic_at_risk_count" "EXPLAIN ANALYZE SELECT COUNT(DISTINCT student_key) FROM main_main_analytics.v_chronic_absenteeism_risk WHERE risk_level IN ('High','Critical');"
audit_query "py_chronic_chronic_rate" "EXPLAIN ANALYZE SELECT ROUND(COUNT(CASE WHEN risk_level != 'Low' THEN 1 END) * 100.0 / COUNT(DISTINCT student_key), 1) FROM main_main_analytics.v_chronic_absenteeism_risk;"
audit_query "py_chronic_declining_count" "EXPLAIN ANALYZE SELECT COUNT(DISTINCT student_key) FROM main_main_analytics.v_chronic_absenteeism_risk WHERE attendance_trend_90d = 'declining';"
audit_query "py_chronic_top_students" "SELECT student_key as student_id, risk_level, ROUND(attendance_rate_30d,1), attendance_trend_90d, COALESCE(_loaded_at::varchar, 'N/A') FROM main_main_analytics.v_chronic_absenteeism_risk WHERE risk_level IN ('High','Critical') ORDER BY chronic_absenteeism_risk_score DESC LIMIT 50;"
audit_query "py_equity_records" "EXPLAIN ANALYZE SELECT * FROM main_main_analytics.v_equity_outcomes_by_demographics LIMIT 100;"

echo "Wrote $SUMMARY"
