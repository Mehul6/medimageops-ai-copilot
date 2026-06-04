from src.ingestion.dicom_to_csv import run_dicom_to_csv_pipeline
from src.database.load_to_postgres import main as load_to_postgres


def run_pipeline():
    print("Starting MedImageOps pipeline...")

    print("Step 1: Extract, clean, and save DICOM metadata")
    run_dicom_to_csv_pipeline()

    print("Step 2: Load clean metadata into PostgreSQL")
    load_to_postgres()

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()