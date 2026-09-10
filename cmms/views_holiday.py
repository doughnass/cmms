"""
Views for Holiday Management API
"""

import json
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Import workalendar for Thailand holidays
# Note: workalendar may not have Thailand calendar in all versions
# This is optional - the system works fine with JSON import
Thailand = None
try:
    # Try various possible import paths
    try:
        from workalendar.asia import Thailand
    except (ImportError, AttributeError):
        try:
            from workalendar.asia.thailand import Thailand
        except ImportError:
            pass
except Exception:
    pass

from .models import Holiday


@login_required
@require_http_methods(["GET"])
def holiday_list(request):
    """
    Get list of holidays with optional filters
    Query params:
    - year: Filter by year
    - month: Filter by month (1-12)
    - is_active: Filter by active status (true/false)
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Authentication required"}, status=401
        )

    holidays = Holiday.objects.filter(is_active=True)

    # Apply filters
    year = request.GET.get("year")
    if year:
        try:
            holidays = holidays.filter(date__year=int(year))
        except ValueError:
            pass

    month = request.GET.get("month")
    if month:
        try:
            holidays = holidays.filter(date__month=int(month))
        except ValueError:
            pass

    # Serialize data
    data = []
    for holiday in holidays:
        data.append(
            {
                "id": holiday.id,
                "date": holiday.date.isoformat(),
                "name": holiday.name,
                "description": holiday.description,
                "is_active": holiday.is_active,
                "created_at": (
                    holiday.created_at.isoformat() if holiday.created_at else None
                ),
                "year": holiday.year,
                "month": holiday.month,
            }
        )

    return JsonResponse({"success": True, "data": data, "count": len(data)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def holiday_create(request):
    """
    Create a new holiday
    Body params (JSON):
    - date: Date in YYYY-MM-DD format
    - name: Holiday name
    - description: Optional description
    """
    try:
        body = json.loads(request.body)

        # Validate required fields
        date_str = body.get("date")
        name = body.get("name", "").strip()

        if not date_str or not name:
            return JsonResponse(
                {"success": False, "error": "กรุณากรอกวันที่และชื่อวันหยุด"}, status=400
            )

        # Parse date
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "รูปแบบวันที่ไม่ถูกต้อง (ใช้ YYYY-MM-DD)"},
                status=400,
            )

        # Check duplicate
        if Holiday.objects.filter(date=date).exists():
            return JsonResponse(
                {"success": False, "error": "วันที่นี้มีอยู่ในรายการแล้ว"}, status=400
            )

        # Create holiday
        holiday = Holiday.objects.create(
            date=date,
            name=name,
            description=body.get("description", ""),
            created_by=request.user,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "เพิ่มวันหยุดเรียบร้อยแล้ว",
                "data": {
                    "id": holiday.id,
                    "date": holiday.date.isoformat(),
                    "name": holiday.name,
                    "description": holiday.description,
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def holiday_update(request, holiday_id):
    """
    Update an existing holiday
    Body params (JSON):
    - date: Date in YYYY-MM-DD format
    - name: Holiday name
    - description: Optional description
    """
    try:
        holiday = Holiday.objects.get(id=holiday_id)
    except Holiday.DoesNotExist:
        return JsonResponse({"success": False, "error": "ไม่พบวันหยุดนี้"}, status=404)

    try:
        body = json.loads(request.body)

        # Validate required fields
        date_str = body.get("date")
        name = body.get("name", "").strip()

        if not date_str or not name:
            return JsonResponse(
                {"success": False, "error": "กรุณากรอกวันที่และชื่อวันหยุด"}, status=400
            )

        # Parse date
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "รูปแบบวันที่ไม่ถูกต้อง (ใช้ YYYY-MM-DD)"},
                status=400,
            )

        # Check duplicate (excluding current holiday)
        if Holiday.objects.filter(date=date).exclude(id=holiday_id).exists():
            return JsonResponse(
                {"success": False, "error": "วันที่นี้มีอยู่ในรายการแล้ว"}, status=400
            )

        # Update holiday
        holiday.date = date
        holiday.name = name
        holiday.description = body.get("description", "")
        holiday.save()

        return JsonResponse(
            {
                "success": True,
                "message": "แก้ไขวันหยุดเรียบร้อยแล้ว",
                "data": {
                    "id": holiday.id,
                    "date": holiday.date.isoformat(),
                    "name": holiday.name,
                    "description": holiday.description,
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def holiday_delete(request, holiday_id):
    """
    Delete a holiday
    """
    try:
        holiday = Holiday.objects.get(id=holiday_id)
        holiday_name = holiday.name
        holiday.delete()

        return JsonResponse(
            {"success": True, "message": f'ลบวันหยุด "{holiday_name}" เรียบร้อยแล้ว'}
        )

    except Holiday.DoesNotExist:
        return JsonResponse({"success": False, "error": "ไม่พบวันหยุดนี้"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def holiday_check(request):
    """
    Check if a specific date is a holiday
    Query params:
    - date: Date in YYYY-MM-DD format
    """
    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"success": False, "error": "กรุณาระบุวันที่"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse(
            {"success": False, "error": "รูปแบบวันที่ไม่ถูกต้อง (ใช้ YYYY-MM-DD)"}, status=400
        )

    try:
        holiday = Holiday.objects.get(date=date, is_active=True)
        return JsonResponse(
            {
                "success": True,
                "is_holiday": True,
                "data": {
                    "id": holiday.id,
                    "name": holiday.name,
                    "description": holiday.description,
                },
            }
        )
    except Holiday.DoesNotExist:
        return JsonResponse({"success": True, "is_holiday": False, "data": None})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def holiday_import_government(request):
    """
    Import government holidays from Thai holidays data source
    Query params:
    - year: Year to import (e.g., 2024, 2025) - can specify multiple years separated by comma
    - overwrite: If true, update existing holidays (default: false)
    """
    try:
        # Get parameters
        years_param = request.POST.get("year", str(datetime.now().year))
        overwrite = request.POST.get("overwrite", "false").lower() == "true"

        # Parse years
        years = [int(y.strip()) for y in years_param.split(",")]

        # Load Thai holidays data
        data_path = os.path.join(
            settings.BASE_DIR, "cmms", "data", "thai_holidays.json"
        )

        if not os.path.exists(data_path):
            return JsonResponse(
                {"success": False, "error": "ไม่พบไฟล์ข้อมูลวันหยุดราชการ"}, status=404
            )

        with open(data_path, "r", encoding="utf-8") as f:
            holidays_data = json.load(f)

        # Statistics
        stats = {"total": 0, "added": 0, "updated": 0, "skipped": 0, "errors": []}

        # Process each year
        for year in years:
            year_str = str(year)

            if year_str not in holidays_data["years"]:
                stats["errors"].append(f"ไม่มีข้อมูลวันหยุดสำหรับปี {year}")
                continue

            year_holidays = holidays_data["years"][year_str]
            stats["total"] += len(year_holidays)

            for holiday_data in year_holidays:
                try:
                    date_obj = datetime.strptime(
                        holiday_data["date"], "%Y-%m-%d"
                    ).date()

                    # Check if holiday already exists
                    existing = Holiday.objects.filter(date=date_obj).first()

                    if existing:
                        if overwrite:
                            # Update existing holiday
                            existing.name = holiday_data["name"]
                            existing.description = holiday_data.get("description", "")
                            existing.is_active = True
                            existing.save()
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        # Create new holiday
                        Holiday.objects.create(
                            date=date_obj,
                            name=holiday_data["name"],
                            description=holiday_data.get("description", ""),
                            is_active=True,
                            created_by=request.user,
                        )
                        stats["added"] += 1

                except Exception as e:
                    stats["errors"].append(
                        f"วันที่ {holiday_data.get('date', 'unknown')}: {str(e)}"
                    )

        # Build response message
        message_parts = []
        if stats["added"] > 0:
            message_parts.append(f"เพิ่มใหม่ {stats['added']} วัน")
        if stats["updated"] > 0:
            message_parts.append(f"อัปเดต {stats['updated']} วัน")
        if stats["skipped"] > 0:
            message_parts.append(f"ข้าม {stats['skipped']} วัน (มีอยู่แล้ว)")

        if not message_parts:
            message = "ไม่มีการเปลี่ยนแปลง"
        else:
            message = "นำเข้าวันหยุดราชการเรียบร้อย: " + ", ".join(message_parts)

        return JsonResponse({"success": True, "message": message, "stats": stats})

    except ValueError as e:
        return JsonResponse(
            {"success": False, "error": f"รูปแบบปีไม่ถูกต้อง: {str(e)}"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500
        )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def holiday_sync_from_api(request):
    """
    Sync holidays from workalendar API and compare with local JSON file
    Returns comparison data showing new, updated, and unchanged holidays

    Body params (JSON):
    - years: Array of years to sync (e.g., [2025, 2026])
    - update_json: If true, update the local thai_holidays.json file (default: false)
    - import_to_db: If true, import changes to database (default: false)
    """
    try:
        # Check if Thailand calendar is available
        if Thailand is None:
            return JsonResponse(
                {
                    "success": False,
                    "error": "ฟีเจอร์ Sync from API ยังไม่พร้อมใช้งาน",
                    "message": "workalendar ไม่รองรับปฏิทินไทยในเวอร์ชันนี้",
                    "suggestion": 'กรุณาใช้ปุ่ม "รีเฟรช" หรือ "นำเข้าวันหยุดราชการ" แทน',
                    "alternative": {
                        "method1": 'ใช้ปุ่ม "รีเฟรชข้อมูลปีปัจจุบัน + ปีหน้า" - อัปเดตจากไฟล์ JSON',
                        "method2": 'ใช้ปุ่ม "นำเข้าวันหยุดราชการ" - เลือกปีที่ต้องการ',
                        "method3": "แก้ไขไฟล์ cmms/data/thai_holidays.json โดยตรง",
                    },
                },
                status=503,
            )

        # Parse request body
        body = json.loads(request.body)
        years = body.get("years", [datetime.now().year, datetime.now().year + 1])
        update_json = body.get("update_json", False)
        import_to_db = body.get("import_to_db", False)

        # Initialize Thailand calendar
        cal = Thailand()

        # Load existing JSON data
        data_path = os.path.join(
            settings.BASE_DIR, "cmms", "data", "thai_holidays.json"
        )

        existing_data = {"years": {}}
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

        # Prepare comparison results
        comparison = {"new": [], "updated": [], "unchanged": [], "removed": []}

        # New data structure
        new_data = {
            "source": "workalendar - Thailand Calendar",
            "last_updated": datetime.now().isoformat(),
            "years": {},
        }

        # Sync each year
        for year in years:
            # Get holidays from workalendar
            api_holidays = cal.holidays(year)

            # Convert to our format
            year_holidays = []
            for holiday_date, holiday_name in api_holidays:
                holiday_dict = {
                    "date": holiday_date.isoformat(),
                    "name": holiday_name,
                    "name_en": holiday_name,  # workalendar returns English names
                    "description": f"วันหยุดราชการไทย - {holiday_name}",
                    "type": "government",
                }
                year_holidays.append(holiday_dict)

            new_data["years"][str(year)] = year_holidays

            # Compare with existing data
            existing_year_data = existing_data.get("years", {}).get(str(year), [])
            existing_dates = {h["date"]: h for h in existing_year_data}
            new_dates = {h["date"]: h for h in year_holidays}

            # Find new holidays
            for date_str, holiday in new_dates.items():
                if date_str not in existing_dates:
                    comparison["new"].append(
                        {
                            "year": year,
                            "date": date_str,
                            "name": holiday["name"],
                            "type": "new",
                        }
                    )
                elif existing_dates[date_str]["name"] != holiday["name"]:
                    comparison["updated"].append(
                        {
                            "year": year,
                            "date": date_str,
                            "old_name": existing_dates[date_str]["name"],
                            "new_name": holiday["name"],
                            "type": "updated",
                        }
                    )
                else:
                    comparison["unchanged"].append(
                        {
                            "year": year,
                            "date": date_str,
                            "name": holiday["name"],
                            "type": "unchanged",
                        }
                    )

            # Find removed holidays
            for date_str, holiday in existing_dates.items():
                if date_str not in new_dates:
                    comparison["removed"].append(
                        {
                            "year": year,
                            "date": date_str,
                            "name": holiday["name"],
                            "type": "removed",
                        }
                    )

        # Update JSON file if requested
        if update_json:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)

        # Import to database if requested
        db_stats = None
        if import_to_db:
            db_stats = {"added": 0, "updated": 0, "errors": []}

            # Import new holidays
            for item in comparison["new"]:
                try:
                    date_obj = datetime.strptime(item["date"], "%Y-%m-%d").date()
                    Holiday.objects.create(
                        date=date_obj,
                        name=item["name"],
                        description=f"วันหยุดราชการไทย - {item['name']}",
                        is_active=True,
                        created_by=request.user,
                    )
                    db_stats["added"] += 1
                except Exception as e:
                    db_stats["errors"].append(f"วันที่ {item['date']}: {str(e)}")

            # Update changed holidays
            for item in comparison["updated"]:
                try:
                    date_obj = datetime.strptime(item["date"], "%Y-%m-%d").date()
                    holiday = Holiday.objects.filter(date=date_obj).first()
                    if holiday:
                        holiday.name = item["new_name"]
                        holiday.save()
                        db_stats["updated"] += 1
                except Exception as e:
                    db_stats["errors"].append(f"วันที่ {item['date']}: {str(e)}")

        # Build summary message
        summary = []
        if comparison["new"]:
            summary.append(f"ใหม่ {len(comparison['new'])} วัน")
        if comparison["updated"]:
            summary.append(f"เปลี่ยนแปลง {len(comparison['updated'])} วัน")
        if comparison["unchanged"]:
            summary.append(f"ไม่เปลี่ยนแปลง {len(comparison['unchanged'])} วัน")
        if comparison["removed"]:
            summary.append(f"ถูกลบ {len(comparison['removed'])} วัน")

        message = "ซิงค์ข้อมูลจาก API เรียบร้อย: " + ", ".join(summary)

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "comparison": comparison,
                "summary": {
                    "new_count": len(comparison["new"]),
                    "updated_count": len(comparison["updated"]),
                    "unchanged_count": len(comparison["unchanged"]),
                    "removed_count": len(comparison["removed"]),
                },
                "db_stats": db_stats,
                "json_updated": update_json,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400
        )
    except Exception as e:
        import traceback

        return JsonResponse(
            {
                "success": False,
                "error": f"เกิดข้อผิดพลาด: {str(e)}",
                "traceback": traceback.format_exc(),
            },
            status=500,
        )
