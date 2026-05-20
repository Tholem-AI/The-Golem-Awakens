#!/usr/bin/env python3
"""
chamber_diff.py — Golem Game chamber diff/verification tool

Compares ASCII grid data from markdown files against JavaScript chamber
definitions in golem.html. Produces tile-by-tile diffs and structural
validation reports.

Usage:
    python3 tools/chamber_diff.py                      # diff all chambers
    python3 tools/chamber_diff.py --chamber T           # diff specific chamber
    python3 tools/chamber_diff.py --validate FILE.md    # validate a markdown file
    python3 tools/chamber_diff.py --diff-proposal DATA.md PROPOSAL.md
    python3 tools/chamber_diff.py --export-ascii [OUT.md]
    python3 tools/chamber_diff.py --strict
    python3 tools/chamber_diff.py --check-flow
    python3 tools/chamber_diff.py --diff-proposal DATA.md PROPOSAL.md --against-js golem.html

Coordinate convention: (col, row) = (x, y) — col is horizontal, row is vertical.
Grid access: g[row][col] = g[y][x]
"""

import sys
import os
import re
import json
from pathlib import Path

# ── Tile constants ──────────────────────────────────────────────────────────

CHAR_TO_CONST = {
    '.': ('AIR', 0),
    '#': ('WALL', 1),
    '~': ('PIT', 2),
    '^': ('GOLEM_SPAWN', 3),
    'v': ('DOOR_D', 4),
    '*': ('GLYPH', 5),
    'X': ('CRACKED', 7),
    '=': ('PLATFORM', 8),
    '@': ('END_PORTAL', 9),
    'M': ('MAGICAL_WALL', 10),
    'S': ('PUSH_SPAWN', 11),
}

CONST_TO_CHAR = {}
VALUE_TO_CONST = {}
VALUE_TO_CHAR = {}
for char, (const, val) in CHAR_TO_CONST.items():
    CONST_TO_CHAR[const] = char
    VALUE_TO_CONST[val] = const
    VALUE_TO_CHAR[val] = char

CONST_TO_VALUE = {
    'AIR': 0, 'WALL': 1, 'PIT': 2, 'GOLEM_SPAWN': 3,
    'DOOR_D': 4, 'GLYPH': 5, 'CRACKED': 7, 'PLATFORM': 8,
    'END_PORTAL': 9, 'MAGICAL_WALL': 10, 'PUSH_SPAWN': 11
}

GRID_W = 25
GRID_H = 15


# ── ASCII grid parser (markdown code blocks) ───────────────────────────────

def parse_ascii_grid(grid_text):
    """
    Parse an ASCII grid from markdown code block text.
    Returns a list of 15 strings, each 25 characters long.
    Also returns the chamber name if found.
    """
    lines = grid_text.strip().split('\n')
    grids = []
    chamber_name = None

    current_lines = []
    in_grid = False

    for line in lines:
        line = line.rstrip()

        # Detect header
        header_match = re.match(r'\|\s*Ch\.([A-Z0-9]+)\s+(.+?)\s*\|', line)
        if header_match:
            chamber_name = f"Ch.{header_match.group(1)} {header_match.group(2)}"
            in_grid = False
            continue

        # Detect grid data lines: |NN <25 chars>
        data_match = re.match(r'^\|(\d{2})\s(.{25})\s?\|?$', line)
        if data_match and chamber_name:
            grid_row = data_match.group(2)
            if len(grid_row) == GRID_W:
                if not in_grid:
                    current_lines = []
                    in_grid = True
                current_lines.append(grid_row)
                continue

        # If we hit a non-grid line while collecting, finalize if complete
        if in_grid and len(current_lines) > 0:
            if len(current_lines) == GRID_H:
                grids.append((chamber_name, current_lines))
            current_lines = []
            in_grid = False
            chamber_name = None

    # Finalize last grid
    if in_grid and len(current_lines) == GRID_H:
        grids.append((chamber_name, current_lines))

    return grids


def extract_chambers_from_markdown(filepath):
    """
    Extract all chamber grids from a markdown file containing code blocks.
    Returns dict: {chamber_key: {name, grid, annotations}}
    """
    with open(filepath, 'r') as f:
        content = f.read()

    chambers = {}

    # Find all fenced code blocks
    code_block_pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
    in_chamber_section = False
    current_chamber_key = None

    # Parse section headers and their associated code blocks
    sections = re.split(r'\n##\s+', content)

    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        # Extract chamber header
        header = lines[0].strip()
        chamber_match = re.match(r'Chamber\s+([A-Z0-9]+)\s*[—\-–]?\s*(.*)', header)
        if not chamber_match:
            continue

        chamber_id = chamber_match.group(1)
        chamber_title = chamber_match.group(2).strip()
        current_chamber_key = f"Ch.{chamber_id}"

        # Find code block within this section
        code_match = re.search(r'```(\w*)\n(.*?)```', section, re.DOTALL)
        if code_match:
            grid_text = code_match.group(2)
            parsed = parse_ascii_grid(grid_text)
            if parsed:
                name, grid = parsed[0]
                # Extract annotations (lines between code block and next ## header)
                annotations: list[str] = []
                code_end = section.find('```', section.find('```') + 3)
                if code_end > 0:
                    after_code = section[code_end+3:]
                    for aline in after_code.strip().split('\n'):
                        aline = aline.strip()
                        if aline and not aline.startswith('##'):
                            annotations.append(aline)

                chambers[current_chamber_key] = {
                    'name': name or f"{current_chamber_key} {chamber_title}",
                    'grid': grid,
                    'annotations': annotations,
                }

    return chambers


# ── JS chamber IIFE parser ─────────────────────────────────────────────────

def find_matching_brace(text, start):
    """Find the index of the matching closing brace for an opening brace at position start."""
    depth = 0
    in_string = None
    escape_next = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if in_string:
            if ch == in_string:
                in_string = None
            continue
        if ch in ('"', "'", '`'):
            in_string = ch
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def parse_chamber_names(content):
    """Parse CHAMBER_NAMES array from golem.html. Returns list of strings."""
    m = re.search(r'const\s+CHAMBER_NAMES\s*=\s*\[([^\]]+)\]', content)
    if not m:
        return []
    return [s.strip().strip("'\"") for s in m.group(1).split(',')]


