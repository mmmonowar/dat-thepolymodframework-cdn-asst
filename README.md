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
(`.github/workflows/update-index.yml`). It contains three files:

- **`index_images.txt`** — a pipe-delimited registry of every image:

  ```
  Index | Date-Added | Container | Title
  ```

  `Container` is the folder a post's assets live in; a container can hold
  more than one image (Title).

- **`stats_images.txt`** — per-image stats, joined to the index by `Index`:

  ```
  Index | Title | Ext | Size | Metadata | Optimized
  ```

  - `Metadata`: `Stripped` / `Has-Metadata` / `Unknown`
  - `Optimized`: `Yes` (WebP) / `No` (source format still present)

- **`index_links.txt`** — a tab-separated (TSV) list of copy-paste-ready
  links for use in blog markdown files and the Hugo layout:

  ```
  Index | Title | Markdown-Link | URL
  ```

  The Markdown-Link column contains the full snippet, e.g.
  `[SS Journaling-Intellectual-Humility](https://cdn.jsdelivr.net/gh/mmmonowar/dat-thepolymodframework-cdn-asst@main/...webp)`.
  The URL column contains the raw URL for tooling (used by the shortcode).

  > **Embedding in a blog:** `[title](url)` is a clickable link, not an image.
  > To display the image inline in a Hugo post use `![alt text](url)` (or
  > `[![alt text](url)](url)` for a clickable image that opens the full-size
  > file).

## Hugo Shortcode

To avoid pasting long CDN URLs into blog posts, use the shortcode in
`hugo-shortcode/cdn.html`. Copy it into your blog repo at
`layouts/shortcodes/cdn.html`, then in any post:

- Embed inline: `{{< cdn "SS Journaling-Intellectual-Humility" >}}`
- Clickable link: `{{< cdn "SS Journaling-Intellectual-Humility" link >}}`

At build time Hugo fetches the live `index_links.txt` from the CDN (cached),
matches the Title, and emits the `<img>` or markdown link. New images work
automatically once pushed. An unknown Title fails the build with a clear
error.

The **Metadata** status (in `stats_images.txt`) reports whether
privacy-related metadata (EXIF, IPTC, XMP) has been removed:

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

Pipeline on push: **optimize (convert + strip + verify) → generate index**, so
the index and markdown links are auto-updated to the optimized WebP assets.

## Metadata Stripping

Metadata stripping happens automatically during optimization: Pillow drops
all EXIF/IPTC/XMP on WebP conversion, and the optimize workflow verifies the
result (see below).

`.github/workflows/strip_metadata.yml` is also available as a **manual**
utility (Actions → Strip Image Metadata → Run workflow) for stripping
metadata from any image using ExifTool (`exiftool -all= -overwrite_original`).
This removes GPS coordinates, camera make/model, timestamps, and other
privacy-sensitive data.

Note: structural tags required to render the image (e.g. dimensions, the
embedded ICC color profile) are retained; they contain no privacy data.

## Automatic Verification

Metadata stripping is enforced automatically — no manual checks needed:

- After optimizing, `optimize-images.yml` rescans every image for
  `EXIF:all`, `IPTC:all`, `XMP:all`, and `gps:all` tags. If anything
  remains, the workflow **fails** (red ✗) and the optimized files are not
  committed — the offending image must be fixed and re-pushed.
- `update-index.yml` also fails if any image reports `Has-Metadata` in the
  index, so a metadata-laden push turns both workflows red.

The scan only looks at embedded metadata groups, so structural tags
(dimensions, codec config, ICC profile) never cause a false failure.

> **HEIC warning:** Most browsers cannot render HEIC/HEIF files inline. The
> optimizer converts these to WebP on push, so generated links always point to
> a browser-friendly format. If you reference raw HEIC files directly, they
> will only open in Safari (macOS/iOS).
