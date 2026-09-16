#!/usr/bin/env python3
"""Prove every named G-P0-023 edge object exists and matches its claim. Exit 1 on miss."""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

from pydicom import dcmread
from pydicom.uid import ImplicitVRLittleEndian, JPEGBaseline8Bit

root = Path(__file__).resolve().parents[1]
phantoms = root / "corpus" / "phantoms"
huge_path = Path(os.environ.get("GENESIS_HUGE_OUT", str(phantoms / "G-P0-edge-gt2gb.dcm")))
two_gib = 2 * 1024 * 1024 * 1024
expected_pixel_vl = 2_148_007_936


class Fail(Exception):
    pass


def must(path: Path) -> Path:
    if not path.exists():
        raise Fail(f"missing {path}")
    return path


def dcm(path: Path, **kw):
    return dcmread(str(path), force=True, stop_before_pixels=kw.pop("stop_before_pixels", False), **kw)


def check_no_preamble() -> str:
    p = must(phantoms / "G-P0-extra-no-preamble.dcm")
    raw = p.read_bytes()
    if raw[128:132] == b"DICM" or raw[:132] == b"\0" * 128 + b"DICM":
        raise Fail("no-preamble still has 128-byte preamble + DICM")
    if raw[:4] == b"DICM":
        raise Fail("no-preamble starts with DICM")
    if raw[:2] != b"\x02\x00":
        raise Fail(f"no-preamble should start at File Meta (0002,xxxx), got {raw[:8]!r}")
    return p.name


def check_raw_stream() -> str:
    p = must(phantoms / "G-P0-edge-raw-stream.dcm")
    raw = p.read_bytes()
    if b"DICM" in raw[:132]:
        raise Fail("raw stream still contains DICM")
    if raw[:2] == b"\x02\x00":
        raise Fail("raw stream still has File Meta group 0002")
    if raw[:2] != b"\x08\x00":
        raise Fail(f"raw stream should start at group 0008 implicit, got {raw[:8]!r}")
    ds = dcm(p, stop_before_pixels=True)
    if ds.file_meta and getattr(ds.file_meta, "TransferSyntaxUID", None):
        # pydicom may invent meta on read; the bytes must not include it.
        pass
    return p.name


def check_implicit_explicit_meta() -> str:
    p = must(phantoms / "G-P0-extra-implicit.dcm")
    raw = p.read_bytes()
    if raw[128:132] != b"DICM":
        raise Fail("implicit file missing Part 10 DICM (explicit File Meta wrapper)")
    ds = dcm(p, stop_before_pixels=True)
    ts = str(ds.file_meta.TransferSyntaxUID)
    if ts != str(ImplicitVRLittleEndian):
        raise Fail(f"want Implicit VR LE body, ts={ts}")
    return p.name


def check_undef_sq() -> str:
    p = must(phantoms / "G-P0-edge-undef-sq.dcm")
    ds = dcm(p, stop_before_pixels=True)
    elem = ds[0x0008, 0x1110]
    if not elem.is_undefined_length:
        raise Fail("ReferencedStudySequence is defined-length")
    return p.name


def check_odd_length() -> str:
    p = must(phantoms / "G-P0-edge-odd-length.dcm")
    raw = p.read_bytes()
    marker = b"\x09\x00\x01\x10UN\x00\x00"
    idx = raw.find(marker)
    if idx < 0:
        raise Fail("odd-length UN marker not found")
    vl = int.from_bytes(raw[idx + 8 : idx + 12], "little")
    if vl % 2 == 0:
        raise Fail(f"UN VL {vl} is even")
    return p.name


def check_truncated() -> str:
    p = must(phantoms / "G-P0-extra-truncated.dcm")
    raw = p.read_bytes()
    marker = bytes([0xE0, 0x7F, 0x10, 0x00])
    idx = raw.find(marker)
    if idx < 0:
        # File is so short Pixel Data never appears — still a truncated object.
        if p.stat().st_size >= 1024:
            raise Fail("truncated file has no Pixel Data but is not short")
        return p.name
    # Explicit VR: OW/OB + reserved + 4-byte VL, or implicit 4-byte VL after tag.
    if raw[idx + 4 : idx + 6] in {b"OW", b"OB"}:
        vl = int.from_bytes(raw[idx + 8 : idx + 12], "little")
        data_off = idx + 12
    else:
        vl = int.from_bytes(raw[idx + 4 : idx + 8], "little")
        data_off = idx + 8
    remain = len(raw) - data_off
    if remain >= vl:
        raise Fail(f"Pixel Data not truncated: remain={remain} vl={vl}")
    return p.name


