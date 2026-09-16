# 4.7 binary census pack (G-P0-014 signed)

From the frozen **v4.7.0** Linux amd64 installer (`weasis_4.7.0-1_amd64.deb`), SHA pin `3b3e46c59879ead782e5c474e895befae616a715`, not from README-on-master.

| Artifact | What |
| --- | --- |
| `bundle-inventory.json` | 48 shipped bundles + SHA-256 |
| `series-splitting-rules.xml` | Weasis resource the library constructor also tries to load |
| `file-associations.properties` | `.dcm` / `application/dicom` (native zip) |
| `Weasis.desktop` / `Weasis-MimeInfo.xml` | installer MIME: `application/dicom`, `x-scheme-handler/weasis`, glob `*.dcm` |
| `debian-control.txt` | Package `weasis` 4.7.0-1 amd64; **Depends:** `libc6`, `xdg-utils`, `libstdc++6`, `libgcc1` (no Ubuntu/Debian release floor) |
| `debian-control-arm64.txt` | Same Depends, Architecture `arm64` |
| `Weasis.cfg` | jpackage launcher: `AppLauncher`, `gosh.port=17179`, MaxRAMPercentage=25, splash, accessibility stub |
| `Weasis.windows.properties` | Windows version resource stubs (no OS floor) |
| `windows-installer.md` | Frozen WiX Package lines + shipped MSI LaunchCondition `VersionNT >= 600` (Vista+, not Win10) |
| `github-v4.7.0-assets.md` | Seven GitHub tag assets; no Windows arm64 MSI |
| `lut-files.txt` | 25 shipped LUT files under `resources/luts/` |
| `screenshots/` | Running binary on Xvfb 1600×900 — see [binary-run.md](binary-run.md). **Keep as test fixtures; do not delete.** |
| `gogo-help.md` | Default GUI never binds 17179 (`gogo.shell` not in `base.json`). Live `help` with shipped `base-shell.json`: [gogo-help-live.txt](gogo-help-live.txt) |
| `g-p0-014-method.md` | Method-item coverage table (unsigned; flyouts `143`–`149`; nested context `164`–`170`; unique-UID TS GUI `150`–`151`, `156`–`161`, `163`; JPEG-XL `.110` `162`; runtime overlay `weasis-properties-runtime.txt` + `171`) |
| `weasis-properties-runtime.txt` | Live `~/.weasis/preferences/ubuntu/default/weasis.properties` after Felix boot |
| `gogo-weasis-info.txt` | Live `weasis:info -a` / `-v` (Weasis 4.7.0, install path `/home/ubuntu/.weasis`) |
| `weasis-shortcuts.html` | Help → Shortcuts dump from ShortcutManager (Weasis 4.7.0); screenshot `173-help-shortcuts.png` |
| `explorer-context-menu.md` | Explorer thumbnail popup live `182`–`183`; viewer tab popup `184` (Close Others / Close All / Maximize `Ctrl+M` / Close `Ctrl+W`) |
| `export-dicom-dialog.md` | File → Export DICOM live wizard `177`–`180` (Local Device / Options / DICOM Send / CD/DVD Image). JPEG XL `.jxl` export + JPEG XL transcode `.110`/`.111`/`.112`; HTJ2K absent. |
| `export-dicom-live-widgets.txt` | Live Swing dump of Export DICOM format combo + Image Export Options transcoding UIDs |
| `print-dialogs.md` | File → Print live `DicomPrintDialog` `187` and `PrintDialog` `188` |
| `toolbar-flyouts.md` | Toolbar DICOM Information `189`–`190`, measure/draw/layout/synch/zoom/mouse flyouts `191`–`195`, `197`, layout views Image Histogram `200` and DICOM dump `201`, Histogram Statistics `207`, Oblique MPR `202`, MPR-context MIP popup `203` plus nested `213`–`218`, 2D `MipMenu` `204`–`206`, Custom thickness `212`, 3D OpenGL error `208`, KO Selection `209` |
| `mpr-mip-nested-live.txt` | MPR MIP thickness / Custom / All views / MIP type / Change MPR preferences / Synchronize (`213`–`218`) |
| `oblique-mpr-menu.txt` | Live Oblique MPR menubar dump (Preset through Reset); screenshot `221-oblique-mpr-menu.png` |
| `mip-2d-live.txt` | Live 2D `MipMenu` projection / thickness / rebuild dump |
| `mip-custom-thickness-live.txt` | Live Custom thickness dialog spinner (`212`) |
| `histogram-stats-live.txt` | Image Histogram → Statistics dialog values (`207`) |
| `help-menu-live.txt` | Live Help `JMenu` dump: Keyboard Shortcuts through About Weasis (`210`) |
| `help-browser-live.txt` | Help browser targets: Shortcuts HTML, Check for Updates download page `211`, Online Help tutorials `219`, GitHub issues `220` |
| `mpeg-video.md` | MPEG-2/4 is `video/dicom` + Default System Application; explorer `222`/`223`; OPEN dump `mpeg-open-h014.txt` + titled handler `234-mpeg-xdg-open.png` |
| `au-encap.md` | DICOM AU player `235` (`au/dicom` / `AuContainer`); hashed AU IOD is encap PDF; encap OPEN `236` / `encap-open-r014.txt` |
| `rt-tool.md` | RT Tool 2D dockable after `(3006,0010)` FOR link: tab `237`, panel `238`, Load RT BODY `239`; hashed `G-P0-iod-rtstruct-for.dcm` |
| `felix-lb-live.txt` | Live `felix:lb` on Linux amd64 GUI (38 rows; other-arch natives and Dicomizer acquire bundles called out) |
| `2dviewer-sortstack-live.txt` | 2D Viewer Sort Stack items including Acquisition Time |
| `2dviewer-preset-live.txt` | 2D Viewer Preset items including Lung |
| `viewer3d-bytecode.md` | 3D `ActionVol` / messages; live path is OpenGL error `208`; `OpenGLInfo.looksSoftware` rejects Mesa llvmpipe so this VM cannot grow a volume tab; live probe [gl-info-aj014.txt](gl-info-aj014.txt) |
| `gl-info-aj014.txt` | Live `View3DFactory.getOpenGLInfo`: `llvmpipe (LLVM 20.1.2, 256 bits)`, `looksSoftware=true`, then `opengl.enable=false` |
| `lut-import.md` | LUT “import” is files in `resources/luts/` (25 SHA-256) |

