from django.conf import settings
from django.db import models


class NotificationPreference(models.Model):
    CHANNEL_CHOICES = [
        ('SMS', 'SMS'),
        ('EMAIL', 'EMAIL'),
        ('WHATSAPP', 'WhatsApp'),
        ('WEBHOOK', 'Webhook'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)

    shipment_booked = models.BooleanField(default=True)
    in_transit = models.BooleanField(default=True)
    out_for_delivery = models.BooleanField(default=True)
    delivered = models.BooleanField(default=True)
    failed = models.BooleanField(default=True)
    rto = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'channel')

    def __str__(self):
        return f'{self.user.email} - {self.channel}'


class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    shipment = models.ForeignKey(
        'shipments.Shipment',
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )

    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=255)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    response_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.shipment.awb} - {self.channel}'