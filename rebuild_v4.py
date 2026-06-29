#!/usr/bin/env python3
"""Recovery v4: cores at alpha>200, 1px expansion, no-collision bbox shrink."""
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
            x1 = x2 = x; y1 = y2 = y
            stack = [(x, y)]
            visited[y, x] = True
            while stack:
                cx, cy = stack.pop()
                if cx < x1: x1 = cx
                if cx > x2: x2 = cx
                if cy < y1: y1 = cy
                if cy > y2: y2 = cy
                if cx > 0 and not visited[cy, cx-1] and mask[cy, cx-1]:
                    visited[cy, cx-1] = True; stack.append((cx-1, cy))
                if cx < w-1 and not visited[cy, cx+1] and mask[cy, cx+1]:
                    visited[cy, cx+1] = True; stack.append((cx+1, cy))
                if cy > 0 and not visited[cy-1, cx] and mask[cy-1, cx]:
                    visited[cy-1, cx] = True; stack.append((cx, cy-1))
                if cy < h-1 and not visited[cy+1, cx] and mask[cy+1, cx]:
                    visited[cy+1, cx] = True; stack.append((cx, cy+1))
            comps.append((x1, y1, x2, y2))
    return comps


def expand_bbox(bbox, amount, max_w, max_h):
    x1, y1, x2, y2 = bbox
    return (max(0, x1 - amount), max(0, y1 - amount),
            min(max_w - 1, x2 + amount), min(max_h - 1, y2 + amount))


def rects_overlap(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

with open(JSON) as f:
    data = json.load(f)
old_frames = data['textures'][0]['frames']
filenames = [f['filename'] for f in old_frames]
trimmed = [f['trimmed'] for f in old_frames]
rotated = [f['rotated'] for f in old_frames]

INTACT = {
    'filename': 'downloadSteam_001.png',
    'rotated': False,
    'trimmed': True,
    'sourceSize': {'w': 284, 'h': 95},
    'spriteSourceSize': {'x': 5, 'y': 5, 'w': 279, 'h': 90},
    'frame': {'x': 551, 'y': 894, 'w': 279, 'h': 90},
}
INTACT_IDX = 18

img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
H, W = alpha.shape

print("Pass 1: cores at alpha > 200 (undilated)")
core_mask = alpha > 200
cores = find_components(core_mask)
cores_with_area = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in cores
                   if (x2 - x1 + 1) >= 3 and (y2 - y1 + 1) >= 3]
print(f"  {len(cores)} raw cores, {len(cores_with_area)} >= 3px")

# Expand each core outward pixel by pixel until hitting another core's bbox or max 3px
# Also track the original core bbox for collision avoidance
MARGIN = 3  # maximum expansion
expanded = []
for cx1, cy1, cx2, cy2 in cores_with_area:
    ex1, ey1, ex2, ey2 = cx1, cy1, cx2, cy2
    # Expand outward as much as possible without overlapping any OTHER core's ORIGINAL bbox
    # First pass: try max expansion for each side
    for dx in range(1, MARGIN + 1):
        # Expand left
        nx1 = max(0, cx1 - dx)
        if nx1 >= cx1 - dx:  # didn't hit edge
            ex1 = nx1
    for dx in range(1, MARGIN + 1):
        nx2 = min(W - 1, cx2 + dx)
        if nx2 <= cx2 + dx:
            ex2 = nx2
    for dy in range(1, MARGIN + 1):
        ny1 = max(0, cy1 - dy)
        if ny1 >= cy1 - dy:
            ey1 = ny1
    for dy in range(1, MARGIN + 1):
        ny2 = min(H - 1, cy2 + dy)
        if ny2 <= cy2 + dy:
            ey2 = ny2
    expanded.append((ex1, ey1, ex2, ey2, cx1, cy1, cx2, cy2))

# Sort by area (descending) to place large components first, then by (y, x)
expanded.sort(key=lambda r: (-((r[2]-r[0]+1)*(r[3]-r[1]+1)), r[1], r[0]))

# Build exclusion mask from intact frame
ie = INTACT['frame']
excluded = np.zeros((H, W), dtype=bool)
excluded[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# Greedy placement: pick non-overlapping expanded bboxes
placed = []
skipped = 0
for ex1, ey1, ex2, ey2, cx1, cy1, cx2, cy2 in expanded:
    eb = (ex1, ey1, ex2, ey2)
    # Check no overlap with intact
    if rects_overlap(eb, (ie['x'], ie['y'], ie['x']+ie['w']-1, ie['y']+ie['h']-1)):
        skipped += 1
        continue
    # Check no overlap with already placed
    overlap = False
    for pb in placed:
        if rects_overlap(eb, pb):
            overlap = True
            break
    if overlap:
        skipped += 1
        continue
    placed.append(eb)

print(f"  Placed: {len(placed)}, skipped: {skipped}")

# Now find remaining sprites in unclaimed areas
unclaimed = np.ones((H, W), dtype=bool)
for ex1, ey1, ex2, ey2 in placed:
    unclaimed[ey1:ey2+1, ex1:ex2+1] = False
unclaimed[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = False

# Pass 2: components in unclaimed areas at alpha > 32
soft_mask = (alpha > 32) & unclaimed
p2 = find_components(soft_mask)
p2 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p2
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]
print(f"Pass 2 (soft): {len(p2)} components")

# Pass 3: tiny in remaining unclaimed alpha > 0
for x1, y1, x2, y2 in p2:
    unclaimed[y1:y2+1, x1:x2+1] = False
tiny_mask = (alpha > 0) & unclaimed
p3 = find_components(tiny_mask)
p3 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p3
      if (x2 - x1 + 1) >= 2 and (y2 - y1 + 1) >= 2]
print(f"Pass 3 (tiny): {len(p3)} components")

# Combine all components, placed first then p2 then p3
all_placed = placed + p2 + p3
print(f"Total: {len(all_placed)} components for {len(filenames)} frames")

# Map to frames — components already non-overlapping, consume in order
used = [False] * len(all_placed)
new_frames = []
missing = 0

for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(INTACT)
        print(f"  [{i:>2}] KEPT  {filenames[i]}")
        continue
    found = False
    for ci in range(len(all_placed)):
        if used[ci]:
            continue
        used[ci] = True
        x1, y1, x2, y2 = all_placed[ci]
        fw, fh = x2 - x1 + 1, y2 - y1 + 1
        new_frames.append({
            'filename': filenames[i],
            'rotated': rotated[i],
            'trimmed': trimmed[i],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': x1, 'y': y1, 'w': fw, 'h': fh},
        })
        found = True
        break
    if not found:
        missing += 1
        new_frames.append({
            'filename': filenames[i],
            'rotated': rotated[i],
            'trimmed': trimmed[i],
            'sourceSize': {'w': 1, 'h': 1},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
            'frame': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        })

data['textures'][0]['frames'] = new_frames
with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

ok = sum(1 for vf in new_frames if vf['frame']['w'] != 1 and vf['frame']['h'] != 1)
print(f"\nWritten: {len(new_frames)} frames, {ok} non-1x1, {missing} missing/1x1")
