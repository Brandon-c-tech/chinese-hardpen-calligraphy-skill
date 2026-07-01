#!/usr/bin/env python3
"""Create a contact sheet from glyph crops for visual review."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def make_contact_sheet(paths: list[Path], out: Path, cell_size: int, cols: int) -> None:
    if not paths:
        raise ValueError("No input images provided")
    rows = math.ceil(len(paths) / cols)
    label_h = 22
    sheet = Image.new("RGB", (cols * cell_size, rows * (cell_size + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for idx, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img = ImageOps.contain(img, (cell_size - 12, cell_size - 12))
        col = idx % cols
        row = idx // cols
        x = col * cell_size + (cell_size - img.size[0]) // 2
        y = row * (cell_size + label_h) + 6
        sheet.paste(img, (x, y))
        label = path.stem[:24]
        draw.text((col * cell_size + 6, row * (cell_size + label_h) + cell_size), label, fill=(60, 60, 60), font=font)
        draw.rectangle(
            [
                col * cell_size,
                row * (cell_size + label_h),
                (col + 1) * cell_size - 1,
                (row + 1) * (cell_size + label_h) - 1,
            ],
            outline=(220, 220, 220),
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cell-size", type=int, default=160)
    parser.add_argument("--cols", type=int, default=8)
    args = parser.parse_args()
    make_contact_sheet(args.images, args.out, args.cell_size, args.cols)


if __name__ == "__main__":
    main()
