#!/usr/bin/env bash
# Second oracle: DCMTK header dump plus pydicom/DCMTK/Weasis pixel compare (G-P0-052).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
f="${1:-$root/corpus/phantoms/G-P0-phantom-ct.dcm}"
dcmdump "$f" | head -n 80
pixel="${2:-$root/corpus/phantoms/G-P0-phantom-ct-02.dcm}"
python3 "$root/scripts/second-oracle.py" "$pixel"
