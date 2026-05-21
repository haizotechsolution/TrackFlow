from celery import shared_task


@shared_task
def push_shipment_to_carrier(shipment_id, carrier_code):
    from .services import CarrierService
    from ..shipments.models import Shipment

    shipment = Shipment.objects.get(id=shipment_id)

    adapter = CarrierService.get_adapter(carrier_code)

    return adapter.create_shipment(shipment)
