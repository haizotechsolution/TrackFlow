from django.db import models


class Carrier(models.Model):
    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=50,
        unique=True
    )

    api_base_url = models.URLField()

    api_key = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CarrierWebhookLog(models.Model):
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE
    )

    event_type = models.CharField(max_length=100)

    payload = models.JSONField(default=dict)

    received_at = models.DateTimeField(auto_now_add=True)

    processed = models.BooleanField(default=False)