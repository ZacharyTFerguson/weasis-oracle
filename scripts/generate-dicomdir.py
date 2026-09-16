#!/usr/bin/env python3
"""Build a PHI-free DICOMDIR media set (G-P0-021 / §0.8)."""
import shutil
import tempfile
from pathlib import Path

from pydicom import dcmread
from pydicom.fileset import FileSet

root = Path(__file__).resolve().parents[1]
ph = root / "corpus/phantoms"
files = [
    ph / "G-P0-phantom-ct-01.dcm",
    ph / "G-P0-phantom-ct-02.dcm",
    ph / "G-P0-phantom-ct-03.dcm",
]
for f in files:
    if not f.is_file():
        raise SystemExit(f"missing {f}")

out = ph / "G-P0-iod-dicomdir"
if out.exists():
    shutil.rmtree(out)

with tempfile.TemporaryDirectory() as tmp:
    fs = FileSet()
    fs.ID = "GENESIS"
    for i, f in enumerate(files, start=1):
        dest = Path(tmp) / f"src{i}.dcm"
        ds = dcmread(f)
        ds.StudyID = "1"
        ds.SeriesNumber = 1
        if not getattr(ds, "StudyTime", None):
            ds.StudyTime = "000000"
        ds.save_as(dest, write_like_original=False)
        fs.add(str(dest))
    fs.write(out)

dicomdir = out / "DICOMDIR"
if not dicomdir.is_file():
    raise SystemExit(f"DICOMDIR not a file: {dicomdir}")
print("wrote", dicomdir)
