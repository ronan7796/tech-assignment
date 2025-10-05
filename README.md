# Technical Assessment — Mini Data Pipeline (POC)

## Overview
This repo implements a POC pipeline:
- Crawl REST Countries API & scrape Wikipedia table → save raw JSON
- ETL: normalize to tabular schema, export CSV, Parquet, Excel
- Generate PostgreSQL UPSERT SQL file
- Simulate S3 upload (local folder)
- Provide CDC & AWS DMS doc + Airflow DAG example

## Setup (local)
Create a virtualenv and install dependencies:

# crawler deps
pip install requests beautifulsoup4

# etl deps
pip install pandas pyarrow openpyxl

# optional S3:
pip install boto3

## Run locally (simple)

Use run_samples.sh 

Outputs will be under `outputs/` and `sql/countries_upsert.sql`. Simulated S3 files are in `s3_sim/`.

## Airflow
Drop `airflow/dag_pipeline.py` into your Airflow DAGs folder. Adjust paths.

## Notes
- This is a POC. For production: add logging, retries, secrets management (AWS creds) and paginated crawling logic.
