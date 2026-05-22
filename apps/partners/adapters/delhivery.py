import requests

from .base import BaseCarrierAdapter


class DelhiveryAdapter(BaseCarrierAdapter):
    def __init__(self, carrier):
        self.carrier = carrier

    def create_shipment(self, shipment):
        receiver = shipment.receiver_address
        payload = {
            'awb': shipment.awb,
            'name': receiver.name,
            'phone': receiver.phone,
            'address': receiver.address_line_1,
        }

        response = requests.post(
            f'{self.carrier.api_base_url}/create-order/',
            json=payload,
            headers={
                'Authorization': f'Token {self.carrier.api_key}'
            }
        )

        return response.json()
