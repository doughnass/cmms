# ระบบบันทึกประวัติการขึ้นทะเบียนและแก้ไขอุปกรณ์
# Equipment Registration and Edit History Tracking System

## ภาพรวม (Overview)

ระบบบันทึกประวัติการขึ้นทะเบียนและแก้ไขอุปกรณ์ถูกออกแบบเพื่อติดตามการเปลี่ยนแปลงทั้งหมดที่เกิดขึ้นกับข้อมูลอุปกรณ์ โดยใช้ Audit Trail Pattern ที่สามารถตรวจสอบย้อนหลังได้ว่าใครทำอะไร เมื่อไหร่ และเปลี่ยนแปลงอะไรบ้าง

The equipment registration and edit history tracking system is designed to track all changes to equipment data using an Audit Trail Pattern that allows you to review who did what, when, and what changed.

---

## 🏗️ สถาปัตยกรรม (Architecture)

### 1. Database Schema

#### Equipment_list Model (Extended)
เพิ่มฟิลด์ต่อไปนี้ในโมเดล `Equipment_list`:

```python
# ประวัติการขึ้นทะเบียนและแก้ไข (Audit Trail)
created_at = DateTimeField(auto_now_add=True)      # วันที่สร้าง
created_by = CharField(max_length=100)             # ผู้สร้าง
updated_at = DateTimeField(auto_now=True)          # วันที่แก้ไขล่าสุด
updated_by = CharField(max_length=100)             # ผู้แก้ไขล่าสุด
```

**จุดประสงค์:**
- `created_at/created_by`: บันทึกว่าใครสร้างทะเบียนเมื่อไหร่ (บันทึกครั้งเดียว)
- `updated_at/updated_by`: บันทึกว่าใครแก้ไขล่าสุดเมื่อไหร่ (อัปเดตทุกครั้งที่แก้ไข)

#### EquipmentHistory Model (New)
โมเดลใหม่สำหรับบันทึกประวัติทุกการเปลี่ยนแปลง:

```python
class EquipmentHistory(models.Model):
    equipment_id = CharField(max_length=20)                    # รหัสเครื่อง
    action_type = CharField(choices=['CREATE', 'UPDATE', 'DELETE'])  # ประเภท
    action_by = CharField(max_length=100)                      # ผู้ดำเนินการ
    action_at = DateTimeField(auto_now_add=True)              # เวลา
    ip_address = GenericIPAddressField()                       # IP Address
    
    # JSON fields for detailed tracking
    changed_fields = JSONField()       # รายการฟิลด์ที่เปลี่ยน: ["field1", "field2"]
    old_values = JSONField()           # ค่าเดิม: {"field1": "old", "field2": "old"}
    new_values = JSONField()           # ค่าใหม่: {"field1": "new", "field2": "new"}
    
    notes = TextField()                # หมายเหตุเพิ่มเติม
```

**จุดประสงค์:**
- บันทึกทุกการเปลี่ยนแปลง (CREATE, UPDATE, DELETE)
- เก็บรายละเอียดว่าฟิลด์ไหนเปลี่ยนจากอะไรเป็นอะไร
- ติดตาม IP address สำหรับ security audit

---

## 📋 การทำงาน (Workflow)

### 1. สร้างทะเบียนใหม่ (CREATE)

```python
# ใน views.py -> add_equipment()
equipment_list = Equipment_list.objects.create(
    equipment_id="MEDCMU-001234",
    equipment_name_TH="เครื่อง X-Ray",
    # ... ฟิลด์อื่นๆ ...
    created_by=request.user.get_full_name()  # เพิ่ม created_by
)

# บันทึกประวัติการสร้าง
new_data = capture_equipment_snapshot(equipment_list)
log_equipment_history(
    equipment_id=equipment_list.equipment_id,
    action_type='CREATE',
    user=request.user,
    request=request,
    new_data=new_data,
    notes='สร้างทะเบียนอุปกรณ์ใหม่'
)
```

