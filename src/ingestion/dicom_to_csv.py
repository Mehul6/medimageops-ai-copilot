from pathlib import Path

import pandas as pd
from pydicom import dcmread


RAW_DICOM_DIR = Path("data/raw/dicom")
OUTPUT_PATH = Path("data/processed/dicom_metadata.csv")


def find_dicom_files(raw_dir=RAW_DICOM_DIR):
    files = list(raw_dir.rglob("*.dcm"))
    print(f"Found {len(files)} DICOM files in {raw_dir}")
    return files


def extract_metadata(file_path):
    ds = dcmread(file_path, stop_before_pixels=True)

    return {
        "file_path": str(file_path),
        "patient_id": getattr(ds, "PatientID", None),
        "modality": getattr(ds, "Modality", None),
        "study_date": getattr(ds, "StudyDate", None),
        "manufacturer": getattr(ds, "Manufacturer", None),
        "body_part": getattr(ds, "BodyPartExamined", None),
        "study_description": getattr(ds, "StudyDescription", None),
        "series_description": getattr(ds, "SeriesDescription", None),
    }


def extract_all_metadata():
    files = find_dicom_files()
    records = []

    for file in files:
        try:
            records.append(extract_metadata(file))
        except Exception as error:
            print(f"Skipping broken file: {file}")
            print(f"Reason: {error}")

    return pd.DataFrame(records)


def clean_metadata(df):
    print("Before cleaning:", len(df))

    if df.empty:
        raise ValueError(
            "No DICOM metadata extracted. Add .dcm files to data/raw/dicom."
        )

    df = df.dropna(subset=["patient_id", "modality", "study_date"])
    df = df[df["patient_id"].astype(str).str.strip() != ""]
    df = df[df["study_date"].astype(str).str.strip() != ""]

    print("After cleaning:", len(df))

    if df.empty:
        raise ValueError("All records were removed during cleaning.")

    return df


def save_metadata(df, output_path=OUTPUT_PATH):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved clean metadata to: {output_path}")


def run_dicom_to_csv_pipeline():
    df = extract_all_metadata()
    clean_df = clean_metadata(df)
    save_metadata(clean_df)


if __name__ == "__main__":
    run_dicom_to_csv_pipeline()