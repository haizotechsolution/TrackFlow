from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
import uuid


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_MERCHANT = 'MERCHANT'
    ROLE_CUSTOMER = 'CUSTOMER'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MERCHANT, 'Merchant'),
        (ROLE_CUSTOMER, 'Customer'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MERCHANT)
    is_merchant = models.BooleanField(default=True)
    is_ops = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True
    )

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER


class Merchant(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='merchant_profile'
    )
    company_name = models.CharField(max_length=255)
    gstin = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9A-Z]{15}$',
                message='GSTIN must be 15 uppercase alphanumeric characters.'
            )
        ]
    )
    address = models.JSONField(default=dict, blank=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def rotate_api_key(self):
        self.api_key = uuid.uuid4()
        self.save(update_fields=['api_key'])
        return self.api_key

    def __str__(self):
        return self.company_name


class WebhookEndpoint(models.Model):
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name='webhook_endpoints'
    )
    url = models.URLField()
    secret = models.UUIDField(default=uuid.uuid4, editable=False)
    events = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.merchant.company_name} -> {self.url}'
