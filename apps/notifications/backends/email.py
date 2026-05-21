from django.core.mail import send_mail
from django.conf import settings


def send_email_notification(subject, body, recipients):
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )