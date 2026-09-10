# Hours to Tasks Conversion System
## ระบบแปลงชั่วโมงเป็นจำนวนงาน

### ภาพรวมระบบ

ระบบแปลงชั่วโมงเป็นจำนวนงาน (Hours to Tasks Conversion) ช่วยให้ผู้ใช้สามารถ:
- **แปลงชั่วโมงการทำงานเป็นจำนวนงาน** โดยอัตโนมัติ
- **ตั้งค่าอัตราแปลง** ตามความต้องการองค์กร (เช่น 3 ชม./งาน)
- **แสดงผลทั้งสองค่าพร้อมกัน** ในทุกส่วนของระบบ
- **บันทึกการตั้งค่า** ใน localStorage เพื่อคงค่าหลังจากรีเฟรชหน้า

---

## 🎯 จุดประสงค์

1. **มาตรฐานการวัดงาน**: แปลงเวลาเป็นหน่วยงานที่เข้าใจง่าย
2. **ความยืดหยุ่น**: ปรับอัตราแปลงได้ตามลักษณะงาน
3. **ความโปร่งใส**: แสดงทั้งชั่วโมงและงานพร้อมกัน
4. **การวางแผน**: ช่วยคำนวณกำลังคนและภาระงาน

---

## 📐 อัตราแปลงมาตรฐาน

### รูปแบบทั่วไป
| อัตราแปลง | กรณีใช้งาน | ตัวอย่าง |
|-----------|-----------|----------|
| **2 ชม./งาน** | งานเบา, งานซ่อมทั่วไป | เปลี่ยนหลอดไฟ, ตรวจเช็คเบื้องต้น |
| **3 ชม./งาน** | งานปานกลาง (ค่าเริ่มต้น) | งานซ่อมบำรุงทั่วไป, PM routine |
| **4 ชม./งาน** | งานหนัก, งานซับซ้อน | Overhaul, งานประกอบใหม่ |

### สูตรการคำนวณ

```javascript
// แปลงชั่วโมง → งาน
จำนวนงาน = จำนวนชั่วโมง ÷ ชั่วโมงต่องาน

// แปลงงาน → ชั่วโมง
จำนวนชั่วโมง = จำนวนงาน × ชั่วโมงต่องาน
```

**ตัวอย่าง** (ใช้ 3 ชม./งาน):
- 6 ชม. = 2 งาน
- 9 ชม. = 3 งาน
- 4.5 ชม. = 1.5 งาน

---

## 🛠️ วิธีใช้งาน

### 1. เปิด Configuration Panel
1. คลิกปุ่ม **"แปลง ชม. → งาน"** มุมขวาล่างของหน้า
2. Panel จะเลื่อนขึ้นมาแสดงการตั้งค่า

### 2. เลือกอัตราแปลง

#### วิธีที่ 1: ใช้ Preset
คลิกปุ่ม preset ที่ต้องการ:
- `2 ชม. ต่อ 1 งาน` - งานเบา
- `3 ชม. ต่อ 1 งาน` - มาตรฐาน (แนะนำ)
- `4 ชม. ต่อ 1 งาน` - งานหนัก

#### วิธีที่ 2: กำหนดเอง
1. ใส่ตัวเลขใน input box
2. ช่วงที่รองรับ: **0.5 - 16 ชั่วโมง**
3. สามารถใช้ทศนิยม เช่น 2.5, 3.5

### 3. ดูตัวอย่างแปลง
- **ตัวอย่าง**: จะแสดงผลการแปลง 6 ชั่วโมง → จำนวนงานตามอัตราที่เลือก
- อัปเดตแบบ real-time เมื่อเปลี่ยนค่า

### 4. บันทึกการตั้งค่า
1. คลิกปุ่ม **"บันทึก"** สีน้ำเงิน
2. ระบบจะ:
   - บันทึกค่าลง localStorage
   - แสดงข้อความยืนยัน
   - รีเฟรช UI ทั้งหมดให้ใช้ค่าใหม่

### 5. รีเซ็ตการตั้งค่า
- คลิกปุ่ม **"รีเซ็ต"** เพื่อกลับไปค่าเริ่มต้น (3 ชม./งาน)

---

## 💻 API และฟังก์ชัน

### ฟังก์ชันหลัก

#### 1. `hoursToTasks(hours, hoursPerTaskOverride)`
แปลงชั่วโมงเป็นงาน

**Parameters:**
- `hours` (number): จำนวนชั่วโมง
- `hoursPerTaskOverride` (number, optional): อัตราแปลงแบบชั่วคราว

**Returns:** `number` - จำนวนงาน (ทศนิยม 1 ตำแหน่ง)

**ตัวอย่าง:**
```javascript
hoursToTasks(6)      // → 2.0 (ใช้ config: 3 ชม./งาน)
hoursToTasks(6, 2)   // → 3.0 (บังคับ: 2 ชม./งาน)
hoursToTasks(7.5)    // → 2.5
```

