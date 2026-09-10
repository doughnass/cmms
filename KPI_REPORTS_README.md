# 📊 KPI Reports System - ระบบรายงาน KPI

ระบบรายงานตัวชี้วัดความสำเร็จ (KPI) สำหรับระบบ CMMS

## 📁 ไฟล์ที่สร้าง

```
cmms/
├── templates/reports/
│   ├── kpi_dashboard.html       # แดชบอร์ด KPI แบบ Interactive
│   ├── kpi_report_print.html    # รายงาน KPI แบบพิมพ์ได้
│   └── kpi_comparison.html      # เปรียบเทียบ KPI
├── views_reports.py             # Views สำหรับรายงาน
├── urls_reports.py              # URL configuration
└── docs/
    └── kpi_reports_guide.md     # เอกสารคำแนะนำฉบับเต็ม
```

## 🎯 ฟีเจอร์หลัก

### 1. 📈 KPI Dashboard (แดชบอร์ดแบบ Interactive)
- **KPI Cards**: แสดง 8 ตัวชี้วัดหลัก
  - อัตราการดำเนินการเสร็จสิ้น (Work Order Completion Rate)
  - เวลาเฉลี่ยในการซ่อม (MTTR)
  - เวลาการใช้งานเครื่องมือ (Equipment Uptime)
  - การปฏิบัติตามแผน PM (PM Compliance)
  - เวลาตอบสนองเฉลี่ย (Response Time)
  - ค่าใช้จ่าย (Maintenance Cost)
  - งานค้างทำ (Backlog)
  - อัตราซ่อมสำเร็จครั้งแรก (First Time Fix Rate)

- **Charts**: กราฟแบบต่างๆ พร้อม Chart.js
  - แนวโน้มการดำเนินงาน (Line Chart)
  - สถานะเครื่องมือ (Doughnut Chart)
  - ประเภทการบำรุงรักษา (Bar Chart)
  - เวลาตอบสนองรายสัปดาห์ (Line Chart)

- **Features**:
  - ตัวกรองช่วงเวลา (วัน, สัปดาห์, เดือน, ไตรมาส, ปี)
  - Trend Indicators (แสดงแนวโน้มเพิ่ม/ลด)
  - ตาราง Top 10 เครื่องมือที่มีประสิทธิภาพสูง
  - Responsive Design

### 2. 🖨️ KPI Print Report (รายงานแบบพิมพ์)
- รูปแบบเอกสารมาตรฐาน
- สรุปผลการดำเนินงาน
- การวิเคราะห์จุดแข็ง/จุดอ่อน
- ข้อเสนอแนะและแผนปรับปรุง
- ส่วนลงนาม
- Print-friendly CSS

### 3. 🔄 KPI Comparison (เปรียบเทียบ KPI)
- เปรียบเทียบระหว่าง 2 ช่วงเวลา
- แสดงค่าเปลี่ยนแปลงและเปอร์เซ็นต์
- Charts เปรียบเทียบ (Line, Radar)
- การวิเคราะห์ข้อมูลเชิงลึก

## ⚙️ การติดตั้ง

### ขั้นตอนที่ 1: เพิ่ม URL Routes

เปิดไฟล์ `cmms/urls.py` และเพิ่ม:

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    
    # KPI Reports
    path('reports/', include('cmms.urls_reports')),
]
```

หรือเพิ่มโดยตรง:

```python
from .views_reports import kpi_dashboard, kpi_report_print, kpi_comparison, api_kpi_data

urlpatterns = [
    # ... existing patterns ...
    
    path('reports/kpi-dashboard/', kpi_dashboard, name='kpi_dashboard'),
    path('reports/kpi-print/', kpi_report_print, name='kpi_report_print'),
    path('reports/kpi-comparison/', kpi_comparison, name='kpi_comparison'),
    path('api/kpi-data/', api_kpi_data, name='api_kpi_data'),
]
```

### ขั้นตอนที่ 2: ปรับแต่ง Models (ถ้าจำเป็น)

ตรวจสอบและปรับแต่งใน `views_reports.py` ให้ตรงกับ Models ของคุณ:

```python
# ตรวจสอบชื่อ fields ใน WorkOrder model
work_orders = WorkOrder.objects.filter(status='COMPLETED')  # ปรับ 'COMPLETED' ตามระบบคุณ

# ตรวจสอบชื่อ fields ใน Equipment model
equipment = Equipment.objects.filter(status='ACTIVE')  # ปรับ 'ACTIVE' ตามระบบคุณ
```

### ขั้นตอนที่ 3: เพิ่มเมนู Navigation (Optional)

เพิ่มในไฟล์ `base.html` หรือ navigation template:

```html
<li class="nav-item dropdown">
  <a class="nav-link dropdown-toggle" href="#" role="button" 
     data-bs-toggle="dropdown">
    <i class="bi bi-graph-up"></i> รายงาน
  </a>
  <ul class="dropdown-menu">
    <li>
      <a class="dropdown-item" href="{% url 'kpi_dashboard' %}">
        <i class="bi bi-speedometer2"></i> Dashboard KPI
      </a>
    </li>
    <li>
      <a class="dropdown-item" href="{% url 'kpi_comparison' %}">
        <i class="bi bi-arrow-left-right"></i> เปรียบเทียบ KPI
      </a>
    </li>
    <li><hr class="dropdown-divider"></li>
    <li>
      <a class="dropdown-item" href="{% url 'kpi_report_print' %}" target="_blank">
        <i class="bi bi-printer"></i> พิมพ์รายงาน
      </a>
    </li>
  </ul>