def check_no_bot() -> str:
    p = must(phantoms / "G-P0-edge-no-bot.dcm")
    ds = dcm(p)
    if str(ds.file_meta.TransferSyntaxUID) != str(JPEGBaseline8Bit):
        raise Fail(f"no-BOT ts {ds.file_meta.TransferSyntaxUID}")
    raw = p.read_bytes()
    marker = bytes([0xE0, 0x7F, 0x10, 0x00])
    idx = raw.find(marker)
    if idx < 0:
        raise Fail("no-BOT Pixel Data tag missing")
    # Encapsulated: after OW/OB VL (FFFFFFFF), first item should be empty BOT (FFFE E000 VL=0).
    frag = raw[idx:]
    bot = bytes([0xFE, 0xFF, 0x00, 0xE0, 0x00, 0x00, 0x00, 0x00])
    if bot not in frag[:64]:
        raise Fail("encapsulated Pixel Data has no empty Basic Offset Table item")
    return p.name


def check_multi_fragment() -> str:
    p = must(phantoms / "G-P0-edge-multi-fragment.dcm")
    ds = dcm(p)
    pix = bytes(ds.PixelData) if isinstance(ds.PixelData, (bytes, bytearray)) else ds.PixelData
    # Count item delimiters FFFE E000 in encapsulated stream (BOT + fragments).
    blob = pix if isinstance(pix, (bytes, bytearray)) else bytes(pix)
    item = b"\xfe\xff\x00\xe0"
    n = blob.count(item)
    if n < 3:  # empty-or-filled BOT + two fragments
        raise Fail(f"want multi-fragment encapsulated items, found {n}")
    return p.name


def check_huge() -> str:
    p = must(huge_path)
    st = p.stat()
    if st.st_size <= two_gib:
        raise Fail(f"huge st_size {st.st_size} is not >2 GiB")
    with p.open("rb") as f:
        head = f.read(65536)
    marker = bytes([0xE0, 0x7F, 0x10, 0x00, 0x4F, 0x57])
    idx = head.rfind(marker)
    if idx < 0:
        raise Fail("huge PixelData OW tag not in first 64 KiB")
    vl = int.from_bytes(head[idx + 8 : idx + 12], "little")
    if vl != expected_pixel_vl:
        raise Fail(f"huge PixelData VL {vl} != {expected_pixel_vl}")
    ds = dcm(p, stop_before_pixels=True)
    frames = int(ds.NumberOfFrames)
    if frames != 4097 or int(ds.Rows) != 512 or int(ds.Columns) != 512:
        raise Fail(f"huge geometry frames={frames} rows={ds.Rows} cols={ds.Columns}")
    if not stat.S_ISREG(st.st_mode):
        raise Fail("huge is not a regular file")
    return f"{p.name} st_size={st.st_size} vl={vl} frames={frames} blocks={st.st_blocks}"


def check_12bit() -> str:
    p = must(phantoms / "G-P0-edge-12bit.dcm")
    ds = dcm(p, stop_before_pixels=True)
    if not (int(ds.BitsAllocated) == 16 and int(ds.BitsStored) == 12 and int(ds.HighBit) == 11):
        raise Fail(f"12-bit fields {ds.BitsAllocated}/{ds.BitsStored}/{ds.HighBit}")
    return p.name


def check_signed_rescale() -> str:
    p = must(phantoms / "G-P0-edge-signed-rescale.dcm")
    ds = dcm(p, stop_before_pixels=True)
    if int(ds.PixelRepresentation) != 1:
        raise Fail("not signed")
    if "RescaleIntercept" not in ds or "RescaleSlope" not in ds:
        raise Fail("missing Rescale")
    return p.name


def check_mono1_plut() -> str:
    p = must(phantoms / "G-P0-edge-mono1-plut.dcm")
    ds = dcm(p, stop_before_pixels=True)
    if str(ds.PhotometricInterpretation) != "MONOCHROME1":
        raise Fail(ds.PhotometricInterpretation)
    if "PresentationLUTSequence" not in ds:
        raise Fail("no Presentation LUT")
    return p.name


def check_ybr_jpeg() -> str:
    p = must(phantoms / "G-P0-codec-jpeg-baseline-us-01.dcm")
    ds = dcm(p, stop_before_pixels=True)
    if str(ds.PhotometricInterpretation) != "YBR_FULL_422":
        raise Fail(str(ds.PhotometricInterpretation))
    if str(ds.file_meta.TransferSyntaxUID) != str(JPEGBaseline8Bit):
        raise Fail(str(ds.file_meta.TransferSyntaxUID))
    return p.name


def check_overlay() -> str:
    p = must(phantoms / "G-P0-edge-overlay-highbits.dcm")
    ds = dcm(p, stop_before_pixels=True)
    bitpos = ds[0x6000, 0x0102].value
    if int(bitpos) != 15:
        raise Fail(f"OverlayBitPosition {bitpos}")
    return p.name


