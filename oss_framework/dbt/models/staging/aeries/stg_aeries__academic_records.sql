
-- models/staging/stg_academic_records.sql
-- Staging: Standardize raw_academic_records with schema normalization
-- Light transformations: GPA conversion, pass/fail categorization

{{ config(
    schema='staging',
    tags=['staging', 'academic']
) }}

SELECT
    CAST(student_id AS VARCHAR) as student_id_raw,
    CAST(course_id AS VARCHAR) as course_id,
    CAST(NULL AS VARCHAR) as course_title,
    CAST(section_id AS VARCHAR) as section_id,
    CAST(teacher_id AS VARCHAR) as teacher_id,
    CAST(school_id AS VARCHAR) as school_id,
    CAST(school_year AS VARCHAR) as school_year,
    CAST(term AS VARCHAR) as term,

    COALESCE(CAST(grade AS VARCHAR), 'INCOMPLETE') as grade,
    CAST(NULL AS DECIMAL(5,2)) as credit_earned,

    CASE
        WHEN grade IN ('A', 'A-') THEN 4.0
        WHEN grade IN ('B+', 'B', 'B-') THEN 3.0
        WHEN grade IN ('C+', 'C', 'C-') THEN 2.0
        WHEN grade IN ('D+', 'D', 'D-') THEN 1.0
        WHEN grade = 'F' THEN 0.0
        WHEN grade = 'P' THEN 4.0
        WHEN grade = 'NP' THEN 0.0
        ELSE TRY_CAST(score AS DOUBLE)
    END as gpa_points,

    CASE
        WHEN grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P') THEN true
        WHEN grade IN ('F', 'NP') THEN false
        ELSE NULL
    END as is_passing,

    CAST(NULL AS INTEGER) as total_absences,
    CAST(NULL AS INTEGER) as total_tardies,
    CAST(NULL AS INTEGER) as days_enrolled,
    CAST(NULL AS INTEGER) as days_present,

    CAST(created_at AS TIMESTAMP) as created_at,
    CAST(created_at AS TIMESTAMP) as updated_at,
    CURRENT_TIMESTAMP as dbt_load_timestamp,
    '{{ run_started_at }}' as dbt_run_timestamp

FROM {{ source('raw', 'raw_academic_records') }}

WHERE created_at IS NOT NULL
