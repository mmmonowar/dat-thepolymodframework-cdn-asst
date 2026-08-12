# asst-thepolymodframework-cdn

Blog Assets for thepolymodframework blog.

## Purpose

This repository acts as a CDN for images referenced from the
[thepolymodframework](https://thepolymodframework.com) Hugo blog. Each post's
assets live under `10 Images/` and are served via jsDelivr CDN URLs
(`https://cdn.jsdelivr.net/gh/mmmonowar/dat-thepolymodframework-cdn-asst@main/...`).
Raw GitHub URLs (`https://raw.githubusercontent.com/...`) also work as a
fallback.

## Image Index

`10 Images/10 Index/` is auto-generated on every push to `10 Images/`
(`.github/workflows/update-index.yml`). It contains two files:

- **`index_images.txt`** — a pipe-delimited table with per-image details:

  ```
  Date-Added | Node | Title | Ext | Size | Metadata
  ```

- **`index_links.txt`** — a tab-separated (TSV) list of copy-paste-ready
  `[title](url)` links for use in blog markdown files:

  ```
  Node | Date-Added | Title | Markdown-Link
  ```

  The Markdown-Link column contains the full snippet, e.g.
  `[SS Journaling-Intellectual-Humility](https://cdn.jsdelivr.net/gh/mmmonowar/dat-thepolymodframework-cdn-asst@main/...HEIC)`.

  > **Embedding in a blog:** `[title](url)` is a clickable link, not an image.
  > To display the image inline in a Hugo post use `![alt text](url)` (or
  > `[![alt text](url)](url)` for a clickable image that opens the full-size
  > file).

The **Metadata** column reports whether privacy-related metadata (EXIF, IPTC,
XMP) has been removed:

- `Stripped` - all EXIF/IPTC/XMP metadata removed
- `Has-Metadata` - metadata still present
- `Unknown` - could not be determined (exiftool unavailable)

## Image Optimization

`.github/workflows/optimize-images.yml` converts every image pushed to
`10 Images/` into an optimized **WebP** (`.github/scripts/optimize_images.py`
using Pillow + pillow-heif):

- Sources: HEIC/HEIF/JPEG/PNG/TIFF/WebP
- Downscaled only if larger than 1920px (never upscaled), quality 80
- The original file is replaced by the `.webp` (metadata is dropped on
  conversion, so stripping is automatic)
- Tune `MAX_WIDTH`, `MAX_HEIGHT`, `WEBP_QUALITY` via workflow env vars

Pipeline on push: **optimize → strip → generate index**, so the index and
markdown links are auto-updated to the optimized WebP assets.

## Metadata Stripping

`.github/workflows/strip_metadata.yml` automatically strips EXIF, IPTC, and
XMP metadata from every image pushed to `10 Images/` using ExifTool
(`exiftool -all= -overwrite_original`). This removes GPS coordinates, camera
make/model, timestamps, and other privacy-sensitive data.

Note: structural tags required to render the image (e.g. dimensions, the
embedded ICC color profile) are retained; they contain no privacy data.

## Automatic Verification

Stripping is enforced automatically — no manual checks needed:

- After stripping, `strip_metadata.yml` rescans every image for
  `EXIF:all`, `IPTC:all`, `XMP:all`, and `gps:all` tags. If anything
  remains, the workflow **fails** (red ✗) and the cleaned files are not
  committed — the offending image must be fixed and re-pushed.
- `update-index.yml` also fails if any image reports `Has-Metadata` in the
  index, so a metadata-laden push turns both workflows red.

The scan only looks at embedded metadata groups, so structural tags
(dimensions, codec config, ICC profile) never cause a false failure.

> **HEIC warning:** Most browsers cannot render HEIC/HEIF files inline. The
> optimizer converts these to WebP on push, so generated links always point to
> a browser-friendly format. If you reference raw HEIC files directly, they
> will only open in Safari (macOS/iOS).
