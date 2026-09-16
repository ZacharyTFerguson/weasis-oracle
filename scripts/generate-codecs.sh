#!/usr/bin/env bash
# PHI-free compressed phantoms via DCMTK / GDCM / ffmpeg (G-P0-022).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
ph="$root/corpus/phantoms"
mkdir -p "$ph"

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need dcmcjpeg
need dcmcjpls
need python3

python3 "$root/scripts/generate-phantom-ct.py"
python3 "$root/scripts/generate-iods.py"

# JPEG-LS (2)
dcmcjpls "$ph/G-P0-phantom-ct-01.dcm" "$ph/G-P0-codec-jpegls-01.dcm"
dcmcjpls "$ph/G-P0-phantom-ct-02.dcm" "$ph/G-P0-codec-jpegls-02.dcm"

# JPEG lossless SOF3 / SV1 (2)
dcmcjpeg +e1 "$ph/G-P0-phantom-ct-01.dcm" "$ph/G-P0-codec-jpeg-lossless-01.dcm"
dcmcjpeg +e1 "$ph/G-P0-phantom-ct-03.dcm" "$ph/G-P0-codec-jpeg-lossless-02.dcm"

# JPEG baseline US YBR (2) — 8-bit color source
dcmcjpeg +eb +cy "$ph/G-P0-iod-us-rgb.dcm" "$ph/G-P0-codec-jpeg-baseline-us-01.dcm"
# second baseline: 8-bit CT forced to 8-bit then baseline
python3 - <<'PY'
from pathlib import Path
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
root = Path("corpus/phantoms")
sop = "1.2.826.0.1.3680043.10.541.47.1"
meta = Dataset()
meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.6.1"
meta.MediaStorageSOPInstanceUID = sop
meta.TransferSyntaxUID = ExplicitVRLittleEndian
meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
ds = FileDataset(str(root / "x"), {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.47"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.47.2"
ds.Modality = "US"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-USJPG"
ds.Rows = 16
ds.Columns = 16
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "RGB"
ds.PlanarConfiguration = 0
ds.PixelData = bytes((255 - (i % 256)) for i in range(16 * 16 * 3))
ds.save_as(root / "G-P0-iod-us-rgb-2.dcm", write_like_original=False)
print("wrote", root / "G-P0-iod-us-rgb-2.dcm")
PY
dcmcjpeg +eb +cy "$ph/G-P0-iod-us-rgb-2.dcm" "$ph/G-P0-codec-jpeg-baseline-us-02.dcm"

# JPEG extended sequential (2)
dcmcjpeg +ee "$ph/G-P0-iod-us-rgb.dcm" "$ph/G-P0-codec-jpeg-extended-01.dcm"
dcmcjpeg +ee "$ph/G-P0-iod-us-rgb-2.dcm" "$ph/G-P0-codec-jpeg-extended-02.dcm"

# JPEG2000 via GDCM when present
if command -v gdcmconv >/dev/null; then
  gdcmconv -K -i "$ph/G-P0-phantom-ct-01.dcm" -o "$ph/G-P0-codec-j2k-reversible-01.dcm"
  gdcmconv -K -i "$ph/G-P0-phantom-ct-02.dcm" -o "$ph/G-P0-codec-j2k-reversible-02.dcm"
  set +o pipefail
  printf 'y\n%.0s' {1..20} | gdcmconv -K -Y -q 40 -n 1 -i "$ph/G-P0-phantom-ct-01.dcm" -o "$ph/G-P0-codec-j2k-irreversible-01.dcm"
  printf 'y\n%.0s' {1..20} | gdcmconv -K -Y -q 50 -n 1 -i "$ph/G-P0-phantom-ct-03.dcm" -o "$ph/G-P0-codec-j2k-irreversible-02.dcm"
  set -o pipefail
else
  echo "gdcmconv not installed; JPEG2000 cells stay empty until apt libgdcm-tools" >&2
fi

# MPEG-2 encapsulated video (presence object)
if command -v ffmpeg >/dev/null; then
  tmp=$(mktemp -d)
  ffmpeg -hide_banner -loglevel error -y -f lavfi -i color=c=gray:s=64x64:d=0.4:r=10 \
    -pix_fmt yuv420p -c:v mpeg2video -qscale:v 8 "$tmp/tiny.mpg"
  python3 - "$tmp/tiny.mpg" "$ph/G-P0-codec-mpeg2.dcm" <<'PY'
import sys
from pathlib import Path
from pydicom.dataset import Dataset, FileDataset
from pydicom.encaps import encapsulate
from pydicom.uid import UID

mpeg = Path(sys.argv[1]).read_bytes()
out = Path(sys.argv[2])
sop = "1.2.826.0.1.3680043.10.541.48.1"
ts = UID("1.2.840.10008.1.2.4.100")  # MPEG2 MP@ML
meta = Dataset()
meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.4.1"  # Video Photographic Image Storage? use US-MF video
# Secondary Capture Multi-frame True Color is awkward; use VL Photographic Image + MPEG TS
meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.4"
meta.MediaStorageSOPInstanceUID = sop
meta.TransferSyntaxUID = ts
meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
ds = FileDataset(str(out), {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.48"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.48.2"
ds.Modality = "XC"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-MPEG"
ds.Rows = 64
ds.Columns = 64
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "YBR_PARTIAL_420"
ds.PlanarConfiguration = 0
ds.NumberOfFrames = 4
ds.CineRate = 10
ds.FrameTime = 100
ds.LossyImageCompression = "01"
ds.LossyImageCompressionMethod = "ISO_13818_2"
ds.PixelData = encapsulate([mpeg])
ds.save_as(out, write_like_original=False)
print("wrote", out)
PY
  rm -rf "$tmp"
else
  echo "ffmpeg missing; MPEG cell empty" >&2
fi

# MPEG-4 AVC encapsulated (presence)
if command -v ffmpeg >/dev/null; then
  tmp=$(mktemp -d)
  ffmpeg -hide_banner -loglevel error -y -f lavfi -i color=c=gray:s=64x64:d=0.4:r=10 \
    -pix_fmt yuv420p -c:v libx264 -profile:v high -level 4.1 -g 10 "$tmp/tiny.mp4"
  python3 - "$tmp/tiny.mp4" "$ph/G-P0-codec-mpeg4.dcm" <<'PY'
import sys
from pathlib import Path
from pydicom.dataset import Dataset, FileDataset
from pydicom.encaps import encapsulate
from pydicom.uid import UID
from pydicom.filewriter import dcmwrite
mpeg = Path(sys.argv[1]).read_bytes()
out = Path(sys.argv[2])
sop = "1.2.826.0.1.3680043.10.541.50.1"
ts = UID("1.2.840.10008.1.2.4.102")
meta = Dataset()
meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.77.1.4"
meta.MediaStorageSOPInstanceUID = sop
meta.TransferSyntaxUID = ts
meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
ds = FileDataset(str(out), {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.50"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.50.2"
ds.Modality = "XC"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-MPEG4"
ds.Rows = 64
ds.Columns = 64
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "YBR_PARTIAL_420"
ds.NumberOfFrames = 4
ds.CineRate = 10
ds.FrameTime = 100
ds.LossyImageCompression = "01"
ds.PixelData = encapsulate([mpeg])
try:
    ds.save_as(out, write_like_original=False)
except ValueError:
    dcmwrite(out, ds, implicit_vr=False, little_endian=True, force_encoding=True, overwrite=True)
print("wrote", out)
PY
  rm -rf "$tmp"
fi

# JPEG-XL encapsulated bitstream when cjxl exists (4.7 TransferSyntax includes JPEGXL)
if command -v cjxl >/dev/null; then
  python3 - <<'PY'
from pathlib import Path
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
root = Path("corpus/phantoms")
# 8x8 RGB PPM for cjxl
ppm = root.parent.parent / "tmp-jxl.ppm" if False else Path("/tmp/g0a.ppm")
header = b"P6\n8 8\n255\n"
pixels = bytes((i, 40, 80)[i % 3] for i in range(8 * 8 * 3))
ppm.write_bytes(header + pixels)
print("ppm", ppm)
PY
  cjxl /tmp/g0a.ppm /tmp/g0a.jxl --lossless 2>/dev/null || cjxl /tmp/g0a.ppm /tmp/g0a.jxl
  python3 - <<'PY'
from pathlib import Path
from pydicom.dataset import Dataset, FileDataset
from pydicom.encaps import encapsulate
from pydicom.uid import UID
from pydicom.filewriter import dcmwrite
jxl = Path("/tmp/g0a.jxl").read_bytes()
out = Path("corpus/phantoms/G-P0-codec-jpegxl.dcm")
sop = "1.2.826.0.1.3680043.10.541.49.1"
ts = UID("1.2.840.10008.1.2.4.110")
meta = Dataset()
meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
meta.MediaStorageSOPInstanceUID = sop
meta.TransferSyntaxUID = ts
meta.ImplementationClassUID = "1.2.826.0.1.3680043.10.541"
ds = FileDataset(str(out), {}, file_meta=meta, preamble=b"\0" * 128)
ds.SOPClassUID = meta.MediaStorageSOPClassUID
ds.SOPInstanceUID = sop
ds.StudyInstanceUID = "1.2.826.0.1.3680043.10.541.49"
ds.SeriesInstanceUID = "1.2.826.0.1.3680043.10.541.49.2"
ds.Modality = "SC"
ds.PatientName = "GENESIS^PHANTOM"
ds.PatientID = "G0A-JXL"
ds.Rows = 8
ds.Columns = 8
ds.BitsAllocated = 8
ds.BitsStored = 8
ds.HighBit = 7
ds.PixelRepresentation = 0
ds.SamplesPerPixel = 3
ds.PhotometricInterpretation = "RGB"
ds.PixelData = encapsulate([jxl])
dcmwrite(out, ds, implicit_vr=False, little_endian=True, force_encoding=True, overwrite=True)
print("wrote", out)
PY
else
  echo "cjxl not installed; JPEG-XL cell empty until census-open or tools" >&2
fi

if command -v ojph_compress >/dev/null || [[ -x /tmp/OpenJPH/build/src/apps/ojph_compress/ojph_compress ]]; then
  python3 "$root/scripts/generate-htj2k.py" || echo "generate-htj2k.py failed; committed probe objects still apply" >&2
fi

echo "codec generation finished"
ls -l "$ph"/G-P0-codec-* 2>/dev/null || true
