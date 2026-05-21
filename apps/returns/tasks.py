from celery import shared_task


@shared_task
def auto_rto_check():
    print("checking pending RTO")