import django_fsm
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0004_shipment_label_file_shipmentitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='awb',
            field=models.CharField(blank=True, db_index=True, max_length=14, unique=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=django_fsm.FSMField(
                choices=[
                    ('BOOKED', 'Booked'),
                    ('PICKUP_SCHEDULED', 'Pickup Scheduled'),
                    ('IN_TRANSIT', 'In Transit'),
                    ('OUT_FOR_DELIVERY', 'Out For Delivery'),
                    ('DELIVERED', 'Delivered'),
                    ('FAILED', 'Failed'),
                    ('RTO', 'RTO'),
                    ('CANCELLED', 'Cancelled'),
                ],
                db_index=True,
                default='BOOKED',
                max_length=50,
            ),
        ),
        migrations.AddIndex(
            model_name='shipment',
            index=models.Index(fields=['merchant', 'created_at'], name='shipments_s_merchan_889b0a_idx'),
        ),
        migrations.AddIndex(
            model_name='shipment',
            index=models.Index(fields=['merchant', 'status'], name='shipments_s_merchan_dba4a6_idx'),
        ),
    ]
