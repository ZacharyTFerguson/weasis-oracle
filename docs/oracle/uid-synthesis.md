# UID synthesis determinism (G-P0-051)

Weasis ingest of **missing Series/Study UIDs does not call** `UIDUtils.createUID()`.

| Site | What happens |
| --- | --- |
| `DicomMediaIO.writeInstanceTags` | Missing SOP Instance UID → `header.getString(SOPInstanceUID, String.valueOf(instNb))` (instance number string) |
| `LoadDicom.buildDicomStructure` | Study UID = `TagD.getUID(Level.STUDY)`; Series UID = `Tag.SeriesInstanceUID` **as-is**. Live explorer after loading `G-P0-extra-missing-*.dcm`: missing Study or Series UID becomes the string **`UNKNOWN`**, not `createUID()` |
| `UIDUtils.createUID()` | Used for KO write (`DicomMediaUtils.createDicomKeyObject`), empty DICOMDIR (`DicomDirLoader.open`), export/print/PR serializers — not missing-UID ingest |
| `UIDUtils.createUIDIfNull` | Exists on dcm4che; **no** `org.weasis` caller in `weasis-dicom-codec` / `weasis-dicom-explorer` 4.7.0 jars |

## Factory probe (class for `O-P1-011`)

`DumpMain` still calls `UIDUtils.createUID()` twice in one JVM so the **factory** is shown non-deterministic → `O-P1-011` class **`ST`**. That is not an ingest golden. Evidence: `corpus/goldens/G-P0-051.json` plus `ingestSite` on `G-P0-003.json`. Live explorer nodes after loading `G-P0-extra-missing-*.dcm` are in the Felix dump `uidIngest`.

Dual-run of `DumpMain` uses `caseId` `G-P0-003` and strips `uidSynthesis.runA/runB` before `cmp` (`G-P0-053`).
