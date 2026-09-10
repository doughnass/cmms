# 🎯 วิธีตั้งค่า Work Status แบบมีประเภทย่อย

## 📋 ภาพรวม

ระบบตอนนี้รองรับการเลือก **ประเภทย่อย** ของสถานะการทำงาน เช่น:
- **ทำงาน** → (ไม่มีประเภทย่อย)
- **ล่วงเวลา (OT)** → OT วันธรรมดา, OT วันหยุด, OT กลางคืน
- **ลา** → ลาป่วย, ลากิจ, ลาพักร้อน

## 🔧 ขั้นตอนการตั้งค่า

### **1. เข้าหน้าจัดการ Master Data**
```
http://localhost:8000/master/manage/work_status/
```

หรือ:
1. เข้าเมนู **Master Data**
2. เลือก Category: **work_status**

---

### **2. สร้างสถานะหลัก (Parent)**

#### **ตัวอย่าง: สถานะ "ทำงาน"**
```
Category: work_status
Code: work
Label: ทำงาน
Description: success (สีเขียว)
Active: ✓
Order: 1
Parent: (ไม่เลือก)
```

#### **ตัวอย่าง: สถานะ "ล่วงเวลา"**
```
Category: work_status
Code: ot
Label: ล่วงเวลา
Description: warning (สีเหลือง)
Active: ✓
Order: 2
Parent: (ไม่เลือก)
```

#### **ตัวอย่าง: สถานะ "ลา"**
```
Category: work_status
Code: leave
Label: ลา
Description: danger (สีแดง)
Active: ✓
Order: 3
Parent: (ไม่เลือก)
```

---

### **3. สร้างประเภทย่อย (Children)**

#### **ประเภทย่อยของ "ล่วงเวลา":**

**OT วันธรรมดา:**
```
Category: work_status
Code: ot_weekday
Label: OT วันธรรมดา
Description: warning
Active: ✓
Order: 1
Parent: ล่วงเวลา (เลือกจาก dropdown)
```

**OT วันหยุด:**
```
Category: work_status
Code: ot_holiday
Label: OT วันหยุด
Description: warning
Active: ✓
Order: 2
Parent: ล่วงเวลา
```

**OT กลางคืน:**
```
Category: work_status
Code: ot_night
Label: OT กลางคืน
Description: warning
Active: ✓
Order: 3
Parent: ล่วงเวลา
```

---

#### **ประเภทย่อยของ "ลา":**

**ลาป่วย:**
```
Category: work_status
Code: leave_sick
Label: ลาป่วย
Description: danger
Active: ✓
Order: 1
Parent: ลา
```

**ลากิจ:**
```
Category: work_status
Code: leave_personal
Label: ลากิจ
Description: danger
Active: ✓
Order: 2
Parent: ลา
```

**ลาพักร้อน:**
```
Category: work_status
Code: leave_vacation
Label: ลาพักร้อน
Description: danger
Active: ✓
Order: 3
Parent: ลา
```

**ลาคลอด:**
```
Category: work_status
Code: leave_maternity
Label: ลาคลอด
Description: danger
Active: ✓
Order: 4
Parent: ลา
```

---

## 🎨 โครงสร้างข้อมูล

```
work_status (Category)
│
├── ทำงาน (work) - ไม่มีลูก
│
├── ล่วงเวลา (ot) - มีลูก
│   ├── OT วันธรรมดา (ot_weekday)
│   ├── OT วันหยุด (ot_holiday)
│   └── OT กลางคืน (ot_night)
│
└── ลา (leave) - มีลูก
    ├── ลาป่วย (leave_sick)
    ├── ลากิจ (leave_personal)
    ├── ลาพักร้อน (leave_vacation)
    └── ลาคลอด (leave_maternity)
```

---

## 💡 การใช้งานในระบบ

### **หน้าจัดการตารางช่าง**

#### **สถานะที่ไม่มีลูก (เช่น "ทำงาน"):**
- แสดงเป็นปุ่มธรรมดา ✓
- คลิกเลือกได้เลย

#### **สถานะที่มีลูก (เช่น "ล่วงเวลา", "ลา"):**
- แสดงเป็นปุ่มพร้อม dropdown 🔽
- **คลิกปุ่ม** → เปิด dropdown แสดงตัวเลือก:
  - ล่วงเวลา (ประเภทหลัก)
  - ───────────
  - OT วันธรรมดา
  - OT วันหยุด
  - OT กลางคืน
- **เลือกประเภทใดก็ได้** → บันทึกเป็น code ของประเภทนั้น

---

## 📊 ตัวอย่างการบันทึกข้อมูล

### **ข้อมูลที่บันทึกในฐานข้อมูล:**

| technician_id | date       | status           |
|---------------|------------|------------------|
| 5             | 2025-10-01 | work             |
| 5             | 2025-10-02 | ot_weekday       |
| 5             | 2025-10-03 | ot_holiday       |
| 5             | 2025-10-04 | leave_sick       |
| 6             | 2025-10-01 | work             |
| 6             | 2025-10-02 | leave_personal   |

