#!/usr/bin/env bash
set +e
DB="oss_framework/data/oea.duckdb"
OUT="DataAnalysisExpert/query_audit_extended"
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

# Class effectiveness JSON definition queries
audit_query "json_class_perf_vs_peer" "SELECT class_id, subject, ROUND(avg_student_learning_gain, 2), ROUND(peer_avg_learning_gain,2), ROUND(avg_student_learning_gain - peer_avg_learning_gain,2), COUNT(DISTINCT student_id) FROM main_main_analytics.v_class_section_comparison GROUP BY class_id, subject, avg_student_learning_gain, peer_avg_learning_gain ORDER BY avg_student_learning_gain DESC;"
audit_query "json_class_top10" "SELECT class_id, ROUND(avg_student_learning_gain,1) as learning_gain FROM main_main_analytics.v_class_section_comparison GROUP BY class_id, avg_student_learning_gain ORDER BY avg_student_learning_gain DESC LIMIT 10;"
audit_query "json_class_growth_trajectory" "SELECT ROUND(avg_student_learning_gain / 10) * 10 as gain_range, COUNT(*) as class_count FROM main_main_analytics.v_class_section_comparison GROUP BY ROUND(avg_student_learning_gain / 10) * 10 ORDER BY gain_range;"

# Performance correlations JSON definition queries
audit_query "json_perf_key_correlations" "SELECT correlation_name, ROUND(correlation_coefficient, 3), p_value, CASE WHEN p_value < 0.05 THEN 'Yes' ELSE 'No' END FROM main_main_analytics.v_performance_correlations ORDER BY ABS(correlation_coefficient) DESC;"
audit_query "json_perf_intervention_status" "SELECT intervention_status, COUNT(*) FROM main_main_analytics.v_performance_correlations WHERE intervention_status IS NOT NULL GROUP BY intervention_status ORDER BY 2 DESC;"
audit_query "json_perf_completion_rate" "SELECT intervention_type, ROUND(SUM(CASE WHEN intervention_status='Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),1) FROM main_main_analytics.v_performance_correlations WHERE intervention_type IS NOT NULL GROUP BY intervention_type ORDER BY 2 DESC;"
audit_query "json_perf_roi" "SELECT intervention_type, COUNT(*), ROUND(AVG(student_outcome_improvement),2), ROUND(SUM(CASE WHEN student_outcome_improvement > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),1) FROM main_main_analytics.v_performance_correlations WHERE intervention_type IS NOT NULL AND intervention_status='Completed' GROUP BY intervention_type ORDER BY 3 DESC;"

# Wellbeing JSON definition queries
audit_query "json_wellbeing_high_risk" "SELECT COUNT(*) FROM main_main_analytics.v_wellbeing_risk_profiles WHERE overall_risk_level = 'High';"
audit_query "json_wellbeing_medium_risk" "SELECT COUNT(*) FROM main_main_analytics.v_wellbeing_risk_profiles WHERE overall_risk_level = 'Medium';"
audit_query "json_wellbeing_active_cases" "SELECT COUNT(*) FROM main_main_analytics.v_wellbeing_risk_profiles WHERE has_active_case_plan = true;"
audit_query "json_wellbeing_followups_due" "SELECT COUNT(*) FROM main_main_analytics.v_wellbeing_risk_profiles WHERE days_since_last_contact > 14 AND has_active_case_plan = true;"
audit_query "json_wellbeing_domain_breakdown" "SELECT 'Academic' as domain, SUM(CASE WHEN academic_risk_flag = true THEN 1 ELSE 0 END) as count FROM main_main_analytics.v_wellbeing_risk_profiles UNION ALL SELECT 'Behavioral', SUM(CASE WHEN behavioral_risk_flag = true THEN 1 ELSE 0 END) FROM main_main_analytics.v_wellbeing_risk_profiles UNION ALL SELECT 'Social-Emotional', SUM(CASE WHEN social_emotional_risk_flag = true THEN 1 ELSE 0 END) FROM main_main_analytics.v_wellbeing_risk_profiles UNION ALL SELECT 'Family Engagement', SUM(CASE WHEN family_engagement_risk_flag = true THEN 1 ELSE 0 END) FROM main_main_analytics.v_wellbeing_risk_profiles;"
audit_query "json_wellbeing_caseload" "SELECT overall_risk_level, COUNT(*) FROM main_main_analytics.v_wellbeing_risk_profiles GROUP BY overall_risk_level ORDER BY overall_risk_level;"
audit_query "json_wellbeing_resource_allocation" "SELECT overall_risk_level, COUNT(*), ROUND(AVG(CASE WHEN has_counseling_services = true THEN 100 ELSE 0 END),1), ROUND(AVG(CASE WHEN has_academic_support = true THEN 100 ELSE 0 END),1), ROUND(AVG(CASE WHEN has_case_plan = true THEN 100 ELSE 0 END),1) FROM main_main_analytics.v_wellbeing_risk_profiles GROUP BY overall_risk_level ORDER BY overall_risk_level DESC;"

echo "Wrote $SUMMARY"
