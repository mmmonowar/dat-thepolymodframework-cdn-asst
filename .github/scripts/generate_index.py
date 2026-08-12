#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

BASE_DIR = Path("10 Images")
INDEX_DIR = BASE_DIR / "10 Index"
INDEX_FILE = INDEX_DIR / "index_images.txt"
LINKS_FILE = INDEX_DIR / "index_links.txt"

REPOSITORY = os.environ.get(
    "GITHUB_REPOSITORY", "mmmonowar/dat-thepolymodframework-cdn-asst"
)
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")

# Regex patterns matching:
# Container: YYYY-MM-DD-hh-mm-SS Title
CONTAINER_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\s+(.+)$")
# File: YYYY-MM-DD-hh-mm-SS Title <number>.ext
FILE_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\s+(.+?)(?:\s+(\d+))?\.([a-zA-Z0-9]+)$"
)


def format_size(size_in_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}" if unit != "B" else f"{size_in_bytes} B"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"


def find_exiftool():
    found = shutil.which("exiftool")
    if found:
        return found
    if sys.platform == "win32":
        exe = shutil.which("exiftool.exe")
        if exe:
            return exe
        candidates = [
            r"C:\Users\musta\AppData\Local\Programs\ExifTool\exiftool.exe",
            r"C:\Program Files\ExifTool\exiftool.exe",
        ]
        for candidate in candidates:
            if Path(candidate).is_file():
                return candidate
    return None


def check_metadata(file_path, exiftool):
    """Return 'Stripped', 'Has-Metadata', or 'Unknown' for an image file."""
    if not exiftool:
        return "Unknown"
    try:
        result = subprocess.run(
            [exiftool, "-s", "-EXIF:all", "-IPTC:all", "-XMP:all", str(file_path)],
            capture_output=True,
            text=True,
        )
    except OSError:
        return "Unknown"
    if result.returncode != 0:
        return "Unknown"
    return "Stripped" if not result.stdout.strip() else "Has-Metadata"


def raw_url(file_path):
    """Build a URL-encoded jsDelivr CDN URL for a tracked file."""
    url_path = urllib.parse.quote(file_path.as_posix(), safe="/")
    return f"https://cdn.jsdelivr.net/gh/{REPOSITORY}@{BRANCH}/{url_path}"


def main():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    if not BASE_DIR.exists():
        print(f"Directory {BASE_DIR} not found.")
        return

    exiftool = find_exiftool()

    # Iterate through all direct subdirectories in '10 Images', excluding '10 Index'
    for container in sorted(BASE_DIR.iterdir()):
        if not container.is_dir() or container.name == "10 Index":
            continue

        c_match = CONTAINER_PATTERN.match(container.name)
        container_node = c_match.group(2) if c_match else container.name

        for file_path in sorted(container.iterdir()):
            if not file_path.is_file() or file_path.name.startswith("."):
                continue

            file_size = format_size(file_path.stat().st_size)
            f_match = FILE_PATTERN.match(file_path.name)

            if f_match:
                date_added = f_match.group(1)
                title = f_match.group(2)
                num = f_match.group(3)
                ext = f_match.group(4)
                if num:
                    title = f"{title} {num}"
            else:
                date_added = "N/A"
                title = file_path.stem
                ext = file_path.suffix.lstrip(".")

            rows.append(
                {
                    "date_added": date_added,
                    "node": container_node,
                    "title": title,
                    "extension": ext,
                    "size": file_size,
                    "metadata": check_metadata(file_path, exiftool),
                    "url": raw_url(file_path),
                }
            )

    # Write output to index_images.txt (Pipe-delimited table)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(
            f"{'Date-Added':<22} | {'Node':<25} | {'Title':<35} | {'Ext':<6} | {'Size':<10} | {'Metadata':<12}\n"
        )
        f.write("-" * 130 + "\n")
        for r in rows:
            f.write(
                f"{r['date_added']:<22} | {r['node']:<25} | {r['title']:<35} | {r['extension']:<6} | {r['size']:<10} | {r['metadata']:<12}\n"
            )

    # Write output to index_links.txt (Tab-separated values)
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("Node\tDate-Added\tTitle\tMarkdown-Link\n")
        for r in rows:
            f.write(f"{r['node']}\t{r['date_added']}\t{r['title']}\t[{r['title']}]({r['url']})\n")

    print(f"Index successfully generated at {INDEX_FILE}")
    print(f"Markdown links generated at {LINKS_FILE}")

    offenders = [r["title"] for r in rows if r["metadata"] == "Has-Metadata"]
    if offenders:
        print(
            f"ERROR: Metadata not stripped from {len(offenders)} file(s): {', '.join(offenders)}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
