---
name: chinese-hardpen-calligraphy
description: |
  Diagnose scanned Chinese hard-pen handwriting practice. Use when the user asks
  to critique, grade, compare, diagnose, or improve Chinese penmanship,
  hard-pen calligraphy, copybook practice, character structure, stroke quality,
  or handwritten Chinese pages from images, PDFs, or scans. The workflow supports
  pages with printed exemplars, pages with only user handwriting, grid paper,
  Tianzige/Mizige practice sheets, ruled paper, and blank paper.
---

# Chinese Hard-Pen Calligraphy Diagnosis

This skill diagnoses Chinese hard-pen calligraphy practice from scanned or
photographed pages. It should behave like a careful writing teacher: build visual
evidence first, inspect individual characters, then aggregate cross-character
patterns into a short practice plan.

The target domain is Chinese handwriting, but these instructions are in English.
Write the final user-facing report in the language requested by the user; if they
do not specify a language, match their language.

## Core Principle

Do not rely on one-shot multimodal judgement of a full page. Use an agentic loop:

1. Classify the input page type.
2. Normalize the scan and extract candidate character crops.
3. Pair user-written characters with exemplars when exemplars are present.
4. Create visual evidence artifacts such as crops, overlays, contact sheets, and annotated comparison images.
5. Verify segmentation visually before judging.
6. Score and explain every user-written glyph, not only representative samples.
7. Classify every glyph by quality and issue type.
8. Compare repeated visible strokes across a cohort when stroke issues recur.
9. Aggregate recurring issues across characters, radicals, structures, and layout.
10. Produce archival Markdown and visual HTML reports with evidence.
11. Produce a concise next-practice prescription.

## When Starting

First determine which input case applies:

- Copybook page with printed exemplars and user-written copies.
- User handwriting only, with no exemplar.
- Tianzige, Mizige, square grid, horizontal ruled paper, or blank paper.
- Single large character, repeated single character, or multi-character page.
- Scan/PDF with stable geometry or photo with perspective distortion/shadow.

If the page has no exemplar, compare against a reasonable hard-pen standard:
balanced structure, stable center of gravity, clear stroke relationships, and
readable printed/Kaiti-like reference proportions. Do not overfit to one font.

## Required Loop

Use this loop for substantive diagnosis:

1. Page triage
   - Identify page type, grid type, likely reading order, and scan quality.
   - Note uncertainty when image quality, cropping, or recognition is weak.

2. Segmentation
   - Extract individual glyph crops.
   - For grid pages, prefer grid-based crops.
   - For blank paper, segment or manually crop every visible glyph before judging.
   - Verify segmentation visually before trusting measurements.

3. Pairing
   - If exemplars exist, pair each user glyph with its exemplar by layout.
   - If multiple user attempts correspond to one exemplar, preserve the grouping.
   - If pairing is uncertain, mark it as uncertain instead of forcing a match.

4. Evidence generation
   - Normalize each glyph into a common square canvas.
   - Generate exemplar/user overlays when possible.
   - Keep raw crops available because normalization can hide layout problems.
   - Produce marked-up visual comparisons for key examples. Use green callouts
     for parts to keep and red callouts for parts to fix.
   - Include side-by-side panels showing exemplar, user writing, and overlay
     for priority samples when an exemplar exists.

5. Per-character diagnosis
   Evaluate every user-written glyph across:
   - Overall proportion and bounding box.
   - Center of gravity and placement in the grid or virtual grid.
   - Component proportions for left-right, top-bottom, enclosing, and semi-enclosing structures.
   - Main stroke emphasis and spatial hierarchy.
   - Stroke direction, length, spacing, and terminal control.
   - Consistency across repeated attempts.
   - Multiple issues when present. Do not reduce a glyph to only one flaw if it
     has several clear problems.

   For every glyph, record:
   - Location / crop id.
   - Character or probable character.
   - Quality class: strong, good, usable, needs work, weak.
   - Score when useful.
   - Typical strengths, as a list.
   - Typical issues, as a list.
   - Concrete correction advice.
   - Evidence image paths.
   - When an exemplar exists, the per-glyph report must show three visuals for
     that glyph: the original exemplar crop, the original user-written crop, and
     an exemplar/user overlay. The overlay supplements the original crops; it
     does not replace them.
   - In overlays, suppress obvious border/grid-line artifacts when possible so
     the structure comparison focuses on the glyph ink. Preserve the unmodified
     original crops beside the overlay for placement and grid context.
   - When no exemplar exists, show the user crop and any available virtual-grid,
     size, or cohort evidence, and clearly mark that the three-way comparison is
     unavailable.

