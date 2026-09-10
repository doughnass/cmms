"""
Usage:
  reparent_category_by_prefix.py <child_category> <parent_category> [--dry-run]

This script will iterate MasterItem in child_category, extract a prefix from the child's code
(by splitting at the first underscore) and attempt to find a parent item in parent_category
with that code. If found, it will set child.parent = parent.

Run with --dry-run to preview changes. Use --commit to apply changes.

Examples:
  python tools/reparent_category_by_prefix.py division customers --dry-run
  python tools/reparent_category_by_prefix.py division customers --commit

"""

import argparse
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reparent MasterItem by prefix matching"
    )
    parser.add_argument("child_category")
    parser.add_argument("parent_category")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed"
    )
    parser.add_argument("--commit", action="store_true", help="Apply changes")
    args = parser.parse_args()

    # Setup Django env
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
    try:
        import django

        django.setup()
    except Exception as e:
        print("Error importing Django:", e)
        sys.exit(2)

    from cmms.models import MasterItem

    child_cat = args.child_category
    parent_cat = args.parent_category

    children = MasterItem.objects.filter(category=child_cat).order_by("code")
    total = children.count()
    print(f'Found {total} items in category "{child_cat}"')

    changes = []
    failed = []
    for c in children:
        code = (c.code or "").strip()
        if not code:
            failed.append((c.pk, "no code"))
            continue
        # prefix extraction: before first underscore
        if "_" in code:
            prefix = code.split("_", 1)[0]
        else:
            # fallback: maybe parent code is prefix of code by first N chars (take first token until number)
            # here we simply use the first contiguous letters/digits sequence
            import re

            m = re.match(r"([A-Za-z0-9]+)", code)
            prefix = m.group(1) if m else ""
        if not prefix:
            failed.append((c.pk, "no prefix"))
            continue
        parent = MasterItem.objects.filter(category=parent_cat, code=prefix).first()
        if parent:
            if c.parent_id == parent.pk:
                # already set
                continue
            changes.append((c, parent))
        else:
            failed.append((c.pk, f'parent not found for prefix "{prefix}"'))

    if not changes:
        print("No candidate changes found.")
    else:
        print("Planned changes:")
        for c, p in changes:
            print(
                f"  Child {c.pk} ({c.category}/{c.code}) -> Parent {p.pk} ({p.category}/{p.code})"
            )

    print("\nFailures / unmatched:")
    for f in failed[:50]:
        print(" ", f)

    if args.commit and changes:
        print("\nApplying changes...")
        applied = 0
        for c, p in changes:
            try:
                c.parent = p
                c.save()
                applied += 1
            except Exception as e:
                print("Failed to apply for", c.pk, e)
        print(f"Applied {applied} changes")
    else:
        if changes:
            print("\nRun with --commit to apply these changes")
    print("\nDone")
