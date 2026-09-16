# Second oracle (G-P0-052)

dcm4che is the Weasis stack. Independent checks are **DCMTK** (`dcmdump`, `dcmj2pnm`) and **pydicom**.

## Uncompressed CT (`G-P0-phantom-ct-02.dcm`)

Stored Pixel Data SHA-256 `d93bf0591d37628e5f4aabec5c1969b05014fe5a19478ba3a1c7f2799e6dc84f` (512 bytes) matches:

- Weasis `DumpMain` `storedPixelData` (`corpus/goldens/G-P0-003.json`)
- pydicom `PixelData` and `pixel_array.tobytes()`
- DCMTK `dcmj2pnm -M -W +opw` (no modality LUT, no VOI) 16-bit little-endian

Decoded `rawFrame` is `DicomImageReader.getPlanarImage` (pre-Modality LUT). On this uncompressed phantom it may match stored bytes; that coincidence is not the definition.

Header UIDs / IOP / IPP / Rows / Columns listed in `corpus/goldens/G-P0-052.json` appear in `dcmdump`.

**Disagreements:** none on this object. None were averaged.

**Dropped in 0a:** fused LUT intermediates (need an independent derivation or `G-P0-042`). Lossy TS (`dcmdjpeg` / GDCM) wait for `G-P0-041`.

Run: `bash scripts/second-oracle-header.sh corpus/phantoms/G-P0-phantom-ct-02.dcm`
