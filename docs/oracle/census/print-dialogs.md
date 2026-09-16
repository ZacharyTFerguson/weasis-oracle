# File → Print dialogs (G-P0-014, unsigned)

Do **not** tick `G-P0-014`. Live GUI from the frozen v4.7.0 AppLauncher (DISPLAY=:1, JDK 25 `AppLauncher`) plus classes in `weasis-dicom-explorer-4.7.0` / `weasis-core`. Pin `v4.7.0` / `3b3e46c59879ead782e5c474e895befae616a715`.

File → Print is a `DynamicMenu`: items are filled in `WeasisWin.buildPrintSubMenu` from the selected viewer’s `getPrintActions()` when the popup opens. On 2D Viewer they are **Print 2D viewer layout** (`P`) and **DICOM Print**.

Opened by `JMenuItem.doClick` after `Print.doClick()` populated the submenu. Close with **Cancel** (these dialogs use `ColorLayerUI`; do not `windowclose`).

The startup **Update** `JOptionPane` (`WeasisWin.checkReleaseUpdate`) is `APPLICATION_MODAL`. On this VM its X11 peer was often zero, so XTEST could not dismiss it. Capture of these print dialogs used a relaunch with overlay `weasis.update.release=false`. First-run Update UI remains `01-main.png`.

## GUI (this session)

| Shot | What |
| --- | --- |
| `137-file-print.png` | File → Print flyout: Print 2D viewer layout `P`, DICOM Print |
| `187-dicom-print.png` | `DicomPrintDialog` title **DICOM Print**. Empty printer combo (none configured). Defaults: Medium Type BLUE FILM, Priority LOW, Film Destination MAGAZINE, Copies 1, Film Orientation PORTRAIT, Film Size ID 8INX10IN, Display Format STANDARD\1,1, Magnification Type REPLICATE, Smoothing Type MEDIUM, Border Density BLACK, Trim NO, Empty Image Density BLACK, DPI 100, Calling Node Default. Checkboxes: Print in color off; Print image with annotations on; Print only the selected view off. Buttons Add / Edit / Delete / Print / Cancel plus help `?`. |
| `188-print-2d-layout.png` | `PrintDialog` title **Print 2D viewer layout**. Image position Centralized, Image DPI 150, Print image with annotations on, Print / Cancel. **Print only the selected view** is omitted on a 1-cell layout (`PrintDialog` only adds it when `layoutModel.getCellCount() > 1`). |

Live dumps: [dicom-print-live-widgets.txt](dicom-print-live-widgets.txt), [print-2d-layout-live-widgets.txt](print-2d-layout-live-widgets.txt).

## How 4.7 opens them

- `View2dContainer.getPrintActions()`: `PrintDialog` (“Print 2D viewer layout”) and `DicomPrintDialog` (“DICOM Print”), both `APPLICATION_MODAL`, shown with `ColorLayerUI.showCenterScreen`.
- Film size enum includes 8INX10IN through 14INX17IN, 24CMX24CM / 24CMX30CM, A4, A3 (`DicomPrintDialog.FilmSize`).
- No printer node is required to **open** the dialog; **Print** returns immediately when the printer combo is empty.

Not a census add or strike. Help → **Check for Updates...** (live menu string, `210-help-menu.png`) is separate: 4.7.0 vs `https://nroduit.github.io/en/api/release/api.json` `v4.7.3` (2026-08-25) opened `https://weasis.org/en/getting-started/download-dicom-viewer/` (`211-updates-after-click.png`), not the first-run Yes/No pane.
