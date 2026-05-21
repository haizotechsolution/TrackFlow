from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shipments.models import Shipment
from apps.shipments.tasks import generate_label_async


@receiver(post_save, sender=Shipment)
def shipment_post_save(sender, instance, created, **kwargs):

    # Only generate label when shipment is first created
    if created and not instance.label_file:

        try:
            generate_label_async.delay(instance.id)

        except Exception as e:
            print(f"Label generation failed: {e}")