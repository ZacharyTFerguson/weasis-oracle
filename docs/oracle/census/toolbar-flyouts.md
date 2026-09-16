# Toolbar dialogs and flyouts (G-P0-014, unsigned)

Do **not** tick `G-P0-014`. Live GUI from the frozen v4.7.0 AppLauncher (DISPLAY=:1, JDK 25). Pin `v4.7.0` / `3b3e46c59879ead782e5c474e895befae616a715`. Opened with `AbstractButton.doClick` on toolbar tooltips inside the running JVM.

## DICOM Information (`JFrame`, not modal)

Toolbar tooltip **Open DICOM Information**. Two tabs:

| Shot | What |
| --- | --- |
| `189-dicom-information.png` | **Limited DICOM attributes**: Search; Patient / Station / Study / Series / DICOM Object groups. Phantom: PatientName `GENESIS, PHANTOM`, PatientID `G0A-001`, Manufacturer `GenesisOracle`, Modality `CT`, TS `1.2.840.10008.1.2.1`. |
| `190-dicom-information-all.png` | **All DICOM attributes**: table Tag ID / VR / Tag Name / Value (FileMetaInformationVersion through InstanceNumber on this object). |

Closed with `Window.dispose` (this frame is not `ColorLayerUI`).

## Toolbar flyouts

| Shot | Tooltip | Live items |
| --- | --- | --- |
| `191-measure-tools.png` | Measurement tools | Selection, Line `D`, Polyline, Rectangle, Ellipse, Three Points Circle, Polygon `Y`, Perpendicular, Parallel, Angle `A`, Open Angle, Four Points Angle, Cobb's Angle, Pixel info |
| `192-drawing-tools.png` | Drawing Tools | Selection, Line, Polyline, Rectangle, Ellipse, Three Points Circle, Polygon, Annotation `B` |
| `193-layout-picker.png` | Define a layout in the selected window | 1x1, 1x2, 2x1, **DICOM dump**, **Image Histogram**, 1x3, 3 views (right merged), 3 views (top merged), 1x4, 2x2, 2x3, 2x4 |
| `194-synchronize.png` | Synchronize several series | Default Stack, Default Tile, Synchronize all views (**disabled** on this one-view layout), then Series Scroll (checked), Pan, Zoom, Rotation, Flip, Window/Level, Spatial Unit |
| `195-zoom-type.png` | Select a zoom type | Actual pixel size, Resize to best fit (same two items as 2D Viewer Zoom `144`; real-world size omitted) |
| `197-mouse-action.png` | Change the mouse action `[ctrl-space]` | Pan `T`, Window/Level `W`, Series Scroll `S`, Zoom `Z`, Rotation `R`, Measure `M`, Draw `G`, Context Menu `Q`, Crosshair `H`, No Action `N` |

## Layout views (not just the picker)

| Shot | Layout item | What |
| --- | --- | --- |
| `200-image-histogram.png` | Image Histogram | Image + **Histogram Parameters** (Channel: Luminance (Gray), Bins: 256, Statistics) and **Gray Histogram [HU]** with Accumulate / Logarithmic / Show intensity color / Reset |
| `201-dicom-dump-layout.png` | DICOM dump | Image + docked Limited/All DICOM attributes (same content family as floating `189`, as a layout pane rather than a `JFrame`) |
| `207-histogram-stats.png` | Image Histogram → **Statistics** | Modal `JOptionPane` title Statistics: Parameter / Value table Pixels [pix], Min/Max/Median/Mean [HU], StDev, Skewness, Kurtosis, Entropy. Closed with OK. |
| `208-3d-viewer.png` | Open the series in the 3D viewer | Modal **Opengl Error**: “Volume Rendering requires OpenGL capabilities”; **Check in preferences**; **OK**. No 3D tab. Same capability miss as prefs `36`. |
| `209-ko-selection.png` | KO Selection | After leaving `MipView` (`no.ko=true` disables KO). Combo items: **None**, **[11]** (KO document for this patient/series). Toggle Key Image stays off until a KO is chosen. |

