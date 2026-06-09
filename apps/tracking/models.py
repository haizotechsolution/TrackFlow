from django.db import models


class TrackingEvent(models.Model):
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='tracking_events'
    )

    status = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    event_time = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_time']
        indexes = [
            models.Index(fields=['shipment', 'event_time']),
        ]

    def __str__(self):
        return f"{self.shipment.awb} - {self.status}"


class TrackingLocation(models.Model):
    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='tracking_locations'
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['shipment', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.shipment.awb} Location"


class ShipmentTransitEvent(models.Model):
    REACHED_HUB = 'REACHED_HUB'
    DEPARTED_HUB = 'DEPARTED_HUB'
    ARRIVED_DESTINATION_HUB = 'ARRIVED_DESTINATION_HUB'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
    DELIVERED = 'DELIVERED'

    EVENT_TYPE_CHOICES = [
        (REACHED_HUB, 'Reached Hub'),
        (DEPARTED_HUB, 'Departed Hub'),
        (ARRIVED_DESTINATION_HUB, 'Arrived at Destination Hub'),
        (OUT_FOR_DELIVERY, 'Out For Delivery'),
        (DELIVERED, 'Delivered'),
    ]

    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='transit_events'
    )
    hub_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True)
    event_type = models.CharField(max_length=40, choices=EVENT_TYPE_CHOICES)
    event_timestamp = models.DateTimeField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_timestamp', 'created_at']
        indexes = [
            models.Index(fields=['shipment', 'event_timestamp']),
        ]

    def __str__(self):
        return f"{self.shipment.awb} - {self.get_event_type_display()} - {self.hub_name}"
