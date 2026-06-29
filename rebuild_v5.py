#!/usr/bin/env python3
"""Recovery v5: cores at alpha>200, NO expansion (precise), then fill tiny sprites."""
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

# Mark intact frame's area
ie = INTACT['frame']
excluded = np.zeros((H, W), dtype=bool)
excluded[ie['y']:ie['y']+ie['h'], ie['x']:ie['x']+ie['w']] = True

# === PASS 1: alpha > 200 cores, NO expansion ===
core_mask = alpha > 200
p1 = find_components(core_mask)
# Only keep components NOT overlapping with intact frame
p1_good = []
for x1, y1, x2, y2 in p1:
    if not (x1 < ie['x']+ie['w'] and x2 >= ie['x'] and y1 < ie['y']+ie['h'] and y2 >= ie['y']):
        p1_good.append((x1, y1, x2, y2))
print(f"P1 (alpha>200 cores): {len(p1)} total, {len(p1_good)} non-intact")

# ALSO exclude p1 core areas from future passes (only ≥3px components)
for x1, y1, x2, y2 in p1_good:
    if (x2 - x1 + 1) >= 3 and (y2 - y1 + 1) >= 3:
        excluded[y1:y2+1, x1:x2+1] = True

# === PASS 2: alpha > 0 in non-excluded areas (fill in the gaps) ===
tiny_mask = (alpha > 0) & ~excluded
p2 = find_components(tiny_mask)
p2 = [(x1, y1, x2, y2) for (x1, y1, x2, y2) in p2
      if (x2 - x1 + 1) >= 2 and (y2 - y1 + 1) >= 2]
print(f"P2 (alpha>0 fill): {len(p2)}")

# === ASSIGNMENT ===
# Sort p1 by (y, x) top-to-bottom left-to-right (natural layout order)
p1_sorted = sorted(p1_good, key=lambda r: (r[1], r[0]))
# Sort p2 by area descending (to fill big gaps first), then (y, x)
p2_sorted = sorted(p2, key=lambda r: (-((r[2]-r[0]+1)*(r[3]-r[1]+1)), r[1], r[0]))

all_comp = p1_sorted + p2_sorted
print(f"Total components: {len(all_comp)} for {len(filenames)-1} non-intact frames")

# Extend bboxes by 1px for AA edges (cautiously — only where no overlap occurs)
MARGIN = 1
def smart_expand(bbox, placed_bboxes, max_w, max_h):
    x1, y1, x2, y2 = bbox
    nx1 = max(0, x1 - MARGIN)
    ny1 = max(0, y1 - MARGIN)
    nx2 = min(max_w - 1, x2 + MARGIN)
    ny2 = min(max_h - 1, y2 + MARGIN)
    eb = (nx1, ny1, nx2, ny2)
    for pb in placed_bboxes:
        if not (eb[0] >= pb[2] or eb[2] <= pb[0] or eb[1] >= pb[3] or eb[3] <= pb[1]):
            # Overlaps, don't expand
            return (x1, y1, x2, y2)
    return eb

placed_bboxes = []
new_frames = []
missing = 0
ci = 0

for i in range(len(filenames)):
    if i == INTACT_IDX:
        new_frames.append(INTACT)
        print(f"  [{i:>2}] KEPT  {filenames[i]}")
        continue
    found = False
    while ci < len(all_comp) and not found:
        x1, y1, x2, y2 = all_comp[ci]
        ci += 1
        # Skip if overlaps intact
        if not (x1 >= ie['x']+ie['w'] or x2 < ie['x'] or y1 >= ie['y']+ie['h'] or y2 < ie['y']):
            continue
        eb = smart_expand((x1, y1, x2, y2), placed_bboxes, W, H)
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
        missing += 1
        new_frames.append({
            'filename': filenames[i],
            'rotated': rotated[i],
            'trimmed': trimmed[i],
            'sourceSize': {'w': 1, 'h': 1},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
            'frame': {'x': 0, 'y': 0, 'w': 1, 'h': 1},
        })

if not found and i == len(filenames) - 1:
    pass

data['textures'][0]['frames'] = new_frames
with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

ok = sum(1 for vf in new_frames if vf['frame']['w'] != 1 or vf['frame']['h'] != 1)
print(f"\nWritten: {len(new_frames)} frames, {ok} non-1x1, {missing} missing/1x1")

# Analysis
import sys
covered = np.zeros((H, W), dtype=bool)
for vf in new_frames:
    f = vf['frame']
    covered[f['y']:f['y']+f['h'], f['x']:f['x']+f['w']] = True
uncovered = (alpha > 0) & ~covered
print(f"Coverage: {covered.sum()}/{H*W} px ({covered.sum()/(H*W)*100:.1f}%)")
print(f"Uncovered alpha>0: {uncovered.sum()} px")

if uncovered.sum() > 0:
    uy, ux = np.where(uncovered)
    print(f"  Uncovered region bbox: ({ux.min()},{uy.min()})-({ux.max()},{uy.max()})")
    print(f"  Alpha distribution of uncovered pixels:")
    vals = alpha[uncovered]
    for t in [1, 32, 64, 128, 200]:
        print(f"    alpha>{t}: {(vals > t).sum()}")

# Check collisions
regions = []
collisions = 0
for i, vf in enumerate(new_frames):
    f = vf['frame']
    box = (f['x'], f['y'], f['x']+f['w'], f['y']+f['h'])
    if f['w'] > 1 and f['h'] > 1:
        for j, (box2, _) in enumerate(regions):
            if box[0] < box2[2] and box[2] > box2[0] and box[1] < box2[3] and box[3] > box2[1]:
                collisions += 1
    regions.append((box, vf['filename']))
print(f"Collisions: {collisions}")
