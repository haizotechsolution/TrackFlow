from celery import shared_task
from .models import *


@shared_task
def create_invoice_task():

    invoices = Invoice.objects.filter(
        paid=False
    )

    return invoices.count()