def parse_chamber_flow(content):
    """Parse CHAMBER_FLOW array from golem.html. Returns list of strings."""
    m = re.search(r'const\s+CHAMBER_FLOW\s*=\s*\[([^\]]+)\]', content)
    if not m:
        return []
    return [s.strip().strip("'\"") for s in m.group(1).split(',')]


def parse_js_chambers(filepath):
    """
    Parse JavaScript chamber IIFEs from golem.html.
    Simulates the execution of mkGrid and all tile assignments.
    Returns dict: {chamber_key: {name, grid (list of lists), properties}}
    """
    with open(filepath, 'r') as f:
        content = f.read()

    chambers = {}

    # Find comment lines that identify chambers: // Chamber N: ... or // Ch.T: ...
    comment_pattern = re.compile(r'//\s*(Chamber\s+\d+:\s*.*?|Ch\.T:\s*.*?)\r?\n')

    for cm in comment_pattern.finditer(content):
        comment = cm.group(1).strip()

        # Determine chamber identity
        ch_match = re.match(r'Chamber\s+(\d+)', comment)
        ch_match_t = re.match(r'Ch\.T', comment)

        chamber_key = None
        if ch_match:
            chamber_num = int(ch_match.group(1))
            chamber_key = f"Ch.{chamber_num}"
        elif ch_match_t:
            chamber_key = "Ch.T"
        else:
            continue

        # Find the (function(){ after this comment
        after_comment = cm.end()
        iife_start = content.find('(function(){', after_comment)
        if iife_start == -1:
            continue

        # Find matching closing brace for function body
        brace_start = iife_start + len('(function()')
        brace_end = find_matching_brace(content, brace_start)
        if brace_end == -1:
            continue

        body = content[iife_start + len('(function(){'):brace_end]

        # Simulate grid execution
        grid = [[0] * GRID_W for _ in range(GRID_H)]

        # Extract properties from chambers.push
        flow_id = None
        glyphs = []
        push_spawn = None
        push_slot = None

        push_match = re.search(r"chambers\.push\(\{(.+)\}\);", body, re.DOTALL)
        if push_match:
            push_str = push_match.group(1)

            # flowId
            fid_match = re.search(r"flowId:\s*'(\w+)'", push_str)
            if fid_match:
                flow_id = fid_match.group(1)

            # glyphs array
            glyphs_match = re.search(r"glyphs:\s*\[([^\]]*)\]", push_str)
            if glyphs_match:
                glyphs_str = glyphs_match.group(1).strip()
                if glyphs_str:
                    glyph_entries = re.findall(
                        r'\{x:\s*(\d+),\s*y:\s*(\d+)\}', glyphs_str
                    )
                    for gx, gy in glyph_entries:
                        glyphs.append({'x': int(gx), 'y': int(gy)})

            # pushSpawn
            pspawn_match = re.search(
                r'pushSpawn:\s*\{x:\s*(\d+),\s*y:\s*(\d+)\}', push_str
            )
            if pspawn_match:
                push_spawn = {'x': int(pspawn_match.group(1)),
                              'y': int(pspawn_match.group(2))}

            # pushSlot
            pslot_match = re.search(
                r'pushSlot:\s*\{gx:\s*(\d+),\s*gy:\s*(\d+)\}', push_str
            )
            if pslot_match:
                push_slot = {'x': int(pslot_match.group(1)),
                             'y': int(pslot_match.group(2))}

        # Process tile assignments in the body
        # Remove the chambers.push line to avoid parsing it twice
        push_idx = body.find('chambers.push')
        exec_body = body[:push_idx] if push_idx >= 0 else body

        # ── HANDLER ORDERING (FIXED) ──────────────────────────────
        # Priority: boundary loops FIRST (lowest), then range loops,
        # then direct overrides LAST (highest priority).
        # This mirrors how JS executes: boundaries fill the grid,
        # then specific assignments override them.
        # Order: multi_for -> multi_for_y -> multi_for_y_h2 ->
        #        for_loop_x -> for_loop_y -> direct_pattern -> special_door
        # ──────────────────────────────────────────────────────────

        # ── 1. multi_for: for(let x=0;x<w;x++){g[r1][x]=C;g[r2][x]=C;...} ──
        multi_for = re.compile(
            r'for\s*\(\s*let\s+x\s*=\s*0\s*;\s*x\s*<\s*w\s*;\s*x\+\+\s*\)\s*\{'
            r'([^}]+)\}'
        )
        for m in multi_for.finditer(exec_body):
            body_str = m.group(1)
            assignments = re.findall(r'g\[(\d+)\]\[x\]\s*=\s*(\w+);', body_str)
            for row, const_name in assignments:
                row = int(row)
                if const_name in CONST_TO_VALUE:
                    val = CONST_TO_VALUE[const_name]
                    for x in range(GRID_W):
                        if 0 <= row < GRID_H:
                            grid[row][x] = val

        # ── 2. multi_for_y: for(let y=0;y<h;y++){g[y][0]=C;g[y][w-1]=C;} ──
        multi_for_y = re.compile(
            r'for\s*\(\s*let\s+y\s*=\s*0\s*;\s*y\s*<\s*h\s*;\s*y\+\+\s*\)\s*\{'
            r'([^}]+)\}'
        )
        for m in multi_for_y.finditer(exec_body):
            body_str = m.group(1)
            # Handle g[y][0] and g[y][w-1]
            assignments = re.findall(r'g\[y\]\[([\w-]+)\]\s*=\s*(\w+);', body_str)
            for col_expr, const_name in assignments:
                if const_name not in CONST_TO_VALUE:
                    continue
                val = CONST_TO_VALUE[const_name]
                if col_expr == '0':
                    col = 0
                elif col_expr == 'w-1':
                    col = GRID_W - 1
                else:
                    continue
                for y in range(GRID_H):
                    grid[y][col] = val

        # ── 3. multi_for_y_h2: for(let y=0;y<h-2;y++){g[y][w-1]=WALL;} ──
        multi_for_y_h2 = re.compile(
            r'for\s*\(\s*let\s+y\s*=\s*0\s*;\s*y\s*<\s*h\s*-\s*2\s*;\s*y\+\+\s*\)\s*\{'
            r'([^}]+)\}'
        )
        for m in multi_for_y_h2.finditer(exec_body):
            body_str = m.group(1)
            assignments = re.findall(r'g\[y\]\[([\w-]+)\]\s*=\s*(\w+);', body_str)
            for col_expr, const_name in assignments:
                if const_name not in CONST_TO_VALUE:
                    continue
                val = CONST_TO_VALUE[const_name]
                if col_expr == 'w-1':
                    col = GRID_W - 1
                else:
                    continue
                for y in range(GRID_H - 2):
                    grid[y][col] = val

        # ── 3b. multi_for_range_x: for(let x=a;x<op b;x++){g[r1][x]=C;g[r2][x]=C;...} ──
        # Handles arbitrary-range loops with multiple body assignments.
        # e.g. for(let x=8;x<17;x++){g[14][x]=PIT;g[13][x]=PIT;}
        multi_for_range_x = re.compile(
            r'for\s*\(\s*let\s+x\s*=\s*(\d+)\s*;\s*x\s*([<>]=?)\s*(\d+)\s*;\s*x\+\+\s*\)\s*\{'
            r'([^}]+)\}'
        )
        for m in multi_for_range_x.finditer(exec_body):
            x_start = int(m.group(1))
            x_op = m.group(2)
            x_end = int(m.group(3))
            body_str = m.group(4)

            if x_op == '<':
                x_range = range(x_start, x_end)
            elif x_op == '<=':
                x_range = range(x_start, x_end + 1)
            else:
                continue

            assignments = re.findall(r'g\[(\d+)\]\[x\]\s*=\s*(\w+);', body_str)
            for row, const_name in assignments:
                row = int(row)
                if const_name not in CONST_TO_VALUE:
                    continue
                val = CONST_TO_VALUE[const_name]
                for x in x_range:
                    if 0 <= row < GRID_H and 0 <= x < GRID_W:
                        grid[row][x] = val

        # ── 3c. multi_for_range_y: for(let y=a;y<op b;y++){g[y][c1]=C;g[y][c2]=C;...} ──
        multi_for_range_y = re.compile(
            r'for\s*\(\s*let\s+y\s*=\s*(\d+)\s*;\s*y\s*([<>]=?)\s*(\d+)\s*;\s*y\+\+\s*\)\s*\{'
            r'([^}]+)\}'
        )
        for m in multi_for_range_y.finditer(exec_body):
            y_start = int(m.group(1))
            y_op = m.group(2)
            y_end = int(m.group(3))
            body_str = m.group(4)

            if y_op == '<':
                y_range = range(y_start, y_end)
            elif y_op == '<=':
                y_range = range(y_start, y_end + 1)
            else:
                continue

            assignments = re.findall(r'g\[y\]\[([\w-]+)\]\s*=\s*(\w+);', body_str)
            for col_expr, const_name in assignments:
                if const_name not in CONST_TO_VALUE:
                    continue
                val = CONST_TO_VALUE[const_name]
                if col_expr == '0':
                    col = 0
                elif col_expr == 'w-1':
                    col = GRID_W - 1
                else:
                    # Try numeric col
                    try:
                        col = int(col_expr)
                    except ValueError:
                        continue
                for y in y_range:
                    if 0 <= y < GRID_H and 0 <= col < GRID_W:
                        grid[y][col] = val

        # ── 4. for_loop_x: for(let x=a;x<b;x++) g[y][x]=CONSTANT; ──
        for_loop_x = re.compile(
            r'for\s*\(\s*let\s+x\s*=\s*(\d+)\s*;\s*x\s*([<>]=?)\s*(\d+)\s*;\s*x\+\+\s*\)\s*'
            r'g\[(\d+)\]\[x\]\s*=\s*(\w+);'
        )
        for m in for_loop_x.finditer(exec_body):
            x_start = int(m.group(1))
            x_op = m.group(2)
            x_end = int(m.group(3))
            row = int(m.group(4))
            const_name = m.group(5)

            if const_name not in CONST_TO_VALUE:
                continue
            val = CONST_TO_VALUE[const_name]

            if x_op == '<':
                x_range = range(x_start, x_end)
            elif x_op == '<=':
                x_range = range(x_start, x_end + 1)
            else:
                continue

            for x in x_range:
                if 0 <= row < GRID_H and 0 <= x < GRID_W:
                    grid[row][x] = val

        # ── 5. for_loop_y: for(let y=a;y<b;y++) g[y][x]=CONSTANT; ──
        for_loop_y = re.compile(
            r'for\s*\(\s*let\s+y\s*=\s*(\d+)\s*;\s*y\s*([<>]=?)\s*(\d+)\s*;\s*y\+\+\s*\)\s*'
            r'g\[y\]\[(\d+)\]\s*=\s*(\w+);'
        )
        for m in for_loop_y.finditer(exec_body):
            y_start = int(m.group(1))
            y_op = m.group(2)
            y_end = int(m.group(3))
            col = int(m.group(4))
            const_name = m.group(5)

            if const_name not in CONST_TO_VALUE:
                continue
            val = CONST_TO_VALUE[const_name]

            if y_op == '<':
                y_range = range(y_start, y_end)
            elif y_op == '<=':
                y_range = range(y_start, y_end + 1)
            else:
                continue

            for y in y_range:
                if 0 <= y < GRID_H and 0 <= col < GRID_W:
                    grid[y][col] = val

        # ── 6. direct_pattern: g[r][c]=CONSTANT; ── (highest priority)
        direct_pattern = re.compile(r'g\[(\d+)\]\[(\d+)\]\s*=\s*(\w+);')
        for m in direct_pattern.finditer(exec_body):
            row, col, const_name = int(m.group(1)), int(m.group(2)), m.group(3)
            if const_name in CONST_TO_VALUE:
                val = CONST_TO_VALUE[const_name]
                if 0 <= row < GRID_H and 0 <= col < GRID_W:
                    grid[row][col] = val

        # ── 7. special_door: g[h-3][w-1]=CONSTANT; ── (final override)
        special_door = re.compile(r'g\[h-3\]\[w-1\]\s*=\s*(\w+);')
        for m in special_door.finditer(exec_body):
            const_name = m.group(1)
            if const_name in CONST_TO_VALUE:
                row = GRID_H - 3  # h-3
                col = GRID_W - 1  # w-1
                grid[row][col] = CONST_TO_VALUE[const_name]

        chambers[chamber_key] = {
            'name': chamber_key,
            'grid': grid,
            'flow_id': flow_id,
            'glyphs': glyphs,
            'push_spawn': push_spawn,
            'push_slot': push_slot,
        }

    return chambers