def check_private() -> str:
    p = must(phantoms / "G-P0-edge-private-creator.dcm")
    ds = dcm(p, stop_before_pixels=True)
    if (0x0009, 0x0010) not in ds:
        raise Fail("private creator missing")
    return p.name


def check_dicomdir_case() -> str:
    ddir = must(phantoms / "G-P0-edge-dicomdir-case" / "DICOMDIR")
    ds = dcm(ddir)
    ids = []
    for rec in ds.DirectoryRecordSequence:
        if "ReferencedFileID" in rec:
            val = rec.ReferencedFileID
            if isinstance(val, (list, tuple)):
                ids.append(tuple(str(x) for x in val))
            else:
                ids.append((str(val),))
    if not ids:
        raise Fail("DICOMDIR has no ReferencedFileID")
    tree = phantoms / "G-P0-edge-dicomdir-case"
    mismatch = False
    for parts in ids:
        on_disk = tree.joinpath(*parts)
        if not on_disk.exists():
            mismatch = True
            break
        # If the recorded ID exists as-is, look for a case-folded twin that differs.
        lower = tree.joinpath(*[p.lower() for p in parts])
        if lower.exists() and any(a != a.lower() for a in parts):
            mismatch = True
            break
    if not mismatch:
        # Directory names on disk are lowercase vs DICOMDIR components.
        disk_names = {p.relative_to(tree).as_posix() for p in tree.rglob("*") if p.is_file()}
        for parts in ids:
            joined = "/".join(parts)
            if joined not in disk_names and joined.lower() in {n.lower() for n in disk_names}:
                mismatch = True
                break
    if not mismatch:
        raise Fail(f"no case mismatch; ids={ids[:3]} disk={sorted(disk_names)[:6]}")
    return str(ddir.relative_to(root))


def check_missing_uids() -> str:
    series = dcm(must(phantoms / "G-P0-extra-missing-series.dcm"), stop_before_pixels=True)
    study = dcm(must(phantoms / "G-P0-extra-missing-study.dcm"), stop_before_pixels=True)
    if "SeriesInstanceUID" in series:
        raise Fail("series UID still present")
    if "StudyInstanceUID" in study:
        raise Fail("study UID still present")
    return "G-P0-extra-missing-series.dcm + G-P0-extra-missing-study.dcm"


CASES = [
    ("no preamble / raw stream", [check_no_preamble, check_raw_stream]),
    ("implicit VR body with explicit meta", [check_implicit_explicit_meta]),
    ("undefined-length sequences/items", [check_undef_sq]),
    ("odd lengths", [check_odd_length]),
    ("truncated Pixel Data", [check_truncated]),
    ("encapsulated frames with no Basic Offset Table", [check_no_bot]),
    ("multi-fragment frames", [check_multi_fragment]),
    (">2 GB multi-frame", [check_huge]),
    ("12-bit-in-16 HighBit", [check_12bit]),
    ("signed + Rescale", [check_signed_rescale]),
    ("MONOCHROME1 + Presentation LUT", [check_mono1_plut]),
    ("YBR_FULL_422 + baseline JPEG US", [check_ybr_jpeg]),
    ("overlays in high bits (retired)", [check_overlay]),
    ("private creator blocks", [check_private]),
    ("DICOMDIR with case-mismatched referenced file IDs", [check_dicomdir_case]),
    ("missing Series/Study UIDs (Weasis synthesizes)", [check_missing_uids]),
]


def main() -> int:
    results = []
    failed = 0
    for name, fns in CASES:
        notes = []
        ok = True
        err = None
        for fn in fns:
            try:
                notes.append(fn())
            except Fail as e:
                ok = False
                err = str(e)
                break
            except Exception as e:
                ok = False
                err = f"{type(e).__name__}: {e}"
                break
        results.append({"name": name, "ok": ok, "evidence": notes, "error": err})
        mark = "PASS" if ok else "FAIL"
        extra = ", ".join(notes) if ok else err
        print(f"{mark}  {name}  {extra}")
        if not ok:
            failed += 1
    payload = {
        "schemaVersion": "genesis.oracle.v1",
        "caseId": "G-P0-023",
        "class": "PR",
        "reference": {
            "weasisTag": "v4.7.0",
            "weasisCommit": "3b3e46c59879ead782e5c474e895befae616a715",
        },
        "allNamedCasesPassed": failed == 0,
        "cases": results,
        "hugeNotCommitted": True,
        "hugeGenerator": "scripts/generate-huge-multiframe.py",
        "hugePixelVL": expected_pixel_vl,
    }
    out = root / "corpus" / "goldens" / "G-P0-023.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", out, "failed", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
