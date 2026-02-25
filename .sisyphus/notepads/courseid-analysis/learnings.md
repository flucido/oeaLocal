# CourseID cross-pipeline type analysis

- Raw stage1: stage_1.courses.course_id is UUID (section in docker/init-db 00_stage1_raw.sql)
- Staging: stg_aeries__academic_records.course_id is VARCHAR (CAST(CourseID AS VARCHAR))
- Analytics (core): fact_academic_records.course_id is VARCHAR (inherited from staging)
- Analytics (class section): v_class_section_comparison uses ace.course_id (VARCHAR)