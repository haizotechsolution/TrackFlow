from django.db import models
from apps.shipments.models import Shipment


class Route(models.Model):

    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name='route'
    )

    origin = models.CharField(
        max_length=255
    )

    destination = models.CharField(
        max_length=255
    )

    current_hub = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    estimated_distance_km = models.FloatField()

    estimated_delivery_time = models.DateTimeField()

    is_route_optimized = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"{self.shipment.tracking_number} Route"