### **การแสดงผลในรายงาน:**

| ช่าง      | วันที่ | สถานะ            |
|-----------|--------|------------------|
| นายสมชาย  | 1 ต.ค. | ทำงาน            |
| นายสมชาย  | 2 ต.ค. | OT วันธรรมดา     |
| นายสมชาย  | 3 ต.ค. | OT วันหยุด       |
| นายสมชาย  | 4 ต.ค. | ลาป่วย           |

---

## 🔍 การค้นหาและสถิติ

### **สถิติแบ่งตามประเภทหลัก:**

```python
# นับรวมตามประเภทหลัก
work_count = 1  # work
ot_count = 2    # ot_weekday + ot_holiday
leave_count = 1 # leave_sick
```

### **สถิติแบ่งตามประเภทย่อย:**

```python
{
  'work': 1,
  'ot_weekday': 1,
  'ot_holiday': 1,
  'leave_sick': 1
}
```

---

## 🎨 สีที่รองรับ

ตั้งค่าใน **Description** field:

| สี | Class | ใช้กับ |
|----|-------|--------|
| 🟢 เขียว | `success` | ทำงาน |
| 🟡 เหลือง | `warning` | ล่วงเวลา |
| 🔴 แดง | `danger` | ลา |
| 🔵 น้ำเงิน | `primary` | อื่นๆ |
| ⚪ เทา | `secondary` | default |

---

## ⚙️ การ Import จาก Excel

### **รูปแบบไฟล์ Excel:**

| category    | code           | label          | description | active | order | parent_category | parent_code |
|-------------|----------------|----------------|-------------|--------|-------|-----------------|-------------|
| work_status | work           | ทำงาน          | success     | TRUE   | 1     |                 |             |
| work_status | ot             | ล่วงเวลา       | warning     | TRUE   | 2     |                 |             |
| work_status | ot_weekday     | OT วันธรรมดา   | warning     | TRUE   | 1     | work_status     | ot          |
| work_status | ot_holiday     | OT วันหยุด     | warning     | TRUE   | 2     | work_status     | ot          |
| work_status | ot_night       | OT กลางคืน     | warning     | TRUE   | 3     | work_status     | ot          |
| work_status | leave          | ลา             | danger      | TRUE   | 3     |                 |             |
| work_status | leave_sick     | ลาป่วย         | danger      | TRUE   | 1     | work_status     | leave       |
| work_status | leave_personal | ลากิจ          | danger      | TRUE   | 2     | work_status     | leave       |
| work_status | leave_vacation | ลาพักร้อน      | danger      | TRUE   | 3     | work_status     | leave       |

### **วิธี Import:**
1. เข้า: `/master/import/`
2. เลือกไฟล์ Excel
3. Upload
4. ระบบจะสร้าง parent-child relationship อัตโนมัติ

---

## 🐛 Troubleshooting

### **ปัญหา: ไม่เห็น dropdown**
✅ **แก้ไข:**
- ตรวจสอบว่าสถานะหลักมี **children** หรือยัง
- เช็คว่า children ตั้งค่า `Active = TRUE`
- ตรวจสอบ `Parent` field ว่าเลือกถูกต้อง

### **ปัญหา: dropdown ไม่แสดงตัวเลือก**
✅ **แก้ไข:**
- ตรวจสอบ JavaScript Console มี error ไหม
- เช็ค `work_statuses` ใน template ว่ามี `children` array

### **ปัญหา: บันทึกแล้วไม่เห็นข้อมูล**
✅ **แก้ไข:**
- ตรวจสอบ `status` ที่บันทึกในฐานข้อมูล
- เช็คว่าใช้ `code` ของ child ไม่ใช่ `code` ของ parent

---

## 📚 เอกสารเพิ่มเติม

- [Master Data Management](/master/manage/)
- [Technician Availability Guide](/docs/technician_availability_report.md)
- [API Documentation](/api/docs/)

---

## 🎯 Best Practices

### **การตั้งชื่อ Code:**
- ใช้ lowercase
- ขั้นด้วย underscore (`_`)
- prefix ตาม parent เช่น `ot_`, `leave_`

### **การจัดเรียง Order:**
- Parent: 1, 2, 3, ...
- Children: 1, 2, 3, ... (เรียงภายใต้ parent)

### **การใช้สี:**
- ใช้สีที่สื่อความหมาย
- เขียว = ดี, เหลือง = เฝ้าระวัง, แดง = หยุด

---

## 💾 Backup ข้อมูล

### **Export Master Data:**
```bash
python manage.py dumpdata cmms.MasterItem --indent 2 > work_status_backup.json
```

### **Import Master Data:**
```bash
python manage.py loaddata work_status_backup.json
```

---

**สร้างโดย:** CMMS Development Team  
**วันที่อัพเดท:** 2025-10-17  
**เวอร์ชัน:** 2.0
