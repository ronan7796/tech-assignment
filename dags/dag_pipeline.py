from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
import pendulum
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
VENV_PATH = ROOT_DIR / ".venv"

with DAG(
    dag_id="countries_pipeline",
    start_date=pendulum.datetime(2025, 10, 5, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["etl", "countries"],
    max_active_runs=1,
) as dag:

    crawl_api_task = BashOperator(
        task_id="crawl_api",
        bash_command=f"source {VENV_PATH}/bin/activate && python {ROOT_DIR}/crawler/crawl_api.py"
    )

    crawl_web_task = BashOperator(
        task_id="crawl_web",
        bash_command=f"source {VENV_PATH}/bin/activate && python {ROOT_DIR}/crawler/crawl_web.py"
    )

    etl_task = BashOperator(
        task_id="etl_pipeline",
        bash_command=f"source {VENV_PATH}/bin/activate && python {ROOT_DIR}/etl/etl_pipeline.py"
    )

    sql_generate_task = BashOperator(
        task_id="sql_generate",
        bash_command=f"source {VENV_PATH}/bin/activate && python {ROOT_DIR}/etl/sql_generator.py"
    )

    upload_s3_task = BashOperator(
        task_id="upload_to_s3_sim",
        bash_command=f"source {VENV_PATH}/bin/activate && python {ROOT_DIR}/infra/s3_upload.py"
    )

    crawl_api_task >> crawl_web_task >> etl_task >> sql_generate_task >> upload_s3_task
