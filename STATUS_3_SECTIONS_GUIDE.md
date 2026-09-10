# คู่มือระบบแสดงสถานะแบบ 3 ส่วน (3 Sections Status Display)

## 📋 สรุปการทำงาน

ระบบแสดงสถานะเครื่องมือแพทย์ได้รับการออกแบบใหม่ให้แบ่งเป็น **3 กลุ่มหลัก** ตามที่คุณร้องขอ:

### 🎨 โครงสร้างการแสดงผล

```
┌─────────────────────────────────────┐
│ ส่วนที่ 1: สถานะการใช้งาน          │
│ (Operational Status)                │
│ • พร้อมใช้งาน (สีเขียว)            │
│ • ไม่พร้อมใช้งาน (สีแดง)           │
│ • อยู่ระหว่างซ่อม (สีเหลือง)       │
├─────────────────────────────────────┤
│ ส่วนที่ 2: สถานะการบำรุงรักษา      │
│ (Maintenance Status)                │
│ 🔧 PM (Preventive Maintenance):    │
│   • PM ปกติ (สีเขียว)              │
│   • PM ใกล้ครบกำหนด (สีเหลือง)    │
│   • PM เกินกำหนด (สีแดง)           │
│ 📐 CAL (Calibration):              │
│   • CAL ปกติ (สีเขียว)             │
│   • CAL ใกล้ครบกำหนด (สีเหลือง)   │
│   • CAL เกินกำหนด (สีแดง)          │
├─────────────────────────────────────┤
│ ส่วนที่ 3: สถานะการรับประกัน       │
│ (Warranty Status)                   │
│ 🛡️ Warranty:                       │
│   • อยู่ในประกัน (สีม่วง)          │
│   • ใกล้หมดประกัน (สีฟ้า)          │
│   • หมดประกัน (สีเทา)              │
└─────────────────────────────────────┘
```

---

## 🗂️ Master Data Structure

### กลุ่มที่ 1: Operational Status (สถานะการใช้งาน)

| Code | Label | สี | ไอคอน | Priority |
|------|-------|-----|-------|----------|
| `ready` | พร้อมใช้งาน | success (เขียว) | check-circle-fill | 0 |
| `not_ready` | ไม่พร้อมใช้งาน | danger (แดง) | x-circle-fill | 100 |
| `under_repair` | อยู่ระหว่างซ่อม | warning (เหลือง) | tools | 50 |

### กลุ่มที่ 2: Maintenance Status (สถานะการบำรุงรักษา)

**PM (Preventive Maintenance):**

| Code | Label | สี | ไอคอน | Priority | เงื่อนไข |
|------|-------|-----|-------|----------|----------|
| `pm_ok` | PM ปกติ | success (เขียว) | check-circle-fill | 0 | > 7 วัน |
| `pm_due_soon` | PM ใกล้ครบกำหนด | warning (เหลือง) | clock-fill | 5 | ≤ 7 วัน |
| `pm_overdue` | PM เกินกำหนด | danger (แดง) | exclamation-triangle-fill | 10 | เกินแล้ว |

**CAL (Calibration):**

| Code | Label | สี | ไอคอน | Priority | เงื่อนไข |
|------|-------|-----|-------|----------|----------|
| `cal_ok` | CAL ปกติ | success (เขียว) | check-circle-fill | 0 | > 14 วัน |
| `cal_due_soon` | CAL ใกล้ครบกำหนด | warning (เหลือง) | clock-fill | 5 | ≤ 14 วัน |
| `cal_overdue` | CAL เกินกำหนด | danger (แดง) | exclamation-triangle-fill | 10 | เกินแล้ว |

### กลุ่มที่ 3: Warranty Status (สถานะการรับประกัน)

