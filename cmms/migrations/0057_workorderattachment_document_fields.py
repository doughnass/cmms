from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0056_equipment_list_type_master_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="workorderattachment",
            name="document_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="workorderattachment",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("image", "รูปภาพ"),
                    ("report", "รายงาน"),
                    ("manual", "คู่มือ"),
                    ("invoice", "ใบแจ้งหนี้/ใบเสร็จ"),
                    ("other", "อื่นๆ"),
                ],
                default="other",
                max_length=20,
            ),
        ),
    ]
