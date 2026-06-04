import os
from pathlib import Path

import boto3


LOCAL_DICOM_DIR = Path("data/raw/dicom")

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX", "medimageops/raw/dicom")


def clear_local_dicom_folder():
    LOCAL_DICOM_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in LOCAL_DICOM_DIR.rglob("*.dcm"):
        file_path.unlink()

    print(f"Cleared existing local DICOM files from {LOCAL_DICOM_DIR}")


def download_dicom_files_from_s3():
    if not S3_BUCKET:
        raise ValueError("S3_BUCKET environment variable is not set.")

    s3_client = boto3.client("s3")

    clear_local_dicom_folder()

    paginator = s3_client.get_paginator("list_objects_v2")

    downloaded_count = 0

    for page in paginator.paginate(
        Bucket=S3_BUCKET,
        Prefix=S3_PREFIX,
    ):
        for obj in page.get("Contents", []):
            s3_key = obj["Key"]

            if not s3_key.endswith(".dcm"):
                continue

            relative_path = Path(s3_key).relative_to(S3_PREFIX)
            local_path = LOCAL_DICOM_DIR / relative_path

            local_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"Downloading s3://{S3_BUCKET}/{s3_key} to {local_path}")

            s3_client.download_file(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Filename=str(local_path),
            )

            downloaded_count += 1

    print(f"Downloaded {downloaded_count} DICOM files from S3.")

    if downloaded_count == 0:
        raise ValueError("No DICOM files downloaded from S3.")


if __name__ == "__main__":
    download_dicom_files_from_s3()