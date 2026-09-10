# KPI Reports Documentation

## ภาพรวม

ระบบรายงาน KPI (Key Performance Indicators) สำหรับระบบ CMMS ประกอบด้วยหน้ารายงาน 3 แบบ:

### 1. KPI Dashboard (`kpi_dashboard.html`)
- **จุดประสงค์**: แดชบอร์ดแบบ Interactive สำหรับติดตามตัวชี้วัดแบบ Real-time
- **ฟีเจอร์**:
  - KPI Cards แสดงตัวเลขสำคัญพร้อม Trend Indicators
  - Charts แบบต่างๆ (Line, Doughnut, Bar) ด้วย Chart.js
  - ตัวกรองช่วงเวลา (วันนี้, สัปดาห์, เดือน, ไตรมาส, ปี)
  - ตาราง Top 10 เครื่องมือที่มีประสิทธิภาพสูงสุด
  - ปุ่มส่งออกรายงาน
- **เหมาะสำหรับ**: ผู้บริหาร, หัวหน้างานบำรุงรักษา

### 2. KPI Report Print (`kpi_report_print.html`)
- **จุดประสงค์**: รายงานแบบเอกสารสำหรับการพิมพ์และนำเสนอ
- **ฟีเจอร์**:
  - Header พร้อมโลโก้องค์กร
  - สรุปผลการดำเนินงาน (Executive Summary)
  - ตารางรายละเอียด KPI ทั้งหมด
  - การวิเคราะห์จุดแข็ง/จุดอ่อน
  - ข้อเสนอแนะและแผนปรับปรุง
  - ส่วนลงนาม (Signature Section)
  - Print-friendly CSS (@media print)
- **เหมาะสำหรับ**: การประชุม, การนำเสนอ, เก็บเข้าแฟ้มเอกสาร

### 3. KPI Comparison (`kpi_comparison.html`)
- **จุดประสงค์**: เปรียบเทียบ KPI ระหว่างช่วงเวลาต่างๆ
- **ฟีเจอร์**:
  - เลือกช่วงเวลาเปรียบเทียบแบบยืดหยุ่น
  - Comparison Cards แสดงค่าเปลี่ยนแปลง
  - Charts เปรียบเทียบ (Line, Radar)
  - ตารางเปรียบเทียบโดยละเอียด
  - การวิเคราะห์ข้อมูลเชิงลึก (Insights)
- **เหมาะสำหรับ**: การวิเคราะห์แนวโน้ม, การปรับปรุงประสิทธิภาพ

---

## ตัวชี้วัด KPI ที่ใช้

### 1. Work Order Completion Rate (อัตราการดำเนินการเสร็จสิ้น)
- **สูตร**: (จำนวนงานที่เสร็จสิ้น / จำนวนงานทั้งหมด) × 100
- **เป้าหมาย**: ≥ 90%
- **ความหมาย**: วัดประสิทธิภาพการทำงานให้เสร็จตามกำหนด

### 2. Mean Time To Repair - MTTR (เวลาเฉลี่ยในการซ่อม)
- **สูตร**: ผลรวมเวลาซ่อมทั้งหมด / จำนวนงานซ่อม
- **เป้าหมาย**: ≤ 4 ชั่วโมง
- **ความหมาย**: วัดความรวดเร็วในการซ่อมแซม ยิ่งต่ำยิ่งดี

### 3. Equipment Uptime (เวลาการใช้งานเครื่องมือ)
- **สูตร**: (เวลาที่ใช้งานได้ / เวลาทั้งหมด) × 100
- **เป้าหมาย**: ≥ 95%
- **ความหมาย**: วัดความพร้อมใช้งานของเครื่องมือ

### 4. PM Compliance (การปฏิบัติตามแผน PM)
- **สูตร**: (จำนวน PM ที่ทำตามกำหนด / จำนวน PM ทั้งหมด) × 100
- **เป้าหมาย**: ≥ 95%
- **ความหมาย**: วัดความสม่ำเสมอในการบำรุงรักษาเชิงป้องกัน

