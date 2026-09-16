#!/usr/bin/env python3
"""G-P0-023 >2 GiB multi-frame. Sparse Pixel Data; logical size is >2 GiB. Not committed."""
from __future__ import annotations

import os
from pathlib import Path

from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian

root = Path(__file__).resolve().parents[1] / "corpus" / "phantoms"
root.mkdir(parents=True, exist_ok=True)
out = Path(os.environ.get("GENESIS_HUGE_OUT", str(root / "G-P0-edge-gt2gb.dcm")))

# 4096 frames is exactly 2 GiB of 512×512×16-bit pixels; 4097 is 524288 bytes past 2 GiB.
rows, cols, frames = 512, 512, 4097
bytes_per_frame = rows * cols * 2
pixel_bytes = bytes_per_frame * frames
two_gib = 2 * 1024 * 1024 * 1024
if pixel_bytes != 2_148_007_936:
    raise SystemExit(f"pixel_bytes math changed: {pixel_bytes}")
if not (two_gib < pixel_bytes < 2**32):
    raise SystemExit(f"Pixel Data VL must be >2 GiB and fit in 32-bit unsigned: {pixel_bytes}")

meta = FileMetaDataset()
meta.MediaStorageSOPClassUID = CTImageStorage
meta.MediaStorageSOPInstanceUID = "1.2.826.0.1.3680043.10.541.90.99"
meta.TransferSyntaxUID = ExplicitVRLittleEndian
meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
ds = FileDataset(str(out), {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = CTImageStorage
ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.90.1"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.90.99"
ds.Modality = "CT"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-023"
ds.Rows = rows
ds.Columns = cols
ds.NumberOfFrames = frames
ds.BitsAllocated = 16
ds.BitsStored = 16
ds.HighBit = 15
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelSpacing = [1.0, 1.0]
ds.ImagePositionPatient = [0.0, 0.0, 0.0]
ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
# Tiny placeholder so pydicom writes a valid Part 10 header; we then patch VL and sparse-extend.
ds.PixelData = b"\x00\x00" * (rows * cols)
ds.save_as(out, write_like_original=False)

raw = bytearray(out.read_bytes())
# Explicit VR OW Pixel Data: (7FE0,0010) then OW, reserved, 32-bit VL.
marker = bytes([0xE0, 0x7F, 0x10, 0x00, 0x4F, 0x57])  # 7FE0,0010 OW
idx = raw.rfind(marker)
if idx < 0:
    raise SystemExit("PixelData OW tag not found")
vl_off = idx + 8  # OW + 2 reserved
old_vl = int.from_bytes(raw[vl_off : vl_off + 4], "little")
if old_vl != bytes_per_frame:
    raise SystemExit(f"placeholder PixelData VL {old_vl} != one frame {bytes_per_frame}")
raw[vl_off : vl_off + 4] = pixel_bytes.to_bytes(4, "little")
header = bytes(raw[: vl_off + 4])
first_frame = bytes(raw[vl_off + 4 : vl_off + 4 + old_vl])
out.write_bytes(header + first_frame)
fd = os.open(out, os.O_RDWR)
try:
    os.lseek(fd, len(header) + pixel_bytes - 2, os.SEEK_SET)
    os.write(fd, b"\x00\x00")
finally:
    os.close(fd)
st = out.stat()
print(
    "wrote",
    out,
    "st_size",
    st.st_size,
    "blocks",
    st.st_blocks,
    "sparse_bytes_approx",
    st.st_blocks * 512,
    "pixel_vl",
    pixel_bytes,
    "frames",
    frames,
)
if st.st_size <= two_gib:
    raise SystemExit("file is not >2 GiB")
