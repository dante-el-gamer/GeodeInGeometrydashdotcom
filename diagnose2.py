#!/usr/bin/env python3
"""Recover GJ_WebSheet.json frame coordinates via alpha erosion + component detection.

Sprites often touch through semi-transparent AA pixels. We erode the alpha mask
before finding components, then dilate bounding boxes back to recover full rects.
"""
import json
import numpy as np
from PIL import Image


def find_bboxes(mask, min_area=4):
    """4-connected component labeling on a boolean 2D array. Returns sorted bboxes."""
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    comps = []

    for y in range(h):
        for x in range(w):
            if visited[y, x] or not mask[y, x]:
                continue
            # BFS
            x1 = x2 = x
            y1 = y2 = y
            stack = [(x, y)]
            visited[y, x] = True
            while stack:
                cx, cy = stack.pop()
                if cx < x1: x1 = cx
                if cx > x2: x2 = cx
                if cy < y1: y1 = cy
                if cy > y2: y2 = cy
                if cx > 0 and not visited[cy, cx-1] and mask[cy, cx-1]:
                    visited[cy, cx-1] = True
                    stack.append((cx-1, cy))
                if cx < w-1 and not visited[cy, cx+1] and mask[cy, cx+1]:
                    visited[cy, cx+1] = True
                    stack.append((cx+1, cy))
                if cy > 0 and not visited[cy-1, cx] and mask[cy-1, cx]:
                    visited[cy-1, cx] = True
                    stack.append((cx, cy-1))
                if cy < h-1 and not visited[cy+1, cx] and mask[cy+1, cx]:
                    visited[cy+1, cx] = True
                    stack.append((cx, cy+1))

            area = (x2 - x1 + 1) * (y2 - y1 + 1)
            comps.append((x1, y1, x2, y2, area))

    comps.sort(key=lambda r: (r[1], r[0]))  # top-to-bottom, left-to-right
    return comps


PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

# Load image, extract alpha
img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
print(f"Image: {arr.shape[1]}x{arr.shape[0]}")

# Create binary mask (alpha > 0)
mask = alpha > 0

# Erode: a pixel is kept only if all 8 neighbors also have alpha > 0
# This removes 1-pixel connections (AA bridges)
eroded = mask.copy()
eroded[1:-1, 1:-1] = (
    mask[1:-1, 1:-1]
    & mask[:-2, 1:-1] & mask[2:, 1:-1]
    & mask[1:-1, :-2] & mask[1:-1, 2:]
    & mask[:-2, :-2] & mask[:-2, 2:]
    & mask[2:, :-2] & mask[2:, 2:]
)
# Also zero out border pixels (they can't be eroded properly)
eroded[0, :] = False
eroded[-1, :] = False
eroded[:, 0] = False
eroded[:, -1] = False

# Find components on eroded mask
comps = find_bboxes(eroded)
print(f"After 1-px erosion: {len(comps)} components (area >= 4)")

# Filter: keep only with area >= some threshold to eliminate tiny noise
min_area = 16  # e.g. 4x4 minimum
comps = [c for c in comps if c[4] >= min_area]
print(f"After min_area={min_area} filter: {len(comps)} components")

# Dilate bounding boxes by 2 pixels (erosion removed 1px, plus padding)
DILATE = 2
for i, (x1, y1, x2, y2, area) in enumerate(comps):
    comps[i] = (max(0, x1 - DILATE), max(0, y1 - DILATE),
                min(arr.shape[1]-1, x2 + DILATE), min(arr.shape[0]-1, y2 + DILATE), area)

# Print large comps for diagnosis
print(f"\nAll {len(comps)} detected sprites:")
for i, (x1, y1, x2, y2, area) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}  area={area}")
