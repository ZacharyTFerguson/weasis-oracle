#!/usr/bin/env bash
# Fetch Weasis 4.7.0 native bundles for the Java producer (G-P0-000 / G-P0-003).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
dest="$root/oracle/java/bundles"
mkdir -p "$dest" /tmp/downloads
zip=/tmp/downloads/weasis-native.zip
pins="$root/docs/oracle/producer-jar-pins.json"
if [[ ! -s "$zip" ]]; then
  curl -fsSL -L -o "$zip" "https://github.com/nroduit/Weasis/releases/download/v4.7.0/weasis-native.zip"
fi
# Hash the zip *before* unzip (G-P0-006 residual: verify-after-extract).
python3 - "$zip" "$pins" <<'PY'
import hashlib, json, sys
from pathlib import Path
zip_path, pins_path = map(Path, sys.argv[1:])
h = hashlib.sha256()
with zip_path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
digest = h.hexdigest()
print("weasis-native.zip sha256", digest, "bytes", zip_path.stat().st_size)
if pins_path.is_file():
    expected = json.loads(pins_path.read_text()).get("files", {}).get("weasis-native.zip", {})
    want = expected.get("sha256")
    if want and want != digest:
        raise SystemExit(f"pin mismatch before unzip: weasis-native.zip {digest} != {want}")
PY
rm -rf /tmp/weasis-native-extract
mkdir -p /tmp/weasis-native-extract
unzip -q "$zip" -d /tmp/weasis-native-extract
b="$(find /tmp/weasis-native-extract -type d -name bundle | head -1)"
cp -a "$b"/. "$dest"/
echo "bundles in $dest"
ls "$dest" | wc -l
lib="$root/oracle/java/lib"
mkdir -p "$lib"
for j in weasis-core-4.7.0 weasis-dicom-codec-4.7.0 weasis-core-img-4.13.0 joml-1.10.8; do
  xz -dkc "$dest/${j}.jar.xz" > "$lib/${j}.jar"
done
native="weasis-opencv-core-linux-x86-64-4.13.0-dcm"
if [[ -f "$dest/${native}.jar.xz" ]]; then
  xz -dkc "$dest/${native}.jar.xz" > "$lib/${native}.jar"
fi
curl -fsSL -o "$lib/slf4j-api-2.0.17.jar" https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.17/slf4j-api-2.0.17.jar
curl -fsSL -o "$lib/slf4j-simple-2.0.17.jar" https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.17/slf4j-simple-2.0.17.jar
curl -fsSL -o "$lib/flatlaf-3.7.1.jar" https://repo1.maven.org/maven2/com/formdev/flatlaf/3.7.1/flatlaf-3.7.1.jar
# Launcher (weasis:// parse). Prefer the native zip; fall back to an unpacked .deb.
if [[ -f "$dest/../weasis-launcher.jar" ]]; then
  cp "$dest/../weasis-launcher.jar" "$lib/weasis-launcher.jar"
else
  launcher="$(find /tmp/weasis-native-extract /tmp/weasis-deb -name weasis-launcher.jar 2>/dev/null | head -1 || true)"
  if [[ -n "${launcher:-}" ]]; then
    cp "$launcher" "$lib/weasis-launcher.jar"
  fi
fi
echo "runtime jars in $lib"
python3 - "$root" "$zip" "$dest" "$lib" <<'PY'
import hashlib, json, sys
from pathlib import Path
root, zip_path, dest, lib = map(Path, sys.argv[1:])
pins = {"schemaVersion": "genesis.oracle.v1", "caseId": "G-P0-006-pins", "source": "scripts/fetch-weasis-4.7-bundles.sh"}
files = {}
def sha(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest(), p.stat().st_size
if zip_path.is_file():
    digest, size = sha(zip_path)
    files["weasis-native.zip"] = {"sha256": digest, "bytes": size, "url": "https://github.com/nroduit/Weasis/releases/download/v4.7.0/weasis-native.zip"}
for p in sorted(lib.glob("*.jar")):
    digest, size = sha(p)
    files[p.name] = {"sha256": digest, "bytes": size}
pins["files"] = files
out = root / "docs/oracle/producer-jar-pins.json"
if out.is_file():
    expected = json.loads(out.read_text()).get("files") or {}
    mismatch = []
    for name, meta in files.items():
        old = expected.get(name)
        if old and old.get("sha256") != meta["sha256"]:
            mismatch.append(name)
    missing = [name for name in expected if name not in files]
    if mismatch or missing:
        raise SystemExit(
            "pin mismatch (pin file not overwritten): "
            + ", ".join(mismatch + [f"missing:{n}" for n in missing])
        )
    print("verified", out, "n=", len(files), "(unchanged)")
else:
    out.write_text(json.dumps(pins, indent=2) + "\n")
    print("wrote", out, "n=", len(files), "(first run)")
PY
