from django.db import models
from apps.accounts.models import Merchant
from apps.shipments.models import Shipment


class RateCard(models.Model):

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
    )

    service_type = models.CharField(
        max_length=50
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    per_kg_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    active = models.BooleanField(
        default=True
    )


class Invoice(models.Model):

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
    )

    invoice_number = models.CharField(
        max_length=100,
        unique=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    gst = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class CODRemittance(models.Model):

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
    )

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE
    )

    cod_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    remitted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )