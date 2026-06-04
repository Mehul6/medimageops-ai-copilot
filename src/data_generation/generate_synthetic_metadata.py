from pathlib import Path
import random

import pandas as pd


OUTPUT_PATH = Path("data/processed/dicom_metadata.csv")
NUM_RECORDS = 100_000

S3_BUCKET = "medimageops-mehul-bisht"
S3_PREFIX = "medimageops/raw/dicom/synthetic"

MANUFACTURERS = [
    "SIEMENS",
    "GE MEDICAL SYSTEMS",
    "PHILIPS",
    "CANON",
    "TOSHIBA",
]

HOSPITALS = [
    "Mass General",
    "Brigham and Women's",
    "Boston Medical Center",
    "Mayo Clinic",
    "Cleveland Clinic",
]

STUDY_CATALOG = {
    "CHEST": {
        "CT": ["Lung Screening CT", "Chest CT"],
        "XR": ["Chest X-Ray"],
    },
    "BRAIN": {
        "MR": ["Brain MRI"],
        "CT": ["Head CT"],
    },
    "ABDOMEN": {
        "CT": ["Abdominal CT"],
        "US": ["Abdominal Ultrasound"],
    },
    "PELVIS": {
        "MR": ["Pelvic MRI"],
        "CT": ["Pelvic CT"],
    },
    "SPINE": {
        "MR": ["Spine MRI"],
    },
    "KNEE": {
        "MR": ["Knee MRI"],
        "XR": ["Knee X-Ray"],
    },
}


def generate_record(index):
    patient_id = f"P{random.randint(1, 50_000):06d}"

    body_part = random.choice(list(STUDY_CATALOG.keys()))
    modality = random.choice(list(STUDY_CATALOG[body_part].keys()))
    study_description = random.choice(
        STUDY_CATALOG[body_part][modality]
    )

    manufacturer = random.choice(MANUFACTURERS)
    hospital = random.choice(HOSPITALS)

    year = random.randint(2018, 2026)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    study_date = f"{year}{month:02d}{day:02d}"

    return {
        "file_path": (
            f"s3://{S3_BUCKET}/{S3_PREFIX}/"
            f"instance-{index:06d}.dcm"
        ),
        "patient_id": patient_id,
        "modality": modality,
        "study_date": study_date,
        "manufacturer": manufacturer,
        "body_part": body_part,
        "study_description": study_description,
        "series_description": (
            f"{body_part}_{modality}_SERIES_"
            f"{random.randint(1, 20)}"
        ),
        "hospital": hospital,
    }


def main():
    print(
        f"Generating {NUM_RECORDS:,} realistic synthetic "
        "DICOM metadata records..."
    )

    records = [
        generate_record(index)
        for index in range(1, NUM_RECORDS + 1)
    ]

    df = pd.DataFrame(records)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Saved {len(df):,} records to {OUTPUT_PATH}")
    print(df.head())


if __name__ == "__main__":
    main()