from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0045_document_quotation_quotationitem_servicerequestv2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicerequest",
            name="preferred_service_date",
            field=models.DateField(null=True, blank=True),
        ),
    ]
