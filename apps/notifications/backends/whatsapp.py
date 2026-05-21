import requests
from django.conf import settings


def send_whatsapp_message(phone, message):
    payload = {
        'phone': phone,
        'message': message,
    }

    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_TOKEN}'
    }

    response = requests.post(
        settings.WHATSAPP_API_URL,
        json=payload,
        headers=headers,
    )

    return response.json()