### 5. Average Response Time (เวลาตอบสนองเฉลี่ย)
- **สูตร**: ผลรวมเวลาตอบสนองทั้งหมด / จำนวนงาน
- **เป้าหมาย**: ≤ 2 ชั่วโมง
- **ความหมาย**: วัดความรวดเร็วในการเริ่มดำเนินการหลังได้รับแจ้ง

### 6. Maintenance Cost (ค่าใช้จ่ายการบำรุงรักษา)
- **สูตร**: ผลรวมค่าใช้จ่ายทั้งหมด (แรงงาน + อะไหล่)
- **เป้าหมาย**: ไม่เกินงบประมาณที่กำหนด
- **ความหมาย**: วัดประสิทธิภาพการควบคุมต้นทุน

### 7. Work Order Backlog (งานค้างทำ)
- **สูตร**: จำนวนงานที่ยังไม่เสร็จ
- **เป้าหมาย**: ≤ 15 งาน
- **ความหมาย**: วัดภาระงานค้างที่ต้องจัดการ

### 8. First Time Fix Rate (อัตราซ่อมสำเร็จครั้งแรก)
- **สูตร**: (จำนวนงานที่ซ่อมสำเร็จครั้งแรก / จำนวนงานทั้งหมด) × 100
- **เป้าหมาย**: ≥ 85%
- **ความหมาย**: วัดคุณภาพการซ่อม

---

## การติดตั้งและใช้งาน

### 1. ไฟล์ที่ต้องมี

```
cmms/templates/reports/
├── kpi_dashboard.html
├── kpi_report_print.html
└── kpi_comparison.html
```

### 2. Dependencies

ระบบใช้ไลบรารีต่อไปนี้ (โหลดจาก CDN):
- **Bootstrap 5.3.0**: UI Framework
- **Bootstrap Icons**: Icon Set
- **Chart.js 4.4.0**: สำหรับสร้าง Charts
- **Google Fonts (Google Sans)**: Typography

### 3. เพิ่ม URL Routes

เพิ่มใน `cmms/urls.py`:

```python
from django.urls import path
from . import views_reports

urlpatterns = [
    # ... existing patterns ...
    
    # KPI Reports
    path('reports/kpi-dashboard/', views_reports.kpi_dashboard, name='kpi_dashboard'),
    path('reports/kpi-print/', views_reports.kpi_report_print, name='kpi_report_print'),
    path('reports/kpi-comparison/', views_reports.kpi_comparison, name='kpi_comparison'),
]
```

### 4. สร้าง Views

สร้างไฟล์ `cmms/views_reports.py`:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from .models import WorkOrder, Equipment

