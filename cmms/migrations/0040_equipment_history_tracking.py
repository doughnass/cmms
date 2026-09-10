# Generated migration for equipment registration and edit history tracking

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cmms', '0030_equipment_list_equipment_service_provider'),
    ]

    operations = [
        # Add timestamp and user tracking fields to Equipment_list
        migrations.AddField(
            model_name='equipment_list',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='สร้างเมื่อ'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='equipment_list',
            name='created_by',
            field=models.CharField(max_length=100, blank=True, default='', verbose_name='สร้างโดย'),
        ),
        migrations.AddField(
            model_name='equipment_list',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='แก้ไขล่าสุดเมื่อ'),
        ),
        migrations.AddField(
            model_name='equipment_list',
            name='updated_by',
            field=models.CharField(max_length=100, blank=True, default='', verbose_name='แก้ไขล่าสุดโดย'),
        ),
        
        # Create new EquipmentHistory model for detailed audit trail
        migrations.CreateModel(
            name='EquipmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment_id', models.CharField(max_length=20, db_index=True, verbose_name='รหัสเครื่อง')),
                ('action_type', models.CharField(max_length=20, choices=[
                    ('CREATE', 'สร้างทะเบียน'),
                    ('UPDATE', 'แก้ไขทะเบียน'),
                    ('DELETE', 'ลบทะเบียน'),
                ], verbose_name='ประเภทการดำเนินการ')),
                ('action_by', models.CharField(max_length=100, verbose_name='ดำเนินการโดย')),
                ('action_at', models.DateTimeField(auto_now_add=True, verbose_name='เวลาที่ดำเนินการ')),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')),
                ('changed_fields', models.JSONField(null=True, blank=True, verbose_name='ฟิลด์ที่เปลี่ยนแปลง')),
                ('old_values', models.JSONField(null=True, blank=True, verbose_name='ค่าเดิม')),
                ('new_values', models.JSONField(null=True, blank=True, verbose_name='ค่าใหม่')),
                ('notes', models.TextField(blank=True, default='', verbose_name='หมายเหตุ')),
            ],
            options={
                'verbose_name': 'ประวัติการขึ้นทะเบียนอุปกรณ์',
                'verbose_name_plural': 'ประวัติการขึ้นทะเบียนอุปกรณ์',
                'ordering': ['-action_at'],
                'indexes': [
                    models.Index(fields=['equipment_id', '-action_at'], name='equipment_history_idx'),
                    models.Index(fields=['action_type'], name='action_type_idx'),
                ],
            },
        ),
    ]
