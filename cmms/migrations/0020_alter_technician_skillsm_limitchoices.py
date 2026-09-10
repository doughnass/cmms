"""Alter Technician.skills_m limit_choices_to to category 'equipments'.

This migration updates the field options so admin/forms that rely on
limit_choices_to show MasterItem entries from the 'equipments' category.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0019_copy_technician_skill_to_equipments"),
    ]

    operations = [
        migrations.AlterField(
            model_name="technician",
            name="skills_m",
            field=models.ManyToManyField(
                blank=True,
                related_name="technicians",
                related_query_name="technician",
                to="cmms.MasterItem",
                verbose_name="ทักษะ / ประเภทอุปกรณ์",
                limit_choices_to={"category": "equipments"},
            ),
        ),
    ]
