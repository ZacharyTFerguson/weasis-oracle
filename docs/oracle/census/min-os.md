# Minimum OS from 4.7.0 installers (G-P0-014)

Frozen tag `v4.7.0` / SHA `3b3e46c59879ead782e5c474e895befae616a715`. Not the current weasis.org 4.7.3 download table.

| Pack | Evidence in this tree | Minimum recorded |
| --- | --- | --- |
| Linux amd64 `.deb` | [debian-control.txt](debian-control.txt) | **No Ubuntu/Debian release floor.** Depends: `libc6`, `xdg-utils`, `libstdc++6`, `libgcc1`. Architecture `amd64`. |
| Linux arm64 `.deb` | [debian-control-arm64.txt](debian-control-arm64.txt) from GitHub `weasis_4.7.0-1_arm64.deb` (SHA-256 `784f094268bc5860809bd3f860631665011ad39acc266a714fb99f9bbe2c245e`) | **No Ubuntu/Debian release floor.** Same Depends as amd64. Architecture `arm64`. |
| macOS | native zip `build/script/resources/macosx/Info.plist` `LSMinimumSystemVersion` (frozen tree **and** GitHub `weasis-native.zip` SHA-256 `bad1334c0ddfa1f381211879e83d37ae78621f573eab0edaff6e1adc217f4862`) | **macOS 11** |
| Windows x64 MSI | Frozen WiX [windows-msi-x86-64-package.wxs.excerpt](windows-msi-x86-64-package.wxs.excerpt); shipped MSI [windows-msi-launchcondition.txt](windows-msi-launchcondition.txt) | **Source undeclared.** Shipped LaunchCondition `Installed OR (VersionNT >= 600)` = Vista+, **not** Windows 10. WiX `InstallerVersion=200` is the MSI engine. GitHub shipped `Weasis-4.7.0-x86-64.msi` only (SHA-256 `b429756f9282dd9bec45dcd669ff83ba5f28c91ca73a36ef049f23ae749de7ea`). |
| Windows arm64 MSI | Frozen WiX [windows-msi-aarch64-package.wxs.excerpt](windows-msi-aarch64-package.wxs.excerpt) | Template in source; **not** a v4.7.0 GitHub asset. Same undeclared OS floor. |

Launcher args: [Weasis.cfg](Weasis.cfg) (`AppLauncher`, `gosh.port=17179`, `MaxRAMPercentage=25`, splash, accessibility stub). File associations: [file-associations.properties](file-associations.properties) `.dcm` / `application/dicom`; [Weasis.desktop](Weasis.desktop) MIME `application/dicom;x-scheme-handler/weasis`.

Do not copy 4.7.3 GLIBC/Windows 10 numbers onto this census. Do not treat WiX `InstallerVersion=200` as Windows 10. The shipped x64 MSI floor is `VersionNT >= 600` (Vista+).
