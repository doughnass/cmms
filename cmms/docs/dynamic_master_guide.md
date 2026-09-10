# คู่มือการใช้งาน Master Data แบบยืดหยุ่น (Dynamic Schema)

## สรุปสั้น ๆ
ระบบ Master Data ใหม่ช่วยให้คุณสามารถกำหนดฟิลด์เพิ่มเติมสำหรับแต่ละหมวด (category) ได้โดยไม่ต้องแก้โค้ดหรือทำ database migration ทุกครั้ง

**ตัวอย่างการใช้งาน:**
- หมวด "locations" อาจต้องการฟิลด์เพิ่มเติม: ชั้น (floor), ความจุ (capacity), มีแอร์หรือไม่ (has_ac)
- หมวด "manufacturers" อาจต้องการ: ประเทศ (country), เว็บไซต์ (website), คะแนนคุณภาพ (quality_rating)
- หมวด "departments" อาจต้องการ: ผู้จัดการ (manager), งบประมาณ (budget), ตึก (building)

---

## ขั้นตอนการตั้งค่า

### 1. รัน Migrations (ครั้งแรกเท่านั้น)
ก่อนใช้งานครั้งแรก ต้องรัน migration เพื่อสร้างตารางใหม่:

**Windows Command Prompt (cmd):**
```cmd
cd /d d:\Python\CMMS\cmms_project
python manage.py migrate
```

**Windows PowerShell:**
```powershell
cd d:\Python\CMMS\cmms_project
python manage.py migrate
```

---

## การสร้าง Category และกำหนด Fields

### 2. เข้าสู่ Django Admin
1. เปิดเว็บเบราว์เซอร์ไปที่ `http://127.0.0.1:8000/admin/`
2. Login ด้วย staff/admin account
3. ไปที่ **CMMS > Master categories**

### 3. สร้าง Category ใหม่
คลิก **Add Master Category** แล้วกรอก:
- **Category Key**: ชื่อ machine-safe (lowercase, underscores, no spaces) เช่น `locations`, `manufacturers`
- **ชื่อหมวดหมู่ (Label)**: ชื่อที่แสดงใน UI เช่น "สถานที่", "ผู้ผลิต"
- **คำอธิบาย**: อธิบายสั้น ๆ ว่าหมวดนี้ใช้เก็บข้อมูลอะไร

### 4. เพิ่ม Field Definitions
ในหน้าเดียวกัน มีส่วน **Master field definitions** (inline form) ให้เพิ่มฟิลด์ที่ต้องการ:

**ตัวอย่างฟิลด์สำหรับ "locations":**

| Field Name (key) | Label (แสดงใน UI) | Field Type | Required | Choices | Help Text |
|------------------|-------------------|------------|----------|---------|-----------|
| `floor`          | ชั้น              | Integer    | ✓ Yes    | -       | ระบุเลขชั้น เช่น 3 |
| `capacity`       | ความจุ            | Integer    | No       | -       | จำนวนคนที่รองรับได้ |
| `has_ac`         | มีแอร์หรือไม่     | Boolean    | No       | -       | เลือกถ้ามีเครื่องปรับอากาศ |
| `room_type`      | ประเภทห้อง        | Select     | No       | ["ห้องประชุม","ห้องทำงาน","ห้องพักผู้ป่วย"] | ประเภทของห้อง |

**Field Types ที่รองรับ:**
- **String**: ข้อความสั้น ๆ (1 บรรทัด)
- **Text**: ข้อความยาว (หลายบรรทัด)
- **Integer**: ตัวเลขจำนวนเต็ม
- **Decimal**: ทศนิยม (เช่น ราคา, คะแนน)
- **Boolean**: เลือกใช่/ไม่ใช่ (checkbox)
- **Date**: วันที่ (YYYY-MM-DD)
- **Select**: ตัวเลือกแบบ dropdown

**Choices (สำหรับ Select type):**
- รูปแบบ JSON array เช่น `["A","B","C"]` หรือ
- รูปแบบ dict เช่น `[{"value":"a","label":"A"},{"value":"b","label":"B"}]`

**Order:**
- เลขลำดับสำหรับเรียงฟิลด์ (เริ่มจาก 0, 1, 2, ...)

---

## การสร้าง/แก้ไข Master Items

