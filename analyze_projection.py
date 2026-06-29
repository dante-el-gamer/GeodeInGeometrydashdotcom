#!/usr/bin/env python3
"""Analyze image structure: row/column projections, background detection, sprite layout."""
import numpy as np
from PIL import Image

img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]
h, w = alpha.shape

# Row projection: count non-transparent pixels per row at various thresholds
for thresh in [0, 50, 100, 200]:
    row_sums = np.sum(alpha > thresh, axis=1)
    total_filled = np.sum(row_sums > 0)
    print(f"\nThreshold > {thresh}: {total_filled} rows have content")
    empty_rows = np.where(row_sums == 0)[0]
    print(f"  Empty rows: {len(empty_rows)} at y={list(empty_rows[:20])}{'...' if len(empty_rows) > 20 else ''}")

# Find empty rows at alpha > 200 (these are where high-opacity elements don't touch)
print("\n\nAt alpha>200:")
row_sums = np.sum(alpha > 200, axis=1)
empty_rows = list(np.where(row_sums == 0)[0])
print(f"Empty rows: {len(empty_rows)}")
# Groups of consecutive empty rows
if empty_rows:
    groups = []
    start = empty_rows[0]
    end = empty_rows[0]
    for r in empty_rows[1:]:
        if r == end + 1:
            end = r
        else:
            groups.append((start, end))
            start = r
            end = r
    groups.append((start, end))
    print(f"Gaps (start_y, end_y):")
    for s, e in groups:
        gap = e - s + 1
        print(f"  y={s}-{e} (gap={gap}px)")

# Find empty columns at alpha > 200
col_sums = np.sum(alpha > 200, axis=0)
empty_cols = list(np.where(col_sums == 0)[0])
print(f"\nEmpty columns at alpha>200: {len(empty_cols)}")

# Check what's at specific positions
print("\n\nChecking common pixel values to identify background:")
bg_colors = {}
for y in range(0, h, 10):
    for x in range(0, w, 10):
        if alpha[y, x] > 0:
            r, g, b, a = arr[y, x]
            # Quantize to identify common colors
            key = (r//32*32, g//32*32, b//32*32, a//64*64)
            bg_colors[key] = bg_colors.get(key, 0) + 1

sorted_colors = sorted(bg_colors.items(), key=lambda kv: -kv[1])
print("Most common RGBA colors (quantized):")
for color, count in sorted_colors[:20]:
    pct = 100 * count / ((h//10) * (w//10))
    print(f"  rgba{color}: {count} samples ({pct:.1f}%)")

# Check region (0, 515, 258, 1030) — the large left background element
print("\nAnalyzing large left region (x=0..258, y=515..1030):")
region = arr[515:1030, 0:258, :]
r_mean, g_mean, b_mean, a_mean = np.mean(region, axis=(0,1))
print(f"  Mean RGBA: ({r_mean:.0f}, {g_mean:.0f}, {b_mean:.0f}, {a_mean:.0f})")

# Check region (0, 278, 976, 432) — the large top background
print("\nAnalyzing large top region (x=0..976, y=278..432):")
region = arr[278:432, 0:976, :]
r_mean, g_mean, b_mean, a_mean = np.mean(region, axis=(0,1))
print(f"  Mean RGBA: ({r_mean:.0f}, {g_mean:.0f}, {b_mean:.0f}, {a_mean:.0f})")

# Check if these are gradient bars
print("\nChecking if background is a gradient (horizontal color variation):")
for y in [300, 350, 400]:
    row = arr[y, 0:976, :3]
    left_color = row[0]
    right_color = row[900]
    print(f"  y={y}: left=rgba{tuple(arr[y,0])} right=rgba{tuple(arr[y,900])}")
