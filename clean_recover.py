#!/usr/bin/env python3
"""Clean recovery: restore original file, then detect all sprite components."""
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

# Step 1: Restore the original corrupted file (all 1x1 frames except downloadSteam_001)
# Read the current (possibly partially-overwritten) file to get metadata/names
with open(JSON) as f:
    data = json.load(f)
old_frames = data['textures'][0]['frames']

# Find the truly intact frame: downloadSteam_001
# It has sourceSize {w:284, h:95} and spriteSourceSize {x:5, y:5, w:279, h:90}
# We know from the original read it's at index 18
TRULY_INTACT_IDX = 18

# Restore all other frames to 1x1
for i in range(len(old_frames)):
    if i != TRULY_INTACT_IDX:
        old_frames[i] = {
            'filename': old_frames[i]['filename'],
            'rotated': old_frames[i]['rotated'],
            'trimmed': old_frames[i]['trimmed'],
            'sourceSize': {'w': 1, 'h': 1},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
            'frame': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        }

print(f"Restored {len(old_frames)} frames ({len([f for f in old_frames if f['frame']['w']==1])} corrupted, "
      f"{sum(1 for f in old_frames if f['frame']['w']!=1)} intact)")

# Step 2: Find ALL sprites in the image using multi-pass detection
img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Pass 1: Solid sprites (alpha > 200, dilate 3px)
solid = dilate_mask(alpha > 200, 3)
p1 = find_components(solid)
p1 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p1
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]

# Build exclusion mask from pass 1
excluded = np.zeros((h, w), dtype=bool)
for x1, y1, x2, y2 in p1:
    excluded[y1:y2+1, x1:x2+1] = True
# Also exclude the intact frame's area
fr = old_frames[TRULY_INTACT_IDX]['frame']
excluded[fr['y']:fr['y']+fr['h'], fr['x']:fr['x']+fr['w']] = True

# Pass 2: Semi-transparent sprites (alpha > 32, in non-excluded areas)
soft = (alpha > 32) & ~excluded
p2 = find_components(soft)
p2 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p2
      if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4]

# Combine all passes
all_comps = p1 + p2
# Remove duplicates
seen = set()
unique = []
for c in all_comps:
    if c not in seen:
        seen.add(c)
        unique.append(c)
unique.sort(key=lambda r: (r[1], r[0]))

print(f"Detected {len(unique)} sprite components total (need {len(old_frames)})")

# Step 3: Map components to corrupted frames
intact_bbox = (fr['x'], fr['y'], fr['x'] + fr['w'] - 1, fr['y'] + fr['h'] - 1)
print(f"Intact frame: [{TRULY_INTACT_IDX}] {old_frames[TRULY_INTACT_IDX]['filename']} at {intact_bbox}")

new_frames = []
used = [False] * len(unique)
missing = 0

for i, f in enumerate(old_frames):
    if i == TRULY_INTACT_IDX:
        new_frames.append(f)
        print(f"[{i:>2}] KEPT  {f['filename']}  ({f['frame']['x']},{f['frame']['y']}) "
              f"{f['frame']['w']}x{f['frame']['h']}")
        continue

    found = False
    for ci, (cx1, cy1, cx2, cy2) in enumerate(unique):
        if used[ci]:
            continue
        # Skip components overlapping with the intact frame
        if rects_overlap((cx1, cy1, cx2, cy2), intact_bbox):
            used[ci] = True
            continue
        used[ci] = True
        fw, fh = cx2 - cx1 + 1, cy2 - cy1 + 1
        new_frames.append({
            'filename': f['filename'],
            'rotated': f['rotated'],
            'trimmed': f['trimmed'],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': cx1, 'y': cy1, 'w': fw, 'h': fh},
        })
        print(f"[{i:>2}] MAP   {f['filename']}  ({cx1},{cy1}) {fw}x{fh}")
        found = True
        break

    if not found:
        missing += 1
        new_frames.append(f)
        print(f"[{i:>2}] FAIL  {f['filename']}  (1x1 fallback)")

data['textures'][0]['frames'] = new_frames

with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

final_count = sum(1 for vf in new_frames if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)
print(f"\nDone: {len(new_frames)} frames, {final_count} non-1x1, {missing} missing/1x1")