@login_required
def kpi_dashboard(request):
    """KPI Dashboard with interactive charts"""
    
    # Get period from request (default: current month)
    period = request.GET.get('period', 'month')
    
    # Calculate date range
    today = datetime.now().date()
    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start_date = today.replace(month=quarter*3 + 1, day=1)
        end_date = (start_date + timedelta(days=93)).replace(day=1) - timedelta(days=1)
    else:  # year
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    # Query WorkOrders
    work_orders = WorkOrder.objects.filter(
        created_at__range=[start_date, end_date]
    )
    
    # Calculate KPIs
    total_work_orders = work_orders.count()
    completed_work_orders = work_orders.filter(status='completed').count()
    completion_rate = (completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0
    
    # Calculate MTTR (Mean Time To Repair)
    completed_orders = work_orders.filter(status='completed')
    mttr_hours = 0
    if completed_orders.exists():
        total_repair_time = sum([
            (wo.completed_at - wo.started_at).total_seconds() / 3600 
            for wo in completed_orders 
            if wo.completed_at and wo.started_at
        ])
        mttr_hours = total_repair_time / completed_orders.count() if completed_orders.count() > 0 else 0
    
    # Calculate Equipment Uptime
    equipment_list = Equipment.objects.all()
    total_uptime = 0
    if equipment_list.exists():
        for eq in equipment_list:
            # Calculate uptime percentage for each equipment
            # This is a simplified example - adjust based on your data model
            uptime = eq.calculate_uptime(start_date, end_date)
            total_uptime += uptime
        avg_uptime = total_uptime / equipment_list.count()
    else:
        avg_uptime = 0
    
    # PM Compliance
    pm_work_orders = work_orders.filter(work_order_type='preventive')
    pm_total = pm_work_orders.count()
    pm_completed = pm_work_orders.filter(status='completed').count()
    pm_compliance = (pm_completed / pm_total * 100) if pm_total > 0 else 0
    
    # Response Time
    response_times = [
        (wo.started_at - wo.created_at).total_seconds() / 3600 
        for wo in work_orders 
        if wo.started_at and wo.created_at
    ]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Backlog
    backlog_count = WorkOrder.objects.filter(
        status__in=['pending', 'in_progress']
    ).count()
    
    # Top Equipment
    top_equipment = Equipment.objects.annotate(
        uptime_score=Count('workorder', filter=Q(workorder__status='completed'))
    ).order_by('-uptime_score')[:10]
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'completion_rate': round(completion_rate, 1),
        'mttr_hours': round(mttr_hours, 1),
        'avg_uptime': round(avg_uptime, 1),
        'pm_compliance': round(pm_compliance, 1),
        'avg_response_time': round(avg_response_time, 1),
        'backlog_count': backlog_count,
        'total_work_orders': total_work_orders,
        'completed_work_orders': completed_work_orders,
        'top_equipment': top_equipment,
    }
    
    return render(request, 'reports/kpi_dashboard.html', context)


@login_required
def kpi_report_print(request):
    """Print-friendly KPI report"""
    
    # Similar calculation as kpi_dashboard
    # Add additional context for print version
    
    context = {
        # ... KPI data ...
    }
    
    return render(request, 'reports/kpi_report_print.html', context)


@login_required
def kpi_comparison(request):
    """KPI comparison between periods"""
    
    current_period = request.GET.get('current', 'this-month')
    previous_period = request.GET.get('previous', 'last-month')
    
    # Calculate KPIs for both periods
    # Compare and calculate differences
    
    context = {
        'current_period': current_period,
        'previous_period': previous_period,
        # ... comparison data ...
    }
    
    return render(request, 'reports/kpi_comparison.html', context)
```

---

## การปรับแต่ง (Customization)

### เปลี่ยนสีธีม

แก้ไขใน CSS variables ของแต่ละไฟล์:

```css
:root {
  --kpi-primary: #667eea;      /* สีหลัก */
  --kpi-primary-dark: #764ba2;  /* สีหลักเข้ม */
  --kpi-success: #10b981;       /* สีสำเร็จ */
  --kpi-warning: #f59e0b;       /* สีเตือน */
  --kpi-danger: #ef4444;        /* สีอันตราย */
  --kpi-info: #3b82f6;          /* สีข้อมูล */
}
```

### เพิ่มตัวชี้วัด KPI ใหม่

1. เพิ่ม KPI Card ใน `kpi_dashboard.html`:

```html
<div class="kpi-card info">
  <div class="kpi-card-header">
    <div class="kpi-icon">
      <i class="bi bi-ICON-NAME"></i>
    </div>
    <span class="kpi-trend up">
      <i class="bi bi-arrow-up"></i>
      X%
    </span>
  </div>
  <div class="kpi-label">ชื่อตัวชี้วัด</div>
  <div class="kpi-value">{{ value }}</div>
  <div class="kpi-subtitle">รายละเอียดเพิ่มเติม</div>