6. Cross-character aggregation
   Cluster repeated issues by:
   - Layout: size, baseline, spacing, grid placement, tilt.
   - Structure: width/height ratio, center of gravity, component balance.
   - Radicals/components: recurring weak radicals or side components.
   - Strokes: horizontal, vertical, left-falling, right-falling, hook, dot, turn.
   - Style: too loose, too cramped, too round, too stiff, weak main stroke.

   Also create batch-level views:
   - Best batch: the strongest several glyphs, analyzed together to show what
     the user should preserve.
   - Worst/priority batch: the weakest several glyphs, analyzed together to show
     what to fix first.
   - Typical strengths: representative examples are allowed, but they supplement
     the full per-glyph table; they do not replace it.
   - Typical errors: one character can appear in multiple error categories if it
     has multiple problems.

7. Stroke cohort analysis
   When several glyphs share the same visible stroke position, compare that
   stroke across the cohort:
   - Same character, same stroke position, such as `下` top horizontal.
   - Same component position, such as center vertical in `市`.
   - Same stroke type across related characters, such as long horizontal,
     vertical support, left-falling, right-falling, dot, hook, or turn.

   Measure and visualize:
   - Exemplar/reference parameters when an exemplar is available: measure the
     same visible stroke in the printed model character and treat it as the
     standard anchor for that cohort.
   - Stroke length, preferably normalized by cell or glyph size.
   - Stroke angle relative to the writing baseline.
   - Start and end position inside the cell or virtual cell.
   - Spread across attempts: range, standard deviation, coefficient of variation.
   - Deviation from exemplar: angle delta, normalized-length delta or ratio,
     start-position delta, and end-position delta.
   - Outliers: strokes that are much too long, too short, too flat, too steep,
     or misplaced.

   The visual cohort panel should show the exemplar/reference segment alongside
   the user samples, not only user samples. If there is no exemplar, state that
   the comparison is user-cohort consistency only.

   This is a comparison of visible final stroke traces, not a claim about
   actual stroke order.

8. Practice prescription
   Give no more than three primary correction themes.
   For each theme, include:
   - Evidence characters.
   - What to change.
   - A concrete drill.
   - What the next upload should be checked for.

9. Visual explanation
   - The diagnosis must not be text-only when image inputs are available.
   - Provide annotated image evidence for at least the strongest sample and the
     highest-priority correction sample.
   - Mark exact regions: center-of-gravity drift, component width imbalance,
     weak main stroke, cramped interior space, tilt, over/under-extension, or
     placement in the grid.
   - Reference the visual artifacts in the report so the user can see the cause
     of the judgment without relying on prose alone.

## Use Local Helpers When Useful

This skill includes lightweight scripts that work with Pillow and NumPy:

- `scripts/crop_grid.py`: split a scanned page into regular grid cells when the
  row/column count is known or visually inferable.
- `scripts/make_overlay.py`: normalize an exemplar glyph and a user glyph,
  then create an overlay image for structure comparison.
- `scripts/make_contact_sheet.py`: combine glyph crops into a review sheet.
- `scripts/make_comparison_panel.py`: create a side-by-side exemplar/user/overlay
  panel with brief visual labels.
- `scripts/annotate_image.py`: draw boxes, circles, arrows, and labels on crops,
  overlays, or full-page images.
- `scripts/make_size_consistency_overlay.py`: center repeated glyphs without
  resizing, draw a low-opacity overlay, and write size-consistency metrics.
- `scripts/segment_blank_glyphs.py`: split blank-paper handwriting into
  individual glyph crops using ink detection and connected components.
- `scripts/segment_blank_by_rows.py`: split isolated blank-paper practice by
  detecting writing rows first, then cutting glyphs within each row by
  horizontal projection. Use this before `segment_blank_glyphs.py` when a blank
  page contains repeated-character drills arranged in loose rows.
- `scripts/compare_stroke_segments.py`: compare a named stroke across multiple
  glyphs using manually or visually identified stroke segments, then output
  angle/length metrics and an annotated comparison panel.

Prefer these scripts for evidence creation. Visual-model judgement should explain
the evidence; it should not replace the evidence.

## Safety And Honesty Rules

- Do not infer stroke order from a static final image. You may discuss visible
  stroke shape, pressure, endpoint control, and likely hesitation, but mark such
  observations as visual inferences.
