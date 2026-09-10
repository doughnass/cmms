import sqlite3, json, os, sys
DB = r'd:\Python\CMMS\cmms_project\db.sqlite3'
if not os.path.exists(DB):
    print('ERROR: DB not found:', DB)
    sys.exit(1)
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute("SELECT id,equipment_code,equipment_name,equipment_owner,equipment_owner_customer,owner,owner_customer FROM cmms_equipment WHERE equipment_owner IS NOT NULL OR owner IS NOT NULL OR equipment_owner_customer IS NOT NULL OR owner_customer IS NOT NULL LIMIT 10;")
    rows = cur.fetchall()
    if not rows:
        print('NO_OWNER_ROWS')
    else:
        out = []
        cols = [d[0] for d in cur.description]
        for r in rows:
            out.append(dict(zip(cols, r)))
        print(json.dumps(out, ensure_ascii=False, indent=2))
finally:
    conn.close()
