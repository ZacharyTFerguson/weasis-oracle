#!/usr/bin/env python3
"""Wrap OpenJPH HTJ2K codestreams into PHI-free DICOM objects (G-P0-016).

Requires ojph_compress (OpenJPH). Does not count as a G-P0-022 corpus floor
unless the frozen 4.7 binary actually opens the object.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from pydicom.dataset import Dataset, FileDataset
from pydicom.encaps import encapsulate
from pydicom.filewriter import dcmwrite
from pydicom.uid import UID

ROOT = Path(__file__).resolve().parents[1]
PH = ROOT / "corpus" / "phantoms"

# dcm4che UID.java names in weasis-dicom-codec-4.7.0 (verified by Htj2kProbe).
TS_HTJ2K_LOSSLESS = UID("1.2.840.10008.1.2.4.201")
TS_HTJ2K_LOSSLESS_RPCL = UID("1.2.840.10008.1.2.4.202")
TS_HTJ2K = UID("1.2.840.10008.1.2.4.203")


def find_ojph() -> Path:
    env = shutil.which("ojph_compress")
    if env:
        return Path(env)
    cand = Path("/tmp/OpenJPH/build/src/apps/ojph_compress/ojph_compress")
    if cand.is_file():
        return cand
    raise SystemExit("ojph_compress not found; build OpenJPH or put it on PATH")


def write_pgm(path: Path, width: int = 16, height: int = 16) -> None:
    pix = bytes((i * 17) % 256 for i in range(width * height))
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode() + pix)


def compress(ojph: Path, pgm: Path, j2c: Path, reversible: bool, prog_order: str) -> None:
    cmd = [
        str(ojph),
        "-i",
        str(pgm),
        "-o",
        str(j2c),
        "-reversible",
        "true" if reversible else "false",
        "-prog_order",
        prog_order,
        "-num_decomps",
        "2",
    ]
    subprocess.check_call(cmd)


def wrap(j2c: Path, out: Path, ts: UID, sop_suffix: str, patient_id: str) -> None:
    bitstream = j2c.read_bytes()
    if bitstream[:2] != b"\xff\x4f":
        raise SystemExit(f"{j2c} is not a JPEG 2000 codestream (missing SOC)")
    sop = f"1.2.826.0.1.3680043.10.541.60.{sop_suffix}"
    meta = Dataset()
    meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
    meta.MediaStorageSOPInstanceUID = sop
    meta.TransferSyntaxUID = ts
    meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
    ds = FileDataset(str(out), {}, file_meta=meta, preamble=b"\0" * 128)
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = sop
    ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.60"
    ds.SeriesInstanceUID = f"1.2.826.0.1.3680043.10.541.60.{sop_suffix}.2"
    ds.Modality = "SC"
    ds.PatientName = "GENESIS^PHANTOM"
    ds.PatientID = patient_id
    ds.Rows = 16
    ds.Columns = 16
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = encapsulate([bitstream])
    try:
        ds.save_as(out, write_like_original=False)
    except ValueError:
        dcmwrite(out, ds, implicit_vr=False, little_endian=True, force_encoding=True, overwrite=True)
    print("wrote", out, "ts", ts, "bytes", out.stat().st_size)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ojph", type=Path, default=None)
    args = parser.parse_args()
    ojph = args.ojph if args.ojph else find_ojph()
    PH.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/g0a-htj2k-gen")
    tmp.mkdir(exist_ok=True)
    pgm = tmp / "src.pgm"
    write_pgm(pgm)

    jobs = [
        ("lrcp.j2c", True, "LRCP", TS_HTJ2K_LOSSLESS, "1", "G-P0-probe-htj2k-lossless.dcm", "G0A-HTJ201"),
        ("rpcl.j2c", True, "RPCL", TS_HTJ2K_LOSSLESS_RPCL, "2", "G-P0-probe-htj2k-lossless-rpcl.dcm", "G0A-HTJ202"),
        ("lossy.j2c", False, "RPCL", TS_HTJ2K, "3", "G-P0-probe-htj2k.dcm", "G0A-HTJ203"),
    ]
    for j2c_name, rev, order, ts, suffix, out_name, pid in jobs:
        j2c = tmp / j2c_name
        compress(ojph, pgm, j2c, rev, order)
        wrap(j2c, PH / out_name, ts, suffix, pid)


if __name__ == "__main__":
    sys.exit(main())
