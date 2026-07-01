#!/usr/bin/env python3
"""Draw callouts on a handwriting crop, overlay, or page image.

Annotation JSON format:

[
  {"kind": "box", "box": [40, 50, 180, 160], "color": "red", "text": "compressed right side"},
  {"kind": "circle", "center": [120, 130], "radius": 28, "color": "green", "text": "stable spacing"},
  {"kind": "arrow", "start": [250, 80], "end": [210, 130], "color": "red", "text": "extend this stroke"},
  {"kind": "line", "points": [[100, 20], [100, 260]], "color": "gray", "text": "center line"},
  {"kind": "label", "xy": [24, 24], "color": "green", "text": "good main stroke"}
]
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


COLORS = {
    "red": (224, 74, 74),
    "green": (46, 148, 88),
    "blue": (54, 109, 220),
    "gray": (120, 120, 120),
    "black": (30, 30, 30),
    "yellow": (235, 174, 52),
}


def color(name: str | None) -> tuple[int, int, int]:
    if not name:
        return COLORS["red"]
    return COLORS.get(name.lower(), COLORS["red"])


def draw_label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: tuple[int, int, int],
    font: ImageFont.ImageFont,
) -> None:
    if not text:
        return
    x, y = xy
    padding = 5
    bbox = draw.textbbox((x, y), text, font=font)
    bg = (255, 255, 255)
    draw.rectangle(
        [bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding],
        fill=bg,
        outline=fill,
        width=2,
    )
    draw.text((x, y), text, fill=fill, font=font)


def arrowhead(start: tuple[int, int], end: tuple[int, int], size: int = 14) -> list[tuple[int, int]]:
    sx, sy = start
    ex, ey = end
    angle = math.atan2(ey - sy, ex - sx)
    left = angle + math.pi * 0.82
    right = angle - math.pi * 0.82
    return [
        end,
        (int(ex + size * math.cos(left)), int(ey + size * math.sin(left))),
        (int(ex + size * math.cos(right)), int(ey + size * math.sin(right))),
    ]


def as_point(value: Any) -> tuple[int, int]:
    return int(value[0]), int(value[1])


def annotate(image: Path, annotations: Path, out: Path, width: int) -> None:
    img = Image.open(image).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    items = json.loads(annotations.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("Annotation file must contain a JSON list")

    for item in items:
        kind = item.get("kind", "label")
        fill = color(item.get("color"))
        text = str(item.get("text", ""))

        if kind == "box":
            box = [int(v) for v in item["box"]]
            draw.rectangle(box, outline=fill, width=width)
            draw_label(draw, (box[0], max(0, box[1] - 18)), text, fill, font)
        elif kind == "circle":
            if "box" in item:
                box = [int(v) for v in item["box"]]
            else:
                cx, cy = as_point(item["center"])
                radius = int(item["radius"])
                box = [cx - radius, cy - radius, cx + radius, cy + radius]
            draw.ellipse(box, outline=fill, width=width)
            draw_label(draw, (box[0], max(0, box[1] - 18)), text, fill, font)
        elif kind == "line":
            points = [as_point(p) for p in item["points"]]
            draw.line(points, fill=fill, width=width)
            if text:
                draw_label(draw, points[-1], text, fill, font)
        elif kind == "arrow":
            start = as_point(item["start"])
            end = as_point(item["end"])
            draw.line([start, end], fill=fill, width=width)
            draw.polygon(arrowhead(start, end), fill=fill)
            if text:
                draw_label(draw, (end[0] + 8, end[1] + 8), text, fill, font)
        elif kind == "label":
            xy = as_point(item["xy"])
            draw_label(draw, xy, text, fill, font)
        else:
            raise ValueError(f"Unsupported annotation kind: {kind}")

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=4)
    args = parser.parse_args()
    annotate(args.image, args.annotations, args.out, args.width)


if __name__ == "__main__":
    main()
