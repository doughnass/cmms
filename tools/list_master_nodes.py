import os
import sys

import django

# Ensure project root is on sys.path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
django.setup()

from cmms.models import MasterItem


def build_tree(items):
    by_id = {it.id: {"item": it, "children": []} for it in items}
    roots = []
    for it in items:
        node = by_id[it.id]
        if it.parent_id and it.parent_id in by_id:
            by_id[it.parent_id]["children"].append(node)
        else:
            roots.append(node)

    # sort children by order then label
    def sort_nodes(lst):
        lst.sort(
            key=lambda n: (
                n["item"].order if n["item"].order is not None else 9999,
                str(n["item"].label),
            )
        )
        for c in lst:
            sort_nodes(c["children"])

    sort_nodes(roots)
    return roots


def print_tree(nodes, indent=0):
    for n in nodes:
        it = n["item"]
        print(" " * indent + f"- {it.label} ({it.code}) [id={it.id}]")
        if n["children"]:
            print_tree(n["children"], indent + 4)


def main():
    cats = list(MasterItem.objects.values_list("category", flat=True).distinct())
    if not cats:
        print("No MasterItem categories found.")
        return
    print("Categories found:", ", ".join(cats))
    for cat in cats:
        items = list(MasterItem.objects.filter(category=cat).select_related("parent"))
        if not items:
            continue
        print("\nCategory:", cat)
        roots = build_tree(items)
        print_tree(roots)


if __name__ == "__main__":
    main()
