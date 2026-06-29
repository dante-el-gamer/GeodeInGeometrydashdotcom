#!/usr/bin/env python3
"""Multi-pass morphological separation + overlap merging for sprite detection."""

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


def erode_once(mask):
    """3x3 erosion (8-neighbor)."""
    result = mask.copy()
    result[1:-1, 1:-1] = (
        mask[1:-1, 1:-1]
        & mask[:-2, 1:-1] & mask[2:, 1:-1]
        & mask[1:-1, :-2] & mask[1:-1, 2:]
        & mask[:-2, :-2] & mask[:-2, 2:]
        & mask[2:, :-2] & mask[2:, 2:]
    )
    result[0, :] = False
    result[-1, :] = False
    result[:, 0] = False
    result[:, -1] = False
    return result


def merge_overlapping(comps):
    """Merge overlapping bounding boxes iteratively until stable."""
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
                # Check overlap
                if not (x2 < ax1 or x1 > ax2 or y2 < ay1 or y1 > ay2):
                    # Merge
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

# Strategy: multi-pass erosion to break connections
# Start with alpha > 0 mask, erode N times
for n_erode in range(1, 6):
    mask = alpha > 0
    for _ in range(n_erode):
        mask = erode_once(mask)
    comps = find_components(mask)
    comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
             if (x2 - x1 + 1) * (y2 - y1 + 1) >= 16]
    comps = merge_overlapping(comps)
    print(f"Erode x{n_erode}: {len(comps)} components (merged)")

# Now pick the best erosion level and use it for the final recovery
# Target: 90+ components, close to 91
print("\nBest approach: erode x4 + merge")
mask = alpha > 0
for _ in range(4):
    mask = erode_once(mask)

comps = find_components(mask)
comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= 16]
comps = merge_overlapping(comps)
comps.sort(key=lambda r: (r[1], r[0]))

# Dilate bounding boxes by 4 pixels to compensate for erosion
DILATE = 4
comps = [(max(0, x1-DILATE), max(0, y1-DILATE),
          min(arr.shape[1]-1, x2+DILATE), min(arr.shape[0]-1, y2+DILATE))
         for (x1, y1, x2, y2) in comps]

# Re-sort after expansion (bboxes might shift in ordering slightly)
comps.sort(key=lambda r: (r[1], r[0]))

print(f"\nFinal: {len(comps)} sprites after dilation:")
for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")
