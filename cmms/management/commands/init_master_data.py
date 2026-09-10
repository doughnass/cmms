from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initialize default master data for CMMS (creates categories and items)"

    DEFAULTS = {
        "equipment_type": [
            ("DIAG", "Diagnostic"),
            ("THER", "Therapeutic"),
            ("SUPP", "Support"),
            ("EDU", "Education"),
            ("RES", "Research"),
        ],
        "equipment_status": [
            ("active", "Active"),
            ("in_maintenance", "In Maintenance"),
            ("decommissioned", "Decommissioned"),
        ],
        "departments": [
            ("nursing", "ฝ่ายการพยาบาล"),
            ("biomed", "หน่วยวิศวกรรมชีวการแพทย์"),
            ("pharmacy", "ฝ่ายเภสัชกรรม"),
        ],
        "priorities": [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        "fault_types": [
            ("electrical", "Electrical"),
            ("mechanical", "Mechanical"),
            ("software", "Software"),
            ("calibration", "Calibration"),
        ],
        "pm_frequencies": [
            ("1m", "1 month"),
            ("3m", "3 months"),
            ("6m", "6 months"),
            ("12m", "12 months"),
        ],
        "calibration_frequencies": [
            ("6m", "6 months"),
            ("12m", "12 months"),
        ],
        "locations": [
            ("main_hospital", "Main Hospital"),
            ("branch", "Branch Site"),
        ],
        "manufacturers": [
            ("philips", "Philips"),
            ("ge", "GE Healthcare"),
            ("siemens", "Siemens Healthineers"),
        ],
        "currencies": [
            ("THB", "Thai Baht"),
            ("USD", "US Dollar"),
        ],
    }

    def handle(self, *args, **options):
        from cmms.models import MasterItem

        created = 0
        updated = 0
        for category, items in self.DEFAULTS.items():
            for code, label in items:
                obj, ok = MasterItem.objects.get_or_create(
                    category=category, code=code, defaults={"label": label}
                )
                if ok:
                    created += 1
                else:
                    # ensure label updated if different
                    if obj.label != label:
                        obj.label = label
                        obj.save()
                        updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Initialized master data: created={created} updated={updated}"
            )
        )