</div>
```

2. เพิ่มการคำนวณใน views:

```python
# Calculate new KPI
new_kpi_value = calculate_new_kpi()

context['new_kpi'] = new_kpi_value
```

### เพิ่ม Chart ใหม่

1. เพิ่ม HTML canvas:

```html
<div class="chart-card">
  <h3><i class="bi bi-graph-up"></i> ชื่อ Chart</h3>
  <div class="chart-wrapper">
    <canvas id="newChartId"></canvas>
  </div>
</div>
```

2. เพิ่ม JavaScript:

```javascript
const newChartCtx = document.getElementById('newChartId').getContext('2d');
new Chart(newChartCtx, {
  type: 'bar', // line, bar, pie, doughnut, radar, etc.
  data: {
    labels: ['Label 1', 'Label 2'],
    datasets: [{
      label: 'Dataset',
      data: [10, 20],
      backgroundColor: chartColors.primary
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
});
```

---

## API Endpoints (ถ้าต้องการ)

สำหรับโหลดข้อมูล KPI แบบ AJAX:

```python
# cmms/views_reports.py

from django.http import JsonResponse

@login_required
def api_kpi_data(request):
    """API endpoint for KPI data"""
    period = request.GET.get('period', 'month')
    
    # Calculate KPIs
    data = {
        'completion_rate': 94.5,
        'mttr': 3.2,
        'uptime': 98.3,
        'pm_compliance': 87.2,
        # ... more KPIs
    }
    
    return JsonResponse(data)
```

URL:
```python
path('api/kpi-data/', views_reports.api_kpi_data, name='api_kpi_data'),
```

JavaScript:
```javascript
fetch('/api/kpi-data/?period=month')
  .then(response => response.json())
  .then(data => {
    // Update UI with data
    document.getElementById('completion-rate').textContent = data.completion_rate + '%';
  });
```

---

## การทดสอบ

### ข้อมูลทดสอบ (Mock Data)

สามารถใช้ข้อมูลตัวอย่างในไฟล์ HTML โดยตรง หรือสร้าง fixture:

```python
# Create test data
python manage.py shell

from cmms.models import WorkOrder, Equipment
from datetime import datetime, timedelta

# Create sample work orders
for i in range(100):
    WorkOrder.objects.create(
        title=f"Test WO {i}",
        status='completed' if i < 90 else 'pending',
        created_at=datetime.now() - timedelta(days=i),
        # ... other fields
    )
```

---

## FAQ

**Q: Charts ไม่แสดงผล?**  
A: ตรวจสอบว่า Chart.js โหลดสำเร็จ และ canvas elements มี id ที่ถูกต้อง

**Q: ต้องการเปลี่ยนเป้าหมาย KPI?**  
A: แก้ไขค่าใน HTML subtitle หรือเก็บไว้ใน database/settings

**Q: ต้องการส่งออกเป็น PDF?**  
A: ใช้ไลบรารี WeasyPrint หรือ ReportLab สำหรับ Django หรือใช้ browser print to PDF

**Q: ต้องการเพิ่มการแจ้งเตือนเมื่อ KPI ต่ำกว่าเป้าหมาย?**  
A: เพิ่ม logic ใน views เช่น:
```python
if pm_compliance < 90:
    messages.warning(request, "PM Compliance ต่ำกว่าเป้าหมาย!")
```

---

## สรุป

ระบบรายงาน KPI นี้ออกแบบมาเพื่อ:
- ✅ ติดตามประสิทธิภาพการทำงานแบบ Real-time
- ✅ วิเคราะห์แนวโน้มและเปรียบเทียบช่วงเวลา
- ✅ สร้างรายงานสำหรับการนำเสนอ
- ✅ ปรับแต่งและขยายได้ง่าย
- ✅ Responsive และ Mobile-friendly

สามารถปรับแต่งเพิ่มเติมตามความต้องการของแต่ละองค์กรได้
