from celery import shared_task

from .backends.sms import send_sms
from .backends.email import send_email_notification
from .backends.whatsapp import send_whatsapp_message


@shared_task
def send_sms_task(phone, message):
    return send_sms(phone, message)


@shared_task
def send_email_task(subject, body, recipients):
    return send_email_notification(subject, body, recipients)


@shared_task
def send_whatsapp_task(phone, message):
    return send_whatsapp_message(phone, message)