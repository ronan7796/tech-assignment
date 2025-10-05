#!/bin/bash
set -e

echo " Mini Data Pipeline – Sample Run "

echo "[1/5] Crawling data from public API..."
python crawler/crawl_api.py

echo "[2/5] Crawling data from web page..."
python crawler/crawl_web.py

echo "[3/5] Running ETL pipeline (normalize & export formats)..."
python etl/etl_pipeline.py

echo "[4/5] Generating SQL UPSERT scripts..."
python etl/sql_generator.py

echo "[5/5] Uploading processed files to S3 (or local simulation)..."
python infra/s3_upload.py

echo " Pipeline completed successfully!"
echo " Raw data: data/raw/"
echo " Processed data: data/processed/"
echo " SQL output: output/etl_output.sql"
