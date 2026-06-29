#!/usr/bin/env python3
"""Morphological opening to separate touching sprites, then detect components."""
import numpy as np
from PIL import Image


def erode(mask, n=1):
    h, w = mask.shape
    result = mask.copy()
    for _ in range(n):
        prev = result.copy()
        result[1:-1, 1:-1] = (
            prev[1:-1, 1:-1]
            & prev[:-2, 1:-1] & prev[2:, 1:-1]
            & prev[1:-1, :-2] & prev[1:-1, 2:]
            & prev[:-2, :-2] & prev[:-2, 2:]
            & prev[2:, :-2] & prev[2:, 2:]
        )
        result[0, :] = False; result[-1, :] = False
        result[:, 0] = False; result[:, -1] = False
    return result


def dilate(mask, n=1):
    h, w = mask.shape
    result = mask.copy()
    for _ in range(n):
        prev = result.copy()
        result[1:-1, 1:-1] = (
            prev[1:-1, 1:-1]
            | prev[:-2, 1:-1] | prev[2:, 1:-1]
            | prev[1:-1, :-2] | prev[1:-1, 2:]
            | prev[:-2, :-2] | prev[:-2, 2:]
            | prev[2:, :-2] | prev[2:, 2:]
        )
        result[0, :] = prev[0, :]; result[-1, :] = prev[-1, :]
        result[:, 0] = prev[:, 0]; result[:, -1] = prev[:, -1]
    return result


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


def merge_overlapping(comps):
    merged = list(comps)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(merged):
            x1, y1, x2, y2 = merged[i]
            j = i + 1
            while j < len(merged):
                ax1, ay1, ax2, ay2 = merged[j]
                if not (x2 < ax1 or x1 > ax2 or y2 < ay1 or y1 > ay2):
                    x1, y1 = min(x1, ax1), min(y1, ay1)
                    x2, y2 = max(x2, ax2), max(y2, ay2)
                    merged.pop(j)
                    changed = True
                else:
                    j += 1
            merged[i] = (x1, y1, x2, y2)
            i += 1
    return merged


img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Try different opening sizes
for erode_n in range(1, 7):
    mask = alpha > 0
    mask = erode(mask, erode_n)
    mask = dilate(mask, erode_n)
    comps = find_components(mask)
    comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
             if (x2 - x1 + 1) * (y2 - y1 + 1) >= 16]
    comps = merge_overlapping(comps)
    comps.sort(key=lambda r: (r[1], r[0]))
    print(f"Opening {erode_n}: {len(comps)} components")

# Try with erode=5 (best result often near 90-100)
print("\n--- Final solution with erode=5 dilate=5 ---")
mask = alpha > 0
mask = erode(mask, 5)
mask = dilate(mask, 5)
comps = find_components(mask)
comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= 16]
comps = merge_overlapping(comps)
comps.sort(key=lambda r: (r[1], r[0]))

print(f"Total: {len(comps)} sprites")
for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")
