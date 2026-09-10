#!/usr/bin/env python3
"""Simple analyzer to count 'try' vs 'except' occurrences up to a given line and print surrounding context."""
import sys
p = r'd:/Python/CMMS/cmms_project/cmms/views.py'
lines = open(p, 'r', encoding='utf-8').read().splitlines()
for i, line in enumerate(lines[:7400], start=1):
    pass

# Count try/except up to full file and report positions of try without except before next function decorator
try_lines = []
except_lines = []
for i, line in enumerate(lines, start=1):
    s = line.strip()
    if s.startswith('try:'):
        try_lines.append(i)
    if s.startswith('except'):
        except_lines.append(i)

print('Total try:', len(try_lines))
print('Total except:', len(except_lines))
print('\nFirst 10 try lines:', try_lines[:10])
print('First 10 except lines:', except_lines[:10])

# Find any try that doesn't have an except below it before next top-level def or decorator
unmatched = []
for idx in try_lines:
    # find next except after idx
    after_except = [e for e in except_lines if e > idx]
    if not after_except:
        unmatched.append((idx, None))
        continue
    first_except = after_except[0]
    # check if there's a top-level decorator/def between idx and first_except
    between = lines[idx:first_except]
    has_def = any(l.strip().startswith('@') or l.strip().startswith('def ') for l in between)
    if has_def:
        unmatched.append((idx, first_except))

print('\nUnmatched try blocks (try_line, next_except_line or None):')
for u in unmatched:
    print(u)

# Print context around the first unmatched try if any
if unmatched:
    tline = unmatched[0][0]
    start = max(1, tline-5)
    end = tline+10
    print(f"\nContext around line {tline}:\n")
    for ln in range(start, min(end, len(lines))+1):
        prefix = '>' if ln==tline else ' '
        print(f"{prefix}{ln:5d}: {lines[ln-1]}")
else:
    print('\nNo unmatched try blocks detected by heuristic.\n')
