# License matrix (G-P0-103)

Genesis original code is Apache-2.0. Leaf algorithms copied from Weasis use Weasis’s **Apache-2.0 option**. Native codec binaries, translations, and icons are **not** copied into this repo.

| Component | License | URL / evidence | Action |
| --- | --- | --- | --- |
| Genesis original modules | Apache-2.0 | [LICENSE](../../LICENSE) | ours |
| Weasis leaf algorithms (LUT, ROI, MPR, split/sort, slice-position) | EPL-2.0 **OR** Apache-2.0; we take Apache-2.0 | https://github.com/nroduit/Weasis/blob/v4.7.0/LICENSE — dual license in source; Debian `copyright` of the .deb lists EPL-2.0 only | NOTICE + attribution |
| NOTICE | Apache-2.0 attribution | [NOTICE](../../NOTICE) | keep current |
| weasis-core-img 4.13.0 / OpenCV native `4.13.0-dcm` | OpenCV Apache-2.0; Weasis JNI wrapper same dual license as Weasis | https://opencv.org/license/ ; fragment `weasis-opencv-core-*-4.13.0-dcm.jar.xz` in native zip | not copied; cgo pin is `G-P0-056` |
| dcm4che3 / weasis-dicom-tools 5.34.3 | Apache-2.0 | https://github.com/dcm4che/dcm4che/blob/master/LICENSE | Weasis stack; not a second oracle |
| Apache Felix 7.0.5 | Apache-2.0 | https://github.com/apache/felix-dev | runtime only |
| JOML 1.10.8 | MIT | https://github.com/JOML-CI/JOML | producer classpath |
| FlatLaf 3.7.1 | Apache-2.0 | https://github.com/JFormDesigner/FlatLaf/blob/main/LICENSE | producer classpath |
| JAXB / jaxb-osgi 4.0.3 | Eclipse Distribution License 1.0 (BSD-3) | https://github.com/eclipse-ee4j/jaxb-ri | producer classpath for `G-P0-017` |
| weasis-i18n translations | EPL-2.0 OR Apache-2.0 (Weasis module) | https://github.com/nroduit/Weasis/tree/v4.7.0/weasis-i18n | not copied; Phase 12 catalog is `G-P0-115` |
| Icons / SVG in `resources/svg` | Weasis original unless a file names another author | native `resources/svg/` | not copied |
| DCMTK (second oracle) | BSD-style DCMTK | https://github.com/DCMTK/dcmtk/blob/master/COPYRIGHT | CI package |
| pydicom phantoms | MIT | generator only; PatientName `GENESIS^PHANTOM` | no PHI |
| GDCM / libjxl / ffmpeg (codec generators) | GDCM Apache-2.0; libjxl BSD-3; ffmpeg LGPL/GPL depending on build | distro packages in CI | generate compressed phantoms only |

Native fragment SHA-256 values live in `docs/oracle/census/bundle-inventory.json` after `scripts/fetch-weasis-4.7-bundles.sh`.
