#!/usr/bin/env python3
"""Interior wall positions for Chamber 4."""

grid = [
'#########################',  # 00
'#@X..MMMM....M......M...#',  # 01
'#######################.#',  # 02
'#.....S...#.........~~#.#',  # 03
'#.^...S...#.XXX.......#.#',  # 04
'#==######~#.XSX........X#',  # 05
'#..~#.....~#####~~....#.#',  # 06
'#..~#........M.......~#.#',  # 07
'#...#.....X..M.......~#.#',  # 08
'#...#...####.........~#.#',  # 09
'#===#===~~~#~##########.#',  # 10
'#.........~#............#',  # 11
'#..........#............#',  # 12
'#.......................#',  # 13
'#~~~~~~##################',  # 14
]

# Interior walls (not on boundary rows/cols)
print("Interior WALL (#):")
interior_walls = []
for y in range(1, 14):
    for x in range(1, 24):
        if grid[y][x] == '#':
            interior_walls.append((x, y))
            print(f"  ({x},{y})")

# Find contiguous vertical runs at each column
from itertools import groupby

print("\nVertical runs by column:")
by_col = {}
for x, y in interior_walls:
    by_col.setdefault(x, []).append(y)
for col in sorted(by_col):
    ys = by_col[col]
    # find contiguous runs
    runs = []
    start = ys[0]
    prev = ys[0]
    for y in ys[1:]:
        if y == prev + 1:
            prev = y
        else:
            runs.append((start, prev))
            start = y
            prev = y
    runs.append((start, prev))
    for s, e in runs:
        print(f"  Col {col}: rows {s}{'-' + str(e) if s != e else ''}")

print("\nHorizontal runs by row:")
by_row = {}
for x, y in interior_walls:
    by_row.setdefault(y, []).append(x)
for row in sorted(by_row):
    xs = by_row[row]
    runs = []
    start = xs[0]
    prev = xs[0]
    for x in xs[1:]:
        if x == prev + 1:
            prev = x
        else:
            runs.append((start, prev))
            start = x
            prev = x
    runs.append((start, prev))
    for s, e in runs:
        print(f"  Row {row}: cols {s}{'-' + str(e) if s != e else ''}")
