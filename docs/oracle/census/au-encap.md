# AU player + encapsulated OPEN on frozen 4.7 (G-P0-014)

Do **not** tick `G-P0-014` / `G-P0-019` from this file.

## Two different 4.7 paths

`AuFactory` reads mime **`au/dicom`** (`uiName` = **DICOM AU**, description **DICOM Voice Audio Waveform**). `MimeSystemAppFactory` reads **`encap/dicom`** (and `video/dicom`) and has no dockable UI.

Hashed `corpus/phantoms/G-P0-iod-au.dcm` is **Encapsulated PDF Storage** (`1.2.840.10008.5.1.4.1.1.104.1`) with `MIMETypeOfEncapsulatedDocument=audio/wav` and a 60-byte `WAVEfmt` payload. Live explorer class is **`DicomEncapDocSeries mime=encap/dicom`**. Double-click does **not** create `AuContainer`. Shot `228-open-au.png` is that explorer **Audio** thumbnail with the SR tab still selected.

Voice-audio mime `au/dicom` needs SOP **Basic Voice Audio Waveform Storage** `1.2.840.10008.5.1.4.1.1.9.4.1`, modality `AU`. Unique-UID copy used for GUI:

`/tmp/census-unique2/au-waveform.dcm` — Patient `G0A^AUWAVE`, Study ID `G0A-AUWAVE`, 1 channel, 8000 samples, 8000 Hz, `SS` 16-bit.

## Live GUI

| Shot | What |
| --- | --- |
| `228-open-au.png` | Explorer **G0A, AU** **Audio** thumbnail; canvas still **DICOM SR Viewer** / `G0A, SR` |
| `235-open-auwave.png` | Menubar **DICOM AU**; selected tab **G0A, AUWAVE**; explorer **G0A, AUWAVE** **Audio** thumbnail |
| `236-encap-xdg-open.png` | OS handler after OPEN of the encap extract: title **genesis-encap-open**, body `xdg-open:` + `encap_*.wav` |

Dump: [specialty-explorer-q014.txt](specialty-explorer-q014.txt) — `AuFactory au/dicom=true`; `G0A, AUWAVE` series `mime=au/dicom`; `ViewerPlugins` includes `org.weasis.dicom.au.AuContainer name=G0A, AUWAVE`; `G0A, AU` remains `DicomEncapDocSeries mime=encap/dicom`.

`AuView.showPlayer` then threw `IllegalArgumentException: No line matching interface Clip supporting format PCM_SIGNED 8000.0 Hz…` ([au-encap-live.log.txt](au-encap-live.log.txt)). This VM has **no JavaSound mixer** (`AudioSystem.isLineSupported(Clip)` is false for ULAW/ALAW/PCM). Play / Stop / slider therefore do not paint. That is a host audio miss, not a missing AU plugin. ECG Waveform `227` is the same class of empty canvas on a tiny phantom.

## Encapsulated OPEN (hole 3 encap)

Live log already had `'xdg-open' failed (exit 4) for …/cache/encap_268070780055639117.wav` before a handler existed. After registering `genesis-encap.desktop` (`audio/wav` → xmessage title **genesis-encap-open**), JVMTI `CensusEncapR014` called `MimeSystemAppViewer.startAssociatedProgramFromLinux` on that extract:

[encap-open-r014.txt](encap-open-r014.txt) — `exists=true len=60` then `startAssociatedProgramFromLinux invoked`.

`236-encap-xdg-open.png` is the titled handler for that path. Census scaffolding desktop file, not a 4.7 bundle. Same OPEN-to-OS mechanism as MPEG `234`.

## RT Tool (see [rt-tool.md](rt-tool.md))

`RtDisplayToolFactory` is a hidden-series 2D dockable, not a viewer. Hashed `G-P0-iod-rtstruct.dcm` lacks `(3006,0010)` so it does not link. Live chrome after a FOR-linked working copy: east-strip tab `237-rt-tool.png`, normalized panel `238-rt-tool-panel.png`, Load RT **PHANTOM / BODY** `239-rt-tool-loaded.png`.
