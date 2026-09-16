# G-P0-006 adversarial harness residual re-review — pass

**Verdict:** **pass.** The three residuals listed after the `69e43d9` named-follow-up pass are present in sources at Origin draft PR 1 HEAD **`06d4216640270c5f608fc3ddbdddd96cc9322ce2`** (PR version 35, parent `4318bef` landed the previous pass file). I do not see a remaining **STOP-class** residual.

**Do not tick `G-P0-014`, `G-P0-015`, or `G-P0-019`.** Do not start Phase 1. Those boxes are still `[ ]`. This review **passes `G-P0-006` as a signed finding**; I did **not** edit `docs/rewrite-checklist.md` (genesis git **403**). The box is still `[ ]` on this HEAD until a commit with git access ticks it from this file.

**Reviewer:** second person, not the `DumpMain` / `DualRunDriver` author. Author notes at `docs/oracle/harness-review-g-p0-006.md` were **untrusted** (still stale: DualRunDriver `G-P0-053`, empty XML marshal).

**How this tree was read:** `origin pr view 1 --repo zachary-ferguson/genesis` (`headSha` `06d421664027`). File blobs reconstructed from `--json files`. `git ls-remote https://origin.cursor.com/git/zachary-ferguson/genesis.git` still **403**. Intended path `docs/oracle/harness-review-g-p0-006-reviewer.md` therefore lands here.

**Independently executed:** reconstructed `go test ./internal/oracle -skip TestEdge023_allNamedCases` → **ok**. `TestDumpMain_headerTextAndUidRole`, `TestSplitGolden_convolutionKernelGroups`, `TestFelix_applySplittingRulesDump` included. `TestEdge023_allNamedCases` was skipped because PR JSON does not carry binary phantoms. Weasis producer / Felix attach / jar download were **not** re-run.

**Signed:** 2026-09-16. Signature is this residual re-review.

---

## Residuals (verify in sources)

### 1. `SeriesSplitHarness` role vs grouping oracle — **pass** (not STOP)

`oracle/java/SeriesSplitHarness.java` still has the first-fit `similar` loop and still writes a `groups` array. That is no longer the claimed grouping oracle:

- Producer emits `"role": "predicate-snapshot-not-grouping-oracle"` and `"groupingOracle": "corpus/goldens/G-P0-000-felix.json applySplittingRules"`.
- `corpus/goldens/G-P0-000-split.json` (and run1/run2) match those two fields.
- `docs/oracle/dual-run.md`: grouping loop is **not** the split oracle; structural groups/order come from live `LoadDicom` → `DicomModel.applySplittingRules` in the Felix dump. Same file still says reimplementing split/sort as the oracle is a fail.
- `JAVA-TO-GO.md` and `docs/oracle/schema.md` name Felix `applySplittingRules` as the grouping oracle; the split JSON is a predicate snapshot.
- `TestSplitGolden_convolutionKernelGroups` **requires** that `role` string.

`DumpMain.splitSort` is still `Rule.isTagValueMatching(media, media)` with `selfMatchAll: true` on one CT in `G-P0-003.json`. It is labeled `"dicomModelApplySplittingRules": "felix-required"` and is not the grouping oracle.

Non-STOP leftover: the recoder class is still compiled by `scripts/run-weasis-producer.sh` and a test still asserts `len(groups)==2` on that snapshot. Contract is explicit that those groups are not the oracle.

### 2. Fetch hashes zip before unzip; pin file not overwritten on mismatch — **pass**

`scripts/fetch-weasis-4.7-bundles.sh`:

1. SHA-256 of `/tmp/downloads/weasis-native.zip` runs **before** `unzip`.
2. If `docs/oracle/producer-jar-pins.json` already has `files.weasis-native.zip.sha256` and it differs, `SystemExit("pin mismatch before unzip: ...")` — extract never starts.
3. After jars are built, a second Python block compares every hashed name to the existing pin file. On mismatch or missing name it `SystemExit("pin mismatch (pin file not overwritten): ...")` **without** `write_text`.
4. `write_text` runs only when the pin file is absent (`first run`).

