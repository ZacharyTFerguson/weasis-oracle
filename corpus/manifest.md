# Corpus manifest v1 (G-P0-020)

Minima from checklist §0.8. `have` is committed files in this repo.

PHI: synthetic generators only (`scripts/generate-phantom-ct.py`, `generate-corpus-extra.py`, `generate-iods.py`, `generate-codecs.sh`, `generate-dicomdir.py`, `generate-edge-023.py`, `generate-huge-multiframe.py`). PatientName `GENESIS^PHANTOM`, no real PHI (G-P0-026). Hashes: `corpus/hashes.json`.

| Cell | min | have | path / license |
| --- | ---: | ---: | --- |
| Uncompressed CT | 3 | 3 | `G-P0-phantom-ct-01..03.dcm` Apache-2.0 |
| JPEG-LS CT or MR | 2 | 2 | `G-P0-codec-jpegls-01..02.dcm` (DCMTK) |
| JPEG2000 reversible | 2 | 2 | `G-P0-codec-j2k-reversible-01..02.dcm` (GDCM) |
| JPEG2000 irreversible | 2 | 2 | `G-P0-codec-j2k-irreversible-01..02.dcm` (GDCM) |
| HTJ2K | 1 | 3 | `G-P0-probe-htj2k-lossless.dcm` (`.201`), `G-P0-probe-htj2k-lossless-rpcl.dcm` (`.202`), `G-P0-probe-htj2k.dcm` (`.203`); OpenJPH wrap; 4.7 `DicomImageReader` opened all three (`G-P0-016`) |
| JPEG lossless SOF3 | 2 | 2 | `G-P0-codec-jpeg-lossless-01..02.dcm` (DCMTK `+e1`) |
| JPEG baseline US (YBR) | 2 | 2 | `G-P0-codec-jpeg-baseline-us-01..02.dcm` |
| JPEG-XL | 1 | 1 | `G-P0-codec-jpegxl.dcm` (cjxl; 4.7 `TransferSyntax.JPEGXL`) |
| MPEG-2 or MPEG-4 | 1 | 2 | `G-P0-codec-mpeg2.dcm`, `G-P0-codec-mpeg4.dcm` |
| RLE | 1 | 1 | `G-P0-extra-rle.dcm` |
| Deflated EVLE | 1 | 1 | `G-P0-extra-deflate.dcm` |
| Float/double PMAP | 1 | 1 | `G-P0-iod-pmap-float.dcm` |
| Enhanced CT or MR | 2 | 2 | `G-P0-iod-enhanced-ct.dcm`, `G-P0-iod-enhanced-mr.dcm` |
| Gantry-tilt CT | 1 | 1 | `G-P0-extra-gantry-tilt.dcm` |
| PR + referenced series | 2 | 2 | `G-P0-iod-pr.dcm`, `G-P0-iod-pr-2.dcm` (refs phantom CT) |
| KOS | 1 | 1 | `G-P0-iod-kos.dcm` |
| SEG | 1 | 1 | `G-P0-iod-seg.dcm` |
| RTSTRUCT + RTDOSE | 1 | 2 | `G-P0-iod-rtstruct.dcm` (no `(3006,0010)`) + `G-P0-iod-rtstruct-for.dcm` (FOR chain for RT Tool) + `G-P0-iod-rtdose.dcm` |
| RTPLAN | 1 | 1 | `G-P0-iod-rtplan.dcm` |
| SR | 1 | 1 | `G-P0-iod-sr.dcm` |
| ECG | 1 | 1 | `G-P0-iod-ecg.dcm` |
| AU | 1 | 1 | `G-P0-iod-au.dcm` |
| DICOMDIR media set | 1 | 1 | `corpus/phantoms/G-P0-iod-dicomdir/` |
| Charset IR 87 or 149 or GB18030 | 2 | 5 | IR 87, IR 149, GB18030, UTF-8, multi-valued |
| Missing UID / no-BOT / truncated / >2 GB | 5 | 16 named G-P0-023 | extras + `G-P0-edge-*` including raw stream. **>2 GiB multi-frame generated in CI, not committed** (`G-P0-edge-gt2gb.dcm`, gitignored) |
| Explicit VR Big Endian | 1 | 1 | `G-P0-extra-bigendian.dcm` |
| SC (AI path) | 1 | 1 | `G-P0-extra-sc.dcm` |
| MG tomosynthesis multi-frame | 1 | 1 | `G-P0-iod-mg-tomo.dcm` |
| XA cine multi-frame | 1 | 1 | `G-P0-iod-xa.dcm` |
| NM | 1 | 1 | `G-P0-iod-nm.dcm` |
| US multi-frame with region calibration | 1 | 1 | `G-P0-iod-us-region.dcm` |
| CR/DX MONOCHROME1 + VOI LUT sequence | 1 | 2 | `G-P0-iod-cr-mono1.dcm`, `G-P0-iod-dx.dcm` |
| Palette Color | 1 | 1 | `G-P0-iod-palette.dcm` |
| RGB planar configuration 1 | 1 | 1 | `G-P0-iod-rgb-planar1.dcm` |
| GSPS graphic types | 1 | 1 | `G-P0-iod-pr-gsps-types.dcm` — POINT/POLYLINE/INTERPOLATED/CIRCLE/ELLIPSE + MULTILINE/MULTIPOINT/RECTANGLE/RULER/ARROW (`docs/oracle/gsps-graphic-types.md`) |
| JPEG extended sequential | (G-P0-022) | 2 | `G-P0-codec-jpeg-extended-01..02.dcm` |

**§0.8 floors:** GSPS-every-type filled from `PrGraphicUtil` (types Weasis 4.7 **renders**). **HTJ2K decode objects exist** (`G-P0-016`). **G-P0-023** named cases verified (`docs/oracle/edge-023.md`); >2 GiB object is on-demand sparse, not hashed.

**G-P0-021 modalities present as files:** CT, MR, US, XA, CR, DX, MG, PT, NM, SR, PR, KOS, SEG, RTSTRUCT, RTDOSE, RTPLAN, ECG, AU, PMAP, Enhanced, SC.
