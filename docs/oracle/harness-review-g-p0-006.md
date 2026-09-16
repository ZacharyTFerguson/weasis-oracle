# G-P0-006 harness review — unsigned

**Status:** author notes only (stale in places; ignored by the reviewer). Second-person residual re-review is a **pass** at HEAD `06d4216` — [harness-review-g-p0-006-reviewer.md](harness-review-g-p0-006-reviewer.md) (signer `bc-d8138da6-8157-5a6f-ba12-bf9ae76e5458`). Checklist **`G-P0-006` is ticked** from that file. `G-P0-014` / `G-P0-019` are ticked from [`census/g-p0-019-reviewer.md`](census/g-p0-019-reviewer.md). **`G-P0-015` stays open.**

## What was reviewed (this checkout)

`oracle/java/DumpMain.java`, `DualRunDriver.java`, `SeriesSplitHarness.java`, `SortKeyHarness.java`, `CanonicalHeader.java`, `XmlGraphicsProbe.java`, `scripts/run-weasis-producer.sh`, `scripts/run-xml-graphics-probe.sh`, goldens `G-P0-003.json`, `G-P0-000-felix.json`, `G-P0-015.json`, `G-P0-017.json`, `G-P0-052.json`.

## Findings (for the actual reviewer)

1. Java producer builds JSON by string concat (`Json.esc`), not a shared schema serializer. Go `internal/oracle.Golden` does not require every DumpMain field.
2. `DualRunDriver` writes `caseId` `G-P0-053` then CI copies the file to `G-P0-003.json`. Confusing but dual-run strip of `uidSynthesis.runA/runB` is real.
3. `HiddenSeriesManager` is `new` in-process, not the Felix singleton. Attachment goldens from DumpMain are library extract, not `DicomModel` attach. Felix tree is `G-P0-000-felix.json`.
4. `WProperties()` is not constructed (needs OSGi). Property JSON mixes `color2Hexadecimal` with hardcoded Felix dump keys.
5. `DicomModel.applySplittingRules` is still Felix-only. Library path is `Rule.isTagValueMatching` + `SplittingRules`.
6. `XmlGraphicsProbe` marshals an empty `XmlGraphicModel` via JAXB, not `writePresentation(ImageElement, File)` (that path skips empty models). `<presentation` in the XML is still the 4.7 write stack.
7. JaCoCo 0.8.12 cannot instrument Java 25 Weasis classes; `scripts/run-jacoco-0a.sh` covers only our `--release 21` mains. Not `DicomMediaIO` (that is `G-P0-027` in 0b).
8. Second oracle (`G-P0-052`) is stored pixels on one uncompressed CT. Fused LUT dropped. Lossy `dcmdjpeg` not run.

## Deps to pin in §5 (when signed)

| Dep | Pin |
| --- | --- |
| Weasis | v4.7.0 / `3b3e46c59879ead782e5c474e895befae616a715` |
| weasis-core-img | 4.13.0 |
| weasis-dicom-tools | 5.34.3 |
| Felix | 7.0.5 |
| OpenCV native | 4.13.0-dcm |
| JDK for producer | 25 (CI Temurin 25) |
| Go | 1.22 in `gate0a.yml` |
| Golden schema | `genesis.oracle.v1` |

Signer: ____ (not the author)
