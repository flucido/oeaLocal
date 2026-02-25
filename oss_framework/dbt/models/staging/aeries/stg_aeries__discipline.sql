
-- models/staging/stg_discipline.sql
-- Staging: Standardize raw_discipline with schema normalization

{{ config(
    schema='staging',
    tags=['staging', 'discipline']
) }}

SELECT
    -- Identifiers
    CAST(IncidentID AS VARCHAR) as incident_id,
    CAST(StudentID AS VARCHAR) as student_id_raw,
    CAST(SchoolOfIncidentCode AS VARCHAR) as school_id,
    CAST(AcademicYear AS VARCHAR) as academic_year,
    -- Incident details
    CAST(IncidentDate AS DATE) as incident_date,
    CAST(LocationCode AS VARCHAR) as location_code,
    CAST(ShortDescription AS VARCHAR) as short_description,
    CAST(Comment AS VARCHAR) as comment,
    
    -- Action details
    CAST(Admin_DispositionCode AS VARCHAR) as disposition_code,
    CAST(Admin_Days AS INTEGER) as suspension_days,
    CAST(Admin_Hours AS DECIMAL(5,2)) as suspension_hours,
    CAST(Admin_StartDate AS DATE) as admin_start_date,
    CAST(Admin_EndDate AS DATE) as admin_end_date,
    CAST(Demerits AS INTEGER) as demerits,
    
    -- Calculated severity (based on suspension days)
    CASE 
        WHEN Admin_Days IS NULL OR Admin_Days = 0 THEN 'Low'
        WHEN Admin_Days BETWEEN 1 AND 3 THEN 'Medium'
        WHEN Admin_Days > 3 THEN 'High'
        ELSE 'Unknown'
    END as severity_category,
    
    -- Suspension indicator
    CASE 
        WHEN Admin_Days > 0 THEN true
        ELSE false
    END as is_suspension,
    
    -- Audit and tracking fields
    CAST(ExtractedAt AS TIMESTAMP) as created_at,
    CAST(ExtractedAt AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_discipline') }}
WHERE ExtractedAt IS NOT NULL

