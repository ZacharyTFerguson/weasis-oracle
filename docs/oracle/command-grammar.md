# Command grammar (G-P0-061)

Captured from Weasis **v4.7.0** source SHA `3b3e46c59879ead782e5c474e895befae616a715` and from live Gogo `dicom:* -?` / `weasis:* -?` with shipped `conf/base-shell.json` ([gogo-help-live.txt](census/gogo-help-live.txt)).

## `$dicom:get` (`DicomModel.get`)

| Flag | Meaning |
| --- | --- |
| `-l --local=PATH` | open DICOMs from local disk (file or recursive directory) |
| `-r --remote=URI` | open DICOMs from an URI |
| `-w --wado=URI` | open DICOMs from an XML manifest |
| `-z --zip=URI` | open DICOM ZIP from an URI |
| `-p --portable` | open DICOMs from configured directories next to the executable |
| `-i --iwado=DATA` | XML manifest as GZIP-Base64 |
| `-? --help` | show help |

## `$dicom:rs` (`DicomModel.rs`)

| Flag | Meaning |
| --- | --- |
| `-u --url=URL` | DICOMweb service URL |
| `-r --request=QUERYPARAMS` | query params (weasis-pacs-connector style) |
| `-H --header=HEADER` | custom header on all requests |
| `--query-header` / `--retrieve-header` | QIDO / WADO headers |
| `--query-ext` / `--retrieve-ext` / `--accept-ext` | extra QIDO/WADO/Accept parameters |
| `--auth-uid` | Weasis authentication method UID |
| `--oidc-iss` / `--oidc-login` | OpenID Connect issuer / login hint |
| `--show-whole-study` | when downloading a series, list other series in the study |
| `-? --help` | show help |

## `$dicom:close` (`DicomModel.close`)

| Flag | Meaning |
| --- | --- |
| `-a --all` | close all patients |
| `-p --patient=ID` | close by Patient ID |
| `-y --study=UID` | close by Study Instance UID |
| `-s --series=UID` | close by Series Instance UID |
| `-? --help` | show help |

## `$weasis:config` (`ConfigData` launcher)

Parsed from the launch command. 4.7 parameter names:

| Token | Constant | Effect |
| --- | --- | --- |
| `wcfg` | `PARAM_CONFIG_URL` | remote config URL |
| `cdb` | `PARAM_CODEBASE` | `weasis.codebase.url` |
| `pro` | `PARAM_PROPERTY` | property `name value` |
| `arg` | `PARAM_ARGUMENT` | extra launch argument |
| `auth` | `PARAM_AUTHORIZATION` | HTTP authorization |

`cdb-ext` is **not** a 4.7 launcher token in this SHA (no matches under `weasis-launcher`). Second-person strike is signed in [g-p0-019-reviewer.md](census/g-p0-019-reviewer.md) (`ConfigData.java` five tokens only). Gogo `help` not listing it is supporting only. Remote `weasis.properties` still goes through `wcfg` / config URLs. Do not tick `G-P0-019` as a whole-census pass.