# ── Grid comparison ─────────────────────────────────────────────────────────

def grid_to_ascii(grid_values):
    """Convert a value grid to ASCII representation."""
    result = []
    for row in grid_values:
        line = ''
        for val in row:
            line += VALUE_TO_CHAR.get(val, '?')
        result.append(line)
    return result


def compare_grids(md_chamber, js_chamber):
    """
    Compare a markdown ASCII grid with a JS value grid.
    Returns list of mismatches: [(row, col, md_char, md_const, js_val, js_const)]
    """
    md_grid = md_chamber['grid']
    js_grid = js_chamber['grid']

    mismatches = []

    for row in range(GRID_H):
        for col in range(GRID_W):
            md_char = md_grid[row][col] if col < len(md_grid[row]) else '?'
            js_val = js_grid[row][col] if col < len(js_grid[row]) else -1

            if md_char in CHAR_TO_CONST:
                md_const, md_val = CHAR_TO_CONST[md_char]
            else:
                md_const, md_val = f'UNKNOWN({md_char})', -1

            js_const = VALUE_TO_CONST.get(js_val, f'UNKNOWN({js_val})')

            if md_val != js_val:
                mismatches.append({
                    'row': row,
                    'col': col,
                    'md_char': md_char,
                    'md_const': md_const,
                    'md_val': md_val,
                    'js_val': js_val,
                    'js_const': js_const,
                })

    return mismatches


