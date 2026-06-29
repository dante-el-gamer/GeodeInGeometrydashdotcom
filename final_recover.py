#!/usr/bin/env python3
"""Final recovery: detect sprite cores at alpha>200, filter, map to filenames."""
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


PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

img = Image.open(PNG).convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Step 1: Find cores at alpha > 200
core_mask = alpha > 200
comps = find_components(core_mask)
comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in comps
         if (x2 - x1 + 1) * (y2 - y1 + 1) >= 50]
print(f"Initial components at alpha>200 (area>=50): {len(comps)}")

# Step 2: Dilate cores to include AA edges
dilated = dilate_mask(core_mask, 2)
dilated_comps = find_components(dilated)
dilated_comps = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in dilated_comps
                 if (x2 - x1 + 1) * (y2 - y1 + 1) >= 50]
dilated_comps.sort(key=lambda r: (r[1], r[0]))
print(f"After 2px dilation: {len(dilated_comps)} components\n")

for i, (x1, y1, x2, y2) in enumerate(dilated_comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    flags = []
    if fw >= 400: flags.append("WIDE")
    if fh >= 300: flags.append("TALL")
    if fw * fh >= 20000: flags.append("HUGE")
    tag = " ".join(flags) if flags else "sprite"
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3} area={fw*fh:<6} {tag}")

# Step 3: For the final recovery, keep only sprite-like components
# Remove: very wide background bars, very tall background columns, enormous areas
SPRITE_MAX_AREA = 18000
SPRITE_MAX_W = 350
SPRITE_MAX_H = 200

filtered = []
removed = []
for i, (x1, y1, x2, y2) in enumerate(dilated_comps):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    area = fw * fh
    if area >= SPRITE_MAX_AREA or fw >= SPRITE_MAX_W or fh >= SPRITE_MAX_H:
        removed.append((i, x1, y1, x2, y2, fw, fh, area))
    else:
        filtered.append((x1, y1, x2, y2))

print(f"\nFiltered: {len(filtered)} sprites, Removed: {len(removed)} backgrounds")
for i, x1, y1, x2, y2, fw, fh, area in removed:
    print(f"  REMOVED [{i:>2}]: ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3} area={area}")

# Step 4: Map to filenames
with open(JSON) as f:
    data = json.load(f)

old_frames = data['textures'][0]['frames']
filenames = [f['filename'] for f in old_frames]
trimmed = [f['trimmed'] for f in old_frames]
rotated = [f['rotated'] for f in old_frames]

# Find intact frame
intact_idx = None
for i, f in enumerate(old_frames):
    if f['frame']['w'] != 1 or f['frame']['h'] != 1:
        intact_idx = i
        break

print(f"\nMapping {len(filtered)} components to {len(filenames)} frames (intact at idx {intact_idx})")

# Handle the intact frame specially
intact_bbox = None
if intact_idx is not None:
    fr = old_frames[intact_idx]['frame']
    intact_bbox = (fr['x'], fr['y'], fr['x'] + fr['w'] - 1, fr['y'] + fr['h'] - 1)

# Map components to frames, preserving intact frame
new_frames = []
comp_idx = 0
mismatch = False

for i, fname in enumerate(filenames):
    if i == intact_idx:
        new_frames.append(old_frames[i])
        print(f"[{i:>2}] KEPT  {fname}")
        continue

    if comp_idx >= len(filtered):
        print(f"[{i:>2}] FAIL  {fname} — ran out of components!")
        mismatch = True
        break

    # Skip components that overlap with the intact frame
    while comp_idx < len(filtered):
        x1, y1, x2, y2 = filtered[comp_idx]
        if intact_bbox and not (x2 < intact_bbox[0] or x1 > intact_bbox[2] or
                                y2 < intact_bbox[1] or y1 > intact_bbox[3]):
            comp_idx += 1
            continue
        break

    if comp_idx >= len(filtered):
        print(f"[{i:>2}] FAIL  {fname} — no more components after intact skip")
        mismatch = True
        break

    x1, y1, x2, y2 = filtered[comp_idx]
    comp_idx += 1
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    new_frames.append({
        'filename': fname,
        'rotated': rotated[i],
        'trimmed': trimmed[i],
        'sourceSize': {'w': fw, 'h': fh},
        'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
        'frame': {'x': x1, 'y': y1, 'w': fw, 'h': fh},
    })
    print(f"[{i:>2}] MAP  {fname} -> ({x1},{y1}) {fw}x{fh}")

if mismatch:
    print(f"\nMISMATCH! Need to handle differently.")
else:
    print(f"\nAll {len(new_frames)} frames mapped successfully!")

    data['textures'][0]['frames'] = new_frames
    with open(JSON, 'w') as f:
        json.dump(data, f, indent='\t')
    print(f"Written to {JSON}")

    # Verify
    with open(JSON) as f:
        verify = json.load(f)
    vframes = verify['textures'][0]['frames']
    print(f"Verification: {len(vframes)} frames in output")
    for vf in vframes[:5]:
        print(f"  {vf['filename']}: frame=({vf['frame']['x']},{vf['frame']['y']}) {vf['frame']['w']}x{vf['frame']['h']}")
