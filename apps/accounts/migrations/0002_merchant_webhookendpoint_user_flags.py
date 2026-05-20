# Generated for TrackFlow Dev 1 core account models

import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_merchant',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_ops',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('gstin', models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message='GSTIN must be 15 uppercase alphanumeric characters.', regex='^[0-9A-Z]{15}$')])),
                ('address', models.JSONField(blank=True, default=dict)),
                ('api_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_profile', to='accounts.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='WebhookEndpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('secret', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('events', models.JSONField(blank=True, default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhook_endpoints', to='accounts.merchant')),
            ],
        ),
    ]
