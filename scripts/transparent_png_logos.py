#!/usr/bin/env python3
"""Remove only dark border-connected backgrounds from owner-approved VMRX PNGs.

Preserve brand artwork; never globally replace every black pixel.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
IMAGES = (
    "assets/vmrx-logo.png",
    "assets/branding/vmrx-logo.png",
    "assets/branding/vmrx-branding-01.png",
    "assets/branding/vmrx-branding-02.png",
    "assets/branding/vmrx-branding-03.png",
)

def transparentize(path):
    with Image.open(path) as im:
        im.load()
        rgba = np.array(im.convert("RGBA"), dtype=np.uint8)
    h, w, _ = rgba.shape
    if min(w, h) < 16:
        raise ValueError(f"{path}: logo too small")
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3].copy()
    n = max(2, min(w, h) // 80)
    corners = np.concatenate((
        rgb[:n, :n].reshape(-1, 3), rgb[:n, -n:].reshape(-1, 3),
        rgb[-n:, :n].reshape(-1, 3), rgb[-n:, -n:].reshape(-1, 3),
    ))
    bg = np.median(corners, axis=0)
    if all(alpha[y, x] == 0 for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
        print(f"ALREADY TRANSPARENT {path.relative_to(ROOT)}")
        return
    if bg.max() > 110:
        raise ValueError(f"{path}: unexpected non-dark corners {bg}; refusing to erase artwork")
    distance = np.max(np.abs(rgb - bg), axis=2)
    darkness = rgb.max(axis=2)
    dark_bg = (distance <= 86) & (darkness < 128)
    seeds = np.zeros((h, w), dtype=bool)
    seeds[0, :] = seeds[-1, :] = True
    seeds[:, 0] = seeds[:, -1] = True
    connected = ndimage.binary_propagation(dark_bg & seeds, mask=dark_bg)
    count = int(connected.sum())
    if count < w*h // 1000:
        raise ValueError(f"{path}: dark border backdrop not detected")
    alpha[connected] = 0
    fringe = ndimage.binary_dilation(connected, iterations=2) & ~connected
    dark_fringe = fringe & (darkness < 150)
    graded = np.clip((distance.astype(np.float32) - 10) * 4.2, 0, 255).astype(np.uint8)
    alpha[dark_fringe] = np.minimum(alpha[dark_fringe], graded[dark_fringe])
    rgba[:, :, 3] = alpha
    if not all(alpha[y, x] == 0 for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1))):
        raise ValueError(f"{path}: corner transparency assertion failed")
    if int(np.count_nonzero(alpha > 240)) < 100:
        raise ValueError(f"{path}: too little artwork remains; refusing save")
    Image.fromarray(rgba, "RGBA").save(path, "PNG", optimize=True)
    print(f"UPDATED {path.relative_to(ROOT)} {w}x{h}: removed {count/(w*h):.1%} dark connected backdrop")

if __name__ == "__main__":
    for name in IMAGES:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        transparentize(path)