| Code | Label | สี | ไอคอน | Priority | เงื่อนไข |
|------|-------|-----|-------|----------|----------|
| `warranty_ok` | อยู่ในประกัน | success (เขียว) | shield-check | 0 | > 30 วัน |
| `warranty_expiring` | ใกล้หมดประกัน | info (ฟ้า) | shield-exclamation | 2 | ≤ 30 วัน |
| `warranty_expired` | หมดประกัน | secondary (เทา) | shield-x | 1 | หมดแล้ว |

---

## 🔧 Technical Implementation

### 1. Database Structure

```python
# MasterItem model
{
    'category': 'equipment_status',
    'code': 'ready',  # unique identifier
    'label': 'พร้อมใช้งาน',  # display text
    'order': 10,  # sorting order
    'active': True,
    'meta': {
        'group': 'operational',  # operational / maintenance / warranty
        'color': 'success',  # Bootstrap color class
        'icon': 'check-circle-fill',  # Bootstrap Icons
        'priority': 0,  # higher = more urgent
        'description': 'เครื่องมือพร้อมใช้งานปกติ'
    }
}
```

### 2. JavaScript Functions

**calculateEquipmentStatus(row)**
- คำนวณสถานะของเครื่องมือแต่ละตัวจากข้อมูลวันที่
- คืนค่า object ที่แบ่งตามกลุ่ม:
  ```javascript
  {
      operational: {...},      // 1 status
      maintenance: [...],      // array of statuses
      warranty: {...}          // 1 status
  }
  ```

**renderStatusSection(status)**
- สร้าง HTML สำหรับแสดงสถานะ 1 รายการ
- รวมไอคอน, label, และจำนวนวัน (ถ้ามี)

**renderStatusDisplay(statusByGroup)**
- รวม 3 sections เข้าด้วยกัน
- แสดงผลเป็น vertical stack

### 3. CSS Styling

**Layout:**
```css
.status-display-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.status-section {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.5rem;
    border-radius: 0.5rem;
    border-left: 3px solid;
}
```

**Color Classes:**
- `.operational.ready` - เขียว gradient
- `.operational.not-ready` - แดง gradient
- `.operational.under-repair` - เหลือง gradient
- `.maintenance.ok` - น้ำเงิน gradient
- `.maintenance.warning` - เหลือง gradient
- `.maintenance.danger` - แดง gradient
- `.warranty.ok` - ม่วง gradient
- `.warranty.expiring` - ฟ้า gradient
- `.warranty.expired` - เทา gradient

---

## 📝 การใช้งาน

### อัปเดต Master Data

รันสคริปต์เพื่ออัปเดตข้อมูล:

```bash
python update_status_groups.py
```

ผลลัพธ์:
```
✅ Created: 6 items
🔄 Updated: 6 items
📁 Total: 12 status items across 3 groups
```

### ตรวจสอบข้อมูล

```python
from cmms.models import MasterItem

# ดูสถานะทั้งหมด
statuses = MasterItem.objects.filter(
    category='equipment_status',
    active=True
).order_by('meta__group', 'order')

for s in statuses:
    print(f"[{s.code}] {s.label} - Group: {s.meta['group']}")
```

### แก้ไขสี/ไอคอน

```python
from cmms.models import MasterItem

# เปลี่ยนสีของ "พร้อมใช้งาน"
status = MasterItem.objects.get(code='ready')
status.meta['color'] = 'primary'  # เปลี่ยนเป็นสีน้ำเงิน
status.meta['icon'] = 'check2-circle'  # เปลี่ยนไอคอน
status.save()

# รีเฟรชหน้าเว็บจะเห็นการเปลี่ยนแปลงทันที
```

---

## 🎯 ตัวอย่างการแสดงผล

### เครื่องมือปกติ (ไม่มีปัญหา)

```
┌─────────────────────────────────────┐
│ ✓ พร้อมใช้งาน                      │ <- เขียว
│ ✓ PM ปกติ                          │ <- น้ำเงิน
│ ✓ CAL ปกติ                         │ <- น้ำเงิน
│ 🛡️ อยู่ในประกัน                    │ <- ม่วง
└─────────────────────────────────────┘
```

