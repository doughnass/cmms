import os
from collections import defaultdict

root = r"d:\Python\CMMS\cmms_project"
ext_ext = [".js", ".css"]
files = defaultdict(list)
for dirpath, dirnames, filenames in os.walk(root):
    for fn in filenames:
        if any(fn.endswith(ext) for ext in ext_ext):
            path = os.path.join(dirpath, fn)
            try:
                size = os.path.getsize(path)
            except OSError:
                size = -1
            files[fn].append((size, path))
for fn, items in sorted(files.items()):
    if len(items) > 1:
        print(fn)
        for sz, p in sorted(items, reverse=True):
            print(f"  {sz:8d}  {p}")
