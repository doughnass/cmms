from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def copied_masteritems_report(request):
    from django.db.models import Count

    from cmms.models import MasterItem

    copied = MasterItem.objects.filter(
        category="equipments", description__contains="[copied-from-technician_skill:"
    )
    total_equip = MasterItem.objects.filter(category="equipments").count()
    total_tech = MasterItem.objects.filter(category="technician_skill").count()
    tech_with_rel = (
        MasterItem.objects.filter(category="technician_skill")
        .annotate(num_tech=Count("technicians"))
        .filter(num_tech__gt=0)
    )

    context = {
        "copied": copied,
        "total_equip": total_equip,
        "total_tech": total_tech,
        "tech_with_rel_count": tech_with_rel.count(),
    }
    return render(request, "admin/copied_masteritems_report.html", context)
