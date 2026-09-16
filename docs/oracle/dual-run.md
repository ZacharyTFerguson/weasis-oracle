# Dual-run driver (G-P0-004)

**Decision:** Gate 0a uses a **headless Java harness** that loads Weasis 4.7 `weasis-dicom-codec` / `weasis-core` classes as a library for structural goldens when that is proven (`G-P0-000`).

Proven library calls: `DicomMediaUtils.computeSlicePosition`, `SplittingRules` construction, `Rule.isTagValueMatching` on dcm4che-read tags.

**Not library-callable without Felix:** `DicomMediaIO` file import (`PatientComparator` → `GuiUtils.getUICore()`), `DicomModel.applySplittingRules`, hanging-protocol `OpeningViewer` persistence, special-element attachment in explorer.

`SeriesSplitHarness` grouping loop is **not** the split oracle (`G-P0-006`). `corpus/goldens/G-P0-000-split.json` is a predicate snapshot (`role` = `predicate-snapshot-not-grouping-oracle`). Structural groups and order come from live `LoadDicom` → `DicomModel.applySplittingRules` in `corpus/goldens/G-P0-000-felix.json`.

If those remaining 0a emissions are required, the driver is a **Felix + dumper bundle** from the same native distro, not Swing automation.

Swing UI automation is deferred to 0b view-state (`G-P0-005`) if Felix dump cannot emit it.

Reimplementing split/sort inside the harness is a **fail**.
