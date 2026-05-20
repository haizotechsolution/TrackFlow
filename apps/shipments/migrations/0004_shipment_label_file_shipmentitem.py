import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0003_restore_core_shipment_contract'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='label_file',
            field=models.FileField(blank=True, upload_to='labels/'),
        ),
        migrations.CreateModel(
            name='ShipmentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('declared_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('hsn_code', models.CharField(blank=True, max_length=20)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shipments.shipment')),
            ],
        ),
    ]
