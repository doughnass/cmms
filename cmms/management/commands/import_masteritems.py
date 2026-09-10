import csv
import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import MasterItem entries from a CSV file. Columns: category,code,label,description,active,order,parent_category,parent_code"

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=str, help="Path to CSV file to import")
        parser.add_argument(
            "--dry-run", action="store_true", help="Parse and report but do not save"
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="Skip rows where (category,code) already exists",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing items when (category,code) matches",
        )

    def handle(self, *args, **options):
        csvpath = options["csvfile"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]
        update_existing = options["update_existing"]

        if not os.path.exists(csvpath):
            raise CommandError(f"File not found: {csvpath}")

        from cmms.models import MasterItem

        created = 0
        updated = 0
        skipped = 0
        failed = 0

        with open(csvpath, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            required = ["category", "label"]
            rows = list(reader)

            # First pass: create/update items without resolving parent
            for rnum, raw in enumerate(rows, start=1):
                # normalize keys and values
                row = {
                    k.strip(): (v.strip() if v is not None else "")
                    for k, v in raw.items()
                }
                if not all(k in row for k in required):
                    self.stderr.write(
                        self.style.ERROR(
                            f"Row {rnum}: missing required columns {required}"
                        )
                    )
                    failed += 1
                    continue

                category = row.get("category") or ""
                code = row.get("code") or ""
                label = row.get("label") or ""
                description = row.get("description") or ""
                active = row.get("active", "").lower() in ("1", "true", "yes", "y", "t")
                order = 0
                try:
                    order = int(row.get("order") or 0)
                except Exception:
                    order = 0

                if not category or not label:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {rnum}: empty category or label; skipping"
                        )
                    )
                    skipped += 1
                    continue

                try:
                    existing = None
                    if code:
                        existing = MasterItem.objects.filter(
                            category=category, code=code
                        ).first()
                    else:
                        existing = MasterItem.objects.filter(
                            category=category, label=label
                        ).first()

                    if existing:
                        if skip_existing and not update_existing:
                            self.stdout.write(
                                f"Row {rnum}: exists -> skipped: {category} / {code or label}"
                            )
                            skipped += 1
                            continue
                        if update_existing:
                            if dry_run:
                                self.stdout.write(
                                    f"Row {rnum}: would update existing: {category} / {code or label}"
                                )
                                updated += 1
                            else:
                                existing.label = label
                                existing.description = description
                                existing.active = active
                                existing.order = order
                                existing.code = code or existing.code
                                existing.save()
                                self.stdout.write(f"Row {rnum}: updated: {existing}")
                                updated += 1
                            continue

                    # create new
                    if dry_run:
                        self.stdout.write(
                            f"Row {rnum}: would create: {category} / {code or label}"
                        )
                        created += 1
                    else:
                        mi = MasterItem.objects.create(
                            category=category,
                            code=code,
                            label=label,
                            description=description,
                            active=active,
                            order=order,
                        )
                        self.stdout.write(f"Row {rnum}: created: {mi}")
                        created += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Row {rnum}: error: {e}"))
                    failed += 1

        # Second pass: resolve parent links where provided
        linked = 0
        for rnum, raw in enumerate(rows, start=1):
            try:
                row = {
                    k.strip(): (v.strip() if v is not None else "")
                    for k, v in raw.items()
                }
                category = row.get("category") or ""
                code = row.get("code") or ""
                label = row.get("label") or ""
                parent_code = row.get("parent_code") or ""
                parent_category = row.get("parent_category") or ""
                if not parent_code:
                    continue

                # find child item
                child = None
                if code:
                    child = MasterItem.objects.filter(
                        category=category, code=code
                    ).first()
                if not child and label:
                    child = MasterItem.objects.filter(
                        category=category, label=label
                    ).first()
                if not child:
                    continue

                # find parent by category+code (or fallback to code-only)
                parent = None
                if parent_category:
                    parent = MasterItem.objects.filter(
                        category=parent_category, code=parent_code
                    ).first()
                if not parent:
                    parent = MasterItem.objects.filter(code=parent_code).first()
                if parent:
                    child.parent = parent
                    child.save()
                    linked += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Linking Row {rnum}: error: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: created={created} updated={updated} skipped={skipped} failed={failed} linked_parents={linked}"
            )
        )
