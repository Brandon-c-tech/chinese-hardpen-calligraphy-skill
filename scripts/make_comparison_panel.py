#!/usr/bin/env python3
"""Create a visual comparison panel for calligraphy diagnosis.

With an exemplar, the panel contains exemplar, user writing, and overlay. Without
an exemplar, it contains the raw user crop and a normalized user crop. Short
green/red labels can be added to make the panel useful inside a final report.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from make_overlay import fit_to_canvas, load_mask


def contain_on_white(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img = ImageOps.contain(img, (size - 24, size - 24))
    canvas = Image.new("RGB", (size, size), "white")
    x = (size - img.size[0]) // 2
    y = (size - img.size[1]) // 2
    canvas.paste(img, (x, y))
    return canvas


def normalized_ink(path: Path, size: int) -> Image.Image:
    mask = fit_to_canvas(load_mask(path), size=size, margin=size // 12)
    rgb = np.full((size, size, 3), 255, dtype=np.uint8)
    rgb[mask] = [35, 35, 35]
    return Image.fromarray(rgb, "RGB")


def overlay_image(exemplar: Path, user: Path, size: int) -> Image.Image:
    exemplar_mask = fit_to_canvas(load_mask(exemplar), size=size, margin=size // 12)
    user_mask = fit_to_canvas(load_mask(user), size=size, margin=size // 12)
    rgb = np.full((size, size, 3), 255, dtype=np.uint8)
    rgb[exemplar_mask & ~user_mask] = [54, 109, 220]
    rgb[user_mask & ~exemplar_mask] = [224, 74, 74]
    rgb[exemplar_mask & user_mask] = [35, 35, 35]
    return Image.fromarray(rgb, "RGB")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    if not text:
        return []
    words = text.split()
    if len(words) <= 1:
        words = list(text)
    lines: list[str] = []
    current = ""
    for word in words:
        separator = "" if len(words) > 8 and " " not in text else " "
        candidate = word if not current else current + separator + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_label(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int] = (30, 30, 30),
) -> None:
    x0, y0, x1, _ = box
    bbox = draw.textbbox((0, 0), text, font=font)
    x = x0 + (x1 - x0 - (bbox[2] - bbox[0])) // 2
    draw.text((x, y0), text, fill=fill, font=font)


def draw_note(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    label: str,
    text: str,
    color: tuple[int, int, int],
    font: ImageFont.ImageFont,
) -> int:
    if not text:
        return y
    draw.rectangle([x, y, x + 10, y + 10], fill=color)
    draw.text((x + 18, y - 2), label, fill=color, font=font)
    y += 18
    for line in wrap_text(draw, text, font, width - 12):
        draw.text((x, y), line, fill=(35, 35, 35), font=font)
        y += 14
    return y + 8


def make_panel(
    user: Path,
    out: Path,
    exemplar: Path | None,
    title: str,
    good: str,
    issue: str,
    size: int,
) -> None:
    font = ImageFont.load_default()
    title_h = 36
    label_h = 24
    note_h = 118
    gap = 16
    cols = 3 if exemplar else 2
    width = cols * size + (cols + 1) * gap
    height = title_h + label_h + size + note_h + gap * 3
    panel = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(panel)

    draw.text((gap, 10), title, fill=(30, 30, 30), font=font)

    images: list[tuple[str, Image.Image]] = []
    if exemplar:
        images.append(("Exemplar", contain_on_white(exemplar, size)))
        images.append(("User", contain_on_white(user, size)))
        images.append(("Overlay: blue exemplar, red user", overlay_image(exemplar, user, size)))
    else:
        images.append(("User crop", contain_on_white(user, size)))
        images.append(("Normalized user glyph", normalized_ink(user, size)))

    y_label = title_h + gap
    y_img = y_label + label_h
    for idx, (label, img) in enumerate(images):
        x = gap + idx * (size + gap)
        draw_centered_label(draw, (x, y_label, x + size, y_label + label_h), label, font)
        panel.paste(img, (x, y_img))
        draw.rectangle([x, y_img, x + size - 1, y_img + size - 1], outline=(220, 220, 220))

    y_note = y_img + size + gap
    x_note = gap
    note_width = width - 2 * gap
    y_note = draw_note(draw, x_note, y_note, note_width, "Keep", good, (46, 148, 88), font)
    draw_note(draw, x_note, y_note, note_width, "Fix", issue, (224, 74, 74), font)

    out.parent.mkdir(parents=True, exist_ok=True)
    panel.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("user", type=Path)
    parser.add_argument("--exemplar", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--title", default="Chinese hard-pen calligraphy comparison")
    parser.add_argument("--good", default="")
    parser.add_argument("--issue", default="")
    parser.add_argument("--size", type=int, default=300)
    args = parser.parse_args()
    make_panel(args.user, args.out, args.exemplar, args.title, args.good, args.issue, args.size)


if __name__ == "__main__":
    main()
