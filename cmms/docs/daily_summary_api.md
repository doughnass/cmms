# Daily Summary API Documentation

## Overview
The Daily Summary API provides aggregated statistics for technician work activities on a specific date, matching the calculation logic used in `technician_availability_report.html`.

## Endpoint
```
GET /api/maintenance/daily-summary/?date=YYYY-MM-DD
```

## Parameters
- `date` (required): Target date in ISO format (YYYY-MM-DD)

## Response Format
Returns a JSON object with the following fields:

```json
{
  "date": "2025-12-03",
  "totalTechnicians": 10,
  "totalRecords": 8,
  
  "totalWork": 5,
  "totalWorkHours": 35,
  
  "totalOT": 2,
  "totalOTHours": 8,
  "totalOTWeekday": 1,
  "totalOTHoliday": 1,
  "totalOTWeekdayHours": 4,
  "totalOTHolidayHours": 4,
  
  "totalLeave": 1,
  "totalLeaveSick": 0,
  "totalLeavePersonal": 1,
  "totalLeaveAnnual": 0,
  "totalLeaveOther": 0,
  
  "totalHoliday": 0,
  
  "totalShift": 2,
  "totalShiftMorning": 1,
  "totalShiftAfternoon": 1,
  "totalShiftHours": 24,
  "totalShiftMorningHours": 8,
  "totalShiftAfternoonHours": 16
}
```

## Field Descriptions

### General
- `date`: The requested date
- `totalTechnicians`: Total number of active technicians in the system
- `totalRecords`: Number of TechnicianAvailability records for this date

### Work Statistics
- `totalWork`: Number of technicians who worked normally (7 hours each)
- `totalWorkHours`: Total regular work hours (totalWork × 7)

### Overtime Statistics
- `totalOT`: Total OT records (weekday + holiday)
- `totalOTHours`: Total OT hours
- `totalOTWeekday`: OT records on weekdays
- `totalOTHoliday`: OT records on holidays/weekends
- `totalOTWeekdayHours`: OT hours on weekdays
- `totalOTHolidayHours`: OT hours on holidays/weekends

### Leave Statistics
- `totalLeave`: Total leave records
- `totalLeaveSick`: Sick leave count
- `totalLeavePersonal`: Personal leave count
- `totalLeaveAnnual`: Annual/vacation leave count
- `totalLeaveOther`: Other types of leave

### Holiday & Shift Statistics
- `totalHoliday`: Official holidays recorded
- `totalShift`: Total shift assignments
- `totalShiftMorning`: Morning shifts (8 hours each)
- `totalShiftAfternoon`: Afternoon shifts (16 hours each)
- `totalShiftHours`: Total shift hours
- `totalShiftMorningHours`: Total morning shift hours
- `totalShiftAfternoonHours`: Total afternoon shift hours

## Calculation Logic
The API uses the same classification logic as `technician_availability_report.html`:

1. **Status Classification**: Analyzes `TechnicianAvailability.status` and `note` fields using keywords:
   - `holiday`: Contains "off_", "holiday", "วันหยุด", "หยุดราชการ", etc.
   - `leave`: Contains "leave", "ลา", "ลากิจ", "ป่วย", "sick", "personal", "vacation", etc.
   - `work`: Default category for active work records

2. **OT Detection**: Extracts overtime hours from note/status using patterns:
   - Explicit: `ot:4`, `ot_4`, `overtime:4`
   - With units: `4h`, `4 ชม.`, `4 hours`
   - Default: 4 hours if "ot" keyword present without number

3. **OT Type**: Distinguishes weekday vs. holiday OT based on:
   - Explicit markers: `ot_holiday`, `ot_weekday`
   - Date analysis: Weekends (Sat/Sun) counted as holiday OT
   - Holiday set (if available)

4. **Shift Hours**:
   - Morning shift: 8 hours
   - Afternoon shift: 16 hours

## Integration with daily_capacity.html

The daily capacity page uses this API to:
1. Display summary cards in the detail panel when a date is selected
2. Store daily summary data alongside technician data for each calendar day
3. Provide consistent metrics that match the availability report

## Example Usage

### JavaScript Fetch
```javascript
async function loadDailySummary(date) {
  const dateStr = date.toISOString().split('T')[0];
  const response = await fetch(`/api/maintenance/daily-summary/?date=${dateStr}`);
  const data = await response.json();
  return data;
}

// Usage
const summary = await loadDailySummary(new Date('2025-12-03'));
console.log(`Total working: ${summary.totalWork} people`);
console.log(`Total OT: ${summary.totalOT} people (${summary.totalOTHours} hours)`);
```

### cURL
```bash
curl "http://127.0.0.1:8000/api/maintenance/daily-summary/?date=2025-12-03"
```

## Testing

To verify the API returns correct values:

1. Open the technician availability report for a specific month:
   ```
   http://127.0.0.1:8000/maintenance/technicians/availability/report/?month=12&year=2025
   ```

2. Note the statistics shown for a specific date in the report

3. Call the daily summary API for that same date:
   ```
   http://127.0.0.1:8000/api/maintenance/daily-summary/?date=2025-12-03
   ```

4. Compare values - they should match exactly:
   - Report's `stats.totalWork` = API's `totalWork`
   - Report's `stats.totalOT` = API's `totalOT`
   - Report's `stats.totalLeave` = API's `totalLeave`
   - etc.

## Related Files
- API Implementation: `cmms/views.py` → `api_daily_summary()`
- URL Route: `cmms/urls.py` → `path("api/maintenance/daily-summary/")`
- Frontend Integration: `cmms/templates/maintenance/daily_capacity.html` → `loadDailySummary()`
- Report Logic: `cmms/templates/maintenance/technician_availability_report.html` (JavaScript section)
