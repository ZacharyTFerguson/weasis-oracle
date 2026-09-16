# File → Export DICOM dialog (G-P0-014, unsigned)

Do **not** tick `G-P0-014`. Live GUI from the frozen v4.7.0 AppLauncher (DISPLAY=:1) plus classes in `weasis-dicom-explorer-4.7.0` / `weasis-dicom-codec-4.7.0` / `weasis-dicom-send` / `weasis-dicom-isowriter`. Pin `v4.7.0` / `3b3e46c59879ead782e5c474e895befae616a715`.

Opened by `JButton.doClick` on the toolbar tooltip **Export DICOM** inside the running JVM (XTEST/Robot cannot click while an off-screen **Update** `JOptionPane` is `APPLICATION_MODAL`). Close with the wizard **Close** button.

## GUI (this session)

| Shot | What |
| --- | --- |
| `177-export-dicom.png` / `177b-export-dicom-window.png` | Wizard **Export DICOM**, page **Local Device**, format combo **DICOM**, **Options**, series tree, **Export** / **Export and Close** / **Close** |
| `178-export-dicom-options.png` | Nested **Image Export Options** (Transcoding, JPEG Quality: 85, Include DICOMDIR, …) |
| `179-export-dicom-send.png` / `179b-export-dicom-send-window.png` | Page **DICOM Send**: Destination, Calling Node: Default |
| `180-export-cd-dvd.png` / `180b-export-cd-dvd-window.png` | Page **CD/DVD Image**: Export to DICOM, Options, Add JPEG images, Add Weasis |

Live combo dump: [export-dicom-live-widgets.txt](export-dicom-live-widgets.txt). File → Export submenu remains `139-file-export.png`. Sibling Import DICOM is `122`.

## How 4.7 opens it

- File → Export → DICOM / toolbar tooltip Export DICOM (`weasis.export.dicom` default true).
- `DicomExport` `APPLICATION_MODAL`. OSGi `DicomExportFactory` pages besides Local Device: **DICOM Send** (`SendDicomView`), **CD/DVD Image** (`IsoImageExport`).

## Format combo (live = `LocalExport.Format`)

| Title in 4.7 | Extension |
| --- | --- |
| DICOM | `dcm` |
| DICOM ZIP | `zip` |
| JPEG Lossy | `jpg` |
| JPEG XL | `jxl` |
| PNG | `png` |
| TIFF | `tif` |
| JPEG 2000 | `jp2` |

JPEG XL as an **export** still-image format is 4.7 binary behavior. Not a census-absent strike. Do not tick `G-P0-019` from this file.

## Image Export Options (live)

Transcoding combo (Keep original selected). UIDs as shown by `TransferSyntax.toString()`:

- Keep original transfer syntax
- Explicit VR Little Endian `[1.2.840.10008.1.2.1]`
- JPEG Lossy (8 bits) `[.50]`
- JPEG Lossy (12 bits) `[.51]`
- JPEG Lossless `[.70]`
- JPEG-LS Lossless `[.80]`
- JPEG-LS Lossy (Near-Lossless) `[.81]`
- JPEG 2000 (Lossless Only) `[.90]`
- JPEG 2000 `[.91]`
- JPEG XL Lossless `[1.2.840.10008.1.2.4.110]`
- JPEG XL Recompression `[.111]`
- JPEG XL `[.112]`

Also: Transcode only uncompressed, JPEG Quality: 85, Generate new unique identifiers, Include DICOMDIR (checked), DICOM CD folders, Keep directory names.

HTJ2K (`.201`/`.202`/`.203`) is **not** in this list (`G-P0-016`: decode yes, export enum no).

## Other wizard pages (live)

- **DICOM Send:** Destination (empty combo on this desktop), Calling Node: Default.
- **CD/DVD Image:** format locked to DICOM; **Add JPEG images**; **Add Weasis** (disabled here).
