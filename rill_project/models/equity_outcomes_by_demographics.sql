-- Equity Outcomes by Demographics Model
-- Source: Parquet export from dbt model v_equity_outcomes_by_demographics
-- Reference documentation: https://docs.rilldata.com/build/models

SELECT * FROM read_parquet('data/equity_outcomes_by_demographics.parquet')
