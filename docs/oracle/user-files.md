# User-file formats (G-P0-063)

Inventory of files the Weasis **4.7** binary reads so `O-P12-012` has an oracle. Sources: v4.7.0 native `resources/` and `conf/base.json` (SHA `3b3e46c59879ead782e5c474e895befae616a715`). Mouse bindings are **properties**, not XML.

| File / key | Role | Schema / fields the 4.7 binary reads | Copied here |
| --- | --- | --- | --- |
| `presets.xml` | Window/level presets | Root `<presets>`. Each `<preset>`: **name**, **modality**, **window**, **level** (mandatory); optional **key** (AWT `KeyEvent` code; 48/49/50 reserved); optional **shape** `LINEAR\|SIGMOID\|SIGMOID_NORM\|LOG\|LOG_INV` | [presets.xml](census/presets.xml) |
| `resources/luts/*.txt` | Custom / shipped LUT directory (`dicom.luts.path` / resources `luts/`) | One LUT per file. Lines `index<TAB>R<TAB>G<TAB>B` (0–255). Filename is the LUT name. | [lut-files.txt](census/lut-files.txt) list; sample [luts/Gray-Rainbow.txt](census/luts/Gray-Rainbow.txt) |
| `attributes-view.xml` | Per-modality overlay text | Root `<modalities>`. `<modality name>` optional `extend`. `<corner name>` `TOP_LEFT\|TOP_RIGHT\|BOTTOM_RIGHT`. `<p index>` DICOM/TagW names, optional `format` (`$V`, `$V:l$n$`, `$V:f$pattern$`) | [attributes-view.xml](census/attributes-view.xml) |
| `series-splitting-rules.xml` | Extra split rules | Loaded by `SplittingRules` when readable | [series-splitting-rules.xml](census/series-splitting-rules.xml) |
| Keyboard shortcuts | Prefs page **Keyboard Shortcuts** | Category / Action / Shortcut / Default table; Edit / Clear / Restore. Not a shipped XML. | [29-prefs-shortcuts.png](census/screenshots/29-prefs-shortcuts.png) |
| Mouse buttons | `weasis.toolbar.mouse.*` in `conf/base.json` | **left/middle/right:** `pan\|winLevel\|sequence\|zoom\|rotation\|measure\|drawings\|contextMenu\|crosshair\|none`. **wheel:** `sequence\|zoom\|rotation\|none`. **buttons:** bitmask LEFT=1024 MIDDLE=2048 RIGHT=4096 SCROLL=2 (show all `7170`) | [weasis-conf/base.json](census/weasis-conf/base.json) |

`O-P12-012` migrates these: XML files as above, LUT dir as `*.txt` RGB tables, shortcuts as the prefs table (no XML), mouse as the four `weasis.toolbar.mouse.*` keys.
