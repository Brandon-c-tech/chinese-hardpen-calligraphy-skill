#!/usr/bin/env python3
"""Crop a scanned handwriting page into regular grid cells.

This is useful for Tianzige, Mizige, square-grid, and copybook pages when the
row and column count is known. It intentionally does not try to understand the
writing; it creates evidence crops for later visual review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def parse_box(text: str | None) -> tuple[int, int, int, int] | None:
    if not text:
        return None
    parts = [int(p.strip()) for p in text.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--box must be x0,y0,x1,y1")
    return parts[0], parts[1], parts[2], parts[3]


def trim_border(img: Image.Image, threshold: int = 245) -> Image.Image:
    gray = ImageOps.grayscale(img)
    arr = np.array(gray)
    ink_or_grid = arr < threshold
    coords = np.argwhere(ink_or_grid)
    if coords.size == 0:
        return img
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    pad = 8
    y0 = max(0, y0 - pad)
    x0 = max(0, x0 - pad)
    y1 = min(arr.shape[0], y1 + pad)
    x1 = min(arr.shape[1], x1 + pad)
    return img.crop((x0, y0, x1, y1))


def is_blankish(cell: Image.Image, threshold: int = 242, min_dark_ratio: float = 0.002) -> bool:
    gray = ImageOps.grayscale(cell)
    arr = np.array(gray)
    return float((arr < threshold).mean()) < min_dark_ratio


def crop_grid(
    image_path: Path,
    out_dir: Path,
    rows: int,
    cols: int,
    box: tuple[int, int, int, int] | None,
    trim: bool,
    skip_blank: bool,
) -> None:
    img = Image.open(image_path).convert("RGB")
    if box:
        img = img.crop(box)
    elif trim:
        img = trim_border(img)

    out_dir.mkdir(parents=True, exist_ok=True)
    width, height = img.size
    cell_w = width / cols
    cell_h = height / rows
    manifest = {
        "source": str(image_path),
        "rows": rows,
        "cols": cols,
        "page_size": [width, height],
        "cells": [],
    }

    for row in range(rows):
        for col in range(cols):
            x0 = int(round(col * cell_w))
            y0 = int(round(row * cell_h))
            x1 = int(round((col + 1) * cell_w))
            y1 = int(round((row + 1) * cell_h))
            cell = img.crop((x0, y0, x1, y1))
            if skip_blank and is_blankish(cell):
                continue
            name = f"r{row + 1:02d}_c{col + 1:02d}.png"
            path = out_dir / name
            cell.save(path)
            manifest["cells"].append(
                {
                    "id": name.removesuffix(".png"),
                    "file": name,
                    "row": row + 1,
                    "col": col + 1,
                    "box": [x0, y0, x1, y1],
                }
            )

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--box", type=parse_box, default=None, help="Optional crop box: x0,y0,x1,y1")
    parser.add_argument("--no-trim", action="store_true", help="Do not auto-trim outer whitespace")
    parser.add_argument("--skip-blank", action="store_true", help="Skip cells with very little dark content")
    args = parser.parse_args()

    crop_grid(
        image_path=args.image,
        out_dir=args.out,
        rows=args.rows,
        cols=args.cols,
        box=args.box,
        trim=not args.no_trim,
        skip_blank=args.skip_blank,
    )


if __name__ == "__main__":
    main()
