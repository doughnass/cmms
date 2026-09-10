import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]


def parse_date(value):
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except Exception:
            continue
    # try ISO
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


class Command(BaseCommand):
    help = "Import Equipment_list entries from a CSV file. Columns should match model field names."

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=str, help="Path to CSV file to import")
        parser.add_argument(
            "--dry-run", action="store_true", help="Parse and report but do not save"
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip rows where equipment_id already exists",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing rows when equipment_id matches",
        )

    def handle(self, *args, **options):
        csvpath = options["csvfile"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]
        update_existing = options["update_existing"]

        if not os.path.exists(csvpath):
            raise CommandError(f"File not found: {csvpath}")

        from cmms.models import Equipment_list

        created = 0
        updated = 0
        skipped = 0
        failed = 0

        with open(csvpath, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for rnum, row in enumerate(reader, start=1):
                # normalize keys and values
                row = {
                    k.strip(): (v.strip() if v is not None else "")
                    for k, v in row.items()
                }
                equipment_id = row.get("equipment_id") or ""
                if not equipment_id:
                    self.stderr.write(
                        self.style.ERROR(f"Row {rnum}: missing equipment_id, skipping")
                    )
                    failed += 1
                    continue

                try:
                    existing = Equipment_list.objects.filter(
                        equipment_id=equipment_id
                    ).first()
                    if existing:
                        if skip_existing and not update_existing:
                            self.stdout.write(
                                f"Row {rnum}: exists -> skipped: {equipment_id}"
                            )
                            skipped += 1
                            continue
                        if update_existing:
                            if dry_run:
                                self.stdout.write(
                                    f"Row {rnum}: would update: {equipment_id}"
                                )
                                updated += 1
                            else:
                                # update only fields provided
                                for field, val in row.items():
                                    if val == "":
                                        continue
                                    # If the existing object has the attribute, set it safely
                                    if hasattr(existing, field):
                                        # handle types
                                        if field in (
                                            "equipment_price",
                                            "equipment_pm_fq",
                                            "equipment_cal_fq",
                                            "equipment_life",
                                        ):
                                            try:
                                                setattr(existing, field, int(val))
                                            except Exception:
                                                pass
                                        elif field in (
                                            "equipment_waranty_date",
                                            "equipment_waranty_due",
                                            "equipment_pm_due",
                                            "equipment_cal_due",
                                            "equipment_register_date",
                                        ):
                                            dt = parse_date(val)
                                            if dt:
                                                setattr(existing, field, dt)
                                        elif field in ("requires_pm", "requires_cal"):
                                            setattr(
                                                existing,
                                                field,
                                                val.lower() in ("1", "true", "yes", "y", "t"),
                                            )
                                        else:
                                            setattr(existing, field, val)
                                    else:
                                        # map legacy owner/user columns into customer fields when possible
                                        if field.startswith("equipment_owner_"):
                                            if hasattr(existing, "equipment_owner_customer"):
                                                setattr(existing, "equipment_owner_customer", val)
                                        if field.startswith("equipment_user_"):
                                            if hasattr(existing, "equipment_user_customer"):
                                                setattr(existing, "equipment_user_customer", val)
                                existing.save()
                                self.stdout.write(f"Row {rnum}: updated: {equipment_id}")
                                updated += 1
                            continue

                    # create new
                    if dry_run:
                        self.stdout.write(f"Row {rnum}: would create: {equipment_id}")
                        created += 1
                    else:
                        obj = Equipment_list()
                        # map provided columns into model fields when they exist
                        for field, val in row.items():
                            if val == "":
                                continue
                            # if the model has this attribute, set it safely
                            if hasattr(obj, field):
                                if field in (
                                    "equipment_price",
                                    "equipment_pm_fq",
                                    "equipment_cal_fq",
                                    "equipment_life",
                                ):
                                    try:
                                        setattr(obj, field, int(val))
                                    except Exception:
                                        pass
                                elif field in (
                                    "equipment_waranty_date",
                                    "equipment_waranty_due",
                                    "equipment_pm_due",
                                    "equipment_cal_due",
                                    "equipment_register_date",
                                ):
                                    dt = parse_date(val)
                                    if dt:
                                        setattr(obj, field, dt)
                                elif field in ("requires_pm", "requires_cal"):
                                    setattr(
                                        obj,
                                        field,
                                        val.lower() in ("1", "true", "yes", "y", "t"),
                                    )
                                else:
                                    setattr(obj, field, val)
                            else:
                                # map legacy owner/user columns into customer fields when possible
                                if field.startswith("equipment_owner_"):
                                    if hasattr(obj, "equipment_owner_customer"):
                                        setattr(obj, "equipment_owner_customer", val)
                                if field.startswith("equipment_user_"):
                                    if hasattr(obj, "equipment_user_customer"):
                                        setattr(obj, "equipment_user_customer", val)
                        obj.save()
                        self.stdout.write(f"Row {rnum}: created: {equipment_id}")
                        created += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Row {rnum}: error: {e}"))
                    failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: created={created} updated={updated} skipped={skipped} failed={failed}"
            )
        )
