# Regeneration policy (G-P0-011)

1. Goldens live under `corpus/goldens/` (JSON) plus pixel buffers regenerated in CI **or** LFS (G-P0-029).
2. Changing `oracle/java`, Weasis pin, or schema version **requires** regenerating the set.
3. PR description lists every `caseId` whose bytes changed and why.
4. Each golden JSON includes `platform` (OS, arch, JDK or Go).
5. Lossy TS goldens are invalid on a different native codec build.
6. Harness determinism (G-P0-053): run twice; dumps must be byte-identical **after** stripping `uidSynthesis.runA` / `runB`. `DualRunDriver` is that check. `G-P0-003.json` `caseId` must be `G-P0-003` (the filename), not `G-P0-053`.
