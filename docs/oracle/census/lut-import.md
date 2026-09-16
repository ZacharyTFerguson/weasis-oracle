# LUT / preset “import” on frozen 4.7 (G-P0-014)

There is **no file-chooser Import LUT** in the 4.7 GUI. Palettes are files under the install tree `resources/luts/`. Presets are `presets.xml`. Do **not** treat that as an unfinished census page.

## Evidence

- Live 2D Viewer LUT palette flyout `134-lut-palette.png` / `143` family; Preset `135`.
- Hunt leftover `124-lut-import.png` is not a chooser (do not promote it).
- Installer list: [lut-files.txt](lut-files.txt) (25 names). SHA-256 of the same files from the unpacked `weasis_4.7.0-1_amd64.deb`: [lut-files-sha256.txt](lut-files-sha256.txt).

Adding a LUT in 4.7 means placing a `.txt` next to those files (or a user overlay), not an Import dialog.
