# Java oracle producer (G-P0-003)

1. `scripts/fetch-weasis-4.7-bundles.sh`
2. Decompress the xz bundles listed in the script into `oracle/java/lib/` (not committed).
3. `scripts/run-weasis-producer.sh` compiles:
   - `SlicePositionHarness` — `DicomMediaUtils.computeSlicePosition`
   - `HeaderDump` — dcm4che canonical-minus-volatile
   - `DumpMain` / `DualRunDriver` — full G-P0-003 emit + UID probe (`G-P0-051`) + two-run strip
4. `DicomMediaIO` file import is **not** used: it calls `GuiUtils.getUICore()` (Felix). Reimplementation of split tag lists is a fail; calling `Rule.isTagValueMatching` is the library path. `DumpMain` also calls `HiddenSeriesManager.extractReferencedSeries`, `WProperties.getBooleanProperty`, and launcher `Utils.getWeasisProtocolPattern` (`weasis-launcher.jar` on the producer CP).
5. `Htj2kProbe` (`scripts/run-htj2k-probe.sh`) — `DicomImageReader.getPlanarImage` on HTJ2K objects (`G-P0-016`). Extracts `libopencv_java.so` from the native jar.

`SlicePositionProbe.java` exits 2 without `WEASIS_BUNDLES` so CI does not fake a pass.

`FelixLiveDump.java` + `scripts/run-felix-live-dump.sh` attaches into a running 4.7 `AppLauncher` (full JDK; installer JRE has no `libinstrument.so`) and writes `corpus/goldens/G-P0-000-felix.json`.

Determinism (G-P0-053): run the real dumper twice; `cmp` the JSON.
