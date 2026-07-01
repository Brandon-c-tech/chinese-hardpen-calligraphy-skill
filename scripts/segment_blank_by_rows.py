#!/usr/bin/env python3
"""Segment isolated blank-paper handwriting by rows and in-row projection.

This helper is for repeated-character practice on blank paper. It first detects
ink, groups ink into writing rows, then splits each row into glyph boxes by
horizontal projection. This works better than raw connected components for
Chinese handwriting because characters such as 心, 小, 六, and 尔 contain
disconnected dots and strokes.

OCR may be useful as a row hint, but this script does not depend on OCR.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


@dataclass
class Box:
    id: str
    x0: int
    y0: int
    x1: int
    y1: int
    label: str = ""
    row: int | None = None

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    def padded(self, pad: int, image_width: int, image_height: int) -> "Box":
        return Box(
            self.id,
            max(0, self.x0 - pad),
            max(0, self.y0 - pad),
            min(image_width, self.x1 + pad),
            min(image_height, self.y1 + pad),
            self.label,
            self.row,
        )

    def to_record(self, file_name: str, crop_box: "Box", ink_pixels: int) -> dict[str, object]:
        return {
            "id": self.id,
            "file": file_name,
            "label": self.label,
            "row": self.row,
            "ink_box": [self.x0, self.y0, self.x1, self.y1],
            "crop_box": [crop_box.x0, crop_box.y0, crop_box.x1, crop_box.y1],
            "ink_pixels": ink_pixels,
        }


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass
    return ImageFont.load_default()


FONT_SMALL = load_font(24)
FONT_MEDIUM = load_font(34)


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


def blue_ink_mask(img: Image.Image) -> np.ndarray:
    rgb = np.array(img.convert("RGB"))
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    return (b > 60) & (b > r + 20) & (b > g + 5) & (r < 190) & (g < 220)


def dark_ink_mask(img: Image.Image) -> np.ndarray:
    gray_img = ImageOps.autocontrast(img.convert("L"))
    gray = np.array(gray_img)
    return gray <= otsu_threshold(gray)


def detect_ink(img: Image.Image, mode: str) -> tuple[np.ndarray, str]:
    if mode == "blue":
        return blue_ink_mask(img), "blue"
    if mode == "dark":
        return dark_ink_mask(img), "dark"

    blue = blue_ink_mask(img)
    # If the page has enough blue ink, prefer color detection. It avoids page
    # shadows and gray dust better than grayscale thresholding.
    if int(blue.sum()) >= max(500, img.size[0] * img.size[1] // 3000):
        return blue, "blue"
    return dark_ink_mask(img), "dark"


def expand_1d(values: np.ndarray, bridge: int) -> np.ndarray:
    if bridge <= 1:
        return values.astype(bool)
    kernel = np.ones(int(bridge), dtype=np.int16)
    return np.convolve(values.astype(np.int16), kernel, mode="same") > 0


def find_runs(values: np.ndarray) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    inside = False
    start = 0
    for idx, present in enumerate(list(values.astype(bool)) + [False]):
        if present and not inside:
            start = idx
            inside = True
        elif inside and not present:
            runs.append((start, idx))
            inside = False
    return runs


def ink_bbox(mask: np.ndarray, x_offset: int = 0, y_offset: int = 0) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return (
        int(xs.min() + x_offset),
        int(ys.min() + y_offset),
        int(xs.max() + 1 + x_offset),
        int(ys.max() + 1 + y_offset),
    )


def keep_candidate(box: Box, ink_pixels: int, min_ink: int, image_height: int) -> bool:
    if ink_pixels < min_ink:
        return False
    # Common scan marks: date/number in the top-left and signature/page number
    # near the bottom-right should not become glyph candidates.
    if box.y0 < 90 and box.x1 < 250:
        return False
    if box.y0 > image_height * 0.85:
        return False
    if box.width < 12 or box.height < 12:
        return False
    if box.width > 380 or box.height > 300:
        return False
    return True


def detect_rows(mask: np.ndarray, row_min_ink: int, row_bridge: int, padding: int) -> list[Box]:
    image_height, image_width = mask.shape
    row_presence = mask.sum(axis=1) >= row_min_ink
    row_presence = expand_1d(row_presence, row_bridge)
    rows: list[Box] = []
    for y0, y1 in find_runs(row_presence):
        bbox = ink_bbox(mask[y0:y1], y_offset=y0)
        if bbox is None:
            continue
        x0, ink_y0, x1, ink_y1 = bbox
        row = Box(
            f"row_{len(rows) + 1:02d}",
            max(0, x0 - padding),
            max(0, ink_y0 - padding),
            min(image_width, x1 + padding),
            min(image_height, ink_y1 + padding),
            row=len(rows) + 1,
        )
        if row.width < 50 or row.height < 20:
            continue
        if row.y0 > image_height * 0.85:
            continue
        rows.append(row)
    return rows


def split_rows(
    mask: np.ndarray,
    rows: list[Box],
    x_bridge: int,
    min_ink: int,
) -> list[Box]:
    image_height = mask.shape[0]
    glyphs: list[Box] = []
    for row_index, row in enumerate(rows, start=1):
        row_mask = mask[row.y0 : row.y1, row.x0 : row.x1]
        x_presence = row_mask.sum(axis=0) > 0
        x_presence = expand_1d(x_presence, x_bridge)
        for x0, x1 in find_runs(x_presence):
            sub = mask[row.y0 : row.y1, row.x0 + x0 : row.x0 + x1]
            bbox = ink_bbox(sub, x_offset=row.x0 + x0, y_offset=row.y0)
            if bbox is None:
                continue
            box = Box(f"glyph_{len(glyphs) + 1:03d}", *bbox, row=row_index)
            ink_pixels = int(mask[box.y0 : box.y1, box.x0 : box.x1].sum())
            if not keep_candidate(box, ink_pixels, min_ink, image_height):
                continue
            glyphs.append(Box(f"glyph_{len(glyphs) + 1:03d}", *bbox, row=row_index))
    return sort_glyphs(glyphs)


def sort_glyphs(glyphs: list[Box]) -> list[Box]:
    rows: dict[int, list[Box]] = {}
    for glyph in glyphs:
        rows.setdefault(glyph.row or 0, []).append(glyph)
    ordered: list[Box] = []
    for row_index in sorted(rows):
        for glyph in sorted(rows[row_index], key=lambda g: g.x0):
            glyph.id = f"glyph_{len(ordered) + 1:03d}"
            ordered.append(glyph)
    return ordered


def parse_expected_rows(text: str | None, file_path: Path | None) -> list[list[str]]:
    if file_path:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [list(str(row)) if isinstance(row, str) else [str(v) for v in row] for row in data]
        if isinstance(data, dict) and isinstance(data.get("rows"), list):
            return [
                list(str(row)) if isinstance(row, str) else [str(v) for v in row]
                for row in data["rows"]
            ]
        raise ValueError("--expected-rows-file must contain a list or {'rows': [...]}")

    if not text:
        return []
    return [list(row.strip()) for row in text.split(";") if row.strip()]


def assign_labels(glyphs: list[Box], expected_rows: list[list[str]]) -> None:
    if not expected_rows:
        return
    by_row: dict[int, list[Box]] = {}
    for glyph in glyphs:
        by_row.setdefault(glyph.row or 0, []).append(glyph)
    for row_index, expected in enumerate(expected_rows, start=1):
        row_glyphs = sorted(by_row.get(row_index, []), key=lambda g: g.x0)
        for glyph, label in zip(row_glyphs, expected):
            glyph.label = label


def safe_label(label: str) -> str:
    cleaned = "".join(ch for ch in label if ch not in '/\\:*?"<>|').strip()
    return cleaned[:12] or "unknown"


def save_outputs(
    img: Image.Image,
    mask: np.ndarray,
    glyphs: list[Box],
    rows: list[Box],
    out_dir: Path,
    params: dict[str, object],
    padding: int,
    debug: Path | None,
    contact_sheet: Path | None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    image_width, image_height = img.size

    for index, glyph in enumerate(glyphs, start=1):
        label = safe_label(glyph.label) if glyph.label else f"{index:03d}"
        file_name = f"{index:03d}_{label}.png" if glyph.label else f"{index:03d}.png"
        crop_box = glyph.padded(padding, image_width, image_height)
        crop = img.crop((crop_box.x0, crop_box.y0, crop_box.x1, crop_box.y1))
        crop.save(out_dir / file_name)
        ink_pixels = int(mask[glyph.y0 : glyph.y1, glyph.x0 : glyph.x1].sum())
        records.append(glyph.to_record(file_name, crop_box, ink_pixels))

    manifest = {
        "source": str(params["source"]),
        "count": len(records),
        "params": params,
        "rows": [
            {
                "id": row.id,
                "row": row.row,
                "box": [row.x0, row.y0, row.x1, row.y1],
            }
            for row in rows
        ],
        "glyphs": records,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if debug:
        dbg = img.copy()
        draw = ImageDraw.Draw(dbg)
        for row in rows:
            draw.rectangle([row.x0, row.y0, row.x1, row.y1], outline=(122, 93, 255), width=3)
            draw.text((row.x0, max(0, row.y0 - 30)), row.id, fill=(122, 93, 255), font=FONT_SMALL)
        for glyph in glyphs:
            crop_box = glyph.padded(padding, image_width, image_height)
            draw.rectangle([crop_box.x0, crop_box.y0, crop_box.x1, crop_box.y1], outline=(28, 151, 92), width=4)
            label = glyph.label or glyph.id
            draw.text((crop_box.x0, max(0, crop_box.y0 - 30)), label, fill=(28, 151, 92), font=FONT_SMALL)
        draw.rectangle([0, 0, min(image_width, 1120), 64], fill=(255, 255, 255))
        draw.text((18, 14), f"row projection segmentation | glyphs={len(glyphs)}", fill=(20, 24, 32), font=FONT_MEDIUM)
        debug.parent.mkdir(parents=True, exist_ok=True)
        dbg.save(debug)

    if contact_sheet:
        make_contact_sheet(img, glyphs, contact_sheet, padding=padding)


def make_contact_sheet(
    img: Image.Image,
    glyphs: list[Box],
    out: Path,
    padding: int,
    thumb: int = 128,
    cols: int = 9,
) -> None:
    if not glyphs:
        raise ValueError("No glyphs to place in contact sheet")
    cell_w = thumb + 34
    cell_h = thumb + 58
    rows = math.ceil(len(glyphs) / cols)
    header = 70
    sheet = Image.new("RGB", (cols * cell_w + 24, header + rows * cell_h + 20), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 18), f"blank-paper row segmentation | crops={len(glyphs)}", fill=(20, 24, 32), font=FONT_MEDIUM)
    image_width, image_height = img.size

    for index, glyph in enumerate(glyphs):
        crop_box = glyph.padded(padding, image_width, image_height)
        crop = img.crop((crop_box.x0, crop_box.y0, crop_box.x1, crop_box.y1)).copy()
        crop.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
        x = 12 + (index % cols) * cell_w
        y = header + (index // cols) * cell_h
        tile = Image.new("RGB", (thumb, thumb), (248, 248, 248))
        tile.paste(crop, ((thumb - crop.width) // 2, (thumb - crop.height) // 2))
        sheet.paste(tile, (x, y))
        label = glyph.label or f"{index + 1:02d}"
        draw.text((x, y + thumb + 4), label, fill=(20, 24, 32), font=FONT_SMALL)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ink-mode", choices=["auto", "blue", "dark"], default="auto")
    parser.add_argument("--row-min-ink", type=int, default=8)
    parser.add_argument("--row-bridge", type=int, default=11)
    parser.add_argument("--x-bridge", type=int, default=27)
    parser.add_argument("--min-ink", type=int, default=60)
    parser.add_argument("--padding", type=int, default=14)
    parser.add_argument(
        "--expected-rows",
        default=None,
        help="Optional semicolon-separated row labels, e.g. '下下下;之之之心心'.",
    )
    parser.add_argument(
        "--expected-rows-file",
        type=Path,
        default=None,
        help="Optional JSON list of expected row labels, or {'rows': [...]}.",
    )
    parser.add_argument("--debug", type=Path, default=None)
    parser.add_argument("--contact-sheet", type=Path, default=None)
    args = parser.parse_args()

    img = Image.open(args.image).convert("RGB")
    mask, resolved_mode = detect_ink(img, args.ink_mode)
    rows = detect_rows(mask, row_min_ink=args.row_min_ink, row_bridge=args.row_bridge, padding=args.padding)
    glyphs = split_rows(
        mask,
        rows,
        x_bridge=args.x_bridge,
        min_ink=args.min_ink,
    )
    expected_rows = parse_expected_rows(args.expected_rows, args.expected_rows_file)
    assign_labels(glyphs, expected_rows)

    params = {
        "source": str(args.image),
        "ink_mode": args.ink_mode,
        "resolved_ink_mode": resolved_mode,
        "row_min_ink": args.row_min_ink,
        "row_bridge": args.row_bridge,
        "x_bridge": args.x_bridge,
        "min_ink": args.min_ink,
        "padding": args.padding,
        "expected_rows": expected_rows,
    }
    save_outputs(img, mask, glyphs, rows, args.out, params, args.padding, args.debug, args.contact_sheet)


if __name__ == "__main__":
    main()
