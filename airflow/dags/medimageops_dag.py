from datetime import datetime
import sys

sys.path.append("/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.cloud.download_from_s3 import download_dicom_files_from_s3
from src.ingestion.dicom_to_csv import run_dicom_to_csv_pipeline
from src.database.load_to_postgres import main as load_to_postgres
from src.quality.validate_postgres import main as validate_loaded_data
from src.quality.generate_quality_report import main as generate_quality_report


default_args = {
    "owner": "mehul",
}


with DAG(
    dag_id="medimageops_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["healthcare", "etl", "dicom", "s3", "data-quality"],
) as dag:

    download_dicom_from_s3 = PythonOperator(
        task_id="download_dicom_from_s3",
        python_callable=download_dicom_files_from_s3,
    )

    extract_and_clean_metadata = PythonOperator(
        task_id="extract_and_clean_metadata",
        python_callable=run_dicom_to_csv_pipeline,
    )

    load_metadata_to_postgres = PythonOperator(
        task_id="load_metadata_to_postgres",
        python_callable=load_to_postgres,
    )

    validate_loaded_data_task = PythonOperator(
        task_id="validate_loaded_data",
        python_callable=validate_loaded_data,
    )

    generate_quality_report_task = PythonOperator(
        task_id="generate_quality_report",
        python_callable=generate_quality_report,
    )

    (
        download_dicom_from_s3
        >> extract_and_clean_metadata
        >> load_metadata_to_postgres
        >> validate_loaded_data_task
        >> generate_quality_report_task
    )