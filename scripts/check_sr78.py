#!/usr/bin/env python3
import sqlite3, os, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db = os.path.join(root, 'db.sqlite3')
if not os.path.exists(db):
    print('DB not found', db); sys.exit(1)
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
sr_id = 78
cur.execute('SELECT id, title, equipment_id, preferred_service_date, status, requested_at FROM cmms_servicerequest WHERE id=?', (sr_id,))
sr = cur.fetchone()
print('SR:', dict(sr) if sr else 'not found')
if sr and sr['equipment_id']:
    cur.execute('SELECT id,equipment_id,equipment_name_TH,equipment_type FROM cmms_equipment_list WHERE id=?', (sr['equipment_id'],))
    eq = cur.fetchone()
    print('Equipment:', dict(eq) if eq else 'not found')
else:
    print('No equipment linked to SR')

if sr and sr['preferred_service_date']:
    pref = sr['preferred_service_date']
    print('preferred_service_date:', pref)
    cur.execute('SELECT id,equipment_id,scheduled_date,notes,created_by_id FROM cmms_maintenanceappointment WHERE scheduled_date=?', (pref,))
    rows = cur.fetchall()
    print('Appointments on that date:', len(rows))
    for r in rows:
        print(dict(r))
else:
    print('No preferred_service_date set')
conn.close()
