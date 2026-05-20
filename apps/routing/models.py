from django.db import models

class Shipment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
    ]

    tracking_id = models.CharField(max_length=20, unique=True)
    sender_name = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)
    pickup_address = models.TextField()
    delivery_address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tracking_id