#!/usr/bin/env python3
"""Segment blank-paper handwriting into individual glyph crops.

This helper is intended for isolated free-practice characters, not dense
continuous writing. It detects ink, lightly dilates it so disconnected strokes
within one character become one component, saves one crop per component, and
writes a manifest plus an optional debug image.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps


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


def detect_ink(img: Image.Image, prefer_blue: bool) -> np.ndarray:
    rgb = np.array(img.convert("RGB"))
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    if prefer_blue:
        return (b > 70) & (b > r + 18) & (b > g + 4) & (r < 180) & (g < 205)

    gray_img = ImageOps.autocontrast(img.convert("L"))
    gray = np.array(gray_img)
    threshold = otsu_threshold(gray)
    return gray <= threshold


def connected_components(mask: np.ndarray, min_pixels: int) -> list[tuple[int, int, int, int, int]]:
    h, w = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    components: list[tuple[int, int, int, int, int]] = []
    ys, xs = np.where(mask)

    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue

        queue: deque[tuple[int, int]] = deque([(start_y, start_x)])
        visited[start_y, start_x] = True
        min_y = max_y = start_y
        min_x = max_x = start_x
        count = 0

        while queue:
            y, x = queue.popleft()
            count += 1
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_x = min(min_x, x)
            max_x = max(max_x, x)

            for ny in (y - 1, y, y + 1):
                for nx in (x - 1, x, x + 1):
                    if ny == y and nx == x:
                        continue
                    if ny < 0 or nx < 0 or ny >= h or nx >= w:
                        continue
                    if visited[ny, nx] or not mask[ny, nx]:
                        continue
                    visited[ny, nx] = True
                    queue.append((ny, nx))

        if count >= min_pixels:
            components.append((min_x, min_y, max_x + 1, max_y + 1, count))

    return components


def sort_reading_order(boxes: list[dict[str, object]]) -> list[dict[str, object]]:
    if not boxes:
        return []
    heights = [int(b["box"][3]) - int(b["box"][1]) for b in boxes]
    row_tolerance = max(24, int(np.median(heights) * 0.6))
    boxes = sorted(boxes, key=lambda b: (int(b["box"][1]), int(b["box"][0])))
    rows: list[list[dict[str, object]]] = []
    for box in boxes:
        y_center = (int(box["box"][1]) + int(box["box"][3])) // 2
        placed = False
        for row in rows:
            row_center = int(np.mean([(int(b["box"][1]) + int(b["box"][3])) // 2 for b in row]))
            if abs(y_center - row_center) <= row_tolerance:
                row.append(box)
                placed = True
                break
        if not placed:
            rows.append([box])

    ordered: list[dict[str, object]] = []
    for row_index, row in enumerate(rows, start=1):
        row = sorted(row, key=lambda b: int(b["box"][0]))
        for col_index, box in enumerate(row, start=1):
            box["row"] = row_index
            box["col"] = col_index
            ordered.append(box)
    return ordered


def segment(
    image_path: Path,
    out_dir: Path,
    prefer_blue: bool,
    dilation_size: int,
    min_pixels: int,
    padding: int,
    debug: Path | None,
) -> None:
    if dilation_size % 2 == 0:
        raise ValueError("--dilation-size must be odd")

    img = Image.open(image_path).convert("RGB")
    ink = detect_ink(img, prefer_blue=prefer_blue)
    dilated = Image.fromarray((ink * 255).astype(np.uint8), "L").filter(
        ImageFilter.MaxFilter(dilation_size)
    )
    components = connected_components(np.array(dilated) > 0, min_pixels=min_pixels)

    w, h = img.size
    pending: list[tuple[dict[str, object], Image.Image]] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, (x0, y0, x1, y1, component_pixels) in enumerate(components, start=1):
        x0p = max(0, x0 - padding)
        y0p = max(0, y0 - padding)
        x1p = min(w, x1 + padding)
        y1p = min(h, y1 + padding)
        crop = img.crop((x0p, y0p, x1p, y1p))
        ink_pixels = int(ink[y0:y1, x0:x1].sum())
        if ink_pixels < max(10, min_pixels // 8):
            continue
        pending.append(
            (
                {
                    "id": f"candidate_{idx:03d}",
                    "file": "",
                    "box": [x0p, y0p, x1p, y1p],
                    "ink_box": [x0, y0, x1, y1],
                    "ink_pixels": ink_pixels,
                    "component_pixels": int(component_pixels),
                },
                crop,
            )
        )

    ordered_records = sort_reading_order([record for record, _ in pending])
    crop_by_candidate = {str(record["id"]): crop for record, crop in pending}
    records: list[dict[str, object]] = []
    for new_idx, record in enumerate(ordered_records, start=1):
        candidate_id = str(record["id"])
        new_name = f"glyph_{new_idx:03d}.png"
        record["id"] = new_name.removesuffix(".png")
        record["file"] = new_name
        record["_candidate_id"] = candidate_id
        records.append(record)

    for record in records:
        old_candidate_id = str(record.pop("_candidate_id"))
        crop = crop_by_candidate.get(old_candidate_id)
        if crop is None:
            continue
        crop.save(out_dir / str(record["file"]))

    manifest = {
        "source": str(image_path),
        "prefer_blue": prefer_blue,
        "dilation_size": dilation_size,
        "min_pixels": min_pixels,
        "padding": padding,
        "count": len(records),
        "glyphs": records,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if debug:
        dbg = img.copy()
        draw = ImageDraw.Draw(dbg)
        for record in records:
            box = [int(v) for v in record["box"]]
            draw.rectangle(box, outline=(224, 74, 74), width=4)
            draw.text((box[0] + 4, max(0, box[1] - 14)), str(record["id"]), fill=(224, 74, 74))
        debug.parent.mkdir(parents=True, exist_ok=True)
        dbg.save(debug)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prefer-blue", action="store_true")
    parser.add_argument("--dilation-size", type=int, default=31)
    parser.add_argument("--min-pixels", type=int, default=80)
    parser.add_argument("--padding", type=int, default=18)
    parser.add_argument("--debug", type=Path, default=None)
    args = parser.parse_args()
    segment(
        image_path=args.image,
        out_dir=args.out,
        prefer_blue=args.prefer_blue,
        dilation_size=args.dilation_size,
        min_pixels=args.min_pixels,
        padding=args.padding,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
