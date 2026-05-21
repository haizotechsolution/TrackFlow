import requests
from django.conf import settings


def send_sms(phone, message):
    if not settings.SMS_API_URL or not settings.SMS_API_KEY:
        return {'status': 'skipped', 'reason': 'SMS provider is not configured.'}

    payload = {
        'apikey': settings.SMS_API_KEY,
        'number': phone,
        'message': message,
        'sender': settings.SMS_SENDER_ID,
    }

    response = requests.post(settings.SMS_API_URL, json=payload)

    return response.json()
