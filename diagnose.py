#!/usr/bin/env python3
"""Diagnose the spritesheet structure — find large components and analyze pixel layout."""
from PIL import Image

img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
w, h = img.size
pix = img.load()

# Find connected components (4-connected), keep only reasonably sized ones (>4 px in each dimension)
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
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx]:
                    if pix[nx, ny][3] > 0:
                        visited[ny * w + nx] = 1
                        stack.append((nx, ny))
        comps.append((x1, y1, x2 - x1 + 1, y2 - y1 + 1, (x2 - x1 + 1) * (y2 - y1 + 1)))

comps.sort(key=lambda c: -c[4])  # sort by area descending

print(f"Total components: {len(comps)}")
print(f"\nTop 30 components by area:")
print(f"{'#':>4} {'x':>4} {'y':>4} {'w':>6} {'h':>6} {'area':>8}")
print("-" * 40)
for i, (x, y, cw, ch, area) in enumerate(comps[:30]):
    print(f"{i:>4} {x:>4} {y:>4} {cw:>6} {ch:>6} {area:>8}")

print(f"\nComponents with area >= 50:")
large = [c for c in comps if c[4] >= 50]
for i, (x, y, cw, ch, area) in enumerate(large):
    print(f"  {i:>3}: ({x:>4},{y:>4}) {cw:>4}x{ch:<4} area={area}")

print(f"\nComponents with w >= 10 or h >= 10:")
medium = [c for c in comps if c[2] >= 10 or c[3] >= 10]
print(f"Count: {len(medium)}")
for i, (x, y, cw, ch, area) in enumerate(medium):
    print(f"  {i:>3}: ({x:>4},{y:>4}) {cw:>4}x{ch:<4} area={area}")
