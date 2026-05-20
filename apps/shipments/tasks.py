from celery import shared_task

from .services import save_label_pdf


@shared_task
def generate_label_async(shipment_id):
    return save_label_pdf(shipment_id)