# ── Structural validation ───────────────────────────────────────────────────

def validate_grid(grid_ascii, chamber_key):
    """
    Validate a grid for structural correctness.
    Returns list of (severity, message) tuples.
    """
    issues = []

    # Check dimensions
    if len(grid_ascii) != GRID_H:
        issues.append(('ERROR', f'Expected {GRID_H} rows, got {len(grid_ascii)}'))
        return issues

    for i, row in enumerate(grid_ascii):
        if len(row) != GRID_W:
            issues.append(('ERROR', f'Row {i}: expected {GRID_W} cols, got {len(row)}'))

    # Check for valid characters
    invalid_chars = set()
    for row in grid_ascii:
        for char in row:
            if char not in CHAR_TO_CONST:
                invalid_chars.add(char)
    if invalid_chars:
        issues.append(('ERROR', f'Invalid characters: {invalid_chars}'))

    # Check for exactly one GOLEM_SPAWN
    spawn_count = sum(1 for row in grid_ascii for c in row if c == '^')
    if spawn_count == 0:
        issues.append(('ERROR', 'No GOLEM_SPAWN (^) tile found'))
    elif spawn_count > 1:
        issues.append(('ERROR', f'{spawn_count} GOLEM_SPAWN (^) tiles found, expected 1'))

    # Check spawn has solid floor beneath
    if spawn_count == 1:
        for row_idx, row in enumerate(grid_ascii):
            for col_idx, char in enumerate(row):
                if char == '^':
                    # Check row below
                    if row_idx + 1 < GRID_H:
                        below = grid_ascii[row_idx + 1][col_idx]
                        if below not in ('#', '=', 'S', 'X'):
                            issues.append(('WARN',
                                f'Spawn at ({col_idx},{row_idx}) has no solid floor '
                                f'({below} below)'))

    # Check pits are bordered
    for row_idx, row in enumerate(grid_ascii):
        for col_idx, char in enumerate(row):
            if char == '~':
                # Check neighbors
                neighbors = []
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = row_idx + dy, col_idx + dx
                    if 0 <= ny < GRID_H and 0 <= nx < GRID_W:
                        neighbors.append(grid_ascii[ny][nx])
                    else:
                        neighbors.append('EDGE')
                for i, (n, pos) in enumerate(zip(neighbors, ['above','below','left','right'])):
                    if n not in ('#', '=', 'X', '~', 'M', '@', '^'):
                        pass  # Pits can have air above for gameplay

    return issues


