from django.contrib import admin

from .models import Address, Shipment

admin.site.register(Address)

admin.site.register(Shipment)