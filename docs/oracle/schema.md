# Golden schema `genesis.oracle.v1` (G-P0-010)

Java and Go validate the same JSON object (`internal/oracle.Golden`).

| Field | 0a required | Notes |
| --- | --- | --- |
| `schemaVersion` | yes | `genesis.oracle.v1` |
| `caseId` | yes | `O-*` / `G-*` / `M-*` |
| `class` | yes | BE / BN / ST / BH / PX / AN / PR |
| `reference` | yes | `docs/oracle/reference.json` pin |
| `platform` | yes | OS × arch × JDK/Go (G-P0-011) |
| `header` | when header case | canonical-minus-volatile (G-P0-049); Go keeps `text` + `volatileList` |
| `rawFrame` | when decode case | decoded typed buffer before Modality LUT (`DicomImageReader.getPlanarImage`) |
| `storedPixelData` | when pixel case | SHA of stored `PixelData` bulk |
| `sortKey` | G-P0-015 dry-run leaf | `SortSeriesStack` comparator names + signum pairs |
| `splitSort` / `specialElementAttachment` / `weasisUriParse` / `localPropertyResolution` | DumpMain extras | Go `Golden` keeps these as `any`; Felix `applySplittingRules` is the grouping oracle |
| LUT / view-state | **no** (0b) | G-P0-018 |

## Regeneration (G-P0-011)

A harness change regenerates all goldens. The PR must explain each changed `caseId` vs the previous set. Lossy goldens are valid only for the stamped native codec build.

## Go dump (G-P0-012)

Specified command:

```text
weasis-dump dump slice-position --iop ... --ipp ... --case-id O-P1-015
weasis-dump dump sort-key          # G-P0-015 SortSeriesStack leaf
weasis-dump dump file <path.dcm>   # O-P1-023, not this gate
```

Class-aware comparator prints `class / bar / observed`. Full file dump is Phase 1 `O-P1-023`.
