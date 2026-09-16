#!/usr/bin/env bash
# Attach FelixLiveDump into a running Weasis 4.7 JVM (G-P0-000).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
pid="${1:-}"
out="${2:-$root/docs/oracle/census/felix-live-dump.json}"
if [[ -z "$pid" ]]; then
  pid="$(pgrep -n -f '/tmp/weasis-deb/opt/weasis/bin/Weasis' || true)"
fi
if [[ -z "$pid" ]]; then
  echo "no Weasis pid" >&2
  exit 1
fi
export JAVA_HOME="${JAVA_HOME:-$(echo "$HOME"/jdk/jdk-*)}"
export PATH="$JAVA_HOME/bin:$PATH"
work=/tmp/felix-live-dump
mkdir -p "$work"
javac -d "$work" "$root/oracle/java/FelixLiveDump.java"
cat > "$work/MANIFEST.MF" <<'EOF'
Manifest-Version: 1.0
Agent-Class: FelixLiveDump
Premain-Class: FelixLiveDump
Can-Redefine-Classes: false
Can-Retransform-Classes: false

EOF
jar cfm "$work/FelixLiveDump.jar" "$work/MANIFEST.MF" -C "$work" FelixLiveDump.class
# *.jar is gitignored; keep the dump JSON in docs/oracle/census.
jcmd "$pid" JVMTI.agent_load "$work/FelixLiveDump.jar" "$out"
echo "wrote $out"
ls -l "$out"
head -c 2000 "$out"; echo
