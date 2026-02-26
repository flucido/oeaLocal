-- Chronic Absenteeism Risk Model
-- Source: Parquet export from dbt model v_chronic_absenteeism_risk
-- Reference documentation: https://docs.rilldata.com/build/models

SELECT * FROM read_parquet('data/chronic_absenteeism_risk.parquet')
