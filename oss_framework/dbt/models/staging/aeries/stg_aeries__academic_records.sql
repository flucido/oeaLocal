
-- models/staging/stg_academic_records.sql
-- Staging: Standardize raw_academic_records with schema normalization
-- Light transformations: GPA conversion, pass/fail categorization

{{ config(
    schema='staging',
    tags=['staging', 'academic']
) }}

SELECT
    -- Identifiers
    CAST(StudentID AS VARCHAR) as student_id_raw,
    CAST(CourseID AS VARCHAR) as course_id,
    CAST(CourseTitle AS VARCHAR) as course_title,
    CAST(SectionNumber AS VARCHAR) as section_id,
    CAST(TeacherNumber AS VARCHAR) as teacher_id,
    CAST(SchoolCode AS VARCHAR) as school_id,
    CAST(AcademicYear AS VARCHAR) as school_year,
    CAST(MP_MarkingPeriod AS VARCHAR) as term,
    
    -- Grade data
    COALESCE(CAST(MP_Mark AS VARCHAR), 'INCOMPLETE') as grade,
    CAST(MP_Credit AS DECIMAL(5,2)) as credit_earned,
    
    -- Calculated grade metrics
    CASE 
        WHEN MP_Mark IN ('A', 'A-') THEN 4.0
        WHEN MP_Mark IN ('B+', 'B', 'B-') THEN 3.0
        WHEN MP_Mark IN ('C+', 'C', 'C-') THEN 2.0
        WHEN MP_Mark IN ('D+', 'D', 'D-') THEN 1.0
        WHEN MP_Mark = 'F' THEN 0.0
        WHEN MP_Mark = 'P' THEN 4.0  -- Pass equivalent to A
        WHEN MP_Mark = 'NP' THEN 0.0  -- No Pass equivalent to F
        ELSE NULL
    END as gpa_points,
    
    CASE 
        WHEN MP_Mark IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P') THEN true
        WHEN MP_Mark IN ('F', 'NP') THEN false
        ELSE NULL
    END as is_passing,
    
    -- Attendance data
    CAST(MP_TotalAbsences AS INTEGER) as total_absences,
    CAST(MP_TotalTardies AS INTEGER) as total_tardies,
    CAST(MP_TotalDaysEnrolled AS INTEGER) as days_enrolled,
    CAST(MP_TotalDaysPresent AS INTEGER) as days_present,
    
    -- Audit and tracking fields
    CAST(ExtractedAt AS TIMESTAMP) as created_at,
    CAST(ExtractedAt AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_academic_records') }}

WHERE ExtractedAt IS NOT NULL
