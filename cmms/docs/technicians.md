เอกสารสั้น: Technicians, skills_m และการย้ายข้อมูล

บทนำ
- ตอนนี้ระบบเก็บทักษะของช่างในรูปแบบ normalized ManyToMany `skills_m` ที่ชี้ไปยัง `MasterItem` (category='technician_skill')
- เพื่อความเข้ากันได้กับข้อมูลเก่า เราสร้างคำสั่ง management command เพื่อแปลงค่า legacy comma-separated `Technician.skills` เป็น `MasterItem` และเชื่อมความสัมพันธ์ `skills_m`
- ปัจจุบันระบบได้ duplicate รายการ MasterItem ที่ถูกสร้างจาก `Equipment_list.equipment_type` ลงใน category `equipments` (migration `0019`), อัปเดตฟิลด์ `skills_m` ให้จำกัดรายการเป็น `equipments` (migration `0020`), และคัดลอกความสัมพันธ์ M2M ไปยังรายการใหม่ (migration `0021`).

คำสั่งย้ายข้อมูล
- คำสั่ง: `python manage.py migrate_skills_to_master`
 - คำสั่ง: `python manage.py migrate_skills_to_master`
- ตัวเลือก: `--dry-run` จะไม่บันทึกการเปลี่ยนแปลง เพียงแสดงสิ่งที่จะทำ
- สิ่งที่ทำ: สำหรับแต่ละ `Technician` จะอ่าน `skills` (comma-separated), สร้าง `MasterItem` ใน category `technician_skill` หากยังไม่มี และเพิ่มความสัมพันธ์ไปยัง `skills_m` ของช่าง

API ที่เกี่ยวข้อง
- Select2 skills endpoint ( AJAX )
  - URL name: `api_select2_skills`
  - Path: `/api/select2/skills/` (ดู `urls.py`)
  - Parameters: `?q=term` - คืนค่า `{ results: [{id: <masteritem id>, text: <label>}, ...] }`
  - Note: The Select2 endpoint will return MasterItem entries from category `equipments` for the technician skills chooser.

- Technicians by date API
  - URL name: `api_technicians_by_date`
  - Path: `/api/technicians/` (ดู `urls.py`)
  - Parameters: `?date=YYYY-MM-DD&skill=<id|label>`
  - Behavior: จะค้นหาโดย `skills_m` (id หรือ label) เป็นหลัก และจะ fallback ไปหา legacy `skills` text หากไม่พบผลผ่าน M2M

คำแนะนำการทดสอบ
1. รันเทสต์ที่มีอยู่:

```bash
python manage.py test cmms.tests.test_select2_skills
python manage.py test cmms.tests.test_capacity
python manage.py test cmms.tests.test_migrate_skills
```

2. รันคำสั่งย้ายข้อมูลแบบ dry-run เพื่อตรวจสอบผลก่อนบันทึก:

```bash
python manage.py migrate_skills_to_master --dry-run
```

3. เมื่อพอใจแล้ว ให้รันโดยไม่ใส่ --dry-run เพื่อทำการย้ายข้อมูลจริง

Cleanup (optional)
- After confirming everything works, you can run the cleanup command to remove unused `technician_skill` MasterItems that are not referenced by any Technician and do not contain the migration marker:

```bash
python manage.py cleanup_technician_skill_masteritems --dry-run
``` 

If the dry-run looks good, re-run without `--dry-run` and confirm the prompt to delete.

Notes about jQuery and Select2 in restricted networks
- The technician form uses Select2 which depends on jQuery loaded from CDN. If your environment blocks external CDNs, either:
  - Allow `https://code.jquery.com` and `https://cdn.jsdelivr.net` in your network, or
  - Provide a local copy of jQuery at `/static/js/jquery-3.6.0.min.js` and a local copy of Select2 assets under `/static/` and update templates accordingly.


หมายเหตุ
- หลังจากย้ายข้อมูลครบและทดสอบแล้ว สามารถพิจารณาลบฟิลด์เก่า `skills` หรือทำให้เป็น read-only ใน UI ได้ตามต้องการ
- หากองค์กรต้องการให้ป้าย label ของ MasterItem แตกต่างจาก text ของ legacy skills คุณอาจต้องทำ mapping แบบแมนนวลก่อนรันคำสั่ง
