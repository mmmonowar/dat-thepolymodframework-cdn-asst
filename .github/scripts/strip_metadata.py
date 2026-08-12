#!/usr/bin/env python3
"""
strip_metadata.py
Single responsibility: Remove all EXIF, GPS, XMP, and IPTC metadata from specified images.
Usage:
  1. CLI Args:   python3 strip_metadata.py path/to/img1.png path/to/img2.jpg
  2. Pipe/stdin: git diff --name-only | python3 strip_metadata.py
  3. Default:    python3 strip_metadata.py  (processes all images in '10 Images/')
"""

import sys
import subprocess
from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".heic"}


def sanitize_files(file_paths):
    valid_files = [
        str(p) for p in file_paths 
        if Path(p).is_file() and Path(p).suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not valid_files:
        print("strip_metadata: No valid image files provided to sanitize.")
        return

    # Call exiftool in a single batch for maximum performance
    cmd = ["exiftool", "-all=", "-overwrite_original", "-q", "-q"] + valid_files
    try:
        subprocess.run(cmd, check=True)
        print(f"strip_metadata: Successfully stripped metadata from {len(valid_files)} file(s).")
    except FileNotFoundError:
        print("strip_metadata error: 'exiftool' is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"strip_metadata error: exiftool failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)


def main():
    # 1. Check if arguments passed via CLI
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    # 2. Check if arguments passed via pipe (stdin)
    elif not sys.stdin.isatty():
        files = [line.strip() for line in sys.stdin if line.strip()]
    # 3. Fallback: Scan '10 Images/' directory
    else:
        base_dir = Path("10 Images")
        if base_dir.exists():
            files = [str(p) for p in base_dir.rglob("*") if p.is_file() and p.parent.name != "10 Index"]
        else:
            files = []

    sanitize_files(files)


if __name__ == "__main__":
    main()