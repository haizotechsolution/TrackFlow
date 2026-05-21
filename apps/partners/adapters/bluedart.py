import requests

from .base import BaseCarrierAdapter


class BlueDartAdapter(BaseCarrierAdapter):
    def __init__(self, carrier):
        self.carrier = carrier

    def cancel_shipment(self, awb):
        response = requests.post(
            f'{self.carrier.api_base_url}/cancel-order/',
            json={'awb': awb},
            headers={
                'Authorization': self.carrier.api_key
            }
        )

        return response.json()