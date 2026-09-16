#!/usr/bin/env bash
# Run the Weasis 4.7 library-call producer twice (G-P0-000 / G-P0-053).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
lib="$root/oracle/java/lib"
export JAVA_HOME="${JAVA_HOME:-$(echo "$HOME"/jdk/jdk-*)}"
export PATH="$JAVA_HOME/bin:$PATH"
CP="$lib/weasis-core-4.7.0.jar:$lib/weasis-dicom-codec-4.7.0.jar:$lib/weasis-core-img-4.13.0.jar:$lib/joml-1.10.8.jar:$lib/slf4j-api-2.0.17.jar:$lib/slf4j-simple-2.0.17.jar:$lib/flatlaf-3.7.1.jar"
if [[ -f "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" ]]; then
  CP="$CP:$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar"
fi
if [[ -f "$lib/weasis-launcher.jar" ]]; then
  CP="$CP:$lib/weasis-launcher.jar"
elif [[ -f /tmp/weasis-deb/opt/weasis/lib/app/weasis-launcher.jar ]]; then
  CP="$CP:/tmp/weasis-deb/opt/weasis/lib/app/weasis-launcher.jar"
fi
out="$root/corpus/goldens"
mkdir -p "$out" /tmp/oracle-java
  javac --class-path "$CP" -d /tmp/oracle-java "$root/oracle/java/SlicePositionHarness.java"
    java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SlicePositionHarness "$out/G-P0-000-run1.json"
    java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SlicePositionHarness "$out/G-P0-000-run2.json"
    cmp "$out/G-P0-000-run1.json" "$out/G-P0-000-run2.json"
    cp "$out/G-P0-000-run1.json" "$out/G-P0-000.json"
    echo "determinism ok; slice golden $out/G-P0-000.json"
    cat "$out/G-P0-000.json"
    javac --class-path "$CP" -d /tmp/oracle-java "$root/oracle/java/SortKeyHarness.java"
    java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SortKeyHarness "$out/G-P0-015-run1.json"
    java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SortKeyHarness "$out/G-P0-015-run2.json"
    cmp "$out/G-P0-015-run1.json" "$out/G-P0-015-run2.json"
    cp "$out/G-P0-015-run1.json" "$out/G-P0-015.json"
    echo "sort-key determinism ok; $out/G-P0-015.json"
    cat "$out/G-P0-015.json"
phantom="$root/corpus/phantoms/G-P0-phantom-ct-02.dcm"
if [[ -f "$phantom" ]]; then
  javac --class-path "$CP" -d /tmp/oracle-java "$root/oracle/java/HeaderDump.java" "$root/oracle/java/VolatileTags.java"
  java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" HeaderDump "$phantom" "$out/G-P0-049-run1.json"
  java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" HeaderDump "$phantom" "$out/G-P0-049-run2.json"
  cmp "$out/G-P0-049-run1.json" "$out/G-P0-049-run2.json"
  cp "$out/G-P0-049-run1.json" "$out/G-P0-049.json"
  echo "header dump determinism ok"
fi

split_out="$out/G-P0-000-split"
mkdir -p "$split_out"
ct1="$root/corpus/phantoms/G-P0-phantom-ct-01.dcm"
ct2="$root/corpus/phantoms/G-P0-phantom-ct-02.dcm"
bone="$root/corpus/phantoms/G-P0-split-bone.dcm"
if [[ -f "$ct1" && -f "$ct2" && -f "$bone" ]]; then
  javac --class-path "$CP" -d /tmp/oracle-java "$root/oracle/java/SeriesSplitHarness.java"
  java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SeriesSplitHarness \
    "$out/G-P0-000-split-run1.json" "$ct1" "$ct2" "$bone"
  java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" SeriesSplitHarness \
    "$out/G-P0-000-split-run2.json" "$ct1" "$ct2" "$bone"
  cmp "$out/G-P0-000-split-run1.json" "$out/G-P0-000-split-run2.json"
  cp "$out/G-P0-000-split-run1.json" "$out/G-P0-000-split.json"
  echo "split-on-files determinism ok"
fi

if [[ -f "$phantom" ]]; then
  javac --class-path "$CP" -d /tmp/oracle-java \
    "$root/oracle/java/Json.java" \
    "$root/oracle/java/VolatileTags.java" \
    "$root/oracle/java/CanonicalHeader.java" \
    "$root/oracle/java/SeriesSplitHarness.java" \
    "$root/oracle/java/DumpMain.java" \
    "$root/oracle/java/DualRunDriver.java"
  native=/tmp/opencv-native
  mkdir -p "$native"
  if [[ -f "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" ]]; then
    unzip -qo -j "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" libopencv_java.so -d "$native"
  fi
  java -Djava.awt.headless=true -Djava.library.path="$native" --enable-native-access=ALL-UNNAMED \
    --class-path "/tmp/oracle-java:$CP" DualRunDriver \
    "$phantom" "$out/G-P0-003-run1.json" "$out/G-P0-003-run2.json"
  cp "$out/G-P0-003-run1.json" "$out/G-P0-003.json"
  python3 - "$out/G-P0-003.json" "$out/G-P0-051.json" <<'PY'
import json, sys
from pathlib import Path
src = json.loads(Path(sys.argv[1]).read_text())
uid = src["uidSynthesis"]
out = {
    "schemaVersion": "genesis.oracle.v1",
    "caseId": "G-P0-051",
    "class": uid["impliedClassForOP1011"],
    "reference": src["reference"],
    "uidSynthesis": {
        "api": uid["api"],
        "deterministic": uid["deterministic"],
        "impliedClassForOP1011": uid["impliedClassForOP1011"],
        "note": "runA/runB stripped from this golden; they differ by design (see G-P0-003 dual-run)",
    },
}
Path(sys.argv[2]).write_text(json.dumps(out, indent=2) + "\n")
print("wrote", sys.argv[2], out["class"], "deterministic", uid["deterministic"])
if uid["deterministic"]:
    raise SystemExit("expected UIDUtils.createUID non-deterministic")
PY
fi

if [[ -f "$root/oracle/java/Htj2kProbe.java" ]]; then
  bash "$root/scripts/run-htj2k-probe.sh"
fi
