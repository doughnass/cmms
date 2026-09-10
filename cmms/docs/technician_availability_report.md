# 📊 รายงานตารางช่างเทคนิค

## 🎯 ภาพรวม

หน้ารายงานสรุปตารางช่างเทคนิคแบบ **Read-only** สำหรับดูข้อมูลและวิเคราะห์สถิติการทำงานของช่างทุกคน

## 📍 การเข้าถึง

### URL
```
/maintenance/technicians/availability/report/
/maintenance/technicians/availability/report/?month=10&year=2025
```

### จากหน้าจัดการตาราง
1. เปิดหน้าจัดการตารางช่าง
2. คลิกปุ่ม **"รายงานสรุป"** (สีเขียว) ที่มุมขวาบน
3. ระบบจะพาไปหน้ารายงานพร้อมเดือน/ปีที่เลือกไว้

## ✨ ฟีเจอร์หลัก

### 1. สถิติรวมภาพรวม (Overview Statistics)
แสดง 4 การ์ดสถิติ:
- 🟢 **วันทำงานทั้งหมด** - จำนวนวันที่มีช่างทำงาน
- 🟡 **วันล่วงเวลาทั้งหมด** - จำนวนวัน OT
- 🔴 **วันลาทั้งหมด** - จำนวนวันลา
- 🔵 **บันทึกทั้งหมด** - จำนวนบันทึกทั้งหมด

### 2. สรุปรายบุคคล (Technician Summary)
ตารางแสดงสถิติแต่ละคน:
- ชื่อช่าง
- จำนวนวันทำงาน (พร้อม progress bar)
- จำนวนวันล่วงเวลา (พร้อม progress bar)
- จำนวนวันลา (พร้อม progress bar)
- รวมทั้งหมด

**Progress Bar:**
- แสดงเปอร์เซ็นต์เทียบกับจำนวนวันในเดือน
- สีเขียว = ทำงาน
- สีเหลือง = ล่วงเวลา
- สีแดง = ลา

### 3. ตารางรายละเอียด (Calendar View)
ตารางแสดงข้อมูลทั้งเดือนแบบ Read-only:
- แถว = ช่างแต่ละคน
- คอลัมน์ = วันที่ในเดือน
- เซลล์ = Badge แสดงสถานะ (ทำงาน/ล่วงเวลา/ลา/-)

**ไฮไลท์พิเศษ:**
- 🏛️ วันหยุดราชการ (พื้นสีแดง)
- 📅 วันเสาร์-อาทิตย์ (พื้นสีเหลือง)
- 📌 วันนี้ (พื้นสีฟ้า)

### 4. ฟังก์ชันเพิ่มเติม

#### 🖨️ พิมพ์รายงาน
- คลิกปุ่ม **"พิมพ์"**
- ระบบจะซ่อนปุ่มควบคุมและเตรียมหน้าสำหรับพิมพ์
- รองรับการบันทึกเป็น PDF

#### ✏️ แก้ไขข้อมูล
- คลิกปุ่ม **"แก้ไข"**
- จะกลับไปหน้าจัดการตารางพร้อมเดือน/ปีที่เลือก

#### 📅 เปลี่ยนเดือน/ปี
- เลือกเดือนและปีจาก dropdown
- คลิก **"แสดง"**
- ระบบจะโหลดข้อมูลใหม่

## 🔍 การอ่านข้อมูล

### Status Badge
| Badge | ความหมาย | สี |
|-------|---------|-----|
| **ทำงาน** | เข้างานปกติ | เขียว |
| **ล่วงเวลา** | OT / ทำงานนอกเวลา | เหลือง |
| **ลา** | ลาป่วย ลากิจ | แดง |
| **-** | ไม่มีข้อมูล | เทา |

### Progress Bar
```
████████░░ 80%  = ทำงาน 24/30 วัน
```
- เต็ม 100% = ทำทุกวันในเดือน
- 50% = ทำครึ่งหนึ่งของเดือน

## 📋 ข้อมูลที่แสดง

### ที่มาของข้อมูล
- **ฐานข้อมูล:** `TechnicianAvailability` model
- **กรอง:** ตาม `work_date__year` และ `work_date__month`
- **รีเลชัน:** join กับ `Technician` model

