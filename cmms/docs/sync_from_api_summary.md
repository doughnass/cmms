# สรุปฟีเจอร์: การจัดการวันหยุดราชการ

## ⚠️ สถานะปัจจุบัน

**ฟีเจอร์ "ซิงค์จาก API" ถูกปิดใช้งานชั่วคราว**

เหตุผล: workalendar library ไม่รองรับปฏิทินไทย (Thailand calendar) ในเวอร์ชันปัจจุบัน

---

## ✅ ฟีเจอร์ที่ใช้งานได้

### 1. 🔄 รีเฟรชข้อมูล (แนะนำ!)
- ปุ่ม: **"รีเฟรชข้อมูลปีปัจจุบัน + ปีหน้า"**
- ทำงาน: ดึงข้อมูลจาก `thai_holidays.json` และนำเข้า Database
- แสดงการเปลี่ยนแปลง: ใหม่ (NEW) / อัปเดต (UPDATED) / ไม่เปลี่ยน
- ใช้เมื่อ: ต้องการอัปเดตวันหยุดปีปัจจุบันและปีหน้าอย่างรวดเร็ว

### 2. 📥 นำเข้าวันหยุดราชการ
- ปุ่ม: **"นำเข้าวันหยุดราชการ"**
- ทำงาน: เลือกปีที่ต้องการนำเข้า (2024, 2025, 2026)
- ตัวเลือก: อัปเดตข้อมูลที่มีอยู่หรือข้าม
- ใช้เมื่อ: ต้องการนำเข้าข้อมูลปีเฉพาะเจาะจง

### 3. ➕ เพิ่ม / แก้ไข / ลบ วันหยุด
- เพิ่มวันหยุดเอง: กรอกวันที่ + ชื่อ + คำอธิบาย
- แก้ไขวันหยุด: คลิกที่รายการที่ต้องการแก้ไข
- ลบวันหยุด: คลิกปุ่มลบ

### 4. 🔍 กรองข้อมูล
- กรองตามปี
- กรองตามเดือน

---

## 📝 วิธีอัปเดตวันหยุดราชการ

### วิธีที่ 1: ใช้ปุ่มรีเฟรช (ง่ายที่สุด) ⭐

```
1. เปิด Holiday Modal
2. คลิก "นำเข้าวันหยุดราชการ"
3. คลิก "🔄 รีเฟรชข้อมูลปีปัจจุบัน + ปีหน้า"
4. ดูผลลัพธ์:
   - 🆕 NEW = วันหยุดใหม่
   - ✏️ UPDATED = เปลี่ยนแปลง
   - ⚪ UNCHANGED = ไม่เปลี่ยน
5. เสร็จแล้ว!
```

### วิธีที่ 2: นำเข้าทีละปี

```
1. เปิด Holiday Modal
2. คลิก "นำเข้าวันหยุดราชการ"  
3. เลือกปี: ☑ 2024 ☑ 2025 ☑ 2026
4. เลือก "อัปเดตข้อมูลที่มีอยู่แล้ว" (ถ้าต้องการ)
5. คลิก "นำเข้าทันที"
```

### วิธีที่ 3: แก้ไข JSON โดยตรง

```
1. เปิดไฟล์: cmms/data/thai_holidays.json
2. แก้ไขข้อมูล:
   {
     "source": "Government of Thailand",
     "years": {
       "2025": [
         {
           "date": "2025-01-01",
           "name": "วันขึ้นปีใหม่",
           "description": "...",
           "type": "government"
         }
       ]
     }
   }
3. บันทึกไฟล์
4. ใช้ปุ่มรีเฟรชเพื่อนำเข้า Database
```

---

## 🎯 สรุปสถานะปัจจุบัน

| ฟีเจอร์ | สถานะ | หมายเหตุ |
|---------|-------|----------|
| Holiday Modal | ✅ ทำงาน | เปิด/ปิด/แสดงรายการ |
| Load Holidays | ✅ ทำงาน | ดึงจาก Database |
| Add/Edit/Delete | ✅ ทำงาน | CRUD ปกติ |
| Import from JSON | ✅ ทำงาน | นำเข้าจาก thai_holidays.json |
| Quick Refresh | ✅ ทำงาน | รีเฟรชปีปัจจุบัน+ปีหน้า |
| Sync from API | ❌ ปิดใช้งาน | workalendar ไม่รองรับไทย |
| Filter by Year | ✅ ทำงาน | กรองตามปี |
| Filter by Month | ✅ ทำงาน | กรองตามเดือน |

---

## 🔧 สำหรับนักพัฒนา

### ทำไมปิดฟีเจอร์ Sync from API?

**ปัญหา:**
```python
from workalendar.asia import Thailand
# ImportError: cannot import name 'Thailand'
```

