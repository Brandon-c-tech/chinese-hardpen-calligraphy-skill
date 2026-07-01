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

Tianzige/Mizige pages require explicit boundary validation:

- Real cell boundaries form the crop edges.
- Internal guide lines are often dashed or lighter and usually cross the center
  of the character; they are not crop edges.
- If the detector finds internal axes, infer boundaries from midpoints between
  adjacent axes and extrapolate the outer boundaries.
- Draw a debug image with boundaries and axes in different colors.
- Build a contact sheet and visually check it before analysis.

Stop and redo segmentation if any crop cuts a stroke, includes a neighboring
character, or shifts the exemplar/user pairing.

## Blank Paper

When no grid exists, create a virtual frame for each character:

- Crop the ink bounding box with padding.
- Normalize to a square canvas.
- Record the original bounding box and neighboring context.

Do not judge page layout only from normalized glyphs. Normalization can hide size
inconsistency and baseline drift.

For repeated-character drills arranged on blank paper, prefer row-first
segmentation:

1. Detect ink with a color-specific mask when the pen color is clear, such as
   blue ink on white paper.
2. Find writing rows with vertical projection.
3. Split each row with horizontal projection. Use a horizontal bridge that
   connects disconnected strokes inside one Chinese character but still leaves
   the larger gaps between characters open.
4. Generate a debug image with row boxes and glyph boxes.
5. Generate a glyph contact sheet and inspect it before using any measurements.

This row-first method is usually more reliable than raw connected components:
characters such as `心`, `小`, `六`, and `尔` contain separated dots or strokes
that raw components split into fragments. General OCR can assist by finding
rough text rows or confirming expected row text, but do not treat OCR word boxes
as authoritative single-character crops. OCR often merges neighboring glyphs or
misreads handwritten Chinese as Latin fragments.

If the page follows a visible practice pattern, such as several `下` followed by
several `尔`, labels may be assigned after segmentation from the row pattern or
copybook order. Labels should not create or move glyph boxes.

For isolated repeated-character practice on blank paper, focus on size
consistency first:

- Segment or crop every visible glyph first.
- Group repeated glyph instances by character when possible.
- Keep their original scale; do not resize them for this check.
- Center them on a common canvas and overlay them with low opacity.
- Quantify width, height, area, and coefficient of variation.

Save row spacing, group spacing, and page-flow comments for continuous writing
or for an explicit layout-analysis request.

The visual report should include the blank-paper glyph contact sheet, not just a
whole-page screenshot.

## Stroke Cohort Visuals

When analyzing a repeated stroke, create a cohort view:

- Each crop shows the same visible stroke highlighted.
- A metric table reports length, normalized length, angle, and start/end position.
- A summary chart or panel shows spread and outliers.

Good candidates:

- Repeated `下`: top horizontal angle and length; center vertical placement.
- Repeated `之`: final sweep length and angle.
- Repeated `市`: center vertical alignment and lower-frame verticals.
- Repeated `心`: dot positions and main curved stroke width.

Use these visuals to explain habitual stroke tendencies, not to infer stroke
order.

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

## Annotated Visual Comparisons

A final diagnosis should include marked-up images, not only text. Use:

- Green marks for "keep this" regions.
- Red marks for "fix this first" regions.
- Blue or black marks for exemplar/reference structure.
- Gray guide lines for center, baseline, bounding box, or component division.

For exemplar pages, create a panel with:

1. Exemplar crop.
2. User crop.
3. Overlay.
4. Short labels naming the visible difference.

For no-exemplar pages, create:

1. Raw crop.
2. Normalized crop or virtual-grid crop.
3. Annotated crop with center/bounding-box/component marks.

The visual comparison should show the specific location of the issue: a left
component that is too wide, a weak main stroke, an upward-drifting center, a
cramped interior, or a tilted vertical. Do not let the final artifact be only a
contact sheet plus written comments.

## Confidence

Mark low confidence when:

- The crop cuts off strokes.
- The character is too faint or blurred.
- The exemplar and user glyph may be mismatched.
- Grid lines dominate the ink mask.
- The character recognition is uncertain.
