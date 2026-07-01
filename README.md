# Chinese Hard-Pen Calligraphy Diagnosis Skill

A Codex skill for diagnosing scanned Chinese hard-pen handwriting practice.

It is designed for an agentic critique loop rather than one-shot image
description. The workflow extracts evidence from scanned pages, compares user
glyphs with exemplars when available, reviews character structure and stroke
quality, then aggregates recurring issues into a concrete practice plan.

## What It Handles

- Chinese hard-pen calligraphy and everyday penmanship practice.
- Copybook pages with printed exemplars plus user writing.
- User handwriting without exemplars.
- Tianzige, Mizige, square grid, ruled paper, and blank paper.
- Single characters, repeated-character drills, and full practice sheets.

## Installed Name

`chinese-hardpen-calligraphy`

## Recommended Workflow

1. Classify the input page.
2. Segment or crop individual characters.
3. Pair each user glyph with its exemplar, if present.
4. Generate overlays, contact sheets, and annotated comparison panels.
5. Visually verify crops and pairings.
6. Diagnose each character.
7. Aggregate recurring structure, stroke, and layout problems.
8. Generate a practice prescription for the next round.

## Helper Scripts

The scripts are intentionally lightweight and local. They create evidence
artifacts for the agent to inspect.

```bash
python3 scripts/crop_grid.py input.png --rows 10 --cols 8 --out out/cells
python3 scripts/make_overlay.py exemplar.png user.png --out out/overlay.png
python3 scripts/make_contact_sheet.py out/cells/*.png --out out/contact-sheet.png
python3 scripts/make_comparison_panel.py user.png --exemplar exemplar.png --out out/panel.png --good "Stable center" --issue "Right side compressed"
python3 scripts/annotate_image.py out/overlay.png --annotations annotations.json --out out/annotated-overlay.png
python3 scripts/make_size_consistency_overlay.py glyphs/*.png --out out/size-overlay.png --metrics out/size-metrics.json
python3 scripts/segment_blank_glyphs.py blank-page.jpg --out out/blank-glyphs --prefer-blue --debug out/blank-segmentation-debug.png
python3 scripts/compare_stroke_segments.py stroke-manifest.json --out out/stroke-comparison.png --metrics out/stroke-metrics.json
```

Dependencies:

```bash
python3 -m pip install pillow numpy
```

## Privacy

The skill is built to work locally. Do not upload private handwriting scans,
student work, or generated crop artifacts to external services unless the user
explicitly asks for that.

## Visual Feedback Requirement

Substantive reports should not be text-only. The skill should produce marked-up
visual evidence: green callouts for what to keep, red callouts for what to fix,
and side-by-side exemplar/user/overlay panels when an exemplar exists.

## Tianzige And Blank Paper Notes

Tianzige recognition is a mandatory gate. Internal center guide lines must not
be used as crop boundaries. Always verify segmentation with a debug overlay and
contact sheet before writing the diagnosis.

For isolated blank-paper practice, prioritize character size consistency first.
Split every visible glyph first, then use centered low-opacity overlays and
width/height/area metrics. Save row spacing, group spacing, and continuous
layout diagnosis for continuous-writing inputs or explicit layout requests.

Substantive outputs should include both:

- Markdown for archival storage.
- HTML for visual review.

## Stroke Cohort Comparison

When the same stroke position recurs across a batch, compare it visually and
quantitatively. Examples: the top horizontal in repeated `下`, the center
vertical in `市`, or the final sweep in `之`. Use annotated crop panels plus
length, angle, and start/end-position metrics so the user can see patterns such
as "my horizontals are consistently too steep" or "my verticals drift left."
