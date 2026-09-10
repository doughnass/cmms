# Quick Start Guide - CMMS Project

## 🚀 เริ่มต้นใช้งาน

### วิธีที่ 1: ใช้ไฟล์ Batch/PowerShell (แนะนำ)

#### Windows (CMD):
1. Double-click ไฟล์: `start_server.bat`
2. รอจนกว่าจะเห็นข้อความ: `Starting development server at http://127.0.0.1:8000/`
3. เปิด browser ไปที่: http://localhost:8000

#### Windows (PowerShell):
1. Right-click ไฟล์: `start_server.ps1`
2. เลือก "Run with PowerShell"
3. ถ้ามี error เรื่อง execution policy ให้รัน:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. เปิด browser ไปที่: http://localhost:8000

---

### วิธีที่ 2: รันใน Terminal เอง

#### 1. เปิด Terminal (CMD หรือ PowerShell)

```cmd
cd d:\Python\CMMS\cmms_project
```

#### 2. Activate Virtual Environment

**CMD:**
```cmd
.venv\Scripts\activate
```

**PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

#### 3. Start Server

```cmd
python manage.py runserver
```

#### 4. เปิด Browser

ไปที่: http://localhost:8000

---

## 🛑 หยุด Server

กด `CTRL + C` ใน terminal

---

## ⚠️ แก้ปัญหา

### Error: ERR_CONNECTION_REFUSED

**สาเหตุ:** Django server ยังไม่ได้เปิด

**แก้ไข:**
1. ตรวจสอบว่า server กำลังทำงานหรือไม่
2. ถ้าไม่ทำงาน → รัน `start_server.bat` หรือ `python manage.py runserver`

### Error: Port 8000 is already in use

**สาเหตุ:** มี server ทำงานอยู่แล้ว

**แก้ไข:**

**วิธีที่ 1: หยุด server เดิม**
```cmd
# หา process ที่ใช้ port 8000
netstat -ano | findstr :8000

# Kill process (แทน <PID> ด้วยเลขที่ได้)
taskkill /PID <PID> /F
```

**วิธีที่ 2: ใช้ port อื่น**
```cmd
python manage.py runserver 8001
```

### Error: No module named 'django'

**สาเหตุ:** Virtual environment ไม่ได้ activate

**แก้ไข:**
```cmd
.venv\Scripts\activate
pip install -r requirements.txt
```

### Error: Virtual environment not found

**สาเหตุ:** ยังไม่ได้สร้าง virtual environment

**แก้ไข:**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔧 เช็คความพร้อม

### ตรวจสอบ Python Version

```cmd
python --version
```

ควรได้: Python 3.8 หรือสูงกว่า

### ตรวจสอบ Django Installation

```cmd
.venv\Scripts\activate
python -m django --version
```

### ตรวจสอบ Dependencies

```cmd
pip list
```

ควรมี:
- Django >= 4.0
- workalendar >= 17.0
- (อื่นๆ ตาม requirements.txt)

---

## 📦 Setup ครั้งแรก (First Time Only)

### 1. Clone/Download โปรเจค

```cmd
cd d:\Python\CMMS
```

### 2. สร้าง Virtual Environment

```cmd
python -m venv .venv
```

### 3. Activate Virtual Environment

```cmd
.venv\Scripts\activate
```

### 4. ติดตั้ง Dependencies

```cmd
pip install -r requirements.txt
```

### 5. Run Migrations

```cmd
python manage.py migrate
```

### 6. สร้าง Superuser (ถ้ายังไม่มี)

```cmd
python manage.py createsuperuser
```

### 7. Start Server

```cmd
python manage.py runserver
```

---

## 🎯 URL สำคัญ

| URL | หน้า |
|-----|------|
| http://localhost:8000 | หน้าหลัก |
| http://localhost:8000/admin | Django Admin |
| http://localhost:8000/maintenance/technicians/availability/ | Technician Availability |
| http://localhost:8000/api/holidays/ | Holiday API |

---

## 📝 Workflow ประจำวัน

### เริ่มทำงาน:
1. เปิด terminal
2. รัน: `start_server.bat` (หรือ `python manage.py runserver`)
3. เปิด browser: http://localhost:8000

### ทำงาน:
- แก้ไขโค้ด
- Django จะ auto-reload (ไม่ต้อง restart server)

### จบงาน:
1. กด `CTRL + C` ใน terminal
2. ปิด browser

---

## 🆘 ติดปัญหา?

### Check Server Status

เปิด browser ไปที่: http://localhost:8000

- ✅ เห็นหน้าเว็บ → Server ทำงานปกติ
- ❌ Connection refused → Server ไม่ทำงาน (ต้องเปิดก่อน)
- ❌ Page not found (404) → Server ทำงาน แต่ URL ผิด

### Check Console

เปิด Browser DevTools (F12):
- Console tab → ดู JavaScript errors
- Network tab → ดู API requests

### Check Django Terminal

ดูข้อความใน terminal ที่รัน `runserver`:
- ✅ Status 200 → Request สำเร็จ
- ❌ Status 404 → URL ไม่พบ
- ❌ Status 500 → Server error (ดู traceback)

---

## 💡 Tips

### Auto-reload
Django จะ auto-reload เมื่อแก้ไขไฟล์ Python
แต่ไฟล์ static (CSS, JS) อาจต้อง hard refresh (CTRL + F5)

### Development vs Production
- Development: `python manage.py runserver` (แนะนำ)
- Production: ใช้ WSGI server (Gunicorn, uWSGI, etc.)

### Database
- SQLite: ไฟล์ `db.sqlite3` (Development)
- PostgreSQL/MySQL: สำหรับ Production

---

## 📚 เอกสารเพิ่มเติม

- [Django Documentation](https://docs.djangoproject.com/)
- [Holiday API Implementation](./cmms/docs/holiday_api_implementation.md)
- [Sync from API Guide](./cmms/docs/sync_from_api_guide.md)
- [Holiday Testing Guide](./cmms/docs/holiday_testing_guide.md)

---

**วันที่สร้าง:** 20 ตุลาคม 2568 (2025)  
**Version:** 1.0