**ผลลัพธ์:**
- `Equipment_list`: มี `created_at`, `created_by` บันทึกเวลาและผู้สร้าง
- `EquipmentHistory`: มี 1 record บันทึกการสร้างพร้อมข้อมูลทั้งหมด

---

### 2. แก้ไขทะเบียน (UPDATE)

```python
# ใน views.py -> edit_equipment()
# 1. บันทึกข้อมูลเดิมก่อนแก้ไข
old_data = capture_equipment_snapshot(equipment_list)

# 2. แก้ไขข้อมูล
equipment_list.equipment_name_TH = "เครื่อง X-Ray ใหม่"
equipment_list.updated_by = request.user.get_full_name()  # เพิ่ม updated_by
equipment_list.save()

# 3. บันทึกประวัติการแก้ไข
new_data = capture_equipment_snapshot(equipment_list)
log_equipment_history(
    equipment_id=equipment_list.equipment_id,
    action_type='UPDATE',
    user=request.user,
    request=request,
    old_data=old_data,
    new_data=new_data,
    notes='แก้ไขทะเบียนอุปกรณ์'
)
```

**ผลลัพธ์:**
- `Equipment_list`: `updated_at`, `updated_by` อัปเดตเป็นเวลาและผู้แก้ไขล่าสุด
- `EquipmentHistory`: มี 1 record ใหม่บันทึกว่าฟิลด์ไหนเปลี่ยนจากอะไรเป็นอะไร

---

## 🛠️ ฟังก์ชันสำคัญ (Key Functions)

### history_utils.py

#### 1. `log_equipment_history()`
บันทึกประวัติการดำเนินการ

```python
log_equipment_history(
    equipment_id='MEDCMU-001234',
    action_type='UPDATE',                # 'CREATE', 'UPDATE', 'DELETE'
    user=request.user,                   # Django User object
    request=request,                     # Django request (สำหรับ IP)
    old_data={'field1': 'old'},          # ข้อมูลเดิม (สำหรับ UPDATE)
    new_data={'field1': 'new'},          # ข้อมูลใหม่
    notes='หมายเหตุเพิ่มเติม'
)
```

#### 2. `capture_equipment_snapshot()`
ถ่ายภาพข้อมูลปัจจุบันของอุปกรณ์

```python
snapshot = capture_equipment_snapshot(equipment_list)
# Returns: {
#     'equipment_id': 'MEDCMU-001234',
#     'equipment_name_TH': 'เครื่อง X-Ray',
#     'equipment_price': '100000',
#     # ... ฟิลด์อื่นๆ ทั้งหมด ...
# }
```

#### 3. `get_equipment_history()`
ดึงประวัติของอุปกรณ์

```python
history = get_equipment_history('MEDCMU-001234', limit=10)
# Returns: QuerySet of EquipmentHistory objects (10 records ล่าสุด)
```

#### 4. `format_field_name()`
แปลงชื่อฟิลด์เป็นภาษาไทย

```python
format_field_name('equipment_name_TH')  # Returns: 'ชื่อเครื่อง (ไทย)'
format_field_name('equipment_price')    # Returns: 'ราคา'
```

---

## 🎨 UI/UX - หน้าแสดงประวัติ

### URL
```
/equipment_history/<equipment_list_id>/
```

### Template
`cmms/templates/equipment/equipment_history.html`

### Features

#### 1. Equipment Header
แสดงข้อมูลสรุปอุปกรณ์:
- รหัสเครื่อง (equipment_id)
- ชื่อเครื่อง (equipment_name_TH)
- วันที่สร้าง (created_at)
- วันที่แก้ไขล่าสุด (updated_at)

#### 2. Timeline Display
แสดงประวัติในรูปแบบ Timeline:
- **CREATE**: จุดสีเขียว + ข้อมูลที่สร้าง
- **UPDATE**: จุดสีเหลือง + ฟิลด์ที่เปลี่ยนแปลง (เก่า → ใหม่)
- **DELETE**: จุดสีแดง + ข้อมูลก่อนลบ

