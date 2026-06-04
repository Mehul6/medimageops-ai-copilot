from pydicom import dcmread
from pydicom.data import get_testdata_file

filename = get_testdata_file("CT_small.dcm")
dataset = dcmread(filename)

print("Patient ID:", dataset.PatientID)
print("Modality:", dataset.Modality)
print("Study Date:", dataset.StudyDate)

if hasattr(dataset, "BodyPartExamined"):
    print("Body Part:", dataset.BodyPartExamined)