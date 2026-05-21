from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="codremittance",
            old_name="cod_amount",
            new_name="amount",
        ),
        migrations.RenameField(
            model_name="codremittance",
            old_name="remitted",
            new_name="paid",
        ),
        migrations.AddField(
            model_name="codremittance",
            name="shipment_awb",
            field=models.CharField(default="", max_length=50),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="codremittance",
            name="merchant",
        ),
        migrations.RemoveField(
            model_name="codremittance",
            name="shipment",
        ),
        migrations.RemoveField(
            model_name="codremittance",
            name="created_at",
        ),
        migrations.RenameField(
            model_name="invoice",
            old_name="amount",
            new_name="total_amount",
        ),
        migrations.RenameField(
            model_name="invoice",
            old_name="gst",
            new_name="gst_amount",
        ),
        migrations.RenameField(
            model_name="invoice",
            old_name="total",
            new_name="grand_total",
        ),
        migrations.AlterField(
            model_name="invoice",
            name="merchant",
            field=models.IntegerField(db_column="merchant_id"),
        ),
        migrations.RenameField(
            model_name="invoice",
            old_name="merchant",
            new_name="merchant_id",
        ),
        migrations.AlterField(
            model_name="invoice",
            name="merchant_id",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="invoice_number",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.RemoveField(
            model_name="invoice",
            name="paid",
        ),
        migrations.RenameField(
            model_name="ratecard",
            old_name="base_price",
            new_name="base_rate",
        ),
        migrations.RenameField(
            model_name="ratecard",
            old_name="per_kg_price",
            new_name="per_kg_rate",
        ),
        migrations.AlterField(
            model_name="ratecard",
            name="merchant",
            field=models.IntegerField(db_column="merchant_id"),
        ),
        migrations.RenameField(
            model_name="ratecard",
            old_name="merchant",
            new_name="merchant_id",
        ),
        migrations.AlterField(
            model_name="ratecard",
            name="merchant_id",
            field=models.IntegerField(),
        ),
        migrations.RemoveField(
            model_name="ratecard",
            name="service_type",
        ),
        migrations.RemoveField(
            model_name="ratecard",
            name="active",
        ),
    ]
