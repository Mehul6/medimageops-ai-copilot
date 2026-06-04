from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine


CSV_PATH = Path("data/processed/dicom_metadata.csv")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://meduser:medpassword@localhost:5432/medimageops"
)


def main():
    df = pd.read_csv(CSV_PATH)

    print(f"Loaded CSV rows: {len(df)}")
    print("Columns:", list(df.columns))

    engine = create_engine(DATABASE_URL)

    df.to_sql(
        name="dicom_metadata",
        con=engine,
        if_exists="replace",
        index=False,
    )

    print("Saved data to PostgreSQL table: dicom_metadata")


if __name__ == "__main__":
    main()