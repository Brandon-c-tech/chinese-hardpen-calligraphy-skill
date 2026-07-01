#!/usr/bin/env python3
"""Visualize and quantify size consistency across repeated glyph crops.

The script detects ink in each input image, crops to the ink bounding box, and
centers every glyph on a common canvas without resizing. This preserves actual
size differences. The output overlay uses low-opacity blue glyphs plus summary
guide boxes for median and min/max extents.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


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


def detect_ink(path: Path, prefer_blue: bool) -> tuple[np.ndarray, dict[str, float]]:
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)

    if prefer_blue:
        mask = (b > 70) & (b > r + 18) & (b > g + 4) & (r < 180) & (g < 205)
    else:
        gray_img = ImageOps.autocontrast(img.convert("L"))
        gray = np.array(gray_img)
        threshold = otsu_threshold(gray)
        mask = gray <= threshold

    coords = np.argwhere(mask)
    if coords.size == 0:
        raise ValueError(f"No ink detected in {path}")

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    crop = mask[y0:y1, x0:x1]
    h, w = crop.shape
    metrics = {
        "width": float(w),
        "height": float(h),
        "area": float(mask.sum()),
        "aspect_ratio": float(w / h) if h else 0.0,
    }
    return crop, metrics


def coefficient_of_variation(values: list[float]) -> float:
    arr = np.array(values, dtype=np.float64)
    mean = float(arr.mean())
    if mean == 0:
        return 0.0
    return float(arr.std(ddof=0) / mean)


def summary(values: list[float]) -> dict[str, float]:
    arr = np.array(values, dtype=np.float64)
    return {
        "min": float(arr.min()),
        "median": float(np.median(arr)),
        "max": float(arr.max()),
        "mean": float(arr.mean()),
        "cv": coefficient_of_variation(values),
    }


def paste_mask(layer: np.ndarray, mask: np.ndarray, x: int, y: int) -> None:
    h, w = mask.shape
    layer[y : y + h, x : x + w] = np.maximum(layer[y : y + h, x : x + w], mask.astype(np.float32))


def make_overlay(paths: list[Path], out: Path, metrics_out: Path, canvas_size: int, prefer_blue: bool) -> None:
    glyphs = []
    records = []
    for path in paths:
        mask, metrics = detect_ink(path, prefer_blue=prefer_blue)
        glyphs.append(mask)
        records.append({"file": str(path), **metrics})

    max_w = max(mask.shape[1] for mask in glyphs)
    max_h = max(mask.shape[0] for mask in glyphs)
    size = max(canvas_size, max(max_w, max_h) + 80)

    layer = np.zeros((size, size), dtype=np.float32)
    center = size // 2
    for mask in glyphs:
        h, w = mask.shape
        x = center - w // 2
        y = center - h // 2
        paste_mask(layer, mask, x, y)

    # Accumulation image: darker blue means more overlap.
    alpha = np.clip(layer, 0, 1)
    rgb = np.full((size, size, 3), 255, dtype=np.uint8)
    rgb[:, :, 0] = (255 - alpha * 160).astype(np.uint8)
    rgb[:, :, 1] = (255 - alpha * 105).astype(np.uint8)
    rgb[:, :, 2] = (255 - alpha * 20).astype(np.uint8)
    img = Image.fromarray(rgb, "RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    widths = [r["width"] for r in records]
    heights = [r["height"] for r in records]
    areas = [r["area"] for r in records]
    width_summary = summary(widths)
    height_summary = summary(heights)
    area_summary = summary(areas)

    # Median box in green, min/max size envelope in red.
    median_w = int(round(width_summary["median"]))
    median_h = int(round(height_summary["median"]))
    max_box_w = int(round(width_summary["max"]))
    max_box_h = int(round(height_summary["max"]))
    min_box_w = int(round(width_summary["min"]))
    min_box_h = int(round(height_summary["min"]))

    def centered_box(w: int, h: int) -> list[int]:
        return [center - w // 2, center - h // 2, center + (w + 1) // 2, center + (h + 1) // 2]

    draw.rectangle(centered_box(max_box_w, max_box_h), outline=(224, 74, 74), width=3)
    draw.rectangle(centered_box(median_w, median_h), outline=(46, 148, 88), width=3)
    draw.rectangle(centered_box(min_box_w, min_box_h), outline=(120, 120, 120), width=2)
    draw.line((center, 20, center, size - 20), fill=(180, 180, 180), width=1)
    draw.line((20, center, size - 20, center), fill=(180, 180, 180), width=1)

    text_lines = [
        f"n={len(records)}",
        f"width {width_summary['min']:.0f}-{width_summary['max']:.0f}px, cv={width_summary['cv']:.2f}",
        f"height {height_summary['min']:.0f}-{height_summary['max']:.0f}px, cv={height_summary['cv']:.2f}",
        f"area cv={area_summary['cv']:.2f}",
        "red=max envelope, green=median, gray=min",
    ]
    y = 10
    for line in text_lines:
        draw.text((10, y), line, fill=(35, 35, 35), font=font)
        y += 14

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)

    metrics = {
        "count": len(records),
        "width": width_summary,
        "height": height_summary,
        "area": area_summary,
        "glyphs": records,
        "interpretation": {
            "width_cv": "lower is more size-consistent",
            "height_cv": "lower is more size-consistent",
            "area_cv": "lower is more ink-area-consistent",
        },
    }
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--canvas-size", type=int, default=512)
    parser.add_argument("--prefer-blue", action="store_true", help="Detect blue pen ink instead of generic dark ink")
    args = parser.parse_args()
    make_overlay(args.images, args.out, args.metrics, args.canvas_size, args.prefer_blue)


if __name__ == "__main__":
    main()