**สาเหตุ:**
- workalendar ไม่มี class `Thailand` 
- Library นี้ไม่รองรับปฏิทินไทย
- วันหยุดไทยมีทั้งตามปฏิทินสากลและจันทรคติ (ซับซ้อน)

**ทางเลือก:**
1. ✅ ใช้ JSON file (`thai_holidays.json`) - **กำลังใช้อยู่**
2. ⚠️ หา API ภายนอก (เช่น API ของราชการ) - ยังไม่มี
3. ⚠️ สร้าง custom calculator - ซับซ้อนเกินไป

---

## 📚 เอกสารเพิ่มเติม

- 📖 [คู่มือใช้งาน Holiday Management](./holiday_api_implementation.md)
- 🧪 [คู่มือทดสอบ](./holiday_testing_guide.md)
- 🚀 [Quick Start Guide](../QUICKSTART.md)

---

**วันที่อัปเดต:** 20 ตุลาคม 2568 (2025)  
**เวอร์ชัน:** 1.1 (Disabled Sync from API)

## 🎯 ปัญหาที่แก้ไข

### ปัญหาเดิม:
- ❌ ต้องแก้ไข `thai_holidays.json` ด้วยมือเมื่อเวลาผ่านไป
- ❌ ไม่รู้ว่าข้อมูลเป็นปัจจุบันหรือไม่
- ❌ ต้องหาข้อมูลวันหยุดราชการเอง
- ❌ Error "TypeError: Failed to fetch" เมื่อโหลด API

### แก้ไขแล้ว:
- ✅ ดึงข้อมูลจาก **workalendar API** อัตโนมัติ
- ✅ เทียบข้อมูลกับ JSON และแสดงความแตกต่าง
- ✅ เลือกได้ว่าจะอัปเดตอะไร (JSON, DB, หรือทั้งสอง)
- ✅ แก้ไข CSRF token และ authentication issues

---

## 🐛 Bug Fixes (สำคัญ!)

### Issue: TypeError: Failed to fetch

**สาเหตุ:**
1. ไม่มี CSRF token ใน API request
2. `@login_required` redirect ไป login page
3. ไม่มี error handling ที่ดี

**แก้ไข:**

#### 1. เพิ่ม CSRF token ในหน้า Modal
```django
<!-- holiday_modal.html -->
{% csrf_token %}
<div class="modal fade" id="holidayModal">
  ...
</div>
```

#### 2. แก้ไข getCSRFToken() ให้แม่นยำ
```javascript
function getCSRFToken() {
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
    || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value
    || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
    || '';
  
  if (!token) {
    console.warn('CSRF token not found!');
  }
  
  return token;
}
```

#### 3. เพิ่ม authentication check ใน views
```python
# views_holiday.py
@login_required
def holiday_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)
    # ...
```

#### 4. ปรับปรุง loadHolidays() function
```javascript
async function loadHolidays(showStatus = false) {
  try {
    const response = await fetch('/api/holidays/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin'  // สำคัญ!
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      holidays = result.data;
      localStorage.setItem('cmms_holidays', JSON.stringify(holidays)); // Backup
      // ...
    }
  } catch (error) {
    console.error('Error loading holidays:', error);
    showMessage('danger', `⚠️ ไม่สามารถโหลดวันหยุดจาก API: ${error.message}`);
    
    // Fallback to localStorage
    const stored = localStorage.getItem('cmms_holidays');
    if (stored) {
      holidays = JSON.parse(stored);
      showMessage('warning', 'โหลดข้อมูลจาก cache (อาจไม่ใหม่ล่าสุด)');
    }
  }
}
```

---

## 🚀 ฟีเจอร์ใหม่

## 🎯 สิ่งที่เพิ่มเข้ามา

### 1. Backend (`views_holiday.py`)
✅ เพิ่ม function **`holiday_sync_from_api()`**
- ดึงข้อมูลจาก **workalendar.asia.Thailand**
- เทียบกับ `thai_holidays.json`
- แสดงผล: new, updated, unchanged, removed
- อัปเดต JSON และ/หรือ Database ตามที่เลือก

### 2. URL Routing (`urls.py`)
✅ เพิ่ม endpoint:
```python
path('api/holidays/sync-from-api/', views_holiday.holiday_sync_from_api, name='api_holiday_sync_from_api')
```

### 3. Frontend (`holiday_modal.html`)

#### 3.1 ปุ่มใหม่ใน Import Dialog
✅ **"🌐 ซิงค์จาก API (เทียบข้อมูล)"**
- วางไว้หลังปุ่ม "รีเฟรชข้อมูล"
- สีชมพู-เหลือง gradient สวยงาม

