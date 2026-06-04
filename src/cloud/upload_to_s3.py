import os
from pathlib import Path

import boto3


LOCAL_DICOM_DIR = Path("data/raw/dicom")

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX", "medimageops/raw/dicom")


def upload_dicom_files_to_s3():
    if not S3_BUCKET:
        raise ValueError("S3_BUCKET environment variable is not set.")

    s3_client = boto3.client("s3")

    dicom_files = list(LOCAL_DICOM_DIR.rglob("*.dcm"))

    print(f"Found {len(dicom_files)} local DICOM files.")

    if not dicom_files:
        raise ValueError(f"No .dcm files found in {LOCAL_DICOM_DIR}")

    for file_path in dicom_files:
        relative_path = file_path.relative_to(LOCAL_DICOM_DIR)
        s3_key = f"{S3_PREFIX}/{relative_path}"

        print(f"Uploading {file_path} to s3://{S3_BUCKET}/{s3_key}")

        s3_client.upload_file(
            Filename=str(file_path),
            Bucket=S3_BUCKET,
            Key=s3_key,
        )

    print("Upload completed successfully.")


if __name__ == "__main__":
    upload_dicom_files_to_s3()