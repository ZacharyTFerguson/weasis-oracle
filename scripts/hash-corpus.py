#!/usr/bin/env python3
"""SHA-256 of committed corpus files (G-P0-029)."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skip_names = {"G-P0-edge-gt2gb.dcm"}
files = []
for p in sorted((root / "corpus").rglob("*")):
    if not p.is_file():
        continue
    if p.name.startswith("."):
        continue
    if p.name in skip_names or p.stat().st_size > 100_000_000:
        continue
    rel = p.relative_to(root).as_posix()
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    files.append({"path": rel, "sha256": h, "bytes": p.stat().st_size})
out = root / "corpus/hashes.json"
out.write_text(json.dumps({"count": len(files), "files": files}, indent=2) + "\n")
print("wrote", out, "count", len(files))
