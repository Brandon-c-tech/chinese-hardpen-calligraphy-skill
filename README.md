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
4. Generate overlays and contact sheets.
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
```

Dependencies:

```bash
python3 -m pip install pillow numpy
```

## Privacy

The skill is built to work locally. Do not upload private handwriting scans,
student work, or generated crop artifacts to external services unless the user
explicitly asks for that.