#### 2. `tasksToHours(tasks, hoursPerTaskOverride)`
แปลงงานเป็นชั่วโมง

**Parameters:**
- `tasks` (number): จำนวนงาน
- `hoursPerTaskOverride` (number, optional): อัตราแปลงแบบชั่วคราว

**Returns:** `number` - จำนวนชั่วโมง (ทศนิยม 1 ตำแหน่ง)

**ตัวอย่าง:**
```javascript
tasksToHours(2)      // → 6.0
tasksToHours(3, 4)   // → 12.0 (บังคับ: 4 ชม./งาน)
```

#### 3. `formatHoursAndTasks(hours, options)`
จัดรูปแบบการแสดงผล

**Parameters:**
- `hours` (number): จำนวนชั่วโมง
- `options` (object):
  - `showHours` (boolean): แสดงชั่วโมง (default: true)
  - `showTasks` (boolean): แสดงงาน (default: true)
  - `separator` (string): ตัวแบ่ง (default: ' • ')
  - `hoursPerTask` (number): อัตราแปลงชั่วคราว

**Returns:** `string` - ข้อความที่จัดรูปแบบแล้ว

**ตัวอย่าง:**
```javascript
formatHoursAndTasks(6)
// → "6 ชม. • 2 งาน"

formatHoursAndTasks(6, { separator: ' ≈ ' })
// → "6 ชม. ≈ 2 งาน"

formatHoursAndTasks(6, { showTasks: false })
// → "6 ชม."
```

#### 4. `createHoursTasksBadge(hours, options)`
สร้าง HTML badge แสดงชั่วโมงและงาน

**Parameters:**
- `hours` (number): จำนวนชั่วโมง
- `options` (object):
  - `compact` (boolean): รูปแบบกระชับ (default: false)
  - `showIcon` (boolean): แสดงไอคอน (default: true)
  - `hoursPerTask` (number): อัตราแปลงชั่วคราว

**Returns:** `string` - HTML string

**ตัวอย่าง:**
```javascript
createHoursTasksBadge(6, { compact: true })
// → <span class="hours-tasks-badge">
//     <i class="bi bi-clock"></i>
//     <span class="hours">6 ชม.</span>
//     <span class="separator">·</span>
//     <span class="tasks">2 งาน</span>
//   </span>
```

---

## 🎨 UI Components ที่ใช้ระบบแปลง

### 1. Calendar Day Cards
แสดง: **Capacity** และ **Equipment Hours**
```
ทั้งหมด: 8 งาน
ว่าง: 5 งาน
จอง: 3 งาน
Equipment: 12 ชม. ≈ 4 งาน
```

### 2. Detail Panel - Daily Summary
แสดง: **Work Hours** และ **OT Hours**
```
ทำงานปกติ: 5 คน
  → 15 ชม. ≈ 5 งาน

ล่วงเวลา: 2 คน
  → 8 ชม. ≈ 2.7 งาน
```

### 3. Equipment Schedule List
แสดง: **Estimated Hours** ของแต่ละงาน
```
1. เครื่องปรับอากาศ ชั้น 3
   🕐 3 ชม. • ⚙️ 1 งาน
```

### 4. Assignment Modal
แสดง: **Hours per equipment** ในรายการที่เลือก
```
☑ เครื่องพิมพ์เลเซอร์
   [Tag] Preventive Maintenance | 🕐 2 ชม. · 0.7 งาน
```

### 5. Work List Modal - Summary Stats
แสดง: **Regular/OT Hours + Tasks**
```
ช่างเทคนิคในเวลา: 8 คน
  มาปฏิบัติงาน • 24 ชม. (8 งาน)

ล่วงเวลา: 3 คน
  คน • 9 ชม. (3 งาน)
```

---

## 💾 การบันทึกและโหลด Config

### Storage Location
```javascript
localStorage.setItem('cmms_hours_to_tasks_config', JSON.stringify({
  hoursPerTask: 3,
  enabled: true
}));
```

### Auto-load on Page Load
```javascript
document.addEventListener('DOMContentLoaded', function() {
  loadConversionConfig();  // โหลดค่าจาก localStorage
  // ... initialize other components
});
```

### Config Structure
```javascript
{
  "hoursPerTask": 3,      // อัตราแปลง (ชม./งาน)
  "enabled": true         // เปิดใช้งานหรือไม่
}
```

---

## 🔧 การปรับแต่งเพิ่มเติม

### 1. เปลี่ยนค่าเริ่มต้น
แก้ไขใน JavaScript:
```javascript
let conversionConfig = {
  hoursPerTask: 3,    // เปลี่ยนเป็น 2, 4, หรือค่าที่ต้องการ
  enabled: true
};
```

