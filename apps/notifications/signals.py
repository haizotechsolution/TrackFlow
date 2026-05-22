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

    # Skip notifications while creating
    if created:
        return

    message = f"Shipment {instance.awb} status updated to {instance.status}"

    # Receiver details
    receiver = instance.receiver_address

    email = None
    phone_number = None

    if receiver:
        email = getattr(receiver, "email", None)
        phone_number = getattr(receiver, "phone", None)

    # EMAIL
    if email:
        try:
            send_email_task.delay(
                "Shipment Update",
                message,
                [email],
            )
        except Exception as e:
            print(f"Email task failed: {e}")

    # SMS + WHATSAPP
    if phone_number:

        try:
            send_sms_task.delay(phone_number, message)
        except Exception as e:
            print(f"SMS task failed: {e}")

        try:
            send_whatsapp_task.delay(phone_number, message)
        except Exception as e:
            print(f"WhatsApp task failed: {e}")
