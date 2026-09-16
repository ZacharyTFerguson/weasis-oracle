#!/usr/bin/env python3
"""Remaining G-P0-023 edge-axis phantoms (PHI-free). Does not write a >2 GB object."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.encaps import decode_data_sequence, encapsulate
from pydicom.filebase import DicomFileLike
from pydicom.fileset import FileSet
from pydicom.filewriter import write_dataset
from pydicom.sequence import Sequence
from pydicom.uid import (
    CTImageStorage,
    ExplicitVRLittleEndian,
    JPEGBaseline8Bit,
)

root = Path(__file__).resolve().parents[1] / "corpus" / "phantoms"
root.mkdir(parents=True, exist_ok=True)


def meta(sop_class: str, inst: str, ts=ExplicitVRLittleEndian) -> FileMetaDataset:
    m = FileMetaDataset()
    m.MediaStorageSOPClassUID = sop_class
    m.MediaStorageSOPInstanceUID = inst
    m.TransferSyntaxUID = ts
    m.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
    return m


def ct_base(inst: str, suffix: str) -> FileDataset:
    ds = FileDataset(str(root / "x"), {}, file_meta=meta(CTImageStorage, inst), preamble=b"\0" * 128)
    ds.SOPClassUID = CTImageStorage
    ds.SOPInstanceUID = inst
    ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.90.1"
    ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.90.2"
    ds.Modality = "CT"
    ds.PatientName = "GENESIS^PHANTOM"
    ds.PatientID = "G0A-023"
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
    ds.ImagePositionPatient = [0.0, 0.0, 0.0]
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    ds.InstanceNumber = 1
    ds.PixelData = b"".join((i & 0xFFFF).to_bytes(2, "little") for i in range(16 * 16))
    return ds


def save(ds: FileDataset, name: str) -> Path:
    out = root / name
    ds.save_as(out, write_like_original=False)
    print("wrote", out)
    return out


# Undefined-length sequence + item (ReferencedStudySequence).
ds = ct_base("1.2.826.0.1.3680043.10.541.90.10", "undef-sq")
item = Dataset()
item.ReferencedSOPClassUID = CTImageStorage
item.ReferencedSOPInstanceUID = ds.SOPInstanceUID
ds.ReferencedStudySequence = Sequence([item])
ds[0x0008, 0x1110].is_undefined_length = True
item.is_undefined_length_sequence_item = True
save(ds, "G-P0-edge-undef-sq.dcm")

# Odd-length UN private value: strip the even pad after write.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.11", "odd")
ds.add_new((0x0009, 0x0010), "LO", "GENESIS_ODD")
ds.add_new((0x0009, 0x1001), "UN", bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE]))
odd_path = save(ds, "G-P0-edge-odd-length.dcm")
# Explicit VR UN uses 32-bit VL. pydicom 3 already wrote 5 bytes (odd). If a
# writer pads to even, strip the pad.
raw = bytearray(odd_path.read_bytes())
marker = b"\x09\x00\x01\x10UN\x00\x00"
idx = raw.find(marker)
if idx < 0:
    raise SystemExit("odd-length UN marker not found")
vl = int.from_bytes(raw[idx + 8 : idx + 12], "little")
if vl % 2 == 0:
    raw[idx + 8 : idx + 12] = (vl - 1).to_bytes(4, "little")
    del raw[idx + 12 + vl - 1]
    odd_path.write_bytes(raw)
    print("stripped UN pad", odd_path, "vl", vl, "->", vl - 1)
else:
    print("UN already odd vl", vl, odd_path)

# Encapsulated JPEG, no Basic Offset Table.
jpeg_src = root / "G-P0-codec-jpeg-baseline-us-01.dcm"
ds = ct_base("1.2.826.0.1.3680043.10.541.90.12", "no-bot")
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"
ds.file_meta = meta(ds.SOPClassUID, ds.SOPInstanceUID, JPEGBaseline8Bit)
ds.Modality = "US"
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "YBR_FULL_422"
ds.PlanarConfiguration = 0
if jpeg_src.is_file():
    src = dcmread(jpeg_src)
    frames = decode_data_sequence(src.PixelData)
else:
    frames = [b"\xff\xd8\xff\xd9"]
ds.PixelData = encapsulate(frames, has_bot=False)
ds["PixelData"].is_undefined_length = True
save(ds, "G-P0-edge-no-bot.dcm")

# Multi-fragment single frame.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.13", "multi-frag")
ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"
ds.file_meta = meta(ds.SOPClassUID, ds.SOPInstanceUID, JPEGBaseline8Bit)
ds.Modality = "US"
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "YBR_FULL_422"
ds.PixelData = encapsulate(frames[:1] or [b"\xff\xd8\xff\xd9"], fragments_per_frame=2)
ds["PixelData"].is_undefined_length = True
save(ds, "G-P0-edge-multi-fragment.dcm")

# 12-bit stored in 16-bit allocated (HighBit 11).
ds = ct_base("1.2.826.0.1.3680043.10.541.90.14", "12bit")
ds.BitsStored = 12
ds.HighBit = 11
ds.PixelData = b"".join((i & 0x0FFF).to_bytes(2, "little") for i in range(16 * 16))
save(ds, "G-P0-edge-12bit.dcm")

# Signed pixels + Rescale.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.15", "signed")
ds.PixelRepresentation = 1
ds.RescaleIntercept = "-1024"
ds.RescaleSlope = "1"
ds.RescaleType = "HU"
pix = []
for i in range(16 * 16):
    v = (i % 2000) - 1000
    pix.append(v.to_bytes(2, "little", signed=True))
ds.PixelData = b"".join(pix)
save(ds, "G-P0-edge-signed-rescale.dcm")

# MONOCHROME1 + Presentation LUT Sequence.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.16", "plut")
ds.PhotometricInterpretation = "MONOCHROME1"
plut = Dataset()
plut.LUTDescriptor = [256, 0, 8]
plut.LUTData = bytes(range(256))
ds.PresentationLUTSequence = Sequence([plut])
save(ds, "G-P0-edge-mono1-plut.dcm")

# Retired overlay in high bits of Pixel Data (group 0x6000).
ds = ct_base("1.2.826.0.1.3680043.10.541.90.17", "overlay")
ds.add_new((0x6000, 0x0010), "US", 16)  # OverlayRows
ds.add_new((0x6000, 0x0011), "US", 16)  # OverlayColumns
ds.add_new((0x6000, 0x0040), "CS", "G")  # OverlayType
ds.add_new((0x6000, 0x0050), "SS", [1, 1])  # OverlayOrigin
ds.add_new((0x6000, 0x0100), "US", 1)  # OverlayBitsAllocated
ds.add_new((0x6000, 0x0102), "US", 15)  # OverlayBitPosition
pixels = bytearray(ds.PixelData)
for i in range(0, len(pixels), 2):
    if (i // 2) % 5 == 0:
        pixels[i + 1] |= 0x80  # set bit 15
ds.PixelData = bytes(pixels)
save(ds, "G-P0-edge-overlay-highbits.dcm")

# Private creator block.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.18", "private")
ds.add_new((0x0009, 0x0010), "LO", "GENESIS_PRIVATE")
ds.add_new((0x0009, 0x1001), "LO", "edge-axis")
ds.add_new((0x0009, 0x1002), "IS", "23")
save(ds, "G-P0-edge-private-creator.dcm")

# DICOMDIR whose Referenced File ID case does not match the files on disk.
src_ct = root / "G-P0-phantom-ct-01.dcm"
if not src_ct.is_file():
    raise SystemExit(f"missing {src_ct}")
out = root / "G-P0-edge-dicomdir-case"
if out.exists():
    shutil.rmtree(out)
with tempfile.TemporaryDirectory() as tmp:
    fs = FileSet()
    fs.ID = "GENCASE"
    dest = Path(tmp) / "src.dcm"
    src = dcmread(src_ct)
    src.StudyID = "1"
    src.SeriesNumber = 1
    if not getattr(src, "StudyTime", None):
        src.StudyTime = "000000"
    src.save_as(dest, write_like_original=False)
    fs.add(str(dest))
    fs.write(out)
# Rename every file under the patient tree to lowercase; DICOMDIR keeps original IDs.
for p in sorted(out.rglob("*"), reverse=True):
    if p.name in {"DICOMDIR"} or not p.is_file():
        if p.is_dir() and p.name not in {"DICOMDIR"} and p.name != out.name:
            lower = p.with_name(p.name.lower())
            if lower != p and not lower.exists():
                p.rename(lower)
        continue
    lower = p.with_name(p.name.lower())
    if lower != p:
        p.rename(lower)
print("wrote", out / "DICOMDIR", "(Referenced File ID case mismatch)")

# Raw implicit-VR dataset stream: no 128-byte preamble, no DICM, no File Meta.
ds = ct_base("1.2.826.0.1.3680043.10.541.90.19", "raw")
ds.is_little_endian = True
ds.is_implicit_VR = True
raw_path = root / "G-P0-edge-raw-stream.dcm"
with raw_path.open("wb") as f:
    fp = DicomFileLike(f)
    fp.is_little_endian = True
    fp.is_implicit_VR = True
    write_dataset(fp, ds)
print("wrote", raw_path, "(raw stream, no preamble/DICM/meta)")

print("G-P0-023 >2 GiB multi-frame is on-demand: python3 scripts/generate-huge-multiframe.py")
