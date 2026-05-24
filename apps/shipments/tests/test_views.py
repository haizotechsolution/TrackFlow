from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.shipments.models import Shipment


class ShipmentAPITests(APITestCase):
    def test_authenticated_user_can_create_shipment_with_nested_addresses(self):
        user = get_user_model().objects.create_user(
            username='merchant@example.com',
            email='merchant@example.com',
            password='strong-pass-123',
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            '/api/shipments/',
            {
                'sender_address': {
                    'name': 'Warehouse',
                    'phone': '9999999999',
                    'address_line_1': 'Origin lane',
                    'city': 'Bengaluru',
                    'state': 'Karnataka',
                    'pincode': '560001',
                },
                'receiver_address': {
                    'name': 'Customer',
                    'phone': '8888888888',
                    'address_line_1': 'Delivery street',
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '400001',
                },
                'weight_kg': '2.50',
                'service_type': 'EXPRESS',
                'cod_amount': '150.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        shipment = Shipment.objects.get()
        self.assertEqual(shipment.merchant, user)
        self.assertEqual(shipment.receiver_address.pincode, '400001')
        self.assertTrue(shipment.label_file.name.endswith('.pdf'))


class ShipmentPageTests(TestCase):
    def test_authenticated_user_can_create_shipment_from_page(self):
        user = get_user_model().objects.create_user(
            username='page-merchant@example.com',
            email='page-merchant@example.com',
            password='strong-pass-123',
        )
        self.client.force_login(user)

        response = self.client.post(
            '/api/shipments/page/new/',
            {
                'sender_name': 'Warehouse',
                'sender_phone': '9999999999',
                'sender_address_line_1': 'Origin lane',
                'sender_city': 'Bengaluru',
                'sender_state': 'Karnataka',
                'sender_pincode': '560001',
                'receiver_name': 'Customer',
                'receiver_phone': '8888888888',
                'receiver_address_line_1': 'Delivery street',
                'receiver_city': 'Mumbai',
                'receiver_state': 'Maharashtra',
                'receiver_pincode': '400001',
                'weight_kg': '2.50',
                'service_type': 'EXPRESS',
                'cod_amount': '150.00',
            },
        )

        shipment = Shipment.objects.get()
        self.assertRedirects(response, f'/api/shipments/page/{shipment.awb}/')
        self.assertEqual(shipment.merchant, user)
        self.assertEqual(shipment.receiver_address.name, 'Customer')
