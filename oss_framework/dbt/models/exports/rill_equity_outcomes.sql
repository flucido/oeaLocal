{{
  config(
    materialized='external',
    location='/Users/flucido/projects/local-data-stack/rill_project/data/equity_outcomes_by_demographics.parquet',
    format='parquet',
    tags=['rill_export']
  )
}}

SELECT * FROM {{ ref('v_equity_outcomes_by_demographics') }}
