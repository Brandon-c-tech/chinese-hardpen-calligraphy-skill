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

For grid pages, crop cells first. For blank pages, segment every visible glyph
or manually crop every visible glyph, then visually verify. For exemplar pages,
preserve row/column position so that a user-written glyph can be paired with the
correct exemplar.

Do not force a pair when the layout is ambiguous. Mark uncertain pairs and use
them only for broad observations.

For Tianzige or Mizige, add a segmentation gate before pairing:

- Identify real cell boundaries separately from internal center guides.
- If detected lines pass through character centers, treat them as axes, not
  boundaries.
- Draw a debug overlay with proposed boundaries and center axes.
- Create a crop contact sheet and inspect it before using any crop for judgment.
- If any crop cuts a stroke or contains two partial characters, redo the grid.

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

For every user-written glyph, record:

- Character or probable character.
- Crop id / page location.
- Score or qualitative grade.
- Quality class: strong, good, usable, needs work, weak.
- Strengths, as a list.
- Issues, as a list. A glyph may have more than one issue.
- Evidence.
- Correction advice.
- Confidence.

Use short, concrete language. Avoid vague comments such as "write more neatly."
When the glyph is selected as a strong or weak sample, create a visual annotation
that marks the exact region being praised or corrected.

Do not replace full per-glyph critique with only one good sample and one bad
sample. Representative samples are useful, but they are evidence highlights
drawn from the full table.

## Pass 5: Cross-Glyph Aggregation

Look for patterns that appear in at least two or three glyphs:

- Same radical too wide/narrow/high/low.
- Same stroke type unstable.
- Same structure family weak, such as left-right or top-bottom characters.
- Same layout problem, such as drifting upward in the grid.
- Same style tendency, such as cramped interiors or weak main strokes.

The final insights should come from this aggregation, not from a single dramatic
bad sample.

Create two batch summaries:

- Best batch: the strongest several glyphs and the shared behavior to preserve.
- Worst/priority batch: the weakest several glyphs and the shared behavior to
  fix first.

Also create issue-category summaries. A glyph can belong to multiple categories,
for example "center drift" and "over-extended final stroke."

For isolated blank-paper repeated characters, first aggregate size consistency:

- Segment every visible glyph before analysis.
- Center glyphs without resizing and make a low-opacity overlay.
- Compare bounding-box width, height, and ink area.
- Discuss row spacing and group spacing only for continuous writing or when the
  user explicitly asks for page-layout feedback.

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

- Did I critique every user-written glyph?
- Did I classify every glyph by quality and issue type?
- Did I show best-batch and worst/priority-batch examples, not only one good and one bad glyph?
- Does every major claim have a visible example?
- Did I show at least one good region and one weak region?
- Did I use overlay or guide marks when the problem is spatial?
- Can the user understand the correction from the image before reading the text?

## Pass 8: Report Outputs

For substantive reports, create:

- A Markdown report for archive.
- An HTML report for visual review.

## Pass 9: Iteration

If the user uploads another page, compare against the previous report:

- Which issue improved?
- Which issue persisted?
- Which new issue became visible after the major problem improved?
- What should be the next single focus?
