from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shipments.models import Shipment

from .tasks import (
    send_email_task,
    send_sms_task,
    send_whatsapp_task,
)


@receiver(post_save, sender=Shipment)
def shipment_notification_handler(sender, instance, created, **kwargs):
    if created:
        message = f'Shipment {instance.awb} booked successfully.'

        send_sms_task.delay(instance.receiver.phone, message)

        send_whatsapp_task.delay(instance.receiver.phone, message)

        if instance.merchant.user.email:
            send_email_task.delay(
                'Shipment Booked',
                message,
                [instance.merchant.user.email]
            )
