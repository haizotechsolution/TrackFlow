from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.shipments.models import Shipment

from .models import TrackingEvent


STATUS_MESSAGES = {
    'BOOKED': 'Shipment booked',
    'PICKUP_SCHEDULED': 'Pickup scheduled',
    'IN_TRANSIT': 'Shipment is in transit',
    'OUT_FOR_DELIVERY': 'Shipment is out for delivery',
    'DELIVERED': 'Shipment delivered',
    'FAILED': 'Delivery attempt failed',
    'RTO': 'Shipment marked for return to origin',
    'CANCELLED': 'Shipment cancelled',
}


@receiver(pre_save, sender=Shipment)
def remember_previous_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return
    instance._previous_status = (
        Shipment.objects
        .filter(pk=instance.pk)
        .values_list('status', flat=True)
        .first()
    )


@receiver(post_save, sender=Shipment)
def create_tracking_event_for_status(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    if not created and previous_status == instance.status:
        return

    description = STATUS_MESSAGES.get(instance.status, f'Status changed to {instance.status}')

    def publish_event():
        event = TrackingEvent.objects.create(
            shipment=instance,
            status=instance.status,
            description=description,
        )
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        try:
            async_to_sync(channel_layer.group_send)(
                f'tracking_{instance.awb}',
                {
                    'type': 'tracking_update',
                    'message': {
                        'awb': instance.awb,
                        'status': event.status,
                        'description': event.description,
                        'location': event.location,
                        'event_time': event.event_time.isoformat(),
                    },
                },
            )
        except Exception as exc:
            print(f"Tracking websocket publish failed: {exc}")

    transaction.on_commit(publish_event)
