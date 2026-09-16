#!/usr/bin/env python3
"""G-P0-052: Weasis vs DCMTK vs pydicom on one uncompressed CT. dcm4che is Weasis, not independent."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from pydicom import dcmread

root = Path(__file__).resolve().parents[1]
ph = Path(sys.argv[1] if len(sys.argv) > 1 else root / "corpus/phantoms/G-P0-phantom-ct-02.dcm")
if not ph.is_file():
    raise SystemExit(f"missing {ph}")

weasis_raw = None
weasis_stored = None
golden_003 = root / "corpus/goldens/G-P0-003.json"
if ph.name == "G-P0-phantom-ct-02.dcm" and golden_003.is_file():
    g = json.loads(golden_003.read_text())
    stored = g.get("storedPixelData") or {}
    weasis_stored = stored.get("sha256")
    raw = g.get("rawFrame") or {}
    weasis_raw = raw.get("sha256") if "error" not in raw else None
    if weasis_stored is None:
        weasis_stored = weasis_raw

ds = dcmread(ph)
pydicom_pixel = hashlib.sha256(ds.PixelData).hexdigest()
pydicom_array = hashlib.sha256(ds.pixel_array.tobytes()).hexdigest()

dump = subprocess.check_output(["dcmdump", str(ph)], text=True, stderr=subprocess.STDOUT)
header = {
    "StudyInstanceUID": str(ds.StudyInstanceUID),
    "SeriesInstanceUID": str(ds.SeriesInstanceUID),
    "SOPInstanceUID": str(ds.SOPInstanceUID),
    "Rows": int(ds.Rows),
    "Columns": int(ds.Columns),
    "BitsAllocated": int(ds.BitsAllocated),
    "ImagePositionPatient": [float(x) for x in ds.ImagePositionPatient],
    "ImageOrientationPatient": [float(x) for x in ds.ImageOrientationPatient],
}
for key, val in [
    ("StudyInstanceUID", header["StudyInstanceUID"]),
    ("SeriesInstanceUID", header["SeriesInstanceUID"]),
    ("SOPInstanceUID", header["SOPInstanceUID"]),
]:
    if val not in dump:
        raise SystemExit(f"dcmdump missing {key}={val}")

tmp = Path("/tmp/genesis-second-oracle.pgm")
subprocess.check_call(
    ["dcmj2pnm", "-M", "-W", "+opw", str(ph), str(tmp)],
)
parts = tmp.read_text().split()
vals = [int(x) for x in parts[4:]]
if len(vals) != header["Rows"] * header["Columns"]:
    raise SystemExit(f"dcmj2pnm values {len(vals)}")
dcmtk_raw = hashlib.sha256(b"".join(v.to_bytes(2, "little") for v in vals)).hexdigest()

disagreements: list[dict] = []
if weasis_stored is not None and not (pydicom_pixel == pydicom_array == dcmtk_raw == weasis_stored):
    disagreements.append(
        {
            "stage": "stored-pixel-sha256",
            "pydicomPixelData": pydicom_pixel,
            "pydicomPixelArray": pydicom_array,
            "dcmtkDcmj2pnm": dcmtk_raw,
            "weasisStoredPixelData": weasis_stored,
            "weasisDecodedRawFrame": weasis_raw,
            "triage": "mismatch — do not average; not a golden until explained",
        }
    )
elif weasis_stored is None and not (pydicom_pixel == pydicom_array == dcmtk_raw):
    disagreements.append(
        {
            "stage": "stored-pixel-sha256-no-weasis",
            "pydicomPixelData": pydicom_pixel,
            "pydicomPixelArray": pydicom_array,
            "dcmtkDcmj2pnm": dcmtk_raw,
            "triage": "mismatch — do not average; not a golden until explained",
        }
    )

out = {
    "schemaVersion": "genesis.oracle.v1",
    "caseId": "G-P0-052",
    "class": "ST",
    "file": ph.name,
    "reference": {
        "weasisTag": "v4.7.0",
        "weasisCommit": "3b3e46c59879ead782e5c474e895befae616a715",
    },
    "oracles": ["weasis-DumpMain-storedPixelData", "pydicom", "dcmtk-dcmdump", "dcmtk-dcmj2pnm"],
    "notIndependent": "dcm4che is the Weasis stack",
    "fusedLut": "dropped in 0a; independently derived or wait for G-P0-042 / 0b",
    "header": header,
    "dcmdumpMatchedListedUIDs": True,
    "storedPixelSHA256": {
        "pydicomPixelData": pydicom_pixel,
        "pydicomPixelArray": pydicom_array,
        "dcmtkDcmj2pnmNoModalityNoVoi": dcmtk_raw,
        "weasisStoredPixelData": weasis_stored,
        "weasisDecodedRawFrame": weasis_raw,
        "weasisRawFrame": weasis_stored,
    },
    "disagreements": disagreements,
    "threeWayStoredPixelsAgree": weasis_stored is not None and len(disagreements) == 0,
}
dest = root / "corpus/goldens/G-P0-052.json"
dest.write_text(json.dumps(out, indent=2) + "\n")
print("wrote", dest, "agree", out["threeWayStoredPixelsAgree"])
if disagreements:
    raise SystemExit("G-P0-052 disagreements")