## Oblique MPR (needs ≥5 images)

`DicomSeries.isSuitableFor3d()` / `DefaultView2d.MINIMAL_IMAGES_FOR_3D = 5`. A one- or two-frame CT leaves **Build oblique MPR** registered but a no-op. After gogo-loading throwaway slices 4–6 of `G-P0-phantom-ct` (same Study/Series UID, not committed), `doClick` on tooltip **Build oblique MPR from the selected view** opened a second tab.

| Shot | What |
| --- | --- |
| `202-mpr.png` | Oblique MPR 3-pane: **MPR AXIAL** / **MPR CORONAL** / **MPR SAGITTAL**, crosshairs, Frame (2\|1\|1) / (2\|1\|1) / (2\|1\|1), series G0A-001. Menubar is File / View / **Oblique MPR** / Help. Live dump: [oblique-mpr-menu.txt](oblique-mpr-menu.txt) — Preset, LUT Shape, LUT, Invert LUT, Filter, Zoom, Orientation, Reset (no Cine / Sort Stack / Open in new tab). |
| `203-mip-menu.png` | Toolbar **Build MIP from the selected view** while an MPR pane is selected. `Basic3DToolBar.getMipAction` calls `MprView.showMprPopup`, not 2D `MipMenu`. Live items: **Center** `Alt+X`, **Show center of crosshair** `Alt+C` (checked), **Show crosshair** `Alt+V` (checked), **MIP thickness**, **Build a new series from the current view**, **Synchronize**, **All views**. |
| `213-mpr-mip-thickness.png` | Nested **MIP thickness**: 1 (3 mm) … 20 (41 mm) using `(i*2+1)*minPixelRatio`, plus **Reset thickness** and **Custom thickness**. Mm values differ from 2D `MipMenu` (`206` uses slice spacing). |
| `214-mpr-custom-thickness.png` | MPR `buildMipThicknessMenu` Custom thickness: **Image Extension:** spinner `1`, conversion **1 pix = 3 mm**, OK / Cancel. Spinner max = volume slice size. Closed with Cancel. |
| `215-mpr-all-views.png` | **All views** submenu: Center `Ctrl+Alt+X`, Show center of crosshair `Ctrl+Alt+C`, Show crosshair `Ctrl+Alt+V` (checked), MIP type, MIP thickness, **Build three series from MPR views**, **Change MPR preferences**. |
| `216-mpr-mip-type.png` | All views → **MIP type**: None / Min / Mean / Max (None selected). |
| `218-mpr-synchronize.png` | MPR MIP **Synchronize**: Series Scroll (checked), Pan, Zoom, Rotation, Flip, Window/Level, Spatial Unit, **Apply to all views**, **Close**. Extra vs 2D toolbar synch `194`. |

2D `MipMenu` (`Basic3DToolBar.getMipAction` when the selected canvas is **not** `MprView`):

| Shot | What |
| --- | --- |
| `204-mip-2d-menu.png` | Projection **None / Min / Mean / Max**; MIP thickness and **Build a new Series** disabled on None. |
| `205-mip-2d-max.png` | Max selected; thickness + rebuild enabled; overlay Thickness 31 mm. |
| `206-mip-2d-thickness.png` | Thickness flyout: 1/2/3/5/7/10/15/20 (mm labels) + **Custom thickness**. 2 selected (55 mm). |
| `212-mip-custom-thickness.png` | `MipMenu.showCustomThicknessDialog`: title **Custom thickness**, **Image Extension:** spinner `2` = 55 mm, OK / Cancel. Spinner range 1..`max(series.size/2, 1)` = 3 on this 6-slice stack. Closed with Cancel. [mip-custom-thickness-live.txt](mip-custom-thickness-live.txt) |

Live dump: [mip-2d-live.txt](mip-2d-live.txt). 3D viewer OpenGL path is the Opengl Error dialog `208` (no volume tab on this VM; prefs `36` is the same capability miss). **KO Selection** after a referenced KO: `209` (None / [11]).
