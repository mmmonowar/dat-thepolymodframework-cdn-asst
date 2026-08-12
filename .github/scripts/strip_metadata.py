#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("dat-thepolymodframework-cdn-asst/10 Images")
INDEX_NAME = "10 Index"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".heic"}


def sanitize_files(file_paths):
    cleaned_paths = []
    for raw in file_paths:
        # Strip whitespace, quotes, and normalize Windows backslashes
        clean = raw.strip().strip('"').strip("'").replace("\\", "/")
        p = Path(clean)
        
        # Ensure file exists, has a supported image extension, and is not inside the Index directory
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            if INDEX_NAME not in p.parts:
                cleaned_paths.append(str(p))

    if not cleaned_paths:
        print("strip_metadata: No valid target image files found to sanitize.")
        return

    print(f"strip_metadata: Found {len(cleaned_paths)} image(s) to process.")

    # ExifTool flags:
    # -all= : Removes all standard EXIF, IPTC, XMP metadata and GPS coordinates
    # -overwrite_original : Direct overwrite without creating ._original backups
    cmd = ["exiftool", "-all=", "-overwrite_original", "-q"] + cleaned_paths
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"strip_metadata ERROR:\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    
    print(f"strip_metadata: Successfully stripped metadata from {len(cleaned_paths)} file(s).")


def main():
    # 1. CLI Arguments
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    # 2. Piped Input / stdin
    elif not sys.stdin.isatty():
        files = [line.strip() for line in sys.stdin.readlines() if line.strip()]
    # 3. Fallback: Recursive directory scan of nested files
    else:
        if BASE_DIR.exists():
            files = [
                str(p) for p in BASE_DIR.rglob("*") 
                if p.is_file() and INDEX_NAME not in p.parts
            ]
        else:
            print(f"strip_metadata warning: Base directory '{BASE_DIR}' does not exist.")
            files = []

    sanitize_files(files)


if __name__ == "__main__":
    main()