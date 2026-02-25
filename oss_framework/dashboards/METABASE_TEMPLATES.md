# Metabase Dashboard Configuration & Templates

## Dashboard 1: Chronic Absenteeism Risk Dashboard

### Purpose
Provide administrators and counselors with early warning system for students at risk of chronic absenteeism, enabling targeted interventions.

### Key Features
- Real-time risk scoring
- Trend analysis (30/60/90 days)
- Intervention tracking
- Peer comparison by school/grade

### Configuration

```json
{
  "name": "Chronic Absenteeism Risk",
  "description": "Real-time identification and monitoring of students at chronic absenteeism risk",
  "target_audience": ["School Administrators", "Counselors"],
  "refresh_interval": "5 minutes",
  "dashboard_tabs": [
    {
      "name": "Overview",
      "cards": [
        {
          "position": [0, 0],
          "size": [4, 2],
          "type": "scalar",
          "title": "Students at Risk",
          "query": "SELECT COUNT(*) FROM v_chronic_absenteeism_risk WHERE risk_classification IN ('Critical', 'High')",
          "visualization": {
            "type": "number",
            "color": "red",
            "conditional_formatting": true
          }
        },
        {
          "position": [4, 0],
          "size": [4, 2],
          "type": "scalar",
          "title": "Chronic Absence Rate",
          "query": "SELECT ROUND(AVG(chronic_absence_flag) * 100, 1) FROM v_chronic_absenteeism_risk",
          "visualization": {
            "type": "gauge",
            "min": 0,
            "max": 30
          }
        },
        {
          "position": [8, 0],
          "size": [4, 2],
          "type": "scalar",
          "title": "Students with Declining Attendance",
          "query": "SELECT COUNT(*) FROM v_chronic_absenteeism_risk WHERE attendance_trend_90d = 'declining'",
          "visualization": {
            "type": "number",
            "color": "orange"
          }
        }
      ]
    },
    {
      "name": "Risk Distribution",
      "cards": [
        {
          "position": [0, 0],
          "size": [6, 3],
          "type": "bar",
          "title": "Risk Score Distribution",
          "query": "SELECT chronic_absenteeism_risk_score, COUNT(*) as count FROM v_chronic_absenteeism_risk GROUP BY chronic_absenteeism_risk_score ORDER BY chronic_absenteeism_risk_score",
          "visualization": {
            "type": "histogram",
            "x_axis": "Risk Score",
            "y_axis": "Student Count"
          }
        },
        {
          "position": [6, 0],
          "size": [6, 3],
          "type": "pie",
          "title": "Risk Classification Breakdown",
          "query": "SELECT risk_classification, COUNT(*) as count FROM v_chronic_absenteeism_risk GROUP BY risk_classification",
          "visualization": {
            "type": "pie_chart"
          }
        }
      ]
    },
    {
      "name": "At-Risk Students",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 5],
          "type": "table",
          "title": "Priority Intervention List",
          "query": "SELECT student_key, grade_level, school_id, chronic_absenteeism_risk_score, risk_classification, attendance_rate_30d, discipline_incidents_30d FROM v_chronic_absenteeism_risk WHERE risk_classification IN ('Critical', 'High') ORDER BY chronic_absenteeism_risk_score DESC LIMIT 50",
          "visualization": {
            "type": "table",
            "enable_drill_down": true,
            "sortable": true,
            "columns": {
              "chronic_absenteeism_risk_score": {
                "format": "number",
                "num_decimals": 0,
                "conditional_formatting": {
                  "type": "range",
                  "rules": [
                    {"min": 0, "max": 40, "color": "green"},
                    {"min": 40, "max": 70, "color": "yellow"},
                    {"min": 70, "max": 100, "color": "red"}
                  ]
                }
              }
            }
          }
        }
      ]
    },
    {
      "name": "Trends & Analysis",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 3],
          "type": "line",
          "title": "30-Day Attendance Trend",
          "query": "SELECT DATE_TRUNC('day', date) as date, AVG(attendance_rate) as avg_attendance FROM (SELECT DATE(created_at) as date, student_key, attendance_rate_30d as attendance_rate FROM v_chronic_absenteeism_risk) GROUP BY DATE_TRUNC('day', date) ORDER BY date DESC LIMIT 30",
          "visualization": {
            "type": "line_chart",
            "x_axis": "Date",
            "y_axis": "Average Attendance Rate (%)"
          }
        }
      ]
    }
  ],
  "filters": [
    {
      "name": "school_filter",
      "type": "category",
      "field": "school_id",
      "label": "School",
      "default": null
    },
    {
      "name": "grade_filter",
      "type": "category",
      "field": "grade_level",
      "label": "Grade",
      "default": null
    },
    {
      "name": "risk_threshold",
      "type": "numeric",
      "field": "chronic_absenteeism_risk_score",
      "label": "Minimum Risk Score",
      "default": 0
    },
    {
      "name": "date_range",
      "type": "date/range",
      "field": "created_at",
      "label": "Date Range",
      "default": "last_30_days"
    }
  ],
  "access_control": {
    "public": false,
    "role_based": true,
    "permissions": [
      {"role": "admin", "access": "full"},
      {"role": "school_leader", "access": "school_data_only"},
      {"role": "counselor", "access": "assigned_students"},
      {"role": "data_analyst", "access": "full"}
    ]
  }
}
```

