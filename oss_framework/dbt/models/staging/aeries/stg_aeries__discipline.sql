
-- models/staging/stg_discipline.sql
-- Staging: Standardize raw_discipline with schema normalization

{{ config(
    schema='staging',
    tags=['staging', 'discipline']
) }}

SELECT
    CAST(incident_id AS VARCHAR) as incident_id,
    CAST(student_id AS VARCHAR) as student_id_raw,
    CAST(school_id AS VARCHAR) as school_id,
    CAST(EXTRACT(YEAR FROM incident_date) AS VARCHAR) as academic_year,
    CAST(incident_date AS DATE) as incident_date,
    CAST(NULL AS VARCHAR) as location_code,
    CAST(incident_type AS VARCHAR) as short_description,
    CAST(NULL AS VARCHAR) as comment,

    CAST(resolution AS VARCHAR) as disposition_code,
    CAST(suspension_days AS INTEGER) as suspension_days,
    CAST(NULL AS DECIMAL(5,2)) as suspension_hours,
    CAST(NULL AS DATE) as admin_start_date,
    CAST(NULL AS DATE) as admin_end_date,
    CAST(NULL AS INTEGER) as demerits,

    CASE
        WHEN LOWER(COALESCE(severity, '')) IN ('critical', 'high') THEN 'High'
        WHEN LOWER(COALESCE(severity, '')) IN ('major', 'medium') THEN 'Medium'
        WHEN LOWER(COALESCE(severity, '')) IN ('minor', 'low') THEN 'Low'
        WHEN suspension_days > 3 THEN 'High'
        WHEN suspension_days BETWEEN 1 AND 3 THEN 'Medium'
        WHEN COALESCE(suspension_days, 0) = 0 THEN 'Low'
        ELSE 'Unknown'
    END as severity_category,

    CASE
        WHEN COALESCE(suspension_days, 0) > 0 THEN true
        ELSE false
    END as is_suspension,

    CAST(created_at AS TIMESTAMP) as created_at,
    CAST(created_at AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_discipline') }}
WHERE created_at IS NOT NULL
  AND CAST(incident_id AS VARCHAR) != '0'  -- Filter invalid placeholder records
  AND student_id IS NOT NULL
  AND incident_id IS NOT NULL
