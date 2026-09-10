from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0028_alter_equipment_list_equipment_id"),
    ]

    operations = [
        # Remove owner/user subfields that are no longer used by the form
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_sv_subunit",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_sv_unit",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_sv_department",
        ),

        # Remove historical PM/CAL last-date fields (form uses only due/frequency)
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_pm_date",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_cal_date",
        ),

        # Remove legacy owner detail fields (keep equipment_owner_customer)
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_owner_unit",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_owner_section",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_owner_department",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_owner_semi_department",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_owner_division",
        ),

        # Remove legacy user detail fields (keep equipment_user_customer)
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_user_unit",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_user_section",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_user_semi_department",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_user_department",
        ),
        migrations.RemoveField(
            model_name="equipment_list",
            name="equipment_user_division",
        ),

        # Align several fields to be optional / match current model defaults
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_code",
            field=models.CharField(max_length=20, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_name_EN",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_name_TH",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_brand",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_model",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_sn",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_gov",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_price",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_photo",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_type",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_life",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_waranty_date",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_waranty_due",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_distributor_name",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_distributor_tel",
            field=models.CharField(max_length=50, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_pm_fq",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_pm_due",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_cal_fq",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_cal_due",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="requires_pm",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="requires_cal",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_owner_customer",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_user_customer",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_register_username",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_register_adminname",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="equipment_list",
            name="equipment_note",
            field=models.CharField(max_length=300, blank=True, default=""),
        ),
    ]
