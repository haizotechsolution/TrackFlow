import requests

from .base import BaseCarrierAdapter


class XpressbeesAdapter(BaseCarrierAdapter):
    def __init__(self, carrier):
        self.carrier = carrier

    def track_shipment(self, awb):
        response = requests.get(
            f'{self.carrier.api_base_url}/track/{awb}',
            headers={
                'Authorization': self.carrier.api_key
            }
        )

        return response.json()