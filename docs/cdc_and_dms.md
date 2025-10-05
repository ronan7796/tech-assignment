# CDC & AWS DMS — Conceptual Plan (Countries Pipeline)

## Objective

Replicate a `countries` table from **PostgreSQL → S3** in near-real-time using **Change Data Capture (CDC)**, and then replicate **from S3 → PostgreSQL** in hourly batches

This ensures that any updates to country or capital data are continuously captured and synchronized across systems with minimal latency

---

## 1. PostgreSQL → S3 using CDC (Change Data Capture)

### Concept

**Change Data Capture (CDC)** allows real-time streaming of data changes (INSERT, UPDATE, DELETE) without performing full table dumps

**AWS Database Migration Service (DMS)** leverages PostgreSQLs **logical replication** to read from the Write-Ahead Log (WAL) and continuously deliver these changes to a target in this case, **Amazon S3**

### Architecture

```
PostgreSQL (Source)
   ↓
AWS DMS Source Endpoint (CDC)
   ↓
AWS DMS Task
   ↓
Amazon S3 (Target)
```

### Steps

1. **Enable logical replication** on PostgreSQL:

   ```sql
   ALTER SYSTEM SET wal_level = logical;
   ALTER SYSTEM SET max_replication_slots = 5;
   ALTER SYSTEM SET max_wal_senders = 5;
   SELECT pg_reload_conf();
   ```

2. **Create a replication user**:

   ```sql
   CREATE USER dms_user WITH REPLICATION PASSWORD 'your_password';
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO dms_user;
   ```

3. **Configure AWS DMS Source Endpoint**
   - Engine: PostgreSQL  
   - Endpoint type: Source  
   - Enable CDC: True
   - Connection: (host, port, username, password, database)

4. **Configure AWS DMS Target Endpoint**
   - Engine: Amazon S3  
   - S3 bucket: `s3://country-cdc-data/`  
   - Output format: `Parquet` or `JSON`  
   - Compression: `gzip` (optional)  
   - Folder structure: `/countries/year=/month=/day=/hour=`

5. **Create and run AWS DMS Task**
   - Migration type: `cdc`  
   - Table mapping includes only `public.countries`  
   - Enable logging and automatic task restarts  
   - Once started, DMS continuously streams country data changes into S3

---

## 2. S3 → PostgreSQL (Hourly Batch Replication)

### Concept

After the CDC data lands in S3, an hourly batch job reloads it into a PostgreSQL target database

This is useful for maintaining an **analytics-ready replica** of the `countries` dataset or synchronizing environments for downstream processing

### Architecture

```
Amazon S3 (CDC data)
   ↓
AWS Glue / Lambda / Airflow Job (every hour)
   ↓
PostgreSQL Staging Table
   ↓
Merge / Upsert into Target `countries` Table
```

### Steps

1. **Schedule a job** (hourly):
   - AWS Glue Workflow with a 1-hour trigger  
   - or AWS Lambda via EventBridge (cron)  
   - or Apache Airflow DAG with `@hourly` schedule  

2. **Extract** the CDC files from S3 generated within the last hour

3. **Transform & Load**:
   - Read CDC files (Parquet or JSON) using **pandas** or **Spark**
   - Validate and clean columns (`cca3`, `name`, `capital`, `region`, `population`, etc.)
   - Load into a temporary staging table (e.g., `countries_staging`)
   - Perform an **UPSERT** into the target table:

   ```sql
   INSERT INTO countries (cca3, name, capital, region, population, updated_at)
   VALUES (%s, %s, %s, %s, %s, %s)
   ON CONFLICT (cca3)
   DO UPDATE SET
       name = EXCLUDED.name,
       capital = EXCLUDED.capital,
       region = EXCLUDED.region,
       population = EXCLUDED.population,
       updated_at = EXCLUDED.updated_at;
   ```

---

## 3. Example AWS DMS JSON Configuration

Below is a simplified example of an AWS DMS **task configuration** for replicating the `countries` table

```json
{
  "ReplicationTaskIdentifier": "countries-cdc-postgres-to-s3",
  "SourceEndpointArn": "arn:aws:dms:ap-southeast-1:123456789012:endpoint:SOURCE_POSTGRES",
  "TargetEndpointArn": "arn:aws:dms:ap-southeast-1:123456789012:endpoint:TARGET_S3",
  "MigrationType": "cdc",
  "TableMappings": {
    "rules": [
      {
        "rule-type": "selection",
        "rule-id": "1",
        "rule-name": "include-countries",
        "object-locator": {
          "schema-name": "public",
          "table-name": "countries"
        },
        "rule-action": "include"
      }
    ]
  },
  "ReplicationTaskSettings": {
    "TargetMetadata": {
      "TargetSchema": "",
      "SupportLobs": true
    },
    "FullLoadSettings": {
      "TargetTablePrepMode": "DO_NOTHING"
    },
    "Logging": {
      "EnableLogging": true
    },
    "ControlTablesSettings": {
      "historyTimeslotInMinutes": 5
    }
  }
}
```

---

## Summary

| Direction | Method | Frequency | Tool | Mode |
|------------|----------|-------------|---------|-------|
| PostgreSQL → S3 | CDC Streaming | Near real-time | AWS DMS | Continuous |
| S3 → PostgreSQL | Batch Load | Every 1 hour | AWS Glue / Airflow / Lambda | Scheduled |

---

This design ensures that **country and capital data** is captured continuously, stored durably in S3, and synchronized back to PostgreSQL on a scheduled basis providing both real-time updates and reliable batch replication for analytics or downstream services
