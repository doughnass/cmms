# คู่มือการใช้งาน: ซิงค์วันหยุดจาก API

## 📚 สารบัญ
1. [ภาพรวมระบบ](#ภาพรวมระบบ)
2. [วิธีใช้งาน](#วิธีใช้งาน)
3. [การทำงานของ API](#การทำงานของ-api)
4. [ตัวอย่างการใช้งาน](#ตัวอย่างการใช้งาน)
5. [FAQ](#faq)

---

## ภาพรวมระบบ

ระบบใหม่นี้ช่วยให้คุณ**ดึงข้อมูลวันหยุดราชการไทยจาก workalendar API** และเทียบกับไฟล์ JSON ที่มีอยู่ **โดยอัตโนมัติ** 

### 🎯 จุดเด่น:
- ✅ **ไม่ต้องแก้ไข JSON เอง** - ระบบดึงข้อมูลจาก API แทน
- ✅ **เทียบข้อมูลแบบอัจฉริยะ** - แสดงว่าวันหยุดไหนใหม่/เปลี่ยนแปลง/ถูกลบ
- ✅ **ควบคุมได้** - เลือกว่าจะอัปเดต JSON, Database หรือทั้งสอง
- ✅ **ไม่ต้องใช้ internet API** - ใช้ workalendar library (คำนวณเอง)
- ✅ **รองรับวันหยุดจันทรคติ** - เช่น วันวิสาขบูชา, วันมาฆบูชา

---

## วิธีใช้งาน

### 1. เปิดหน้าจัดการวันหยุด
ไปที่เมนู **Maintenance > Technicians > Availability Management** แล้วคลิกปุ่ม **"Manage Holidays"**

### 2. คลิกปุ่ม "ซิงค์จาก API"
ใน Import Dialog จะเห็นปุ่ม:
```
🌐 ซิงค์จาก API (เทียบข้อมูล)
```

### 3. ดูผลการเปรียบเทียบ
ระบบจะแสดง Dialog เปรียบเทียบ:

#### 📊 สรุปการเปรียบเทียบ:
- **🆕 วันหยุดใหม่** (สีเขียว) - วันหยุดที่ API มีแต่ JSON ไม่มี
- **✏️ วันหยุดที่เปลี่ยนแปลง** (สีเหลือง) - วันที่เดียวกัน แต่เปลี่ยนชื่อ
- **❌ วันหยุดที่ถูกลบ** (สีแดง) - วันหยุดที่ JSON มีแต่ API ไม่มี
- **⚪ ไม่เปลี่ยนแปลง** (สีเทา) - ข้อมูลตรงกัน

### 4. เลือกการดำเนินการ

คุณมี 3 ตัวเลือก:

| ปุ่ม | การทำงาน |
|------|---------|
| **ปิด** | ไม่ทำอะไร (แค่ดูข้อมูล) |
| **อัปเดต JSON เท่านั้น** | แก้ไข `thai_holidays.json` แต่ไม่เปลี่ยน Database |
| **อัปเดตทั้ง JSON + Database** | แก้ไขทั้ง JSON และนำเข้า Database |

---

## การทำงานของ API

### Backend: `views_holiday.py`

```python
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def holiday_sync_from_api(request):
    """
    Sync holidays from workalendar API
    
    Body params:
    - years: [2025, 2026]
    - update_json: true/false
    - import_to_db: true/false
    """
```

### Flow Chart:

```
1. ผู้ใช้คลิกปุ่ม "ซิงค์จาก API"
   ↓
2. Frontend เรียก POST /api/holidays/sync-from-api/
   ↓
3. Backend:
   - ดึงข้อมูลจาก workalendar.asia.Thailand
   - อ่าน thai_holidays.json
   - เปรียบเทียบทั้งสองชุดข้อมูล
   ↓
4. ส่งผลลัพธ์กลับ:
   {
     comparison: { new: [...], updated: [...], unchanged: [...], removed: [...] },
     summary: { new_count, updated_count, unchanged_count, removed_count }
   }
   ↓
5. Frontend แสดง Dialog เปรียบเทียบ
   ↓
6. ถ้าผู้ใช้เลือก "อัปเดต":
   - เรียก API อีกครั้งด้วย update_json=true และ/หรือ import_to_db=true
   - Backend ทำการอัปเดตตามที่เลือก
```

---

## ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ตรวจสอบความแตกต่าง

**สถานการณ์:** ต้องการดูว่ามีวันหยุดใหม่จาก API หรือไม่

1. คลิก "ซิงค์จาก API"
2. รอสักครู่ (3-5 วินาที)
3. ดูผลการเปรียบเทียบ
4. ถ้าไม่ต้องการอัปเดต → คลิก "ปิด"

### ตัวอย่างที่ 2: อัปเดต JSON (เก็บ Backup)

**สถานการณ์:** ต้องการอัปเดตไฟล์ JSON เพื่อใช้ในอนาคต แต่ยังไม่ต้องการนำเข้า Database

1. คลิก "ซิงค์จาก API"
2. ตรวจสอบการเปลี่ยนแปลง
3. คลิก **"อัปเดต JSON เท่านั้น"**
4. ไฟล์ `cmms/data/thai_holidays.json` จะถูกแก้ไข

### ตัวอย่างที่ 3: อัปเดตทั้งหมด

**สถานการณ์:** ต้องการอัปเดตทั้ง JSON และ Database

1. คลิก "ซิงค์จาก API"
2. ตรวจสอบการเปลี่ยนแปลง
3. คลิก **"อัปเดตทั้ง JSON + Database"**
4. ทั้ง JSON และ Database จะถูกอัปเดต
5. รายการวันหยุดจะรีเฟรชอัตโนมัติ

---

## FAQ

### ❓ API นี้ดึงข้อมูลจากไหน?
**ตอบ:** ใช้ **workalendar library** (https://github.com/workalendar/workalendar)
- ไม่ใช่ internet API (ไม่ต้องต่อเน็ต)
- คำนวณวันหยุดจากปฏิทินไทย
- รองรับวันหยุดจันทรคติ

### ❓ ถ้า workalendar ข้อมูลไม่ถูกต้องล่ะ?
**ตอบ:** 
1. กด "ปิด" ใน Dialog (ไม่อัปเดตอะไร)
2. แก้ไข JSON เองด้วยมือ
3. หรือรายงาน issue ที่ workalendar GitHub

### ❓ ข้อมูลในไฟล์ JSON จะหายไหม?
**ตอบ:** ไม่หาย! เว้นแต่คุณเลือก "อัปเดต JSON" - แต่ถ้าต้องการ backup:
```bash
cp cmms/data/thai_holidays.json cmms/data/thai_holidays.json.backup
```

### ❓ ทำไมต้องมีทั้ง JSON และ Database?
**ตอบ:**
- **JSON** = ข้อมูลต้นฉบับ (master data)
- **Database** = ข้อมูลที่ใช้งานจริง (มีประวัติ, created_by, etc.)

### ❓ กี่ครั้งควรซิงค์?
**แนะนำ:**
- **ปีละ 1 ครั้ง** (ช่วงต้นปี)
- หรือเมื่อรัฐบาลประกาศวันหยุดเพิ่มเติม

### ❓ ถ้า workalendar library ล้าสมัยล่ะ?
**อัปเดต library:**
```bash
pip install --upgrade workalendar
```

### ❓ ถ้าต้องการซิงค์หลายปีพร้อมกัน?
**ตอบ:** แก้ไขใน `syncFromAPI()` function:
```javascript
body: JSON.stringify({
  years: [2024, 2025, 2026, 2027],  // เพิ่มปีได้เลย
  update_json: false,
  import_to_db: false
})
```

---

## 🔧 การบำรุงรักษา

### เช็คเวอร์ชัน workalendar
```bash
pip show workalendar
```

### อัปเดต workalendar
```bash
pip install --upgrade workalendar
```

### Backup JSON ก่อนอัปเดต
```bash
cd cmms/data
copy thai_holidays.json thai_holidays.json.bak
```

### Restore JSON ถ้าผิดพลาด
```bash
cd cmms/data
copy thai_holidays.json.bak thai_holidays.json
```

---

## 📝 บันทึกการเปลี่ยนแปลง

### Version 1.0 (2025-10-20)
- ✅ เพิ่ม endpoint `/api/holidays/sync-from-api/`
- ✅ เพิ่มปุ่ม "ซิงค์จาก API" ใน Import Dialog
- ✅ เพิ่ม Dialog เปรียบเทียบข้อมูล
- ✅ รองรับการอัปเดต JSON และ Database แยกกัน
- ✅ ใช้ workalendar.asia.Thailand API

---

## 👨‍💻 สำหรับนักพัฒนา

### ทดสอบ workalendar ใน Python Shell

```python
from workalendar.asia import Thailand

cal = Thailand()
holidays_2025 = cal.holidays(2025)

for date, name in holidays_2025:
    print(f"{date} - {name}")
```

### เทียบกับ JSON Manual

```python
import json
from workalendar.asia import Thailand

cal = Thailand()
api_holidays = {str(d): n for d, n in cal.holidays(2025)}

with open('cmms/data/thai_holidays.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    json_holidays = {h['date']: h['name'] for h in data['years']['2025']}

# Compare
new = set(api_holidays.keys()) - set(json_holidays.keys())
removed = set(json_holidays.keys()) - set(api_holidays.keys())

print(f"New: {len(new)}, Removed: {len(removed)}")
```

### API Endpoint Test (cURL)

```bash
# Test sync (comparison only)
curl -X POST http://localhost:8000/api/holidays/sync-from-api/ \
  -H "Content-Type: application/json" \
  -d '{"years": [2025, 2026], "update_json": false, "import_to_db": false}'
```

---

## 🎉 สรุป

ระบบนี้ช่วยให้คุณ:
1. **ไม่ต้องแก้ไข JSON เอง** อีกต่อไป
2. **มั่นใจ** ว่าข้อมูลวันหยุดเป็นปัจจุบัน
3. **ควบคุมได้** ว่าจะอัปเดตอะไรบ้าง
4. **ดูการเปลี่ยนแปลง** ก่อนอัปเดต

🚀 **Happy Syncing!**
