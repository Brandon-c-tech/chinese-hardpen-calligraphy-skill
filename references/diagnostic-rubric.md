# Diagnostic Rubric

Use this rubric to keep judgments stable across pages.

## Score Bands

- 5: Strong. Balanced structure, stable placement, clear main strokes, and good consistency.
- 4: Good. Readable and mostly balanced, with one noticeable but local issue.
- 3: Usable. Legible but structurally uneven or inconsistent.
- 2: Needs work. Multiple issues affect balance, proportion, or stroke clarity.
- 1: Weak. Hard to recognize or structurally collapsed.

Scores are optional. If scoring would distract the user, use qualitative labels:
strong, good, usable, needs work, weak.

Every user-written glyph should receive a quality class. Do not only classify
selected examples.

## Dimensions

### Layout

Check the character in its page context:

- Size consistency across cells or lines.
- Placement in the grid or virtual grid.
- Center of gravity.
- Baseline and vertical drift.
- Spacing between neighboring characters.
- Tilt and page slant.

For isolated blank-paper drills, size consistency is the first layout metric.
Do not over-prioritize row spacing or group spacing unless the input is
continuous writing. Use centered overlays and width/height/area metrics to show
the issue visually and quantitatively.

### Structure

Check the internal architecture:

- Width-height ratio.
- Left-right balance.
- Top-bottom balance.
- Enclosing and semi-enclosing structures.
- Interior white space.
- Main component versus secondary component.
- Whether the character feels too loose, too cramped, too tall, too flat, or lopsided.

### Stroke Quality

Check visible pen control:

- Horizontal stability and slight upward tendency.
- Vertical straightness.
- Left-falling and right-falling stroke extension.
- Dots and short strokes placement.
- Hooks and turns.
- Stroke length hierarchy.
- Start/end control visible in the final shape.

Do not claim actual pressure or stroke order unless there is direct evidence.
Use phrases such as "visually appears" or "the final trace suggests."

### Exemplar Deviation

When an exemplar exists, compare:

- Character scale inside the same frame.
- Bounding box and center.
- Major component placement.
- Main stroke length and angle.
- Interior spacing.
- Overall rhythm.

Separate two ideas:

- Deviation from exemplar.
- Independent writing quality.

A glyph can differ from the exemplar but still be structurally good.

## Common Chinese Hard-Pen Issues

- Left component too wide in left-right characters.
- Right component squeezed or floating.
- Top component too heavy in top-bottom characters.
- Bottom support too weak.
- Enclosure too tight or not closed enough.
- Character center drifting upward.
- Horizontal strokes inconsistent in angle.
- Vertical strokes leaning.
- Main stroke not long enough to stabilize the character.
- Interior spaces uneven.
- Repeated attempts lack consistency.

One glyph may have several issues. Record multiple issues when they are visible,
then use issue-category aggregation to show the user recurring patterns.

## Evidence Language

Prefer evidence-backed comments:

- "The left component takes about half the width, so the right component is compressed."
- "The center of gravity sits above the grid center, making the character feel top-heavy."
- "The longest horizontal does not become the main stabilizing stroke."
- "The repeated samples vary mainly in width, so the next drill should focus on bounding box control."

Avoid vague comments:

- "Looks ugly."
- "Needs practice."
- "Not like the model."
- "Wrong stroke order."

## Visual Evidence Rules

For important praise or criticism, pair the sentence with a marked image:

- Green: stable, balanced, or worth keeping.
- Red: priority correction.
- Blue: exemplar/reference structure.
- Gray: guide lines such as center line, baseline, or component boundary.

Examples:

- Use a vertical guide line to show center-of-gravity drift.
- Use a red box around a compressed component.
- Use a green line over a stable main horizontal stroke.
- Use circles to show cramped or uneven interior spaces.
- Use arrows to show where a stroke should extend or retract.

Text explains the diagnosis; the image proves where it appears.

## Grid Segmentation Reliability

Grid segmentation errors outrank calligraphy judgments. If the crop is wrong,
the diagnosis is invalid.

Before scoring any Tianzige/Mizige page, verify:

- Full character is visible inside each crop.
- Internal center guides are not used as cell boundaries.
- Exemplar and user cells are aligned by row and column.
- Random samples from left, center, and right columns all contain complete glyphs.
- A contact sheet has been visually inspected.

## Batch Analysis

After all glyphs are classified, create:

- Best batch: strongest several glyphs, with shared strengths.
- Worst/priority batch: weakest several glyphs, with shared fixes.
- Issue buckets: all glyphs grouped by problem type.

This helps the user see patterns across multiple characters instead of feeling
that the critique depends on one cherry-picked example.