---

## Dashboard 2: Wellbeing & Mental Health Risk

### Purpose
Enable counselors and support staff to identify students needing mental health and social-emotional support.

### Configuration

```json
{
  "name": "Wellbeing & Mental Health Risk",
  "description": "Multi-domain risk assessment for student wellbeing and mental health interventions",
  "target_audience": ["Counselors", "Social Workers", "Mental Health Specialists"],
  "refresh_interval": "5 minutes",
  "dashboard_tabs": [
    {
      "name": "Risk Dashboard",
      "cards": [
        {
          "position": [0, 0],
          "size": [4, 2],
          "type": "scalar",
          "title": "Students Needing Support",
          "query": "SELECT COUNT(*) FROM v_wellbeing_risk_profiles WHERE overall_risk_score > 40"
        },
        {
          "position": [4, 0],
          "size": [8, 3],
          "type": "table",
          "title": "Risk Assessment Matrix",
          "query": "SELECT student_key, academic_risk, behavioral_risk, social_emotional_risk, family_engagement_risk, overall_risk_score, recommended_support FROM v_wellbeing_risk_profiles ORDER BY overall_risk_score DESC",
          "visualization": {
            "type": "heatmap",
            "conditional_formatting": {
              "type": "numeric",
              "rules": [
                {"min": 0, "max": 30, "color": "green"},
                {"min": 30, "max": 60, "color": "yellow"},
                {"min": 60, "max": 100, "color": "red"}
              ]
            }
          }
        }
      ]
    },
    {
      "name": "Support Resource Allocation",
      "cards": [
        {
          "position": [0, 0],
          "size": [6, 3],
          "type": "table",
          "title": "Students by Support Need",
          "query": "SELECT recommended_support, COUNT(*) as student_count, ROUND(AVG(overall_risk_score), 1) as avg_risk FROM v_wellbeing_risk_profiles GROUP BY recommended_support ORDER BY student_count DESC"
        },
        {
          "position": [6, 0],
          "size": [6, 3],
          "type": "table",
          "title": "Support Resource Capacity",
          "query": "SELECT resource_type, available_capacity, currently_serving, (available_capacity - currently_serving) as available_slots FROM support_resources ORDER BY available_slots"
        }
      ]
    }
  ],
  "access_control": {
    "role_based": true,
    "row_level_filtering": {
      "counselor": "assigned_students_only",
      "social_worker": "assigned_students_only"
    }
  }
}
```

---

## Dashboard 3: Equity Outcomes Analysis

### Purpose
Enable district leadership to identify and monitor achievement gaps and intervention effectiveness by demographic groups.

### Configuration