</li>
```

## 🚀 การใช้งาน

### เข้าถึงรายงาน

1. **KPI Dashboard**:
   ```
   http://localhost:8000/reports/kpi-dashboard/
   http://localhost:8000/reports/kpi-dashboard/?period=month
   ```

2. **KPI Print Report**:
   ```
   http://localhost:8000/reports/kpi-print/
   ```

3. **KPI Comparison**:
   ```
   http://localhost:8000/reports/kpi-comparison/
   http://localhost:8000/reports/kpi-comparison/?current=this-month&previous=last-month
   ```

### Parameters

**period** (สำหรับ Dashboard และ Print):
- `today` - วันนี้
- `week` - สัปดาห์นี้
- `month` - เดือนนี้ (default)
- `quarter` - ไตรมาสนี้
- `year` - ปีนี้

**current/previous** (สำหรับ Comparison):
- `this-month` / `last-month`
- `this-quarter` / `last-quarter`
- `this-year` / `last-year`

## 🎨 การปรับแต่ง

### เปลี่ยนสีธีม

แก้ไขใน CSS variables:

```css
:root {
  --kpi-primary: #667eea;      /* สีหลัก */
  --kpi-primary-dark: #764ba2;  /* สีหลักเข้ม */
  --kpi-success: #10b981;       /* สีสำเร็จ */
  --kpi-warning: #f59e0b;       /* สีเตือน */
  --kpi-danger: #ef4444;        /* สีอันตราย */
}
```

### เพิ่ม KPI ใหม่

1. เพิ่มการคำนวณใน `views_reports.py`:

```python
def calculate_kpis(start_date, end_date):
    # ... existing code ...
    
    # เพิ่ม KPI ใหม่
    custom_kpi = calculate_custom_kpi()
    
    return {
        # ... existing KPIs ...
        'custom_kpi': custom_kpi,
    }
```

2. เพิ่ม Card ใน template:

```html
<div class="kpi-card info">
  <div class="kpi-icon">
    <i class="bi bi-ICON"></i>
  </div>
  <div class="kpi-label">ชื่อ KPI</div>
  <div class="kpi-value">{{ custom_kpi }}</div>
</div>
```

## 📊 ตัวชี้วัด KPI ที่รองรับ

| KPI | เป้าหมาย | การคำนวณ |
|-----|---------|----------|
| Work Order Completion Rate | ≥ 90% | (งานเสร็จ / งานทั้งหมด) × 100 |
| MTTR | ≤ 4 ชม. | ผลรวมเวลาซ่อม / จำนวนงาน |
| Equipment Uptime | ≥ 95% | (เวลาใช้งานได้ / เวลาทั้งหมด) × 100 |
| PM Compliance | ≥ 95% | (PM ทำตามกำหนด / PM ทั้งหมด) × 100 |
| Response Time | ≤ 2 ชม. | เวลาเฉลี่ยจากแจ้งถึงเริ่มงาน |
| First Time Fix Rate | ≥ 85% | (ซ่อมสำเร็จครั้งแรก / งานทั้งหมด) × 100 |

## 🔧 การแก้ไขปัญหา

### Charts ไม่แสดงผล
- ตรวจสอบว่า Chart.js โหลดสำเร็จ
- ตรวจสอบ Console เช็ค JavaScript errors
- ตรวจสอบว่า canvas elements มี id ที่ถูกต้อง

### ข้อมูลไม่ถูกต้อง
- ตรวจสอบ field names ใน `views_reports.py`
- ตรวจสอบว่า status values ตรงกับ model
- ตรวจสอบ date filtering

### Print Layout ไม่ถูกต้อง
- ใช้ Chrome/Edge Print to PDF
- ตรวจสอบ `@media print` CSS rules
- ปรับ page margins ใน browser print settings

## 📝 TODO / แนวทางพัฒนาต่อ

- [ ] เพิ่มการส่งออกเป็น PDF อัตโนมัติ
- [ ] เพิ่มการส่งรายงานทาง Email
- [ ] เพิ่ม Real-time updates ด้วย WebSocket
- [ ] เพิ่มการตั้งค่าเป้าหมาย KPI แบบ custom
- [ ] เพิ่ม Drill-down สำหรับดูรายละเอียดแต่ละ KPI
- [ ] เพิ่มการ Export ข้อมูลเป็น Excel
- [ ] เพิ่ม Permission-based access control

## 📚 เอกสารเพิ่มเติม

อ่านเอกสารฉบับเต็มได้ที่: [`cmms/docs/kpi_reports_guide.md`](docs/kpi_reports_guide.md)

## 💡 ตัวอย่างการใช้งาน

### AJAX Update

```javascript
// โหลด KPI แบบ dynamic
fetch('/api/kpi-data/?period=month')
  .then(response => response.json())
  .then(data => {
    console.log('Completion Rate:', data.completion_rate);
    console.log('MTTR:', data.mttr_hours);
  });
```

### Template Tags

```django
{% load static %}

<!-- Link to dashboard -->
<a href="{% url 'kpi_dashboard' %}">View KPI Dashboard</a>

<!-- Link with period parameter -->
<a href="{% url 'kpi_dashboard' %}?period=quarter">Q2 2026 KPI</a>
```

## 🎯 Best Practices

1. **Performance**: ใช้ cache สำหรับข้อมูลที่คำนวณบ่อย
2. **Security**: ใช้ `@login_required` และ permission checks
3. **Data Accuracy**: Validate date ranges และ null values
4. **User Experience**: แสดง loading indicators ระหว่างคำนวณ
5. **Mobile**: ทดสอบบน mobile devices

## 📧 ติดต่อ

หากมีคำถามหรือต้องการความช่วยเหลือ:
- เปิด Issue ใน repository
- ติดต่อทีมพัฒนาระบบ CMMS

---

**Version**: 1.0.0  
**Last Updated**: June 23, 2026  
**Author**: CMMS Development Team
