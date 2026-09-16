# MPEG-2 / MPEG-4 on frozen 4.7 (G-P0-014)

This is **4.7 behavior**, not a missing 2D still-frame. Do **not** tick `G-P0-014` / `G-P0-019` from this file.

## What the binary does

`DicomMediaIO.setMimeType` (v4.7.0 `weasis-dicom-codec`): if `hasPixel` and `DicomMetaData.isVideoTransferSyntaxUID()` → mime **`video/dicom`**. Image TS stays `image/dicom`. Series class is **`DicomVideoSeries`**; media is **`DicomVideoElement`**. `DicomVideoSeries.getMimeType()` always returns `video/dicom`.

The only live `SeriesViewerFactory` that accepts `video/dicom` is **`MimeSystemAppFactory`** (`uiName` = **Default System Application**). `View2dFactory.canReadMimeType("video/dicom")` is **false**. Opening a video series extracts PixelData fragments to a temp file (`DicomVideoElement.getExtractFile`) and calls `startAssociatedProgramFromLinux` / Desktop OPEN. `getSeriesViewerUI()` / `getDockableUID()` are **null** — no 2D Viewer tab.

## Live GUI (this AppLauncher, DISPLAY=:1)

Unique-UID copies so explorer rows do not merge with hashed originals:

- `/tmp/census-unique/mpeg2.dcm` — Patient `G0A, MPEG2`, Study ID `MPEG2`, TS `1.2.840.10008.1.2.4.100` (MPEG2 MP@ML), SOP VL Photographic, 64×64, 4 frames
- `/tmp/census-unique/mpeg4.dcm` — Patient `G0A, MPEG4`, Study ID `MPEG4`, TS `1.2.840.10008.1.2.4.102`

Hashed corpus files: `corpus/phantoms/G-P0-codec-mpeg2.dcm`, `G-P0-codec-mpeg4.dcm`.

| Shot | What |
| --- | --- |
| `222-mpeg2-explorer.png` | Explorer combo **G0A, MPEG2**; thumbnail **Video** (filmstrip); **no** MPEG 2D tab (canvas still `G0A, MISS SER`) |
| `223-mpeg4-explorer.png` | Same for **G0A, MPEG4** |
| `234-mpeg-xdg-open.png` | OS handler after OPEN of the MPEG extract: window title **genesis-mpeg-open**, body `xdg-open:` + extract path |

Live dump: [mpeg-explorer-live.txt](mpeg-explorer-live.txt) — `DicomVideoSeries mime=video/dicom` under `G0A, MPEG2` / `G0A, MPEG4`. `ViewerPlugins` list has no MPEG container. Factory row: `MimeSystemAppFactory video/dicom=true`; `View2dFactory video/dicom=false`.

## Default System Application OPEN (hole 2 evidence)

4.7 Linux OPEN is `MimeSystemAppViewer.startAssociatedProgramFromLinux(Path)` on the PixelData extract, then `xdg-open`. This VM had no `video/mpeg` handler until `~/.local/share/applications/genesis-ffplay.desktop` was registered (`MimeType=video/mpeg;…`, `Exec=xmessage … -title genesis-mpeg-open xdg-open:%f`). That desktop file is **census scaffolding**, not a 4.7 bundle.

JVMTI agent `CensusMpegOpenH014` (unique class name) on the live AppLauncher PID:

- classLoader `weasis-core [19]`
- extract `/tmp/weasis-ubuntu.BE65BCAB/cache/video_5114729716266442391.mpg` exists, 2048 bytes (tiny phantom; not a playable movie)
- `startAssociatedProgramFromLinux invoked`

Dump: [mpeg-open-h014.txt](mpeg-open-h014.txt). Screenshot `234-mpeg-xdg-open.png` is that same extract path in a titled **genesis-mpeg-open** xmessage (the Weasis-spawned window used the same `Exec`; the framed PNG is `xdg-open` of the same file after that window’s 40s timeout). This is OPEN-to-OS, **not** in-app play + frame grab (`O-P2-010` stays Phase 2).

Do **not** tick `G-P0-014` / `G-P0-019` from this file.

Load log: [gogo-load-mpeg-unique.txt](gogo-load-mpeg-unique.txt). `LoadDicom` **Adding patient: G0A, MPEG2** / **MPEG4** then End of loading. **No** `DicomMediaIO: Start reading dicom image frame` (that line fires for 2D decode).

Earlier `18-open-mpeg2.png` / `55-open-mpeg4.png` are **mislabeled** (prefs / CT). Do not use them as MPEG evidence.

## README

v4.7.0 README names JPEG / JPEG-LS / JPEG 2000 / JPEG-XL / RLE / Deflate. MPEG is not in that codec sentence. The binary still **loads** MPEG as `video/dicom` and hands it to the OS app. That is presence of a video series, not a 2D raster. Phase 2 MPEG boxes (`O-P2-010` play + frame grab) stay later work.