```json
{
  "name": "Equity Outcomes Analysis",
  "description": "Achievement gap analysis and equity metrics by demographic group",
  "target_audience": ["District Leadership", "Equity Officers", "Data Analysts"],
  "refresh_interval": "5 minutes",
  "dashboard_tabs": [
    {
      "name": "Disparity Index",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 4],
          "type": "table",
          "title": "Disparity Index by Demographic Group",
          "query": "SELECT demographic_group, outcome_metric, avg_score, district_average, disparity_index, ROUND((disparity_index - 1) * 100, 1) as gap_percentage FROM v_equity_outcomes_by_demographics ORDER BY disparity_index DESC",
          "visualization": {
            "type": "table",
            "conditional_formatting": {
              "disparity_index": {
                "type": "numeric",
                "rules": [
                  {"min": 0.85, "max": 1, "color": "green", "label": "Equity achieved"},
                  {"min": 0.7, "max": 0.85, "color": "yellow", "label": "Gap present"},
                  {"min": 0, "max": 0.7, "color": "red", "label": "Significant gap"}
                ]
              }
            }
          }
        }
      ]
    },
    {
      "name": "Intervention Effectiveness",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 3],
          "type": "bar",
          "title": "Intervention Outcomes by Demographic",
          "query": "SELECT demographic_group, intervention_type, COUNT(*) as participants, ROUND(AVG(outcome_improvement), 2) as avg_improvement FROM (SELECT *, CASE WHEN post_score > pre_score THEN (post_score - pre_score) / pre_score ELSE 0 END as outcome_improvement FROM equity_intervention_results) GROUP BY demographic_group, intervention_type ORDER BY avg_improvement DESC"
        }
      ]
    }
  ]
}
```

---

## Dashboard 4: Class Effectiveness & Teacher Quality

### Purpose
Enable teachers and school leaders to monitor class-level learning outcomes and compare performance with peer classes.

### Configuration

```json
{
  "name": "Class Effectiveness & Teacher Quality",
  "description": "Class-level learning outcomes and peer comparison metrics",
  "target_audience": ["Teachers", "Instructional Coaches", "School Leaders"],
  "refresh_interval": "5 minutes",
  "access_control": {
    "role_based": true,
    "permissions": [
      {"role": "teacher", "access": "own_classes_only"},
      {"role": "school_leader", "access": "all_classes"},
      {"role": "admin", "access": "full"}
    ]
  },
  "dashboard_tabs": [
    {
      "name": "Class Performance",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 3],
          "type": "table",
          "title": "Class Performance vs Peer Median",
          "query": "SELECT school_id, class_id, teacher_name, student_count, avg_learning_outcome, peer_median, ROUND(avg_learning_outcome - peer_median, 2) as variance, ROUND((avg_learning_outcome / peer_median - 1) * 100, 1) as pct_above_median FROM v_class_section_comparison ORDER BY variance DESC"
        }
      ]
    },
    {
      "name": "Learning Outcomes",
      "cards": [
        {
          "position": [0, 0],
          "size": [6, 3],
          "type": "box_plot",
          "title": "Learning Outcome Distribution",
          "query": "SELECT grade_level, subject, learning_outcome FROM class_learning_outcomes"
        },
        {
          "position": [6, 0],
          "size": [6, 3],
          "type": "scatter",
          "title": "Student Growth Trajectories",
          "query": "SELECT class_id, student_id, start_score, end_score, (end_score - start_score) as growth FROM student_class_performance WHERE class_id = {{ class_filter }}"
        }
      ]
    }
  ]
}
```

---

## Dashboard 5: Performance Correlations & Interventions

### Purpose
Enable data analysts and researchers to identify root causes, track interventions, and measure ROI.

### Configuration

