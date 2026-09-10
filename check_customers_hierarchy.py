#!/usr/bin/env python
"""Check customers hierarchy structure."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms.models import MasterItem

# Get all customers
customers = MasterItem.objects.filter(category='customers').order_by('parent_id', 'order', 'label')

print("\n" + "="*80)
print("CUSTOMERS HIERARCHY STRUCTURE")
print("="*80 + "\n")

def get_ancestors(item):
    """Get ancestor chain for an item."""
    ancestors = []
    parent = item.parent
    while parent:
        ancestors.insert(0, parent.label)
        parent = parent.parent
    return ancestors

# Group by root parent
roots = {}
for customer in customers:
    ancestors = get_ancestors(customer)
    root = ancestors[0] if ancestors else customer.label
    if root not in roots:
        roots[root] = []
    roots[root].append((customer, ancestors))

# Print hierarchical structure
total = 0
for root_name in sorted(roots.keys()):
    items = roots[root_name]
    print(f"\n📁 {root_name} (root)")
    
    for customer, ancestors in items:
        total += 1
        if not ancestors:  # This is the root
            continue
        
        level = len(ancestors)
        indent = "   " * (level - 1)
        print(f"{indent}├─ {customer.label}")
        ancestor_path = " > ".join(ancestors)
        print(f"{indent}│  └─ Ancestors: {ancestor_path}")

print(f"\n{'='*80}")
print(f"Total customers: {len(customers)}")
print(f"Hierarchy items shown: {total + len(set(get_ancestors(c)[0] if get_ancestors(c) else c.label for c in customers))}")
print("="*80 + "\n")
