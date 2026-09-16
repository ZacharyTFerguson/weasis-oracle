#!/usr/bin/env python3
"""Click remaining Preferences tree leaves on the running 4.7 binary (DISPLAY=:99)."""
from __future__ import annotations

import hashlib
import os
import subprocess
import time
from pathlib import Path

os.environ["DISPLAY"] = ":99"
OUT = Path("/workspace/docs/oracle/census/screenshots")
OUT.mkdir(parents=True, exist_ok=True)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def shot(name: str, window: str = "root") -> Path:
    dest = OUT / name
    run("import", "-window", window, str(dest))
    return dest


def geom(window_id: str) -> tuple[int, int, int, int]:
    info = run("xwininfo", "-id", window_id).stdout
    abs_x = abs_y = w = h = 0
    for line in info.splitlines():
        if "Absolute upper-left X" in line:
            abs_x = int(line.split(":")[1])
        elif "Absolute upper-left Y" in line:
            abs_y = int(line.split(":")[1])
        elif line.strip().startswith("Width:"):
            w = int(line.split(":")[1])
        elif line.strip().startswith("Height:"):
            h = int(line.split(":")[1])
    return abs_x, abs_y, w, h


def find_prefs() -> str | None:
    ids = run("xdotool", "search", "--name", "Preferences", check=False).stdout.split()
    for wid in ids:
        name = run("xdotool", "getwindowname", wid, check=False).stdout.strip()
        if name == "Preferences":
            return wid
    return None


def click_screen(x: int, y: int) -> None:
    run("xdotool", "mousemove", "--sync", str(x), str(y))
    time.sleep(0.05)
    run("xdotool", "click", "1")
    time.sleep(0.45)


def panel_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    prefs = find_prefs()
    if not prefs:
        raise SystemExit("Preferences window not found")
    x, y, w, h = geom(prefs)
    print(f"prefs {prefs} {w}x{h}+{x}+{y}")
    tree_x = x + 78
    seen: dict[str, str] = {}
    n = 28
    for rel_y in range(48, min(h - 40, 430), 16):
        click_screen(tree_x, y + rel_y)
        name = f"{n:02d}-prefs-y{rel_y}.png"
        dest = shot(name, prefs)
        digest = panel_hash(dest)
        if digest in seen:
            dest.unlink()
            continue
        seen[digest] = name
        print(f"saved {name} hash={digest}")
        n += 1
    print("unique pages", len(seen))
    # Close button: lower-right of dialog
    click_screen(x + w - 70, y + h - 36)
    time.sleep(0.5)
    if find_prefs():
        click_screen(x + w - 70, y + h - 22)
        time.sleep(0.4)
    print("prefs still open", bool(find_prefs()))


if __name__ == "__main__":
    main()
