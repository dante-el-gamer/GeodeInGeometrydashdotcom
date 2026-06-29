#!/usr/bin/env python3
"""Detailed analysis of high-threshold cores, with duplicate filtering."""
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


img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
w, h = arr.shape[1], arr.shape[0]

# Use moderate threshold
mask = alpha > 128
comps = find_components(mask)

# Filter: min area 20px
min_px = 20
comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= min_px]

# Remove near-duplicates (same bbox)
uniq = {}
for c in comps:
    key = c  # exact match
    uniq[key] = uniq.get(key, 0) + 1

comps = list(uniq.keys())
print(f"Unique cores at alpha>128, min_area={min_px}: {len(comps)}")

comps.sort(key=lambda r: (r[1], r[0]))

for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Now let's check the full-alpha extent of each core
full_mask = alpha > 0
print(f"\n--- Expanding each core to full-alpha boundary ---")

# For each core, grow to include surrounding full-alpha pixels
expanded = []
for x1, y1, x2, y2 in comps:
    # Grow to include ALL connected alpha>0 pixels
    # Use BFS on full mask, but constrained by the size
    # Actually, just grow rect by rect to include adjacent full-alpha pixels
    grew = True
    while grew:
        grew = False
        if x1 > 0 and np.any(full_mask[y1:y2+1, x1-1]):
            x1 -= 1
            grew = True
        if x2 < w-1 and np.any(full_mask[y1:y2+1, x2+1]):
            x2 += 1
            grew = True
        if y1 > 0 and np.any(full_mask[y1-1, x1:x2+1]):
            y1 -= 1
            grew = True
        if y2 < h-1 and np.any(full_mask[y2+1, x1:x2+1]):
            y2 += 1
            grew = True
    expanded.append((x1, y1, x2, y2))

# Remove duplicates again
uniq2 = {}
for c in expanded:
    key = c
    uniq2[key] = uniq2.get(key, 0) + 1
expanded = list(uniq2.keys())

# Merge overlapping
merged = list(expanded)
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

merged.sort(key=lambda r: (r[1], r[0]))
print(f"After expansion + merge: {len(merged)} components")
for i, (x1, y1, x2, y2) in enumerate(merged):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")
