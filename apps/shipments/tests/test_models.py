from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.shipments.models import (
    BOOKED,
    DELIVERED,
    IN_TRANSIT,
    OUT_FOR_DELIVERY,
    PICKUP_SCHEDULED,
    Address,
    Shipment,
)


class ShipmentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='merchant@example.com',
            email='merchant@example.com',
            password='strong-pass-123',
        )
        self.sender = Address.objects.create(
            name='Warehouse',
            phone='9999999999',
            address_line_1='Origin lane',
            city='Bengaluru',
            state='Karnataka',
            pincode='560001',
        )
        self.receiver = Address.objects.create(
            name='Customer',
            phone='8888888888',
            address_line_1='Delivery street',
            city='Mumbai',
            state='Maharashtra',
            pincode='400001',
        )

    def test_generates_trackflow_awb(self):
        shipment = Shipment.objects.create(
            merchant=self.user,
            sender_address=self.sender,
            receiver_address=self.receiver,
            weight_kg='1.25',
        )

        self.assertEqual(shipment.status, BOOKED)
        self.assertEqual(len(shipment.awb), 14)
        self.assertTrue(shipment.awb.startswith('TF'))

    def test_fsm_happy_path_to_delivered(self):
        shipment = Shipment.objects.create(
            merchant=self.user,
            sender_address=self.sender,
            receiver_address=self.receiver,
            weight_kg='1.25',
        )

        shipment.schedule_pickup()
        self.assertEqual(shipment.status, PICKUP_SCHEDULED)
        shipment.mark_in_transit()
        self.assertEqual(shipment.status, IN_TRANSIT)
        shipment.mark_out_for_delivery()
        self.assertEqual(shipment.status, OUT_FOR_DELIVERY)
        shipment.mark_delivered()
        self.assertEqual(shipment.status, DELIVERED)
