{{
  config(
    materialized='external',
    location='/Users/flucido/projects/local-data-stack/rill_project/data/chronic_absenteeism_risk.parquet',
    format='parquet',
    tags=['rill_export']
  )
}}

SELECT * FROM {{ ref('v_chronic_absenteeism_risk') }}
