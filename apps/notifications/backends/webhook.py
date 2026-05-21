import hashlib
import hmac
import json

import requests


def send_webhook(url, secret, payload):
    payload_json = json.dumps(payload)

    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'X-TrackFlow-Signature': signature,
    }

    response = requests.post(
        url,
        data=payload_json,
        headers=headers,
        timeout=10,
    )

    return response.status_code