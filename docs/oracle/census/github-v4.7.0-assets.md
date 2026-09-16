# GitHub `v4.7.0` release assets (G-P0-014 installer census)

Fetched 2026-09-16 from `https://api.github.com/repos/nroduit/Weasis/releases/tags/v4.7.0`.
Published `2026-05-28T06:19:03Z`. Tag SHA pin remains `3b3e46c59879ead782e5c474e895befae616a715`.
SHA-256 hashed on this VM from those download URLs.

| Asset | Bytes | SHA-256 (this VM) |
| --- | ---: | --- |
| `weasis-4.7.0-1.x86_64.rpm` | 53720181 | `10deb057f4f2d1114d38fb0746606e566022a8ca592c4b5499564fb0aca6d7cb` |
| `Weasis-4.7.0-aarch64.pkg` | 60849412 | `622d02e10fbc3664dafb82f0f35ae9834cd00b547d837738d2a7ff10d6e13af5` |
| `Weasis-4.7.0-x86-64.msi` | 51085312 | `b429756f9282dd9bec45dcd669ff83ba5f28c91ca73a36ef049f23ae749de7ea` |
| `Weasis-4.7.0-x86-64.pkg` | 63505387 | `947293ac474187d1f49482220baf6d8ae57ba60a1f82e498abab982c29f7f2a3` |
| `weasis-native.zip` | 43813853 | `bad1334c0ddfa1f381211879e83d37ae78621f573eab0edaff6e1adc217f4862` |
| `weasis_4.7.0-1_amd64.deb` | 53636522 | `db307a451ce212c1cbb618fe35386fa4634a3b72a232f4a5765c108cb55ae60b` |
| `weasis_4.7.0-1_arm64.deb` | 51500986 | `784f094268bc5860809bd3f860631665011ad39acc266a714fb99f9bbe2c245e` |

No Windows arm64 MSI. Source has `windows/msi/aarch64/main.wxs`; that pack is not a v4.7.0 GitHub asset.

`weasis-native.zip` `build/script/resources/macosx/Info.plist` `LSMinimumSystemVersion` = **11** (same as the frozen source tree).

`InstallerVersion=200` on the WiX templates is the Windows Installer **engine** version (2.0), not a Windows 10 OS floor. Shipped x64 MSI LaunchCondition is `VersionNT >= 600` (Vista+). See [min-os.md](min-os.md).
