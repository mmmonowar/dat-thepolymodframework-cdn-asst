# asst-thepolymodframework-cdn

Blog Assets for thepolymodframework blog.

## Purpose

This repository acts as a CDN for images referenced from the
[thepolymodframework](https://thepolymodframework.com) Hugo blog. Each post's
assets live under `10 Images/` and are served via raw GitHub URLs
(`https://raw.githubusercontent.com/mmmonowar/dat-thepolymodframework-cdn-asst/main/...`).

## Image Index

`10 Images/10 Index/index_images.txt` is auto-generated on every push to
`10 Images/` (`.github/workflows/update-index.yml`). It contains a
pipe-delimited table with per-image details and a **Markdown Snippets**
section at the bottom with copy-paste-ready `[title](url)` links for use in
blog markdown files.

```
Date-Added | Node | Title | Ext | Size | Metadata
```

The **Metadata** column reports whether privacy-related metadata (EXIF, IPTC,
XMP) has been removed:

- `Stripped` - all EXIF/IPTC/XMP metadata removed
- `Has-Metadata` - metadata still present
- `Unknown` - could not be determined (exiftool unavailable)

## Metadata Stripping

`.github/workflows/strip_metadata.yml` automatically strips EXIF, IPTC, and
XMP metadata from every image pushed to `10 Images/` using ExifTool
(`exiftool -all= -overwrite_original`). This removes GPS coordinates, camera
make/model, timestamps, and other privacy-sensitive data.

Note: structural tags required to render the image (e.g. dimensions, the
embedded ICC color profile) are retained; they contain no privacy data.

> **HEIC warning:** Most browsers cannot render HEIC/HEIF files inline. The
> generated `[title](url)` links work as download/source links, but a
> `![alt](url)` embed will not display for HEIC images. Convert HEIC assets
> to JPEG/WebP/PNG if inline display is required.
