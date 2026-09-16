# weasis-oracle

Characterization lab for **Weasis 4.7.0**. This is not the Java→Go port and not the clean-room Java rebuild.

| Track | Repo | What it is |
| --- | --- | --- |
| Java→Go port | Origin [genesis](https://cursor.com/codebase/zachary-ferguson/genesis) | Mechanical 4.7.0 source map under `internal/weasis/`. Keep that moving. |
| Clean-room Java | [weasisrebuid](https://github.com/ZacharyTFerguson/weasisrebuid) | Rebuild from using the app + docs. Spec in `dicomlight`. Pin **4.7.3**. |
| This repo | [weasis-oracle](https://github.com/ZacharyTFerguson/weasis-oracle) | Gate 0a goldens, census screenshots, Go leaf tests. Pin **4.7.0**. |

Pin: tag `v4.7.0`, SHA `3b3e46c59879ead782e5c474e895befae616a715`. Census PNGs are test fixtures (PHI-free phantoms). Do not delete them.

`weasisrebuid` is 4.7.3. Goldens here are 4.7.0. Treat version drift as a named gap, not a surprise.

## Run

```bash
go test ./internal/oracle
go run ./cmd/weasis-dump dump slice-position --iop 1,0,0,0,1,0 --ipp 0,0,10
go run ./cmd/weasis-dump dump sort-key
```

Java producer (optional): JDK 25 + `bash scripts/fetch-weasis-4.7-bundles.sh` then `bash scripts/run-weasis-producer.sh`.

## License

Apache-2.0. Derived Weasis leaf math: Apache-2.0 option of EPL-2.0 OR Apache-2.0. See NOTICE.
