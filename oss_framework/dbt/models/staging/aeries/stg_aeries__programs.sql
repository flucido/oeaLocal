-- models/staging/stg_aeries__programs.sql
-- Staging: Standardize raw_aeries_programs with schema normalization
-- Provides program participation data for student demographics

{{ config(
    schema='staging',
    tags=['staging', 'programs']
) }}

SELECT
    -- Identifiers
    CAST(StudentID AS VARCHAR) as student_id_raw,
    CAST(ProgramCode AS VARCHAR) as program_code,
    CAST(ProgramDescription AS VARCHAR) as program_description,
    -- Academic context
    CAST(AcademicYear AS VARCHAR) as academic_year,
    -- Dates
    CAST(EligibilityStartDate AS DATE) as eligibility_start_date,
    CAST(EligibilityEndDate AS DATE) as eligibility_end_date,
    CAST(ParticipationStartDate AS DATE) as participation_start_date,
    CAST(ParticipationEndDate AS DATE) as participation_end_date,
    -- Calculated status
    CASE 
        WHEN EligibilityEndDate IS NULL THEN true
        ELSE false
    END as is_currently_active,
    -- Program categorization
    CASE ProgramCode
        WHEN '144' THEN 'Special Education'
        WHEN '181' THEN 'Free Lunch'
        WHEN '182' THEN 'Reduced-Price Lunch'
        WHEN '101' THEN 'Section 504'
        WHEN '191' THEN 'Homeless'
        WHEN '190' THEN 'Foster'
        WHEN '127' THEN 'GATE'
        WHEN '305' THEN 'ELL Program'
        WHEN '122' THEN 'Title I'
        WHEN '185' THEN 'Transitional Kindergarten'
        ELSE 'Other'
    END as program_category,
    -- Metadata
    CAST(ExtractedAt AS TIMESTAMP) as created_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp
FROM {{ source('raw', 'raw_aeries_programs') }}
WHERE ExtractedAt IS NOT NULL
