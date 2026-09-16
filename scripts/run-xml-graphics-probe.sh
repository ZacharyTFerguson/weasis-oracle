#!/usr/bin/env bash
# G-P0-017: marshal XmlGraphicModel through Weasis XmlSerializer.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
lib="$root/oracle/java/lib"
bundles="$root/oracle/java/bundles"
export JAVA_HOME="${JAVA_HOME:-$(echo "$HOME"/jdk/jdk-*)}"
export PATH="$JAVA_HOME/bin:$PATH"
if [[ ! -f "$lib/jaxb-osgi-4.0.3.jar" && -f "$bundles/jaxb-osgi-4.0.3.jar.xz" ]]; then
  xz -dkc "$bundles/jaxb-osgi-4.0.3.jar.xz" > "$lib/jaxb-osgi-4.0.3.jar"
fi
jaxb=/tmp/jaxb-osgi-explode
mkdir -p "$jaxb"
if [[ -f "$lib/jaxb-osgi-4.0.3.jar" ]]; then
  unzip -qo -d "$jaxb" "$lib/jaxb-osgi-4.0.3.jar" "lib/*.jar"
fi
CP="$lib/weasis-core-4.7.0.jar:$lib/weasis-dicom-codec-4.7.0.jar:$lib/weasis-core-img-4.13.0.jar:$lib/joml-1.10.8.jar:$lib/slf4j-api-2.0.17.jar:$lib/slf4j-simple-2.0.17.jar:$lib/flatlaf-3.7.1.jar"
for j in "$jaxb"/lib/*.jar; do
  CP="$CP:$j"
done
mkdir -p /tmp/oracle-java
javac --class-path "$CP" -d /tmp/oracle-java "$root/oracle/java/XmlGraphicsProbe.java"
java -Djava.awt.headless=true --class-path "/tmp/oracle-java:$CP" XmlGraphicsProbe "$root/corpus/goldens/G-P0-017.json"
