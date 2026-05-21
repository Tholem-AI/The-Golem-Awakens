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
                    # Try numeric literal (e.g., 24)
                    try:
                        col = int(col_expr)
                    except ValueError:
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

        # ── 6. direct: g[y][x]=CONSTANT; ──
        direct_pattern = re.compile(
            r'g\[(\d+)\]\[(\d+)\]\s*=\s*(\w+);'
        )
        for m in direct_pattern.finditer(exec_body):
            row = int(m.group(1))
            col = int(m.group(2))
            const_name = m.group(3)

            if const_name not in CONST_TO_VALUE:
                continue
            val = CONST_TO_VALUE[const_name]
            if 0 <= row < GRID_H and 0 <= col < GRID_W:
                grid[row][col] = val

        # Store result
        chambers[chamber_key] = {
            'name': comment.split(':', 1)[-1].strip() if ':' in comment else comment,
            'grid': grid,
            'flow_id': flow_id,
            'glyphs': glyphs,
            'push_spawn': push_spawn,
            'push_slot': push_slot,
        }

    return chambers


# ── Grid comparison ─────────────────────────────────────────────────────────

def ascii_row_to_values(row_str):
    """Convert an ASCII grid row string to a list of tile values."""
    return [CHAR_TO_CONST.get(ch, ('AIR', 0))[1] for ch in row_str]


def compare_grids(ascii_grid, js_grid, strict=False):
    """
    Compare an ASCII grid with a JS-simulated grid.
    Returns (mismatches, total_cells).
    In strict mode, every cell must match exactly.
    """
    mismatches = []
    ascii_vals = [ascii_row_to_values(row) for row in ascii_grid]

    for y in range(GRID_H):
        for x in range(GRID_W):
            expected = ascii_vals[y][x]
            actual = js_grid[y][x]
            if expected != actual:
                exp_char = VALUE_TO_CHAR.get(expected, '?')
                act_char = VALUE_TO_CHAR.get(actual, '?')
                exp_name = VALUE_TO_CONST.get(expected, 'UNKNOWN')
                act_name = VALUE_TO_CONST.get(actual, 'UNKNOWN')
                mismatches.append((x, y, exp_name, act_name, exp_char, act_char))

    return mismatches, GRID_W * GRID_H


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    base_dir = Path(__file__).parent.parent
    js_file = base_dir / 'golem.html'
    md_file = base_dir / 'chamber-data.md'

    args = sys.argv[1:]

    if not js_file.exists():
        print(f"ERROR: golem.html not found at {js_file}")
        sys.exit(1)

    # Parse JS chambers
    js_chambers = parse_js_chambers(str(js_file))

    if '--check-flow' in args:
        # ── Flow consistency check ──
        with open(js_file) as f:
            content = f.read()

        names = parse_chamber_names(content)
        flow = parse_chamber_flow(content)

        print("=== Flow Consistency Check ===")
        errors = 0

        # Check 1: CHAMBER_NAMES length matches CHAMBER_FLOW length
        if len(names) != len(flow):
            print(f"  FAIL: CHAMBER_NAMES length ({len(names)}) != CHAMBER_FLOW length ({len(flow)})")
            errors += 1
        else:
            print(f"  PASS: Names and Flow lengths match ({len(names)})")

        # Check 2: Each flowId has a corresponding name at same index
        chamber_keys = sorted([k for k in js_chambers.keys() if k != 'Ch.T'],
                             key=lambda k: int(k.split('.')[1]) if k != 'Ch.T' else 99)
        for key in chamber_keys:
            ch_data = js_chambers[key]
            idx = int(key.split('.')[1])
            if ch_data['flow_id']:
                flow_id = ch_data['flow_id']
                if idx < len(flow) and flow[idx] != flow_id:
                    print(f"  FAIL: {key} flowId '{flow_id}' != CHAMBER_FLOW[{idx}] '{flow[idx]}'")
                    errors += 1
                elif idx >= len(flow):
                    print(f"  FAIL: {key} index {idx} out of CHAMBER_FLOW range")
                    errors += 1
                else:
                    print(f"  PASS: {key} flowId '{flow_id}' == CHAMBER_FLOW[{idx}]")

        # Check 3: Flow IDs are unique
        seen = {}
        for i, fid in enumerate(flow):
            if fid in seen:
                print(f"  FAIL: Duplicate flowId '{fid}' at indices {seen[fid]} and {i}")
                errors += 1
            seen[fid] = i
        else:
            print(f"  PASS: All flowIds unique")

        # Check 4: CH.T has no flowId
        if 'Ch.T' in js_chambers:
            if js_chambers['Ch.T']['flow_id']:
                print(f"  WARN: Ch.T has flowId '{js_chambers['Ch.T']['flow_id']}' (should be absent)")
            else:
                print(f"  PASS: Ch.T has no flowId (correct)")

        if errors == 0:
            print("\n  ALL FLOW CHECKS PASSED")
        else:
            print(f"\n  {errors} FLOW ERROR(S)")

        sys.exit(errors)

    if '--strict' in args:
        strict = True
    else:
        strict = False

    # Parse markdown chambers
    if not md_file.exists():
        print(f"ERROR: chamber-data.md not found at {md_file}")
        sys.exit(1)

    md_chambers = extract_chambers_from_markdown(str(md_file))

    if not md_chambers:
        print("ERROR: No chambers found in chamber-data.md")
        sys.exit(1)

    # Chamber filter
    chamber_filter = None
    for i, arg in enumerate(args):
        if arg == '--chamber' and i + 1 < len(args):
            chamber_filter = args[i + 1].upper()
            break

    # Compare each chamber
    total_errors = 0
    for key in sorted(md_chambers.keys()):
        if chamber_filter and key != f"Ch.{chamber_filter}":
            continue

        md_ch = md_chambers[key]
        if key not in js_chambers:
            print(f"\n  {key}: FAIL (not found in JS)")
            total_errors += 1
            continue

        js_ch = js_chambers[key]
        mismatches, total = compare_grids(md_ch['grid'], js_ch['grid'], strict)

        if mismatches:
            print(f"\n  {key} ({md_ch['name']}):")
            print(f"    {len(mismatches)} mismatch(es) out of {total} cells:")
            for mx, my, exp, act, ec, ac in mismatches:
                print(f"      ({mx},{my}): expected {ec}({exp}), got {ac}({act})")
            total_errors += len(mismatches)
        else:
            print(f"\n  {key} ({md_ch['name']}): 0 tile mismatches (pass)")

        # Verify properties
        js_props = js_ch
        if js_props['flow_id']:
            print(f"    flowId: '{js_props['flow_id']}'")
        if js_props['glyphs']:
            print(f"    glyphs: {js_props['glyphs']}")
        if js_props['push_spawn']:
            print(f"    pushSpawn: {js_props['push_spawn']}")
        if js_props['push_slot']:
            print(f"    pushSlot: {js_props['push_slot']}")

    if total_errors == 0:
        print(f"\n  ALL CHECKS PASSED")
    else:
        print(f"\n  {total_errors} ERROR(S) FOUND")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == '__main__':
    main()