```json
{
  "name": "Performance Correlations & Interventions",
  "description": "Root cause analysis, intervention tracking, and outcome ROI analysis",
  "target_audience": ["Data Analysts", "Researchers", "District Leadership"],
  "refresh_interval": "5 minutes",
  "dashboard_tabs": [
    {
      "name": "Correlation Analysis",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 3],
          "type": "table",
          "title": "Key Performance Correlations",
          "query": "SELECT variable1, variable2, correlation_strength, p_value, effect_size, significance_level FROM v_performance_correlations ORDER BY ABS(correlation_strength) DESC"
        }
      ]
    },
    {
      "name": "Intervention Tracking",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 4],
          "type": "funnel",
          "title": "Intervention Funnel",
          "query": "SELECT stage, COUNT(DISTINCT student_id) as students FROM (SELECT student_id, 'Identified' as stage FROM v_wellbeing_risk_profiles WHERE risk_score > 40 UNION ALL SELECT student_id, 'Referred' FROM interventions WHERE status IN ('referred', 'in_progress', 'completed') UNION ALL SELECT student_id, 'In Progress' FROM interventions WHERE status = 'in_progress' UNION ALL SELECT student_id, 'Completed' FROM interventions WHERE status = 'completed' UNION ALL SELECT student_id, 'Successful' FROM interventions WHERE status = 'completed' AND outcome = 'success') GROUP BY stage ORDER BY FIELD(stage, 'Identified', 'Referred', 'In Progress', 'Completed', 'Successful')"
        }
      ]
    },
    {
      "name": "ROI Analysis",
      "cards": [
        {
          "position": [0, 0],
          "size": [12, 3],
          "type": "scatter",
          "title": "ROI by Intervention Type",
          "query": "SELECT intervention_type, cost_per_student, outcome_improvement, roi FROM intervention_roi WHERE school_year = YEAR(CURRENT_DATE) ORDER BY roi DESC"
        }
      ]
    }
  ]
}
```

---

## Metabase Configuration Best Practices

### Connection Setup

```yaml
Database: DuckDB
Name: OSS Framework Student Analytics
Engine: DuckDB
File: /path/to/oss_framework/data/oea.duckdb

Connection Settings:
  Connection timeout: 60 seconds
  Query timeout: 60 seconds
  Test data: Enabled
  Caching:
    Query result cache TTL: 60 seconds
    Dashboard cache TTL: 600 seconds
```

### Performance Optimization

```yaml
Caching Strategy:
  Dashboard cache: 10 minutes
  Native query cache: 1 minute
  Table metadata: 1 hour
  
Query Limits:
  Fetch size: 1000 rows
  Connection pool size: 10
  Max query rows: 100,000
```

### Security Configuration

```yaml
Row-Level Security:
  Enabled: true
  
  Roles:
    - name: admin
      permissions: view_all_data
      
    - name: school_leader
      permissions: filter_by_school_id
      filter: WHERE school_id IN ({{ user.school_ids }})
      
    - name: counselor
      permissions: filter_by_assigned_students
      filter: WHERE student_id IN (SELECT student_id FROM counselor_assignments WHERE counselor_id = {{ user.id }})
      
    - name: teacher
      permissions: filter_by_class
      filter: WHERE class_id IN (SELECT class_id FROM teacher_assignments WHERE teacher_id = {{ user.id }})
      
    - name: data_analyst
      permissions: view_all_data

SSL/TLS:
  Enabled: true
  Certificate: /etc/ssl/certs/metabase.crt
```

---

## Query Templates

### High-Performance Patterns

```sql
-- Pattern 1: Pre-aggregated metrics (fast)
SELECT * FROM v_chronic_absenteeism_risk
WHERE school_id = {{ school_filter }}
  AND grade_level = {{ grade_filter }}
LIMIT 1000;

-- Pattern 2: Time-series with index (fast)
SELECT DATE_TRUNC('day', created_at) as date, COUNT(*) as risk_count
FROM v_chronic_absenteeism_risk
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at);

-- Pattern 3: Drill-down queries (optimized)
SELECT 
  student_key,
  school_id,
  chronic_absenteeism_risk_score,
  attendance_rate_30d,
  discipline_incidents_30d
FROM v_chronic_absenteeism_risk
WHERE chronic_absenteeism_risk_score > {{ risk_threshold }}
  AND school_id = {{ school_filter }}
ORDER BY chronic_absenteeism_risk_score DESC
LIMIT 100;
```

---

## Next Steps

1. **Week 5**: Create dashboard templates in Metabase
2. **Week 6**: Configure parameters, filters, and access controls
3. **Week 7**: Validate performance with production data
4. **Week 8**: Train users and go live
