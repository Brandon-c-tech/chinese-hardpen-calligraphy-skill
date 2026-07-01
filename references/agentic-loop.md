# Agentic Diagnosis Loop

Use this workflow when diagnosing Chinese hard-pen calligraphy from scans.

## Pass 1: Page Triage

Answer these questions before judging writing quality:

- Is there a printed exemplar?
- Are user-written glyphs aligned with exemplars by row, column, or repeated group?
- Is the page in Tianzige, Mizige, square grid, horizontal ruled paper, or blank paper?
- Is the scan flat, skewed, shadowed, low contrast, or perspective distorted?
- Is the task copying a model, writing from memory, or free writing?

State any uncertainty. Poor segmentation will poison the diagnosis.

## Pass 2: Segmentation And Pairing

For grid pages, crop cells first. For blank pages, group connected ink regions and
then visually verify. For exemplar pages, preserve row/column position so that a
user-written glyph can be paired with the correct exemplar.

Do not force a pair when the layout is ambiguous. Mark uncertain pairs and use
them only for broad observations.

## Pass 3: Evidence Artifacts

Create at least one evidence artifact before final diagnosis:

- Raw crop contact sheet.
- Exemplar/user overlay.
- Normalized glyph sheet.
- Annotated page screenshot with boxes or notes.
- Side-by-side comparison panel showing exemplar, user glyph, and overlay.
- Red/green marked crop showing exact strong and weak regions.

For repeated-character practice, create a sequence sheet so consistency is easy
to inspect.

## Pass 4: Per-Glyph Diagnosis

For each inspected glyph, record:

- Character or probable character.
- Crop id / page location.
- Score or qualitative grade.
- Strong point.
- Main issue.
- Evidence.
- Correction advice.
- Confidence.

Use short, concrete language. Avoid vague comments such as "write more neatly."
When the glyph is selected as a strong or weak sample, create a visual annotation
that marks the exact region being praised or corrected.

## Pass 5: Cross-Glyph Aggregation

Look for patterns that appear in at least two or three glyphs:

- Same radical too wide/narrow/high/low.
- Same stroke type unstable.
- Same structure family weak, such as left-right or top-bottom characters.
- Same layout problem, such as drifting upward in the grid.
- Same style tendency, such as cramped interiors or weak main strokes.

The final insights should come from this aggregation, not from a single dramatic
bad sample.

## Pass 6: Practice Prescription

Limit the prescription to the highest-leverage changes:

1. One layout or grid-placement issue.
2. One structural proportion issue.
3. One stroke or component issue.

For each issue, provide a drill:

- What to practice.
- How many repetitions or minutes.
- What visual checkpoint to use.
- Which characters from the current page should be retried.

## Pass 7: Visual Explanation Check

Before finalizing, ask:

- Does every major claim have a visible example?
- Did I show at least one good region and one weak region?
- Did I use overlay or guide marks when the problem is spatial?
- Can the user understand the correction from the image before reading the text?

## Pass 8: Iteration

If the user uploads another page, compare against the previous report:

- Which issue improved?
- Which issue persisted?
- Which new issue became visible after the major problem improved?
- What should be the next single focus?