def strict_validate(grid_ascii, chamber_key, js_chamber=None):
    """
    Strict validation mode — comprehensive checks beyond basic structure.
    Returns list of (severity, message) tuples.

    Checks:
    1. Spawn walkability: 3x3 area around spawn is AIR/GOLEM_SPAWN
    2. Spawn floor support: tile below spawn is WALL/PLATFORM (ERROR not WARN)
    3. Pit bordering: left/right of pit tiles must be WALL/PLATFORM/CRACKED/MAGICAL_WALL
    4. Property consistency: pushSpawn matches S, glyphs match *, pushSlot matches AIR
    5. Door reachability: DOOR_D/END_PORTAL has at least one adjacent AIR tile
    6. Unique tiles: exactly one GOLEM_SPAWN, exactly one DOOR_D or END_PORTAL
    """
    issues = []

    # Basic dimension/character validation
    issues.extend(validate_grid(grid_ascii, chamber_key))
    if any(s == 'ERROR' for s, _ in issues):
        return issues

    # Find spawn position
    spawn_pos = None
    spawn_count = 0
    for r in range(GRID_H):
        for c in range(GRID_W):
            if grid_ascii[r][c] == '^':
                spawn_count += 1
                spawn_pos = (r, c)

    # Check exactly one spawn
    if spawn_count != 1:
        # Already reported by validate_grid
        return issues

    # ── 1. Spawn walkability: 3x3 area around spawn ──
    sr, sc = spawn_pos
    walkable = {'.', '^'}  # AIR and GOLEM_SPAWN
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            if dr == 0 and dc == 0:
                continue
            nr, nc = sr + dr, sc + dc
            if 0 <= nr < GRID_H and 0 <= nc < GRID_W:
                tile = grid_ascii[nr][nc]
                if tile not in walkable:
                    issues.append(('WARN',
                        f'Spawn at ({sc},{sr}) has non-walkable tile {tile} at '
                        f'({sc+dc},{sr+dr}) in 3x3 area'))

   # ── 2. Spawn floor support (WARN — spawn over air is valid game design) ──
    if sr + 1 < GRID_H:
        below = grid_ascii[sr + 1][sc]
        if below not in ('#', '='):
            issues.append(('WARN',
                f'Spawn at ({sc},{sr}) has no solid floor immediately below: '\
                f'tile below is {below} (golem will fall — ensure terrain below is solid)'))

    # ── 3. Pit bordering: left/right must be WALL/PLATFORM/CRACKED/MAGICAL_WALL ──
    solid_border = {'#', '=', 'X', 'M'}
    for r in range(GRID_H):
        for c in range(GRID_W):
            if grid_ascii[r][c] == '~':
                # Check left
                if c > 0:
                    left_tile = grid_ascii[r][c - 1]
                    if left_tile not in solid_border and left_tile != '~':
                        issues.append(('ERROR',
                            f'Pit at ({c},{r}) has AIR/non-solid left neighbor {left_tile}'))
                # Check right
                if c < GRID_W - 1:
                    right_tile = grid_ascii[r][c + 1]
                    if right_tile not in solid_border and right_tile != '~':
                        issues.append(('ERROR',
                            f'Pit at ({c},{r}) has AIR/non-solid right neighbor {right_tile}'))

    # ── 4. Property consistency (requires JS chamber data) ──
    if js_chamber:
        # pushSpawn must match PUSH_SPAWN (S) tile
        if js_chamber.get('push_spawn'):
            ps = js_chamber['push_spawn']
            px, py = ps['x'], ps['y']
            if 0 <= py < GRID_H and 0 <= px < GRID_W:
                actual = grid_ascii[py][px]
                if actual != 'S':
                    issues.append(('ERROR',
                        f'pushSpawn property says ({px},{py}) but grid has '
                        f'{actual} there (expected S/PUSH_SPAWN)'))

        # pushSlot must match AIR tile
        if js_chamber.get('push_slot'):
            ps = js_chamber['push_slot']
            gx, gy = ps['x'], ps['y']
            if 0 <= gy < GRID_H and 0 <= gx < GRID_W:
                actual = grid_ascii[gy][gx]
                if actual != '.':
                    issues.append(('ERROR',
                        f'pushSlot property says ({gx},{gy}) but grid has '
                        f'{actual} there (expected ./AIR)'))

        # Glyphs must match * tile
        for gl in js_chamber.get('glyphs', []):
            gx, gy = gl['x'], gl['y']
            if 0 <= gy < GRID_H and 0 <= gx < GRID_W:
                actual = grid_ascii[gy][gx]
                if actual != '*':
                    issues.append(('ERROR',
                        f'Glyph property says ({gx},{gy}) but grid has '
                        f'{actual} there (expected */GLYPH)'))

# ── 5. Door reachability: DOOR_D/END_PORTAL has adjacent AIR or CRACKED tile ──
    for r in range(GRID_H):
        for c in range(GRID_W):
            if grid_ascii[r][c] in ('v', '@'):  # DOOR_D or END_PORTAL
                tile_name = 'DOOR_D' if grid_ascii[r][c] == 'v' else 'END_PORTAL'
                has_reachable_neighbor = False
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < GRID_H and 0 <= nc < GRID_W:
                        n = grid_ascii[nr][nc]
                        if n in ('.', 'X'):  # AIR or CRACKED (breakable)
                            has_reachable_neighbor = True
                            break
                if not has_reachable_neighbor:
                    issues.append(('WARN',
                        f'{tile_name} at ({c},{r}) has no adjacent AIR or CRACKED tile '\
                        f'(may be unreachable without breaking surrounding walls)'))

    # ── 6. Unique tiles: exactly one DOOR_D or END_PORTAL ──
    door_count = sum(1 for r in range(GRID_H) for c in range(GRID_W)
                     if grid_ascii[r][c] == 'v')
    portal_count = sum(1 for r in range(GRID_H) for c in range(GRID_W)
                       if grid_ascii[r][c] == '@')
    exit_count = door_count + portal_count

    if exit_count == 0:
        issues.append(('ERROR', 'No DOOR_D or END_PORTAL tile found'))
    elif exit_count > 1:
        issues.append(('ERROR',
            f'{exit_count} exit tiles found (DOOR_D: {door_count}, END_PORTAL: {portal_count}), '
            f'expected exactly 1'))

    return issues


# ── Flow consistency check ──────────────────────────────────────────────────

def check_flow_consistency(golem_path):
    """
    Parse CHAMBER_FLOW and CHAMBER_NAMES from golem.html.
    Verify flow consistency.
    Returns list of (severity, message) tuples.
    """
    with open(golem_path, 'r') as f:
        content = f.read()

    issues = []

    chamber_names = parse_chamber_names(content)
    chamber_flow = parse_chamber_flow(content)
    js_chambers = parse_js_chambers(golem_path)

    # Check CHAMBER_FLOW length == CHAMBER_NAMES length
    if len(chamber_flow) != len(chamber_names):
        issues.append(('ERROR',
            f'CHAMBER_FLOW length ({len(chamber_flow)}) != CHAMBER_NAMES length ({len(chamber_names)})'))

    # Build set of valid flowIds
    valid_flow_ids = set(chamber_flow)

    # Check each chamber's flowId
    for key, chamber in js_chambers.items():
        fid = chamber.get('flow_id')
        if fid is None:
            # No flowId = special chamber (test chamber)
            if key != 'Ch.T':
                issues.append(('WARN',
                    f'{key} has no flowId (expected only for special chambers like Ch.T)'))
        else:
            if fid not in valid_flow_ids:
                issues.append(('ERROR',
                    f'{key} has flowId "{fid}" which is not in CHAMBER_FLOW '
                    f'({", ".join(chamber_flow)})'))

    # Check for orphaned flowIds (in CHAMBER_FLOW but no matching chamber)
    used_flow_ids = set()
    for key, chamber in js_chambers.items():
        fid = chamber.get('flow_id')
        if fid:
            used_flow_ids.add(fid)

    orphaned = valid_flow_ids - used_flow_ids
    for fid in sorted(orphaned):
        issues.append(('WARN',
            f'flowId "{fid}" is in CHAMBER_FLOW but no chamber uses it (orphaned)'))

    # Check for missing chambers (flowId referenced but no chamber found)
    expected_chambers = set()
    for i, name in enumerate(chamber_names):
        expected_chambers.add(f'Ch.{i}')
    found_chambers = set(js_chambers.keys())
    missing = expected_chambers - found_chambers
    for ch in sorted(missing):
        issues.append(('ERROR', f'Expected chamber {ch} (in CHAMBER_NAMES) but not found in code'))

    return issues