#### 3. Change Details
สำหรับแต่ละ UPDATE แสดง:
- ฟิลด์ที่เปลี่ยน (เช่น "ชื่อเครื่อง (ไทย)")
- ค่าเดิม (สีแดง, ขีดทับ)
- ค่าใหม่ (สีเขียว, เน้น)

#### 4. Metadata
แต่ละ record แสดง:
- ผู้ดำเนินการ (action_by)
- เวลา (action_at) - รูปแบบ: dd/mm/yyyy HH:MM:SS
- IP Address (ip_address)
- หมายเหตุ (notes)

---

## 📊 ตัวอย่างข้อมูล (Example Data)

### สถานการณ์: สร้างและแก้ไขทะเบียน 2 ครั้ง

#### Record 1: CREATE
```json
{
  "equipment_id": "MEDCMU-001234",
  "action_type": "CREATE",
  "action_by": "นายสมชาย ใจดี",
  "action_at": "2024-01-15 10:30:00",
  "ip_address": "192.168.1.100",
  "changed_fields": ["equipment_id", "equipment_name_TH", "equipment_price"],
  "old_values": {},
  "new_values": {
    "equipment_id": "MEDCMU-001234",
    "equipment_name_TH": "เครื่อง X-Ray",
    "equipment_price": "100000"
  },
  "notes": "สร้างทะเบียนอุปกรณ์ใหม่"
}
```

#### Record 2: UPDATE (แก้ไขชื่อและราคา)
```json
{
  "equipment_id": "MEDCMU-001234",
  "action_type": "UPDATE",
  "action_by": "นางสาวสมหญิง รักงาน",
  "action_at": "2024-01-20 14:15:00",
  "ip_address": "192.168.1.101",
  "changed_fields": ["equipment_name_TH", "equipment_price"],
  "old_values": {
    "equipment_name_TH": "เครื่อง X-Ray",
    "equipment_price": "100000"
  },
  "new_values": {
    "equipment_name_TH": "เครื่อง X-Ray รุ่นใหม่",
    "equipment_price": "150000"
  },
  "notes": "แก้ไขทะเบียนอุปกรณ์"
}
```

#### Record 3: UPDATE (แก้ไขเฉพาะหน่วยงาน)
```json
{
  "equipment_id": "MEDCMU-001234",
  "action_type": "UPDATE",
  "action_by": "นายสมชาย ใจดี",
  "action_at": "2024-01-25 09:00:00",
  "ip_address": "192.168.1.100",
  "changed_fields": ["equipment_owner_customer"],
  "old_values": {
    "equipment_owner_customer": "คณะแพทยศาสตร์"
  },
  "new_values": {
    "equipment_owner_customer": "คณะวิทยาศาสตร์"
  },
  "notes": "แก้ไขทะเบียนอุปกรณ์"
}
```

---

## 🔒 Security & Performance

### Security Features

1. **IP Address Tracking**
   - บันทึก IP ของผู้ใช้ทุกครั้ง
   - ช่วยระบุตัวตนและตรวจสอบการเข้าถึงผิดปกติ

2. **Read-only History**
   - ข้อมูลประวัติไม่สามารถลบหรือแก้ไขได้ (admin panel)
   - รักษาความสมบูรณ์ของข้อมูล Audit Trail

3. **User Authentication Required**
   - ต้อง login ก่อนเข้าถึงหน้าประวัติ
   - บันทึกชื่อผู้ใช้ที่แท้จริง (full name หรือ username)

### Performance Optimization

1. **Database Indexing**
   ```python
   indexes = [
       Index(fields=['equipment_id', '-action_at']),  # ค้นหาประวัติของอุปกรณ์
       Index(fields=['action_type']),                  # Filter ตามประเภท
   ]
   ```

2. **Query Optimization**
   - ใช้ `order_by('-action_at')` สำหรับแสดงผลล่าสุดก่อน
   - รองรับ pagination ด้วย `limit` parameter

