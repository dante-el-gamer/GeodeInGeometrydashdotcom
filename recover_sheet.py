#!/usr/bin/env python3
"""Recover GJ_WebSheet.json frame coordinates from the spritesheet PNG.
Finds all non-transparent 4-connected regions, sorts them top-to-bottom/left-to-right,
and maps them to the existing frame filenames (preserving the one intact frame's trim data).
"""
import json
from PIL import Image


def find_components(img):
    """Find 4-connected components of non-transparent pixels via iterative BFS."""
    w, h = img.size
    pix = img.load()
    visited = bytearray(w * h)
    comps = []

    for y in range(h):
        for x in range(w):
            if visited[y * w + x] or pix[x, y][3] == 0:
                continue
            x1 = x2 = x
            y1 = y2 = y
            stack = [(x, y)]
            visited[y * w + x] = 1
            while stack:
                cx, cy = stack.pop()
                if cx < x1: x1 = cx
                if cx > x2: x2 = cx
                if cy < y1: y1 = cy
                if cy > y2: y2 = cy
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx]:
                        if pix[nx, ny][3] > 0:
                            visited[ny * w + nx] = 1
                            stack.append((nx, ny))
            comps.append((x1, y1, x2, y2))
    return comps


def rects_overlap(a, b):
    """Check if two (x1,y1,x2,y2) rects overlap."""
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


PNG = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png'
JSON = '/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.json'

# 1. Scan image for sprite bounding boxes
img = Image.open(PNG).convert('RGBA')
print(f"Image: {img.size[0]}x{img.size[1]}")

comps = find_components(img)
comps.sort(key=lambda r: (r[1], r[0]))  # top-to-bottom, left-to-right
print(f"Detected {len(comps)} non-transparent regions")

# 2. Load existing JSON
with open(JSON) as f:
    data = json.load(f)

old_frames = data['textures'][0]['frames']
print(f"JSON frames: {len(old_frames)}")

# 3. Identify the intact frame (the one non-1x1 entry)
intact = None
for f in old_frames:
    if f['frame']['w'] != 1 or f['frame']['h'] != 1:
        intact = f
        fr = f['frame']
        intact_bbox = (fr['x'], fr['y'], fr['x'] + fr['w'] - 1, fr['y'] + fr['h'] - 1)
        print(f"Intact frame: {f['filename']} -> {intact_bbox}")
        break

# 4. Rebuild frames: keep intact, map detected components to corrupted ones
new_frames = []
used = set()
missing = 0

for i, f in enumerate(old_frames):
    if f is intact:
        new_frames.append(f)
        print(f"[{i:2d}] KEPT    {f['filename']}  {f['frame']['w']}x{f['frame']['h']}")
        continue

    matched = None
    for ci, c in enumerate(comps):
        if ci in used:
            continue
        if intact and rects_overlap(c, intact_bbox):
            used.add(ci)
            continue
        used.add(ci)
        matched = c
        break

    if matched:
        x1, y1, x2, y2 = matched
        fw, fh = x2 - x1 + 1, y2 - y1 + 1
        new_frames.append({
            'filename': f['filename'],
            'rotated': f['rotated'],
            'trimmed': f['trimmed'],
            'sourceSize': {'w': fw, 'h': fh},
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh},
            'frame': {'x': x1, 'y': y1, 'w': fw, 'h': fh},
        })
        print(f"[{i:2d}] MAPPED  {f['filename']}  ({x1},{y1}) {fw}x{fh}")
    else:
        missing += 1
        print(f"[{i:2d}] FAILED  {f['filename']}  — no free component")

data['textures'][0]['frames'] = new_frames

# 5. Write back with the same formatting (tabs)
with open(JSON, 'w') as f:
    json.dump(data, f, indent='\t')

print(f"\nWritten {len(new_frames)} frames ({missing} failures, {len(comps)} components found)")
print("Verify with: python3 -c \"import json; d=json.load(open('assets/GJ_WebSheet.json')); print(len(d['textures'][0]['frames']), 'frames'); [print(f['filename'], f['frame']) for f in d['textures'][0]['frames'][:5]]\"")
