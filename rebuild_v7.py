#!/usr/bin/env python3
"""Recovery v7: dilated cores (merge nearby sprites), then fill gaps."""
import json, numpy as np
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


def dilate(mask, n=2):
    result = mask.copy()
    for _ in range(n):
        prev = result.copy()
        result[1:-1, 1:-1] = (
            prev[1:-1, 1:-1] | prev[:-2, 1:-1] | prev[2:, 1:-1] |
            prev[1:-1, :-2] | prev[1:-1, 2:] |
            prev[:-2, :-2] | prev[:-2, 2:] | prev[2:, :-2] | prev[2:, 2:]
        )
    return result


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

# Exclude intact frame area
ie = INTACT['frame']
used = np.zeros((H, W), dtype=bool)
used[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# === PASS 1: Dilate alpha > 200, find merged components ===
core = alpha > 200
dilated = dilate(core, 2)
p1 = find_components(dilated)
# Remove components overlapping with intact
p1 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p1
      if not (x1 < ie['x']+ie['w'] and x2 >= ie['x'] and y1 < ie['y']+ie['h'] and y2 >= ie['y'])]
p1 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p1
      if (x2-x1+1) >= 6 or (y2-y1+1) >= 6]
print(f"P1 (dilated alpha>200, >=6px): {len(p1)}")

# Sort by area DESC (largest sprites first)
p1.sort(key=lambda r: -((r[2]-r[0]+1)*(r[3]-r[1]+1)))

# Build exclusion mask from p1 bboxes
for x1, y1, x2, y2 in p1:
    used[y1:y2+1, x1:x2+1] = True

# === PASS 2: alpha > 32 in unclaimed ===
p2 = find_components((alpha > 32) & ~used)
p2 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p2 if (x2-x1+1) >= 4 and (y2-y1+1) >= 4]
print(f"P2 (alpha>32, >=4px): {len(p2)}")
for x1, y1, x2, y2 in p2:
    used[y1:y2+1, x1:x2+1] = True

# === PASS 3: alpha > 0, all remnants ===
p3 = find_components((alpha > 0) & ~used)
p3 = [(x1,y1,x2,y2) for (x1,y1,x2,y2) in p3 if (x2-x1+1) >= 2 and (y2-y1+1) >= 2]
print(f"P3 (alpha>0, >=2px): {len(p3)}")

all_comp = p1 + p2 + p3
print(f"Total: {len(all_comp)} (need {len(filenames)-1})")

# Sort by (y, x) for natural assignment
all_comp.sort(key=lambda r: (r[1], r[0]))

# Assign to frames
placed = []
new_frames = []
ci = 0
for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(INTACT)
        continue
    found = False
    while ci < len(all_comp) and not found:
        x1, y1, x2, y2 = all_comp[ci]
        ci += 1
        if x1 < ie['x']+ie['w'] and x2 >= ie['x'] and y1 < ie['y']+ie['h'] and y2 >= ie['y']:
            continue
        # Check no overlap with placed bboxes
        ok = True
        for px1, py1, px2, py2 in placed:
            if not (x1 > px2 or x2 < px1 or y1 > py2 or y2 < py1):
                ok = False
                break
        if not ok:
            continue
        placed.append((x1, y1, x2, y2))
        fw, fh = x2-x1+1, y2-y1+1
        new_frames.append({
            'filename': filenames[i], 'rotated': rotated[i], 'trimmed': trimmed[i],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': x1, 'y': y1, 'w': fw, 'h': fh},
        })
        found = True
    if not found:
        new_frames.append({
            'filename': filenames[i], 'rotated': rotated[i], 'trimmed': trimmed[i],
            'sourceSize': {'w': 1, 'h': 1},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
            'frame': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        })

data['textures'][0]['frames'] = new_frames
with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

ok = sum(1 for vf in new_frames if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)
big = sum(1 for vf in new_frames if vf['frame']['w'] > 1 and vf['frame']['h'] > 1)
print(f"\nWritten: {len(new_frames)}, {ok} non-1x1, {big} both>1")

covered = np.zeros((H, W), dtype=bool)
for vf in new_frames:
    f = vf['frame']
    covered[f['y']:f['y']+f['h'], f['x']:f['x']+f['w']] = True
uncovered = (alpha > 0) & ~covered
print(f"Cov: {covered.sum()}/{H*W} ({covered.sum()/(H*W)*100:.1f}%) Uncov alpha>0: {uncovered.sum()}")

# Collisions
regs = []
col = 0
for vf in new_frames:
    f = vf['frame']
    bx = (f['x'], f['y'], f['x']+f['w'], f['y']+f['h'])
    for j, (bx2,_) in enumerate(regs):
        if bx[0] < bx2[2] and bx[2] > bx2[0] and bx[1] < bx2[3] and bx[3] > bx2[1]:
            col += 1
    regs.append((bx, vf['filename']))
print(f"Collisions: {col}")
