# Windows 4.7.0 installer census (unsigned)

Frozen tag `v4.7.0` / SHA `3b3e46c59879ead782e5c474e895befae616a715`.
Do **not** copy weasis.org 4.7.3 “Windows 10” marketing text onto this census.

## What the frozen WiX actually says

Excerpts: [windows-msi-x86-64-package.wxs.excerpt](windows-msi-x86-64-package.wxs.excerpt), [windows-msi-aarch64-package.wxs.excerpt](windows-msi-aarch64-package.wxs.excerpt).

| Field | x86-64 template | aarch64 template |
| --- | --- | --- |
| `JpInstallerVersion` | `200` | `200` |
| `Package/@Platform` | `x64` | `arm64` |
| `Package/@InstallerVersion` | `$(var.JpInstallerVersion)` → 200 | same |
| `VersionNT` / `Windows 10` string | **absent** | **absent** |
| `FragmentOsCondition` | referenced, **not in Weasis source** (jpackage injects at pack time) | same |

WiX `InstallerVersion=200` means “this MSI needs Windows Installer 2.0” (XP-era engine). It is **not** a Windows 10 OS floor.

`Weasis.windows.properties` in this tree is jpackage version-resource **stubs** (`FILE_VERSION`, `COMPANY_NAME`). No OS floor there either.

## What GitHub shipped

[github-v4.7.0-assets.md](github-v4.7.0-assets.md): one Windows installer, `Weasis-4.7.0-x86-64.msi` (51085312 bytes, SHA-256 `b429756f9282dd9bec45dcd669ff83ba5f28c91ca73a36ef049f23ae749de7ea`). No arm64 MSI on that tag.

Shipped MSI string table (not Weasis source): [windows-msi-launchcondition.txt](windows-msi-launchcondition.txt)

```
LaunchCondition  Installed OR (VersionNT >= 600)
[ProductName][ProductVersion] is not supported on this version of Windows
```

`VersionNT >= 600` is Windows Vista / Server 2008. **No `Windows 10` or `Windows 11` string** in that MSI. This is the jpackage `FragmentOsCondition` injected at pack time.

## Min OS row

- Weasis **source** WiX: undeclared (InstallerVersion=200 is the MSI engine).
- Shipped **x64 MSI**: Vista+ (`VersionNT >= 600`), not Windows 10.

See [min-os.md](min-os.md).
