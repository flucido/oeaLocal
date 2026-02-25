-- models/staging/stg_students.sql
-- Staging: Standardize raw_students with schema normalization
-- Light transformations: age calculation, enrollment status, grade categorization
-- Updated: Added race codes (RaceCode1-5) and program participation flags

{{ config(
    schema='staging',
    tags=['staging', 'students']
) }}

WITH program_flags AS (
    -- Aggregate program participation per student
    SELECT
        CAST(StudentID AS VARCHAR) as student_id_raw,
        -- Special Education (ProgramCode 144)
        MAX(CASE WHEN ProgramCode = '144' THEN true ELSE false END) as special_education_flag,
        -- Free/Reduced Lunch (ProgramCode 181 = Free, 182 = Reduced)
        MAX(CASE WHEN ProgramCode IN ('181', '182') THEN true ELSE false END) as free_reduced_lunch_flag,
        -- Section 504 (ProgramCode 101)
        MAX(CASE WHEN ProgramCode = '101' THEN true ELSE false END) as section_504_flag,
        -- Homeless (ProgramCode 191)
        MAX(CASE WHEN ProgramCode = '191' THEN true ELSE false END) as homeless_flag,
        -- Foster (ProgramCode 190)
        MAX(CASE WHEN ProgramCode = '190' THEN true ELSE false END) as foster_care_flag,
        -- GATE (ProgramCode 127)
        MAX(CASE WHEN ProgramCode = '127' THEN true ELSE false END) as gate_flag,
        -- ELL/Language Immersion (ProgramCode 305)
        MAX(CASE WHEN ProgramCode = '305' THEN true ELSE false END) as ell_program_flag
    FROM {{ source('raw', 'raw_aeries_programs') }}
    WHERE EligibilityEndDate IS NULL  -- Currently active programs
    GROUP BY StudentID
)

SELECT
    -- Identifiers (will be hashed in privacy layer)
    CAST(s.StudentID AS VARCHAR) as student_id_raw,
    CAST(s.FirstName AS VARCHAR) as first_name_raw,
    CAST(s.LastName AS VARCHAR) as last_name_raw,
    CAST(s.Birthdate AS DATE) as date_of_birth_raw,
    -- Demographics
    CAST(s.Gender AS VARCHAR) as gender,
    CAST(s.EthnicityCode AS VARCHAR) as ethnicity,
    -- Race codes (Federal Race Categories - RC1-RC5)
    CAST(s.RaceCode1 AS VARCHAR) as race_code_1,
    CAST(s.RaceCode2 AS VARCHAR) as race_code_2,
    CAST(s.RaceCode3 AS VARCHAR) as race_code_3,
    CAST(s.RaceCode4 AS VARCHAR) as race_code_4,
    CAST(s.RaceCode5 AS VARCHAR) as race_code_5,
    CAST(s.Grade AS INTEGER) as grade_level,
    CAST(s.SchoolCode AS VARCHAR) as school_id,
    -- Calculated demographics
    DATE_PART('year', AGE(CURRENT_DATE, CAST(s.Birthdate AS DATE))) as age,
    CASE 
        WHEN s.Grade BETWEEN 1 AND 5 THEN 'Elementary'
        WHEN s.Grade BETWEEN 6 AND 8 THEN 'Middle'
        WHEN s.Grade BETWEEN 9 AND 12 THEN 'High'
        ELSE 'Unknown'
    END as grade_level_category,
    
    -- Enrollment status flags
    CAST(s.AttendanceProgramCodePrimary AS VARCHAR) as attendance_program_code,
    CAST(s.LanguageFluencyCode AS VARCHAR) as ell_status,
    -- Program participation flags (from programs table)
    COALESCE(pf.special_education_flag, false) as special_education_flag,
    COALESCE(pf.free_reduced_lunch_flag, false) as free_reduced_lunch_flag,
    COALESCE(pf.homeless_flag, false) as homeless_flag,
    COALESCE(pf.foster_care_flag, false) as foster_care_flag,
    COALESCE(pf.section_504_flag, false) as section_504_flag,
    COALESCE(pf.gate_flag, false) as gate_flag,
    COALESCE(pf.ell_program_flag, false) as ell_program_flag,
    -- Language
    COALESCE(CAST(s.HomeLanguageCode AS VARCHAR), 'ENGLISH') as home_language,
    -- Enrollment dates
    CAST(s.SchoolEnterDate AS DATE) as enrollment_date,
    CAST(s.SchoolLeaveDate AS DATE) as withdrawal_date,
    -- Calculated enrollment status
    CASE 
        WHEN s.SchoolLeaveDate IS NULL THEN true
        ELSE false
    END as is_currently_enrolled,
    CAST(s.ExtractedAt AS TIMESTAMP) as created_at,
    CAST(s.ExtractedAt AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp
FROM {{ source('raw', 'raw_students') }} s
LEFT JOIN program_flags pf ON CAST(s.StudentID AS VARCHAR) = pf.student_id_raw
WHERE s.ExtractedAt IS NOT NULL
