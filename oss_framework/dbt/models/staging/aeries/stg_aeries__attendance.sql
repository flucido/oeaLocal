
-- models/staging/stg_attendance.sql
-- Staging: Standardize raw_attendance with schema normalization
-- Light transformations: date parts, day categorization

{{ config(
    schema='staging',
    tags=['staging', 'attendance']
) }}

SELECT
    CAST(student_id AS VARCHAR) as student_id_raw,
    CAST(school_id AS VARCHAR) as school_id,
    CAST(academic_year AS VARCHAR) as academic_year,
    CAST(attendance_program_code AS VARCHAR) as attendance_program_code,

    -- Aggregated metrics (already calculated in source)
    CAST(days_enrolled AS INTEGER) as days_enrolled,
    CAST(days_present AS INTEGER) as days_present,
    CAST(days_absent AS INTEGER) as days_absent,
    CAST(days_excused AS INTEGER) as days_excused,
    CAST(days_unexcused AS INTEGER) as days_unexcused,
    CAST(days_tardy AS INTEGER) as days_tardy,
    CAST(days_truancy AS INTEGER) as days_truancy,
    CAST(days_suspended AS INTEGER) as days_suspended,
    CAST(0 AS INTEGER) as days_in_school_suspension,  -- Not in source
    CAST(0 AS INTEGER) as days_complete_independent_study,  -- Not in source
    CAST(0 AS INTEGER) as days_incomplete_independent_study,  -- Not in source

    CAST(periods_expected AS INTEGER) as periods_expected,
    CAST(periods_attended AS INTEGER) as periods_attended,
    CAST(periods_excused_absence AS INTEGER) as periods_excused_absence,
    CAST(periods_unexcused_absence AS INTEGER) as periods_unexcused_absence,
    CAST(0 AS INTEGER) as periods_out_of_school_suspension,  -- Not in source
    CAST(0 AS INTEGER) as periods_in_school_suspension,  -- Not in source

    -- Rate calculations (already in source)
    CAST(attendance_rate AS DOUBLE) as attendance_rate,
    CAST(absence_rate AS DOUBLE) as absence_rate,
    CAST(excused_absence_rate AS DOUBLE) as excused_absence_rate,

    CAST(created_at AS TIMESTAMP) as created_at,
    CAST(updated_at AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_attendance') }}
WHERE created_at IS NOT NULL
