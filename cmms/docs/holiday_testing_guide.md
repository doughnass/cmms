# Quick Test Guide - Holiday API

## 🚀 Quick Start

### 1. Start Server
```bash
cd d:\Python\CMMS\cmms_project
python manage.py runserver
```

### 2. Open in Browser
```
http://localhost:8000/admin/cmms/holiday/
```

## ✅ Test Checklist

### Backend Tests (via Admin)

- [ ] **Add Holiday**
  1. Go to Admin → Holidays → Add Holiday
  2. Enter: Date, Name, Description
  3. Click Save
  4. Verify appears in list

- [ ] **Edit Holiday**
  1. Click on existing holiday
  2. Modify name or description
  3. Click Save
  4. Verify changes saved

- [ ] **Delete Holiday**
  1. Select holiday checkbox
  2. Choose "Delete selected" action
  3. Confirm deletion
  4. Verify removed from list

- [ ] **Duplicate Date Prevention**
  1. Try adding holiday with existing date
  2. Should show error: "Holiday with this Date already exists"

### Frontend Tests (via UI)

- [ ] **Open Holiday Modal**
  1. Navigate to technician availability page
  2. Click "จัดการวันหยุดราชการ" button
  3. Modal should open with current year selected

- [ ] **Add Holiday via UI**
  1. Fill in: Date (picker), Name (text), Description (textarea)
  2. Click "เพิ่ม" button
  3. Success message should appear
  4. New holiday should appear in list below
  5. Year/month filters should update if needed

- [ ] **Filter by Year**
  1. Select different year from dropdown
  2. List should update to show only that year's holidays
  3. Buddhist year (พ.ศ.) should be displayed

- [ ] **Filter by Month**
  1. Select month from dropdown
  2. List should show only holidays in that month
  3. Month header should show in Thai

- [ ] **Search Holidays**
  1. Type in search box (e.g., "สงกรานต์")
  2. List should filter in real-time
  3. Searches both name and description

- [ ] **Edit Holiday via UI**
  1. Click "แก้" button next to a holiday
  2. Edit modal should open with current values
  3. Change date, name, or description
  4. Click "บันทึก"
  5. Success message appears
  6. Changes reflected in list immediately

- [ ] **Delete Holiday via UI**
  1. Click "ลบ" button next to a holiday
  2. Confirmation dialog appears
  3. Click OK
  4. Success message appears
  5. Holiday removed from list

- [ ] **Close Modal**
  1. Click "บันทึก" button at bottom
  2. Modal closes
  3. Success message appears

### API Tests (via Browser DevTools)

#### Open Browser Console (F12 → Console Tab)

