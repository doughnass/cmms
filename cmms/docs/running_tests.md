เอกสาร: วิธีรันเทสต์ของโปรเจ็กต์ CMMS (Windows / CI)

ภาพรวม
- โปรเจ็กต์ใช้ Django test runner. สำหรับการรันเทสต์ของแอป `cmms` ให้รันจาก root ของโปรเจ็กต์ (ที่มี `manage.py`).
- บางสภาพแวดล้อมอาจพบปัญหา discovery (เช่น ImportError: 'tests' module incorrectly imported ...) หาก PYTHONPATH มีโฟลเดอร์ที่ทำให้ `tests` ถูก resolve ผิดพลาด เอกสารนี้แนะนำการรันที่ปลอดภัยและการตั้งค่าสำหรับ CI

คำสั่งพื้นฐาน (Windows cmd / PowerShell)
- เปลี่ยน working directory เป็น project root (ตำแหน่งไฟล์ `manage.py`):

  PowerShell / cmd:
  ```powershell
  cd D:\Python\CMMS\cmms_project
  python manage.py test cmms.tests.test_select2_skills
  python manage.py test cmms.tests.test_capacity
  python manage.py test cmms.tests.test_migrate_skills
  ```

- หากต้องการรันทั้งหมดของแอป (อาจขึ้นกับสภาพแวดล้อม):
  ```powershell
  cd D:\Python\CMMS\cmms_project
  python manage.py test cmms
  ```
  หากเจอ ImportError เกี่ยวกับ `tests` ให้ใช้วิธีด้านล่างเพื่อตรวจ/แก้

ตรวจสอบปัญหา PYTHONPATH
- ก่อนรันเทสต์ ให้ตรวจ `sys.path` ว่า project root อยู่ก่อน entry อื่น ๆ ที่อาจมีโฟลเดอร์ชื่อ `tests`:

  สร้างไฟล์ `check_tests_import.py`:
  ```python
  import importlib, sys
  try:
      m = importlib.import_module('tests')
      print('tests module file:', getattr(m, '__file__', None), 'package=', getattr(m, '__package__', None))
  except Exception as e:
      print('import tests failed:', e)
  print('sys.path (first 10):')
  for p in sys.path[:10]:
      print(' ', p)
  ```

  แล้วรัน:
  ```powershell
  python check_tests_import.py
  ```
  ถ้าพบ `tests` ถูก resolve ไปยังที่อื่น ให้ปรับ PYTHONPATH หรือ working directory

ตั้งค่า PYTHONPATH ชั่วคราว (Windows)
- PowerShell:
  ```powershell
  $env:PYTHONPATH = 'D:\Python\CMMS\cmms_project;' + $env:PYTHONPATH
  python manage.py test cmms
  ```
- cmd.exe:
  ```cmd
  set PYTHONPATH=D:\Python\CMMS\cmms_project;%PYTHONPATH%
  python manage.py test cmms
  ```
- (คำสั่งข้างต้นชั่วคราวเฉพาะ session นั้น ๆ)

ตัวอย่าง CI (GitHub Actions)
- ให้ตั้ง working-directory เป็น root ของโปรเจ็กต์ และอย่าเพิ่ม path ที่มีโฟลเดอร์ `tests` ก่อนโปรเจ็กต์

```yaml
name: CI
on: [push]
jobs:
  tests:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install -r requirements.txt
      - name: Run tests
        working-directory: D:\\a\\1\\s # adjust to runner workspace path if needed
        run: |
          python manage.py test cmms
``` 

Fallback: รันเป็นโมดูลเจาะจง
- หาก discovery ยังมีปัญหา ให้รันเทสต์ทีละโมดูลโดยระบุ label เต็ม เช่น:
  ```powershell
  python manage.py test cmms.tests.test_capacity
  ```

สรุป
- แนวทางที่สะอาดที่สุด: รันคำสั่งจาก project root และตรวจให้แน่ใจว่า PYTHONPATH ไม่ชี้ไปยังโฟลเดอร์ที่มี `tests` ก่อนโปรเจ็กต์ของคุณ
- หากต้องการ ผมสามารถเพิ่มสคริปต์ run-tests หรือ CI snippet แบบเจาะจงสำหรับ environment ของคุณ (PowerShell/Windows) ให้เรียบร้อย
