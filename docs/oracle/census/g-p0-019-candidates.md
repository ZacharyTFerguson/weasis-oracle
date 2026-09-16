# G-P0-019 candidates (author notes; two rows signed)

Harness reviewer ≠ census author. Author notes below. **Whole-census Sign:** [g-p0-019-reviewer.md](g-p0-019-reviewer.md) (`82cc891`). Checklist `G-P0-014` / `G-P0-019` ticked from that file. `G-P0-015` stays open.

## Signed §2 add (README-absent, binary does it)

| Row | Evidence | README quote |
| --- | --- | --- |
| HTJ2K open/decode `.201` / `.202` / `.203` (decode/open only, not export, not 16-bit `BE`) | Signed: [g-p0-019-reviewer.md](g-p0-019-reviewer.md). GUI `13`/`56`/`57`; library `docs/oracle/htj2k-probe.md`, `corpus/goldens/G-P0-016.json` | v4.7.0 README: “Modern codecs: … **JPEG-XL** …” — HTJ2K is absent ([readme-v4.7.0-codecs.md](readme-v4.7.0-codecs.md)) |

## Signed census-absent strike

| Row | Evidence | README quote |
| --- | --- | --- |
| `$weasis:config` token `cdb-ext` | Signed: [g-p0-019-reviewer.md](g-p0-019-reviewer.md). v4.7.0 `ConfigData.java` has only `wcfg`/`cdb`/`pro`/`arg`/`auth`. Gogo `help` absence is supporting only. | Connectivity / `weasis://` lines never name `cdb-ext` |

## Not a strike

| Topic | Evidence |
| --- | --- |
| Plugin licenses dialog “No license found” | `48-plugin-licenses.png` — unpacked tree, not a missing feature in the installer UI |
| 3D prefs “No graphic card found” | `36-prefs-3dviewer.png` — Xvfb, not a 4.7 absence |
| gogo `help` | [gogo-help.md](gogo-help.md) — default GUI never binds 17179; live transcript with shipped `base-shell.json`: [gogo-help-live.txt](gogo-help-live.txt) |
| No User's Guide in Help | `45-help-menu.png` / desktop `210-help-menu.png` — `weasis.help.url` unset on this run |
| JPEG-XL | README names it; binary opens hashed `.110` (`162-open-jpegxl.png`). Present, not an add or a strike. Reviewer **refused** add/strike. |
| Hanging protocols | v4.7.0 README does not name a hanging-protocol engine. Binary is `OpeningViewer` `{NONE, ALL_PATIENTS}` + `weasis.open.viewer.clean` (Felix dump). Reviewer **refused** a README strike. |

## Census pages now captured

Language (`47-prefs-language.png`), About (`60-about.png`, `61-about-system-information.png`), System resources (`49-system-resources.png`), Plugin licenses (`48-plugin-licenses.png`), Help Shortcuts (`173` / `weasis-shortcuts.html`), Help flyout **Check for Updates...** (`210`) opening the download page (`211`), Online Help tutorials (`219`), GitHub issues (`220`), Export DICOM wizard (`177`–`180`), explorer thumbnail (`182`–`183`), viewer tab (`184`), File → Print dialogs (`187`–`188`), toolbar DICOM Information (`189`–`190`) and measure/draw/layout/synch/zoom/mouse flyouts (`191`–`195`, `197`), Image Histogram / DICOM dump layouts (`200`–`201`), Histogram Statistics `207`, Oblique MPR `202`, Oblique MPR menubar `221`, MPR-context MIP popup `203`, 2D `MipMenu` `204`–`206`, MIP Custom thickness `212`, MPR MIP nested `213`–`218`, 3D OpenGL error `208`, KO Selection `209`, Implicit VR LE `224`, Explicit VR BE `225`, SR Viewer `226`, ECG Waveform `227`, AU Audio thumbnail `228`, DICOM AU player `235`, encap OPEN `236`, MPEG OPEN `234`, RT Tool `237`–`239`.

## Live extras (not a strike, not an add)

| Topic | Evidence |
| --- | --- |
| JPEG XL **export** format `.jxl` + transcode `.110`/`.111`/`.112` | [export-dicom-dialog.md](export-dicom-dialog.md), `178-export-dicom-options.png`, [export-dicom-live-widgets.txt](export-dicom-live-widgets.txt). README already names JPEG-XL. |
| HTJ2K not in export transcoding combo | same Options dump — consistent with `G-P0-016` |
| MPEG-2 / MPEG-4 | Not a missing 2D still. 4.7 loads `video/dicom` `DicomVideoSeries` and opens **Default System Application** (`MimeSystemAppFactory`). Explorer `222`/`223` show a **Video** thumbnail and no MPEG 2D tab. [mpeg-video.md](mpeg-video.md). |
| Implicit VR LE / Explicit VR BE | GUI opens: `224-open-implicit.png`, `225-open-bigendian.png`. |
| SR / ECG / AU | SR Viewer `226`; Waveform `227`; AU Encapsulated PDF is explorer **Audio** `228` + encap OPEN `236`; DICOM AU player is `235` (`au/dicom`). |
| LUT / preset “import” | Not an unfinished chooser. 25 hashed files in `resources/luts/` ([lut-import.md](lut-import.md)). |
| 3D Viewer | Not a 4.7 absence. This VM has no OpenGL (`208`, prefs `36`). `OpenGLInfo.looksSoftware` rejects llvmpipe. Bytecode chrome: [viewer3d-bytecode.md](viewer3d-bytecode.md). |
| RT Tool | Hidden-series 2D dockable after `(3006,0010)` FOR link. Tab `237`, panel `238`, Load RT BODY `239`. [rt-tool.md](rt-tool.md). |
| Nested Acquisition Time / Lung | Context shots `165`/`166` cropped them. Live 2D Viewer dumps include both ([2dviewer-sortstack-live.txt](2dviewer-sortstack-live.txt), [2dviewer-preset-live.txt](2dviewer-preset-live.txt)). |
