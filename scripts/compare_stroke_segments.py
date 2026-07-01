#!/usr/bin/env python3
"""Compare a named visible stroke across multiple glyph crops.

Input manifest example:

{
  "stroke_name": "下 top horizontal",
  "stroke_type": "horizontal",
  "exemplar": {
    "id": "xia_exemplar",
    "character": "下",
    "image": "crops/xia/exemplar.png",
    "points": [[42, 78], [128, 66]]
  },
  "items": [
    {
      "id": "xia_user_01",
      "character": "下",
      "image": "crops/xia/user_01.png",
      "points": [[34, 68], [126, 55]]
    }
  ]
}

Coordinates are pixel coordinates inside each image. The script measures segment
length, normalized length, angle, start/end position, and spread across the
cohort. When an exemplar is provided, the script also reports each user sample's
deviation from the exemplar. It compares visible final stroke traces, not stroke
order.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_font(size: int = 12) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def as_points(item: dict[str, Any]) -> list[tuple[float, float]]:
    if "points" in item:
        return [(float(p[0]), float(p[1])) for p in item["points"]]
    if "segment" in item:
        seg = item["segment"]
        if len(seg) == 4 and not isinstance(seg[0], list):
            return [(float(seg[0]), float(seg[1])), (float(seg[2]), float(seg[3]))]
        return [(float(p[0]), float(p[1])) for p in seg]
    raise ValueError(f"Missing points/segment for item {item.get('id', '')}")


def polyline_length(points: list[tuple[float, float]]) -> float:
    total = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        total += math.hypot(x1 - x0, y1 - y0)
    return total


def segment_angle(points: list[tuple[float, float]]) -> float:
    x0, y0 = points[0]
    x1, y1 = points[-1]
    # Image y grows downward; invert y so positive angle means rising to the right.
    return math.degrees(math.atan2(-(y1 - y0), x1 - x0))


def summary(values: list[float]) -> dict[str, float]:
    arr = np.array(values, dtype=np.float64)
    mean = float(arr.mean()) if len(arr) else 0.0
    std = float(arr.std(ddof=0)) if len(arr) else 0.0
    cv = float(std / abs(mean)) if mean else 0.0
    return {
        "min": float(arr.min()) if len(arr) else 0.0,
        "median": float(np.median(arr)) if len(arr) else 0.0,
        "max": float(arr.max()) if len(arr) else 0.0,
        "mean": mean,
        "std": std,
        "cv": cv,
        "range": float(arr.max() - arr.min()) if len(arr) else 0.0,
    }


def resolve_image(base_dir: Path, image_value: str) -> Path:
    path = Path(image_value)
    if path.is_absolute():
        return path
    return base_dir / path


def draw_crop_panel(
    item: dict[str, Any],
    image_path: Path,
    points: list[tuple[float, float]],
    size: int,
    font: ImageFont.ImageFont,
) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    source_w, source_h = img.size
    contained = ImageOps.contain(img, (size - 18, size - 48))
    scale = contained.size[0] / source_w
    x_offset = (size - contained.size[0]) // 2
    y_offset = 8

    canvas = Image.new("RGB", (size, size), "white")
    canvas.paste(contained, (x_offset, y_offset))
    draw = ImageDraw.Draw(canvas)

    scaled_points = [
        (int(round(x_offset + x * scale)), int(round(y_offset + y * scale))) for x, y in points
    ]
    is_exemplar = str(item.get("role", "")).lower() == "exemplar"
    stroke_color = (28, 132, 80) if is_exemplar else (224, 74, 74)
    endpoint_color = (35, 94, 168) if is_exemplar else (46, 148, 88)
    if len(scaled_points) >= 2:
        draw.line(scaled_points, fill=stroke_color, width=4)
        r = 4
        for x, y in [scaled_points[0], scaled_points[-1]]:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=endpoint_color)

    label = str(item.get("id") or Path(image_path).stem)
    if is_exemplar:
        label = f"STD {label}"
    angle = item["_metrics"]["angle_degrees"]
    length = item["_metrics"]["length_px"]
    draw.rectangle([0, size - 34, size, size], fill=(250, 251, 252))
    draw.text((6, size - 31), label[:28], fill=(35, 35, 35), font=font)
    draw.text((6, size - 16), f"len {length:.0f}px  angle {angle:.1f} deg", fill=(90, 90, 90), font=font)
    draw.rectangle([0, 0, size - 1, size - 1], outline=(220, 220, 220))
    return canvas


def draw_bar_chart(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    size: tuple[int, int],
    labels: list[str],
    values: list[float],
    title: str,
    color: tuple[int, int, int],
    font: ImageFont.ImageFont,
    reference_value: float | None = None,
) -> None:
    x0, y0 = origin
    w, h = size
    draw.text((x0, y0), title, fill=(35, 35, 35), font=font)
    plot_y = y0 + 20
    plot_h = h - 30
    if not values:
        return
    domain_values = list(values)
    if reference_value is not None:
        domain_values.append(reference_value)
    min_v = min(domain_values)
    max_v = max(domain_values)
    span = max(max_v - min_v, 1e-6)
    bar_w = max(8, int((w - 20) / len(values)) - 4)
    baseline = plot_y + plot_h
    for idx, value in enumerate(values):
        bh = int(((value - min_v) / span) * (plot_h - 18)) + 4
        bx = x0 + 10 + idx * (bar_w + 4)
        draw.rectangle([bx, baseline - bh, bx + bar_w, baseline], fill=color)
        draw.text((bx, baseline + 2), str(idx + 1), fill=(90, 90, 90), font=font)
    if reference_value is not None:
        rel = (reference_value - min_v) / span
        ref_y = baseline - int(rel * (plot_h - 18)) - 4
        draw.line([x0 + 8, ref_y, x0 + w - 8, ref_y], fill=(28, 132, 80), width=2)
        draw.text((x0 + 12, ref_y - 13), f"STD {reference_value:.2f}", fill=(28, 132, 80), font=font)
    draw.line([x0 + 6, baseline, x0 + w - 6, baseline], fill=(180, 180, 180))
    draw.text((x0 + w - 112, plot_y), f"min {min_v:.1f}", fill=(90, 90, 90), font=font)
    draw.text((x0 + w - 112, plot_y + 14), f"max {max_v:.1f}", fill=(90, 90, 90), font=font)


def compare(manifest_path: Path, out: Path, metrics_out: Path, cell_size: int, cols: int) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_dir = manifest_path.parent
    stroke_name = str(manifest.get("stroke_name", "stroke cohort"))
    stroke_type = str(manifest.get("stroke_type", "other"))
    exemplar = manifest.get("exemplar")
    items = manifest.get("items", [])
    if not items:
        raise ValueError("Manifest contains no items")

    records = []
    input_items = []
    if exemplar:
        exemplar_item = dict(exemplar)
        exemplar_item["role"] = "exemplar"
        input_items.append(exemplar_item)
    for item in items:
        user_item = dict(item)
        user_item.setdefault("role", "user")
        input_items.append(user_item)

    for item in input_items:
        item = dict(item)
        image_path = resolve_image(base_dir, str(item["image"]))
        points = as_points(item)
        img = Image.open(image_path)
        w, h = img.size
        length = polyline_length(points)
        angle = segment_angle(points)
        start_x, start_y = points[0]
        end_x, end_y = points[-1]
        diagonal = math.hypot(w, h)
        metrics = {
            "id": str(item.get("id") or image_path.stem),
            "character": str(item.get("character", "")),
            "role": str(item.get("role", "user")),
            "image": str(image_path),
            "length_px": length,
            "length_by_width": length / w if w else 0.0,
            "length_by_height": length / h if h else 0.0,
            "length_by_diagonal": length / diagonal if diagonal else 0.0,
            "angle_degrees": angle,
            "start_rel": [start_x / w if w else 0.0, start_y / h if h else 0.0],
            "end_rel": [end_x / w if w else 0.0, end_y / h if h else 0.0],
            "points": points,
        }
        item["_image_path"] = image_path
        item["_points"] = points
        item["_metrics"] = metrics
        records.append(item)

    exemplar_record = next((r for r in records if r["_metrics"]["role"] == "exemplar"), None)
    user_records = [r for r in records if r["_metrics"]["role"] != "exemplar"]

    if exemplar_record:
        exemplar_metrics = exemplar_record["_metrics"]
        for r in user_records:
            metrics = r["_metrics"]
            metrics["deviation_from_exemplar"] = {
                "angle_delta_degrees": metrics["angle_degrees"] - exemplar_metrics["angle_degrees"],
                "abs_angle_delta_degrees": abs(metrics["angle_degrees"] - exemplar_metrics["angle_degrees"]),
                "length_by_diagonal_delta": metrics["length_by_diagonal"] - exemplar_metrics["length_by_diagonal"],
                "length_by_diagonal_ratio": (
                    metrics["length_by_diagonal"] / exemplar_metrics["length_by_diagonal"]
                    if exemplar_metrics["length_by_diagonal"]
                    else 0.0
                ),
                "start_rel_delta": [
                    metrics["start_rel"][0] - exemplar_metrics["start_rel"][0],
                    metrics["start_rel"][1] - exemplar_metrics["start_rel"][1],
                ],
                "end_rel_delta": [
                    metrics["end_rel"][0] - exemplar_metrics["end_rel"][0],
                    metrics["end_rel"][1] - exemplar_metrics["end_rel"][1],
                ],
            }

    lengths = [r["_metrics"]["length_px"] for r in user_records]
    normalized_lengths = [r["_metrics"]["length_by_diagonal"] for r in user_records]
    angles = [r["_metrics"]["angle_degrees"] for r in user_records]
    start_xs = [r["_metrics"]["start_rel"][0] for r in user_records]
    end_xs = [r["_metrics"]["end_rel"][0] for r in user_records]

    font = load_font(12)
    rows = math.ceil(len(records) / cols)
    chart_h = 180
    title_h = 50
    width = cols * cell_size
    height = title_h + rows * cell_size + chart_h
    panel = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(panel)
    draw.text((12, 10), stroke_name, fill=(30, 30, 30), font=font)
    draw.text(
        (12, 26),
        f"type={stroke_type} | users={len(user_records)} | angle std={summary(angles)['std']:.1f} deg | length cv={summary(normalized_lengths)['cv']:.2f}",
        fill=(90, 90, 90),
        font=font,
    )
    if exemplar_record:
        em = exemplar_record["_metrics"]
        draw.text(
            (width - 250, 26),
            f"STD angle {em['angle_degrees']:.1f} deg | norm len {em['length_by_diagonal']:.2f}",
            fill=(28, 132, 80),
            font=font,
        )

    for idx, item in enumerate(records):
        crop_panel = draw_crop_panel(item, item["_image_path"], item["_points"], cell_size, font)
        x = (idx % cols) * cell_size
        y = title_h + (idx // cols) * cell_size
        panel.paste(crop_panel, (x, y))

    chart_y = title_h + rows * cell_size + 8
    half_w = width // 2
    reference_angle = exemplar_record["_metrics"]["angle_degrees"] if exemplar_record else None
    reference_length = exemplar_record["_metrics"]["length_by_diagonal"] if exemplar_record else None
    draw_bar_chart(
        draw,
        (12, chart_y),
        (half_w - 24, chart_h - 16),
        [r["_metrics"]["id"] for r in user_records],
        angles,
        "Angle spread (deg)",
        (54, 109, 220),
        font,
        reference_angle,
    )
    draw_bar_chart(
        draw,
        (half_w + 12, chart_y),
        (half_w - 24, chart_h - 16),
        [r["_metrics"]["id"] for r in user_records],
        normalized_lengths,
        "Normalized length spread",
        (46, 148, 88),
        font,
        reference_length,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    panel.save(out)

    deviation_summary = {}
    if exemplar_record:
        angle_deltas = [r["_metrics"]["deviation_from_exemplar"]["angle_delta_degrees"] for r in user_records]
        abs_angle_deltas = [
            r["_metrics"]["deviation_from_exemplar"]["abs_angle_delta_degrees"] for r in user_records
        ]
        length_deltas = [
            r["_metrics"]["deviation_from_exemplar"]["length_by_diagonal_delta"] for r in user_records
        ]
        length_ratios = [
            r["_metrics"]["deviation_from_exemplar"]["length_by_diagonal_ratio"] for r in user_records
        ]
        deviation_summary = {
            "angle_delta_degrees": summary(angle_deltas),
            "abs_angle_delta_degrees": summary(abs_angle_deltas),
            "length_by_diagonal_delta": summary(length_deltas),
            "length_by_diagonal_ratio": summary(length_ratios),
        }

    metrics = {
        "stroke_name": stroke_name,
        "stroke_type": stroke_type,
        "count": len(user_records),
        "exemplar": exemplar_record["_metrics"] if exemplar_record else None,
        "length_px": summary(lengths),
        "length_by_diagonal": summary(normalized_lengths),
        "angle_degrees": summary(angles),
        "start_x_rel": summary(start_xs),
        "end_x_rel": summary(end_xs),
        "deviation_from_exemplar": deviation_summary,
        "items": [r["_metrics"] for r in user_records],
        "notes": [
            "Angles use image coordinates with y inverted: positive means rising to the right.",
            "When an exemplar is present, STD marks the exemplar's visible stroke segment.",
            "This compares visible final stroke traces, not stroke order.",
        ],
    }
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--cell-size", type=int, default=220)
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()
    compare(args.manifest, args.out, args.metrics, args.cell_size, args.cols)


if __name__ == "__main__":
    main()
