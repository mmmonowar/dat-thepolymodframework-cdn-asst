#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path("10 Images")
INDEX_NAME = "10 Index"

SUPPORTED_EXTENSIONS = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
OUTPUT_EXTENSION = ".webp"

MAX_WIDTH = int(os.environ.get("MAX_WIDTH", "1920"))
MAX_HEIGHT = int(os.environ.get("MAX_HEIGHT", "1920"))
QUALITY = int(os.environ.get("WEBP_QUALITY", "80"))


def optimize_file(file_path):
    try:
        from PIL import Image, ImageOps
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError as exc:
        print(f"optimize_images: Missing dependency: {exc}", file=sys.stderr)
        print("Run: pip install pillow pillow-heif", file=sys.stderr)
        sys.exit(1)

    original_size = file_path.stat().st_size
    target = file_path.with_suffix(OUTPUT_EXTENSION)

    with Image.open(file_path) as img:
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img = ImageOps.contain(img, (MAX_WIDTH, MAX_HEIGHT))
            image = img
        else:
            image = img
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB" if not image.mode.endswith("A") else "RGBA")
        image.save(target, "WEBP", quality=QUALITY)

    optimized_size = target.stat().st_size
    saved_bytes = original_size - optimized_size
    print(
        f"optimize_images: {file_path.name} -> {target.name} "
        f"({original_size} B -> {optimized_size} B, saved {saved_bytes} B)"
    )

    file_path.unlink()
    return target


def main():
    if len(sys.argv) > 1:
        files = [Path(raw.strip().strip('"').strip("'")) for raw in sys.argv[1:]]
    elif not sys.stdin.isatty():
        files = [
            Path(line.strip().strip('"').strip("'"))
            for line in sys.stdin.readlines()
            if line.strip()
        ]
    else:
        if not BASE_DIR.exists():
            print(f"optimize_images warning: Base directory '{BASE_DIR}' does not exist.")
            return
        files = [
            p
            for p in BASE_DIR.rglob("*")
            if p.is_file() and INDEX_NAME not in p.parts
        ]

    targets = [
        p
        for p in files
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not targets:
        print("optimize_images: No supported image files found to optimize.")
        return

    print(f"optimize_images: Optimizing {len(targets)} image(s).")
    for p in targets:
        optimize_file(p)
    print("optimize_images: Done.")


if __name__ == "__main__":
    main()
