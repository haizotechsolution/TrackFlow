from django.db import models

from django_fsm import FSMField, transition

from apps.accounts.models import Merchant


BOOKED = 'BOOKED'

PICKUP_SCHEDULED = 'PICKUP_SCHEDULED'

IN_TRANSIT = 'IN_TRANSIT'

OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'

DELIVERED = 'DELIVERED'

FAILED = 'FAILED'

RTO = 'RTO'

CANCELLED = 'CANCELLED'


class Address(models.Model):

    name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=15
    )

    address_line_1 = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=6
    )

    def __str__(self):

        return self.name


class Shipment(models.Model):

    STATUS_CHOICES = [

        (BOOKED, 'Booked'),

        (
            PICKUP_SCHEDULED,
            'Pickup Scheduled'
        ),

        (
            IN_TRANSIT,
            'In Transit'
        ),

        (
            OUT_FOR_DELIVERY,
            'Out For Delivery'
        ),

        (
            DELIVERED,
            'Delivered'
        ),

        (
            FAILED,
            'Failed'
        ),

        (
            RTO,
            'RTO'
        ),

        (
            CANCELLED,
            'Cancelled'
        ),
    ]

    awb = models.CharField(
        max_length=50,
        unique=True
    )

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
    )

    sender_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='sender_shipments'
    )

    receiver_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='receiver_shipments'
    )

    weight = models.FloatField()

    status = FSMField(
        default=BOOKED,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.awb


    @transition(
        field=status,
        source=BOOKED,
        target=PICKUP_SCHEDULED
    )
    def schedule_pickup(self):
        pass


    @transition(
        field=status,
        source=PICKUP_SCHEDULED,
        target=IN_TRANSIT
    )
    def mark_in_transit(self):
        pass


    @transition(
        field=status,
        source=IN_TRANSIT,
        target=OUT_FOR_DELIVERY
    )
    def mark_out_for_delivery(self):
        pass


    @transition(
        field=status,
        source=OUT_FOR_DELIVERY,
        target=DELIVERED
    )
    def mark_delivered(self):
        pass