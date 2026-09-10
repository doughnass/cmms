import urllib.request
import json

def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body = r.read().decode()
            return (r.getcode(), r.headers.get('Content-Type'), body)
    except Exception as e:
        return (0, '', f"ERROR: {e}")

base='http://127.0.0.1:8000'
endpoints=[
    '/api/maintenance/daily-summary/?date=2025-12-03',
    '/api/equipment/maintenance-schedule/?due_date=2025-12-03',
    '/api/maintenance/technicians/?date=2025-12-03'
]

for ep in endpoints:
    url = base + ep
    print('\n===', url, '===')
    code, ctype, out = fetch(url)
    print('HTTP', code, 'Content-Type:', ctype)
    try:
        parsed = json.loads(out)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception:
        print(out[:400])
        if len(out) > 400:
            print('... (truncated)')

print('\nDone')