- [ ] **Test GET /api/holidays/**
```javascript
fetch('/api/holidays/')
  .then(r => r.json())
  .then(d => console.log(d));
// Should show: { success: true, data: [...] }
```

- [ ] **Test GET with Year Filter**
```javascript
fetch('/api/holidays/?year=2024')
  .then(r => r.json())
  .then(d => console.log(d));
// Should show only 2024 holidays
```

- [ ] **Test POST /api/holidays/create/**
```javascript
fetch('/api/holidays/create/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
  },
  body: JSON.stringify({
    date: '2024-12-25',
    name: 'Christmas',
    description: 'Test holiday'
  })
})
.then(r => r.json())
.then(d => console.log(d));
// Should show: { success: true, message: "...", data: {...} }
```

- [ ] **Test PUT /api/holidays/<id>/update/**
```javascript
fetch('/api/holidays/1/update/', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
  },
  body: JSON.stringify({
    date: '2024-12-25',
    name: 'Christmas (Updated)',
    description: 'Updated description'
  })
})
.then(r => r.json())
.then(d => console.log(d));
// Should show success message
```

- [ ] **Test DELETE /api/holidays/<id>/delete/**
```javascript
fetch('/api/holidays/1/delete/', {
  method: 'DELETE',
  headers: {
    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
  }
})
.then(r => r.json())
.then(d => console.log(d));
// Should show: { success: true, message: "..." }
```

- [ ] **Test GET /api/holidays/check/?date=...**
```javascript
fetch('/api/holidays/check/?date=2024-12-31')
  .then(r => r.json())
  .then(d => console.log(d));
// Should show: { is_holiday: true/false, holiday: {...} }
```

## 🐛 Troubleshooting

### Modal doesn't open
```javascript
// Check if Bootstrap is loaded
typeof bootstrap
// Should return "object"

// Check if modal element exists
document.getElementById('holidayModal')
// Should return element, not null
```

### CSRF token errors
```javascript
// Check CSRF token
document.querySelector('[name=csrfmiddlewaretoken]').value
// Should return a long token string

// Or check cookie
document.cookie.includes('csrftoken')
// Should return true
```

### API returns 403 Forbidden
1. Check you're logged in
2. Verify CSRF token is being sent
3. Check Django logs for details

### Changes don't save
1. Open DevTools → Network tab
2. Perform action (add/edit/delete)
3. Check request/response
4. Look for error status codes (400, 403, 500)

### No holidays appear in list
```javascript
// Check if loadHolidays() was called
loadHolidays();

// Check holidays array
console.log(holidays);
// Should show array of holiday objects
```

## 📊 Sample Test Data

Use this data for quick testing:

```javascript
// Run in browser console after opening holiday modal
const testHolidays = [
  { date: '2024-01-01', name: 'วันขึ้นปีใหม่', description: 'New Year' },
  { date: '2024-02-14', name: 'วันวาเลนไทน์', description: 'Valentine Day' },
  { date: '2024-04-13', name: 'วันสงกรานต์', description: 'Songkran Festival' },
  { date: '2024-12-31', name: 'วันสิ้นปี', description: 'New Year Eve' }
];

// Add each holiday
for (const h of testHolidays) {
  await fetch('/api/holidays/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify(h)
  });
}

// Reload holidays
await loadHolidays();
```

## ✨ Expected Behavior

### Success Messages
- Add: "เพิ่มวันหยุดเรียบร้อยแล้ว" (green notification, auto-dismiss after 3s)
- Edit: "แก้ไขวันหยุดเรียบร้อยแล้ว" (green notification)
- Delete: "ลบวันหยุดเรียบร้อยแล้ว" (green notification)
- Close: "ปิดหน้าต่างวันหยุดเรียบร้อยแล้ว" (green notification)

### Error Messages
- Duplicate date: Alert dialog with message from backend
- Missing fields: "กรุณากรอกวันที่และชื่อวันหยุด"
- Network error: "เกิดข้อผิดพลาดในการเชื่อมต่อกับเซิร์ฟเวอร์"

### List Display
- Grouped by month with Thai month names
- 1 row per holiday
- Date shown in box on left (DD format)
- Name and description in center
- Edit/Delete buttons on right
- Buddhist year in headers (2024 → 2567)

## 📝 Test Report Template

After testing, fill this out:

```
Date: _______________
Tester: _______________

Backend Tests:
[ ] Add: PASS / FAIL - Notes: _______________
[ ] Edit: PASS / FAIL - Notes: _______________
[ ] Delete: PASS / FAIL - Notes: _______________
[ ] Duplicate prevention: PASS / FAIL - Notes: _______________

Frontend Tests:
[ ] Modal open: PASS / FAIL - Notes: _______________
[ ] Add UI: PASS / FAIL - Notes: _______________
[ ] Filter year: PASS / FAIL - Notes: _______________
[ ] Filter month: PASS / FAIL - Notes: _______________
[ ] Search: PASS / FAIL - Notes: _______________
[ ] Edit UI: PASS / FAIL - Notes: _______________
[ ] Delete UI: PASS / FAIL - Notes: _______________
[ ] Close: PASS / FAIL - Notes: _______________

API Tests:
[ ] GET list: PASS / FAIL - Notes: _______________
[ ] POST create: PASS / FAIL - Notes: _______________
[ ] PUT update: PASS / FAIL - Notes: _______________
[ ] DELETE: PASS / FAIL - Notes: _______________
[ ] GET check: PASS / FAIL - Notes: _______________

Overall Status: PASS / FAIL
Issues Found: _______________________________________________
```

---

**Ready to test? Start with Backend Tests using Django Admin!**