A non-empty cached zip is still reused, but it is digested against the committed pin **before** unzip. Claimed `weasis-dicom-tools 5.34.3` is still a `reference.json` string, not a hashed classpath jar — not STOP (producer classpath is the pinned Weasis jars).

### 3. Go `HeaderDump` / `UIDSynthesis` nested fields — **pass**

`internal/oracle/schema.go`:

- `HeaderDump`: `VolatileList`, `Text` (plus existing `projection` / `sha256` / `tags`)
- `UIDSynthesis`: `Role`, `IngestSite`, `RunA`, `RunB`

`TestDumpMain_headerTextAndUidRole` unmarshals `G-P0-003.json` into `Golden` and requires `Header.Text` contains `GENESIS^PHANTOM`, `Header.VolatileList == "docs/oracle/volatile-tags.md"`, `UIDSynthesis.Role == "factory-probe-only"`, and `IngestSite != nil`. That test **passed** in this agent’s reconstructed tree.

---

## STOP-class scan

No remaining STOP for this box:

- Grouping oracle is Felix `applySplittingRules` dump, not the harness recoder.
- Missing Study/Series ingest remains live `UNKNOWN` (prior pass; not reopened).
- Header volatile list + `header.text` round-trip through Go.
- Stored vs decoded pixel APIs remain distinct (prior pass).
- XML probe remains non-empty `writePresentation` (prior pass).
- Zip/jars have SHA-256 pins; fetch verifies zip before extract and does not clobber pins on mismatch.

---

## Pin table (for the §5 “Oracle harness SHA + deps” line)

| Dep | Pin at HEAD `06d4216` | Hash-pinned? |
| --- | --- | --- |
| Weasis tag / commit | `v4.7.0` / `3b3e46c59879ead782e5c474e895befae616a715` | zip SHA in `producer-jar-pins.json` |
| weasis-native.zip | GitHub `v4.7.0` | **yes** `bad1334c0ddfa1f381211879e83d37ae78621f573eab0edaff6e1adc217f4862` |
| weasis-core / weasis-dicom-codec | `4.7.0` | **yes** |
| weasis-core-img | `4.13.0` | **yes** |
| weasis-dicom-tools (claimed) | `5.34.3` in `reference.json` | **no file** |
| Felix | `7.0.5` claimed | installer bundles, not a separate pin file |
| OpenCV native | `4.13.0-dcm` linux-x86-64 | **yes** |
| slf4j 2.0.17 / flatlaf 3.7.1 / jaxb-osgi 4.0.3 / joml 1.10.8 / launcher | as in pin JSON | **yes** |
| Producer JDK | Temurin 25; golden `25.0.4.1+1-LTS` | CI image |
| Go | `1.22` | `go.mod` / `gate0a.yml` |
| Schema | `genesis.oracle.v1` | n/a |

§5 template in the checklist is still blank placeholders. That is phase-exit paste, not a harness STOP. Pins for this review are the table above plus `docs/oracle/producer-jar-pins.json`.

---

## Checklist

`G-P0-014` / `G-P0-015` / `G-P0-019` remain `[ ]` — do not tick. Do not start Phase 1.

`G-P0-006` is a **signed pass** in this file. It is still `[ ]` on HEAD `06d4216` because this agent could not commit. Copy this document to `docs/oracle/harness-review-g-p0-006-reviewer.md` and tick `G-P0-006` when genesis git works.

Coordinator copy: this file was copied unchanged (YAML store frontmatter stripped) onto `cursor/gate-0a-oracle-ed7a` from `/cursor/stores/bc-051498ed-27f1-4109-9e4a-1e51af4eed7a/internal/harness-review-g-p0-006-reviewer.md`. Review HEAD is `06d4216`. Later commit `82a47da` only refreshed the unsigned §5 draft. `G-P0-006` is ticked from this signed pass. `G-P0-014` / `G-P0-019` / `G-P0-015` stay `[ ]`.
