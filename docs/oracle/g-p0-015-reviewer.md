# G-P0-015 second-person review (not the leaf author)

**Verdict: Pass** of the vertical dry-run leaf.

**Role:** adversarial reviewer of the sort-key + Felix-tree dry-run chain. Not the author of `oracle/java/SortKeyHarness.java`, `internal/oracle/sortkey.go`, `cmd/weasis-dump` `dump sort-key`, or `docs/oracle/g-p0-015.md`.

**HEAD reviewed (leaf):** `2dbc4afed85a17a53ab1d23d10a84dc34f37a14f` on `cursor/gate-0a-oracle-ed7a` (Origin draft PR https://cursor.com/codebase/zachary-ferguson/genesis/pull/1). Sort-key sources landed at `97b8460` / `69e43d9`; unsigned author packet at `2647d0e`; `2dbc4af` ports `Double.compare` / clock-only `LocalTime`. This reviewer file is a later commit on the same branch.

**Signer:** `bc-f5d7dd6f-4373-5f7a-8b78-72c90d7188a6`

**This file does not tick `G-P0-015`.** It does not fill checklist §5 as signed. It does not merge. Phase 1 is not started. The box stays `[ ]` for the coordinator after a §5 paste.

Git `user.name` on this VM is also `Cursor Agent`; identity for this review is the signer id above.

**Untrusted:** `docs/oracle/g-p0-015.md` and `docs/oracle/sortseriesstack-bytecode.md` (author notes). Inverse Stack / `getValues()` / `Double.compare` were re-checked against frozen Weasis + OpenJDK `Double.compare`, not taken from those files.

Frozen pin independently confirmed from `docs/oracle/reference.json`: tag `v4.7.0` SHA `3b3e46c59879ead782e5c474e895befae616a715`.

---

## Required chain (independently checked)

| Step | Artifact | Result |
| --- | --- | --- |
| Harness golden | `corpus/goldens/G-P0-015.json` (`SortKeyHarness` / `SortSeriesStack`) | **Pass** |
| Mapping-guide | `JAVA-TO-GO.md` five `SortSeriesStack.*` → `oracle.Cmp*` rows | **Pass** |
| Go port | `internal/oracle/sortkey.go` (`CmpInstanceNumber`, `CmpSlicePosition`, `CmpSliceLocation`, `CmpLocalTime`, `CmpDiffusionBValue`) | **Pass** |
| Tests bound to the case | `weasis-dump dump sort-key` + `TestSortKeyGolden_matchesGoLeaf` + `TestFelix_dicomModelTreeDryRun` | **Pass** |
| Inverse Stack | 2D reverse flag, not a seventh comparator | **Pass** |

Code lives in `internal/oracle` (and the Gate 0a `weasis-dump` emitter). This is process validation of the last 0a leaf, not a Spike A–D throwaway tree and not Phase 1 identity/ingest/`dump file`.

---

## What I checked

### 1. Harness golden calls Weasis (six comparators)

`oracle/java/SortKeyHarness.java` sets `Locale.ROOT`, reads `SortSeriesStack.getValues()` for names, and compares stub `DicomImageElement`s with the Weasis fields (`instanceNumber`, `slicePosition` via `TagW.SlicePosition`, `sliceLocation`, `contentTime`, `acquisitionTime`, `diffusionBValue`). It does not reimplement sort. `DicomMediaIO` is avoided. Pair `cmp` values are `Integer.signum(...)`.

Independent fetch of frozen `SortSeriesStack.java` at SHA `3b3e46c59879ead782e5c474e895befae616a715`:

`getValues()` order is exactly `instanceNumber`, `slicePosition`, `sliceLocation`, `contentTime`, `acquisitionTime`, `diffusionBValue` (six). Every comparator uses `if (val1 == null || val2 == null) return 0`.

English `toString()` keys from frozen `weasis-dicom-codec/.../messages.properties`:

| Message key | English |
| --- | --- |
| `SortSeriesStack.inst` | Instance Number |
| `SortSeriesStack.pos_orient` | Anatomical Direction |
| `SortSeriesStack.location` | Slice Location |
| `SortSeriesStack.content_time` | Content Time |
| `SortSeriesStack.time` | Acquisition Time |
| `SortSeriesStack.dvalue` | Diffusion b-value |

That matches golden `sortKey.comparators` and Go `SortKeyNames`.

Golden header: `caseId` `G-P0-015`, class `ST`, `schemaVersion` `genesis.oracle.v1`, `api` `org.weasis.dicom.codec.SortSeriesStack`, `producer` `weasis-library`, pin SHA matches `reference.json`. Ten pairs; signs match `Integer.signum` of the Weasis compares for the harness inputs (including `instanceNumber_null_left` / `slicePosition_null_left` = 0).

`G-P0-015.json` / `-run1.json` / `-run2.json` are byte-identical. SHA-256 `1883d029a3187452c1eae5e1c4bb308662a0149fb6194e28334101707aaa9483` (1422 bytes) matches `corpus/hashes.json`. Producer script `scripts/run-weasis-producer.sh` dual-runs `SortKeyHarness` and `cmp`s the two dumps.

Live census flyout `docs/oracle/census/2dviewer-sortstack-live.txt` lists the same six names, then `SEP`, then Inverse Stack — consistent with the menu construction below, not with a seventh `getValues()` entry.

I did **not** recompile `SortKeyHarness` (no producer jars in this tree). The Pass for “calls Weasis” is the harness source + frozen `SortSeriesStack` + committed dual-run identity.

### 2. Mapping-guide rows

`JAVA-TO-GO.md` maps:

- `SortSeriesStack.instanceNumber` → `oracle.CmpInstanceNumber`
- `slicePosition` (“Anatomical Direction”) → `oracle.CmpSlicePosition` (`TagW.SlicePosition`)
- `sliceLocation` → `oracle.CmpSliceLocation`
- `contentTime` / `acquisitionTime` → `oracle.CmpLocalTime`
- `diffusionBValue` → `oracle.CmpDiffusionBValue`

Rules paragraph: goldens from Weasis; Go is the consumer; Inverse Stack is a reverse flag; `TestFelix_dicomModelTreeDryRun` is the second structural dry run; merge + second-person + §5 still required before ticking. NOTICE names the six comparators as Apache-2.0 derived leaf algorithms and states Inverse Stack is not a seventh comparator.

### 3. Go port

`internal/oracle/sortkey.go`: `SortKeyNames` is the six English `getValues()` names (no Inverse Stack). `cmpNilEither` copies the 4.7 null-or-null → 0 rule. `Signum` matches harness `Integer.signum`. `doubleCompare` follows the `<` / `>` then bit-pattern tail of `java.lang.Double.compare` (OpenJDK: NaN greater than numbers; `-0.0` < `+0.0`). `CmpLocalTime` uses clock nanos only (`time.Time.Clock` + nanosecond), matching `LocalTime.compareTo` date-independence. `CmpSliceLocation` and `CmpDiffusionBValue` still alias `CmpSlicePosition` (`Double.compareTo` → `Double.compare`). Inner-class numbers `$1`–`$6` match declaration order in frozen `SortSeriesStack.java`; `getValues()` still lists contentTime (`$5`) before acquisitionTime (`$4`).

### 4. Tests bound to the case

- `TestSortKeyGolden_matchesGoLeaf` reads `corpus/goldens/G-P0-015.json`, requires case id `G-P0-015`, class `ST`, API `SortSeriesStack`, six names equal to `SortKeyNames`, and all ten pair ids/signs equal to the Go `Cmp*` on the same harness inputs.
- `cmd/weasis-dump` `dump sort-key` emits the same case id, API, six names, and ten signum pairs via those `Cmp*` functions (full file dump remains `O-P1-023`). Independently executed: `go run ./cmd/weasis-dump dump sort-key` — comparators and pair `cmp` values match the golden.
- `TestFelix_dicomModelTreeDryRun` is the second structural dry run (G-P0-000 concluded Felix-boot for `DicomModel` attach). It consumes `corpus/goldens/G-P0-000-felix.json` (`producer` `felix-live-attach`): OpeningViewer `NONE` / `ALL_PATIENTS` only; explorer mimeTypes `series/dicom`, `pr/dicom`, `ko/dicom`, `seg/dicom`, `sr/dicom`; HSM `KOSpecialElement` / `PRSpecialElement` / `SegSpecialElement` with `series2ElementsCount` ≥ 3. Independently confirmed those fields exist in the Felix golden.

Independently executed on leaf `2dbc4af`: `go test ./internal/oracle` — **ok**. Targeted `TestSortKeyGolden_matchesGoLeaf` / `TestFelix_dicomModelTreeDryRun` / `TestCmp*` / `TestDoubleCompare_matchesJava` / `TestCmpLocalTime_clockOnly` — **ok**.

### 5. Inverse Stack is a reverse flag, not a seventh comparator

Independent v4.7.0 source (same pin), not author prose:

- `SortSeriesStack.getValues()` does not include Inverse Stack.
- `ActionW.INVERSE_STACK` is a `ToggleButtonListenerValue` (`cmd` `inverseStack`), separate from `ActionW.SORT_STACK` (`ComboItemListenerValue` over `SortSeriesStack.getValues()`).
- `ImageViewerEventManager.newInverseStackAction()` is a boolean toggle (default false) that fires `SynchEvent` with the selected flag.
- `EventManager.getSortStackMenu` builds a radio menu from `SORT_STACK`, then `menu.add(new JSeparator())`, then a checkbox `View2dContainer.inv_stack` = **Inverse Stack**.
- `DefaultView2d.getCurrentSortComparator()`: `return (reverse != null && reverse) ? sort.getReversOrderComparator() : sort`.
- `SeriesComparator.getReversOrderComparator()` is `Collections.reverseOrder(this)`.

That is a 2D reverse flag on the selected comparator. Go `SortKeyNames` correctly has six entries.

---

## Nits (not STOP / not Fail)

1. No `cmd/weasis-dump` `_test.go`. The CLI is the specified Go dump path; `TestSortKeyGolden_matchesGoLeaf` binds the same `Cmp*` the CLI calls. I ran the CLI myself.
2. `doubleCompare` uses `math.Float64bits` (`doubleToRawLongBits`). OpenJDK `Double.compare` uses `doubleToLongBits` and says it cannot use raw bits because of NaNs (canonical quiet NaN `0x7ff8000000000000L`). Distinct NaN payloads can disagree; `math.NaN()` vs finite and `-0` vs `+0` match Java. Golden pairs are finite. Not STOP.
3. `weasis-dump dump sort-key` omits Java `producer` / `platform` (Go emitter, not the harness). Pair signs still match.
4. Did not re-run the Java producer (jars absent). Dual-run goldens are already byte-identical in-tree. Author `javap` notes were not treated as evidence.

---

## What this Pass does **not** do

- Tick `G-P0-015` on `docs/rewrite-checklist.md` (still `[ ]`).
- Fill or sign checklist §5 (`docs/oracle/gate-0a-signoff-draft.md` remains **unsigned**; `Signed: ____`; G-P0-015 reviewer line still pending until the coordinator pastes).
- Merge Origin PR 1 (status **draft**; mergeability blocked by `change-is-draft`).
- Start Phase 1.

Coordinator: after this Pass, paste §5, then tick `G-P0-015` only when the leaf is **merged via a normal PR into `internal/`**.