### 2. เพิ่ม Preset ใหม่
เพิ่มปุ่มใน HTML:
```html
<button class="conversion-preset-btn" onclick="applyConversionPreset(5)" data-preset="5">
  <div>5 ชม.</div>
  <div style="font-size: 0.65rem;">ต่อ 1 งาน</div>
</button>
```

### 3. ปรับรูปแบบการแสดงผล
แก้ CSS class `.hours-tasks-badge`:
```css
.hours-tasks-badge {
  /* ปรับสี, ขนาด, spacing ตามต้องการ */
  background: linear-gradient(135deg, #EFF6FF 0%, white 100%);
  border: 1px solid #BFDBFE;
}
```

---

## 📊 Use Cases

### Case 1: วางแผนกำลังคน
**สถานการณ์**: ต้องการทราบว่าต้องใช้ช่างกี่คนสำหรับงานทั้งหมด

**การใช้งาน**:
1. ดู Total Equipment Hours: 18 ชม.
2. แปลงเป็น: 18 ชม. ≈ 6 งาน (ใช้ 3 ชม./งาน)
3. สรุป: **ต้องใช้ช่าง 6 คน** (ถ้าแต่ละคนทำ 1 งาน)

### Case 2: จัดสรร OT
**สถานการณ์**: คำนวณงาน OT เป็นจำนวนงาน

**การใช้งาน**:
1. ช่าง A: OT 4 ชม. → 1.3 งาน
2. ช่าง B: OT 6 ชม. → 2 งาน
3. รวม OT: 10 ชม. → **3.3 งาน**

### Case 3: ประเมินความจุ
**สถานการณ์**: ตรวจสอบว่าช่างที่มีเพียงพอหรือไม่

**การใช้งาน**:
1. งานรวม: 21 ชม. → 7 งาน
2. ช่างพร้อม: 5 คน (capacity: 5 งาน)
3. สรุป: **ขาด 2 งาน** → ต้องหาช่างเพิ่มหรือใช้ OT

---

## ⚠️ ข้อควรระวัง

1. **อัตราแปลงไม่เท่ากันทุกงาน**
   - งานซ่อมเร่งด่วนอาจใช้เวลามากกว่าปกติ
   - งานที่ต้องรอ parts อาจใช้เวลาน้อยกว่า

2. **ใช้เป็นแนวทางเท่านั้น**
   - ไม่ใช่ค่าแม่นยำ 100%
   - ควรปรับตามประสบการณ์จริง

3. **ความแตกต่างระหว่างทีม**
   - ทีมที่มีประสบการณ์อาจทำงานเร็วกว่า
   - ควรพิจารณา skill level ด้วย

4. **การปัดเศษ**
   - ระบบปัดเศษทศนิยม 1 ตำแหน่ง
   - งาน 0.7 อาจต้องปัดเป็น 1 งานจริง

---

## 🚀 การพัฒนาต่อยอด

### แนวทางที่เป็นไปได้:

1. **อัตราแปลงหลายระดับ**
   - Easy tasks: 2 ชม./งาน
   - Medium tasks: 3 ชม./งาน
   - Hard tasks: 5 ชม./งาน

2. **อัตราแปลงตาม Technician Skill**
   - Junior: 4 ชม./งาน
   - Senior: 2.5 ชม./งาน

3. **อัตราแปลงตามประเภทงาน**
   - PM: 2 ชม./งาน
   - CM: 3.5 ชม./งาน
   - BM: 6 ชม./งาน

4. **Machine Learning Prediction**
   - เรียนรู้จากข้อมูลในอดีต
   - ปรับอัตราแปลงอัตโนมัติ

5. **Reports & Analytics**
   - สถิติการใช้งานระบบ
   - ความแม่นยำของการประมาณ
   - Variance analysis

---

## 📝 สรุป

ระบบ **Hours to Tasks Conversion** ช่วยให้:
- ✅ แปลงเวลาเป็นหน่วยงานได้อัตโนมัติ
- ✅ ปรับอัตราแปลงได้ตามความต้องการ
- ✅ แสดงผลทั้งสองค่าพร้อมกัน
- ✅ บันทึกและโหลดการตั้งค่าอัตโนมัติ
- ✅ ใช้งานง่าย มี UI ที่เข้าใจง่าย

**อัตราแปลงมาตรฐาน**: 3 ชั่วโมง = 1 งาน

**Configuration Panel**: มุมขวาล่างของหน้า Daily Capacity

---

## 📞 ติดต่อสอบถาม

หากมีคำถามหรือต้องการความช่วยเหลือเพิ่มเติม:
- ดูเอกสารเพิ่มเติมใน `/cmms/docs/`
- ติดต่อทีมพัฒนาระบบ

**เอกสารนี้อัปเดตล่าสุด**: 9 ธันวาคม 2025
