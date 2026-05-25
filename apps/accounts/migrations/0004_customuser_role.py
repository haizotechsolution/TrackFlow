from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_default_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Admin'),
                    ('MERCHANT', 'Merchant'),
                    ('CUSTOMER', 'Customer'),
                ],
                default='MERCHANT',
                max_length=20,
            ),
        ),
    ]
