
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
    CAST(EXTRACT(YEAR FROM attendance_date) AS VARCHAR) as academic_year,
    CAST(NULL AS VARCHAR) as attendance_program_code,

    CAST(COUNT(*) AS INTEGER) as days_enrolled,
    CAST(SUM(CASE WHEN COALESCE(present_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as days_present,
    CAST(SUM(CASE WHEN COALESCE(absent_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as days_absent,
    CAST(SUM(CASE WHEN COALESCE(excused_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as days_excused,
    CAST(SUM(CASE WHEN COALESCE(unexcused_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as days_unexcused,
    CAST(SUM(CASE WHEN COALESCE(tardy_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as days_tardy,
    0 as days_truancy,
    0 as days_suspended,
    0 as days_in_school_suspension,
    0 as days_complete_independent_study,
    0 as days_incomplete_independent_study,

    CAST(COUNT(*) AS INTEGER) as periods_expected,
    CAST(SUM(CASE WHEN COALESCE(present_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as periods_attended,
    CAST(SUM(CASE WHEN COALESCE(excused_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as periods_excused_absence,
    CAST(SUM(CASE WHEN COALESCE(unexcused_flag, false) THEN 1 ELSE 0 END) AS INTEGER) as periods_unexcused_absence,
    0 as periods_out_of_school_suspension,
    0 as periods_in_school_suspension,

    CASE
        WHEN COUNT(*) > 0 THEN CAST(SUM(CASE WHEN COALESCE(present_flag, false) THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE)
        ELSE 0.0
    END as attendance_rate,
    CASE
        WHEN COUNT(*) > 0 THEN CAST(SUM(CASE WHEN COALESCE(absent_flag, false) THEN 1 ELSE 0 END) AS DOUBLE) / CAST(COUNT(*) AS DOUBLE)
        ELSE 0.0
    END as absence_rate,
    CASE
        WHEN SUM(CASE WHEN COALESCE(absent_flag, false) THEN 1 ELSE 0 END) > 0
            THEN CAST(SUM(CASE WHEN COALESCE(excused_flag, false) THEN 1 ELSE 0 END) AS DOUBLE)
               / CAST(SUM(CASE WHEN COALESCE(absent_flag, false) THEN 1 ELSE 0 END) AS DOUBLE)
        ELSE 0.0
    END as excused_absence_rate,

    MIN(CAST(created_at AS TIMESTAMP)) as created_at,
    MAX(CAST(created_at AS TIMESTAMP)) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_attendance') }}
WHERE created_at IS NOT NULL
GROUP BY 1, 2, 3, 4
