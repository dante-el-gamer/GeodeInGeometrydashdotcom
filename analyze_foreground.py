#!/usr/bin/env python3
"""Smart sprite recovery: detect, classify background, remove, then recover remaining."""
import json
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


def dilate(mask, n=1):
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
    return result


# Load image
img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Step 1: Find ALL components at alpha > 200 (near-opaque cores only)
core_mask = alpha > 200
comps = find_components(core_mask)
comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= 50]
print(f"Initial alpha>200 components (area>=50): {len(comps)}")

# Step 2: Classify background elements
# Background: very large areas (> 10000 px²) or very wide/tall elements
BG_AREA = 8000  # Background minimum area
BG_WIDTH = 400  # Background minimum width
BG_HEIGHT = 300  # Background minimum height

background_ids = set()
foreground = []
for i, (x1, y1, x2, y2) in enumerate(comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    area = fw * fh
    is_bg = (area >= BG_AREA) or (fw >= BG_WIDTH) or (fh >= BG_HEIGHT)
    if is_bg:
        background_ids.add(i)
        print(f"  BG [{i:>2}]: ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3} area={area}")
    else:
        foreground.append((x1, y1, x2, y2))
        print(f"  FG [{i:>2}]: ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3} area={area}")

print(f"\nBackground: {len(background_ids)}, Foreground: {len(foreground)}")

# Step 3: Remove background from alpha mask, then dilate to restore sprites
fg_mask = core_mask.copy()
for x1, y1, x2, y2 in foreground:
    pass  # foreground is already the non-background components

# Actually, let's create a mask of ONLY foreground
fg_only = np.zeros_like(core_mask)
for x1, y1, x2, y2 in foreground:
    fg_only[y1:y2+1, x1:x2+1] = core_mask[y1:y2+1, x1:x2+1]

# Dilate to include soft edges
fg_dilated = dilate(fg_only, 2)

# Re-find components on the dilated foreground mask
fg_comps = find_components(fg_dilated)
fg_comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in fg_comps
            if (x2 - x1 + 1) * (y2 - y1 + 1) >= 50]
print(f"Foreground components after dilation: {len(fg_comps)}")
fg_comps.sort(key=lambda r: (r[1], r[0]))

for i, (x1, y1, x2, y2) in enumerate(fg_comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Step 4: Also try adding back the glow sprites using a lower threshold
glow_mask = (alpha > 0) & ~core_mask  # pixels with alpha 1-200
# Find glow components that don't overlap with existing foreground
glow_comps = find_components(glow_mask)
glow_comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in glow_comps
              if (x2 - x1 + 1) * (y2 - y1 + 1) >= 100]  # min size for glow
print(f"\nGlow/soft-only components (alpha 1-200, area>=100): {len(glow_comps)}")
glow_comps.sort(key=lambda r: (r[1], r[0]))
for i, (x1, y1, x2, y2) in enumerate(glow_comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Check if glow components overlap with foreground
for gx1, gy1, gx2, gy2 in glow_comps:
    for fx1, fy1, fx2, fy2 in fg_comps:
        if not (gx2 < fx1 or gx1 > fx2 or gy2 < fy1 or gy1 > fy2):
            print(f"  OVERLAP: glow ({gx1},{gy1},{gx2-gx1+1}x{gy2-gy1+1}) overlaps fg ({fx1},{fy1},{fx2-fx1+1}x{fy2-fy1+1})")