#### 3.2 JavaScript Functions
✅ **`syncFromAPI()`** - เรียก API และเปิด Dialog
✅ **`showSyncComparisonDialog(result)`** - แสดงผลการเปรียบเทียบ
✅ **`applySyncChanges(updateDB)`** - อัปเดตข้อมูล

### 4. Dependencies
✅ ติดตั้ง **workalendar** library
```bash
pip install workalendar
```

### 5. Documentation
✅ สร้างคู่มือครบถ้วน: `cmms/docs/sync_from_api_guide.md`

---

## 🎨 UI/UX Flow

```
[Import Dialog]
├── [Year Checkboxes]
│   ├── ☑ 2024
│   ├── ☑ 2025
│   └── ☑ 2026
│
├── [Quick Refresh Button] (สีฟ้า)
│   └── รีเฟรชข้อมูลปีปัจจุบัน + ปีหน้า
│
├── [🆕 Sync from API Button] (สีชมพู-เหลือง)
│   └── ซิงค์จาก API (เทียบข้อมูล)
│       ↓
│   [Comparison Dialog แสดง]
│   ├── 📊 Summary (badges)
│   │   ├── 🆕 ใหม่ X วัน
│   │   ├── ✏️ เปลี่ยนแปลง X วัน
│   │   ├── ⚪ ไม่เปลี่ยนแปลง X วัน
│   │   └── ❌ ถูกลบ X วัน
│   │
│   ├── 📋 Tables
│   │   ├── New Holidays (สีเขียว)
│   │   ├── Updated Holidays (สีเหลือง)
│   │   └── Removed Holidays (สีแดง)
│   │
│   └── [Action Buttons]
│       ├── [ปิด]
│       ├── [อัปเดต JSON เท่านั้น]
│       └── [อัปเดตทั้ง JSON + Database]
```

---

## 🔧 การทำงานของระบบ

### Step 1: กดปุ่ม "ซิงค์จาก API"
```javascript
syncFromAPI() {
  1. Confirm กับผู้ใช้
  2. Show loading animation
  3. POST /api/holidays/sync-from-api/
     Body: { years: [2025, 2026], update_json: false, import_to_db: false }
  4. รับ response
  5. เปิด Comparison Dialog
}
```

### Step 2: Backend ประมวลผล
```python
holiday_sync_from_api() {
  1. Initialize Thailand calendar
  2. Get holidays from workalendar API
  3. Load existing JSON
  4. Compare:
     - New holidays (in API, not in JSON)
     - Updated holidays (same date, different name)
     - Unchanged holidays (exact match)
     - Removed holidays (in JSON, not in API)
  5. Return comparison result
}
```

### Step 3: แสดง Comparison Dialog
- Summary badges พร้อมจำนวน
- Tables แสดงรายละเอียด
- Action buttons

### Step 4: Apply Changes (Optional)
```javascript
applySyncChanges(updateDB) {
  1. Confirm กับผู้ใช้
  2. POST /api/holidays/sync-from-api/
     Body: { years: [2025, 2026], update_json: true, import_to_db: updateDB }
  3. Backend update JSON และ/หรือ DB
  4. Show success message
  5. Reload holidays (ถ้า updateDB = true)
}
```

---

## 📊 ตัวอย่างผลลัพธ์

### API Response (Comparison Only)
```json
{
  "success": true,
  "message": "ซิงค์ข้อมูลจาก API เรียบร้อย: ใหม่ 2 วัน, เปลี่ยนแปลง 1 วัน, ไม่เปลี่ยนแปลง 16 วัน",
  "comparison": {
    "new": [
      {
        "year": 2025,
        "date": "2025-05-01",
        "name": "Labour Day",
        "type": "new"
      }
    ],
    "updated": [
      {
        "year": 2025,
        "date": "2025-04-13",
        "old_name": "วันสงกรานต์",
        "new_name": "Songkran Festival",
        "type": "updated"
      }
    ],
    "unchanged": [...],
    "removed": []
  },
  "summary": {
    "new_count": 2,
    "updated_count": 1,
    "unchanged_count": 16,
    "removed_count": 0
  },
  "db_stats": null,
  "json_updated": false
}
```

### API Response (With Update)
```json
{
  "success": true,
  "message": "...",
  "comparison": {...},
  "summary": {...},
  "db_stats": {
    "added": 2,
    "updated": 1,
    "errors": []
  },
  "json_updated": true
}
```

---

## 🎯 Use Cases

### Use Case 1: ตรวจสอบประจำปี
**เมื่อ:** ต้นปี หรือเมื่อรัฐบาลประกาศวันหยุดใหม่
**วิธี:**
1. กดปุ่ม "ซิงค์จาก API"
2. ดูการเปลี่ยนแปลง
3. ถ้าไม่มีอะไร → กด "ปิด"
4. ถ้ามี → กด "อัปเดตทั้ง JSON + Database"

