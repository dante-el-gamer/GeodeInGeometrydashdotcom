#!/usr/bin/env python3
"""Two-pass recovery: solid sprites at alpha>200, glow sprites at alpha>64."""
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

img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Pass 1: Find all components at alpha > 200, dilate 2px
core_mask = alpha > 200
dilated = dilate_mask(core_mask, 2)
pass1 = find_components(dilated)
pass1 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in pass1
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= 50]
print(f"Pass 1 (alpha>200, dilate2, area>=50): {len(pass1)} components")

# Pass 2: Find additional components at alpha > 64, excluding pass1 regions
# Create a mask of areas not covered by pass1
excluded = np.zeros((h, w), dtype=bool)
for x1, y1, x2, y2 in pass1:
    excluded[y1:y2+1, x1:x2+1] = True

# At alpha > 64, find components in non-excluded areas
soft_mask = (alpha > 64) & ~excluded
pass2 = find_components(soft_mask)
pass2 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in pass2
         if (x2 - x1 + 1) >= 5 and (y2 - y1 + 1) >= 5]
print(f"Pass 2 (alpha>64, non-overlapping, min_side=5): {len(pass2)} components")

# Pass 3: Small sprites only at alpha > 0, non-overlapping with pass1 and pass2
excluded2 = excluded.copy()
for x1, y1, x2, y2 in pass2:
    excluded2[y1:y2+1, x1:x2+1] = True
tiny_mask = (alpha > 0) & ~excluded2
pass3 = find_components(tiny_mask)
pass3 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in pass3
         if (x2 - x1 + 1) >= 4 and (y2 - y1 + 1) >= 4
         and (x2 - x1 + 1) * (y2 - y1 + 1) >= 16]
print(f"Pass 3 (alpha>0, non-overlapping, min 4x4): {len(pass3)} components")

# Combine all passes
all_comps = pass1 + pass2 + pass3
# Remove duplicates
seen = set()
unique = []
for c in all_comps:
    if c not in seen:
        seen.add(c)
        unique.append(c)
unique.sort(key=lambda r: (r[1], r[0]))
print(f"Unique total: {len(unique)} components (need ~90)")

# Take the first 90 (or as many as needed)
needed = 91  # total frames
target_comps = unique[:needed]
print(f"Using {len(target_comps)} components for {needed} frames")

# Load existing JSON
with open(JSON) as f:
    data = json.load(f)
old_frames = data['textures'][0]['frames']

# Find intact frame
intact_idx = None
for i, f in enumerate(old_frames):
    if f['frame']['w'] != 1 or f['frame']['h'] != 1:
        intact_idx = i
        break

if intact_idx is not None:
    fr = old_frames[intact_idx]['frame']
    intact_bbox = (fr['x'], fr['y'], fr['x'] + fr['w'] - 1, fr['y'] + fr['h'] - 1)
    print(f"Intact frame: idx={intact_idx}, bbox={intact_bbox}")

# Build new frames
new_frames = []
used = [False] * len(target_comps)

for i, f in enumerate(old_frames):
    if i == intact_idx:
        new_frames.append(f)
        continue

    found = False
    for ci, (cx1, cy1, cx2, cy2) in enumerate(target_comps):
        if used[ci]:
            continue
        if intact_idx is not None and rects_overlap((cx1, cy1, cx2, cy2), intact_bbox):
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
        found = True
        break

    if not found:
        # Fallback: just use 1x1 at 0,0 (shouldn't happen often)
        print(f"  WARNING: no component for {f['filename']}")
        new_frames.append(f)

data['textures'][0]['frames'] = new_frames

with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

print(f"\nWritten {len(new_frames)} frames to {JSON}")

# Quick verify
verify = json.load(open(JSON))
print(f"Verify: {len(verify['textures'][0]['frames'])} frames, "
      f"{sum(1 for vf in verify['textures'][0]['frames'] if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)} non-1x1 frames")
