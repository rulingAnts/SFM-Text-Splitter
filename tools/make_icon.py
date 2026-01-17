#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("ERROR: Pillow not installed. Install with: pip install pillow", file=sys.stderr)
    sys.exit(1)


def find_best_source(appiconset: Path) -> Path | None:
    candidates = ["mac1024.png", "mac512.png", "appstore1024.png"]
    for name in candidates:
        p = appiconset / name
        if p.is_file():
            return p
    macs = sorted(appiconset.glob("mac*.png"), key=lambda p: p.stat().st_size, reverse=True)
    return macs[0] if macs else None


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    default_appiconset = repo_root / "AppIcon.appiconset"
    default_out = repo_root / "assets" / "appicon.ico"

    src = None
    if len(sys.argv) >= 2:
        arg1 = Path(sys.argv[1])
        if arg1.is_dir():
            src = find_best_source(arg1)
        elif arg1.is_file():
            src = arg1
        else:
            print(f"ERROR: Source not found: {arg1}", file=sys.stderr)
            sys.exit(2)
    else:
        if default_appiconset.is_dir():
            src = find_best_source(default_appiconset)
        else:
            print("ERROR: AppIcon.appiconset not found. Provide a 1024x1024 PNG as argument.", file=sys.stderr)
            sys.exit(2)

    if src is None or not src.is_file():
        print("ERROR: No suitable source image found.", file=sys.stderr)
        sys.exit(2)

    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else default_out
    ensure_parent(out_path)

    sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    with Image.open(src) as im:
        im = im.convert("RGBA")
        im.save(out_path, format="ICO", sizes=sizes)
    print(f"INFO: Wrote {out_path}")


if __name__ == "__main__":
    main()