# ── ASCII export ────────────────────────────────────────────────────────────

def format_chamber_name(chamber_key, chamber_names):
    """Get display name for a chamber key."""
    if chamber_key == 'Ch.T':
        return '[TEST CHAMBER]'
    # Try to match Ch.N to CHAMBER_NAMES index
    m = re.match(r'Ch\.(\d+)', chamber_key)
    if m:
        idx = int(m.group(1))
        if idx < len(chamber_names):
            return chamber_names[idx]
    return chamber_key


def export_ascii_grid(js_chambers, chamber_names, output_path=None):
    """
    Export parsed JS chambers as clean ASCII markdown grids.

    Output format:
      # Chamber Data

      Existing chambers parsed from `golem.html`. See `chamber-template.md` for the
      legend, format spec, and extraction/conversion instructions.

      ## Chamber 0 — Awakening

      ```
      +-----------------------------+
      | Ch.0 Awakening              |
      +-----------------------------+
      |00 ######################### |
      ...
      |14 ######################### |
      +-----------------------------+
      ```
    """
    lines = []
    lines.append('# Chamber Data')
    lines.append('')
    lines.append('Existing chambers parsed from `golem.html`. See `chamber-template.md` for the')
    lines.append('legend, format spec, and extraction/conversion instructions.')

    # Sort chambers: Ch.0, Ch.1, ..., Ch.T last
    ordered_keys = []
    numeric_keys = []
    special_keys = []
    for key in js_chambers:
        m = re.match(r'Ch\.(\d+)', key)
        if m:
            numeric_keys.append((int(m.group(1)), key))
        else:
            special_keys.append(key)
    numeric_keys.sort()
    for _, key in numeric_keys:
        ordered_keys.append(key)
    for key in special_keys:
        ordered_keys.append(key)

    for key in ordered_keys:
        ch = js_chambers[key]
        grid_ascii = grid_to_ascii(ch['grid'])

        # Determine display name
        display_name = format_chamber_name(key, chamber_names)

        # Determine section header
        if key == 'Ch.T':
            section_header = '## Chamber T — Test Chamber (no flowId)'
        else:
            m = re.match(r'Ch\.(\d+)', key)
            if m:
                idx = int(m.group(1))
                section_header = f'## Chamber {idx} — {display_name}'
            else:
                section_header = f'## {key}'

        lines.append('')
        lines.append(section_header)
        lines.append('')
        lines.append('```')

        # Border top
        lines.append('+-----------------------------+')

        # Title row (padded to fit within border)
        title = f' Ch.{key.split(".", 1)[1] if "." in key else key} {display_name}'
        title_padded = title.ljust(27)
        lines.append(f'|{title_padded}|')

        # Border mid
        lines.append('+-----------------------------+')

        # Data rows
        for row_idx, row_str in enumerate(grid_ascii):
            lines.append(f'|{row_idx:02d} {row_str} |')

        # Border bottom
        lines.append('+-----------------------------+')

        lines.append('```')

    lines.append('')

    result = '\n'.join(lines)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(result)
        print(f'Exported {len(ordered_keys)} chamber(s) to {output_path}')
    else:
        print(result)

    return result


# ── Output formatting ──────────────────────────────────────────────────────

def print_mismatch_table(mismatches, chamber_key):
    """Print a formatted table of mismatches."""
    if not mismatches:
        print(f"\n  [OK] {chamber_key}: No mismatches (0 differences)\n")
        return

    print(f"\n  [MISMATCH] {chamber_key}: {len(mismatches)} tile difference(s)\n")
    print(f"  {'Row':>3} {'Col':>3}  {'Grid':^6} {'Grid Label':>12}  |  {'Code':>6} {'Code Label':>12}")
    print(f"  {'-'*3} {'-'*3}  {'-'*6} {'-'*12}  |  {'-'*6} {'-'*12}")

    for m in mismatches:
        print(f"  R{m['row']:>2}  C{m['col']:>2}  '{m['md_char']:^4}'  {m['md_const']:>12}  |  "
              f"{m['js_val']:>6}  {m['js_const']:>12}")

    print()


def print_validation_report(issues, chamber_key):
    """Print validation issues."""
    if not issues:
        print(f"  [VALID] {chamber_key}: No issues found\n")
        return

    print(f"\n  {chamber_key} validation issues:\n")
    for severity, msg in issues:
        print(f"    [{severity}] {msg}")
    print()


def print_grid_side_by_side(md_chamber, js_chamber, chamber_key, mismatches):
    """Print the ASCII grids side by side for visual comparison."""
    print(f"\n  --- {chamber_key} visual comparison ---\n")

    md_grid = md_chamber['grid']
    js_ascii = grid_to_ascii(js_chamber['grid'])

    mismatch_set = {(m['row'], m['col']) for m in mismatches}

    for row in range(GRID_H):
        md_line = md_grid[row]
        js_line = js_ascii[row]

        # Mark mismatched positions
        md_marked = ''
        js_marked = ''
        for col in range(GRID_W):
            if (row, col) in mismatch_set:
                md_marked += f'[{md_line[col]}]'
                js_marked += f'[{js_line[col]}]'
            else:
                md_marked += f' {md_line[col]} '
                js_marked += f' {js_line[col]} '

        print(f"  R{row:>2}: MD: {md_marked}")
        print(f"        JS: {js_marked}")

    print()


