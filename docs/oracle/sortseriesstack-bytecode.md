# SortSeriesStack 4.7 bytecode (G-P0-015 author notes)

Pinned jar: `oracle/java/lib/weasis-dicom-codec-4.7.0.jar` from `docs/oracle/producer-jar-pins.json`. **Not a Pass.** Do not tick `G-P0-015` from this file.

`javap -c -p` on `org.weasis.dicom.codec.SortSeriesStack` and `$1`–`$6`.

## `getValues()` order (six, not seven)

`$1` instanceNumber → `$2` slicePosition → `$3` sliceLocation → `$5` contentTime → `$4` acquisitionTime → `$6` diffusionBValue.

English `Messages` keys in the same jar:

| Inner | Field | Tag | Message key | `toString` |
| --- | --- | --- | --- | --- |
| `$1` | `instanceNumber` | (0020,0013) `2097171` | `SortSeriesStack.inst` | Instance Number |
| `$2` | `slicePosition` | `TagW.SlicePosition` | `SortSeriesStack.pos_orient` | Anatomical Direction |
| `$3` | `sliceLocation` | (0020,1041) `2101313` | `SortSeriesStack.location` | Slice Location |
| `$5` | `contentTime` | (0008,0033) `524339` | `SortSeriesStack.content_time` | Content Time |
| `$4` | `acquisitionTime` | (0008,0032) `524338` | `SortSeriesStack.time` | Acquisition Time |
| `$6` | `diffusionBValue` | (0018,9087) `1609863` | `SortSeriesStack.dvalue` | Diffusion b-value |

Every `compare` returns `0` if either side is null (`ifnull` / `ifnonnull`). Non-null path:

- `$1`: `Integer.compareTo`
- `$2`: `Double.compare` on `doubleValue`
- `$3` / `$6`: `Double.compareTo`
- `$4` / `$5`: `LocalTime.compareTo`

`SeriesComparator.getReversOrderComparator()` is `Collections.reverseOrder(this)` (Inverse Stack). It is not a seventh `getValues()` entry.

Go: `internal/oracle/sortkey.go` (`doubleCompare` = `Double.compare`; `CmpLocalTime` uses clock nanos only).
