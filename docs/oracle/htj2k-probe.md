# G-P0-016 HTJ2K probe (Weasis 4.7)

Contract of record is the **4.7 decode path**, not README folklore.

## How

1. Encode PHI-free 16×16 MONOCHROME2 phantoms with [OpenJPH](https://github.com/aous72/OpenJPH) `ojph_compress` (BSD-2-Clause; not shipped in this repo).
2. Wrap the JPEG 2000 **codestream** (`FF4F` SOC) in DICOM:
   - `1.2.840.10008.1.2.4.201` lossless LRCP — `corpus/phantoms/G-P0-probe-htj2k-lossless.dcm`
   - `1.2.840.10008.1.2.4.202` lossless RPCL — `corpus/phantoms/G-P0-probe-htj2k-lossless-rpcl.dcm`
   - `1.2.840.10008.1.2.4.203` lossy — `corpus/phantoms/G-P0-probe-htj2k.dcm`
   UIDs are `org.dcm4che3.data.UID` in `weasis-dicom-codec-4.7.0`.
3. Feed those files to `org.dcm4che3.img.DicomImageReader.getPlanarImage`, the same call `DicomMediaIO.getImageFragment` uses in 4.7. Native `libopencv_java.so` comes from the frozen `weasis-opencv-core-linux-x86-64-4.13.0-dcm` bundle (OSGi extracts it; the harness `System.load`s it).
4. Control: JPEG 2000 lossless `.90` (`G-P0-codec-j2k-reversible-01.dcm`) must open first so a native-load failure is not mistaken for an HTJ2K rejection.

Commands: `python3 scripts/generate-htj2k.py` then `bash scripts/run-htj2k-probe.sh`. Golden: `corpus/goldens/G-P0-016.json`.

This is **not** a GUI screenshot. `DicomMediaIO` construction still needs Felix (`GuiUtils.getUICore`). `setMimeType()` does **not** call `DicomImageReader.isSupportedSyntax`; pixel presence is enough for `IMAGE_MIMETYPE`. Export/transcode *does* consult `isSupportedSyntax`.

## Result (this environment)

| Check | Result |
| --- | --- |
| OpenCV native loaded | yes (`4.13.0-dcm`) |
| J2K `.90` control `getPlanarImage` | **opened** 16×16 |
| HTJ2K `.201` / `.202` / `.203` `getPlanarImage` | **opened** 16×16 each |
| `Imgcodecs.imdecode` of the fragment | **opened** (same sizes) |
| `DicomImageReader.isSupportedSyntax` HTJ2K | **false** |
| `DicomOutputData.isSupportedSyntax` HTJ2K | **false** |
| `TransferSyntaxType.forUID` HTJ2K | `JPEG_2000` |
| Weasis `TransferSyntax` enum | JPEG-XL yes, **no HTJ2K** |
| NativeOpenCVCodec MIME list | jp2/j2k/jxl; **no jph/htj2k** |

**Verdict:** 4.7 **does decode HTJ2K pixels** through the frozen OpenCV native. It does **not** advertise HTJ2K in the export TransferSyntax list, and `isSupportedSyntax` will not treat HTJ2K as a supported transcode source/target.

`G-P0-022` may count HTJ2K as a present transfer syntax for decode. Do not claim export-UI parity. GUI “open one object per TS” screenshots remain `G-P0-014`.

## Not this probe

- JPIP HTJ2K referenced (`.204` / `.205`)
- Signed 16-bit HTJ2K / Enhanced HTJ2K (`O-P2-006`)
- DCMTK `dcmj2pnm` as a second oracle (likely no HTJ2K)
