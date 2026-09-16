# Java tests that already pin behavior (G-P0-002)

From Weasis v4.7.0 source SHA `3b3e46c59879ead782e5c474e895befae616a715` (not executed in this PR’s CI). Paths under `weasis-dicom/` / `weasis-core/`.

| Area | Location |
| --- | --- |
| Decode / TS | `weasis-dicom-codec/.../TransferSyntaxTest.java` |
| Geometry / identity | `VectorUtilsTest`, `ImageOrientationTest`, `GeometryOfSliceTest`, `PatientOrientationTest`, `LocalizerPosterTest`, `DicomMediaUtilsTest` — VectorUtils **ported** to `internal/oracle/geometry_test.go` |
| LUT / display | `ModalityTest`, `ModalityInfoDataTest`, `CornerDisplayTest`, `CornerInfoDataTest` |
| Measurements | `weasis-core/.../ImageRegionStatisticsTest.java` plus graphic `*GraphicTest.java` (line, angle, Cobb, polygon, …) |
| Anonymisation | `AnonymizationProfileTest.java` |
| Sync | `SynchDataTest`, `ViewSynchDataTest`, `SynchEventTest`, `SynchCineEventTest` |
| Sort / split | `SortSeriesStackTest`, `SplittingModalityRulesTest`, `DicomSorterTest` |
| XML graphics | `weasis-core/.../imp/suite/SerializationTest.java` (feeds `G-P0-017`) |
| Charset | `CharsetEncodingTest.java` |
| Auth | **no dedicated 4.7 unit test found** in this SHA (DIMSE/OIDC live in explorer/launcher; not a JUnit pin) |

This inventory is the Gate 0a artifact. Running those tests in CI is not required to tick `G-P0-002`.
