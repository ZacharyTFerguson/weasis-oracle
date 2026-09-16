# G-P0-023 edge-case axis

Every named case is a real object. `python3 scripts/verify-edge-023.py` is the gate (CI after `generate-huge-multiframe.py`).

| Named case | Object |
| --- | --- |
| no preamble / raw stream | `G-P0-extra-no-preamble.dcm` (File Meta, no 128-byte preamble/DICM) + `G-P0-edge-raw-stream.dcm` (implicit dataset only) |
| implicit VR body with explicit meta | `G-P0-extra-implicit.dcm` — Part 10 DICM + group 0002, TS `1.2.840.10008.1.2` |
| undefined-length sequences/items | `G-P0-edge-undef-sq.dcm` |
| odd lengths | `G-P0-edge-odd-length.dcm` — UN VL=5 |
| truncated Pixel Data | `G-P0-extra-truncated.dcm` |
| encapsulated frames with no Basic Offset Table | `G-P0-edge-no-bot.dcm` |
| multi-fragment frames | `G-P0-edge-multi-fragment.dcm` |
| >2 GB multi-frame | on-demand `scripts/generate-huge-multiframe.py` → `G-P0-edge-gt2gb.dcm` (**not committed**; gitignored). 512×512×4097×16-bit, Pixel Data VL `2148007936`, logical `st_size` `2148008638` (>2 GiB), sparse (~1040 blocks) |
| 12-bit-in-16 HighBit | `G-P0-edge-12bit.dcm` |
| signed + Rescale | `G-P0-edge-signed-rescale.dcm` |
| MONOCHROME1 + Presentation LUT | `G-P0-edge-mono1-plut.dcm` |
| YBR_FULL_422 + baseline JPEG US | `G-P0-codec-jpeg-baseline-us-01.dcm` |
| overlays in high bits (retired) | `G-P0-edge-overlay-highbits.dcm` |
| private creator blocks | `G-P0-edge-private-creator.dcm` |
| DICOMDIR with case-mismatched referenced file IDs | `G-P0-edge-dicomdir-case/` |
| missing Series/Study UIDs (Weasis synthesizes) | `G-P0-extra-missing-series.dcm`, `G-P0-extra-missing-study.dcm` |

Golden: `corpus/goldens/G-P0-023.json` (`allNamedCasesPassed`).
