from django.db import models
from apps.shipments.models import Shipment


class ReturnRequest(models.Model):

    STATUS = (

        ("NDR", "NDR"),

        ("RTO", "RTO"),

        ("RETURNED", "RETURNED"),

    )

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS,
        default="NDR"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )