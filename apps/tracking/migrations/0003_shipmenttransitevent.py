from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0005_shipment_indexes'),
        ('tracking', '0002_tracking_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentTransitEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hub_name', models.CharField(max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('event_type', models.CharField(choices=[('REACHED_HUB', 'Reached Hub'), ('DEPARTED_HUB', 'Departed Hub'), ('ARRIVED_DESTINATION_HUB', 'Arrived at Destination Hub'), ('OUT_FOR_DELIVERY', 'Out For Delivery'), ('DELIVERED', 'Delivered')], max_length=40)),
                ('event_timestamp', models.DateTimeField()),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transit_events', to='shipments.shipment')),
            ],
            options={
                'ordering': ['event_timestamp', 'created_at'],
                'indexes': [models.Index(fields=['shipment', 'event_timestamp'], name='tracking_sh_shipmen_86f089_idx')],
            },
        ),
    ]
