from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='trackingevent',
            index=models.Index(fields=['shipment', 'event_time'], name='tracking_tr_shipmen_b4b95d_idx'),
        ),
        migrations.AddIndex(
            model_name='trackinglocation',
            index=models.Index(fields=['shipment', 'recorded_at'], name='tracking_tr_shipmen_d852b0_idx'),
        ),
    ]