Whole-census `G-P0-014` / `G-P0-019` **signed** at `82cc891` ([g-p0-019-reviewer.md](g-p0-019-reviewer.md)). MPEG explorer **Video** `222`/`223` plus OPEN-to-OS `234` / [mpeg-open-h014.txt](mpeg-open-h014.txt); RT Tool `237`–`239` ([rt-tool.md](rt-tool.md)); 3D live path is OpenGL error `208` (`OpenGLInfo.looksSoftware` rejects llvmpipe — [viewer3d-bytecode.md](viewer3d-bytecode.md), [gl-info-aj014.txt](gl-info-aj014.txt)). LUT import is files-on-disk. Implicit VR LE `224`, Explicit VR BE `225`, SR Viewer `226`, ECG Waveform `227`, AU Encapsulated-PDF Audio thumbnail `228`, DICOM AU player `235` ([au-encap.md](au-encap.md)), encap OPEN `236`. Explorer thumbnail popup (`182`–`183`) and viewer tab popup (`184`) are captured. Live gogo `help` is captured via shipped `base-shell.json` ([gogo-help-live.txt](gogo-help-live.txt)); default GUI `base.json` still does not bind 17179. Language / About / System resources / Plugin licenses / File Import DICOM / DICOM CD prompt / logging folder / LUT Shape / LUT palette / Preset list / 2D Viewer Filter–Reset flyouts / nested image-context flyouts (`164`–`170`) / extra toolbars (`172`) / Help → Shortcuts HTML ([weasis-shortcuts.html](weasis-shortcuts.html)) / Export DICOM wizard (`177`–`180`) / File → Print dialogs (`187`–`188`) / toolbar DICOM Information + flyouts (`189`–`195`, `197`) / Image Histogram + DICOM dump layouts (`200`–`201`) / Histogram Statistics `207` / Oblique MPR `202` + MPR-context MIP `203` / 2D `MipMenu` `204`–`206` / MIP Custom thickness `212` / MPR MIP nested `213`–`218` / 3D toolbar OpenGL error `208` / KO Selection `209` / Help flyout `210` + Check for Updates download page `211` / Online Help tutorials `219` / GitHub issues `220` are captured. LUT/preset “import” is files on disk, not a chooser. Minimum OS from this tree: [min-os.md](min-os.md) (macOS 11 in Info.plist; Linux amd64/arm64 `.deb` have no Ubuntu floor; shipped Windows x64 MSI `VersionNT >= 600` / Vista+, not Win10 — [windows-installer.md](windows-installer.md)). Zoom flyout on this Xvfb omits “real world size” (`Monitor.getRealScaleFactor` is 0).

Native `conf/*.json` preference keys: `docs/oracle/weasis-properties.json` (114). Command grammar from 4.7 source: `docs/oracle/command-grammar.md`. Hanging protocols in this SHA are `OpeningViewer` `{NONE, ALL_PATIENTS}` plus `weasis.open.viewer.clean` (live dump), not a full HP engine.

**Signed §2 add:** HTJ2K decode/open `.201`/`.202`/`.203` ([g-p0-019-reviewer.md](g-p0-019-reviewer.md)). **Signed strike:** `cdb-ext`. Whole-census `G-P0-014` / `G-P0-019` ticked from that Sign. `G-P0-015` remains last. Xvfb 3D prefs: “No graphic card found or required OpenGL capabilities not available.”
