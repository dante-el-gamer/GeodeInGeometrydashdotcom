#!/usr/bin/env python3
"""Analyze the image around the intact frame to understand sprite connections."""
import numpy as np
from PIL import Image

img = Image.open('/home/dante/Documentos/GeodeInGeometrydash.com/assets/GJ_WebSheet.png').convert('RGBA')
arr = np.array(img)
alpha = arr[:, :, 3]

# Intact frame: (551, 894) 279x90
# Check pixel transparency around its borders and extended area
x1, y1, fw, fh = 551, 894, 279, 90

# Show a slice of alpha values at selected rows/cols
print("Column scan at y=894 (top edge):")
for x in range(540, 560):
    print(f"  x={x}: alpha={alpha[894, x]}")

print("\nColumn scan at y=983 (bottom edge):")
for x in range(540, 560):
    print(f"  x={x}: alpha={alpha[983, x]}")

print("\nAlpha values in region (545:560, 890:905) — top-left corner context:")
for y in range(890, 905):
    row = [f"{alpha[y, x]:4d}" for x in range(545, 560)]
    print(f"  y={y}: " + " ".join(row))

print("\nChecking if there's a connection between sprites near (547, 894):")
for dy in range(-2, 6):
    for dx in range(-2, 6):
        x, y = 547 + dx, 894 + dy
        a = alpha[y, x]
        if a > 0:
            print(f"  ({x},{y}): alpha={a}")

# Check the strip to the left of the intact frame: x=540..550, y=894..983
print("\nVertical strip x=540..550 (left of intact frame) alpha values:")
for y in range(894, 984):
    max_a = max(alpha[y, 540:551])
    if max_a > 0:
        print(f"  y={y}: max_alpha={max_a}")

# Check the row below intact frame: y=984, x=551..830
print("\nRow y=984 (below intact frame) alpha values:")
for x in range(551, 830):
    if alpha[984, x] > 0:
        print(f"  x={x}: alpha={alpha[984, x]}")

# Look at component #107 bounds: (550, 893) 335x141
print("\n\nAnalyzing merged component (550,893, 335x141):")
print(f"Right edge x=884..886, y=893..1033:")
for y in range(893, 1034, 10):
    alphas = [alpha[max(0,y), min(884, arr.shape[1]-1)] for y_slice in range(max(0,y-2), min(arr.shape[0], y+2))]
    print(f"  y={y}: alpha={alpha[min(y, arr.shape[0]-1), min(884, arr.shape[1]-1)]}")

# Check if there's a gradient or background connection
print("\nAlpha at right edge of intact frame (x=830):")
for y in range(890, 1000, 5):
    if y < alpha.shape[0] and 830 < alpha.shape[1]:
        print(f"  y={y}: alpha={alpha[y, 830]}")
