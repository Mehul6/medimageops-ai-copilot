import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops",
)

QUALITY_REPORT_PATH = Path("data/reports/quality_report.csv")
OUTPUT_PATH = Path("data/processed/rag_documents.csv")


def load_dicom_metadata():
    engine = create_engine(DATABASE_URL)

    df = pd.read_sql(
        "SELECT * FROM dicom_metadata",
        engine,
    )

    print(f"Loaded {len(df)} DICOM metadata records from PostgreSQL")

    return df


def create_metadata_documents(df):
    documents = []

    for _, row in df.iterrows():
        text = (
            f"Patient {row.get('patient_id')} underwent a "
            f"{row.get('body_part')} {row.get('modality')} scan "
            f"on study date {row.get('study_date')}. "
            f"The scanner manufacturer was {row.get('manufacturer')}. "
            f"The study description was {row.get('study_description')}. "
            f"The series description was {row.get('series_description')}. "
            f"The source DICOM file path is {row.get('file_path')}."
        )

        documents.append(
            {
                "document_type": "dicom_metadata",
                "source_id": row.get("file_path"),
                "text": text,
            }
        )

    return documents


def create_quality_report_documents():
    documents = []

    if not QUALITY_REPORT_PATH.exists():
        print("Quality report not found. Skipping quality report documents.")
        return documents

    report_df = pd.read_csv(QUALITY_REPORT_PATH)

    for _, row in report_df.iterrows():
        text = (
            f"The data quality metric '{row.get('metric')}' "
            f"has value {row.get('value')}."
        )

        documents.append(
            {
                "document_type": "quality_report",
                "source_id": row.get("metric"),
                "text": text,
            }
        )

    print(f"Loaded {len(documents)} quality report documents")

    return documents


def main():
    metadata_df = load_dicom_metadata()

    metadata_documents = create_metadata_documents(metadata_df)
    quality_documents = create_quality_report_documents()

    all_documents = metadata_documents + quality_documents

    output_df = pd.DataFrame(all_documents)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Created {len(output_df)} RAG documents")
    print(f"Saved RAG documents to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()