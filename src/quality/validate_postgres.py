import os

import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops",
)


def main():
    engine = create_engine(DATABASE_URL)

    df = pd.read_sql(
        "SELECT * FROM dicom_metadata",
        engine,
    )

    print(f"Rows found: {len(df)}")

    required_columns = [
        "file_path",
        "patient_id",
        "modality",
        "study_date",
        "manufacturer",
        "body_part",
        "study_description",
        "series_description",
        "hospital",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if len(df) == 0:
        raise ValueError(
            "No records found in dicom_metadata"
        )

    print("Data quality checks passed!")


if __name__ == "__main__":
    main()