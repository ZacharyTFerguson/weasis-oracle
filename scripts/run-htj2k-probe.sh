#!/usr/bin/env bash
# G-P0-016: feed HTJ2K DICOM to frozen Weasis 4.7 DicomImageReader.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
lib="$root/oracle/java/lib"
export JAVA_HOME="${JAVA_HOME:-$(echo "$HOME"/jdk/jdk-*)}"
export PATH="$JAVA_HOME/bin:$PATH"
CP="$lib/weasis-core-4.7.0.jar:$lib/weasis-dicom-codec-4.7.0.jar:$lib/weasis-core-img-4.13.0.jar:$lib/joml-1.10.8.jar:$lib/slf4j-api-2.0.17.jar:$lib/slf4j-simple-2.0.17.jar:$lib/flatlaf-3.7.1.jar"
if [[ -f "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" ]]; then
  CP="$CP:$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar"
fi
cd "$root"
out="$root/corpus/goldens"
mkdir -p "$out" /tmp/oracle-java
javac --class-path "$CP" -d /tmp/oracle-java \
  "$root/oracle/java/Json.java" \
  "$root/oracle/java/Htj2kProbe.java"
control="corpus/phantoms/G-P0-codec-j2k-reversible-01.dcm"
args=(--out "$out/G-P0-016.json" --control "$control")
for f in \
  corpus/phantoms/G-P0-probe-htj2k-lossless.dcm \
  corpus/phantoms/G-P0-probe-htj2k-lossless-rpcl.dcm \
  corpus/phantoms/G-P0-probe-htj2k.dcm
do
  if [[ -f "$f" ]]; then
    args+=(--in "$f")
  fi
done
native=/tmp/opencv-native
mkdir -p "$native"
if [[ -f "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" ]]; then
  unzip -qo -j "$lib/weasis-opencv-core-linux-x86-64-4.13.0-dcm.jar" libopencv_java.so -d "$native"
fi
java -Djava.awt.headless=true \
  -Djava.library.path="$native" \
  --enable-native-access=ALL-UNNAMED \
  --class-path "/tmp/oracle-java:$CP" Htj2kProbe "${args[@]}"
echo "wrote $out/G-P0-016.json"