3. **JSON Storage**
   - เก็บ changed_fields, old_values, new_values ใน JSON
   - ประหยัดพื้นที่กว่าสร้าง table แยก

---

## 🚀 การใช้งาน (Usage)

### 1. เพิ่มลิงก์ประวัติในรายการอุปกรณ์

```html
<!-- ใน equipment_list.html -->
<a href="{% url 'equipment_history' equipment.id %}" class="btn btn-info">
    <i class="bi bi-clock-history"></i> ดูประวัติ
</a>
```

### 2. แสดงประวัติในหน้ารายละเอียด

```html
<!-- ใน equipment_detail.html -->
<div class="history-summary">
    <h5>ประวัติล่าสุด</h5>
    {% for record in recent_history %}
        <div class="history-item">
            {{ record.action_at|date:'d/m/Y H:i' }} - 
            {{ record.get_action_type_display }} โดย {{ record.action_by }}
        </div>
    {% endfor %}
    <a href="{% url 'equipment_history' equipment.id %}">ดูทั้งหมด</a>
</div>
```

### 3. ตรวจสอบประวัติใน Admin Panel

1. เข้า Django Admin: `/admin/`
2. ไปที่ "ประวัติการขึ้นทะเบียนอุปกรณ์" (Equipment Histories)
3. ค้นหาด้วย equipment_id หรือ action_by
4. Filter ด้วย action_type (CREATE/UPDATE/DELETE)

---

## 🔧 Migration

### Run Migration

```bash
# สร้าง migration file (ถ้ายังไม่มี)
python manage.py makemigrations cmms

# Run migration
python manage.py migrate cmms 0040_equipment_history_tracking
```

### สำหรับข้อมูลเก่า (Existing Data)

ข้อมูลอุปกรณ์ที่มีอยู่แล้วจะมี:
- `created_at`: วันที่ run migration (ไม่ใช่วันที่สร้างจริง)
- `created_by`: ว่าง (ไม่ทราบผู้สร้างจริง)
- `updated_at`: วันที่ run migration
- `updated_by`: ว่าง

**แนะนำ:**
- สร้าง script อัปเดต `created_at` จาก `equipment_register_date` ถ้ามี
- สร้าง script อัปเดต `created_by` จาก `equipment_register_adminname` ถ้ามี

---

## 📝 ข้อควรระวัง (Considerations)

### 1. Storage Space
- ประวัติเพิ่มขึ้นทุกครั้งที่แก้ไข
- คำนวณว่าระบบต้องเก็บประวัตินานแค่ไหน
- พิจารณาทำ data archiving สำหรับข้อมูลเก่ามากๆ

### 2. Privacy
- ข้อมูล IP address อาจเป็น personal data
- ต้องปฏิบัติตาม PDPA หรือ GDPR ถ้ามี

### 3. Bulk Operations
- ถ้ามีการ bulk update ควรระวังเรื่องจำนวน history records
- พิจารณาใช้ `log_equipment_history()` แบบ batch

---

## 🎯 Future Enhancements

### 1. Advanced Features
- [ ] Compare versions (เปรียบเทียบ 2 versions)
- [ ] Restore to previous version (คืนค่าไปเวอร์ชันเก่า)
- [ ] Export history to Excel/PDF
- [ ] Email notifications on specific changes

### 2. Dashboard & Analytics
- [ ] Dashboard แสดงจำนวนการแก้ไขต่อเดือน
- [ ] Top editors ranking
- [ ] Most changed equipment
- [ ] Change frequency analysis

### 3. Integration
- [ ] Integrate กับ django-auditlog
- [ ] Real-time notifications ด้วย WebSocket
- [ ] API endpoint สำหรับ external systems

---

## 📞 Support

หากมีคำถามหรือพบปัญหา กรุณาติดต่อ:
- Developer: CMMS Development Team
- Email: support@cmms.example.com

---

**เอกสารนี้อัปเดตล่าสุด: {{ current_date }}**
