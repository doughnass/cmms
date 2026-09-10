"""
KPI Reports Views
-----------------
Views for generating KPI reports and dashboards
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    WorkOrder, Equipment_list, MasterItem,
    ServiceRequest, Technician, SparePart,
)

# ── Title-based type keyword lookup (fallback when neither M2M nor CharField is set) ──
# Users embed the type in the WO title (e.g. "ซ่อมเครื่อง X", "PM ประจำปี Y")
# because the form exposes workorder_types M2M but not the legacy workorder_type CharField.
def _kw_q(*keywords):
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw)
    return q

_TITLE_TYPE_Q = {
    'maintenance':  _kw_q('PM', 'บำรุงรักษา', 'บำรุง', 'preventive', 'maintenance'),
    'repair':       _kw_q('ซ่อม', 'repair', 'แก้ไข', 'corrective'),
    'calibration':  _kw_q('สอบเทียบ', 'calibrat', 'CAL'),
    'installation': _kw_q('ติดตั้ง', 'install'),
    'consultation': _kw_q('ให้คำปรึกษา', 'ปรึกษา', 'consult'),
}
_ALL_TITLE_TYPE_Q = (
    _TITLE_TYPE_Q['maintenance'] | _TITLE_TYPE_Q['repair'] | _TITLE_TYPE_Q['calibration'] |
    _TITLE_TYPE_Q['installation'] | _TITLE_TYPE_Q['consultation']
)


def get_date_range(period):
    """Return (start_date, end_date) for the given period string."""
    today = timezone.now().date()

    if period == 'today':
        return today, today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        return start_date, start_date + timedelta(days=6)
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start_date = today.replace(month=quarter * 3 + 1, day=1)
        if quarter == 3:
            end_date = today.replace(month=12, day=31)
        else:
            end_date = today.replace(month=(quarter + 1) * 3 + 1, day=1) - timedelta(days=1)
        return start_date, end_date
    elif period == 'year':
        return today.replace(month=1, day=1), today.replace(month=12, day=31)
    else:  # month (default)
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(day=31)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start_date, end_date


def calculate_kpis(start_date, end_date):
    """Calculate all KPIs for the given date range."""

    # WorkOrders created in range (reported_at is auto_now_add)
    work_orders = WorkOrder.objects.filter(
        reported_at__date__range=[start_date, end_date]
    )

    # 1. Work Order Completion Rate
    total_work_orders = work_orders.count()
    completed_work_orders = work_orders.filter(
        status__in=['completed', 'verified', 'closed']
    ).count()
    completion_rate = (completed_work_orders / total_work_orders * 100) if total_work_orders > 0 else 0

    # 2. Mean Time To Repair (MTTR) — actual_start → actual_end
    completed_with_times = work_orders.filter(
        status__in=['completed', 'verified', 'closed'],
        actual_start__isnull=False,
        actual_end__isnull=False,
    )
    mttr_hours = 0.0
    if completed_with_times.exists():
        total_secs = sum(
            (wo.actual_end - wo.actual_start).total_seconds()
            for wo in completed_with_times
            if wo.actual_end and wo.actual_start and wo.actual_end >= wo.actual_start
        )
        count = completed_with_times.count()
        mttr_hours = (total_secs / 3600) / count if count > 0 else 0.0

    # 3. Equipment availability (simple ratio — no downtime tracking field)
    total_equipment = Equipment_list.objects.count()
    # Equipment that has an open/in_progress WO right now = "down"
    down_equipment = Equipment_list.objects.filter(
        workorder__status__in=['open', 'assigned', 'in_progress', 'on_hold']
    ).distinct().count()
    available_equipment = total_equipment - down_equipment
    downtime_rate = (down_equipment / total_equipment * 100) if total_equipment > 0 else 0.0
    avg_uptime = (available_equipment / total_equipment * 100) if total_equipment > 0 else 0.0

    # 4. PM Compliance — workorder_types M2M code='maintenance'
    pm_work_orders = work_orders.filter(workorder_types__code='maintenance').distinct()
    pm_total = pm_work_orders.count()
    pm_completed = pm_work_orders.filter(status__in=['completed', 'verified', 'closed']).count()
    pm_compliance = (pm_completed / pm_total * 100) if pm_total > 0 else 0.0

    # 5. Average Response Time (reported_at → actual_start)
    started_orders = work_orders.filter(actual_start__isnull=False)
    response_times = [
        (wo.actual_start - wo.reported_at).total_seconds() / 3600
        for wo in started_orders
        if wo.actual_start and wo.actual_start >= wo.reported_at
    ]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

    # 6. Outsource cost as a proxy for maintenance cost
    total_cost = work_orders.filter(
        status__in=['completed', 'verified', 'closed'],
        outsource_cost__isnull=False,
    ).aggregate(total=Sum('outsource_cost'))['total'] or 0

    # 7. Work Order Backlog
    backlog_count = WorkOrder.objects.filter(
        status__in=['open', 'assigned', 'in_progress', 'on_hold']
    ).count()

    # 8. First Time Fix Rate — WOs that were completed and have no follow-up
    first_time_fix = work_orders.filter(
        status__in=['completed', 'verified', 'closed'],
        follow_up_needed=False,
    ).count()
    first_time_fix_rate = (first_time_fix / completed_work_orders * 100) if completed_work_orders > 0 else 0.0

    # Breakdown by type — dynamic using MasterItem(category='workorder_type').
    # Multi-count mode: a single WO may contribute to multiple types if its title matches multiple
    # type keywords/labels. We still count explicit M2M links first, then include CharField and
    # title/label matches (allowing overlap across different master types).
    no_m2m_qs = work_orders.filter(workorder_types__isnull=True)

    # Query master-defined workorder types (allows admin to control labels/codes)
    master_types = list(MasterItem.objects.filter(category='workorder_type', active=True).order_by('order', 'label'))
    master_id_by_code = {m.code: m.id for m in master_types if m.code}

    # Start with counts from explicit M2M links (each linked WO counts once per linked type)
    counts_by_master = {m.id: work_orders.filter(workorder_types__id=m.id).distinct().count() for m in master_types}
    type_labels = [(m.label or '').strip() for m in master_types]
    type_codes = [(m.code if m.code else f"mi:{m.id}") for m in master_types]

    # Track which unfiled WOs matched any type (for computing untyped_count)
    matched_ids = set()

    # 1) Count no-M2M WOs that explicitly set the legacy CharField (skip 'other' default)
    for code, mid in master_id_by_code.items():
        if code == 'other':
            continue
        ids = list(no_m2m_qs.filter(workorder_type=code).values_list('id', flat=True))
        if ids:
            counts_by_master[mid] += len(ids)
            matched_ids.update(ids)

    # 2) For WOs with workorder_type == 'other', add counts for every master whose
    #    keyword map or label appears in the title (multi-count — do not stop at first match).
    unfiled_qs = no_m2m_qs.filter(workorder_type='other')
    for m in master_types:
        # Build a flexible match expression: prefer the predefined keyword map
        # but also include the MasterItem.label as a fallback (OR) so admin-defined
        # labels like "ขอความเห็น / คำแนะนำ" are matched even when the
        # keyword list doesn't include every phrasing.
        q_expr = None
        label = (m.label or '').strip()
        if m.code and m.code in _TITLE_TYPE_Q:
            q_expr = _TITLE_TYPE_Q[m.code]
            if label:
                q_expr = q_expr | Q(title__icontains=label)
        else:
            if label:
                q_expr = Q(title__icontains=label)
        if not q_expr:
            continue
        ids = list(unfiled_qs.filter(q_expr).values_list('id', flat=True))
        if ids:
            counts_by_master[m.id] += len(ids)
            matched_ids.update(ids)

    # untyped = unfiled WOs that didn't match any category
    untyped_count = unfiled_qs.exclude(id__in=matched_ids).count()

    # Build ordered type_counts matching master_types order
    type_counts = [counts_by_master.get(m.id, 0) for m in master_types]

    # Map legacy counters from master-driven data when possible, otherwise
    # fall back to previous logic for backward compatibility
    code_to_mid = {m.code: m.id for m in master_types if m.code}
    def legacy_or_zero(code, fallback_q=None):
        if code in code_to_mid:
            return counts_by_master.get(code_to_mid[code], 0)
        if fallback_q is not None:
            return fallback_q()
        return 0

    maintenance_count = legacy_or_zero('maintenance', lambda: (
        work_orders.filter(workorder_types__code='maintenance').distinct().count() +
        no_m2m_qs.filter(workorder_type='maintenance').count() +
        no_m2m_qs.filter(_TITLE_TYPE_Q['maintenance']).count()
    ))
    repair_count = legacy_or_zero('repair', lambda: (
        work_orders.filter(workorder_types__code='repair').distinct().count() +
        no_m2m_qs.filter(workorder_type='repair').count() +
        no_m2m_qs.filter(_TITLE_TYPE_Q['repair']).count()
    ))
    calibration_count = legacy_or_zero('calibration', lambda: (
        work_orders.filter(workorder_types__code='calibration').distinct().count() +
        no_m2m_qs.filter(workorder_type='calibration').count() +
        no_m2m_qs.filter(_TITLE_TYPE_Q['calibration']).count()
    ))

    other_count = legacy_or_zero('other', lambda: (
        work_orders.filter(workorder_types__code__in=['installation', 'consultation', 'other']).distinct().count() +
        no_m2m_qs.filter(workorder_type__in=['installation', 'consultation']).count() +
        no_m2m_qs.filter(_TITLE_TYPE_Q['installation'] | _TITLE_TYPE_Q['consultation']).count()
    ))

    # JSON arrays for Chart.js (use ensure_ascii=False to keep Thai labels readable)
    type_labels_json = json.dumps(type_labels, ensure_ascii=False)
    type_codes_json = json.dumps(type_codes)
    type_counts_json = json.dumps(type_counts)

    # ── Service Request KPIs ──────────────────────────────────────────────────
    today = timezone.now().date()
    sr_qs = ServiceRequest.objects.filter(
        requested_at__date__range=[start_date, end_date]
    )
    sr_total = sr_qs.count()
    sr_converted = sr_qs.filter(status='converted').count()
    sr_conversion_rate = round((sr_converted / sr_total * 100) if sr_total > 0 else 0.0, 1)
    sr_pending = ServiceRequest.objects.filter(status='new').count()
    sr_rejected = sr_qs.filter(status='rejected').count()

    # ── Equipment Health KPIs ─────────────────────────────────────────────────
    pm_overdue = Equipment_list.objects.filter(
        requires_pm=True,
        equipment_pm_due__lt=today,
        equipment_pm_due__isnull=False,
    ).count()
    cal_overdue = Equipment_list.objects.filter(
        requires_cal=True,
        equipment_cal_due__lt=today,
        equipment_cal_due__isnull=False,
    ).count()
    pm_due_soon = Equipment_list.objects.filter(
        requires_pm=True,
        equipment_pm_due__range=[today, today + timedelta(days=30)],
    ).count()

    # ── Work Order special states (current/all time) ──────────────────────────
    wo_on_hold = WorkOrder.objects.filter(status='on_hold').count()
    wo_follow_up = WorkOrder.objects.filter(
        follow_up_needed=True,
        status__in=['completed', 'verified', 'closed'],
    ).count()
    wo_outsource_period = work_orders.exclude(outsource_vendor='').count()
    wo_outsource_overdue = WorkOrder.objects.filter(
        status__in=['open', 'assigned', 'in_progress', 'on_hold'],
        outsource_expected_date__lt=today,
        outsource_expected_date__isnull=False,
    ).count()

    return {
        'completion_rate': round(completion_rate, 1),
        'mttr_hours': round(mttr_hours, 1),
        'avg_uptime': round(avg_uptime, 1),
        'downtime_rate': round(downtime_rate, 1),
        'pm_compliance': round(pm_compliance, 1),
        'avg_response_time': round(avg_response_time, 1),
        'total_cost': total_cost,
        'backlog_count': backlog_count,
        'first_time_fix_rate': round(first_time_fix_rate, 1),
        'total_work_orders': total_work_orders,
        'completed_work_orders': completed_work_orders,
        'total_equipment': total_equipment,
        'down_equipment': down_equipment,
        'available_equipment': available_equipment,
        # compatibility keys
        'maintenance_count': maintenance_count,
        'repair_count': repair_count,
        'calibration_count': calibration_count,
        'other_count': other_count,
        'untyped_count': untyped_count,
        # Master-driven arrays
        'type_labels_json': type_labels_json,
        'type_codes_json': type_codes_json,
        'type_counts_json': type_counts_json,
        # Service Request
        'sr_total': sr_total,
        'sr_converted': sr_converted,
        'sr_conversion_rate': sr_conversion_rate,
        'sr_pending': sr_pending,
        'sr_rejected': sr_rejected,
        # Equipment Health
        'pm_overdue': pm_overdue,
        'cal_overdue': cal_overdue,
        'pm_due_soon': pm_due_soon,
        # WO special states
        'wo_on_hold': wo_on_hold,
        'wo_follow_up': wo_follow_up,
        'wo_outsource_period': wo_outsource_period,
        'wo_outsource_overdue': wo_outsource_overdue,
    }


@login_required
def kpi_dashboard(request):
    """KPI Dashboard with interactive charts."""
    period = request.GET.get('period', 'month')
    start_date, end_date = get_date_range(period)
    kpis = calculate_kpis(start_date, end_date)

    # Auto-fallback: if selected period has no WOs, widen to the next period
    _fallback_order = ['month', 'quarter', 'year']
    _fallback_note = None
    if kpis['total_work_orders'] == 0 and period in _fallback_order:
        _PERIOD_LABEL = {'month': 'เดือนนี้', 'quarter': 'ไตรมาสนี้', 'year': 'ปีนี้'}
        for wider in _fallback_order[_fallback_order.index(period) + 1:]:
            _s, _e = get_date_range(wider)
            _k = calculate_kpis(_s, _e)
            if _k['total_work_orders'] > 0:
                period, start_date, end_date, kpis = wider, _s, _e, _k
                _fallback_note = f'ไม่มีข้อมูลในช่วงที่เลือก — แสดงผล{_PERIOD_LABEL.get(wider, wider)}แทน'
                break

    # Top equipment by completed WO count
    top_equipment = Equipment_list.objects.annotate(
        wo_count=Count(
            'workorder',
            filter=Q(workorder__status__in=['completed', 'verified', 'closed'])
        )
    ).order_by('-wo_count')[:10]

    # Trend vs previous period
    delta = end_date - start_date
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - delta
    prev_kpis = calculate_kpis(prev_start, prev_end)

    trends = {}
    for key, val in kpis.items():
        if isinstance(val, (int, float)) and key in prev_kpis and prev_kpis[key]:
            trends[f'{key}_trend'] = round((val - prev_kpis[key]) / prev_kpis[key] * 100, 1)
        else:
            trends[f'{key}_trend'] = 0

    # Monthly data for line chart
    monthly_data = list(
        WorkOrder.objects.filter(
            reported_at__date__gte=start_date - timedelta(days=180)
        ).annotate(
            month=TruncMonth('reported_at')
        ).values('month').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'verified', 'closed']))
        ).order_by('month')
    )

    # ── Spare Parts & Technician context (not period-bound) ─────────────────
    from django.db.models import F as _F
    low_stock_count = SparePart.objects.filter(
        active=True, quantity__lte=_F('min_quantity')
    ).count()
    total_parts = SparePart.objects.filter(active=True).count()
    active_tech_count = Technician.objects.filter(active=True).count()

    # Weekly response time data
    from collections import defaultdict
    weekly_buckets = defaultdict(list)
    for wo in WorkOrder.objects.filter(
        reported_at__date__range=[start_date, end_date],
        actual_start__isnull=False,
    ).values('reported_at', 'actual_start'):
        rs, as_ = wo['reported_at'], wo['actual_start']
        if as_ and as_ >= rs:
            wk = f"สัปดาห์ {rs.isocalendar()[1]}"
            weekly_buckets[wk].append((as_ - rs).total_seconds() / 3600)
    weekly_response = [
        {'week': wk, 'avg': round(sum(v) / len(v), 1)}
        for wk, v in sorted(weekly_buckets.items())
    ]

    # ── Per-assignee Performance (3 queries only, no N+1) ──────────────────────
    from collections import defaultdict as _dd2

    # Queryset scoped to the same period
    period_wos = WorkOrder.objects.filter(reported_at__date__range=[start_date, end_date])

    # Q1: aggregate counts per assignee in the period
    assignee_agg = list(
        period_wos.filter(assigned_to__isnull=False)
        .values(
            'assigned_to__id', 'assigned_to__username',
            'assigned_to__first_name', 'assigned_to__last_name',
        )
        .annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'verified', 'closed'])),
            on_hold_count=Count('id', filter=Q(status='on_hold')),
            follow_up_count=Count('id', filter=Q(follow_up_needed=True)),
        )
        .order_by('-total')
    )

    # Q2: timed WOs for MTTR per assignee
    user_times = _dd2(list)
    for wo in period_wos.filter(
        assigned_to__isnull=False,
        status__in=['completed', 'verified', 'closed'],
        actual_start__isnull=False,
        actual_end__isnull=False,
    ).values('assigned_to__id', 'actual_start', 'actual_end'):
        if wo['actual_end'] and wo['actual_start'] and wo['actual_end'] >= wo['actual_start']:
            user_times[wo['assigned_to__id']].append(
                (wo['actual_end'] - wo['actual_start']).total_seconds() / 3600
            )

    # Q3: Technician name map (user_id → name)
    tech_name_map = {
        t.user_id: t.name
        for t in Technician.objects.filter(user__isnull=False).only('user_id', 'name')
    }

    assignee_stats = []
    for a in assignee_agg:
        uid = a['assigned_to__id']
        full_name = f"{a['assigned_to__first_name']} {a['assigned_to__last_name']}".strip()
        name = tech_name_map.get(uid) or full_name or a['assigned_to__username']
        times = user_times.get(uid, [])
        total = a['total']
        completed = a['completed']
        rate = round(completed / total * 100, 1) if total > 0 else 0.0
        assignee_stats.append({
            'name': name,
            'username': a['assigned_to__username'],
            'total': total,
            'completed': completed,
            'rate': rate,
            'mttr': round(sum(times) / len(times), 1) if times else None,
            'on_hold': a['on_hold_count'],
            'follow_up': a['follow_up_count'],
            'has_profile': uid in tech_name_map,
        })

    assignee_chart_json = json.dumps({
        'names': [a['name'] for a in assignee_stats],
        'rates': [a['rate'] for a in assignee_stats],
        'totals': [a['total'] for a in assignee_stats],
        'colors': [
            '#10b981' if a['rate'] >= 90 else '#f59e0b' if a['rate'] >= 70 else '#ef4444'
            for a in assignee_stats
        ],
    })

    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'top_equipment': top_equipment,
        'monthly_data_json': json.dumps(monthly_data, default=str),
        'weekly_response_json': json.dumps(weekly_response),
        'available_equipment': kpis.get('available_equipment', kpis['total_equipment'] - kpis['down_equipment']),
        'low_stock_count': low_stock_count,
        'total_parts': total_parts,
        'active_tech_count': active_tech_count,
        'assignee_stats': assignee_stats,
        'assignee_chart_json': assignee_chart_json,
        'fallback_note': _fallback_note,
        **kpis,
        **trends,
    }
    return render(request, 'reports/kpi_dashboard.html', context)


@login_required
def kpi_report_print(request):
    """Print-friendly KPI report."""
    period = request.GET.get('period', 'month')
    start_date, end_date = get_date_range(period)
    kpis = calculate_kpis(start_date, end_date)

    top_equipment = Equipment_list.objects.annotate(
        wo_count=Count(
            'workorder',
            filter=Q(workorder__status__in=['completed', 'verified', 'closed'])
        )
    ).order_by('-wo_count')[:10]

    delta = end_date - start_date
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - delta
    prev_kpis = calculate_kpis(prev_start, prev_end)

    context = {
        'report_date': timezone.now(),
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'top_equipment': top_equipment,
        'prev_kpis': prev_kpis,
        **kpis,
    }
    return render(request, 'reports/kpi_report_print.html', context)


@login_required
def kpi_comparison(request):
    """KPI comparison between two periods."""
    current_period = request.GET.get('current', 'this-month')
    previous_period = request.GET.get('previous', 'last-month')
    today = timezone.now().date()

    # Current period dates
    if current_period == 'this-month':
        current_start = today.replace(day=1)
        current_end = (current_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif current_period == 'this-quarter':
        quarter = (today.month - 1) // 3
        current_start = today.replace(month=quarter * 3 + 1, day=1)
        current_end = today
    elif current_period == 'this-year':
        current_start = today.replace(month=1, day=1)
        current_end = today
    else:
        current_start, current_end = get_date_range('month')

    # Previous period dates
    if previous_period == 'last-month':
        previous_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        previous_end = today.replace(day=1) - timedelta(days=1)
    elif previous_period == 'last-quarter':
        quarter = (today.month - 1) // 3
        if quarter == 0:
            previous_start = today.replace(year=today.year - 1, month=10, day=1)
            previous_end = today.replace(year=today.year - 1, month=12, day=31)
        else:
            previous_start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            previous_end = today.replace(month=quarter * 3 + 1, day=1) - timedelta(days=1)
    elif previous_period == 'last-year':
        previous_start = today.replace(year=today.year - 1, month=1, day=1)
        previous_end = today.replace(year=today.year - 1, month=12, day=31)
    else:
        delta = current_end - current_start
        previous_end = current_start - timedelta(days=1)
        previous_start = previous_end - delta

    current_kpis = calculate_kpis(current_start, current_end)
    previous_kpis = calculate_kpis(previous_start, previous_end)

    comparisons = {}
    improve_when_higher = {'completion_rate', 'avg_uptime', 'pm_compliance', 'first_time_fix_rate'}
    for key, cur_val in current_kpis.items():
        prev_val = previous_kpis.get(key, 0)
        if not isinstance(cur_val, (int, float)):
            continue
        diff = cur_val - prev_val
        pct_change = round(diff / prev_val * 100, 1) if prev_val else 0
        comparisons[key] = {
            'current': cur_val,
            'previous': prev_val,
            'diff': round(diff, 1),
            'pct_change': pct_change,
            'improved': diff > 0 if key in improve_when_higher else diff < 0,
        }

    weekly_current = list(
        WorkOrder.objects.filter(
            reported_at__date__range=[current_start, current_end]
        ).annotate(week=TruncWeek('reported_at')).values('week').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'verified', 'closed']))
        ).order_by('week')
    )
    weekly_previous = list(
        WorkOrder.objects.filter(
            reported_at__date__range=[previous_start, previous_end]
        ).annotate(week=TruncWeek('reported_at')).values('week').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'verified', 'closed']))
        ).order_by('week')
    )

    context = {
        'current_period': current_period,
        'previous_period': previous_period,
        'current_start': current_start,
        'current_end': current_end,
        'previous_start': previous_start,
        'previous_end': previous_end,
        'current_kpis': current_kpis,
        'previous_kpis': previous_kpis,
        'comparisons': comparisons,
        'weekly_current_json': json.dumps(weekly_current, default=str),
        'weekly_previous_json': json.dumps(weekly_previous, default=str),
    }
    return render(request, 'reports/kpi_comparison.html', context)


@login_required
def api_kpi_data(request):
    """API endpoint — returns KPI data as JSON for AJAX requests."""
    from django.http import JsonResponse

    period = request.GET.get('period', 'month')
    start_date, end_date = get_date_range(period)
    kpis = calculate_kpis(start_date, end_date)
    kpis['start_date'] = start_date.isoformat()
    kpis['end_date'] = end_date.isoformat()
    # Decimal fields are not JSON-serialisable by default
    kpis['total_cost'] = float(kpis['total_cost'])
    return JsonResponse(kpis)


@login_required
def api_workorders_by_type(request):
    """Return work orders filtered by workorder_types__code for the drill-down modal."""
    from django.http import JsonResponse

    code = request.GET.get('code', '')
    period = request.GET.get('period', 'month')
    start_date, end_date = get_date_range(period)

    base_qs = WorkOrder.objects.filter(
        reported_at__date__range=[start_date, end_date]
    ).select_related('assigned_to', 'equipment')

    # WOs with no M2M and CharField at default 'other' — use title keyword as last resort
    no_m2m_unfiled = base_qs.filter(workorder_types__isnull=True, workorder_type='other')

    if code == 'untyped':
        qs = no_m2m_unfiled.exclude(_ALL_TITLE_TYPE_Q)
    elif code == 'other':
        qs = base_qs.filter(
            Q(workorder_types__code__in=['installation', 'consultation', 'other']) |
            Q(workorder_types__isnull=True, workorder_type__in=['installation', 'consultation']) |
            (Q(workorder_types__isnull=True, workorder_type='other') &
             (_TITLE_TYPE_Q['installation'] | _TITLE_TYPE_Q['consultation']))
        ).distinct()
    elif code:
        # Support codes that are master-item id references like 'mi:123'
        if code.startswith('mi:'):
            try:
                mi_id = int(code.split(':', 1)[1])
                qs = base_qs.filter(workorder_types__id=mi_id).distinct()
            except Exception:
                qs = base_qs.none()
        else:
            if code in _TITLE_TYPE_Q:
                # use predefined keyword map for well-known codes
                title_q = _TITLE_TYPE_Q[code]
                qs = base_qs.filter(
                    Q(workorder_types__code=code) |
                    Q(workorder_types__isnull=True, workorder_type=code) |
                    (Q(workorder_types__isnull=True, workorder_type='other') & title_q)
                ).distinct()
            else:
                # Custom code (e.g. 'breakdown') — look up MasterItem.label for title matching
                mi = MasterItem.objects.filter(
                    category='workorder_type', code=code, active=True
                ).first()
                base_q = (
                    Q(workorder_types__code=code) |
                    Q(workorder_types__isnull=True, workorder_type=code)
                )
                if mi and mi.label:
                    base_q |= Q(
                        workorder_types__isnull=True,
                        workorder_type='other',
                        title__icontains=mi.label,
                    )
                qs = base_qs.filter(base_q).distinct()
    else:
        qs = base_qs.none()

    STATUS_TH = {
        'open': 'เปิด', 'assigned': 'มอบหมายแล้ว', 'in_progress': 'กำลังดำเนินการ',
        'on_hold': 'ระงับชั่วคราว', 'completed': 'เสร็จสิ้น',
        'verified': 'ตรวจสอบแล้ว', 'closed': 'ปิดแล้ว',
    }

    data = []
    for wo in qs.order_by('-reported_at')[:100]:
        assignee = ''
        if wo.assigned_to:
            assignee = wo.assigned_to.get_full_name() or wo.assigned_to.username
        data.append({
            'id': wo.id,
            'title': wo.title,
            'status': wo.status,
            'status_th': STATUS_TH.get(wo.status, wo.status),
            'assigned_to': assignee,
            'equipment': str(wo.equipment) if wo.equipment else '-',
            'reported_at': wo.reported_at.strftime('%d/%m/%Y'),
        })

    return JsonResponse({'workorders': data, 'count': qs.count()})
