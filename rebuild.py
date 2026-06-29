#!/usr/bin/env python3
"""Final recovery: reconstruct original state, detect all sprites, write clean JSON."""
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


def dilate_mask(mask, n=1):
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


def rects_overlap(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

# Original metadata (from the file's header — unchanged)
with open(JSON) as f:
    data = json.load(f)
old_frames = data['textures'][0]['frames']
filenames = [f['filename'] for f in old_frames]
trimmed_flags = [f['trimmed'] for f in old_frames]
rotated_flags = [f['rotated'] for f in old_frames]

# Hard-code the one truly intact frame's original data
ORIG_INTACT = {
    'filename': 'downloadSteam_001.png',
    'rotated': False,
    'trimmed': True,
    'sourceSize': {'w': 284, 'h': 95},
    'spriteSourceSize': {'x': 5, 'y': 5, 'w': 279, 'h': 90},
    'frame': {'x': 551, 'y': 894, 'w': 279, 'h': 90},
}
INTACT_IDX = 18

# Restore all frames to corrupted (1x1) except the intact one
for i in range(len(filenames)):
    pass  # We'll build fresh from our detection

print(f"Total frames: {len(filenames)} (1 intact at idx {INTACT_IDX})")

# Detect all sprite components from image
img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Pass 1: Solid cores at alpha > 200, dilate 3px for AA edges
solid_mask = dilate_mask(alpha > 200, 3)
p1 = find_components(solid_mask)
p1 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p1
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]

# Build exclusion mask: all pass1 regions + intact frame
excluded = np.zeros((h, w), dtype=bool)
for x1, y1, x2, y2 in p1:
    excluded[y1:y2+1, x1:x2+1] = True
# Exclude intact frame area
ie = ORIG_INTACT['frame']
excluded[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# Pass 2: Remaining soft sprites
soft_mask = (alpha > 32) & ~excluded
p2 = find_components(soft_mask)
p2 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p2
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]

# All unique components
all_c = p1 + p2
seen = {}
unique = []
for c in all_c:
    if c not in seen:
        seen[c] = True
        unique.append(c)
unique.sort(key=lambda r: (r[1], r[0]))
print(f"Detected {len(unique)} components")

# Map components to frames
intact_bbox = (ie['x'], ie['y'], ie['x'] + ie['w'] - 1, ie['y'] + ie['h'] - 1)
used = [False] * len(unique)
new_frames = []
missing = 0

for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(ORIG_INTACT)
        print(f"[{i:>2}] KEPT  {filenames[i]}")
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
            'rotated': rotated_flags[i],
            'trimmed': trimmed_flags[i],
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
            'rotated': rotated_flags[i],
            'trimmed': trimmed_flags[i],
            'sourceSize': {'w': 1, 'h': 1},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
            'frame': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        })

# Update data and write
data['textures'][0]['frames'] = new_frames
with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

ok = sum(1 for vf in new_frames if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)
print(f"\nWritten: {len(new_frames)} frames, {ok} non-1x1, {missing} missing/1x1")
