#!/usr/bin/env python3
"""Recovery v6: clean multi-pass with proper exclusion and size-based filtering."""
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

# Exclude intact frame area from all detection
ie = INTACT['frame']
used = np.zeros((H, W), dtype=bool)
used[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# === PASS 1: solid cores at alpha > 200 ===
p1 = find_components(alpha > 200)
# Keep only >= 3px components (actual sprites, not noise fragments)
p1_good = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p1
           if (x2-x1+1) >= 3 and (y2-y1+1) >= 3
           and not (x1 < ie['x']+ie['w'] and x2 >= ie['x'] and y1 < ie['y']+ie['h'] and y2 >= ie['y'])]
# Exclude p1_good areas from future detection
for x1, y1, x2, y2 in p1_good:
    used[y1:y2+1, x1:x2+1] = True
print(f"P1 (alpha>200 cores >=3px): {len(p1_good)}")

# === PASS 2: alpha > 32 in unused areas ===
p2 = find_components((alpha > 32) & ~used)
p2_good = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p2
           if (x2-x1+1) >= 3 and (y2-y1+1) >= 3]
for x1, y1, x2, y2 in p2_good:
    used[y1:y2+1, x1:x2+1] = True
print(f"P2 (alpha>32 fill): {len(p2_good)}")

# === PASS 3: alpha > 0 tiny remnants ===
p3 = find_components((alpha > 0) & ~used)
p3_good = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p3
           if (x2-x1+1) >= 2 and (y2-y1+1) >= 2]
print(f"P3 (alpha>0 tiny): {len(p3_good)}")

# Combine all passes, sort by (y,x)
all_comp = sorted(p1_good + p2_good + p3_good, key=lambda r: (r[1], r[0]))
print(f"Total: {len(all_comp)} components for {len(filenames)-1} non-intact frames")

# Assign with smart 1px expansion (only where no overlap)
MARGIN = 1
placed_bboxes = []
new_frames = []
ci = 0

def expand_or_shrink(bbox, placed, max_w, max_h):
    x1, y1, x2, y2 = bbox
    # Try 1px expansion in each direction that doesn't cause overlap
    for dx in [0, 1]:
        for dy in [0, 1]:
            nx1 = max(0, x1 - dx)
            ny1 = max(0, y1 - dy)
            nx2 = min(max_w - 1, x2 + dx)
            ny2 = min(max_h - 1, y2 + dy)
            eb = (nx1, ny1, nx2, ny2)
            # Also ensure min 3x3
            if nx2 - nx1 < 2: nx2 = nx1 + 2
            if ny2 - ny1 < 2: ny2 = ny1 + 2
            eb = (nx1, ny1, min(nx2, max_w-1), min(ny2, max_h-1))
            ok = True
            for pb in placed:
                if not (eb[0] >= pb[2] or eb[2] <= pb[0] or eb[1] >= pb[3] or eb[3] <= pb[1]):
                    ok = False
                    break
            if ok:
                return eb
    return bbox

for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(INTACT)
        continue
    # Find next available component
    found = False
    while ci < len(all_comp) and not found:
        x1, y1, x2, y2 = all_comp[ci]
        ci += 1
        # Skip if overlaps intact
        if not (x1 >= ie['x']+ie['w'] or x2 < ie['x'] or y1 >= ie['y']+ie['h'] or y2 < ie['y']):
            continue
        eb = expand_or_shrink((x1, y1, x2, y2), placed_bboxes, W, H)
        placed_bboxes.append(eb)
        fw, fh = eb[2] - eb[0] + 1, eb[3] - eb[1] + 1
        new_frames.append({
            'filename': filenames[i],
            'rotated': rotated[i],
            'trimmed': trimmed[i],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': eb[0], 'y': eb[1], 'w': fw, 'h': fh},
        })
        found = True

    if not found:
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

ok = sum(1 for vf in new_frames if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)
big = sum(1 for vf in new_frames if vf['frame']['w'] > 1 and vf['frame']['h'] > 1)
print(f"\nWritten: {len(new_frames)} frames, {ok} non-1x1, {big} both>1")

# Coverage
covered = np.zeros((H, W), dtype=bool)
for vf in new_frames:
    f = vf['frame']
    covered[f['y']:f['y']+f['h'], f['x']:f['x']+f['w']] = True
uncovered = (alpha > 0) & ~covered
print(f"Coverage: {covered.sum()}/{H*W} ({covered.sum()/(H*W)*100:.1f}%) | Uncovered alpha>0: {uncovered.sum()}")

# Collisions
regions = []
col = 0
for vf in new_frames:
    f = vf['frame']
    box = (f['x'], f['y'], f['x']+f['w'], f['y']+f['h'])
    for j, (box2, _) in enumerate(regions):
        if box[0] < box2[2] and box[2] > box2[0] and box[1] < box2[3] and box[3] > box2[1]:
            col += 1
    regions.append((box, vf['filename']))
print(f"Collisions: {col}")
