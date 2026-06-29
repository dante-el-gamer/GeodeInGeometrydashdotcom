#!/usr/bin/env python3
"""Two-pass sprite detection: find cores at high alpha threshold, expand to full extent."""
import numpy as np
from PIL import Image


def find_components(mask):
    """4-connected component labeling on boolean 2D array. Returns list of (x1,y1,x2,y2)."""
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
print(f"Image: {arr.shape[1]}x{arr.shape[0]}")

# Try different thresholds to find the sweet spot
for threshold in [50, 100, 128, 150, 200, 250]:
    core = alpha > threshold
    comps = find_components(core)
    # Filter: min area 16
    comps = [c for c in comps if (c[2]-c[0]+1)*(c[3]-c[1]+1) >= 16]
    print(f"Threshold > {threshold:>3}: {len(comps):>3} components (min_area=16)")

# Now use alpha > 200 as core, expand to full alpha extent
CORE_THRESH = 200
core = alpha > CORE_THRESH
cores = find_components(core)
print(f"\nCore threshold > {CORE_THRESH}: {len(cores)} raw cores")

# Filter tiny cores
min_core_area = 16
cores = [c for c in cores if (c[2]-c[0]+1)*(c[3]-c[1]+1) >= min_core_area]
print(f"After min_area={min_core_area}: {len(cores)} cores")

# Expand each core's bounding box to include all full-alpha (>0) pixels nearby
full_mask = alpha > 0
expanded = []

for x1, y1, x2, y2 in cores:
    # Grow the box in all directions until we hit fully transparent boundaries
    grown = True
    while grown:
        grown = False
        # Try expanding left
        if x1 > 0 and np.any(full_mask[y1:y2+1, x1-1]):
            x1 -= 1
            grown = True
        # Right
        if x2 < alpha.shape[1]-1 and np.any(full_mask[y1:y2+1, x2+1]):
            x2 += 1
            grown = True
        # Up
        if y1 > 0 and np.any(full_mask[y1-1, x1:x2+1]):
            y1 -= 1
            grown = True
        # Down
        if y2 < alpha.shape[0]-1 and np.any(full_mask[y2+1, x1:x2+1]):
            y2 += 1
            grown = True

    expanded.append((x1, y1, x2, y2))

# Sort top-to-bottom, left-to-right
expanded.sort(key=lambda r: (r[1], r[0]))
print(f"\n{len(expanded)} expanded sprites:\n")
for i, (x1, y1, x2, y2) in enumerate(expanded):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Check if we got close to 90+ frames
print(f"\n{'='*40}")
print(f"Total sprites detected: {len(expanded)} (need ~90)")
