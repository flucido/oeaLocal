
-- models/staging/stg_enrollment.sql
-- Staging: Standardize raw_enrollment with schema normalization

{{ config(
    schema='staging',
    tags=['staging', 'enrollment']
) }}

SELECT
    CAST(student_id AS VARCHAR) as student_id_raw,
    CAST(school_id AS VARCHAR) as school_id,
    CAST(NULL AS VARCHAR) as student_number,
    CAST(school_year AS VARCHAR) as school_year,
    CAST(grade_level AS INTEGER) as grade_level,
    CAST(NULL AS VARCHAR) as track,
    CAST(enrollment_date AS DATE) as enrollment_date,
    CAST(withdrawal_date AS DATE) as withdrawal_date,
    CAST(NULL AS VARCHAR) as exit_reason_code,

    CASE
        WHEN withdrawal_date IS NULL THEN COALESCE(UPPER(CAST(enrollment_status AS VARCHAR)), 'ACTIVE')
        ELSE 'WITHDRAWN'
    END as enrollment_status,

    CAST(NULL AS VARCHAR) as attendance_program_code,
    CAST(NULL AS VARCHAR) as attendance_program_code_add1,

    CAST(created_at AS TIMESTAMP) as created_at,
    CAST(created_at AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_enrollment') }}
WHERE created_at IS NOT NULL
