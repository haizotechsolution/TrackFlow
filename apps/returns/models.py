from django.db import models


class NDR(models.Model):
    shipment_awb = models.CharField(max_length=50)
    reason = models.CharField(max_length=255)
    attempts = models.IntegerField(default=1)

    ACTIONS = [
        ("PENDING", "Pending"),
        ("REATTEMPT", "Reattempt"),
        ("RTO", "Return To Origin"),
    ]

    merchant_action = models.CharField(
        max_length=20,
        choices=ACTIONS,
        default="PENDING"
    )

    def __str__(self):
        return self.shipment_awb