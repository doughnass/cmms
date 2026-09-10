from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0029_align_equipment_list_with_form"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipment_list",
            name="equipment_service_provider",
            field=models.CharField(
                max_length=100,
                blank=True,
                default="",
                verbose_name="ผู้ดูแล/ผู้ให้บริการ",
                help_text="บริษัทหรือหน่วยงานที่รับผิดชอบดูแลและบำรุงรักษาเครื่องมือ",
            ),
        ),
    ]
