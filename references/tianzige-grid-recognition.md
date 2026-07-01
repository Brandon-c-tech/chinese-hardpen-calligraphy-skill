# Tianzige / Mizige Grid Recognition

Correct grid recognition is a prerequisite for Chinese hard-pen diagnosis. If
the segmentation cuts characters apart, all downstream scoring and overlay
comparison becomes unreliable.

## Key Distinction

Tianzige and Mizige often contain two kinds of lines:

- Cell boundaries: the true outer edges of each writing cell.
- Internal guides: center cross, diagonal guides, or dotted axes inside a cell.

Do not crop on internal guides. Internal guide lines often pass through the
character body and are frequently dashed, lighter, or visually centered inside
each square.

## Recognition Procedure

1. Locate the full writing table.
2. Detect candidate vertical and horizontal lines.
3. Separate strong continuous cell boundaries from internal guide lines.
4. If detected lines pass through character centers, treat them as center axes.
5. When center axes are detected, infer cell boundaries from the midpoint between
   adjacent axes and extrapolate the first and last outer boundaries.
6. Draw a debug overlay:
   - Boundaries in one color.
   - Center axes or internal guides in another color.
7. Crop cells only after the debug overlay looks correct.
8. Generate a contact sheet from cropped cells.
9. Visually inspect the contact sheet before using any crop in the diagnosis.

## Validation Checklist

A crop set is valid only if:

- Each sampled crop contains exactly one complete character.
- No stroke is cut by the crop edge.
- The center guide appears inside the crop, not at the crop edge.
- Exemplar and user cells align by row and column.
- Left, middle, and right columns all pass inspection.
- Top, middle, and bottom rows all pass inspection.

If any check fails, stop diagnosis and redo segmentation.

## Common Failure Modes

### Internal Axis Used As Boundary

Symptom: each glyph is split into left/right or top/bottom fragments.

Fix: treat the detected line as a center guide. Use midpoints between adjacent
center guides as cell boundaries.

### Instruction Column Treated As Character Cell

Symptom: exemplar crops include vertical instructional text or miss part of the
example character.

Fix: identify the actual first character-cell center, then infer boundaries from
character-cell centers, not from the page label column.

### Grid Lines Pollute Ink Overlay

Symptom: exemplar/user overlay shows large red or blue grid-line artifacts.

Fix: keep raw crops for placement, but create ink-emphasized crops or masks for
structure overlay. Explain any remaining grid artifacts as evidence limitations.

### Skewed Scan

Symptom: crops are correct on the left but drift by the right side of the page.

Fix: deskew or detect row/column lines locally by row band. Do not use one global
constant pitch if the scan is warped.

## Required Evidence Before Diagnosis

Create at least:

- A debug grid overlay with proposed boundaries.
- A corrected contact sheet.
- A note stating whether segmentation confidence is high, medium, or low.

Do not proceed with per-character judgment until the contact sheet is visually
verified.