### 5. เพิ่ม Item ในหมวดที่มี Schema
1. ไปที่หน้า Master List หรือเลือก **Add Master Item**
2. เลือก **Category** ที่คุณสร้าง schema ไว้ (เช่น `locations`)
3. กรอกฟิลด์พื้นฐาน: Label, Code, Description, Active, Order
4. ด้านล่างจะมีส่วน **"ฟิลด์เพิ่มเติมสำหรับหมวดนี้"** แสดงฟิลด์ที่คุณกำหนดไว้
5. กรอกค่าฟิลด์เพิ่มเติม (ฟิลด์ที่มี * คือจำเป็นต้องกรอก)
6. คลิก **บันทึก**

**ตัวอย่าง:**
- Label: `ห้องประชุม 301`
- Code: `room301`
- ชั้น (floor): `3`
- ความจุ (capacity): `30`
- มีแอร์หรือไม่: ✓ (checked)

### 6. แก้ไข Item ที่มีอยู่
1. ไปที่รายการ Master และคลิก **Edit** ที่ item ที่ต้องการแก้
2. ฟิลด์เพิ่มเติม (meta) จะแสดงพร้อมค่าเดิม
3. แก้ไขและ **บันทึก**

---

## Validation & Error Messages

**ระบบจะตรวจสอบ:**
- **Required fields**: ถ้าฟิลด์บังคับว่าง จะแจ้ง error
- **Type checking**: ถ้ากรอกข้อความในฟิลด์ Integer จะแจ้ง error "ค่าไม่ถูกต้อง"
- **Choices**: ถ้าเลือกค่านอก choices ที่กำหนด จะแจ้ง error

**ตัวอย่าง Error:**
- "ชั้น เป็นฟิลด์ที่จำเป็น" → ต้องกรอก floor
- "ค่าไม่ถูกต้อง: invalid literal for int()" → กรอกตัวอักษรในฟิลด์ Integer

---

## Best Practices (แนะนำ)

### การตั้งชื่อ Field Name (machine key)
- ใช้ lowercase และ underscores เท่านั้น เช่น `floor_number`, `has_ac`, `room_type`
- ห้ามใช้เว้นวรรค หรืออักขระพิเศษ
- ห้ามใช้ชื่อที่ซ้ำกับฟิลด์พื้นฐาน เช่น `label`, `code`, `parent`, `category`

### การเลือก Field Type
- ถ้าข้อมูลเป็นตัวเลขที่ต้อง filter/เรียงลำดับ → Integer/Decimal
- ถ้าเป็น yes/no → Boolean
- ถ้าเป็นตัวเลือกจำกัด (< 20 options) → Select
- ถ้าเป็นข้อความสั้น → String
- ถ้าเป็นข้อความยาว → Text

### Help Text
- ควรเขียน help text สั้น ๆ เพื่ออธิบายว่าฟิลด์นี้ใช้เก็บอะไร หรือตัวอย่างค่า
- ตัวอย่าง: "ระบุเลขชั้น เช่น 3", "จำนวนคนที่รองรับได้"

### Visible in Preview
- เลือก ✓ สำหรับฟิลด์ที่ต้องการให้แสดงใน option label (future feature)
- ตัวอย่าง: floor → ช่วยให้เห็น "ห้อง 301 (ชั้น 3)" ใน dropdown

---

## การ Query และ Filter ข้อมูล Meta (สำหรับ Developer)

**Basic query:**
```python
from cmms.models import MasterItem

# Get all locations on floor 3
items = MasterItem.objects.filter(category='locations', meta__floor=3)

# Get locations with capacity > 20 (requires JSONB on Postgres)
items = MasterItem.objects.filter(category='locations', meta__capacity__gt=20)
```

**Indexing (Postgres only):**
- สำหรับฟิลด์ที่ต้อง query บ่อย ๆ ควรสร้าง index:
```sql
CREATE INDEX idx_meta_floor ON cmms_masteritem USING GIN ((meta));
-- or expression index for specific key:
CREATE INDEX idx_meta_floor_value ON cmms_masteritem ((meta->>'floor'));
```

**SQLite / heavy filtering:**
- พิจารณา denormalize ค่าที่ต้อง query บ่อยลงคอลัมน์จริง
- หรือสร้างตาราง side-table `MasterItemAttribute(item, key, value)` ที่ index ได้

---

## Troubleshooting

