# Corpus logistics (G-P0-029)

- JSON goldens: committed under `corpus/goldens/`.
- Pixel buffers: regenerate with `scripts/generate-phantom-ct.py` in CI (PHI-free synthetic only in this PR).
- **>2 GiB multi-frame:** `scripts/generate-huge-multiframe.py` writes a sparse `corpus/phantoms/G-P0-edge-gt2gb.dcm` (gitignored, not hashed). CI generates, `verify-edge-023.py` checks `st_size` and Pixel Data VL, then deletes the file.
- De-identification tool: **not used** for the synthetic phantom (no PHI). Future TCIA/etc. files must name a tool + verification step before commit.
- CI JDK for Java harness: 25 to match Weasis 4.7 `weasis-parent` (this PR’s Go tests run on the runner’s Go 1.22).
