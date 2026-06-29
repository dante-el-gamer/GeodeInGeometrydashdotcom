#!/usr/bin/env python3
"""Final approach: find disconnected cores at very high alpha, dilate to include edges."""
import numpy as np
from PIL import Image


def find_components(mask):
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if visited[y, x] or not mask[y, x]:
                continue
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
            comps.append((x1, y1, x2, y2))
    return comps


def dilate_once(mask):
    h, w = mask.shape
    result = mask.copy()
    result[1:-1, 1:-1] = (
        mask[1:-1, 1:-1]
        | mask[:-2, 1:-1] | mask[2:, 1:-1]
        | mask[1:-1, :-2] | mask[1:-1, 2:]
        | mask[:-2, :-2] | mask[:-2, 2:]
        | mask[2:, :-2] | mask[2:, 2:]
    )
    return result


def find_bboxes_from_mask(mask, h, w, min_side=4, min_area=16):
    comps = find_components(mask)
    comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
             if (x2 - x1 + 1) >= min_side and (y2 - y1 + 1) >= min_side
             and (x2 - x1 + 1) * (y2 - y1 + 1) >= min_area]
    return comps


img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Try: find cores at alpha > 240, dilate N times, then find components
for threshold in [240, 250, 252, 254]:
    core = alpha > threshold
    for nd in range(0, 4):
        mask = core.copy()
        for _ in range(nd):
            mask = dilate_once(mask)
        comps = find_bboxes_from_mask(mask, h, w, min_side=4, min_area=16)
        comps.sort(key=lambda r: (r[1], r[0]))
        print(f"  thresh>{threshold} dilate{nd}: {len(comps)} comps")
        if len(comps) >= 85 and len(comps) <= 100:
            print("  ^^^ CANDIDATE ^^^")

# Best candidate: show details
print("\n\nBest candidate: alpha > 250, dilate 1")
core = alpha > 250
mask = dilate_once(core)
comps = find_bboxes_from_mask(mask, h, w, min_side=4, min_area=16)
comps.sort(key=lambda r: (r[1], r[0]))
print(f"Total: {len(comps)} sprites")
for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Also show alpha>254, dilate 2
print("\n\nCandidate: alpha > 254, dilate 2")
core = alpha > 254
mask = core.copy()
for _ in range(2):
    mask = dilate_once(mask)
comps = find_bboxes_from_mask(mask, h, w, min_side=4, min_area=16)
comps.sort(key=lambda r: (r[1], r[0]))
print(f"Total: {len(comps)} sprites")
for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")
