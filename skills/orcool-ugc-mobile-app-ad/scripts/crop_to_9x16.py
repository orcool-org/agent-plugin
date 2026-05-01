#!/usr/bin/env python3
"""
Crop any image to 9:16 vertical (1080x1920) centered on the visually important
region. Default: center crop. If you know the subject is off-center, pass
--center-x <px>.

Usage:
    python crop_to_9x16.py input.jpg output.jpg [--center-x 3050]
"""
import argparse
from PIL import Image


def crop_to_9x16(input_path: str, output_path: str, center_x: int | None = None,
                 target_w: int = 1080, target_h: int = 1920, quality: int = 92):
    img = Image.open(input_path).convert("RGB")
    w, h = img.size

    # Compute 9:16 crop window at full height
    crop_w = int(h * target_w / target_h)  # = h * 9/16
    if crop_w > w:
        # Source is narrower than 9:16 — keep full width and center-crop height.
        # center_x is ignored on this branch (no horizontal slack to use).
        crop_h = int(w * target_h / target_w)  # = w * 16/9
        left, right = 0, w
        top = max(0, (h - crop_h) // 2)
        bottom = top + crop_h
    else:
        cx = center_x if center_x is not None else w // 2
        left = max(0, cx - crop_w // 2)
        right = left + crop_w
        if right > w:
            right = w
            left = w - crop_w
        top, bottom = 0, h

    cropped = img.crop((left, top, right, bottom))
    resized = cropped.resize((target_w, target_h), Image.LANCZOS)
    resized.save(output_path, "JPEG", quality=quality)
    print(f"{input_path} ({w}x{h}) → {output_path} ({target_w}x{target_h})")
    print(f"Crop box: ({left}, {top}, {right}, {bottom})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--center-x", type=int, default=None,
                   help="Horizontal center of interest in source px (default: image center)")
    args = p.parse_args()
    crop_to_9x16(args.input, args.output, args.center_x)