**Q: ฟิลด์เพิ่มเติมไม่ปรากฏในฟอร์ม**
A: ตรวจสอบว่า:
1. Category key ตรงกับที่กำหนดใน MasterCategory
2. Field definitions มี order ที่ถูกต้อง (0, 1, 2, ...)
3. เรียก page ใหม่ (hard refresh: Ctrl+F5)

**Q: Error "Template filter cmms_filters not found"**
A: ตรวจสอบว่า:
1. ไฟล์ `cmms/templatetags/__init__.py` และ `cmms_filters.py` มีอยู่
2. Restart Django dev server
3. Template ต้องมี `{% load cmms_filters %}` ด้านบน

**Q: ค่า meta ไม่ถูกบันทึก**
A: ตรวจสอบว่า:
1. POST data มี `meta.<field_name>` ที่ถูกต้อง
2. ไม่มี validation error (check console/logs)
3. ฟิลด์ required ทั้งหมดถูกกรอก

**Q: ต้องการเปลี่ยนชื่อ field ภายหลัง**
A: ถ้าเปลี่ยน `name` ของ FieldDefinition หลังจากมีข้อมูลแล้ว ค่าเดิมใน `meta` จะไม่ถูก migrate อัตโนมัติ — ต้องเขียน script เพื่อ rename key ใน JSON ของทุก item ในหมวดนั้น

---

## ตัวอย่าง Use Cases

### Use Case 1: เพิ่มฟิลด์ "ประเทศ" ให้หมวด manufacturers
1. Admin → Master categories → manufacturers → Add field
2. Name: `country`, Label: `ประเทศ`, Type: Select, Choices: `["Thailand","USA","Japan","Germany"]`
3. บันทึก
4. ไปสร้าง/แก้ไข manufacturer → จะมีฟิลด์ "ประเทศ" ให้เลือก

### Use Case 2: บันทึกงบประมาณและผู้จัดการในหมวด departments
1. สร้าง 2 fields:
   - `manager`: String, Label: `ผู้จัดการ`
   - `budget`: Decimal, Label: `งบประมาณ (บาท)`
2. เมื่อสร้าง department item ใหม่ กรอก manager และ budget
3. ค่าจะถูกเก็บใน `meta` ของ item

### Use Case 3: ตรวจสอบว่าห้องมีแอร์หรือไม่
1. สร้าง field `has_ac`: Boolean
2. เมื่อสร้าง location item ให้ check/uncheck
3. ค้นหาห้องที่มีแอร์:
```python
ac_rooms = MasterItem.objects.filter(category='locations', meta__has_ac=True)
```

---

## การ Migrate ข้อมูลเดิม (ถ้ามี)

ถ้าคุณมีข้อมูล master เก่าที่เก็บฟิลด์พิเศษใน `description` หรือฟิลด์อื่น สามารถเขียน management command เพื่อ migrate:

```python
# cmms/management/commands/migrate_old_master_to_meta.py
from django.core.management.base import BaseCommand
from cmms.models import MasterItem
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        # ตัวอย่าง: migrate floor จาก description
        items = MasterItem.objects.filter(category='locations')
        for item in items:
            # parse description: "ชั้น 3"
            if 'ชั้น' in item.description:
                floor = int(item.description.split('ชั้น')[1].strip())
                item.meta = item.meta or {}
                item.meta['floor'] = floor
                item.save()
        self.stdout.write(self.style.SUCCESS('Migration done'))
```

---

## สรุป
ระบบนี้ช่วยให้คุณขยายฟิลด์ Master Data ได้ง่าย ๆ โดยไม่ต้องแก้โค้ดหรือ migrate database ทุกครั้ง — แค่กำหนด schema ใน Admin UI แล้วใช้งานได้ทันที!

**ขั้นตอนสั้น ๆ:**
1. สร้าง MasterCategory + FieldDefinitions ใน Admin
2. สร้าง/แก้ไข MasterItem → ฟิลด์เพิ่มเติมจะปรากฏอัตโนมัติ
3. ข้อมูลถูกเก็บใน `meta` (JSON) และ validate ตาม schema

---

**ติดปัญหาหรือต้องการเพิ่มฟีเจอร์?**
- ดูเอกสาร Django admin: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- ดูเอกสาร JSONField: https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield
- ติดต่อทีมพัฒนา
