#!/usr/bin/env python3
"""PHI-free 16x16 uncompressed CT phantoms (G-P0-026). Three slices for §0.8 min."""
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

root = Path(__file__).resolve().parents[1] / "corpus" / "phantoms"
root.mkdir(parents=True, exist_ok=True)

study = "1.2.826.0.1.3680043.10.541.1.1"
series = "1.2.826.0.1.3680043.10.541.1.2"
for inst, z in enumerate((0.0, 10.0, 20.0), start=1):
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = f"1.2.826.0.1.3680043.10.541.1.2.{inst}"
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
    out = root / f"G-P0-phantom-ct-{inst:02d}.dcm"
    ds = FileDataset(str(out), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.SOPClassUID = CTImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = study
    ds.SeriesInstanceUID = series
    ds.Modality = "CT"
    ds.PatientName = "GENESIS^PHANTOM"
    ds.PatientID = "G0A-001"
    ds.StudyDate = "20200101"
    ds.ContentDate = "20200101"
    ds.StudyTime = "000000"
    ds.ContentTime = "000000"
    ds.AccessionNumber = "1"
    ds.StudyID = "1"
    ds.SeriesNumber = 1
    ds.Manufacturer = "GenesisOracle"
    ds.Rows = 16
    ds.Columns = 16
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelSpacing = [1.0, 1.0]
    ds.SliceThickness = 1.0
    ds.ImagePositionPatient = [0.0, 0.0, z]
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    ds.InstanceNumber = inst
    ds.PixelData = b"".join((i & 0xFFFF).to_bytes(2, "little") for i in range(16 * 16))
    ds.save_as(out, write_like_original=False)
    print("wrote", out)

alias = root / "G-P0-phantom-ct.dcm"
alias.write_bytes((root / "G-P0-phantom-ct-02.dcm").read_bytes())
print("wrote", alias)
