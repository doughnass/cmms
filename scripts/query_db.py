#!/usr/bin/env python3
"""
Query local SQLite DB for ServiceRequest and Technician rows.
"""

import sqlite3
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(root, 'db.sqlite3')

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}", file=sys.stderr)
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def list_tables():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [r['name'] for r in cur.fetchall()]

try:
    tables = list_tables()
except Exception as e:
    print('Error listing tables:', e, file=sys.stderr)
    sys.exit(1)

print('Tables:', len(tables))
for t in tables:
    print(' -', t)


def print_table_info(table):
    try:
        cur.execute(f"PRAGMA table_info('{table}')")
        cols = cur.fetchall()
        print(f"\nSchema for {table}:")
        for c in cols:
            print(f"  {c['name']} ({c['type']})")
    except Exception as e:
        print('Error getting schema for', table, e, file=sys.stderr)

# find ServiceRequest table
sr_table = None
for candidate in ['cmms_servicerequest','servicerequest','service_request','cmms_service_request']:
    if candidate in tables:
        sr_table = candidate
        break

if sr_table is None:
    print('\nServiceRequest table not found; available tables:', tables)
else:
    print(f"\nFound ServiceRequest table: {sr_table}")
    print_table_info(sr_table)
    try:
        cur.execute(f"SELECT id, title, status, requested_at, customer_name, preferred_service_date, notes FROM {sr_table} ORDER BY requested_at DESC LIMIT 50;")
        rows = cur.fetchall()
        print(f"\nLast {len(rows)} ServiceRequest rows:")
        for r in rows:
            requested_at = r['requested_at'] if r['requested_at'] else ''
            print(f"- id={r['id']} status={r['status']} requested_at={requested_at} title={r['title']!r} customer={r['customer_name']!r} preferred_date={r['preferred_service_date']!r}")
    except Exception as e:
        print('Error querying ServiceRequest rows:', e, file=sys.stderr)

# find Technician table
tech_table = None
for candidate in ['cmms_technician','technician','cmms_technicians']:
    if candidate in tables:
        tech_table = candidate
        break

if tech_table:
    print(f"\nFound Technician table: {tech_table}")
    print_table_info(tech_table)
    try:
        cur.execute(f"SELECT id, name, skills, phone, per_day_capacity, active FROM {tech_table} ORDER BY id;")
        rows = cur.fetchall()
        print(f"\nTechnicians ({len(rows)}):")
        for r in rows:
            print(f"- id={r['id']} name={r['name']} skills={r['skills']!r} per_day_capacity={r['per_day_capacity']} active={r['active']}")
    except Exception as e:
        print('Error querying Technician rows:', e, file=sys.stderr)
else:
    print('\nTechnician table not found.')

conn.close()
