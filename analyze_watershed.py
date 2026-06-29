#!/usr/bin/env python3
"""Multi-source BFS watershed sprite detection.

1. Find core regions (alpha > 128) as seed labels
2. Propagate labels to soft-edge pixels via BFS (nearest-core wins)
3. Compute bounding boxes per label
4. Filter and map to texture
"""
import json
import numpy as np
from PIL import Image
from collections import deque


def watershed_sprites(alpha, core_thresh=128, min_area=50):
    """Detect sprites via seeded watershed from high-alpha cores."""
    h, w = alpha.shape
    core = alpha > core_thresh
    labels = np.zeros((h, w), dtype=np.int32)
    q = deque()

    label_id = 1
    for y in range(h):
        for x in range(w):
            if core[y, x] and labels[y, x] == 0:
                # Label this entire core component
                stack = [(x, y)]
                labels[y, x] = label_id
                while stack:
                    cx, cy = stack.pop()
                    q.append((cx, cy, label_id))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and not labels[ny, nx] and core[ny, nx]:
                            labels[ny, nx] = label_id
                            stack.append((nx, ny))
                label_id += 1

    print(f"  Core components: {label_id - 1}")

    # Propagate labels to unlabeled alpha > 0 pixels (BFS)
    while q:
        x, y, lid = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and labels[ny, nx] == 0 and alpha[ny, nx] > 0:
                labels[ny, nx] = lid
                q.append((nx, ny, lid))

    # Extract bounding boxes per label
    bboxes = []
    for lid in range(1, label_id):
        ys, xs = np.where(labels == lid)
        if len(xs) == 0:
            continue
        x1, y1 = int(xs.min()), int(ys.min())
        x2, y2 = int(xs.max()), int(ys.max())
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        if area >= min_area:
            bboxes.append((x1, y1, x2, y2, lid))

    return bboxes, labels


img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
print(f"Image: {arr.shape[1]}x{arr.shape[0]}")

# Try different thresholds
for thresh in [64, 96, 128, 160, 200]:
    bboxes, _ = watershed_sprites(alpha, core_thresh=thresh, min_area=20)
    print(f"  thresh>{thresh}: {len(bboxes)} sprites")
    bboxes.sort(key=lambda r: (r[1], r[0]))
    if len(bboxes) <= 110 and len(bboxes) >= 80:
        print(f"  -> Good candidate! Showing sprites:")
        for i, (x1, y1, x2, y2, lid) in enumerate(bboxes):
            fw, fh = x2 - x1 + 1, y2 - y1 + 1
            print(f"      [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")

# Also show thresh=96 (might give ~91)
print("\n\nBest candidate: thresh=96")
bboxes, labels = watershed_sprites(alpha, core_thresh=96, min_area=20)
print(f"  Total: {len(bboxes)} sprites")
bboxes.sort(key=lambda r: (r[1], r[0]))
for i, (x1, y1, x2, y2, lid) in enumerate(bboxes):
    fw, fh = x2 - x1 + 1, y2 - y1 + 1
    print(f"  [{i:>2}] ({x1:>4},{y1:>4}) {fw:>3}x{fh:<3}")
