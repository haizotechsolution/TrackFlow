import requests
from django.conf import settings


def send_sms(phone, message):
    payload = {
        'apikey': settings.SMS_API_KEY,
        'number': phone,
        'message': message,
        'sender': settings.SMS_SENDER_ID,
    }

    response = requests.post(settings.SMS_API_URL, json=payload)

    return response.json()