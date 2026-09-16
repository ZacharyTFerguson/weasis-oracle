# Tracks

Earlier tries stay as separate repos. This lab only holds shared 4.7.0 oracle evidence.

1. **genesis** — Weasis **4.7.0** Java→Go. Do not park census work there if it stalls the port.
2. **weasisrebuid** — Clean-room **4.7.3** Java (Felix/Swing) from running the app and docs. Not a fork of `nroduit/Weasis`.
3. **dicomlight** / **Dicomlight-TS** — Spec and earlier DICOM viewer experiments.
4. **weasis-oracle** — Goldens, 219 census PNGs, `weasis-dump`, Go sort-key / slice-position leaves.

Integration here means: goldens + screenshots that both the Go port and the Java rebuild can test against. It is not a merge of those codebases.
