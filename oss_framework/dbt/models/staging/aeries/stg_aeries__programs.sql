-- models/staging/stg_aeries__programs.sql
-- Staging: Standardize raw_aeries_programs with schema normalization
-- Provides program participation data for student demographics

{{ config(
    schema='staging',
    tags=['staging', 'programs']
) }}

WITH derived_programs AS (
    SELECT CAST(student_id AS VARCHAR) as student_id_raw, '144' as program_code, 'Special Education' as program_description, created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE COALESCE(CAST(special_education AS BOOLEAN), false)

    UNION ALL

    SELECT CAST(student_id AS VARCHAR), '181', 'Free/Reduced Lunch', created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE COALESCE(CAST(free_reduced_lunch AS BOOLEAN), false)

    UNION ALL

    SELECT CAST(student_id AS VARCHAR), '101', 'Section 504', created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE COALESCE(CAST(section_504 AS BOOLEAN), false)

    UNION ALL

    SELECT CAST(student_id AS VARCHAR), '191', 'Homeless', created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE COALESCE(CAST(homeless AS BOOLEAN), false)

    UNION ALL

    SELECT CAST(student_id AS VARCHAR), '190', 'Foster', created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE COALESCE(CAST(foster_care AS BOOLEAN), false)

    UNION ALL

    SELECT CAST(student_id AS VARCHAR), '305', 'ELL Program', created_at
    FROM {{ source('raw', 'raw_students') }}
    WHERE ell_status IS NOT NULL AND TRIM(CAST(ell_status AS VARCHAR)) != ''
)

SELECT
    student_id_raw,
    program_code,
    program_description,
    CAST(NULL AS VARCHAR) as academic_year,
    CAST(NULL AS DATE) as eligibility_start_date,
    CAST(NULL AS DATE) as eligibility_end_date,
    CAST(NULL AS DATE) as participation_start_date,
    CAST(NULL AS DATE) as participation_end_date,
    true as is_currently_active,
    program_description as program_category,
    CAST(created_at AS TIMESTAMP) as created_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp
FROM derived_programs
