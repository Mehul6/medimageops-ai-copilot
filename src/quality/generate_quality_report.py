import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops",
)

REPORT_PATH = Path("data/reports/quality_report.csv")


def main():
    engine = create_engine(DATABASE_URL)

    df = pd.read_sql(
        "SELECT * FROM dicom_metadata",
        engine,
    )

    report_rows = [
        {
            "metric": "total_records",
            "value": len(df),
        },
        {
            "metric": "unique_patients",
            "value": df["patient_id"].nunique(),
        },
        {
            "metric": "unique_modalities",
            "value": df["modality"].nunique(),
        },
        {
            "metric": "unique_body_parts",
            "value": df["body_part"].nunique(),
        },
        {
            "metric": "unique_manufacturers",
            "value": df["manufacturer"].nunique(),
        },
        {
            "metric": "unique_hospitals",
            "value": df["hospital"].nunique(),
        },
        {
            "metric": "unique_study_descriptions",
            "value": df["study_description"].nunique(),
        },
        {
            "metric": "unique_series_descriptions",
            "value": df["series_description"].nunique(),
        },
        {
            "metric": "missing_patient_ids",
            "value": df["patient_id"].isna().sum(),
        },
        {
            "metric": "missing_hospitals",
            "value": df["hospital"].isna().sum(),
        },
    ]

    report = pd.DataFrame(report_rows)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report.to_csv(
        REPORT_PATH,
        index=False,
    )

    print(f"Quality report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()