# ── Main CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Golem Game chamber diff/verification tool'
    )
    parser.add_argument('--chamber', '-c', type=str, default=None,
                        help='Diff specific chamber (e.g., "T" or "0")')
    parser.add_argument('--validate', '-v', type=str, default=None,
                        help='Validate a markdown file (grid structure only)')
    parser.add_argument('--diff-proposal', '-d', type=str, nargs=2,
                        metavar=('DATA', 'PROPOSAL'),
                        help='Diff proposal against existing data')
    parser.add_argument('--visual', action='store_true',
                        help='Show visual side-by-side comparison')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Only show mismatches, not OK results')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    parser.add_argument('--project-root', type=str, default=None,
                        help='Path to project root (default: auto-detect)')
    parser.add_argument('--export-ascii', type=str, nargs='?', const='', default=None,
                        metavar='OUTPUT.md',
                        help='Export JS chambers as ASCII markdown grids')
    parser.add_argument('--strict', action='store_true',
                        help='Run strict validation (enhanced checks)')
    parser.add_argument('--check-flow', action='store_true',
                        help='Check CHAMBER_FLOW and chamber flowId consistency')
    parser.add_argument('--against-js', type=str, default=None,
                        help='Path to golem.html for three-way diff (use with --diff-proposal)')

    args = parser.parse_args()

    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent

    golem_path = project_root / 'golem.html'
    data_path = project_root / 'chamber-data.md'
    proposal_path = project_root / 'chamber-proposal.md'

    # ── Check-flow mode ──
    if args.check_flow:
        if not golem_path.exists():
            print(f"Error: golem.html not found at {golem_path}")
            sys.exit(1)

        print("=" * 60)
        print("  Chamber Flow Consistency Check")
        print(f"  Analyzing: {golem_path}")
        print("=" * 60)

        issues = check_flow_consistency(str(golem_path))
        if not issues:
            print("\n  [OK] All flow checks passed.\n")
            print("  CHAMBER_FLOW matches CHAMBER_NAMES length.")
            print("  All chamber flowIds are valid.")
            print("  No orphaned flowIds found.\n")
            sys.exit(0)
        else:
            print("\n  Flow consistency issues:\n")
            for severity, msg in issues:
                print(f"    [{severity}] {msg}")
            has_errors = any(s == 'ERROR' for s, _ in issues)
            print()
            sys.exit(1 if has_errors else 0)

    # ── Export ASCII mode ──
    if args.export_ascii is not None:
        if not golem_path.exists():
            print(f"Error: golem.html not found at {golem_path}")
            sys.exit(1)

        # Parse chamber names and chambers from golem.html
        with open(golem_path, 'r') as f:
            content = f.read()
        chamber_names = parse_chamber_names(content)
        js_chambers = parse_js_chambers(str(golem_path))

        if not js_chambers:
            print("Error: No chambers found in golem.html")
            sys.exit(1)

        output_path = args.export_ascii if args.export_ascii else None
        export_ascii_grid(js_chambers, chamber_names, output_path)
        sys.exit(0)

    # ── Validate mode ──
    if args.validate:
        vpath = Path(args.validate)
        if not vpath.is_absolute():
            vpath = project_root / vpath

        if not vpath.exists():
            print(f"Error: File not found: {vpath}")
            sys.exit(1)

        # Parse JS chambers for property consistency checks
        js_chambers = {}
        if golem_path.exists():
            js_chambers = parse_js_chambers(str(golem_path))

        md_chambers = extract_chambers_from_markdown(str(vpath))
        all_valid = True

        print("=" * 60)
        print(f"  {'Strict Validation' if args.strict else 'Validation'}: {vpath.name}")
        print("=" * 60)

        for key, chamber in md_chambers.items():
            js_ch = js_chambers.get(key)
            if args.strict:
                issues = strict_validate(chamber['grid'], key, js_ch)
            else:
                issues = validate_grid(chamber['grid'], key)
            print_validation_report(issues, key)
            if any(s == 'ERROR' for s, _ in issues):
                all_valid = False

        if all_valid:
            print("\nAll chambers passed validation.\n")
            sys.exit(0)
        else:
            print("\nSome chambers have validation errors.\n")
            sys.exit(1)

    # ── Diff proposal mode (with optional three-way) ──
    if args.diff_proposal:
        data_file = Path(args.diff_proposal[0])
        proposal_file = Path(args.diff_proposal[1])
        if not data_file.is_absolute():
            data_file = project_root / data_file
        if not proposal_file.is_absolute():
            proposal_file = project_root / proposal_file

        if not data_file.exists():
            print(f"Error: Data file not found: {data_file}")
            sys.exit(1)
        if not proposal_file.exists():
            print(f"Error: Proposal file not found: {proposal_file}")
            sys.exit(1)

        print("=" * 60)
        print("  Proposal vs Existing Data Diff")
        if args.against_js:
            print("  (Three-way: includes JS code comparison)")
        print("=" * 60)

        existing = extract_chambers_from_markdown(str(data_file))
        proposal = extract_chambers_from_markdown(str(proposal_file))

        # Optionally parse JS for three-way diff
        js_chambers = {}
        if args.against_js:
            js_path = Path(args.against_js)
            if not js_path.is_absolute():
                js_path = project_root / js_path
            if not js_path.exists():
                print(f"Error: JS file not found: {js_path}")
                sys.exit(1)
            js_chambers = parse_js_chambers(str(js_path))

        for pkey, pchamber in proposal.items():
            print(f"\n  --- {pkey} ---")

            pgrid = pchamber['grid']

            if pkey in existing:
                egrid = existing[pkey]['grid']
                mismatches = []
                for row in range(GRID_H):
                    for col in range(GRID_W):
                        if col < len(egrid[row]) and col < len(pgrid[row]):
                            ec = egrid[row][col]
                            pc = pgrid[row][col]
                            if ec != pc:
                                mismatches.append({
                                    'row': row, 'col': col,
                                    'md_char': pc,
                                    'md_const': CHAR_TO_CONST.get(pc, ('?', -1))[0],
                                    'md_val': CHAR_TO_CONST.get(pc, ('?', -1))[1],
                                    'js_val': CHAR_TO_CONST.get(ec, ('?', -1))[1],
                                    'js_const': CHAR_TO_CONST.get(ec, ('?', -1))[0],
                                })
                print(f"  Changes vs existing: {len(mismatches)} tile(s) changed")
                for m in mismatches:
                    print(f"    R{m['row']}C{m['col']}: "
                          f"'{m['md_char']}' ({m['md_const']}) <- "
                          f"'{m['js_const']}' [was]")
            else:
                print(f"  NEW chamber (not in existing data)")

            # Three-way: validate proposal against JS
            if pkey in js_chambers:
                js_ch = js_chambers[pkey]
                js_ascii = grid_to_ascii(js_ch['grid'])
                js_mismatches = []
                for row in range(GRID_H):
                    for col in range(GRID_W):
                        if col < len(pgrid[row]):
                            pc = pgrid[row][col]
                            if pc != js_ascii[row][col]:
                                js_mismatches.append({
                                    'row': row, 'col': col,
                                    'proposal': pc,
                                    'proposal_const': CHAR_TO_CONST.get(pc, ('?', -1))[0],
                                    'js': js_ascii[row][col],
                                    'js_const': CHAR_TO_CONST.get(js_ascii[row][col], ('?', -1))[0],
                                })
                if js_mismatches:
                    print(f"  vs JS code: {len(js_mismatches)} tile(s) differ")
                    for m in js_mismatches:
                        print(f"    R{m['row']}C{m['col']}: "
                              f"proposal '{m['proposal']}' ({m['proposal_const']}) "
                              f"vs js '{m['js']}' ({m['js_const']})")
                else:
                    print(f"  vs JS code: MATCH (all tiles consistent)")

            # Strict validation on proposal
            if args.strict and pkey in js_chambers:
                issues = strict_validate(pchamber['grid'], pkey, js_chambers[pkey])
                if issues:
                    print(f"  Strict validation issues:")
                    for sev, msg in issues:
                        print(f"    [{sev}] {msg}")
                else:
                    print(f"  Strict validation: PASSED")

        sys.exit(0)

    # ── Default mode: diff chamber-data.md vs golem.html ──
    if not data_path.exists():
        print(f"Error: chamber-data.md not found at {data_path}")
        sys.exit(1)
    if not golem_path.exists():
        print(f"Error: golem.html not found at {golem_path}")
        sys.exit(1)

    mode_label = "Strict" if args.strict else "Standard"
    print("=" * 60)
    print(f"  Golem Game Chamber Diff ({mode_label} mode)")
    print(f"  Comparing: chamber-data.md vs golem.html")
    print(f"  Coordinate convention: (col, row) = (x, y)")
    print("=" * 60)

    # Parse both sources
    md_chambers = extract_chambers_from_markdown(str(data_path))
    js_chambers = parse_js_chambers(str(golem_path))

    if not md_chambers:
        print("\nError: No chambers found in chamber-data.md")
        sys.exit(1)
    if not js_chambers:
        print("\nError: No chambers found in golem.html")
        sys.exit(1)

    all_keys = sorted(set(list(md_chambers.keys()) + list(js_chambers.keys())))

    total_mismatches = 0
    total_chambers = 0
    total_validation_errors = 0

    for key in all_keys:
        if args.chamber and key != f"Ch.{args.chamber}":
            continue

        if key not in md_chambers:
            print(f"\n  [NOTE] {key}: In golem.html but not in chamber-data.md")
            continue
        if key not in js_chambers:
            print(f"\n  [NOTE] {key}: In chamber-data.md but not in golem.html")
            continue

        md_ch = md_chambers[key]
        js_ch = js_chambers[key]

        # Strict validation first
        strict_issues = []
        if args.strict:
            strict_issues = strict_validate(md_ch['grid'], key, js_ch)
            if any(s == 'ERROR' for s, _ in strict_issues):
                print(f"\n  [STRICT] {key}: Validation issues")
                print_validation_report(strict_issues, key)
                total_validation_errors += sum(1 for s, _ in strict_issues if s == 'ERROR')
            # Also run normal validation for WARN-level issues
            normal_issues = validate_grid(md_ch['grid'], key)
            for sev, msg in normal_issues:
                if sev == 'WARN' and not any(m == msg for _, m in strict_issues):
                    print(f"    [WARN] {msg}")

        # Tile comparison
        mismatches = compare_grids(md_ch, js_ch)
        total_chambers += 1

        if args.json:
            result = {
                'chamber': key,
                'mismatches': len(mismatches),
                'details': mismatches,
            }
            if args.strict:
                result['validation'] = strict_issues
            print(json.dumps(result, indent=2))
        else:
            if mismatches:
                total_mismatches += len(mismatches)
                print_mismatch_table(mismatches, key)
                if args.visual:
                    print_grid_side_by_side(md_ch, js_ch, key, mismatches)
            elif not args.quiet:
                if args.strict:
                    # Only print OK if no strict validation errors
                    strict_issues = strict_validate(md_ch['grid'], key, js_ch)
                    if not any(s == 'ERROR' for s, _ in strict_issues):
                        print(f"\n  [OK] {key}: No mismatches, strict validation passed")
                    else:
                        print(f"\n  [WARN] {key}: No tile mismatches, but strict validation found issues")
                else:
                    print(f"\n  [OK] {key}: No mismatches")

    print(f"\n{'=' * 60}")
    if args.json:
        pass
    else:
        print(f"  Summary: {total_chambers} chamber(s) compared, "
              f"{total_mismatches} total mismatch(es)")
        if args.strict:
            print(f"  Strict validation errors: {total_validation_errors}")
        if total_mismatches == 0 and total_validation_errors == 0:
            print("  All chambers are in sync.\n")
        else:
            print("  ACTION REQUIRED: Fix mismatches in chamber-data.md\n")

    sys.exit(0 if (total_mismatches == 0 and total_validation_errors == 0) else 1)


if __name__ == '__main__':
    main()
