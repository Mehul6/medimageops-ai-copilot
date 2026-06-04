import pandas as pd

data = {
    "patient_id": ["id00001", None, "4MR1", "", None],
    "modality": ["RTPLAN", None, "MR", "SR", None],
    "study_date": ["20030716", None, "20040826", "", None],
    "manufacturer": ["Manufacturer name here", None, "TOSHIBA_MEC", "Kuratorium OFFIS e.V.", None],
}

df = pd.DataFrame(data)

print("Before cleaning:")
print(df)

df = df.dropna(subset=["patient_id", "modality", "study_date"])
df = df[df["patient_id"].str.strip() != ""]
df = df[df["study_date"].str.strip() != ""]

print("\nAfter cleaning:")
print(df)