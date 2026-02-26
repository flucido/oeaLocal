-- models/staging/stg_students.sql
-- Staging: Standardize raw_students with schema normalization
-- Light transformations: age calculation, enrollment status, grade categorization
-- Updated: Added race codes (RaceCode1-5) and program participation flags

{{ config(
    schema='staging',
    tags=['staging', 'students']
) }}

SELECT
    -- Identifiers (will be hashed in privacy layer)
    CAST(s.student_id AS VARCHAR) as student_id_raw,
    CAST(s.first_name AS VARCHAR) as first_name_raw,
    CAST(s.last_name AS VARCHAR) as last_name_raw,
    CAST(s.date_of_birth AS DATE) as date_of_birth_raw,
    -- Demographics
    CAST(s.gender AS VARCHAR) as gender,
    CAST(s.ethnicity AS VARCHAR) as ethnicity,
    -- Race codes (Federal Race Categories - RC1-RC5)
    CAST(NULL AS VARCHAR) as race_code_1,
    CAST(NULL AS VARCHAR) as race_code_2,
    CAST(NULL AS VARCHAR) as race_code_3,
    CAST(NULL AS VARCHAR) as race_code_4,
    CAST(NULL AS VARCHAR) as race_code_5,
    CAST(s.grade_level AS INTEGER) as grade_level,
    CAST(s.school_id AS VARCHAR) as school_id,
    -- Calculated demographics
    DATE_PART('year', AGE(CURRENT_DATE, CAST(s.date_of_birth AS DATE))) as age,
    CASE
        WHEN s.grade_level BETWEEN 1 AND 5 THEN 'Elementary'
        WHEN s.grade_level BETWEEN 6 AND 8 THEN 'Middle'
        WHEN s.grade_level BETWEEN 9 AND 12 THEN 'High'
        ELSE 'Unknown'
    END as grade_level_category,

    -- Enrollment status flags
    CAST(NULL AS VARCHAR) as attendance_program_code,
    CAST(s.ell_status AS VARCHAR) as ell_status,
    COALESCE(CAST(s.special_education AS BOOLEAN), false) as special_education_flag,
    COALESCE(CAST(s.free_reduced_lunch AS BOOLEAN), false) as free_reduced_lunch_flag,
    COALESCE(CAST(s.homeless AS BOOLEAN), false) as homeless_flag,
    COALESCE(CAST(s.foster_care AS BOOLEAN), false) as foster_care_flag,
    COALESCE(CAST(s.section_504 AS BOOLEAN), false) as section_504_flag,
    false as gate_flag,
    CASE
        WHEN s.ell_status IS NOT NULL AND TRIM(CAST(s.ell_status AS VARCHAR)) != '' THEN true
        ELSE false
    END as ell_program_flag,
    -- Language
    COALESCE(CAST(s.home_language AS VARCHAR), 'ENGLISH') as home_language,
    -- Enrollment dates
    CAST(s.enrollment_date AS DATE) as enrollment_date,
    CAST(s.withdrawal_date AS DATE) as withdrawal_date,
    -- Calculated enrollment status
    CASE
        WHEN s.withdrawal_date IS NULL THEN true
        ELSE false
    END as is_currently_enrolled,
    CAST(s.created_at AS TIMESTAMP) as created_at,
    CAST(COALESCE(s.updated_at, s.created_at) AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp
FROM {{ source('raw', 'raw_students') }} s
WHERE s.created_at IS NOT NULL