### การคำนวณสถิติ
```python
# สำหรับแต่ละช่าง
work_count = จำนวน status='work'
ot_count = จำนวน status='ot'
leave_count = จำนวน status='leave'

# สำหรับภาพรวม
total_work = รวม work_count ของทุกคน
total_ot = รวม ot_count ของทุกคน
total_leave = รวม leave_count ของทุกคน
total_records = total_work + total_ot + total_leave
```

## 🎨 UI/UX Design

### Color Scheme
- **Primary:** `#6366f1` (Indigo)
- **Success:** `#10b981` (Green)
- **Warning:** `#f59e0b` (Amber)
- **Danger:** `#ef4444` (Red)

### Responsive Design
- Desktop: Grid layout 4 คอลัมน์
- Tablet: Grid auto-fit
- Mobile: 1 คอลัมน์ต่อแถว

### Print-Friendly
- ซ่อนปุ่มควบคุมทั้งหมด (class: `no-print`)
- แสดงหัวเรื่องพิเศษสำหรับพิมพ์
- ลบ box-shadow และ background gradient

## 🔧 Technical Details

### Template File
```
cmms/templates/maintenance/technician_availability_report.html
```

### View Function
```python
def technician_availability_report(request):
    # Get month/year from GET params
    # Query availabilities for selected month
    # Serialize data to JSON
    # Render template with context
```

### URL Pattern
```python
path('maintenance/technicians/availability/report/', 
     views.technician_availability_report, 
     name='technician_availability_report')
```

### Context Variables
```python
{
    'date': datetime.date object (1st day of month),
    'technicians': [{id, name}, ...],
    'availabilities': [{id, technician, work_date, status, note}, ...]
}
```

### JavaScript Features
- โหลดวันหยุดจาก `localStorage` (key: `cmms_holidays`)
- คำนวณสถิติแบบ client-side
- สร้าง Calendar dynamically
- Render Progress bars

## 📊 ตัวอย่างการใช้งาน

### Case 1: ดูรายงานเดือนปัจจุบัน
1. เข้าหน้ารายงาน (จะแสดงเดือนปัจจุบันอัตโนมัติ)
2. ดูสถิติรวมทั้งหมด
3. เช็คช่างคนไหนทำงานมากที่สุด
4. ดูรายละเอียดในตาราง

### Case 2: เปรียบเทียบข้อมูลหลายเดือน
1. เลือกเดือน 1 → ดูสถิติ
2. เลือกเดือน 2 → ดูสถิติ
3. เปรียบเทียบ total_work, total_ot

### Case 3: พิมพ์รายงานส่งผู้บริหาร
1. เลือกเดือนที่ต้องการ
2. คลิก "พิมพ์"
3. บันทึกเป็น PDF
4. ส่งรายงาน

## 🔐 Permissions

- ไม่มีการจำกัดสิทธิ์ (ทุกคนดูได้)
- ถ้าต้องการจำกัด ให้เพิ่ม decorator:
```python
@login_required
@permission_required('cmms.view_technicianavailability')
def technician_availability_report(request):
    ...
```

## 🐛 Troubleshooting

### ไม่มีข้อมูลแสดง
- ✅ เช็คว่ามีการบันทึกตารางแล้วหรือยัง
- ✅ เช็ค month/year ใน URL
- ✅ เช็ค availabilities ในฐานข้อมูล

### สถิติไม่ตรง
- ✅ เช็ค JavaScript Console มี error ไหม
- ✅ เช็ค status values ในฐานข้อมูล (ต้องเป็น 'work', 'ot', 'leave')

### วันหยุดไม่แสดง
- ✅ เช็ค localStorage (`cmms_holidays`)
- ✅ เพิ่มวันหยุดในหน้าจัดการตาราง

## 🚀 Future Enhancements

- [ ] Export เป็น Excel
- [ ] Export เป็น PDF (server-side)
- [ ] กราฟแสดงสถิติแบบ Chart.js
- [ ] เปรียบเทียบหลายเดือน
- [ ] กรองตามทักษะช่าง
- [ ] Email รายงานอัตโนมัติ
- [ ] Dashboard แบบ Real-time

## 📞 Support

หากมีปัญหาหรือข้อสงสัย ติดต่อ:
- 📧 Email: support@cmms.example.com
- 💬 Issues: GitHub Issues
- 📚 Docs: `/docs/technician_availability_report.md`