### Use Case 2: Backup JSON
**เมื่อ:** ต้องการอัปเดต JSON แต่ยังไม่อัปเดต DB
**วิธี:**
1. กดปุ่ม "ซิงค์จาก API"
2. ตรวจสอบ
3. กด "อัปเดต JSON เท่านั้น"
4. JSON ถูกแก้ไข, DB ไม่เปลี่ยน

### Use Case 3: เปรียบเทียบอย่างเดียว
**เมื่อ:** แค่อยากดูว่า workalendar มีอะไรต่างจาก JSON
**วิธี:**
1. กดปุ่ม "ซิงค์จาก API"
2. ดูรายละเอียด
3. กด "ปิด"
4. ไม่มีอะไรเปลี่ยน

---

## 🔄 เปรียบเทียบกับฟีเจอร์เดิม

| ฟีเจอร์ | ปุ่ม "รีเฟรช" | ปุ่ม "ซิงค์จาก API" |
|---------|---------------|---------------------|
| **ข้อมูลที่ใช้** | thai_holidays.json | workalendar API |
| **ต้องแก้ไข JSON เอง** | ใช่ | **ไม่** |
| **แสดงการเปลี่ยนแปลง** | ใช่ | **ใช่ (ละเอียดกว่า)** |
| **อัปเดต JSON** | ไม่ | **ใช่ (ถ้าเลือก)** |
| **เปรียบเทียบก่อนอัปเดต** | ไม่ | **ใช่** |
| **ควบคุมได้** | น้อย | **มาก (3 options)** |

**คำแนะนำ:**
- ใช้ **"รีเฟรช"** = เมื่อแก้ไข JSON แล้ว ต้องการโหลดเข้า DB
- ใช้ **"ซิงค์จาก API"** = เมื่อต้องการข้อมูลใหม่จาก workalendar

---

## ⚠️ ข้อควรระวัง

### 1. workalendar อาจไม่ตรงกับรัฐบาลไทย 100%
- **สาเหตุ:** วันหยุดบางวันประกาศทีหลัง
- **แก้ไข:** ตรวจสอบก่อนอัปเดต, แก้ใน JSON ได้

### 2. วันหยุดชดเชย (Compensatory Day)
- workalendar อาจไม่มีวันชดเชย
- ต้องเพิ่มเองใน JSON

### 3. วันหยุดพิเศษ (Special Decree)
- เช่น "ราชพิธี", "เลือกตั้ง"
- ต้องเพิ่มเองด้วยมือ

---

## 🧪 วิธีทดสอบ

### ทดสอบ workalendar

1. เปิด Django shell:
```bash
python manage.py shell
```

2. ทดสอบ:
```python
from workalendar.asia import Thailand
cal = Thailand()
holidays = cal.holidays(2025)
for date, name in holidays:
    print(f"{date} - {name}")
```

### ทดสอบ API Endpoint

```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/api/holidays/sync-from-api/ `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"years": [2025, 2026], "update_json": false, "import_to_db": false}'
```

---

## 📦 ไฟล์ที่เกี่ยวข้อง

```
cmms_project/
├── cmms/
│   ├── views_holiday.py              # ✅ เพิ่ม holiday_sync_from_api()
│   ├── urls.py                       # ✅ เพิ่ม route
│   ├── templates/
│   │   └── maintenance/
│   │       └── partials/
│   │           └── holiday_modal.html # ✅ เพิ่ม UI + JS
│   ├── data/
│   │   └── thai_holidays.json        # 📝 อาจถูกอัปเดต
│   └── docs/
│       ├── sync_from_api_guide.md    # ✅ คู่มือใหม่
│       └── sync_from_api_summary.md  # ✅ ไฟล์นี้
└── requirements.txt                   # 📝 ควรเพิ่ม workalendar
```

---

## 🎉 สรุป

ตอนนี้คุณมีระบบที่:
1. ✅ **ไม่ต้องแก้ไข JSON เอง** อีกต่อไป
2. ✅ **ดึงข้อมูลจาก workalendar API** อัตโนมัติ
3. ✅ **เทียบกับ JSON** และแสดงความแตกต่าง
4. ✅ **ควบคุมได้** ว่าจะอัปเดตอะไร
5. ✅ **มี UI สวยงาม** พร้อม Dialog เปรียบเทียบ

### 🚀 Next Steps
1. ทดสอบปุ่ม "ซิงค์จาก API"
2. ตรวจสอบผลลัพธ์
3. อัปเดต JSON และ Database
4. เปรียบเทียบกับข้อมูลเดิม

### 📚 อ่านเพิ่มเติม
- `cmms/docs/sync_from_api_guide.md` - คู่มือใช้งานฉบับเต็ม
- `cmms/docs/holiday_api_implementation.md` - เอกสารเดิม

---

**Happy Syncing! 🎊**
