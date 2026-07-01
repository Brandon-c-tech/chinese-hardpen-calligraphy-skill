#!/usr/bin/env python3
"""Create an exemplar/user glyph overlay for handwriting comparison.

The script uses only Pillow and NumPy. It thresholds each image, crops the ink
bounding box, fits both masks into the same square canvas, and writes a PNG where
the exemplar is blue, the user glyph is red, and overlap appears dark.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


def otsu_threshold(gray: np.ndarray) -> int:
    hist = np.bincount(gray.ravel(), minlength=256).astype(np.float64)
    total = gray.size
    sum_total = np.dot(np.arange(256), hist)
    weight_bg = 0.0
    sum_bg = 0.0
    best_var = -1.0
    best_t = 127
    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        between = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if between > best_var:
            best_var = between
            best_t = t
    return best_t


def load_mask(path: Path) -> Image.Image:
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img)
    arr = np.array(img)
    threshold = otsu_threshold(arr)
    # Ink is usually darker than paper.
    mask = arr <= threshold
    coords = np.argwhere(mask)
    if coords.size == 0:
        raise ValueError(f"No ink detected in {path}")
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    pad = max(4, int(max(y1 - y0, x1 - x0) * 0.08))
    y0 = max(0, y0 - pad)
    x0 = max(0, x0 - pad)
    y1 = min(mask.shape[0], y1 + pad)
    x1 = min(mask.shape[1], x1 + pad)
    cropped = Image.fromarray((mask[y0:y1, x0:x1] * 255).astype(np.uint8), "L")
    return cropped


def fit_to_canvas(mask: Image.Image, size: int, margin: int) -> np.ndarray:
    max_side = size - 2 * margin
    w, h = mask.size
    scale = min(max_side / w, max_side / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = mask.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (size, size), 0)
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(resized, (x, y))
    return np.array(canvas) > 127


def make_overlay(exemplar: Path, user: Path, out: Path, size: int) -> None:
    exemplar_mask = fit_to_canvas(load_mask(exemplar), size=size, margin=size // 12)
    user_mask = fit_to_canvas(load_mask(user), size=size, margin=size // 12)

    rgb = np.full((size, size, 3), 255, dtype=np.uint8)
    # Exemplar only: blue.
    rgb[exemplar_mask & ~user_mask] = [54, 109, 220]
    # User only: red.
    rgb[user_mask & ~exemplar_mask] = [224, 74, 74]
    # Overlap: near black.
    rgb[exemplar_mask & user_mask] = [35, 35, 35]

    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb, "RGB").save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exemplar", type=Path)
    parser.add_argument("user", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--size", type=int, default=512)
    args = parser.parse_args()
    make_overlay(args.exemplar, args.user, args.out, args.size)


if __name__ == "__main__":
    main()
