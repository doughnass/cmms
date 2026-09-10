import re
import sys

HTML_PATH = r'd:\Python\CMMS\cmms_project\cmms\templates\maintenance\daily_capacity.html'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# Extract script contents (all <script>...</script>)
script_re = re.compile(r'<script[^>]*>([\s\S]*?)<\/script>', re.I)
matches = script_re.findall(text)
if not matches:
    print('No <script> blocks found in file')
    sys.exit(1)

# We'll analyze concatenation of all script blocks
script_text = '\n'.join(matches)

pairs = {'{':'}','[':']','(':')'}
opening = set(pairs.keys())
closing = set(pairs.values())
stack = []
errors = []

in_single = False
in_double = False
in_backtick = False
escape = False

line = 1
col = 0
positions = []

for i,ch in enumerate(script_text):
    col += 1
    if ch == '\n':
        line += 1
        col = 0
        escape = False
        continue

    if escape:
        escape = False
        continue

    if ch == '\\':
        escape = True
        continue

    # If in single-quoted string
    if in_single:
        if ch == "'":
            in_single = False
        continue
    if in_double:
        if ch == '"':
            in_double = False
        continue
    if in_backtick:
        if ch == '`':
            in_backtick = False
        continue

    # Not in any string
    if ch == "'":
        in_single = True
        continue
    if ch == '"':
        in_double = True
        continue
    if ch == '`':
        in_backtick = True
        continue

    if ch in opening:
        stack.append((ch, line, col))
        continue
    if ch in closing:
        # find the last opening that matches
        if not stack:
            errors.append((line, col, 'Unmatched closing ' + ch))
        else:
            last, l, c = stack[-1]
            if pairs[last] == ch:
                stack.pop()
            else:
                errors.append((line, col, f'Expected {pairs[last]} but found {ch} (opened at {l}:{c})'))

# Report
if in_single:
    errors.append(('EOF', 'EOF', "Unclosed single-quoted string '"))
if in_double:
    errors.append(('EOF', 'EOF', 'Unclosed double-quoted string "'))
if in_backtick:
    errors.append(('EOF', 'EOF', 'Unclosed template literal `'))

if stack:
    for ch,l,c in stack:
        errors.append((l,c, f"Unclosed {ch} opened at {l}:{c}"))

if errors:
    print('Found potential syntax problems in script content:')
    for e in errors:
        print('-', e)
    sys.exit(2)
else:
    print('No obvious unbalanced braces/quotes/backticks found in script blocks')
    sys.exit(0)
