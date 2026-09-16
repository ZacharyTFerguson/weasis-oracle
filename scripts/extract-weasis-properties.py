#!/usr/bin/env python3
"""Dump weasis.* / preference keys from the 4.7 native conf JSON (G-P0-060)."""
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
candidates = [
    repo / "docs/oracle/census/weasis-conf",
    Path("/tmp/weasis-native-extract/bin-dist/weasis/conf"),
]
root = next((p for p in candidates if p.is_dir()), None)
if root is None:
    raise SystemExit("no weasis conf directory; run scripts/fetch-weasis-4.7-bundles.sh")

keys = {}
for conf in sorted(root.glob("*.json")):
    data = json.loads(conf.read_text())
    if isinstance(data, list):
        continue
    prefs = data.get("weasisPreferences") or []
    for item in prefs:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        if not code:
            continue
        keys[code] = {
            "code": code,
            "source": conf.name,
            "category": item.get("category"),
            "description": item.get("description"),
            "type": item.get("type"),
        }

out = repo / "docs/oracle/weasis-properties.json"
out.write_text(
    json.dumps(
        {
            "weasis": "v4.7.0",
            "count": len(keys),
            "keys": sorted(keys.values(), key=lambda x: x["code"]),
        },
        indent=2,
    )
    + "\n"
)
print("wrote", out, "count", len(keys))
