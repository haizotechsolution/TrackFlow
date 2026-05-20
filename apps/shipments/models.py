from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django_fsm import FSMField, transition


BOOKED = 'BOOKED'

PICKUP_SCHEDULED = 'PICKUP_SCHEDULED'

IN_TRANSIT = 'IN_TRANSIT'

OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'

DELIVERED = 'DELIVERED'

FAILED = 'FAILED'

RTO = 'RTO'

CANCELLED = 'CANCELLED'


class Address(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message='Pincode must be exactly 6 digits.'
            )
        ]
    )
    landmark = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.name}, {self.city} - {self.pincode}'


class Shipment(models.Model):
    STATUS_CHOICES = [
        (BOOKED, 'Booked'),
        (PICKUP_SCHEDULED, 'Pickup Scheduled'),
        (IN_TRANSIT, 'In Transit'),
        (OUT_FOR_DELIVERY, 'Out For Delivery'),
        (DELIVERED, 'Delivered'),
        (FAILED, 'Failed'),
        (RTO, 'RTO'),
        (CANCELLED, 'Cancelled'),
    ]

    SERVICE_STANDARD = 'STANDARD'
    SERVICE_EXPRESS = 'EXPRESS'
    SERVICE_SAME_DAY = 'SAME_DAY'

    SERVICE_CHOICES = [
        (SERVICE_STANDARD, 'Standard'),
        (SERVICE_EXPRESS, 'Express'),
        (SERVICE_SAME_DAY, 'Same Day'),
    ]

    awb = models.CharField(max_length=14, unique=True, blank=True)
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipments',
        null=True,
        blank=True
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
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    length_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    width_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES,
        default=SERVICE_STANDARD
    )
    cod_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    freight_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_fragile = models.BooleanField(default=False)
    is_dangerous = models.BooleanField(default=False)
    is_reverse = models.BooleanField(default=False)
    original_awb = models.CharField(max_length=14, blank=True)
    status = FSMField(max_length=50, choices=STATUS_CHOICES, default=BOOKED)
    label_file = models.FileField(upload_to='labels/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.awb:
            self.awb = self.generate_awb()
        super().save(*args, **kwargs)

    @classmethod
    def generate_awb(cls):
        last_id = cls.objects.order_by('-id').values_list('id', flat=True).first() or 0
        return f'TF{last_id + 1:012d}'

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

    @transition(field=status, source=OUT_FOR_DELIVERY, target=FAILED)
    def mark_failed(self):
        pass

    @transition(field=status, source=[FAILED, IN_TRANSIT], target=RTO)
    def mark_rto(self):
        pass

    def initiate_rto(self):
        return self.mark_rto()

    @transition(field=status, source=[BOOKED, PICKUP_SCHEDULED], target=CANCELLED)
    def cancel(self):
        pass


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    declared_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hsn_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.name} x {self.quantity}'
