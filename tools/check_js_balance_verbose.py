import re
import sys

HTML_PATH = r'd:\Python\CMMS\cmms_project\cmms\templates\maintenance\daily_capacity.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

script_re = re.compile(r'<script[^>]*>([\s\S]*?)<\/script>', re.I)
matches = script_re.findall(text)
if not matches:
    print('No <script> blocks found in file')
    sys.exit(1)

script_text = '\n'.join(matches)
lines = script_text.splitlines()

# Simple check: print a window around problematic lines based on earlier run
# We'll scan for common problematic patterns: unclosed single quotes and backticks

# Print some spans
for i, ln in enumerate(lines[:1200], start=1):
    if i % 200 == 0:
        print(f'-- reached line {i}')

# Now run a simpler search for lone single quote not closed on same line
for i, ln in enumerate(lines, start=1):
    if ln.count("'") % 2 == 1:
        # Potential odd number of single quotes in this line
        print(f'Line {i}: odd single quotes count ->', ln.strip())

# Print specific neighborhoods reported by the other checker
candidates = [61, 452, 397, 259, 658, 660, 784, 1014, 1018, 1019, 1020, 1025, 1070, 1516, 1046, 1070]
for c in sorted(set([x for x in candidates if x <= len(lines)])):
    start = max(1, c-5)
    end = min(len(lines), c+5)
    print('\n--- Context around script line', c, f'(showing {start}-{end})')
    for j in range(start, end+1):
        print(f'{j:5d}: {lines[j-1]}')

print('\nDone')
