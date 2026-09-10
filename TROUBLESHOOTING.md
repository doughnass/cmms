# 🚨 แก้ปัญหา: ERR_CONNECTION_REFUSED

## ปัญหา

```
Failed to load resource: net::ERR_CONNECTION_REFUSED
Error loading holidays: TypeError: Failed to fetch
```

---

## สาเหตุ

❌ **Django server ไม่ได้เปิด!**

Browser พยายามเรียก `http://localhost:8000/api/holidays/` แต่ไม่มี server ทำงาน

---

## วิธีแก้ไข (3 ขั้นตอน)

### ⚡ ขั้นตอนที่ 1: เปิด Django Server

**ตัวเลือก A: ใช้ไฟล์ .bat (ง่ายที่สุด)**

1. ไปที่โฟลเดอร์: `d:\Python\CMMS\cmms_project`
2. **Double-click**: `start_server.bat`
3. รอจนเห็นข้อความ:
   ```
   Starting development server at http://127.0.0.1:8000/
   ```

**ตัวเลือก B: รัน Terminal เอง**

```cmd
cd d:\Python\CMMS\cmms_project
.venv\Scripts\python.exe manage.py runserver
```

---

### 🔄 ขั้นตอนที่ 2: Refresh Browser

1. กลับไปที่ browser
2. กด **F5** หรือ **CTRL + R** (Refresh)

---

### ✅ ขั้นตอนที่ 3: ทดสอบ

1. คลิกปุ่ม **"Manage Holidays"**
2. Modal ควรเปิดและโหลดข้อมูลได้

---

## เช็คว่า Server ทำงานหรือไม่

### วิธีที่ 1: ดู Terminal
ควรเห็นข้อความแบบนี้:
```
Django version 4.x, using settings 'cmms_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### วิธีที่ 2: เปิด Browser
ไปที่: http://localhost:8000

- ✅ เห็นหน้าเว็บ → **Server ทำงาน**
- ❌ "This site can't be reached" → **Server ไม่ทำงาน**

---

## ปัญหาอื่นๆ ที่อาจพบ

### 🔴 Port 8000 is already in use

**สาเหตุ:** มี server ทำงานอยู่แล้ว

**แก้ไข:**

1. หา process ที่ใช้ port 8000:
```cmd
netstat -ano | findstr :8000
```

2. Kill process (แทน `<PID>` ด้วยตัวเลขที่ได้):
```cmd
taskkill /PID <PID> /F
```

3. หรือใช้ port อื่น:
```cmd
python manage.py runserver 8001
```

---

### 🔴 No module named 'django'

**สาเหตุ:** Virtual environment ไม่ได้ activate

**แก้ไข:**
```cmd
cd d:\Python\CMMS\cmms_project
.venv\Scripts\activate
pip install -r requirements.txt
```

---

### 🔴 Virtual environment not found

**สาเหตุ:** ยังไม่ได้สร้าง venv

**แก้ไข:**
```cmd
cd d:\Python\CMMS\cmms_project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

---

## 📋 Checklist

ก่อนเปิดหน้าเว็บ ตรวจสอบ:

- [ ] Terminal แสดงข้อความ "Starting development server at..."
- [ ] ไปที่ http://localhost:8000 เห็นหน้าเว็บ
- [ ] ไม่มี error ใน terminal
- [ ] Browser ไม่แสดง "ERR_CONNECTION_REFUSED"

ถ้าทุกอย่างเช็คแล้ว:

- [ ] Refresh browser (F5)
- [ ] เปิด Holiday Modal
- [ ] ควรโหลดข้อมูลได้แล้ว ✅

---

## 🎯 สรุป

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|---------|
| ERR_CONNECTION_REFUSED | Server ไม่ทำงาน | รัน `start_server.bat` |
| Port already in use | Server ซ้ำ | Kill process หรือใช้ port อื่น |
| No module named 'django' | Venv ไม่ activate | `pip install -r requirements.txt` |

---

## 🆘 ยังแก้ไม่ได้?

### Debug Steps:

1. **เช็ค Python version**
   ```cmd
   python --version
   ```
   ควรได้ Python 3.8+

2. **เช็ค Virtual Environment**
   ```cmd
   dir .venv\Scripts
   ```
   ควรเห็น `python.exe`, `activate.bat`

3. **เช็ค Dependencies**
   ```cmd
   .venv\Scripts\activate
   pip list
   ```
   ควรเห็น Django, workalendar

4. **เช็ค Database**
   ```cmd
   python manage.py migrate
   ```

5. **ดู Full Error**
   เปิด Browser DevTools (F12) → Console tab

---

## 📚 อ่านเพิ่มเติม

- [QUICKSTART.md](./QUICKSTART.md) - คู่มือเริ่มต้นฉบับเต็ม
- [Sync from API Guide](./cmms/docs/sync_from_api_guide.md) - คู่มือใช้งานฟีเจอร์ซิงค์

---

**ไฟล์นี้สร้างขึ้นเพื่อช่วยแก้ปัญหา ERR_CONNECTION_REFUSED**  
**วันที่:** 20 ตุลาคม 2568 (2025)
