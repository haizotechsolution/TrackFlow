from django.db import models


class RateCard(models.Model):
    merchant_id = models.IntegerField()
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"RateCard-{self.merchant_id}"


class Invoice(models.Model):
    merchant_id = models.IntegerField()
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class CODRemittance(models.Model):
    shipment_awb = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.shipment_awb