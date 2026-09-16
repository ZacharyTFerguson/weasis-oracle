#!/usr/bin/env bash
# G-P0-027a: JaCoCo on the 0a Java producer over corpus v1 (not the 0b 80% gate).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
lib="$root/oracle/java/lib"
export JAVA_HOME="${JAVA_HOME:-$(echo "$HOME"/jdk/jdk-*)}"
export PATH="$JAVA_HOME/bin:$PATH"
ver=0.8.12
jdir=/tmp/jacoco-$ver
mkdir -p "$jdir"
agent="$jdir/jacocoagent.jar"
cli="$jdir/jacococli.jar"
if [[ ! -s "$agent" ]]; then
  curl -fsSL -o "$agent" \
    "https://repo1.maven.org/maven2/org/jacoco/org.jacoco.agent/${ver}/org.jacoco.agent-${ver}-runtime.jar"
fi
if [[ ! -s "$cli" ]]; then
  curl -fsSL -o "$cli" \
    "https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/${ver}/org.jacoco.cli-${ver}-nodeps.jar"
fi
CP="$lib/weasis-core-4.7.0.jar:$lib/weasis-dicom-codec-4.7.0.jar:$lib/weasis-core-img-4.13.0.jar:$lib/joml-1.10.8.jar:$lib/slf4j-api-2.0.17.jar:$lib/slf4j-simple-2.0.17.jar:$lib/flatlaf-3.7.1.jar"
if [[ -f "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" ]]; then
  CP="$CP:$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar"
fi
if [[ -f "$lib/weasis-launcher.jar" ]]; then
  CP="$CP:$lib/weasis-launcher.jar"
fi
mkdir -p /tmp/oracle-java /tmp/jacoco-0a
rm -rf /tmp/oracle-java
mkdir -p /tmp/oracle-java
javac --release 21 --class-path "$CP" -d /tmp/oracle-java \
  "$root/oracle/java/Json.java" \
  "$root/oracle/java/CanonicalHeader.java" \
  "$root/oracle/java/SeriesSplitHarness.java" \
  "$root/oracle/java/DumpMain.java" \
  "$root/oracle/java/DualRunDriver.java" \
  "$root/oracle/java/SlicePositionHarness.java" \
  "$root/oracle/java/HeaderDump.java"
exec_file=/tmp/jacoco-0a/producer.exec
rm -f "$exec_file"
incl='DumpMain*:CanonicalHeader*:SeriesSplitHarness*:DualRunDriver*:HeaderDump*:SlicePositionHarness*:Json*'
agent_arg="-javaagent:$agent=destfile=$exec_file,append=true,includes=$incl,output=file"
ours=/tmp/oracle-java-ours
rm -rf "$ours"
mkdir -p "$ours"
cp /tmp/oracle-java/*.class "$ours/"
phantom="$root/corpus/phantoms/G-P0-phantom-ct-02.dcm"
java -Djava.awt.headless=true "$agent_arg" --class-path "/tmp/oracle-java:$CP" DualRunDriver \
  "$phantom" /tmp/jacoco-0a/run1.json /tmp/jacoco-0a/run2.json >/tmp/jacoco-0a/dual.log 2>&1
java -Djava.awt.headless=true "$agent_arg" --class-path "/tmp/oracle-java:$CP" SlicePositionHarness /tmp/jacoco-0a/slice.json >/tmp/jacoco-0a/slice.log 2>&1
java -Djava.awt.headless=true "$agent_arg" --class-path "/tmp/oracle-java:$CP" HeaderDump "$phantom" /tmp/jacoco-0a/header.json >/tmp/jacoco-0a/header.log 2>&1
ct1="$root/corpus/phantoms/G-P0-phantom-ct-01.dcm"
ct2="$root/corpus/phantoms/G-P0-phantom-ct-02.dcm"
bone="$root/corpus/phantoms/G-P0-split-bone.dcm"
java -Djava.awt.headless=true "$agent_arg" --class-path "/tmp/oracle-java:$CP" SeriesSplitHarness \
  /tmp/jacoco-0a/split.json "$ct1" "$ct2" "$bone" >/tmp/jacoco-0a/split.log 2>&1
out="$root/docs/oracle/jacoco"
mkdir -p "$out"
java -jar "$cli" report "$exec_file" --classfiles "$ours" --csv "$out/jacoco-0a.csv" --xml "$out/jacoco-0a.xml"
python3 - "$out/jacoco-0a.csv" "$out/gap-list.md" <<'PY'
import csv, sys
from pathlib import Path
src, dest = Path(sys.argv[1]), Path(sys.argv[2])
rows = list(csv.DictReader(src.open()))
lines = ["# JaCoCo gaps (G-P0-027a)", "", "Initial report of the 0a harness over corpus v1. Coverage **target** remains `G-P0-027` in 0b.", "", "| Class | Instruction missed | Branch missed | Corpus-add ticket |", "| --- | ---: | ---: | --- |"]
for r in rows:
    name = r.get("CLASS") or r.get("class") or ""
    missed = int(r.get("INSTRUCTION_MISSED") or 0)
    bmiss = int(r.get("BRANCH_MISSED") or 0)
    if missed == 0 and bmiss == 0:
        continue
    ticket = "add objects that hit uncovered DumpMain/split/header branches"
    lines.append(f"| `{name}` | {missed} | {bmiss} | {ticket} |")
dest.write_text("\n".join(lines) + "\n")
print("wrote", dest, "gap rows", len(lines) - 5)
PY
echo "JaCoCo CSV $out/jacoco-0a.csv"
cat "$out/jacoco-0a.csv"
