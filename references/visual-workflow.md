# Visual Workflow

This reference describes how to handle scanned or photographed handwriting pages.

## Input Handling

Accepted inputs may be:

- PNG/JPEG/HEIC scans or photos.
- PDF pages rendered to images.
- Cropped single-character images.
- A page that includes both exemplars and user writing.

If the input is a PDF, render pages to PNG before segmentation. Prefer a stable
resolution of 200-300 DPI if available.

## Preprocessing

For scans:

- Convert to grayscale.
- Increase contrast.
- Deskew if obvious.
- Preserve the original image.

For photos:

- Correct perspective if the page boundary is visible.
- Remove excessive shadow where possible.
- Do not over-binarize thin pen strokes.

## Grid Pages

When row and column counts are known, use grid cropping. If the visible border is
uneven, crop the page boundary first, then split into cells.

For Tianzige or Mizige, grid lines can interfere with ink extraction. Keep both:

- Raw crop: for placement and grid relationship.
- Ink-emphasized crop: for stroke/structure review.

## Blank Paper

When no grid exists, create a virtual frame for each character:

- Crop the ink bounding box with padding.
- Normalize to a square canvas.
- Record the original bounding box and neighboring context.

Do not judge page layout only from normalized glyphs. Normalization can hide size
inconsistency and baseline drift.

## Overlay Comparison

For exemplar/user comparison:

1. Convert both glyphs to ink masks.
2. Crop each to its ink bounding box.
3. Fit both into the same square canvas with margin.
4. Overlay exemplar and user masks in different colors.
5. Inspect large non-overlap regions.

Overlay is useful for structure, but it is not a final score. A handwritten
glyph may be good even when it does not perfectly match a printed model.

## Contact Sheets

For long pages, use contact sheets:

- Raw cell sheet for segmentation sanity check.
- Normalized glyph sheet for structure comparison.
- Best/worst sample sheet for final report evidence.

## Confidence

Mark low confidence when:

- The crop cuts off strokes.
- The character is too faint or blurred.
- The exemplar and user glyph may be mismatched.
- Grid lines dominate the ink mask.
- The character recognition is uncertain.
