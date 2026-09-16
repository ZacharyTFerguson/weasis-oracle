# Semantic traps (G-P0-008)

| Trap | Java | Go | Gate 0a rule |
| --- | --- | --- | --- |
| `assert` side effects | may be off | no `assert` | never rely on assert for goldens |
| unsigned | limited | `uint` explicit | pixel buffers typed |
| `defer` in loops | n/a | last defer wins | don’t close files in for-range defer |
| DA/TM | dcm4che TZ | time.Time location | store as DICOM strings until parsed |
| IS/DS | BigDecimal-ish | float64 | DS: keep string for BE header |
| `LockOSThread` | EDT | UI thread | Phase 4 |
| **FMA** | Java strict-ish | arm64 fuses `x*y+z` | named intermediates; default suppress |
| `int` width | 32 | 32 or 64 | use `int32`/`int64` in oracle |
| map iteration | HashMap order | random | canonical dumps sort keys (G-P0-053) |
| SortSeriesStack null | `if (val1 == null \|\| val2 == null) return 0` on SHA `3b3e46c5` | Go `cmpNilEither` copies the golden | null-or-null is Weasis behavior, not a stub accident. `instanceNumber_null_left` `cmp: 0` |
| `Double.compare` | NaN greater than numbers; `-0.0 < +0.0` via bit pattern | `oracle.doubleCompare` uses `math.Float64bits` after IEEE `<`/`>` | Go `<`/`>` alone would return 0 for NaN and for `-0` vs `+0` |
