#!/usr/bin/env python3
"""Extra PHI-free phantoms for transfer-syntax and edge-case cells."""
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset
from pydicom.filewriter import dcmwrite
from pydicom.uid import (
    CTImageStorage,
    DeflatedExplicitVRLittleEndian,
    ExplicitVRBigEndian,
    ExplicitVRLittleEndian,
    ImplicitVRLittleEndian,
    RLELossless,
)

root = Path(__file__).resolve().parents[1] / "corpus" / "phantoms"
root.mkdir(parents=True, exist_ok=True)


def base(inst: int, ts, sop_suffix: str) -> FileDataset:
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = f"1.2.826.0.1.3680043.10.541.9.{inst}"
    file_meta.TransferSyntaxUID = ts
    file_meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
    out = root / f"G-P0-extra-{sop_suffix}.dcm"
    ds = FileDataset(str(out), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.SOPClassUID = CTImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.9.1"
    ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.9.2"
    ds.Modality = "CT"
    ds.PatientName = "GENESIS^PHANTOM"
    ds.PatientID = "G0A-009"
    ds.StudyDate = "20200101"
    ds.Rows = 16
    ds.Columns = 16
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelSpacing = [1.0, 1.0]
    ds.ImagePositionPatient = [0.0, 0.0, 10.0]
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    ds.InstanceNumber = inst
    ds.PixelData = b"".join((i & 0xFFFF).to_bytes(2, "little") for i in range(16 * 16))
    return ds


def save(ds: FileDataset, name: str, *, big: bool = False) -> Path:
    out = root / name
    if big:
        dcmwrite(out, ds, write_like_original=False)
    else:
        ds.save_as(out, write_like_original=False)
    print("wrote", out)
    return out


ds = base(1, ExplicitVRLittleEndian, "deflate")
ds.file_meta.TransferSyntaxUID = DeflatedExplicitVRLittleEndian
save(ds, "G-P0-extra-deflate.dcm")

ds = base(2, ExplicitVRBigEndian, "big")
save(ds, "G-P0-extra-bigendian.dcm", big=True)

ds = base(3, ExplicitVRLittleEndian, "rle")
try:
    ds.compress(RLELossless)
    save(ds, "G-P0-extra-rle.dcm")
except Exception as e:
    print("RLE skip:", type(e).__name__, e)

ds = base(4, ExplicitVRLittleEndian, "gb18030")
ds.SpecificCharacterSet = "GB18030"
ds.PatientName = "GENESIS^PHANTOM"
save(ds, "G-P0-extra-gb18030.dcm")

ds = base(5, ExplicitVRLittleEndian, "ir149")
ds.SpecificCharacterSet = "ISO 2022 IR 149"
save(ds, "G-P0-extra-ir149.dcm")

ds = base(6, ExplicitVRLittleEndian, "missing-series")
if "SeriesInstanceUID" in ds:
    del ds.SeriesInstanceUID
save(ds, "G-P0-extra-missing-series.dcm")

ds = base(7, ExplicitVRLittleEndian, "no-preamble")
p = save(ds, "G-P0-extra-no-preamble.dcm")
raw = p.read_bytes()
if raw[:128] == b"\0" * 128 and raw[128:132] == b"DICM":
    p.write_bytes(raw[132:])
    print("stripped preamble", p)

ds = base(8, ExplicitVRLittleEndian, "truncated")
p = save(ds, "G-P0-extra-truncated.dcm")
raw = p.read_bytes()
p.write_bytes(raw[: max(256, len(raw) // 2)])
print("truncated", p)

ds = base(9, ExplicitVRLittleEndian, "tilt")
ds.GantryDetectorTilt = 15.5
save(ds, "G-P0-extra-gantry-tilt.dcm")

ds = base(10, ExplicitVRLittleEndian, "sc")
ds.Modality = "SC"
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
save(ds, "G-P0-extra-sc.dcm")

ds = base(11, ImplicitVRLittleEndian, "implicit")
save(ds, "G-P0-extra-implicit.dcm")

ds = base(12, ExplicitVRLittleEndian, "missing-study")
if "StudyInstanceUID" in ds:
    del ds.StudyInstanceUID
save(ds, "G-P0-extra-missing-study.dcm")
