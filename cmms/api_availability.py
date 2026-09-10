from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def api_maintenance_availability(request):
    """Lightweight aggregated API for daily maintenance availability.
    Returns technicians[], dailySummary{}, equipment{items, totalHours}.
    """
    from datetime import datetime
    try:
        date_str = request.GET.get("date")
        if not date_str:
            return JsonResponse({"ok": False, "error": "date parameter required"}, status=400)
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"ok": False, "error": "invalid date format"}, status=400)

        # Local imports to avoid circular import at module load time
        from .models import (
            Technician,
            TechnicianAvailability,
            ShiftSchedule,
            WorkOrder,
            Equipment_list,
            MaintenanceTaskDuration,
        )

        # Technicians list (minimal)
        tech_qs = Technician.objects.filter(active=True).order_by("name")
        technicians = []
        for tech in tech_qs:
            avail = TechnicianAvailability.objects.filter(technician=tech, date=target_date).first()
            availability_status = avail.status if avail else None
            note = avail.note if avail else ""
            current_tasks = 0
            if getattr(tech, "user", None):
                current_tasks = (
                    WorkOrder.objects.filter(
                        assigned_to=tech.user,
                        planned_start__date=target_date,
                        status__in=["assigned", "in_progress"],
                    ).count()
                )
            per_day_capacity = getattr(tech, "per_day_capacity", None)
            is_available = True if availability_status is None else (availability_status == "working")
            if per_day_capacity is not None:
                available_flag = is_available and (current_tasks < per_day_capacity)
            else:
                available_flag = is_available

            technicians.append(
                {
                    "id": tech.id,
                    "name": tech.name,
                    "phone": tech.phone or "",
                    "skills": ", ".join(list(tech.skills_m.values_list("label", flat=True))) if getattr(tech, "skills_m", None) else (tech.skills or ""),
                    "currentTasks": current_tasks,
                    "capacity": per_day_capacity,
                    "available": available_flag,
                    "availability_status": availability_status,
                    "note": note,
                }
            )

        # Daily summary (simple counts)
        avails_qs = TechnicianAvailability.objects.filter(date=target_date)
        shifts_qs = ShiftSchedule.objects.filter(date=target_date)

        stats = {
            "totalTechnicians": tech_qs.count(),
            "totalRecords": avails_qs.count(),
            "totalWork": 0,
            "totalLeave": 0,
            "totalHoliday": 0,
            "totalOT": 0,
            "totalOTHours": 0,
            "totalShift": shifts_qs.count(),
        }

        for a in avails_qs:
            st = (a.status or "").lower()
            note = (a.note or "").lower()
            text = f"{st} {note}"
            if any(k in text for k in ["off_", "holiday", "วันหยุด", "หยุด"]):
                stats["totalHoliday"] += 1
            elif any(k in text for k in ["leave", "ลา", "ลากิจ", "ป่วย"]):
                stats["totalLeave"] += 1
            else:
                stats["totalWork"] += 1
            # OT heuristic
            if any(k in text for k in ["ot", "overtime", "ล่วงเวลา", "ล่วง"]):
                stats["totalOT"] += 1

        # Equipment hours
        equipment_items = []
        total_equip_hours = 0.0
        try:
            defaults = {d.task_type: float(d.hours) for d in MaintenanceTaskDuration.objects.all()}
        except Exception:
            defaults = {}

        eq_qs = Equipment_list.objects.filter(requires_pm=True, equipment_pm_due=target_date)
        for eq in eq_qs:
            est = None
            if getattr(eq, "estimated_hours", None) is not None:
                try:
                    est = float(eq.estimated_hours)
                except Exception:
                    est = None
            task_type = "calibration" if getattr(eq, "requires_cal", False) else "maintenance"
            if est is None:
                est = defaults.get(task_type, 1.0)
            equipment_items.append({
                "id": eq.id,
                "code": eq.equipment_id,
                "name": eq.equipment_name_TH or eq.equipment_name_EN,
                "estimatedHours": est,
            })
            try:
                total_equip_hours += float(est)
            except Exception:
                pass

        result = {
            "ok": True,
            "date": date_str,
            "technicians": technicians,
            "dailySummary": stats,
            "equipment": {"items": equipment_items, "totalHours": round(total_equip_hours, 2)},
        }
        return JsonResponse(result)

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.exception("Error in api_maintenance_availability")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
