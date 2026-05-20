from django.db import models

# Create your models here.
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

        def __str__(self):
            return f"{self.shipment.awb_number} - {self.status}"

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

    def __str__(self):
        return f"{self.shipment.awb_number} Location"

