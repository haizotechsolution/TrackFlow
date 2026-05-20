from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Shipment
from .tasks import generate_label_async


@receiver(post_save, sender=Shipment)
def shipment_post_save(sender, instance, created, **kwargs):
    if not created or instance.label_file:
        return

    if getattr(settings, 'TRACKFLOW_ASYNC_LABELS', False):
        generate_label_async.delay(instance.id)
        return

    generate_label_async(instance.id)
