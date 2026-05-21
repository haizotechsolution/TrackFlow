import requests

from .base import BaseCarrierAdapter


class DelhiveryAdapter(BaseCarrierAdapter):
    def __init__(self, carrier):
        self.carrier = carrier

    def create_shipment(self, shipment):
        payload = {
            'awb': shipment.awb,
            'name': shipment.receiver.name,
            'phone': shipment.receiver.phone,
            'address': shipment.receiver.address_line1,
        }

        response = requests.post(
            f'{self.carrier.api_base_url}/create-order/',
            json=payload,
            headers={
                'Authorization': f'Token {self.carrier.api_key}'
            }
        )

        return response.json()