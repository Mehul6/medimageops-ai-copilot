from pydicom import dcmread
from pydicom.data import get_testdata_files
import pandas as pd

files = get_testdata_files("*.dcm")

records = []

for file in files[:10]:

    try:
        ds = dcmread(file, stop_before_pixels=True)

        records.append({
            "patient_id": getattr(ds, "PatientID", None),
            "modality": getattr(ds, "Modality", None),
            "study_date": getattr(ds, "StudyDate", None),
            "manufacturer": getattr(ds, "Manufacturer", None)
        })

    except Exception as e:
        print(f"Error reading {file}: {e}")

df = pd.DataFrame(records)

print(df.head())
print("\nTotal Records:", len(df))