- Do not claim exact character recognition when the crop is unclear.
- Do not treat font mismatch as a writing error. Separate "deviation from the
  exemplar" from "legibility or structural weakness."
- Do not upload private handwriting scans or generated crops to external services
  unless the user explicitly asks.
- If the scan quality is too poor, ask for a clearer scan or explain the limit.

## Report Shape

Use `templates/report-template.md` for full reports. A short report should still
include:

- Overall diagnosis.
- Visual comparison images showing where the writing is strong or weak.
- Per-glyph critique for every user-written glyph.
- Classification of every glyph by quality and issue type.
- Best batch and worst/priority batch analysis.
- Typical strengths and typical errors, with multiple examples.
- Stroke cohort comparisons when repeated stroke-level issues are visible.
- Recurring issues across characters.
- Next practice plan.

For long pages, include a table of per-character results and then summarize the
common patterns. The user should be able to practice immediately after reading.

When exemplars are available, the per-character table must include side-by-side
visual evidence columns for `exemplar`, `user`, and `overlay` so the reader can
compare each critique without opening a separate artifact.

## Report Outputs

Create two report formats for substantial analysis:

- Markdown report for archival storage, diffing, and reuse.
- HTML report for visual review, with embedded or linked images, grouped visual
  evidence, and scannable tables.

The HTML report is the primary reading artifact. The Markdown report is the
record copy.

## Visual Artifact Standard

For each major report, create or include:

- A crop/contact sheet to show what was inspected.
- At least one green-annotated "good sample" image that shows the specific
  stable structure or stroke relationship.
- At least one red-annotated "fix first" image that shows the exact imbalance
  or stroke problem.
- If exemplars exist, at least one exemplar/user/overlay panel.

Do not only say "left side is too wide" or "main stroke is good." Show it with a
marked crop, overlay, guide line, circle, box, or arrow.

## Tianzige Recognition Gate

Correct Tianzige/Mizige recognition is a mandatory gate before diagnosis. A
wrong grid crop can make the entire critique misleading.

Before comparing characters:

- Distinguish real cell boundaries from internal guide lines. In Tianzige, the
  central cross is often dashed or lighter and passes through the character; it
  is not a crop boundary.
- If the strongest detected vertical/horizontal lines cut through glyph centers,
  treat them as internal axes and infer cell boundaries from midpoints between
  neighboring axes.
- Generate a debug image that draws candidate boundaries and candidate center
  axes in different colors.
- Generate a contact sheet from the proposed crops.
- Visually verify that every sampled crop contains exactly one complete
  character with margin on all sides. If any stroke is cut, redo segmentation.

Do not produce final analysis until the corrected contact sheet has been checked.

## Blank Paper Size Consistency

For isolated free-practice characters on blank paper, prioritize character-size
consistency before analyzing row spacing or group spacing. Continuous-writing
spacing can be a separate module later.

Do not start blank-paper segmentation by trusting OCR word boxes. OCR may help
find rough text rows or confirm expected row content, but handwriting OCR often
misreads Chinese glyphs as Latin fragments or merges several glyphs into one
word box. The preferred order for repeated-character drill pages is:

1. Detect ink, preferring color-specific ink masks when the pen color is clear.
2. Detect writing rows by vertical projection.
3. Split each row into glyph boxes by horizontal projection, using a bridge
   wide enough to connect disconnected strokes inside one character but narrow
   enough not to merge neighboring characters.
4. If the row pattern is visually clear or known from the copybook, apply
   row-pattern labels after segmentation; do not let labels create boxes.
5. Generate both a full-page debug overlay and a glyph contact sheet.
6. Visually verify that each crop contains one complete glyph before size or
   structure analysis.

Use size-specific evidence:

- Segment or crop every visible glyph first. Do not analyze blank-paper practice
  only at the page level.
- Group repeated instances of the same character when possible.
- Center all glyph masks on a common canvas without resizing them.
- Overlay them with low opacity so size spread becomes visible.
- Report simple metrics: width range, height range, area range, and coefficient
  of variation.

Only discuss row spacing, group spacing, or page layout when the user provides
continuous writing or explicitly asks for layout analysis.

## References

Read these only as needed:

- `references/agentic-loop.md` for the full multi-pass workflow.
- `references/diagnostic-rubric.md` for scoring criteria.
- `references/visual-workflow.md` for scan/crop/overlay handling.
- `references/tianzige-grid-recognition.md` for identifying and validating
  Tianzige/Mizige cell boundaries.
