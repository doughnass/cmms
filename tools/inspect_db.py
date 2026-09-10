import sqlite3, json, os, sys
DB = r'd:\Python\CMMS\cmms_project\db.sqlite3'
if not os.path.exists(DB):
    print('ERROR: DB not found:', DB)
    sys.exit(1)
conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    out = {'tables': tables, 'samples': {}}
    for t in tables:
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info('{t}')").fetchall()]
        owner_cols = [c for c in cols if 'owner' in c or 'equipment' in c or 'code' in c]
        if owner_cols:
            # fetch up to 3 sample rows
            try:
                rows = cur.execute(f"SELECT {', '.join(owner_cols)} FROM {t} LIMIT 3").fetchall()
            except Exception as e:
                rows = [str(e)]
            out['samples'][t] = {'cols': owner_cols, 'rows': rows}
    print(json.dumps(out, ensure_ascii=False, indent=2))
finally:
    conn.close()
