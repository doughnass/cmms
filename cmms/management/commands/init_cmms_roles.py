from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from cmms.models import Equipment_list


class Command(BaseCommand):
    help = "Initialize CMMS roles and assign basic permissions"

    def handle(self, *args, **options):
        # Roles to create
        roles = {
            "Admin": {
                "permissions": [
                    "add_equipment_list",
                    "change_equipment_list",
                    "delete_equipment_list",
                    "view_equipment_list",
                ]
            },
            "Planner": {
                "permissions": [
                    "add_equipment_list",
                    "change_equipment_list",
                    "view_equipment_list",
                ]
            },
            "Technician": {
                "permissions": ["change_equipment_list", "view_equipment_list"]
            },
            "Viewer": {"permissions": ["view_equipment_list"]},
        }

        ct = ContentType.objects.get_for_model(Equipment_list)

        for role_name, meta in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            perms = []
            for perm_codename in meta["permissions"]:
                try:
                    perm = Permission.objects.get(
                        content_type=ct, codename=perm_codename
                    )
                    perms.append(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Permission {perm_codename} not found for model Equipment_list"
                        )
                    )
            group.permissions.set(perms)
            group.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group {role_name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated group {role_name}"))

        self.stdout.write(self.style.SUCCESS("CMMS roles initialization complete."))
