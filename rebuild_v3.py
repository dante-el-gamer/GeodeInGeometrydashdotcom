#!/usr/bin/env python3
"""Recovery v3: detect cores on undilated mask, expand bboxes for AA edges."""
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
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


MARGIN = 2  # px to expand for AA edges
PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

# Read current JSON for metadata only
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
print(f"Frames: {len(filenames)}, intact at idx {INTACT_IDX}")

# Load image
img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
H, W = alpha.shape

# Pass 1: components at alpha>200 (undilated) → precisely separated cores
core_mask = alpha > 200
p1 = find_components(core_mask)
# Expand each bbox by MARGIN for AA
p1_expanded = [expand_bbox(c, MARGIN, W, H) for c in p1]
# Remove tiny/empty ones
p1_expanded = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p1_expanded
               if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]
print(f"Pass 1 (alpha>200 cores +{MARGIN}px): {len(p1)} cores, {len(p1_expanded)} usable")

# Build exclusion mask from pass1 bboxes + intact frame
excluded = np.zeros((H, W), dtype=bool)
for x1, y1, x2, y2 in p1_expanded:
    excluded[y1:y2+1, x1:x2+1] = True
ie = INTACT['frame']
excluded[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# Pass 2: remaining soft sprites at alpha>32, in non-excluded areas
soft_mask = (alpha > 32) & ~excluded
p2 = find_components(soft_mask)
p2 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p2
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]
print(f"Pass 2 (alpha>32 soft): {len(p2)}")

# Pass 3: tiny sprites at alpha>0 in remaining space
tiny_mask = (alpha > 0) & ~excluded
# First exclude all pass2 areas too
for x1, y1, x2, y2 in p2:
    tiny_mask[y1:y2+1, x1:x2+1] = False
p3 = find_components(tiny_mask)
p3 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p3
      if (x2 - x1 + 1) >= 2 and (y2 - y1 + 1) >= 2]
print(f"Pass 3 (alpha>0 tiny): {len(p3)}")

# Combine all passes, deduplicate
all_c = p1_expanded + p2 + p3
seen = {}
unique = []
for c in all_c:
    if c not in seen:
        seen[c] = True
        unique.append(c)
unique.sort(key=lambda r: (r[1], r[0]))
print(f"Total unique components: {len(unique)} (need {len(filenames)})")

# Map to frames
intact_bbox = (ie['x'], ie['y'], ie['x'] + ie['w'] - 1, ie['y'] + ie['h'] - 1)
used = [False] * len(unique)
new_frames = []
missing = 0

for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(INTACT)
        print(f"  [{i:>2}] KEPT  {filenames[i]}")
        continue

    found = False
    for ci in range(len(unique)):
        if used[ci]:
            continue
        cx1, cy1, cx2, cy2 = unique[ci]
        if rects_overlap((cx1, cy1, cx2, cy2), intact_bbox):
            used[ci] = True
            continue
        used[ci] = True
        fw, fh = cx2 - cx1 + 1, cy2 - cy1 + 1
        new_frames.append({
            'filename': filenames[i],
            'rotated': rotated[i],
            'trimmed': trimmed[i],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': cx1, 'y': cy1, 'w': fw, 'h': fh},
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
