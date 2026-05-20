# Generated for TrackFlow Dev 1 core shipment contract

import django.core.validators
import django.db.models.deletion
import django_fsm
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_merchant_webhookendpoint_user_flags'),
        ('shipments', '0002_alter_shipment_receiver_address_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='address',
            name='landmark',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='pincode',
            field=models.CharField(max_length=6, validators=[django.core.validators.RegexValidator(message='Pincode must be exactly 6 digits.', regex='^\\d{6}$')]),
        ),
        migrations.AddField(
            model_name='shipment',
            name='cod_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='shipment',
            name='freight_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='shipment',
            name='height_cm',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='shipment',
            name='is_dangerous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shipment',
            name='is_fragile',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shipment',
            name='is_reverse',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='shipment',
            name='length_cm',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='shipment',
            name='merchant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shipment',
            name='original_awb',
            field=models.CharField(blank=True, max_length=14),
        ),
        migrations.AddField(
            model_name='shipment',
            name='service_type',
            field=models.CharField(choices=[('STANDARD', 'Standard'), ('EXPRESS', 'Express'), ('SAME_DAY', 'Same Day')], default='STANDARD', max_length=20),
        ),
        migrations.AddField(
            model_name='shipment',
            name='width_cm',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.RenameField(
            model_name='shipment',
            old_name='weight',
            new_name='weight_kg',
        ),
        migrations.AlterField(
            model_name='shipment',
            name='weight_kg',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='awb',
            field=models.CharField(blank=True, max_length=14, unique=True),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='receiver_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver_shipments', to='shipments.address'),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='sender_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_shipments', to='shipments.address'),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=django_fsm.FSMField(choices=[('BOOKED', 'Booked'), ('PICKUP_SCHEDULED', 'Pickup Scheduled'), ('IN_TRANSIT', 'In Transit'), ('OUT_FOR_DELIVERY', 'Out For Delivery'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed'), ('RTO', 'RTO'), ('CANCELLED', 'Cancelled')], default='BOOKED', max_length=50),
        ),
    ]
