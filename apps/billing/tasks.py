from celery import shared_task


@shared_task
def generate_weekly_invoices():
    print("Generating weekly invoices...")