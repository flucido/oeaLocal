# Equity Outcomes by Demographics Model
# Reads from dbt-generated table in DuckDB

type: model
sql: |
  SELECT
    race_ethnicity,
    english_learner,
    special_education,
    economically_disadvantaged,
    cohort_size,
    pct_good_attendance,
    pct_no_discipline,
    avg_gpa,
    pct_gpa_2_5_plus,
    pct_below_c,
    _loaded_at
  FROM main_analytics.v_equity_outcomes_by_demographics
