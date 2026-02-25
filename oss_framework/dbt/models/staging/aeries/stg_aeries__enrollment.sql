
-- models/staging/stg_enrollment.sql
-- Staging: Standardize raw_enrollment with schema normalization

{{ config(
    schema='staging',
    tags=['staging', 'enrollment']
) }}

SELECT
    -- Identifiers
    CAST(StudentID AS VARCHAR) as student_id_raw,
    CAST(SchoolCode AS VARCHAR) as school_id,
    CAST(StudentNumber AS VARCHAR) as student_number,
    -- Terms and years
    CAST(AcademicYear AS VARCHAR) as school_year,
    CAST(Grade AS INTEGER) as grade_level,
    CAST(Track AS VARCHAR) as track,
    -- Enrollment tracking
    CAST(EnterDate AS DATE) as enrollment_date,
    CAST(LeaveDate AS DATE) as withdrawal_date,
    CAST(ExitReasonCode AS VARCHAR) as exit_reason_code,
    
    -- Calculated enrollment status
    CASE 
        WHEN LeaveDate IS NULL THEN 'ACTIVE'
        ELSE 'WITHDRAWN'
    END as enrollment_status,
    
    -- Attendance program codes
    CAST(AttendanceProgramCode AS VARCHAR) as attendance_program_code,
    CAST(AttendanceProgramCodeAdditional1 AS VARCHAR) as attendance_program_code_add1,
    
    -- Audit and tracking fields
    CAST(ExtractedAt AS TIMESTAMP) as created_at,
    CAST(ExtractedAt AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_enrollment') }}
WHERE ExtractedAt IS NOT NULL

