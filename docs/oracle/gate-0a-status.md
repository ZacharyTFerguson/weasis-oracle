# Gate 0a evidence (this PR)

Checked boxes require a passing named case. **Do not tick the frozen checklist from this list until that is true.**

## Ran in this environment

- `go test ./internal/oracle` — VectorUtils + axial slice position + split golden groups + hash inventory + `TestXMLGraphics_fourSevenWrites` + `TestSortKeyGolden_matchesGoLeaf` + `TestFelix_dicomModelTreeDryRun` (ok on `2e3fddf` and the 015-packet commit)
- `weasis-dump dump sort-key` — six `SortSeriesStack` names + ten signum pairs matching `G-P0-015.json`
- `javap` of 4.7 `SortSeriesStack$1`–`$6` — [sortseriesstack-bytecode.md](sortseriesstack-bytecode.md); Go `doubleCompare` matches `Double.compare` (NaN / `-0.0`)
- `weasis-dump dump slice-position` — `slicePosition` 10
- DCMTK `dcmdump` on synthetic CT phantom
- 4.7 pin recorded from `weasis-parent` + git tag `v4.7.0`
- **Java producer:** `scripts/run-weasis-producer.sh` — slice position, header dump, split-on-files, **DumpMain** schema emit (`G-P0-003.json`) with raw-frame hash, `SplittingRules`/`Rule.isTagValueMatching`, `HiddenSeriesManager.extractReferencedSeries`, `WProperties.color2Hexadecimal`, `Utils.getWeasisProtocolPattern`; **UID probe** `G-P0-051.json`. Dual-run ok. `DicomModel.applySplittingRules` **results** remain Felix (`corpus/goldens/G-P0-000-felix.json`).
- dcm4che header dump two-run `cmp` (`G-P0-049.json`)
- 48-bundle SHA inventory + 114 preference keys from native `conf/*.json` (`docs/oracle/weasis-properties.json`)
- **HTJ2K probe (`G-P0-016`):** `scripts/run-htj2k-probe.sh` — `DicomImageReader.getPlanarImage` opened `.201`/`.202`/`.203`; `docs/oracle/htj2k-probe.md`
- Corpus §0.8 floors filled including GSPS-every-graphic-type (`G-P0-iod-pr-gsps-types.dcm`)
- **XML graphics (`G-P0-017`):** `scripts/run-xml-graphics-probe.sh` — `fourSevenWritesXmlGraphics=true`; `O-P5-008` applies
- User-file inventory (`G-P0-063`), license matrix (`G-P0-103`), M-/waiver/deadline/divergences templates (`G-P0-109`–`113`)
- **Second oracle (`G-P0-052`):** Weasis / pydicom / DCMTK stored pixels agree on `G-P0-phantom-ct-02.dcm`; fused LUT dropped
- **JaCoCo (`G-P0-027a`):** `docs/oracle/jacoco/` initial report + gap list (0b 80% target untouched)
- G-P0-021 modality files present (CT/MR/US/XA/CR/DX/MG/PT/NM/SR/PR/KOS/SEG/RT*/ECG/AU/PMAP/Enhanced/SC)
- Command grammar table from 4.7 `DicomModel` / `ConfigData` (`docs/oracle/command-grammar.md`)

## STOP closed

- Origin [PR 1](https://cursor.com/codebase/zachary-ferguson/genesis/pull/1) **merged** at `2026-09-16T11:17:46Z`. `mergedAt` set. Merge commit `36e5385c04da9edc912de37539a41e22dc7dd170` (message `Gate 0a oracle on main (#1)`). Head `b8f75890b884041f177125185f10a6e70fa0a2c7`.
- Gate 0a STOP “merged via a normal PR” is **false**. Phase 1 is unblocked and **not started**.

## Closed on this PR

- **G-P0-015 vertical dry run:** second-person **Pass** [`g-p0-015-reviewer.md`](g-p0-015-reviewer.md) (signer `bc-f5d7dd6f-4373-5f7a-8b78-72c90d7188a6`); checklist ticked; §5 pasted.
- **4.7 Linux binary census (`G-P0-014` / `G-P0-019` ticked):** method pack [census/README.md](census/README.md); second-person **Sign** [g-p0-019-reviewer.md](census/g-p0-019-reviewer.md) `82cc891`.
- G-P0-006 adversarial harness review **ticked**: residual **pass** at `06d4216` ([harness-review-g-p0-006-reviewer.md](harness-review-g-p0-006-reviewer.md), signer `bc-d8138da6-8157-5a6f-ba12-bf9ae76e5458`).
- G-P0-023 **closed**: `scripts/verify-edge-023.py` passed all 16 named cases including sparse >2 GiB `G-P0-edge-gt2gb.dcm` (not committed; CI generates, verifies, deletes).
