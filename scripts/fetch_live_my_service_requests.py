import urllib.request
import sys
url = 'http://127.0.0.1:8000/my-service-requests'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        status = r.getcode()
        body = r.read(4096)
        print('Status:', status)
        print(body.decode('utf-8', errors='replace')[:2000])
except Exception as e:
    print('Error:', repr(e))
    sys.exit(1)
