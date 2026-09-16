# RT Tool on frozen 4.7 (G-P0-014)

Do **not** tick `G-P0-014` / `G-P0-019` from this file.

`RtDisplayToolFactory` is an `ExtToolFactory` on `View2dContainer` (`rt.tool` = **RT Tool**), not a standalone `SeriesViewerFactory`. Every factory row stays `rt/dicom=false`. The dockable appears on a **CT/MR 2D Viewer** when `RtDisplayTool.isCtLinkedRT` is true.

## How 4.7 links RTSTRUCT to CT

`DicomModel.extractReferencedSeries` is **PR/SEG only**. RT uses `StructureSet.initReferences`:

`(3006,0010) ReferencedFrameOfReferenceSequence` → `(3006,0012) RTReferencedStudySequence` → `(3006,0014) RTReferencedSeriesSequence` → `SeriesInstanceUID`.

That UID is stored in `HiddenSeriesManager.reference2Series` (CT series → RT series). `isCtLinkedRT` then requires `hasHiddenElementsFromSeries(RtSpecialElement)` on those hidden series.

Hashed `corpus/phantoms/G-P0-iod-rtstruct.dcm` **lacks** `(3006,0010)`, so it never populates `reference2Series` and does not grow RT Tool. Hashed `corpus/phantoms/G-P0-iod-rtstruct-for.dcm` **has** that chain (CT series `1.2.826.0.1.3680043.10.541.1.2`). Unique-UID `G0A, RTSTRUCT` (`229`, not in this pack) is a separate patient with no referenced series — ignore it.

Working copy used for GUI: `/tmp/census-unique2/rtstruct-for.dcm` (same FOR chain; FrameOfReferenceUID on that copy was `…1.for`). Dump: [rt-hsm-z014.txt](rt-hsm-z014.txt).

## Live GUI (this AppLauncher, DISPLAY=:1)

`View → Tools` lists Mini Tool / Display / Image Tools / Draw & Measure — **not** RT Tool. Default extended mode is **minimized** (east strip tab only). [rt-dock-af014.txt](rt-dock-af014.txt) `CControl` row `title=RT Tool vis=true mode=dock.mode.minimized`. Tools list on `View2dContainer` does not include `RtDisplayTool` (ExtToolFactory insert); the dockable is still on `CControl`.

JVMTI `CensusRtNormAG014` called `setExtendedMode(NORMALIZED)` on that dockable ([rt-norm-ag014.txt](rt-norm-ag014.txt)). `CensusRtLoadAH014` clicked **Load RT** ([rt-load-ah014.txt](rt-load-ah014.txt)).

| Shot | What |
| --- | --- |
| `237-rt-tool.png` | East-strip tab **RT Tool** on **GENESIS, PHANTOM** 2D (minimized; panel not expanded) |
| `238-rt-tool-panel.png` | Normalized **RT Tool**: **Load RT**, Structures, Plan, Dose: cGy, **Display DVH chart**, Structures / Isodoses tabs, Graphic Opacity 100% |
| `239-rt-tool-loaded.png` | After Load RT: Structures combo **PHANTOM**; tree **Structures → BODY** (checked, green); Load RT disabled |

`weasis-dicom-rt` is **Active** in [felix-lb-live.txt](felix-lb-live.txt). Tiny phantom: no RTDOSE, Plan combo empty, no isodose tree. That is the corpus, not a missing plugin.

Do **not** tick `G-P0-014` / `G-P0-019` from this file.