### เครื่องมือมีปัญหา

```
┌─────────────────────────────────────┐
│ ✗ ไม่พร้อมใช้งาน                   │ <- แดง
│ ⚠ PM เกินกำหนด (15 วัน)           │ <- แดง
│ ⚠ CAL ใกล้ครบกำหนด (3 วัน)        │ <- เหลือง
│ ⚠ ใกล้หมดประกัน                   │ <- ฟ้า
└─────────────────────────────────────┘
```

---

## 🔄 Logic Flow

```
User เปิดหน้า equipment_list
    ↓
Django view query master_statuses
    ↓
Template render with masterStatuses array
    ↓
JavaScript: DOMContentLoaded
    ↓
Loop through equipment rows
    ↓
For each row:
    1. calculateEquipmentStatus(row)
       ├→ Check operational (default: ready)
       ├→ Check PM dates
       ├→ Check CAL dates
       └→ Check warranty dates
    ↓
    2. renderStatusDisplay(statusByGroup)
       ├→ Render operational section
       ├→ Render maintenance sections (PM + CAL)
       └→ Render warranty section
    ↓
    3. Insert HTML into status-cell
    ↓
Display complete with colors and icons
```

---

## ✨ ข้อดี

1. **แยกกลุ่มชัดเจน**: แต่ละ section มีความหมายเฉพาะ
2. **ใช้สีตามหลัก UX**: เขียว=ปกติ, เหลือง=เตือน, แดง=เร่งด่วน
3. **Sync กับ master data**: แก้ไข master → UI เปลี่ยนทันที
4. **ไอคอนสื่อความหมาย**: ใช้ Bootstrap Icons ที่เหมาะสม
5. **แสดงจำนวนวัน**: ให้รู้ว่าเหลือเวลาหรือเกินมานานแค่ไหน
6. **Responsive**: แสดงผลดีในทุกขนาดหน้าจอ
7. **Print-friendly**: ปรับ layout เมื่อพิมพ์

---

## 🚀 การทดสอบ

1. **เปิดหน้า equipment_list**:
   ```
   http://localhost:8000/equipment_list/
   ```

2. **ตรวจสอบ**:
   - [ ] แต่ละแถวแสดง 3 sections แยกกัน
   - [ ] สีตรงตาม master data
   - [ ] ไอคอนแสดงถูกต้อง
   - [ ] จำนวนวันคำนวณถูกต้อง
   - [ ] PM/CAL แสดงแยกกันชัดเจน
   - [ ] Warranty section อยู่ท้ายสุด

3. **ทดสอบ edge cases**:
   - เครื่องไม่ต้อง PM → ไม่แสดง PM section
   - เครื่องไม่ต้อง CAL → ไม่แสดง CAL section
   - ไม่มีข้อมูล warranty → ไม่แสดง warranty section

---

## 📚 Files Modified

1. `update_status_groups.py` - สคริปต์สร้าง/อัปเดต master data
2. `equipment_list.html` - template หลัก
   - CSS: เพิ่ม status-display-container และ status-section
   - JavaScript: 
     - `calculateEquipmentStatus()` - คำนวณ 3 กลุ่ม
     - `renderStatusSection()` - render 1 section
     - `renderStatusDisplay()` - รวม 3 sections
3. `views.py` - ไม่ต้องแก้ (ใช้ query เดิม)

---

## 🎓 สรุป

ระบบสถานะใหม่นี้:
- ✅ แบ่งกลุ่มชัดเจนเป็น 3 ส่วนตามที่ร้องขอ
- ✅ ใช้สีตามหลัก UX (เขียว/เหลือง/แดง)
- ✅ แสดงไอคอนที่เหมาะสมกับแต่ละกลุ่ม
- ✅ Sync กับ master data อย่างสมบูรณ์
- ✅ พร้อมใช้งานจริง

**รีเฟรชหน้าเพื่อดูผลลัพธ์!** 🎉
